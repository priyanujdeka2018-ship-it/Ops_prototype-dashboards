"""
Deterministic briefing and capacity-action-card utilities for Capacity SLA.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import pandas as pd


def _as_dict(row: pd.Series | dict[str, Any]) -> dict[str, Any]:
    if isinstance(row, pd.Series):
        return row.to_dict()
    return dict(row)


def _is_missing(value: Any) -> bool:
    """Return True for None, pd.NA, NaN, and common missing-value strings."""
    if value is None:
        return True
    if isinstance(value, str) and value.strip().lower() in {"", "n/a", "nan", "none"}:
        return True
    try:
        result = pd.isna(value)
    except (TypeError, ValueError):
        return False
    if isinstance(result, bool):
        return result
    try:
        return bool(result.item())
    except (AttributeError, TypeError, ValueError):
        return False


def _value(data: dict[str, Any], *keys: str, default: Any = "n/a") -> Any:
    for key in keys:
        value = data.get(key)
        if not _is_missing(value):
            return value
    return default


def _fmt_pct(value: Any) -> str:
    if _is_missing(value):
        return "n/a"
    return f"{float(value) * 100:.1f}%"


def _fmt_num(value: Any, decimals: int = 1) -> str:
    if _is_missing(value):
        return "n/a"
    return f"{float(value):.{decimals}f}"


def _primary_driver(data: dict[str, Any]) -> str:
    drivers = str(data.get("risk_drivers", "")).strip()
    if not drivers or drivers == "Within expected range":
        return "Capacity signals are within expected range"
    return drivers.split(",")[0].strip()


def _metric_to_monitor(driver: str) -> str:
    lower = driver.lower()
    if "aged backlog" in lower:
        return "Aged backlog over 72h"
    if "throughput" in lower or "backlog growing" in lower:
        return "Inflow vs throughput gap"
    if "sla" in lower:
        return "SLA adherence and SLA miss rate"
    if "utilization" in lower:
        return "Utilization rate and capacity gap"
    if "complexity" in lower or "expert" in lower:
        return "High-complexity backlog and expert coverage"
    if "rework" in lower:
        return "Rework rate and effective capacity"
    if "quality" in lower:
        return "Quality score, rework rate, and calibration outcomes"
    if "escalation" in lower:
        return "Recurring escalation count and open escalation age"
    return "Backlog, throughput, utilization, and SLA adherence"


def _owner_suggestion(card_type: str, driver: str) -> str:
    lower = driver.lower()
    if "quality" in lower or "rework" in lower:
        return "Team manager + quality lead"
    if "escalation" in lower:
        return "Regional ops lead + structural fix owner"
    if "complexity" in lower or "expert" in lower:
        return "Team manager + senior reviewer lead"
    if card_type == "Team":
        return "Team manager + regional capacity lead"
    return "Regional capacity lead + affected team managers"


def _decision_needed(card_type: str, driver: str) -> str:
    lower = driver.lower()
    if "throughput" in lower or "backlog" in lower:
        return "Whether to add temporary coverage, reroute work, or run a backlog burn-down sprint"
    if "utilization" in lower:
        return "Whether to rebalance workload before utilization creates SLA or quality risk"
    if "complexity" in lower or "expert" in lower:
        return "Whether to shift complex work to senior contributors or request specialist coverage"
    if "quality" in lower or "rework" in lower:
        return "Whether to pause volume growth until calibration, coaching, or workflow fixes are complete"
    if "escalation" in lower:
        return "Whether to assign a structural fix owner before routing additional volume"
    if card_type == "Team":
        return "Whether the manager needs staffing, routing, or cross-training support this week"
    return "Which staffing, routing, or cross-training action should be approved this week"


def generate_capacity_action_card(
    subject_row: pd.Series | dict[str, Any],
    card_type: str | None = None,
    follow_up_days: int = 7,
) -> dict[str, Any]:
    """Generate a deterministic work-type or team capacity action card."""
    data = _as_dict(subject_row)
    inferred_type = card_type or str(data.get("card_type", "Work Type"))
    subject_id = _value(data, "subject_id", "team_id", "work_type")
    risk_level = _value(data, "risk_level", "capacity_risk_level")
    risk_score = _value(data, "capacity_risk_score", "risk_score", default=0)
    driver = _primary_driver(data)
    action = _value(data, "recommended_action", "recommended_capacity_action", "recommended_manager_action", default="Review capacity")

    open_backlog = _value(data, "open_backlog", default="n/a")
    aged_backlog = _value(data, "aged_backlog_72h", default="n/a")
    sla_adherence = _value(data, "sla_adherence_7d", default="n/a")
    throughput_gap = _value(data, "throughput_gap", default="n/a")
    utilization = _value(data, "utilization_rate", default="n/a")
    capacity_gap = _value(data, "capacity_gap", default="n/a")
    forecasted_sla_risk = _value(data, "forecasted_sla_risk", default="n/a")

    evidence_parts = [
        f"open backlog {_fmt_num(open_backlog, 0)}",
        f"aged backlog {_fmt_num(aged_backlog, 0)}",
        f"SLA adherence {_fmt_pct(sla_adherence)}",
        f"throughput gap {_fmt_num(throughput_gap)} items/day",
        f"utilization {_fmt_pct(utilization)}",
        f"capacity gap {_fmt_num(capacity_gap)} units",
    ]

    if forecasted_sla_risk != "n/a":
        signal_summary = (
            f"Forecast status is {forecasted_sla_risk}; risk score is {_fmt_num(risk_score)}. "
            f"Primary driver: {driver}."
        )
    else:
        signal_summary = f"Capacity risk score is {_fmt_num(risk_score)}. Primary driver: {driver}."

    return {
        "card_type": inferred_type,
        "subject_id": subject_id,
        "risk_level": risk_level,
        "capacity_signal_summary": signal_summary,
        "evidence": "; ".join(evidence_parts) + ".",
        "likely_driver": driver,
        "recommended_staffing_or_routing_action": action,
        "owner_suggestion": _owner_suggestion(inferred_type, driver),
        "metric_to_monitor": _metric_to_monitor(driver),
        "decision_needed": _decision_needed(inferred_type, driver),
        "follow_up_date": (date.today() + timedelta(days=follow_up_days)).isoformat(),
    }


def format_capacity_action_card_markdown(card: dict[str, Any]) -> str:
    """Render a capacity action card as Markdown."""
    return f"""### Capacity Action Card

