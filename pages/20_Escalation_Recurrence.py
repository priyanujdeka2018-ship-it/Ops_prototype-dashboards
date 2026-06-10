from __future__ import annotations

import pandas as pd
import streamlit as st

from src.metrics import (
    executive_kpis,
    group_metrics_by_team,
    group_metrics_by_work_type,
)
from src.rules import classify_metric, detect_anomalies
from src.charts import health_heatmap, bar_chart, line_chart, stacked_bar_chart
from src.briefing import generate_weekly_ops_briefing
from src.data_loader import load_tables
from src.escalation_patterns import (
    get_pattern_events,
    get_top_patterns,
    summarize_patterns,
)
from src.escalation_briefing import generate_escalation_pattern_briefing
from src.ui_components import (
    SCALE_ACCENT,
    SCALE_BAD,
    SCALE_GOOD,
    SCALE_WARN,
    install_scale_theme, install_command_center_polish,
    render_module_hero,
    render_demo_caption,
    render_decision_strip,
)


install_scale_theme()
install_command_center_polish()



def format_pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def format_float(value: float, decimals: int = 1) -> str:
    return f"{value:.{decimals}f}"


def build_health_table(work_type_metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []

    metric_map = {
        "SLA": ("sla_adherence", "sla_adherence"),
        "Backlog >72h": ("aged_backlog_72h", "aged_backlog_72h"),
        "CSAT": ("csat_trailing_7d", "csat"),
        "Quality": ("average_quality_score", "quality_score"),
        "Escalation Rate": ("escalation_rate_per_1000", "escalation_rate_per_1000"),
        "Rework": ("rework_rate", "rework_rate"),
    }

    for _, row in work_type_metrics.iterrows():
        for display_metric, mapping in metric_map.items():
            source_col, rule_metric = mapping
            value = row[source_col]
            status = classify_metric(rule_metric, value)

            rows.append(
                {
                    "work_type": row["work_type"],
                    "metric": display_metric,
                    "value": value,
                    "status": status,
                }
            )
    return pd.DataFrame(rows)


def prepare_weekly_trend(
    work_items: pd.DataFrame,
    quality_events: pd.DataFrame,
    escalation_events: pd.DataFrame,
    selected_work_type: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    wi = work_items[work_items["work_type"] == selected_work_type].copy()
    wi["date_created"] = pd.to_datetime(wi["date_created"])
    wi["week"] = wi["date_created"].dt.to_period("W").dt.start_time

    completed = wi[wi["status"] == "completed"].copy()

    sla_weekly = (
        completed.groupby("week")
        .agg(
            completed_items=("work_item_id", "count"),
            sla_met=("sla_met", lambda x: x.eq(True).sum()),
        )
        .reset_index()
    )
    sla_weekly["sla_adherence"] = sla_weekly["sla_met"] / sla_weekly["completed_items"]

    qe = quality_events[
        quality_events["work_item_id"].isin(wi["work_item_id"])
    ].copy()

    if not qe.empty:
        qe = qe.merge(
            wi[["work_item_id", "date_created"]],
            on="work_item_id",
            how="left",
        )
        qe["week"] = pd.to_datetime(qe["date_created"]).dt.to_period("W").dt.start_time
        quality_weekly = (
            qe.groupby("week")
            .agg(average_quality_score=("quality_score", "mean"))
            .reset_index()
        )
    else:
        quality_weekly = pd.DataFrame(columns=["week", "average_quality_score"])

    ee = escalation_events[escalation_events["work_type"] == selected_work_type].copy()

    if not ee.empty:
        ee["date"] = pd.to_datetime(ee["date"])
        ee["week"] = ee["date"].dt.to_period("W").dt.start_time
        escalation_weekly = (
            ee.groupby("week")
            .agg(escalation_count=("escalation_id", "count"))
            .reset_index()
        )
    else:
        escalation_weekly = pd.DataFrame(columns=["week", "escalation_count"])

    return sla_weekly, quality_weekly, escalation_weekly


def backlog_age_bands(work_items: pd.DataFrame, selected_work_type: str) -> pd.DataFrame:
    wi = work_items[work_items["work_type"] == selected_work_type].copy()
    wi["date_created"] = pd.to_datetime(wi["date_created"])

    open_statuses = ["queued", "in_progress", "blocked"]
    open_items = wi[wi["status"].isin(open_statuses)].copy()

    if open_items.empty:
        return pd.DataFrame({"age_band": [], "count": []})

    open_items["age_hours"] = (
        pd.Timestamp.now() - open_items["date_created"]
    ).dt.total_seconds() / 3600

    bins = [0, 24, 48, 72, 168, 99999]
    labels = ["0-24h", "24-48h", "48-72h", "72h-7d", ">7d"]

    open_items["age_band"] = pd.cut(
        open_items["age_hours"],
        bins=bins,
        labels=labels,
        include_lowest=True,
    )

    return (
        open_items.groupby("age_band", observed=False)
        .size()
        .reset_index(name="count")
    )


def select_optional_filter(df: pd.DataFrame, column: str, label: str, key: str) -> str:
    if column not in df.columns or df.empty:
        return "All"
    values = sorted(df[column].dropna().astype(str).unique())
    return st.selectbox(label, ["All"] + values, key=key)


def apply_optional_filter(df: pd.DataFrame, column: str, selected_value: str) -> pd.DataFrame:
    if selected_value == "All" or column not in df.columns:
        return df
    return df[df[column].astype(str) == selected_value].copy()


def render_module_b(
    escalation_events: pd.DataFrame,
    selected_region: str,
    selected_filter_work_type: str,
) -> None:
    st.markdown("---")
    st.subheader("Escalation Recurrence")
    st.markdown(
        "Operations Health shows where regional health is degrading. Escalation Recurrence checks whether "
        "escalations are isolated incidents or repeat operating-system failures."
    )

    if escalation_events.empty:
        st.info("No escalation events available for the selected health scope.")
        return

    pattern_grain_labels = {
        "work_type_root_cause": "Work type + root cause",
        "work_type_team_root_cause": "Work type + team + root cause",
        "customer_work_type_root_cause": "Customer segment + work type + root cause",
        "team_severity_root_cause": "Team + severity + root cause",
    }

    with st.expander("Escalation filters and pattern definition", expanded=True):
        pattern_grain = st.selectbox(
            "Pattern key definition",
            list(pattern_grain_labels.keys()),
            format_func=lambda value: pattern_grain_labels[value],
            key="module_b_pattern_grain",
        )

        f1, f2, f3 = st.columns(3)
        with f1:
            selected_b_work_type = select_optional_filter(
                escalation_events, "work_type", "Work type", "module_b_work_type"
            )
            selected_b_team = select_optional_filter(
                escalation_events, "team_id", "Team", "module_b_team"
            )
        with f2:
            selected_b_customer = select_optional_filter(
                escalation_events,
                "customer_segment",
                "Customer segment",
                "module_b_customer",
            )
            selected_b_severity = select_optional_filter(
                escalation_events, "severity", "Severity", "module_b_severity"
            )
        with f3:
            selected_b_root_cause = select_optional_filter(
                escalation_events,
                "root_cause_category",
                "Root cause category",
                "module_b_root_cause",
            )
            selected_b_status = select_optional_filter(
                escalation_events, "status", "Status", "module_b_status"
            )

    filtered_escalations = escalation_events.copy()
    for column, selected_value in [
        ("work_type", selected_b_work_type),
        ("team_id", selected_b_team),
        ("customer_segment", selected_b_customer),
        ("severity", selected_b_severity),
        ("root_cause_category", selected_b_root_cause),
        ("status", selected_b_status),
    ]:
        filtered_escalations = apply_optional_filter(
            filtered_escalations, column, selected_value
        )

    if filtered_escalations.empty:
        st.info("No escalation events match the selected filters.")
        return

    pattern_summary = summarize_patterns(
        filtered_escalations,
        pattern_grain=pattern_grain,
    )

    if pattern_summary.empty:
        st.info("No escalation patterns found for the selected filters.")
        return

    recurring_statuses = {"Recurring", "Accelerating", "Resolved"}
    recurring_clusters = pattern_summary[
        pattern_summary["recurrence_status"].isin(recurring_statuses)
    ]
    high_risk_clusters = pattern_summary[
        pattern_summary["risk_level"] == "High recurrence risk"
    ]

    top_work_type = (
        pattern_summary.groupby("work_type")["escalation_count"]
        .sum()
        .sort_values(ascending=False)
        .index[0]
    )
    top_root_cause = (
        pattern_summary.groupby("root_cause_category")["escalation_count"]
        .sum()
        .sort_values(ascending=False)
        .index[0]
    )

    st.markdown("### Recurring Escalation Pattern Summary")
    b1, b2, b3, b4, b5 = st.columns(5)
    b1.metric("Escalations", f"{len(filtered_escalations):,}")
    b2.metric("Recurring Patterns", f"{len(recurring_clusters):,}")
    b3.metric("High-Risk Patterns", f"{len(high_risk_clusters):,}")
    b4.metric("Top Work Type", top_work_type)
    b5.metric("Top Root Cause", top_root_cause)

    st.markdown("### Top Repeat Root Causes")
    c1, c2 = st.columns(2)
    with c1:
        root_cause_chart = (
            pattern_summary.groupby("root_cause_category", as_index=False)
            .agg(escalation_count=("escalation_count", "sum"))
            .sort_values("escalation_count", ascending=False)
            .head(10)
        )
        st.plotly_chart(
            bar_chart(
                root_cause_chart,
                x="root_cause_category",
                y="escalation_count",
                title="Top Recurring Root Causes",
            ),
            use_container_width=True,
        )
    with c2:
        work_type_chart = (
            pattern_summary.groupby("work_type", as_index=False)
            .agg(escalation_count=("escalation_count", "sum"))
            .sort_values("escalation_count", ascending=False)
        )
        st.plotly_chart(
            bar_chart(
                work_type_chart,
                x="work_type",
                y="escalation_count",
                title="Escalation Patterns by Work Type",
            ),
            use_container_width=True,
        )

    c3, c4 = st.columns(2)
    with c3:
        open_events = filtered_escalations[
            filtered_escalations["status"].astype(str).isin(["open", "in_progress"])
        ].copy()
        if not open_events.empty:
            open_severity_chart = (
                open_events.groupby("severity")
                .size()
                .reset_index(name="open_escalations")
                .sort_values("open_escalations", ascending=False)
            )
            st.plotly_chart(
                bar_chart(
                    open_severity_chart,
                    x="severity",
                    y="open_escalations",
                    title="Open Recurring Patterns by Severity",
                ),
                use_container_width=True,
            )
        else:
            st.info("No open escalation events in the selected pattern scope.")
    with c4:
        status_chart = (
            pattern_summary.groupby("recurrence_status")
            .size()
            .reset_index(name="pattern_count")
            .sort_values("pattern_count", ascending=False)
        )
        st.plotly_chart(
            bar_chart(
                status_chart,
                x="recurrence_status",
                y="pattern_count",
                title="Pattern Status Mix",
            ),
            use_container_width=True,
        )

    st.markdown("### Pattern Risk Table")
    display_cols = [
        "pattern_id",
        "pattern_key",
        "escalation_count",
        "severity_mix",
        "unique_teams_impacted",
        "unique_customer_segments_impacted",
        "sev1_count",
        "sev2_count",
        "open_count",
        "avg_days_to_resolve",
        "first_seen_date",
        "latest_escalation_date",
        "recurrence_status",
        "risk_score",
        "risk_level",
        "recommended_action",
    ]
    st.dataframe(pattern_summary[display_cols], use_container_width=True)

    st.markdown("### Pattern Drilldown")
    pattern_options = pattern_summary["pattern_key"].tolist()
    selected_pattern_key = st.selectbox(
        "Select pattern for drilldown",
        pattern_options,
        key="module_b_selected_pattern",
    )
    selected_pattern = pattern_summary[
        pattern_summary["pattern_key"] == selected_pattern_key
    ].iloc[0]
    pattern_events = get_pattern_events(
        filtered_escalations,
        pattern_key=selected_pattern_key,
        pattern_grain=pattern_grain,
    )

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Risk Level", selected_pattern["risk_level"])
    d2.metric("Escalation Count", int(selected_pattern["escalation_count"]))
    d3.metric("Open Count", int(selected_pattern["open_count"]))
    d4.metric("Avg Days to Resolve", selected_pattern["avg_days_to_resolve"])

    st.markdown(f"**Pattern key:** `{selected_pattern_key}`")
    st.markdown(f"**Status:** {selected_pattern['recurrence_status']}")
    st.markdown(f"**Severity mix:** {selected_pattern['severity_mix']}")
    st.markdown(f"**Affected teams:** {selected_pattern['team_id']}")
    st.markdown(f"**Affected customer segments:** {selected_pattern['customer_segment']}")
    st.markdown(f"**Recommended action:** {selected_pattern['recommended_action']}")

    if not pattern_events.empty:
        pattern_events["date"] = pd.to_datetime(pattern_events["date"])
        timeline = (
            pattern_events.sort_values("date")
            .groupby("date")
            .size()
            .reset_index(name="escalation_count")
        )
        st.plotly_chart(
            line_chart(
                timeline,
                x="date",
                y="escalation_count",
                title="Trend of Selected Pattern Over Time",
            ),
            use_container_width=True,
        )

        recent_cols = [
            "escalation_id",
            "date",
            "work_type",
            "team_id",
            "severity",
            "customer_segment",
            "status",
            "days_to_resolve",
            "escalation_summary",
        ]
        st.markdown("#### Recent Escalation Summaries")
        st.dataframe(pattern_events[recent_cols].head(10), use_container_width=True)

    st.markdown("### Recommended Leadership Actions")
    for _, pattern in get_top_patterns(pattern_summary, n=5).iterrows():
        st.warning(
            f"**{pattern['risk_level']} | {pattern['recurrence_status']} | "
            f"{pattern['pattern_key']}**\n\n"
            f"Recommended action: {pattern['recommended_action']}"
        )

    st.markdown("### Generate Escalation Pattern Briefing")
    if st.button("Generate Escalation Pattern Briefing"):
        briefing = generate_escalation_pattern_briefing(
            pattern_summary=pattern_summary,
            selected_scope={
                "region": selected_region,
                "health work type filter": selected_filter_work_type,
                "escalation pattern grain": pattern_grain_labels[pattern_grain],
                "work_type": selected_b_work_type,
                "team_id": selected_b_team,
                "customer_segment": selected_b_customer,
                "severity": selected_b_severity,
                "root_cause_category": selected_b_root_cause,
                "status": selected_b_status,
            },
        )
        st.markdown(briefing)
        st.download_button(
            label="Download Escalation Pattern Briefing as Markdown",
            data=briefing,
            file_name="escalation_pattern_briefing.md",
            mime="text/markdown",
        )



def main() -> None:
    render_module_hero(
        eyebrow="Escalation intelligence",
        title="Escalation Recurrence",
        lede="Move escalation management from ticket closure to repeat-pattern prevention.",
        answer="Which escalation patterns are recurring, accelerating, open, or structurally risky?",
        why="Recurring escalation patterns point to operating-system issues that need ownership, not one-off ticket handling.",
        chips=[
            ("Repeat patterns", SCALE_WARN),
            ("Root cause view", SCALE_ACCENT),
            ("Leadership actions", SCALE_GOOD),
        ],
    )

    render_demo_caption(
        "This tells me whether we are closing tickets or fixing repeat operating-system failures."
    )

    render_decision_strip(
        signal="Recurring and accelerating escalation patterns show where ticket closure is not solving the underlying issue.",
        driver="Pattern keys combine work type, team, customer segment, severity, and root cause.",
        decision="Assign ownership for the highest-risk repeat pattern before more volume flows through the same failure mode.",
        monitor="Open recurrence count, severity mix, blast radius, days to resolve, and repeat root cause.",
    )

    data = load_tables(
        "work_items",
        "teams",
        "contributors",
        "sla_events",
        "quality_events",
        "escalation_events",
        "csat_events",
    )
    if any(df.empty for df in data.values()):
        st.stop()
    work_items = data["work_items"]
    escalation_events = data["escalation_events"]

    st.sidebar.header("Filters")

    regions = sorted(work_items["region"].dropna().astype(str).unique())
    selected_region = st.sidebar.selectbox("Region", regions)

    if "region" in escalation_events.columns:
        escalation_events = escalation_events[
            escalation_events["region"].astype(str) == str(selected_region)
        ].copy()

    work_types = ["All"] + sorted(escalation_events["work_type"].dropna().astype(str).unique())
    selected_filter_work_type = st.sidebar.selectbox("Work Type Filter", work_types)

    if selected_filter_work_type != "All":
        escalation_events = escalation_events[
            escalation_events["work_type"].astype(str) == str(selected_filter_work_type)
        ].copy()

    render_module_b(
        escalation_events=escalation_events,
        selected_region=selected_region,
        selected_filter_work_type=selected_filter_work_type,
    )


if __name__ == "__main__":
    main()
