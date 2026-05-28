"""
Deterministic weekly ops briefing generator.

This module converts KPI metrics and anomaly outputs into a structured
leadership-ready weekly operating briefing.

No LLM API is used. The briefing is deterministic and template-based.
"""

from __future__ import annotations

import pandas as pd


def _fmt_pct(value: float | int | None) -> str:
    if value is None:
        return "N/A"
    return f"{float(value) * 100:.1f}%"


def _fmt_float(value: float | int | None, decimals: int = 1) -> str:
    if value is None:
        return "N/A"
    return f"{float(value):.{decimals}f}"


def _fmt_int(value: float | int | None) -> str:
    if value is None:
        return "N/A"
    return f"{int(value):,}"


def _scope_text(region: str, work_type_filter: str) -> str:
    if work_type_filter == "All":
        return f"Region: {region}; Scope: all work types"
    return f"Region: {region}; Scope: {work_type_filter}"


def _hypothesis_for_anomaly(anomaly_type: str, work_type: str) -> str:
    mapping = {
        "SLA deterioration": (
            f"{work_type}: likely capacity, queue routing, shift coverage, or delay-reason concentration issue."
        ),
        "Aged backlog risk": (
            f"{work_type}: likely backlog aging from capacity shortfall, blocked workflow, or unclear ownership of oldest queues."
        ),
        "Rework spike": (
            f"{work_type}: likely rubric ambiguity, reviewer calibration drift, or higher-complexity task mix."
        ),
        "CSAT below threshold": (
            f"{work_type}: likely customer-visible friction from timeliness, accuracy, calibration, or communication gaps."
        ),
        "Quality decline": (
            f"{work_type}: likely quality calibration drift, gold-task weakness, or inconsistent reviewer interpretation."
        ),
        "Escalation spike": (
            f"{work_type}: likely repeated root-cause pattern, customer requirement change, or unresolved workflow defect."
        ),
    }

    return mapping.get(
        anomaly_type,
        f"{work_type}: requires manager review to isolate operational root cause.",
    )


def _risk_for_anomaly(anomaly_type: str, work_type: str) -> str:
    mapping = {
        "SLA deterioration": (
            f"{work_type}: customer delivery commitments may be missed if throughput and queue aging are not corrected."
        ),
        "Aged backlog risk": (
            f"{work_type}: backlog may convert into SLA misses and customer escalations."
        ),
        "Rework spike": (
            f"{work_type}: review capacity may be consumed by rework instead of new throughput."
        ),
        "CSAT below threshold": (
            f"{work_type}: customer confidence may decline and leadership escalation risk may rise."
        ),
        "Quality decline": (
            f"{work_type}: defect leakage may increase, causing rework, customer dissatisfaction, and calibration escalations."
        ),
        "Escalation spike": (
            f"{work_type}: recurring escalations may create customer trust risk and distract managers from planned execution."
        ),
    }

    return mapping.get(
        anomaly_type,
        f"{work_type}: operational risk may increase without corrective action.",
    )


def _follow_up_questions() -> list[str]:
    return [
        "Which teams are contributing most to the metric movement?",
        "Is the issue caused by volume, capacity, quality calibration, tooling, or workflow handoff?",
        "Which customer segments are affected, and are any strategic accounts exposed?",
        "What is the 48-hour containment action?",
        "What permanent fix should be reviewed in next week's operating meeting?",
    ]


