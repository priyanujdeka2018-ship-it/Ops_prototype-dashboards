"""
Build web/public/data/data.json for the TanStack front-end from the real
CSVs in data/, reusing the same metric and pattern-scoring logic that powers
the Streamlit pages so both front-ends show identical numbers.

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
    return round(float(value), digits)


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


def build_payload(scenario: str = "current") -> dict:
    teams = pd.read_csv(DATA_DIR / "teams.csv")
    contributors = pd.read_csv(DATA_DIR / "contributors.csv")
    work_items = pd.read_csv(DATA_DIR / "work_items.csv")
    quality_events = pd.read_csv(DATA_DIR / "quality_events.csv")
    escalation_events = pd.read_csv(DATA_DIR / "escalation_events.csv")
    csat_events = pd.read_csv(DATA_DIR / "csat_events.csv")

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
            "sla_events": int(len(pd.read_csv(DATA_DIR / "sla_events.csv"))),
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
    return payload


def _parse_scenario(argv: list[str]) -> str:
    """Read --scenario VALUE (or --scenario=VALUE) from argv; default current."""
    for i, arg in enumerate(argv):
        if arg == "--scenario" and i + 1 < len(argv):
            return argv[i + 1]
        if arg.startswith("--scenario="):
            return arg.split("=", 1)[1]
    return "current"


def main(scenario: str = "current") -> dict:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_payload(scenario=scenario)

    scenario_path = OUTPUT_DIR / f"data-{scenario}.json"
    scenario_path.write_text(json.dumps(payload, indent=1))
    # Keep data.json as a copy of the most recently built scenario so the
    # default fetch("data/data.json") keeps working for single-scenario deploys.
    shutil.copyfile(scenario_path, OUTPUT_PATH)

    print(
        f"Wrote {scenario_path.relative_to(REPO_ROOT)} (+ data.json): "
        f"scenario={scenario}, {payload['totals']['escalations']} escalations, "
        f"{len(payload['patterns'])} patterns, {len(payload['teams'])} teams"
    )
    return payload


if __name__ == "__main__":
    import sys

    main(scenario=_parse_scenario(sys.argv))
