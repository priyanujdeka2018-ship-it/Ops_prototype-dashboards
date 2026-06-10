"""Smoke tests for src/metrics.py using small hand-built DataFrames."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import pytest

from src.metrics import (
    aged_backlog_count,
    average_quality_score,
    backlog_count,
    csat_trailing_average,
    escalation_rate_per_1000,
    executive_kpis,
    fcr_proxy,
    group_metrics_by_work_type,
    rework_rate,
    safe_divide,
    sla_adherence,
)

AS_OF = datetime(2026, 6, 8, 12, 0, 0)


def make_work_items() -> pd.DataFrame:
    """8 items: 4 completed (3 SLA met, 1 rework), 4 open (2 older than 72h)."""
    return pd.DataFrame(
        {
            "work_item_id": [f"WI-{i}" for i in range(1, 9)],
            "work_type": ["labeling"] * 4 + ["code_review"] * 4,
            "team_id": ["T1"] * 4 + ["T2"] * 4,
            "status": [
                "completed",
                "completed",
                "completed",
                "completed",
                "queued",
                "in_progress",
                "blocked",
                "queued",
            ],
            "date_created": [
                "2026-06-01 12:00:00",  # completed
                "2026-06-02 12:00:00",  # completed
                "2026-06-03 12:00:00",  # completed
                "2026-06-04 12:00:00",  # completed
                "2026-06-01 12:00:00",  # open, 168h old -> aged
                "2026-06-03 12:00:00",  # open, 120h old -> aged
                "2026-06-07 12:00:00",  # open, 24h old
                "2026-06-08 06:00:00",  # open, 6h old
            ],
            "sla_met": [True, True, True, False, False, False, False, False],
            "rework_required": [False, False, True, False, False, False, False, False],
        }
    )


def make_quality_events() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "work_item_id": ["WI-1", "WI-2", "WI-3"],
            "quality_score": [90.0, 80.0, 70.0],
        }
    )


def make_escalation_events() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "escalation_id": ["E-1", "E-2"],
            "work_type": ["labeling", "labeling"],
            "team_id": ["T1", "T1"],
            "date": ["2026-06-05", "2026-06-06"],
        }
    )


def make_csat_events() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "work_type": ["labeling", "labeling", "labeling"],
            "team_id": ["T1", "T1", "T1"],
            # The 30-day-old score falls outside the trailing 7-day window.
            "date": ["2026-06-07", "2026-06-08", "2026-05-09"],
            "csat_score": [4.0, 5.0, 1.0],
        }
    )


def test_safe_divide():
    assert safe_divide(6, 3) == 2.0
    assert safe_divide(1, 0) == 0.0


def test_sla_adherence():
    assert sla_adherence(make_work_items()) == pytest.approx(0.75)


def test_backlog_count():
    assert backlog_count(make_work_items()) == 4


def test_aged_backlog_count():
    assert aged_backlog_count(make_work_items(), as_of=AS_OF, hours=72) == 2


def test_average_quality_score():
    assert average_quality_score(make_quality_events()) == pytest.approx(80.0)
    assert average_quality_score(pd.DataFrame()) == 0.0


def test_rework_rate():
    assert rework_rate(make_work_items()) == pytest.approx(0.25)


def test_csat_trailing_average_window():
    # Only the two scores within 7 days of the max date count.
    assert csat_trailing_average(make_csat_events(), days=7) == pytest.approx(4.5)
    assert csat_trailing_average(pd.DataFrame()) == 0.0


def test_escalation_rate_per_1000():
    rate = escalation_rate_per_1000(make_escalation_events(), make_work_items())
    assert rate == pytest.approx(250.0)  # 2 escalations / 8 items * 1000


def test_fcr_proxy():
    # Completed with SLA met and no rework: WI-1, WI-2 out of 4 completed.
    assert fcr_proxy(make_work_items()) == pytest.approx(0.5)


def test_executive_kpis_matches_components():
    work_items = make_work_items()
    quality_events = make_quality_events()
    escalation_events = make_escalation_events()
    csat_events = make_csat_events()

    kpis = executive_kpis(work_items, quality_events, escalation_events, csat_events)

    assert kpis["sla_adherence"] == pytest.approx(0.75)
    assert kpis["csat_trailing_7d"] == pytest.approx(4.5)
    assert kpis["backlog_count"] == 4
    assert kpis["escalation_rate_per_1000"] == pytest.approx(250.0)
    assert kpis["average_quality_score"] == pytest.approx(80.0)
    assert kpis["rework_rate"] == pytest.approx(0.25)
    assert kpis["fcr_proxy"] == pytest.approx(0.5)
    # aged_backlog_72h uses wall-clock now; both open 2026 items are long past 72h.
    assert kpis["aged_backlog_72h"] >= 2


def test_group_metrics_by_work_type():
    grouped = group_metrics_by_work_type(
        make_work_items(),
        make_quality_events(),
        make_escalation_events(),
        make_csat_events(),
    )

    assert list(grouped["work_type"]) == ["code_review", "labeling"]
    labeling = grouped[grouped["work_type"] == "labeling"].iloc[0]
    code_review = grouped[grouped["work_type"] == "code_review"].iloc[0]

    # All 4 labeling items are completed, 3 of 4 with SLA met.
    assert labeling["sla_adherence"] == pytest.approx(0.75)
    assert labeling["backlog_count"] == 0
    assert labeling["work_item_count"] == 4
    assert labeling["escalation_count"] == 2
    assert labeling["escalation_rate_per_1000"] == pytest.approx(500.0)
    assert labeling["average_quality_score"] == pytest.approx(80.0)

    # All 4 code_review items are open.
    assert code_review["sla_adherence"] == 0.0
    assert code_review["backlog_count"] == 4
    assert code_review["escalation_count"] == 0
