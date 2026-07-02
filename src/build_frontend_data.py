"""
Build web/public/data/data.json for the TanStack front-end from the real
CSVs in data/, reusing the same metric and pattern-scoring logic in src/ so
the UI shows exactly the numbers the pipeline computes.

Usage:
    python -m src.build_frontend_data [--scenario healthy|current|crisis]
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.escalation_patterns import summarize_patterns
from src.metrics import (
    aged_backlog_count,
    average_quality_score,
    backlog_count,
    csat_trailing_average,
    escalation_rate_per_1000,
    fcr_proxy,
    group_metrics_by_team,
    group_metrics_by_work_type,
    rework_rate,
    sla_adherence,
)
from src.workforce_quality import (
    build_contributor_quality_features,
    build_team_quality_features,
    build_work_type_quality_features,
)
from src.capacity_forecast import (
    build_team_capacity_features,
    build_work_type_capacity_features,
    prepare_capacity_data,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
OUTPUT_DIR = REPO_ROOT / "web" / "public" / "data"
OUTPUT_PATH = OUTPUT_DIR / "data.json"

PIPELINE_VERSION = "1.0.0"
OPEN_STATUSES = {"open", "in_progress"}
TREND_WEEKS = 7


def _week_start(dates: pd.Series) -> pd.Series:
    return pd.to_datetime(dates).dt.to_period("W").dt.start_time


def _risk_level_short(label: str) -> str:
    return str(label).replace(" recurrence risk", "")


def _round(value: float, digits: int = 1) -> float:
    number = float(value)
    if number != number:  # NaN -> avoid emitting invalid JSON
        return 0.0
    return round(number, digits)


def _numf(value: object, default: float = 0.0) -> float:
    """NaN/None-safe float for sparse engine columns."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return default if number != number else number


def build_kpis(work_items, quality_events, escalation_events, csat_events, as_of) -> dict:
    return {
        "sla_adherence": _round(sla_adherence(work_items) * 100),
        "csat_7d": _round(csat_trailing_average(csat_events, days=7), 2),
        "backlog": backlog_count(work_items),
        "aged_backlog_72h": aged_backlog_count(work_items, as_of=as_of, hours=72),
        "escalation_rate_per_1000": _round(escalation_rate_per_1000(escalation_events, work_items)),
        "avg_quality": _round(average_quality_score(quality_events)),
        "rework_rate": _round(rework_rate(work_items) * 100),
        "fcr_proxy": _round(fcr_proxy(work_items) * 100),
    }


def build_kpi_trends(work_items, quality_events, escalation_events, csat_events) -> dict:
    """Weekly KPI series for the sparklines, ending at the reference week."""
    wi = work_items.copy()
    wi["created_week"] = _week_start(wi["date_created"])
    completed = wi[wi["status"] == "completed"].copy()
    completed["completed_week"] = _week_start(completed["completed_at"])

    weeks = sorted(wi["created_week"].unique())[-TREND_WEEKS:]

    quality = quality_events.merge(
        wi[["work_item_id", "created_week"]], on="work_item_id", how="left"
    )

    csat = csat_events.copy()
    csat["week"] = _week_start(csat["date"])
    esc = escalation_events.copy()
    esc["week"] = _week_start(esc["date"])

    created_cum = wi.groupby("created_week").size().cumsum()
    completed_cum = completed.groupby("completed_week").size().cumsum()

    trends: dict[str, list[float]] = {
        "sla": [], "csat": [], "backlog": [], "quality": [], "esc_rate": [], "fcr": []
    }
    for week in weeks:
        week_completed = completed[completed["completed_week"] == week]
        week_created = wi[wi["created_week"] == week]
        week_quality = quality[quality["created_week"] == week]
        week_csat = csat[csat["week"] == week]
        week_esc = esc[esc["week"] == week]

        trends["sla"].append(_round(sla_adherence(week_completed.assign(status="completed")) * 100))
        trends["csat"].append(_round(week_csat["csat_score"].mean(), 2) if not week_csat.empty else None)
        trends["quality"].append(_round(week_quality["quality_score"].mean()) if not week_quality.empty else None)
        trends["esc_rate"].append(
            _round(len(week_esc) / max(len(week_created), 1) * 1000, 0)
        )
        trends["fcr"].append(_round(fcr_proxy(week_completed) * 100))

        created_to_date = int(created_cum[created_cum.index <= week].iloc[-1]) if (created_cum.index <= week).any() else 0
        completed_to_date = int(completed_cum[completed_cum.index <= week].iloc[-1]) if (completed_cum.index <= week).any() else 0
        trends["backlog"].append(created_to_date - completed_to_date)

    # Sparklines cannot render gaps; backfill the rare empty week.
    for key, series in trends.items():
        last = next((v for v in series if v is not None), 0)
        trends[key] = [last := (v if v is not None else last) for v in series]
    return trends


