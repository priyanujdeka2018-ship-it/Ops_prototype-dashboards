"""Tests for contributor risk-score composition and risk-level labels
in src/workforce_quality.py."""

from __future__ import annotations

import pandas as pd
import pytest

from src.workforce_quality import (
    MIN_CONTRIBUTOR_SAMPLE,
    _risk_level,
    classify_quality_status,
    recommend_quality_action,
    score_contributor_quality_risk,
)

# Risk-level thresholds used by build_contributor_quality_features.
CONTRIBUTOR_HIGH = 35
CONTRIBUTOR_MEDIUM = 20


def make_row(**overrides) -> pd.Series:
    """A healthy contributor row; overrides introduce specific risk factors."""
    row = {
        "sampled_quality_events": 10,
        "avg_quality_score": 95.0,
        "gold_task_fail_rate": 0.0,
        "reviewer_override_rate": 0.0,
        "avg_peer_agreement_score": 0.90,
        "rework_rate": 0.0,
        "quality_delta": 0.0,
        "tenure_days": 400.0,
        "high_complexity_share": 0.0,
        "expert_complexity_share": 0.0,
    }
    row.update(overrides)
    return pd.Series(row)


def test_healthy_contributor_scores_zero():
    assert score_contributor_quality_risk(make_row()) == 0.0


def test_individual_penalty_terms():
    # Quality gap below the 90.0 target: (90 - 80) * 1.2 = 12.0
    assert score_contributor_quality_risk(make_row(avg_quality_score=80.0)) == pytest.approx(12.0)
    # Gold task fail rate: 0.2 * 30 = 6.0
    assert score_contributor_quality_risk(make_row(gold_task_fail_rate=0.2)) == pytest.approx(6.0)
    # Reviewer override rate: 0.2 * 25 = 5.0
    assert score_contributor_quality_risk(make_row(reviewer_override_rate=0.2)) == pytest.approx(5.0)
    # Peer agreement below the 0.82 target: (0.82 - 0.72) * 45 = 4.5
    assert score_contributor_quality_risk(make_row(avg_peer_agreement_score=0.72)) == pytest.approx(4.5)
    # Rework rate: 0.2 * 25 = 5.0
    assert score_contributor_quality_risk(make_row(rework_rate=0.2)) == pytest.approx(5.0)
    # Recent quality drop: min(18, |-5| * 1.8) = 9.0
    assert score_contributor_quality_risk(make_row(quality_delta=-5.0)) == pytest.approx(9.0)
    # Low tenure + high complexity: 8 + expert_share * 6 = 8 + 3 = 11.0
    assert score_contributor_quality_risk(
        make_row(tenure_days=60.0, high_complexity_share=0.30, expert_complexity_share=0.50)
    ) == pytest.approx(11.0)
    # Low sample (< 8 but >= MIN_CONTRIBUTOR_SAMPLE): flat 5.0
    assert score_contributor_quality_risk(make_row(sampled_quality_events=5)) == pytest.approx(5.0)


def test_penalty_terms_are_additive():
    row = make_row(
        avg_quality_score=80.0,          # 12.0
        gold_task_fail_rate=0.2,         # 6.0
        reviewer_override_rate=0.2,      # 5.0
        avg_peer_agreement_score=0.72,   # 4.5
        rework_rate=0.2,                 # 5.0
        quality_delta=-5.0,              # 9.0
        tenure_days=60.0,                # with shares below: 11.0
        high_complexity_share=0.30,
        expert_complexity_share=0.50,
    )
    assert score_contributor_quality_risk(row) == pytest.approx(52.5)


def test_score_is_capped_at_100():
    row = make_row(
        avg_quality_score=0.0,
        gold_task_fail_rate=1.0,
        reviewer_override_rate=1.0,
        avg_peer_agreement_score=0.0,
        rework_rate=1.0,
        quality_delta=-50.0,
    )
    assert score_contributor_quality_risk(row) == 100.0


class TestInsufficientSample:
    def test_score_is_zero(self):
        row = make_row(sampled_quality_events=MIN_CONTRIBUTOR_SAMPLE - 1, avg_quality_score=50.0)
        assert score_contributor_quality_risk(row) == 0.0

    def test_status_label(self):
        row = make_row(sampled_quality_events=2)
        assert classify_quality_status(row) == "Insufficient sample"

    def test_risk_level_label(self):
        assert (
            _risk_level(0.0, 2, MIN_CONTRIBUTOR_SAMPLE, CONTRIBUTOR_HIGH, CONTRIBUTOR_MEDIUM)
            == "Insufficient sample"
        )

    def test_recommended_action(self):
        row = make_row(sampled_quality_events=2)
        assert recommend_quality_action(row) == (
            "Increase QA sampling before making a coaching decision"
        )


class TestRiskLevelBoundaries:
    @pytest.mark.parametrize(
        "score,expected",
        [
            (50.0, "High quality risk"),
            (35.0, "High quality risk"),    # exact high boundary
            (34.9, "Medium quality risk"),
            (20.0, "Medium quality risk"),  # exact medium boundary
            (19.9, "Low quality risk"),
            (0.0, "Low quality risk"),
        ],
    )
    def test_contributor_levels(self, score, expected):
        level = _risk_level(score, 10, MIN_CONTRIBUTOR_SAMPLE, CONTRIBUTOR_HIGH, CONTRIBUTOR_MEDIUM)
        assert level == expected


class TestQualityStatus:
    def test_declining(self):
        assert classify_quality_status(make_row(quality_delta=-4.0)) == "Declining"

    def test_volatile_on_override(self):
        assert classify_quality_status(make_row(reviewer_override_rate=0.12)) == "Volatile"

    def test_volatile_on_low_peer_agreement(self):
        assert classify_quality_status(make_row(avg_peer_agreement_score=0.70)) == "Volatile"

    def test_improving(self):
        assert classify_quality_status(make_row(quality_delta=4.0)) == "Improving"

    def test_stable(self):
        assert classify_quality_status(make_row()) == "Stable"


class TestRecommendedActions:
    def test_gold_task_failures_take_priority(self):
        row = make_row(gold_task_fail_rate=0.2, reviewer_override_rate=0.2)
        assert recommend_quality_action(row) == "Gold task review + targeted coaching"

    def test_healthy_contributor(self):
        assert recommend_quality_action(make_row()) == "Continue standard monitoring"
