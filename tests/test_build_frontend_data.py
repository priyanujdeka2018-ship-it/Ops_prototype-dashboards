"""Phase 3 data-contract tests.

The frontend payload must carry the Module C/D + leadership blocks, and the
emitted scores must equal the tested engines' outputs for the fixed-seed data
in data/ — proving Python is the single source of truth (no client re-derivation).
"""

from __future__ import annotations

import pandas as pd
import pytest

from src import build_frontend_data as bfd
from src.capacity_forecast import build_work_type_capacity_features, prepare_capacity_data
from src.workforce_quality import build_contributor_quality_features, build_team_quality_features

DATA_DIR = bfd.DATA_DIR
_TABLE_NAMES = (
    "teams", "contributors", "work_items",
    "quality_events", "escalation_events", "csat_events", "sla_events",
)


@pytest.fixture(scope="module")
def payload() -> dict:
    return bfd.build_payload(scenario="current")


@pytest.fixture(scope="module")
def tables() -> dict[str, pd.DataFrame]:
    return {name: pd.read_csv(DATA_DIR / f"{name}.csv") for name in _TABLE_NAMES}


def test_payload_has_contract_blocks(payload):
    for key in ("workforce", "capacity", "leadership"):
        assert key in payload, f"payload missing {key!r}"

    wf = payload["workforce"]
    assert {"region", "byWorkType", "teams", "contributors"} <= set(wf)
    assert {"highRiskTeams", "avgQuality"} <= set(wf["region"])

    cap = payload["capacity"]
    assert {"region", "byWorkType", "teams"} <= set(cap)
    assert {"atRisk", "agedShare", "forecast"} <= set(cap["region"])

    ld = payload["leadership"]
    assert isinstance(ld["headline"], str) and ld["headline"]
    assert len(ld["alerts"]) <= 3


def test_workforce_team_shape_and_order(payload):
    teams = payload["workforce"]["teams"]
    assert teams, "no workforce teams emitted"
    expected = {"team_id", "name", "work_type", "risk_score", "risk_band", "drivers", "action", "quality_gap"}
    first = teams[0]
    assert expected <= set(first)
    assert isinstance(first["drivers"], list)
    assert first["risk_band"] in {"High", "Medium", "Low", "Insufficient"}
    scores = [t["risk_score"] for t in teams]
    assert scores == sorted(scores, reverse=True), "teams must be ranked by risk_score desc"


def test_workforce_contributors_are_flagged_only(payload):
    bands = {c["risk_band"] for c in payload["workforce"]["contributors"]}
    assert "Low" not in bands, "contributors block should hold only flagged (High/Medium) rows"


def test_capacity_worktype_shape(payload):
    expected = {"work_type", "forecast", "riskLevel", "complexity", "action", "headGap", "decision"}
    w = payload["capacity"]["byWorkType"][0]
    assert expected <= set(w)
    assert isinstance(w["headGap"], int) and w["headGap"] >= 0


def test_workforce_team_scores_match_engine(payload, tables):
    """Emitted team risk_score equals build_team_quality_features output."""
    contrib = build_contributor_quality_features(
        tables["contributors"], tables["quality_events"], tables["work_items"], tables["teams"]
    )
    team_feat = build_team_quality_features(
        tables["contributors"], tables["quality_events"], tables["work_items"], tables["teams"],
        contributor_quality_summary=contrib,
    )
    engine = {row["team_id"]: round(float(row["risk_score"]), 1) for _, row in team_feat.iterrows()}
    emitted = {t["team_id"]: t["risk_score"] for t in payload["workforce"]["teams"]}
    assert emitted == engine


def test_capacity_forecast_matches_engine(payload, tables):
    """Emitted work-type SLA forecast equals build_work_type_capacity_features output."""
    cap_data = prepare_capacity_data(
        tables["contributors"], tables["work_items"], tables["teams"],
        tables["sla_events"], tables["quality_events"], tables["escalation_events"],
    )
    wt = build_work_type_capacity_features(
        cap_data, contributors=tables["contributors"], teams=tables["teams"],
        quality_events=tables["quality_events"], escalation_events=tables["escalation_events"],
    )
    engine = {row["work_type"]: str(row["forecasted_sla_risk"]) for _, row in wt.iterrows()}
    emitted = {w["work_type"]: w["forecast"] for w in payload["capacity"]["byWorkType"]}
    assert emitted == engine


def test_leadership_alerts_deep_link_to_real_entities(payload):
    ld = payload["leadership"]
    pattern_ids = {p["pattern_id"] for p in payload["patterns"]}
    work_types = {w["work_type"] for w in payload["capacity"]["byWorkType"]}
    team_ids = {t["team_id"] for t in payload["workforce"]["teams"]}
    for alert in ld["alerts"]:
        assert alert["kind"] in {"pattern", "capacity", "quality"}
        assert {"section", "focus"} <= set(alert["target"])
        focus = alert["target"]["focus"]
        if alert["kind"] == "pattern":
            assert focus["patternId"] in pattern_ids
        elif alert["kind"] == "capacity":
            assert focus["workType"] in work_types
        else:
            assert focus["teamId"] in team_ids