def build_patterns(escalation_events: pd.DataFrame) -> list[dict]:
    summary = summarize_patterns(escalation_events, pattern_grain="work_type_root_cause")
    events = escalation_events.copy()
    events["date"] = pd.to_datetime(events["date"])
    grouped = events.groupby(["work_type", "root_cause_category"])

    patterns = []
    for _, row in summary.iterrows():
        group = grouped.get_group((row["work_type"], row["root_cause_category"]))
        sample_summaries = (
            group.sort_values("date", ascending=False)["escalation_summary"]
            .dropna().astype(str).drop_duplicates().head(3).tolist()
        )
        patterns.append(
            {
                "pattern_id": row["pattern_id"],
                "pattern_key": row["pattern_key"],
                "work_type": row["work_type"],
                "root_cause": row["root_cause_category"],
                "escalation_count": int(row["escalation_count"]),
                "sev1_count": int(row["sev1_count"]),
                "sev2_count": int(row["sev2_count"]),
                "sev3_count": int((group["severity"] == "sev3").sum()),
                "sev4_count": int((group["severity"] == "sev4").sum()),
                "open_count": int(row["open_count"]),
                "unique_teams": int(row["unique_teams_impacted"]),
                "unique_segments": int(row["unique_customer_segments_impacted"]),
                "teams": sorted(group["team_id"].dropna().unique().tolist()),
                "segments": sorted(group["customer_segment"].dropna().unique().tolist()),
                "avg_days_to_resolve": float(row["avg_days_to_resolve"]),
                "first_seen": str(row["first_seen_date"]),
                "latest_seen": str(row["latest_escalation_date"]),
                "last_14d": int(row["last_14d_count"]),
                "prior_14d": int(row["prior_14d_count"]),
                "last_30d": int(row["last_30d_count"]),
                "last_60d": int(row["last_60d_count"]),
                "days_since_latest": int(row["days_since_latest_escalation"]),
                "recurrence_status": row["recurrence_status"],
                "risk_score": float(row["risk_score"]),
                "risk_level": _risk_level_short(row["risk_level"]),
                "recommended_action": row["recommended_action"],
                "sample_summaries": sample_summaries,
            }
        )
    return patterns


def build_teams(teams, contributors, work_items, quality_events, escalation_events, csat_events) -> list[dict]:
    metrics = group_metrics_by_team(work_items, quality_events, escalation_events, csat_events)
    metrics = metrics.set_index("team_id")
    esc = escalation_events
    rows = []
    for _, team in teams.iterrows():
        team_id = team["team_id"]
        team_esc = esc[esc["team_id"] == team_id]
        m = metrics.loc[team_id] if team_id in metrics.index else None
        rows.append(
            {
                "team_id": team_id,
                "city": team["city"],
                "region": team["region"],
                "work_type": team["work_type"],
                "manager": team["manager_name"],
                "shift": team["shift_type"],
                "contributors": int(team["active_contributors"]),
                "escalations": int(len(team_esc)),
                "sev1_escalations": int((team_esc["severity"] == "sev1").sum()),
                "open_escalations": int(team_esc["status"].isin(OPEN_STATUSES).sum()),
                "sla": _round(m["sla_adherence"] * 100) if m is not None else 0.0,
                "csat": _round(m["csat_trailing_7d"], 2) if m is not None else 0.0,
                "quality": _round(m["average_quality_score"]) if m is not None else 0.0,
            }
        )
    return rows


