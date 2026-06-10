"""Boundary tests for health thresholds and anomaly detection in src/rules.py."""

from __future__ import annotations

import pandas as pd
import pytest

from src.rules import classify_metric, detect_anomalies


class TestHigherIsBetterThresholds:
    """sla_adherence, csat, quality_score: value >= green -> green, >= amber -> amber."""

    @pytest.mark.parametrize(
        "value,expected",
        [
            (0.96, "green"),
            (0.95, "green"),   # exact green boundary
            (0.949, "amber"),
            (0.90, "amber"),   # exact amber boundary
            (0.899, "red"),
        ],
    )
    def test_sla_adherence(self, value, expected):
        assert classify_metric("sla_adherence", value) == expected

    @pytest.mark.parametrize(
        "value,expected",
        [
            (4.5, "green"),
            (4.4, "green"),
            (4.39, "amber"),
            (4.2, "amber"),
            (4.19, "red"),
        ],
    )
    def test_csat(self, value, expected):
        assert classify_metric("csat", value) == expected

    @pytest.mark.parametrize(
        "value,expected",
        [
            (95.0, "green"),
            (90.0, "green"),
            (89.9, "amber"),
            (85.0, "amber"),
            (84.9, "red"),
        ],
    )
    def test_quality_score(self, value, expected):
        assert classify_metric("quality_score", value) == expected


class TestLowerIsBetterThresholds:
    """rework_rate, escalation_rate_per_1000, aged_backlog_72h: value <= green -> green."""

    @pytest.mark.parametrize(
        "value,expected",
        [
            (0.05, "green"),
            (0.06, "green"),   # exact green boundary
            (0.061, "amber"),
            (0.10, "amber"),   # exact amber boundary
            (0.101, "red"),
        ],
    )
    def test_rework_rate(self, value, expected):
        assert classify_metric("rework_rate", value) == expected

    @pytest.mark.parametrize(
        "value,expected",
        [
            (7.9, "green"),
            (8.0, "green"),
            (8.1, "amber"),
            (15.0, "amber"),
            (15.1, "red"),
        ],
    )
    def test_escalation_rate(self, value, expected):
        assert classify_metric("escalation_rate_per_1000", value) == expected

    @pytest.mark.parametrize(
        "value,expected",
        [
            (0, "green"),
            (25, "green"),
            (26, "amber"),
            (60, "amber"),
            (61, "red"),
        ],
    )
    def test_aged_backlog(self, value, expected):
        assert classify_metric("aged_backlog_72h", value) == expected


def test_classify_metric_none_is_unknown():
    assert classify_metric("sla_adherence", None) == "unknown"


def test_classify_metric_unconfigured_metric_raises():
    with pytest.raises(ValueError):
        classify_metric("not_a_metric", 1.0)


def test_detect_anomalies_flags_sla_drop():
    """SLA falling from 100% to 50% week over week must raise a High anomaly."""
    week1 = "2026-05-18"  # Monday
    week2 = "2026-05-25"  # Monday
    work_items = pd.DataFrame(
        {
            "work_item_id": [f"WI-{i}" for i in range(1, 9)],
            "work_type": ["labeling"] * 8,
            "status": ["completed"] * 8,
            "date_created": [week1] * 4 + [week2] * 4,
            "sla_met": [True, True, True, True, True, True, False, False],
            "rework_required": [False] * 8,
        }
    )
    empty_quality = pd.DataFrame(columns=["work_item_id", "quality_score"])
    empty_escalations = pd.DataFrame(columns=["escalation_id", "work_type", "date"])
    empty_csat = pd.DataFrame(columns=["work_type", "date", "csat_score"])

    anomalies = detect_anomalies(work_items, empty_quality, empty_escalations, empty_csat)

    assert len(anomalies) == 1
    row = anomalies.iloc[0]
    assert row["anomaly_type"] == "SLA deterioration"
    assert row["work_type"] == "labeling"
    assert row["severity"] == "High"  # drop of 50 points > 10 points
    assert row["current_value"] == pytest.approx(0.5)
    assert row["previous_value"] == pytest.approx(1.0)


def test_detect_anomalies_empty_when_healthy():
    work_items = pd.DataFrame(
        {
            "work_item_id": ["WI-1", "WI-2"],
            "work_type": ["labeling"] * 2,
            "status": ["completed"] * 2,
            "date_created": ["2026-05-18", "2026-05-25"],
            "sla_met": [True, True],
            "rework_required": [False, False],
        }
    )
    empty_quality = pd.DataFrame(columns=["work_item_id", "quality_score"])
    empty_escalations = pd.DataFrame(columns=["escalation_id", "work_type", "date"])
    empty_csat = pd.DataFrame(columns=["work_type", "date", "csat_score"])

    anomalies = detect_anomalies(work_items, empty_quality, empty_escalations, empty_csat)

    assert anomalies.empty
