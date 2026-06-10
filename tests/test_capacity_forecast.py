"""Deterministic forecast tests for src/capacity_forecast.py."""

from __future__ import annotations

import pandas as pd
import pytest

from src.capacity_forecast import (
    _risk_level,
    build_team_capacity_features,
    build_work_type_capacity_features,
    classify_sla_forecast_status,
    prepare_capacity_data,
    score_work_type_capacity_risk,
)

ANCHOR = pd.Timestamp("2026-06-08")  # midnight, matches the normalized reference date


def day(offset: int) -> str:
    return (ANCHOR + pd.Timedelta(days=offset)).strftime("%Y-%m-%d %H:%M:%S")


def make_flat_work_items() -> pd.DataFrame:
    """Inflow exactly matches throughput over the trailing 7 days.

    - 6 completed items, completed on days -5..0 (created earlier, outside
      the inflow window).
    - 6 open items created on days -6, -5, -4, -2, -1, 0; the first three
      are older than 72 hours and count as aged backlog.
    """
    completed = pd.DataFrame(
        {
            "work_item_id": [f"C-{i}" for i in range(6)],
            "work_type": "labeling",
            "region": "amer",
            "team_id": "T1",
            "contributor_id": "P1",
            "status": "completed",
            "date_created": [day(-10)] * 6,
            "completed_at": [day(offset) for offset in range(-5, 1)],
            "sla_met": True,
            "rework_required": False,
            "task_complexity": "medium",
        }
    )
    open_items = pd.DataFrame(
        {
            "work_item_id": [f"O-{i}" for i in range(6)],
            "work_type": "labeling",
            "region": "amer",
            "team_id": "T1",
            "contributor_id": "P1",
            "status": "queued",
            "date_created": [day(offset) for offset in [-6, -5, -4, -2, -1, 0]],
            "completed_at": pd.NaT,
            "sla_met": False,
            "rework_required": False,
            "task_complexity": "medium",
        }
    )
    return pd.concat([completed, open_items], ignore_index=True)