def build_work_type_rollup(teams, work_items, quality_events, escalation_events, csat_events) -> list[dict]:
    metrics = group_metrics_by_work_type(work_items, quality_events, escalation_events, csat_events)
    esc = escalation_events
    rows = []
    for _, m in metrics.iterrows():
        work_type = m["work_type"]
        wt_teams = teams[teams["work_type"] == work_type]
        wt_esc = esc[esc["work_type"] == work_type]
        rows.append(
            {
                "work_type": work_type,
                "teams": int(len(wt_teams)),
                "contributors": int(wt_teams["active_contributors"].sum()),
                "sla": _round(m["sla_adherence"] * 100),
                "csat": _round(m["csat_trailing_7d"], 2),
                "quality": _round(m["average_quality_score"]),
                "escalations": int(m["escalation_count"]),
                "open_escalations": int(wt_esc["status"].isin(OPEN_STATUSES).sum()),
                "sev1": int((wt_esc["severity"] == "sev1").sum()),
                "escalation_rate_per_1000": int(round(m["escalation_rate_per_1000"])),
            }
        )
    return rows


# ─── Module C/D emit: workforce + capacity + leadership (Phase 3 contract) ───
# Python becomes the single source of truth for the C/D scores the frontend
# used to fabricate client-side. Every field below comes from the tested
# engines in workforce_quality.py / capacity_forecast.py.

QUALITY_TARGET = 90.0

WORK_TYPE_LABELS = {
    "image_annotation": "Image annotation",
    "rlhf_evaluation": "RLHF evaluation",
    "code_review": "Code review",
    "audio_evaluation": "Audio evaluation",
    "expert_review": "Expert review",
}
ROOT_CAUSE_LABELS = {
    "policy_ambiguity": "Policy ambiguity",
    "reviewer_misalignment": "Reviewer misalignment",
    "quality_defect": "Quality defect",
    "tooling_issue": "Tooling issue",
    "customer_requirement_change": "Customer requirement change",
    "sla_miss": "SLA miss",
    "workflow_handoff_gap": "Workflow handoff gap",
    "capacity_shortfall": "Capacity shortfall",
}


def _wt_label(work_type: object) -> str:
    return WORK_TYPE_LABELS.get(work_type, str(work_type).replace("_", " ").capitalize())


def _rc_label(root_cause: object) -> str:
    return ROOT_CAUSE_LABELS.get(root_cause, str(root_cause).replace("_", " ").capitalize())


def _short_band(label: object) -> str:
    """'High quality risk' / 'Low capacity risk' / 'Insufficient data' -> first word."""
    text = str(label).strip()
    return text.split()[0] if text else "Low"


def _driver_list(value: object) -> list[str]:
    if value is None:
        return []
    return [part.strip() for part in str(value).split(",") if part.strip()]


def _is_at_risk(forecast: object) -> bool:
    return "stable" not in str(forecast).lower()


def _heads_short(row) -> int:
    """Convert the engine's skill-weighted capacity-unit shortfall to equivalent heads."""
    units = _numf(row["capacity_units"])
    heads = _numf(row["active_contributors"])
    required = _numf(row["required_capacity_units"])
    if heads <= 0 or units <= 0:
        return 0
    units_per_head = units / heads
    return int(round(max(0.0, required - units) / units_per_head)) if units_per_head > 0 else 0


def _capacity_decision(row, head_gap: int) -> str:
    work_type = _wt_label(row["work_type"])
    if head_gap > 0:
        head_word = "head" if head_gap == 1 else "heads"
        return f"Approve +{head_gap} trained {head_word} (or surge coverage) for {work_type}?"
    if _is_at_risk(row["forecasted_sla_risk"]):
        return f"Approve load rebalance / intake throttle for {work_type}?"
    return "Maintain current staffing."


