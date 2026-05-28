"""
Structural fix card generator for Module B v2.

Fix cards convert recurring escalation clusters into weekly leadership decisions.
They are deterministic and do not require an LLM.
"""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd


ROOT_CAUSE_FIX_MAP = {
    "policy_ambiguity": {
        "fix": "SOP rewrite + calibration huddle",
        "owner": "Policy Ops lead + frontline manager",
        "metric": "Repeat escalations from policy ambiguity; reviewer agreement rate",
        "decision": "Approve SOP clarification and require examples for ambiguous cases.",
    },
    "reviewer_misalignment": {
        "fix": "Calibration huddle + QA sampling increase",
        "owner": "Quality lead + reviewer manager",
        "metric": "Reviewer disagreement rate; QA defect rate; rework rate",
        "decision": "Decide whether calibration is required across one team or all regional reviewers.",
    },
    "quality_defect": {
        "fix": "Gold task refresh + QA containment",
        "owner": "QA lead",
        "metric": "Quality score; gold task pass rate; customer defect escalations",
        "decision": "Approve gold task refresh and temporary QA sampling increase.",
    },
    "tooling_issue": {
        "fix": "Tooling change + workaround communication",
        "owner": "Tooling/product operations owner",
        "metric": "Tooling-related escalations; latency/outage incidents; duplicate work rate",
        "decision": "Prioritize tooling fix or approve an interim operational workaround.",
    },
    "customer_requirement_change": {
        "fix": "Customer instruction propagation",
        "owner": "Customer operations lead + training owner",
        "metric": "Instruction-change escalations; affected work types; customer CSAT",
        "decision": "Confirm source of truth for customer instructions and audit propagation.",
    },
    "sla_miss": {
        "fix": "Staffing / capacity correction",
        "owner": "Regional operations manager",
        "metric": "SLA adherence; aged backlog; open escalation count",
        "decision": "Approve temporary staffing rebalance or surge coverage.",
    },
    "workflow_handoff_gap": {
        "fix": "Queue routing rule change + named handoff owner",
        "owner": "Workflow operations lead",
        "metric": "Handoff delay count; queue aging; escalation reopen rate",
        "decision": "Clarify handoff ownership and update routing rules.",
    },
    "capacity_shortfall": {
        "fix": "Staffing / capacity correction",
        "owner": "Regional workforce planning lead",
        "metric": "Backlog age; SLA misses; utilization by team",
        "decision": "Approve capacity rebalance, overtime, or cross-trained backup pool.",
    },
    "gold_task_mismatch": {
        "fix": "Gold task refresh",
        "owner": "Quality systems lead",
        "metric": "Gold task disagreement; QA override rate; customer defect rate",
        "decision": "Approve refresh of outdated gold tasks and sampling logic.",
    },
    "duplicate_assignment": {
        "fix": "Tooling change + queue routing rule change",
        "owner": "Tooling owner + queue ops lead",
        "metric": "Duplicate assignment rate; rework rate; cycle time",
        "decision": "Fix duplicate assignment trigger and audit impacted items.",
    },
    "onboarding_gap": {
        "fix": "Training module update + manager coaching",
        "owner": "Training lead + team manager",
        "metric": "New labeler defect rate; first-30-day quality score; escalation count",
        "decision": "Approve onboarding module update and targeted coaching.",
    },
}


def _safe_text(value: object, default: str = "unknown") -> str:
    if value is None or pd.isna(value):
        return default
    text = str(value).strip()
    return text if text else default


def _root_cause_config(root_cause: str) -> dict[str, str]:
    return ROOT_CAUSE_FIX_MAP.get(
        root_cause,
        {
            "fix": "Manager review + containment and prevention action",
            "owner": "Regional operations manager",
            "metric": "Repeat escalation count; open escalation count; average days to resolve",
            "decision": "Assign owner and define a prevention action for the recurring pattern.",
        },
    )


