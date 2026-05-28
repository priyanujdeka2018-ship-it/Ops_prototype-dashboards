"""
Deterministic briefing and coaching-card utilities for Module C.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import pandas as pd


def _as_dict(row: pd.Series | dict[str, Any]) -> dict[str, Any]:
    if isinstance(row, pd.Series):
        return row.to_dict()
    return dict(row)


def _value(data: dict[str, Any], *keys: str, default: Any = "n/a") -> Any:
    for key in keys:
        value = data.get(key)
        if value is not None and not pd.isna(value):
            return value
    return default


def _fmt_pct(value: Any) -> str:
    if value is None or value == "n/a" or pd.isna(value):
        return "n/a"
    return f"{float(value) * 100:.1f}%"


def _fmt_num(value: Any, decimals: int = 1) -> str:
    if value is None or value == "n/a" or pd.isna(value):
        return "n/a"
    return f"{float(value):.{decimals}f}"


def _primary_driver(data: dict[str, Any]) -> str:
    drivers = str(data.get("risk_drivers", "")).strip()
    if not drivers or drivers == "Within expected range":
        return "Quality signals are within expected range"
    return drivers.split(",")[0].strip()


def _metric_to_monitor(driver: str) -> str:
    mapping = {
        "Low gold task pass rate": "Gold task pass rate",
        "Team gold task fail rate": "Gold task pass rate",
        "High reviewer override rate": "Reviewer override rate",
        "Team reviewer override rate": "Reviewer override rate",
        "Low peer agreement": "Peer agreement score",
        "High rework rate": "Rework rate",
        "Team rework rate": "Rework rate",
        "Recent quality drop": "Recent quality score",
        "Team-wide drift": "Team quality score trend",
        "Low tenure plus high complexity": "Ramp quality and complexity mix",
        "Low-tenure concentration": "Low-tenure cohort quality",
        "High-risk contributor concentration": "High-risk contributor count",
    }
    return mapping.get(driver, "Quality score and rework rate")


def _owner_suggestion(card_type: str, driver: str) -> str:
    if card_type == "Team":
        if "reviewer" in driver.lower() or "peer" in driver.lower() or "calibration" in driver.lower():
            return "Quality lead + team manager"
        if "tenure" in driver.lower() or "training" in driver.lower():
            return "Training lead + team manager"
        return "Team manager + regional ops lead"
    if "reviewer" in driver.lower() or "peer" in driver.lower():
        return "Quality lead + direct manager"
    return "Direct manager + quality coach"


def _decision_needed(card_type: str, driver: str) -> str:
    if card_type == "Team":
        if "reviewer" in driver.lower() or "peer" in driver.lower():
            return "Whether to run team-wide calibration or targeted reviewer coaching"
        if "tenure" in driver.lower():
            return "Whether to slow ramp on high-complexity tasks for low-tenure contributors"
        return "Whether to run a team calibration huddle or targeted manager action plan"
    if "tenure" in driver.lower():
        return "Whether to adjust task mix while coaching is completed"
    if "sample" in driver.lower():
        return "Whether additional QA samples are needed before action"
    return "Whether to use targeted coaching or calibration support"


def generate_quality_coaching_card(
    subject_row: pd.Series | dict[str, Any],
    card_type: str | None = None,
    follow_up_days: int = 14,
) -> dict[str, Any]:
    """Generate a deterministic contributor or team coaching/calibration card."""
    data = _as_dict(subject_row)
    inferred_type = card_type or str(data.get("card_type", "Contributor"))
    subject_id = _value(data, "subject_id", "contributor_id", "team_id")
    risk_level = _value(data, "risk_level", "team_risk_level")
    risk_score = _value(data, "risk_score", "team_risk_score", default=0)
    quality_delta = _value(data, "quality_delta", default="n/a")
    avg_quality = _value(data, "avg_quality_score", default="n/a")
    driver = _primary_driver(data)
    action = _value(data, "recommended_action", "recommended_manager_action", default="Continue monitoring")

    evidence_parts = [
        f"average quality score {_fmt_num(avg_quality)}",
        f"gold task fail rate {_fmt_pct(_value(data, 'gold_task_fail_rate', default='n/a'))}",
        f"reviewer override rate {_fmt_pct(_value(data, 'reviewer_override_rate', default='n/a'))}",
        f"rework rate {_fmt_pct(_value(data, 'rework_rate', default='n/a'))}",
        f"peer agreement {_fmt_num(_value(data, 'avg_peer_agreement_score', default='n/a'), 2)}",
    ]

    if quality_delta != "n/a":
        signal_summary = (
            f"Quality score changed by {_fmt_num(quality_delta)} points in the recent 30-day window."
        )
    else:
        signal_summary = (
            f"Current quality score is {_fmt_num(avg_quality)} with risk score {_fmt_num(risk_score)}."
        )

    return {
        "card_type": inferred_type,
        "subject_id": subject_id,
        "risk_level": risk_level,
        "quality_signal_summary": signal_summary,
        "evidence": "; ".join(evidence_parts) + ".",
        "likely_driver": driver,
        "recommended_action": action,
        "owner_suggestion": _owner_suggestion(inferred_type, driver),
        "metric_to_monitor": _metric_to_monitor(driver),
        "decision_needed": _decision_needed(inferred_type, driver),
        "follow_up_date": (date.today() + timedelta(days=follow_up_days)).isoformat(),
    }


def format_quality_coaching_card_markdown(card: dict[str, Any]) -> str:
    """Render a coaching card as Markdown."""
    return f"""### Quality Coaching and Calibration Card