**Card type:** {card['card_type']}  
**Subject ID:** {card['subject_id']}  
**Risk level:** {card['risk_level']}

**Capacity signal summary:** {card['capacity_signal_summary']}

**Evidence:** {card['evidence']}

**Likely driver:** {card['likely_driver']}

**Recommended staffing or routing action:** {card['recommended_staffing_or_routing_action']}

**Owner suggestion:** {card['owner_suggestion']}

**Metric to monitor:** {card['metric_to_monitor']}

**Decision needed:** {card['decision_needed']}

**Follow-up date:** {card['follow_up_date']}
"""


def generate_capacity_review_briefing(
    work_type_capacity_summary: pd.DataFrame,
    team_capacity_summary: pd.DataFrame,
    skill_complexity_capacity_summary: pd.DataFrame,
    weekly_queue: pd.DataFrame,
) -> str:
    """Generate a deterministic weekly Capacity SLA staffing and capacity briefing."""
    work_types = work_type_capacity_summary.copy()
    teams = team_capacity_summary.copy()
    skill_complexity = skill_complexity_capacity_summary.copy()
    queue = weekly_queue.copy()

    high_work_types = 0 if work_types.empty else int(work_types["capacity_risk_level"].astype(str).eq("High capacity risk").sum())
    high_teams = 0 if teams.empty else int(teams["capacity_risk_level"].astype(str).eq("High capacity risk").sum())
    avg_utilization = "n/a" if teams.empty or "utilization_rate" not in teams.columns else _fmt_pct(teams["utilization_rate"].mean())
    avg_sla = "n/a" if work_types.empty or "sla_adherence_7d" not in work_types.columns else _fmt_pct(work_types["sla_adherence_7d"].mean())

    if not work_types.empty and "capacity_risk_score" in work_types.columns:
        top_work_type_row = work_types.sort_values("capacity_risk_score", ascending=False).iloc[0]
        top_work_type = top_work_type_row.get("work_type", "n/a")
        top_work_type_action = top_work_type_row.get("recommended_capacity_action", "Review capacity")
    else:
        top_work_type = "n/a"
        top_work_type_action = "Review capacity"

    if not teams.empty and "capacity_gap" in teams.columns:
        largest_gap_row = teams.sort_values("capacity_gap", ascending=True).iloc[0]
        largest_gap = f"{largest_gap_row.get('team_id', 'n/a')} ({_fmt_num(largest_gap_row.get('capacity_gap', 0))} units)"
    else:
        largest_gap = "n/a"

    if not queue.empty:
        queue_lines = [
            f"- {row['card_type']} `{row['subject_id']}`: {row['risk_level']} | {row['recommended_action']}"
            for _, row in queue.head(6).iterrows()
        ]
    else:
        queue_lines = ["- No high-priority staffing or capacity items in the current filtered scope."]

    if not skill_complexity.empty and "risk_level" in skill_complexity.columns:
        high_skill_segments = int(skill_complexity["risk_level"].astype(str).eq("High capacity risk").sum())
    else:
        high_skill_segments = 0

    return "\n".join(
        [
            "# Weekly Staffing and Capacity Briefing",
            "",
            "## TL;DR",
            f"- High-risk work types: {high_work_types}",
            f"- High-risk teams: {high_teams}",
            f"- High-risk skill/complexity segments: {high_skill_segments}",
            f"- Average utilization: {avg_utilization}",
            f"- Average SLA adherence 7d: {avg_sla}",
            f"- Largest team capacity gap: {largest_gap}",
            f"- Top affected work type: {top_work_type}",
            f"- Recommended next staffing action: {top_work_type_action}",
            "",
            "## Weekly Staffing and Capacity Review Queue",
            *queue_lines,
            "",
            "## Manager Review Questions",
            "1. Is backlog growing because inflow rose, throughput fell, or capacity mix is mismatched?",
            "2. Are aged backlog and SLA miss risk concentrated by work type, team, shift, skill level, or complexity?",
            "3. Does quality or rework risk reduce effective capacity before additional volume is routed?",
            "4. Which staffing, cross-training, rerouting, or burn-down decision needs approval this week?",
            "",
            "## Operating Principle",
            "Use these signals for capacity planning, workload balancing, SLA protection, and quality preservation. Do not use the review queue as a worker productivity leaderboard.",
        ]
    )