def build_workforce(teams, contributors, work_items, quality_events, escalation_events, kpis) -> dict:
    """Module C scores, straight from workforce_quality.py — never recomputed in the UI."""
    contrib = build_contributor_quality_features(contributors, quality_events, work_items, teams)
    team_feat = build_team_quality_features(
        contributors, quality_events, work_items, teams, contributor_quality_summary=contrib
    )
    wt_feat = build_work_type_quality_features(contrib, team_feat)

    bands_by_wt: dict[str, set[str]] = {}
    teams_out = []
    for _, t in team_feat.iterrows():
        band = _short_band(t["risk_level"])
        bands_by_wt.setdefault(t["work_type"], set()).add(band)
        teams_out.append(
            {
                "team_id": t["team_id"],
                "name": t["manager_name"],
                "work_type": t["work_type"],
                "risk_score": _round(t["risk_score"]),
                "risk_band": band,
                "drivers": _driver_list(t["risk_drivers"]),
                "action": str(t["recommended_manager_action"]),
                "quality_gap": _round(max(0.0, QUALITY_TARGET - _numf(t["avg_quality_score"]))),
                # real per-team metrics (surfaced for the workforce route)
                "quality": _round(t["avg_quality_score"]),
                "drift": _round(t["quality_delta"]),
                "goldFail": _round(_numf(t["gold_task_fail_rate"]) * 100),
                "override": _round(_numf(t["reviewer_override_rate"]) * 100),
                "peerAgree": _round(_numf(t["avg_peer_agreement_score"]) * 100),
                "rework": _round(_numf(t["rework_rate"]) * 100),
                "lowTenure": _round(_numf(t["low_tenure_share"]) * 100),
                "contributors": int(_numf(t["active_contributors"])),
            }
        )
    teams_out.sort(key=lambda r: r["risk_score"], reverse=True)

    def _agg_band(work_type: str) -> str:
        bands = bands_by_wt.get(work_type, set())
        for band in ("High", "Medium", "Low", "Insufficient"):
            if band in bands:
                return band
        return "Low"

    by_work_type = [
        {
            "work_type": w["work_type"],
            "riskLevel": _agg_band(w["work_type"]),
            "avgQuality": _round(w["avg_quality_score"]),
            "teamsAtRisk": int(w["high_risk_teams"]),
            "avgScore": _round(w["work_type_risk_score"]),
            "flagged": int(
                sum(
                    1
                    for _, c in contrib.iterrows()
                    if c["work_type"] == w["work_type"] and _short_band(c["risk_level"]) in ("High", "Medium")
                )
            ),
        }
        for _, w in wt_feat.iterrows()
    ]

    flagged = [c for _, c in contrib.iterrows() if _short_band(c["risk_level"]) in ("High", "Medium")]
    flagged.sort(key=lambda c: _numf(c["risk_score"]), reverse=True)
    contributors_out = [
        {
            "contributor_id": c["contributor_id"],
            "team_id": c["team_id"],
            "work_type": c["work_type"],
            "risk_score": _round(c["risk_score"]),
            "risk_band": _short_band(c["risk_level"]),
            "drivers": _driver_list(c["risk_drivers"]),
            "coaching": str(c["recommended_action"]),
            # real per-contributor metrics (surfaced for coaching cards)
            "skill": str(c["skill_level"]),
            "tenure": int(_numf(c["tenure_days"])),
            "lowTenure": bool(_numf(c["tenure_days"]) < 120),
            "quality": _round(c["avg_quality_score"]),
            "goldPass": _round(max(0.0, 100.0 - _numf(c["gold_task_fail_rate"]) * 100)),
            "override": _round(_numf(c["reviewer_override_rate"]) * 100),
            "rework": _round(_numf(c["rework_rate"]) * 100),
            "peer": _round(_numf(c["avg_peer_agreement_score"]) * 100),
            "status": str(c["risk_status"]),
        }
        for c in flagged
    ]

    return {
        "region": {
            "highRiskTeams": sum(1 for t in teams_out if t["risk_band"] == "High"),
            "avgQuality": kpis["avg_quality"],
            "teamCount": len(teams_out),
            "reworkRate": kpis["rework_rate"],
            "flaggedContributors": len(contributors_out),
            "highRiskContributors": sum(1 for c in contributors_out if c["risk_band"] == "High"),
        },
        "byWorkType": by_work_type,
        "teams": teams_out,
        "contributors": contributors_out,
    }