def generate_weekly_ops_briefing(
    kpis: dict,
    work_type_metrics: pd.DataFrame,
    anomalies: pd.DataFrame,
    region: str,
    work_type_filter: str = "All",
) -> str:
    """
    Generate a deterministic weekly operating briefing.

    Args:
        kpis: Executive KPI dictionary from metrics.executive_kpis.
        work_type_metrics: Work-type level metrics DataFrame.
        anomalies: Anomaly DataFrame from rules.detect_anomalies.
        region: Selected region.
        work_type_filter: Selected work type filter from Streamlit sidebar.

    Returns:
        Markdown briefing string.
    """
    scope = _scope_text(region, work_type_filter)

    high_count = 0
    medium_count = 0

    if anomalies is not None and not anomalies.empty:
        high_count = int((anomalies["severity"] == "High").sum())
        medium_count = int((anomalies["severity"] == "Medium").sum())

    top_anomalies = (
        anomalies.head(3).copy()
        if anomalies is not None and not anomalies.empty
        else pd.DataFrame()
    )

    weakest_work_type_text = "No clear weak work type identified."

    if work_type_metrics is not None and not work_type_metrics.empty:
        ranked = work_type_metrics.copy()

        ranked["risk_score"] = (
            (1 - ranked["sla_adherence"].fillna(1.0)) * 30
            + ranked["rework_rate"].fillna(0.0) * 25
            + ranked["escalation_rate_per_1000"].fillna(0.0)
            + ranked["aged_backlog_72h"].fillna(0.0) * 0.2
            + (4.5 - ranked["csat_trailing_7d"].fillna(4.5)).clip(lower=0) * 10
            + (90 - ranked["average_quality_score"].fillna(90)).clip(lower=0) * 0.5
        )

        weakest = ranked.sort_values("risk_score", ascending=False).iloc[0]
        weakest_work_type_text = (
            f"{weakest['work_type']} appears to carry the highest operating risk, "
            f"with SLA {_fmt_pct(weakest['sla_adherence'])}, "
            f"CSAT {_fmt_float(weakest['csat_trailing_7d'])}, "
            f"quality {_fmt_float(weakest['average_quality_score'])}, "
            f"and aged backlog {_fmt_int(weakest['aged_backlog_72h'])}."
        )

    lines: list[str] = []

    lines.append("# Weekly Regional Operations Briefing")
    lines.append("")
    lines.append(f"**{scope}**")
    lines.append("")
    lines.append("## 1. Executive TL;DR")
    lines.append("")
    lines.append(
        f"This week, the region is operating at **{_fmt_pct(kpis.get('sla_adherence'))} SLA adherence**, "
        f"**{_fmt_float(kpis.get('csat_trailing_7d'))} trailing 7-day CSAT**, "
        f"**{_fmt_float(kpis.get('average_quality_score'))} average quality**, "
        f"and **{_fmt_pct(kpis.get('rework_rate'))} rework rate**."
    )
    lines.append(
        f"Current backlog is **{_fmt_int(kpis.get('backlog_count'))}** items, including "
        f"**{_fmt_int(kpis.get('aged_backlog_72h'))}** items older than 72 hours. "
        f"Escalation rate is **{_fmt_float(kpis.get('escalation_rate_per_1000'))} per 1,000 work items**."
    )
    lines.append(
        f"Detected anomalies: **{high_count} high severity** and **{medium_count} medium severity**. "
        f"{weakest_work_type_text}"
    )

    lines.append("")
    lines.append("## 2. Top 3 Anomalies")
    lines.append("")

    if top_anomalies.empty:
        lines.append("No rule-based anomalies were detected for the selected scope.")
    else:
        for idx, anomaly in enumerate(top_anomalies.itertuples(index=False), start=1):
            lines.append(
                f"{idx}. **{anomaly.severity} | {anomaly.work_type} | {anomaly.anomaly_type}**: "
                f"{anomaly.description}"
            )

    lines.append("")
    lines.append("## 3. Likely Causal Hypotheses")
    lines.append("")

    if top_anomalies.empty:
        lines.append(
            "- No anomaly-triggered hypothesis this week. Continue watching SLA, backlog age, CSAT, quality, and rework."
        )
    else:
        for anomaly in top_anomalies.itertuples(index=False):
            lines.append(
                f"- {_hypothesis_for_anomaly(anomaly.anomaly_type, anomaly.work_type)}"
            )

    lines.append("")
    lines.append("## 4. Recommended Actions")
    lines.append("")

    if top_anomalies.empty:
        lines.append("- Maintain weekly operating rhythm and monitor for early movement in backlog, quality, and CSAT.")
    else:
        for anomaly in top_anomalies.itertuples(index=False):
            lines.append(
                f"- **{anomaly.work_type}**: {anomaly.recommended_action}"
            )

    lines.append("")
    lines.append("## 5. Risks If No Action Is Taken")
    lines.append("")

    if top_anomalies.empty:
        lines.append("- No immediate material risk detected, but delayed detection could allow backlog, quality, or CSAT issues to surface late.")
    else:
        for anomaly in top_anomalies.itertuples(index=False):
            lines.append(
                f"- {_risk_for_anomaly(anomaly.anomaly_type, anomaly.work_type)}"
            )

    lines.append("")
    lines.append("## 6. Follow-up Questions for Frontline Managers")
    lines.append("")

    for question in _follow_up_questions():
        lines.append(f"- {question}")

    lines.append("")
    lines.append("## 7. Manager Action Summary")
    lines.append("")
    lines.append(
        "Frontline managers should use the next operating review to validate anomaly drivers, "
        "identify the teams contributing most to risk, and agree on a 48-hour containment plan plus a permanent fix."
    )

    return "\n".join(lines)