def make_overlay_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Minimal benign quality/escalation frames, mirroring how page 50 always
    calls build_work_type_capacity_features with both provided."""
    quality_events = pd.DataFrame({"work_item_id": ["C-0"], "quality_score": [95.0]})
    escalation_events = pd.DataFrame(
        {
            "escalation_id": ["E-1"],
            "date": [day(-2)],
            "work_type": ["labeling"],
            "region": ["amer"],
            "team_id": ["T1"],
            "root_cause_category": ["other"],
            "severity": ["sev4"],
            "status": ["resolved"],
        }
    )
    return quality_events, escalation_events


def build_features(work_items: pd.DataFrame) -> pd.DataFrame:
    capacity_data = prepare_capacity_data(
        contributors=None,
        work_items=work_items,
        teams=None,
    )
    quality_events, escalation_events = make_overlay_inputs()
    return build_work_type_capacity_features(
        capacity_data,
        quality_events=quality_events,
        escalation_events=escalation_events,
    )


def build_flat_features() -> pd.Series:
    features = build_features(make_flat_work_items())
    assert len(features) == 1
    return features.iloc[0]


def test_flat_inflow_means_flat_backlog():
    row = build_flat_features()
    assert row["work_type"] == "labeling"
    assert row["new_items_7d"] == 6
    assert row["completed_items_7d"] == 6
    assert row["avg_daily_inflow_7d"] == pytest.approx(6 / 7)
    assert row["avg_daily_throughput_7d"] == pytest.approx(6 / 7)
    assert row["throughput_gap"] == pytest.approx(0.0)


def test_flat_scenario_backlog_and_clear_time():
    row = build_flat_features()
    assert row["open_backlog"] == 6
    assert row["aged_backlog_72h"] == 3
    # 6 open items at 6/7 items per day -> exactly 7 days to clear.
    assert row["estimated_days_to_clear_backlog"] == pytest.approx(7.0)
    assert row["sla_adherence_7d"] == pytest.approx(1.0)
    assert row["sla_miss_rate_7d"] == pytest.approx(0.0)
    assert row["rework_rate_7d"] == pytest.approx(0.0)


def test_flat_scenario_capacity_units():
    row = build_flat_features()
    # Without contributor data, capacity falls back to completed * complexity.
    assert row["capacity_units"] == pytest.approx(6.0)
    # required = (new_items + 0.4 * backlog) * complexity * (1 + rework)
    assert row["required_capacity_units"] == pytest.approx((6 + 6 * 0.4) * 1.0)
    assert row["capacity_gap"] == pytest.approx(6.0 - 8.4)


def test_growing_backlog_is_flagged():
    """Inflow with zero throughput must report a negative throughput gap."""
    work_items = make_flat_work_items()
    work_items["status"] = "queued"
    work_items["completed_at"] = pd.NaT
    row = build_features(work_items).iloc[0]

    assert row["completed_items_7d"] == 0
    assert row["throughput_gap"] < 0
    assert "Backlog growing faster than throughput" in row["risk_drivers"]
    # With zero throughput there is no meaningful clear-time estimate.
    assert pd.isna(row["estimated_days_to_clear_backlog"])


def test_build_features_without_overlay_inputs():
    """Regression: missing quality/escalation events used to crash because the
    scalar default from DataFrame.get had .fillna called on it."""
    capacity_data = prepare_capacity_data(None, make_flat_work_items(), None)
    features = build_work_type_capacity_features(capacity_data)
    assert len(features) == 1
    row = features.iloc[0]
    assert row["quality_risk_overlay"] == 0.0
    assert row["escalation_risk_overlay"] == 0.0
    assert row["throughput_gap"] == pytest.approx(0.0)


def test_build_team_features_without_overlay_inputs():
    """Same regression as above for the team-grain feature builder."""
    capacity_data = prepare_capacity_data(None, make_flat_work_items(), None)
    features = build_team_capacity_features(capacity_data)
    assert len(features) == 1
    row = features.iloc[0]
    assert row["quality_risk_overlay"] == 0.0
    assert row["escalation_risk_overlay"] == 0.0


def test_score_work_type_capacity_risk_empty_row():
    result = score_work_type_capacity_risk({})
    assert result.score == 0.0
    assert result.drivers == ()


def test_score_work_type_capacity_risk_negative_gap():
    result = score_work_type_capacity_risk({"throughput_gap": -2.0})
    assert result.score == pytest.approx(10.0)  # min(16, 2 * 5)
    assert result.drivers == ("Backlog growing faster than throughput",)


class TestCapacityRiskLevels:
    @pytest.mark.parametrize(
        "score,expected",
        [
            (70.0, "High capacity risk"),
            (55.0, "High capacity risk"),    # exact high boundary
            (54.9, "Medium capacity risk"),
            (30.0, "Medium capacity risk"),  # exact medium boundary
            (29.9, "Low capacity risk"),
        ],
    )
    def test_boundaries(self, score, expected):
        assert _risk_level(score, data_points=10) == expected

    def test_no_data_points(self):
        assert _risk_level(50.0, data_points=0) == "Insufficient data"

    def test_missing_score(self):
        assert _risk_level(None) == "Insufficient data"


def test_sla_forecast_status_no_data():
    assert classify_sla_forecast_status({}) == "Insufficient data"


def test_sla_forecast_status_stable():
    row = {
        "new_items_7d": 5,
        "completed_items_7d": 5,
        "open_backlog": 2,
        "aged_backlog_72h": 0,
        "throughput_gap": 0.0,
        "sla_adherence_7d": 0.98,
        "utilization_rate": 0.5,
        "high_complexity_share": 0.1,
        "rework_rate_7d": 0.02,
    }
    assert classify_sla_forecast_status(row) == "SLA likely stable"