def build_capacity(contributors, work_items, teams, sla_events, quality_events, escalation_events, kpis) -> dict:
    """Module D capacity + SLA forecast, straight from capacity_forecast.py."""
    cap_data = prepare_capacity_data(
        contributors, work_items, teams, sla_events, quality_events, escalation_events
    )
    wt_feat = build_work_type_capacity_features(
        cap_data, contributors=contributors, teams=teams,
        quality_events=quality_events, escalation_events=escalation_events,
    )
    team_feat = build_team_capacity_features(
        cap_data, contributors=contributors, teams=teams,
        quality_events=quality_events, escalation_events=escalation_events,
    )

    # team context the capacity engine doesn't carry: city/shift + open escalations
    team_meta = {r["team_id"]: {"city": r.get("city", ""), "shift": r.get("shift_type", "")} for _, r in teams.iterrows()}
    open_esc = escalation_events[escalation_events["status"].isin(OPEN_STATUSES)].groupby("team_id").size().to_dict()

    by_work_type = []
    at_risk = 0
    for _, w in wt_feat.iterrows():
        forecast = str(w["forecasted_sla_risk"])
        if _is_at_risk(forecast):
            at_risk += 1
        head_gap = _heads_short(w)
        by_work_type.append(
            {
                "work_type": w["work_type"],
                "forecast": forecast,
                "riskLevel": _short_band(w["capacity_risk_level"]),
                "complexity": int(round(_numf(w["high_complexity_share"]) * 100)),
                "action": str(w["recommended_capacity_action"]),
                "headGap": head_gap,
                "decision": _capacity_decision(w, head_gap),
                # real per-work-type capacity metrics (surfaced for the capacity route)
                "riskScore": _round(w["capacity_risk_score"]),
                "drivers": _driver_list(w["risk_drivers"]),
                "utilization": int(round(_numf(w["utilization_rate"]) * 100)),
                "slaNow": _round(_numf(w["sla_adherence_7d"]) * 100),
                "backlog": int(_numf(w["open_backlog"])),
                "backlogPressure": _round(_numf(w["estimated_days_to_clear_backlog"]) / 7.0),
                "inflow": int(round(_numf(w["avg_daily_inflow_7d"]) * 7)),
                "throughput": int(round(_numf(w["avg_daily_throughput_7d"]) * 7)),
                "contributors": int(_numf(w["active_contributors"])),
            }
        )

    teams_out = [
        {
            "team_id": t["team_id"],
            "name": t["manager_name"],
            "work_type": t["work_type"],
            "utilization": int(round(_numf(t["utilization_rate"]) * 100)),
            "load": int(_numf(t["open_backlog"])),
            "action": str(t["recommended_manager_action"]),
            "riskScore": _round(t["capacity_risk_score"]),
            "riskLevel": _short_band(t["capacity_risk_level"]),
            "sla": _round(_numf(t["sla_adherence_7d"]) * 100),
            "backlog": int(_numf(t["open_backlog"])),
            "throughput": int(round(_numf(t["avg_daily_throughput_7d"]) * 7)),
            "contributors": int(_numf(t["active_contributors"])),
            "city": team_meta.get(t["team_id"], {}).get("city", ""),
            "shift": team_meta.get(t["team_id"], {}).get("shift", ""),
            "openEsc": int(open_esc.get(t["team_id"], 0)),
            "lowTenureHighComplex": bool(_numf(t["low_tenure_share"]) > 0.2 and _numf(t["high_complexity_share"]) > 0.25),
        }
        for _, t in team_feat.iterrows()
    ]

    def _forecast_rank(forecast: str) -> int:
        text = forecast.lower()
        if "recovery" in text:
            return 3
        if "risk" in text:
            return 2
        if "watch" in text:
            return 1
        return 0

    region_forecast = max(
        (w["forecast"] for w in by_work_type), key=_forecast_rank, default="SLA likely stable"
    )

    return {
        "region": {
            "atRisk": at_risk,
            "agedShare": int(round(kpis["aged_backlog_72h"] / max(1, kpis["backlog"]) * 100)),
            "forecast": region_forecast,
            "backlog": kpis["backlog"],
            "totalHeadGap": sum(w["headGap"] for w in by_work_type),
            "avgSla": kpis["sla_adherence"],
        },
        "byWorkType": by_work_type,
        "teams": teams_out,
    }


