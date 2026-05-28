from __future__ import annotations

from pathlib import Path

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


DATA_DIR = Path(__file__).resolve().parent / "data"


st.set_page_config(
    page_title="Scale Regional Ops Health Dashboard",
    page_icon="📊",
    layout="wide",
)


@st.cache_data
def load_data() -> dict[str, pd.DataFrame]:
    required_files = {
        "work_items": "work_items.csv",
        "teams": "teams.csv",
        "contributors": "contributors.csv",
        "sla_events": "sla_events.csv",
        "quality_events": "quality_events.csv",
        "escalation_events": "escalation_events.csv",
        "csat_events": "csat_events.csv",
    }

    data = {}

    for key, filename in required_files.items():
        path = DATA_DIR / filename
        if not path.exists():
            st.error(f"Missing data file: {path}")
            st.stop()
        data[key] = pd.read_csv(path)

    return data


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

    now = pd.Timestamp.now(tz=None)
    open_items["age_hours"] = (pd.Timestamp.now() - open_items["date_created"]).dt.total_seconds() / 3600

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


def main() -> None:
    st.title("Scale Regional Ops Command Center")
    st.subheader("Module A: Regional Operations Health Dashboard")

    data = load_data()

    work_items = data["work_items"]
    teams = data["teams"]
    contributors = data["contributors"]
    quality_events = data["quality_events"]
    escalation_events = data["escalation_events"]
    csat_events = data["csat_events"]
    sla_events = data["sla_events"]

    st.sidebar.header("Filters")

    regions = sorted(work_items["region"].dropna().unique())
    selected_region = st.sidebar.selectbox("Region", regions)

    work_items = work_items[work_items["region"] == selected_region]
    teams = teams[teams["region"] == selected_region]

    work_types = ["All"] + sorted(work_items["work_type"].dropna().unique())
    selected_filter_work_type = st.sidebar.selectbox("Work Type Filter", work_types)

    if selected_filter_work_type != "All":
        work_items = work_items[work_items["work_type"] == selected_filter_work_type]
        teams = teams[teams["work_type"] == selected_filter_work_type]
        quality_events = quality_events[
            quality_events["work_item_id"].isin(work_items["work_item_id"])
        ]
        escalation_events = escalation_events[
            escalation_events["work_type"] == selected_filter_work_type
        ]
        csat_events = csat_events[
            csat_events["work_type"] == selected_filter_work_type
        ]

    st.markdown(
        """
        This dashboard gives a regional operations leader one operating view across
        SLA, backlog, CSAT, quality, rework, and escalation risk.
        """
    )

    kpis = executive_kpis(
        work_items=work_items,
        quality_events=quality_events,
        escalation_events=escalation_events,
        csat_events=csat_events,
    )

    st.markdown("## Executive KPI Tiles")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("SLA Adherence", format_pct(kpis["sla_adherence"]))
    c2.metric("CSAT 7D Avg", format_float(kpis["csat_trailing_7d"]))
    c3.metric("Backlog", f'{kpis["backlog_count"]:,}')
    c4.metric("Aged Backlog >72h", f'{kpis["aged_backlog_72h"]:,}')

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Escalation Rate / 1k", format_float(kpis["escalation_rate_per_1000"]))
    c6.metric("Avg Quality Score", format_float(kpis["average_quality_score"]))
    c7.metric("Rework Rate", format_pct(kpis["rework_rate"]))
    c8.metric("FCR Proxy", format_pct(kpis["fcr_proxy"]))

    st.markdown("## Regional Health Heatmap")

    work_type_metrics = group_metrics_by_work_type(
        work_items=work_items,
        quality_events=quality_events,
        escalation_events=escalation_events,
        csat_events=csat_events,
    )

    health_df = build_health_table(work_type_metrics)

    st.plotly_chart(health_heatmap(health_df), use_container_width=True)

    with st.expander("View work type health table"):
        display_metrics = work_type_metrics.copy()
        pct_cols = ["sla_adherence", "rework_rate", "fcr_proxy"]
        for col in pct_cols:
            display_metrics[col] = display_metrics[col].map(lambda x: f"{x * 100:.1f}%")
        st.dataframe(display_metrics, use_container_width=True)


    st.markdown("## Anomaly Detection Panel")

    anomalies = detect_anomalies(
        work_items=work_items,
        quality_events=quality_events,
        escalation_events=escalation_events,
        csat_events=csat_events,
    )

    if anomalies.empty:
        st.success("No rule-based anomalies detected for the selected scope.")
    else:
        high_count = int((anomalies["severity"] == "High").sum())
        medium_count = int((anomalies["severity"] == "Medium").sum())

        a1, a2, a3 = st.columns(3)
        a1.metric("High Severity Anomalies", high_count)
        a2.metric("Medium Severity Anomalies", medium_count)
        a3.metric("Total Anomalies", len(anomalies))

        st.dataframe(anomalies, use_container_width=True)

        st.markdown("### Leadership Attention Required")
        for _, anomaly in anomalies.head(5).iterrows():
            st.warning(
                f"**{anomaly['severity']} | {anomaly['work_type']} | "
                f"{anomaly['anomaly_type']}** — {anomaly['description']}\n\n"
                f"Recommended action: {anomaly['recommended_action']}"
            )



    st.markdown("## Weekly Ops Briefing Generator")

    st.markdown(
        "Generate a deterministic leadership briefing from the current KPI view, "
        "work type health, and anomaly detection output."
    )

    if st.button("Generate Weekly Ops Briefing"):
        briefing = generate_weekly_ops_briefing(
            kpis=kpis,
            work_type_metrics=work_type_metrics,
            anomalies=anomalies,
            region=selected_region,
            work_type_filter=selected_filter_work_type,
        )

        st.markdown(briefing)

        st.download_button(
            label="Download Briefing as Markdown",
            data=briefing,
            file_name="weekly_ops_briefing.md",
            mime="text/markdown",
        )


    st.markdown("## Work Type Drilldown")

    selectable_work_types = sorted(work_items["work_type"].dropna().unique())
    selected_work_type = st.selectbox(
        "Select work type for drilldown",
        selectable_work_types,
    )

    sla_weekly, quality_weekly, escalation_weekly = prepare_weekly_trend(
        work_items=work_items,
        quality_events=quality_events,
        escalation_events=escalation_events,
        selected_work_type=selected_work_type,
    )

    drill_col1, drill_col2 = st.columns(2)

    with drill_col1:
        if not sla_weekly.empty:
            st.plotly_chart(
                line_chart(
                    sla_weekly,
                    x="week",
                    y="sla_adherence",
                    title=f"SLA Trend: {selected_work_type}",
                ),
                use_container_width=True,
            )
        else:
            st.info("No SLA trend data available.")

    with drill_col2:
        age_df = backlog_age_bands(work_items, selected_work_type)
        if not age_df.empty:
            st.plotly_chart(
                bar_chart(
                    age_df,
                    x="age_band",
                    y="count",
                    title=f"Backlog by Age Band: {selected_work_type}",
                ),
                use_container_width=True,
            )
        else:
            st.info("No open backlog for this work type.")

    drill_col3, drill_col4 = st.columns(2)

    with drill_col3:
        if not quality_weekly.empty:
            st.plotly_chart(
                line_chart(
                    quality_weekly,
                    x="week",
                    y="average_quality_score",
                    title=f"Quality Trend: {selected_work_type}",
                ),
                use_container_width=True,
            )
        else:
            st.info("No quality trend data available.")

    with drill_col4:
        if not escalation_weekly.empty:
            st.plotly_chart(
                bar_chart(
                    escalation_weekly,
                    x="week",
                    y="escalation_count",
                    title=f"Escalation Trend: {selected_work_type}",
                ),
                use_container_width=True,
            )
        else:
            st.info("No escalation trend data available.")

    st.markdown("### Team-Level Comparison")

    team_metrics = group_metrics_by_team(
        work_items=work_items,
        quality_events=quality_events,
        escalation_events=escalation_events,
        csat_events=csat_events,
    )

    team_metrics_for_work_type = team_metrics[
        team_metrics["work_type"] == selected_work_type
    ].copy()

    if not team_metrics_for_work_type.empty:
        st.dataframe(team_metrics_for_work_type, use_container_width=True)

        st.plotly_chart(
            stacked_bar_chart(
                team_metrics_for_work_type,
                x="team_id",
                y="backlog_count",
                color="team_id",
                title=f"Backlog by Team: {selected_work_type}",
            ),
            use_container_width=True,
        )
    else:
        st.info("No team metrics available for this work type.")

    st.markdown("## Team Drilldown")

    team_options = sorted(team_metrics["team_id"].dropna().unique())
    selected_team = st.selectbox("Select team", team_options)

    selected_team_metrics = team_metrics[team_metrics["team_id"] == selected_team]

    if not selected_team_metrics.empty:
        row = selected_team_metrics.iloc[0]

        t1, t2, t3, t4 = st.columns(4)
        t1.metric("Team SLA", format_pct(row["sla_adherence"]))
        t2.metric("Team CSAT 7D", format_float(row["csat_trailing_7d"]))
        t3.metric("Team Quality", format_float(row["average_quality_score"]))
        t4.metric("Team Rework", format_pct(row["rework_rate"]))

        team_contributors = contributors[contributors["team_id"] == selected_team]
        st.metric("Contributor Count", f"{len(team_contributors):,}")

        team_sla_events = sla_events[
            sla_events["work_item_id"].isin(
                work_items[work_items["team_id"] == selected_team]["work_item_id"]
            )
        ].copy()

        st.markdown("### Top Delay Reasons")

        delay_reasons = (
            team_sla_events[team_sla_events["delay_reason"].notna()]
            .groupby("delay_reason")
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
            .head(10)
        )

        if not delay_reasons.empty:
            st.plotly_chart(
                bar_chart(
                    delay_reasons,
                    x="delay_reason",
                    y="count",
                    title=f"Top Delay Reasons: {selected_team}",
                ),
                use_container_width=True,
            )
        else:
            st.info("No SLA delay reasons found for this team.")

        st.markdown("### Recent Escalations")

        team_escalations = escalation_events[
            escalation_events["team_id"] == selected_team
        ].copy()

        if not team_escalations.empty:
            team_escalations["date"] = pd.to_datetime(team_escalations["date"])
            team_escalations = team_escalations.sort_values("date", ascending=False)
            st.dataframe(team_escalations.head(10), use_container_width=True)
        else:
            st.info("No escalations found for this team.")

    st.markdown("---")
    st.caption(
        "Module A only. Future modules: Escalation Pattern Recurrence Detector and Distributed Workforce Quality Scorer."
    )


if __name__ == "__main__":
    main()