def generate_fix_card(
    cluster_row: pd.Series,
    cluster_events: pd.DataFrame,
    follow_up_days: int = 14,
) -> dict[str, str]:
    """
    Generate one structural fix card from a semantic cluster summary row.
    """
    root_cause = _safe_text(cluster_row.get("dominant_root_cause"))
    config = _root_cause_config(root_cause)

    incident_count = int(cluster_row.get("incident_count", 0))
    open_count = int(cluster_row.get("open_count", 0))
    sev1_count = int(cluster_row.get("sev1_count", 0))
    sev2_count = int(cluster_row.get("sev2_count", 0))

    affected_work_types = _safe_text(cluster_row.get("affected_work_types"))
    affected_teams = _safe_text(cluster_row.get("affected_teams"))
    affected_customers = _safe_text(cluster_row.get("affected_customer_segments"))

    sample_summaries = []
    if cluster_events is not None and not cluster_events.empty:
        sample_summaries = (
            cluster_events.sort_values("date", ascending=False)["escalation_summary"]
            .dropna()
            .astype(str)
            .head(3)
            .tolist()
        )

    evidence = (
        f"{incident_count} related escalations; {open_count} currently open; "
        f"{sev1_count} sev1 and {sev2_count} sev2 incidents; "
        f"affected work types: {affected_work_types}; "
        f"affected teams: {affected_teams}; "
        f"affected customer segments: {affected_customers}."
    )

    if sample_summaries:
        evidence += " Recent examples: " + " / ".join(sample_summaries)

    follow_up_date = date.today() + timedelta(days=follow_up_days)

    return {
        "cluster_id": _safe_text(cluster_row.get("semantic_cluster_id")),
        "cluster_name": _safe_text(cluster_row.get("cluster_name")),
        "problem_statement": (
            f"Recurring escalations indicate a repeat operating breakdown linked to "
            f"{root_cause.replace('_', ' ')} in {affected_work_types}."
        ),
        "evidence": evidence,
        "likely_root_cause": root_cause,
        "durable_fix_recommendation": config["fix"],
        "owner_suggestion": config["owner"],
        "metric_to_monitor": config["metric"],
        "decision_needed": config["decision"],
        "follow_up_date": str(follow_up_date),
        "risk_level": _safe_text(cluster_row.get("risk_level")),
        "recurrence_status": _safe_text(cluster_row.get("recurrence_status")),
        "risk_score": str(cluster_row.get("risk_score", "")),
    }


def format_fix_card_markdown(fix_card: dict[str, str]) -> str:
    """
    Render a structural fix card as markdown for Streamlit display or download.
    """
    return f"""## Structural Fix Card: {fix_card['cluster_name']}

**Cluster ID:** {fix_card['cluster_id']}  
**Risk Level:** {fix_card['risk_level']}  
**Recurrence Status:** {fix_card['recurrence_status']}  
**Risk Score:** {fix_card['risk_score']}  

### Problem Statement
{fix_card['problem_statement']}

### Evidence
{fix_card['evidence']}

### Likely Root Cause
{fix_card['likely_root_cause']}

### Durable Fix Recommendation
{fix_card['durable_fix_recommendation']}

### Owner Suggestion
{fix_card['owner_suggestion']}

### Metric to Monitor
{fix_card['metric_to_monitor']}

### Decision Needed
{fix_card['decision_needed']}

### Follow-Up Date
{fix_card['follow_up_date']}
"""


def generate_fix_cards(
    cluster_summary: pd.DataFrame,
    clustered_events: pd.DataFrame,
) -> list[dict[str, str]]:
    cards = []

    if cluster_summary.empty:
        return cards

    for _, row in cluster_summary.iterrows():
        cluster_id = row["semantic_cluster_id"]
        events = clustered_events[
            clustered_events["semantic_cluster_id"].astype(str) == str(cluster_id)
        ].copy()
        cards.append(generate_fix_card(row, events))

    return cards