def _leadership_headline(scenario: str, payload: dict) -> str:
    at_risk = payload["capacity"]["region"]["atRisk"]
    high_q = payload["workforce"]["region"]["highRiskTeams"]
    sla = payload["kpis"]["sla_adherence"]
    return (
        f"{scenario.capitalize()} scenario · SLA {sla}% · "
        f"{at_risk} work type{'s' if at_risk != 1 else ''} with SLA at risk · "
        f"{high_q} team{'s' if high_q != 1 else ''} flagged for quality."
    )


def build_leadership(payload: dict, scenario: str) -> dict:
    """Top-ranked cross-module signals -> <=3 click-through alerts (mirrors Aurora's buildAlerts)."""
    patterns = payload["patterns"]
    alerts: list[dict] = []

    top_pat = next((p for p in patterns if p["risk_level"] == "High"), patterns[0] if patterns else None)
    if top_pat:
        alerts.append(
            {
                "kind": "pattern",
                "title": f"{_rc_label(top_pat['root_cause'])} in {_wt_label(top_pat['work_type'])} is {str(top_pat['recurrence_status']).lower()}",
                "body": f"{top_pat['escalation_count']} escalations · {top_pat['open_count']} open · last-14d {top_pat['last_14d']} vs prior {top_pat['prior_14d']} · {top_pat['unique_teams']} teams.",
                "target": {"section": "patterns", "focus": {"patternId": top_pat["pattern_id"]}},
            }
        )

    top_cap = next((w for w in payload["capacity"]["byWorkType"] if _is_at_risk(w["forecast"])), None)
    if top_cap:
        gap_txt = f" · short {top_cap['headGap']} heads" if top_cap["headGap"] > 0 else ""
        forecast_txt = top_cap["forecast"].replace("SLA ", "").lower()
        alerts.append(
            {
                "kind": "capacity",
                "title": f"{_wt_label(top_cap['work_type'])} SLA forecast: {forecast_txt}",
                "body": f"{top_cap['action']}{gap_txt}.",
                "target": {"section": "capacity", "focus": {"workType": top_cap["work_type"]}},
            }
        )

    top_q = next((t for t in payload["workforce"]["teams"] if t["risk_band"] == "High"), None)
    if top_q and len(alerts) < 3:
        alerts.append(
            {
                "kind": "quality",
                "title": f"Quality risk concentrating in {_wt_label(top_q['work_type'])} ({top_q['name']})",
                "body": f"Risk score {top_q['risk_score']} · quality gap {top_q['quality_gap']}pt · {top_q['action']}.",
                "target": {"section": "workforce", "focus": {"teamId": top_q["team_id"]}},
            }
        )

    return {"headline": _leadership_headline(scenario, payload), "alerts": alerts[:3]}


