"""
Deterministic escalation pattern briefing generator for Module B.

The briefing turns recurrence-pattern rows into a management narrative without using
an LLM or paid API. This keeps the MVP explainable and runnable locally.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


def _scope_label(selected_scope: dict[str, Any] | None) -> str:
    if not selected_scope:
        return "current dashboard scope"

    parts = []
    for key, value in selected_scope.items():
        if value in (None, "", [], ["All"], "All"):
            continue
        if isinstance(value, list):
            value_text = ", ".join(str(v) for v in value)
        else:
            value_text = str(value)
        parts.append(f"{key}: {value_text}")

    return "; ".join(parts) if parts else "current dashboard scope"


def _top_values(pattern_summary: pd.DataFrame, column: str, n: int = 3) -> list[str]:
    if pattern_summary.empty or column not in pattern_summary.columns:
        return []

    exploded = (
        pattern_summary.assign(_value=pattern_summary[column].astype(str).str.split(", "))
        .explode("_value")
        .groupby("_value", dropna=False)["escalation_count"]
        .sum()
        .sort_values(ascending=False)
        .head(n)
    )
    return [f"{idx} ({int(count)} escalations)" for idx, count in exploded.items()]


def _format_pattern(row: pd.Series, rank: int) -> str:
    return (
        f"{rank}. **{row['pattern_key']}** — {row['risk_level']} "
        f"({row['recurrence_status']}, score {row['risk_score']}). "
        f"Escalations: {int(row['escalation_count'])}; open: {int(row['open_count'])}; "
        f"sev1/sev2: {int(row['sev1_count'])}/{int(row['sev2_count'])}; "
        f"avg days to resolve: {row['avg_days_to_resolve']}. "
        f"Action: {row['recommended_action']}"
    )


def _systemic_cause_line(pattern_summary: pd.DataFrame) -> str:
    root_causes = _top_values(pattern_summary, "root_cause_category", n=3)
    work_types = _top_values(pattern_summary, "work_type", n=3)

    if not root_causes:
        return "No systemic cause is visible from the selected scope yet."

    return (
        "The strongest recurring drivers are "
        + "; ".join(root_causes)
        + ". The most affected work types are "
        + ("; ".join(work_types) if work_types else "not yet concentrated")
        + "."
    )


def generate_escalation_pattern_briefing(
    pattern_summary: pd.DataFrame,
    selected_scope: dict[str, Any] | None = None,
) -> str:
    """
    Generate an explainable Module B leadership briefing from pattern_summary.

    Expected input is the DataFrame returned by src.escalation_patterns.summarize_patterns.
    """
    scope = _scope_label(selected_scope)

    if pattern_summary.empty:
        return (
            "## Escalation Pattern Briefing\n\n"
            f"**Scope:** {scope}\n\n"
            "### Executive TL;DR\n"
            "No escalation patterns were found for the selected scope. Continue monitoring, "
            "but there is no repeat escalation theme requiring leadership review right now.\n"
        )

    df = pattern_summary.copy().sort_values("risk_score", ascending=False)
    top = df.head(5)

    total_patterns = len(df)
    high_risk = int((df["risk_level"] == "High recurrence risk").sum())
    accelerating = int((df["recurrence_status"] == "Accelerating").sum())
    recurring = int(df["recurrence_status"].isin(["Recurring", "Accelerating"]).sum())
    open_patterns = int((df["open_count"] > 0).sum())

    top_pattern = top.iloc[0]

    lines = [
        "## Escalation Pattern Briefing",
        "",
        f"**Scope:** {scope}",
        "",
        "### Executive TL;DR",
        (
            f"Module B detected **{total_patterns} repeat-pattern candidates**. "
            f"There are **{high_risk} high-risk patterns**, **{accelerating} accelerating patterns**, "
            f"and **{open_patterns} patterns with unresolved escalations**. "
            f"The top leadership item is **{top_pattern['pattern_key']}**."
        ),
        "",
        "### Top Recurring Patterns",
    ]

    for rank, (_, row) in enumerate(top.iterrows(), start=1):
        lines.append(_format_pattern(row, rank))

    lines.extend(
        [
            "",
            "### Likely Systemic Causes",
            _systemic_cause_line(df),
            "",
            "### Recommended Leadership Actions",
            "1. Review the highest-risk recurring pattern in the next weekly ops retro and assign one accountable owner.",
            "2. Separate containment from prevention: close open escalations now, but also fix the SOP, routing, calibration, staffing, or tooling driver.",
            "3. Ask frontline managers to bring three recent examples for the top pattern so the team can validate the root-cause hypothesis.",
            "4. Track whether recurrence falls over the next two operating reviews, not only whether the current tickets close.",
            "",
            "### Risks If Not Addressed",
            "- Recurring escalations may be misread as isolated customer issues.",
            "- Open or slow-to-resolve patterns can compound into SLA, CSAT, and quality degradation.",
            "- Teams may spend capacity on repeat containment instead of structural prevention.",
            "",
            "### Questions for Frontline Managers",
            "- What changed in SOP, customer instructions, staffing, tooling, or reviewer calibration before the pattern increased?",
            "- Are the same teams or customer segments repeatedly affected?",
            "- What prevention action will make the next escalation less likely, not merely faster to close?",
            "- What metric will prove the fix is durable in the next weekly review?",
        ]
    )

    return "\n".join(lines)