**Card type:** {card['card_type']}  
**Subject ID:** {card['subject_id']}  
**Risk level:** {card['risk_level']}  

**Quality signal summary:** {card['quality_signal_summary']}

**Evidence:** {card['evidence']}

**Likely driver:** {card['likely_driver']}

**Recommended coaching or system action:** {card['recommended_action']}

**Owner suggestion:** {card['owner_suggestion']}

**Metric to monitor:** {card['metric_to_monitor']}

**Decision needed:** {card['decision_needed']}

**Follow-up date:** {card['follow_up_date']}
"""


def generate_quality_review_briefing(
    contributor_quality_summary: pd.DataFrame,
    team_quality_summary: pd.DataFrame,
    work_type_quality_summary: pd.DataFrame,
    weekly_queue: pd.DataFrame,
) -> str:
    """Generate a deterministic weekly Module C review briefing."""
    contributors = contributor_quality_summary.copy()
    teams = team_quality_summary.copy()
    work_types = work_type_quality_summary.copy()
    queue = weekly_queue.copy()

    high_contributors = 0 if contributors.empty else int(contributors["risk_level"].astype(str).eq("High quality risk").sum())
    high_teams = 0 if teams.empty else int(teams["team_risk_level"].astype(str).eq("High quality risk").sum())
    avg_quality = "n/a" if contributors.empty else _fmt_num(contributors["avg_quality_score"].mean())

    if not work_types.empty and "work_type_risk_score" in work_types.columns:
        top_work_type_row = work_types.sort_values("work_type_risk_score", ascending=False).iloc[0]
        top_work_type = top_work_type_row.get("work_type", "n/a")
        top_work_type_action = top_work_type_row.get("recommended_action", "Review quality sampling")
    else:
        top_work_type = "n/a"
        top_work_type_action = "Review quality sampling"

    if not queue.empty:
        top_queue = queue.head(5)
        queue_lines = [
            f"- {row['card_type']} `{row['subject_id']}`: {row['risk_level']} | {row['recommended_action']}"
            for _, row in top_queue.iterrows()
        ]
    else:
        queue_lines = ["- No high-priority coaching or calibration items in the current filtered scope."]

    return "\n".join(
        [
            "# Module C Weekly Workforce Quality Briefing",
            "",
            "## TL;DR",
            f"- Average contributor quality score: {avg_quality}",
            f"- High-risk contributors: {high_contributors}",
            f"- High-risk teams: {high_teams}",
            f"- Top affected work type: {top_work_type}",
            f"- Recommended system action: {top_work_type_action}",
            "",
            "## Weekly Coaching and Calibration Queue",
            *queue_lines,
            "",
            "## Manager Review Questions",
            "1. Are the highest-risk signals concentrated in one team, cohort, work type, or task-complexity band?",
            "2. Are reviewer overrides and peer agreement pointing to calibration drift?",
            "3. Do low-tenure contributors need a slower ramp or more targeted training?",
            "4. Which action owner will review movement in the next weekly operating rhythm?",
            "",
            "## Operating Principle",
            "Use these signals for coaching, calibration, training, staffing, and SOP improvement. Do not use the queue as a punitive individual leaderboard.",
        ]
    )