def build_payload(scenario: str = "current") -> dict:
    teams = pd.read_csv(DATA_DIR / "teams.csv")
    contributors = pd.read_csv(DATA_DIR / "contributors.csv")
    work_items = pd.read_csv(DATA_DIR / "work_items.csv")
    quality_events = pd.read_csv(DATA_DIR / "quality_events.csv")
    escalation_events = pd.read_csv(DATA_DIR / "escalation_events.csv")
    csat_events = pd.read_csv(DATA_DIR / "csat_events.csv")
    sla_events = pd.read_csv(DATA_DIR / "sla_events.csv")

    esc_dates = pd.to_datetime(escalation_events["date"])
    ref_date = esc_dates.max().normalize()
    as_of = pd.to_datetime(work_items["date_created"]).max()
    week_start = ref_date.to_period("W").start_time

    esc = escalation_events.copy()
    esc["week"] = _week_start(esc["date"])
    weekly_trend = [
        {"week": str(week.date()), "count": int(count)}
        for week, count in esc.groupby("week").size().items()
    ]

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scenario": scenario,
        "pipeline_version": PIPELINE_VERSION,
        "row_counts": {
            "work_items": int(len(work_items)),
            "escalations": int(len(escalation_events)),
            "teams": int(len(teams)),
            "contributors": int(len(contributors)),
            "quality_events": int(len(quality_events)),
            "sla_events": int(len(sla_events)),
            "csat_events": int(len(csat_events)),
        },
        "refDate": str(ref_date.date()),
        "weekStart": week_start.strftime("%b %-d"),
        "region": str(teams["region"].iloc[0]),
        "kpis": build_kpis(work_items, quality_events, escalation_events, csat_events, as_of),
        "kpiTrends": build_kpi_trends(work_items, quality_events, escalation_events, csat_events),
        "totals": {
            "escalations": int(len(escalation_events)),
            "open": int(escalation_events["status"].isin(OPEN_STATUSES).sum()),
            "sev1": int((escalation_events["severity"] == "sev1").sum()),
            "sev2": int((escalation_events["severity"] == "sev2").sum()),
            "contributors": int(len(contributors)),
            "teams": int(len(teams)),
        },
        "severityCounts": {k: int(v) for k, v in escalation_events["severity"].value_counts().sort_index().items()},
        "statusCounts": {k: int(v) for k, v in escalation_events["status"].value_counts().items()},
        "rootCauseCounts": {k: int(v) for k, v in escalation_events["root_cause_category"].value_counts().items()},
        "workTypeCounts": {k: int(v) for k, v in escalation_events["work_type"].value_counts().items()},
        "segmentCounts": {k: int(v) for k, v in escalation_events["customer_segment"].value_counts().items()},
        "weeklyTrend": weekly_trend,
        "patterns": build_patterns(escalation_events),
        "teams": build_teams(teams, contributors, work_items, quality_events, escalation_events, csat_events),
        "workTypeRollup": build_work_type_rollup(teams, work_items, quality_events, escalation_events, csat_events),
        "escalations": json.loads(escalation_events.to_json(orient="records")),
    }
    payload["workforce"] = build_workforce(
        teams, contributors, work_items, quality_events, escalation_events, payload["kpis"]
    )
    payload["capacity"] = build_capacity(
        contributors, work_items, teams, sla_events, quality_events, escalation_events, payload["kpis"]
    )
    payload["leadership"] = build_leadership(payload, scenario)
    return payload


def _parse_scenario(argv: list[str]) -> str:
    """Read --scenario VALUE (or --scenario=VALUE) from argv; default current."""
    for i, arg in enumerate(argv):
        if arg == "--scenario" and i + 1 < len(argv):
            return argv[i + 1]
        if arg.startswith("--scenario="):
            return arg.split("=", 1)[1]
    return "current"


def _parse_label(argv: list[str]) -> str | None:
    """Read --label VALUE (or --label=VALUE); emits data-<label>.json as a vintage snapshot."""
    for i, arg in enumerate(argv):
        if arg == "--label" and i + 1 < len(argv):
            return argv[i + 1]
        if arg.startswith("--label="):
            return arg.split("=", 1)[1]
    return None


def main(scenario: str = "current", label: str | None = None) -> dict:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_payload(scenario=scenario)

    out_name = label or scenario
    out_path = OUTPUT_DIR / f"data-{out_name}.json"
    out_path.write_text(json.dumps(payload, indent=1))
    # A --label build is a pre-baked vintage snapshot; only a plain scenario build
    # refreshes the default data.json that fetch("data/data.json") falls back to.
    if label is None:
        shutil.copyfile(out_path, OUTPUT_PATH)

    print(
        f"Wrote {out_path.relative_to(REPO_ROOT)}"
        f"{' (+ data.json)' if label is None else ' (vintage)'}: "
        f"scenario={scenario}, {payload['totals']['escalations']} escalations, "
        f"{len(payload['patterns'])} patterns, {len(payload['teams'])} teams"
    )
    return payload


if __name__ == "__main__":
    import sys

    main(scenario=_parse_scenario(sys.argv), label=_parse_label(sys.argv))
