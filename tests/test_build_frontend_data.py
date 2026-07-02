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


# ─── Semantic clusters emission (Module B v2 payload contract) ───────────────

_CLUSTER_KEYS = {
    "cluster_id", "cluster_name", "cluster_kind", "work_type", "root_cause",
    "incident_count", "sev1_count", "sev2_count", "open_count", "resolved_count",
    "team_count", "segment_count", "teams", "segments", "work_types",
    "severity_mix", "avg_days_to_resolve", "first_seen", "latest_seen",
    "last_14d", "prior_14d", "last_30d", "last_60d", "days_since_latest",
    "recurrence_status", "risk_score", "risk_level", "sample_summaries",
}


def test_clusters_shape_and_order(payload):
    clusters = payload["clusters"]
    assert clusters, "no semantic clusters emitted for the fixed-seed data"
    for c in clusters:
        assert _CLUSTER_KEYS <= set(c), f"cluster missing keys: {_CLUSTER_KEYS - set(c)}"
        assert c["cluster_kind"] in {"semantic_cluster", "watchlist_pair"}
        assert c["risk_level"] in {"High", "Medium", "Low"}
        assert isinstance(c["sample_summaries"], list) and c["sample_summaries"]
        assert c["incident_count"] >= 2, "isolated escalations must not be emitted"
    scores = [c["risk_score"] for c in clusters]
    assert scores == sorted(scores, reverse=True), "clusters must be ranked by risk_score desc"


def test_clusters_match_engine(payload, tables):
    """Emitted cluster scores equal summarize_semantic_clusters output."""
    from src.escalation_semantic_clusters import cluster_escalations, summarize_semantic_clusters

    summary = summarize_semantic_clusters(cluster_escalations(tables["escalation_events"]))
    engine = {
        str(row["semantic_cluster_id"]): float(row["risk_score"]) for _, row in summary.iterrows()
    }
    emitted = {c["cluster_id"]: c["risk_score"] for c in payload["clusters"]}
    assert emitted == engine


def test_clusters_empty_input_is_graceful():
    empty = pd.DataFrame(columns=[
        "escalation_id", "date", "work_type", "team_id", "severity",
        "customer_segment", "escalation_summary", "root_cause_category",
        "status", "days_to_resolve",
    ])
    assert bfd.build_clusters(empty) == []
