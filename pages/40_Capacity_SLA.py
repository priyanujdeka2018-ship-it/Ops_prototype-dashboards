from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.capacity_briefing import (
    format_capacity_action_card_markdown,
    generate_capacity_action_card,
    generate_capacity_review_briefing,
)
from src.capacity_forecast import (
    build_capacity_trend,
    build_skill_complexity_capacity_features,
    build_team_capacity_features,
    build_work_type_capacity_features,
    get_weekly_capacity_review_queue,
    prepare_capacity_data,
)
from src.charts import bar_chart, line_chart


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


st.set_page_config(
    page_title="Capacity & SLA",
    page_icon="📈",
    layout="wide",
)


@st.cache_data
def read_csv_safe(filename: str) -> pd.DataFrame:
    path = DATA_DIR / filename
    if not path.exists():
        st.warning(f"Missing data file: {path}")
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        st.warning(f"Data file is empty: {path}")
        return pd.DataFrame()


@st.cache_data
def load_capacity_inputs() -> dict[str, pd.DataFrame]:
    return {
        "contributors": read_csv_safe("contributors.csv"),
        "quality_events": read_csv_safe("quality_events.csv"),
        "work_items": read_csv_safe("work_items.csv"),
        "teams": read_csv_safe("teams.csv"),
        "escalation_events": read_csv_safe("escalation_events.csv"),
        "csat_events": read_csv_safe("csat_events.csv"),
        "sla_events": read_csv_safe("sla_events.csv"),
    }


@st.cache_data
def build_module_d_outputs(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    capacity_data = prepare_capacity_data(
        data.get("contributors"),
        data.get("work_items"),
        data.get("teams"),
        data.get("sla_events"),
        data.get("quality_events"),
        data.get("escalation_events"),
    )
    work_types = build_work_type_capacity_features(
        capacity_data,
        contributors=data.get("contributors"),
        teams=data.get("teams"),
        quality_events=data.get("quality_events"),
        escalation_events=data.get("escalation_events"),
    )
    teams = build_team_capacity_features(
        capacity_data,
        contributors=data.get("contributors"),
        teams=data.get("teams"),
        quality_events=data.get("quality_events"),
        escalation_events=data.get("escalation_events"),
    )
    skill_complexity = build_skill_complexity_capacity_features(
        capacity_data,
        contributors=data.get("contributors"),
        quality_events=data.get("quality_events"),
    )
    queue = get_weekly_capacity_review_queue(work_types, teams)
    return {
        "capacity_data": capacity_data,
        "work_types": work_types,
        "teams": teams,
        "skill_complexity": skill_complexity,
        "queue": queue,
    }


def is_missing(value: object) -> bool:
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


def format_pct(value: float | int | None) -> str:
    if is_missing(value):
        return "n/a"
    return f"{float(value) * 100:.1f}%"


def format_float(value: float | int | None, decimals: int = 1) -> str:
    if is_missing(value):
        return "n/a"
    return f"{float(value):.{decimals}f}"


def optional_filter(df: pd.DataFrame, column: str, label: str, key: str) -> str:
    if df.empty or column not in df.columns:
        return "All"
    values = sorted(df[column].dropna().astype(str).unique())
    return st.selectbox(label, ["All"] + values, key=key)


def apply_filter(df: pd.DataFrame, column: str, selected: str) -> pd.DataFrame:
    if selected == "All" or df.empty or column not in df.columns:
        return df
    return df[df[column].astype(str) == selected].copy()


def available_columns(df: pd.DataFrame, columns: list[str]) -> list[str]:
    return [column for column in columns if column in df.columns]


def render_chart(df: pd.DataFrame, x: str, y: str, title: str, chart_type: str = "bar") -> None:
    if df.empty or x not in df.columns or y not in df.columns:
        st.info(f"No data available for {title}.")
        return
    if chart_type == "line":
        st.plotly_chart(line_chart(df, x=x, y=y, title=title), use_container_width=True)
    else:
        st.plotly_chart(bar_chart(df, x=x, y=y, title=title), use_container_width=True)


def render_metric_row(work_types: pd.DataFrame, teams: pd.DataFrame) -> None:
    total_open = int(work_types["open_backlog"].sum()) if "open_backlog" in work_types.columns else 0
    aged_backlog = int(work_types["aged_backlog_72h"].sum()) if "aged_backlog_72h" in work_types.columns else 0
    high_work_types = int(work_types["capacity_risk_level"].astype(str).eq("High capacity risk").sum()) if "capacity_risk_level" in work_types.columns else 0
    high_teams = int(teams["capacity_risk_level"].astype(str).eq("High capacity risk").sum()) if "capacity_risk_level" in teams.columns else 0
    avg_utilization = teams["utilization_rate"].mean() if "utilization_rate" in teams.columns else None
    avg_sla = work_types["sla_adherence_7d"].mean() if "sla_adherence_7d" in work_types.columns else None
    sla_at_risk = int(work_types["forecasted_sla_risk"].astype(str).isin(["SLA at risk", "SLA recovery needed"]).sum()) if "forecasted_sla_risk" in work_types.columns else 0

    if not teams.empty and "capacity_gap" in teams.columns:
        largest_gap_row = teams.sort_values("capacity_gap", ascending=True).iloc[0]
        largest_gap = f"{largest_gap_row.get('team_id', 'n/a')} ({format_float(largest_gap_row.get('capacity_gap', 0))})"
    else:
        largest_gap = "n/a"

    if not teams.empty and "utilization_rate" in teams.columns:
        top_overloaded_team = str(teams.sort_values("utilization_rate", ascending=False).iloc[0].get("team_id", "n/a"))
    else:
        top_overloaded_team = "n/a"

    if not work_types.empty and "capacity_risk_score" in work_types.columns:
        recommended_action = str(work_types.sort_values("capacity_risk_score", ascending=False).iloc[0].get("recommended_capacity_action", "Review capacity"))
    else:
        recommended_action = "Review capacity"

    r1, r2, r3, r4, r5 = st.columns(5)
    r1.metric("Total open backlog", f"{total_open:,}")
    r2.metric("Aged backlog over 72h", f"{aged_backlog:,}")
    r3.metric("High-risk work types", f"{high_work_types:,}")
    r4.metric("High-risk teams", f"{high_teams:,}")
    r5.metric("Average utilization", format_pct(avg_utilization))

    r6, r7, r8, r9, r10 = st.columns(5)
    r6.metric("Average SLA adherence 7d", format_pct(avg_sla))
    r7.metric("Projected SLA at-risk work types", f"{sla_at_risk:,}")
    r8.metric("Largest capacity gap", largest_gap)
    r9.metric("Top overloaded team", top_overloaded_team)
    r10.metric("Next staffing action", recommended_action)


def filter_queue(queue: pd.DataFrame, selected_work_type: str, selected_team: str, selected_region: str, selected_risk: str) -> pd.DataFrame:
    filtered = queue.copy()
    filtered = apply_filter(filtered, "work_type", selected_work_type)
    filtered = apply_filter(filtered, "team_id", selected_team)
    filtered = apply_filter(filtered, "region", selected_region)
    if selected_risk != "All" and not filtered.empty and "risk_level" in filtered.columns:
        filtered = filtered[filtered["risk_level"].astype(str) == selected_risk].copy()
    if not filtered.empty:
        filtered = filtered.sort_values("priority_score", ascending=False).copy()
        filtered["queue_rank"] = range(1, len(filtered) + 1)
    return filtered


def main() -> None:
    st.title("Capacity & SLA")
    st.markdown(
        "Capacity & SLA extends the command center from health, escalation recurrence, and workforce quality "
        "into capacity and SLA forecasting. It is designed for capacity planning, workload balancing, "
        "SLA protection, and quality preservation - not productivity surveillance."
    )

    data = load_capacity_inputs()
    outputs = build_module_d_outputs(data)
    capacity_data = outputs["capacity_data"]
    work_type_summary = outputs["work_types"]
    team_summary = outputs["teams"]
    skill_complexity_summary = outputs["skill_complexity"]
    review_queue = outputs["queue"]

    if capacity_data.empty and work_type_summary.empty and team_summary.empty:
        st.error("No capacity, SLA, quality, or team data is available for Module D.")
        return

    with st.expander("Capacity filters", expanded=True):
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1:
            selected_work_type = optional_filter(work_type_summary, "work_type", "Work type", "module_d_work_type")
        with c2:
            selected_team = optional_filter(team_summary, "team_id", "Team", "module_d_team")
        with c3:
            selected_region = optional_filter(work_type_summary, "region", "Region", "module_d_region")
        with c4:
            selected_skill = optional_filter(skill_complexity_summary, "skill_level", "Skill level", "module_d_skill")
        with c5:
            selected_complexity = optional_filter(skill_complexity_summary, "task_complexity", "Complexity", "module_d_complexity")
        with c6:
            selected_risk = optional_filter(work_type_summary, "capacity_risk_level", "Risk level", "module_d_risk")

    filtered_work_types = work_type_summary.copy()
    for column, selected in [("work_type", selected_work_type), ("region", selected_region)]:
        filtered_work_types = apply_filter(filtered_work_types, column, selected)
    if selected_risk != "All" and not filtered_work_types.empty:
        filtered_work_types = filtered_work_types[filtered_work_types["capacity_risk_level"].astype(str) == selected_risk].copy()

    filtered_teams = team_summary.copy()
    for column, selected in [("work_type", selected_work_type), ("team_id", selected_team), ("region", selected_region)]:
        filtered_teams = apply_filter(filtered_teams, column, selected)
    if selected_risk != "All" and not filtered_teams.empty:
        filtered_teams = filtered_teams[filtered_teams["capacity_risk_level"].astype(str) == selected_risk].copy()

    filtered_skill_complexity = skill_complexity_summary.copy()
    for column, selected in [("work_type", selected_work_type), ("skill_level", selected_skill), ("task_complexity", selected_complexity)]:
        filtered_skill_complexity = apply_filter(filtered_skill_complexity, column, selected)
    if selected_risk != "All" and not filtered_skill_complexity.empty:
        filtered_skill_complexity = filtered_skill_complexity[filtered_skill_complexity["risk_level"].astype(str) == selected_risk].copy()

    filtered_queue = filter_queue(review_queue, selected_work_type, selected_team, selected_region, selected_risk)

    st.markdown("## 1. Executive Capacity and SLA Forecast Summary")
    render_metric_row(filtered_work_types, filtered_teams)

    st.markdown("## 2. Work-Type Capacity Risk Table")
    work_type_cols = [
        "work_type",
        "region",
        "open_backlog",
        "aged_backlog_72h",
        "new_items_7d",
        "completed_items_7d",
        "avg_daily_inflow_7d",
        "avg_daily_throughput_7d",
        "throughput_gap",
        "estimated_days_to_clear_backlog",
        "sla_adherence_7d",
        "rework_rate_7d",
        "active_contributors",
        "capacity_units",
        "required_capacity_units",
        "capacity_gap",
        "utilization_rate",
        "forecasted_sla_risk",
        "capacity_risk_score",
        "capacity_risk_level",
        "recommended_capacity_action",
    ]
    st.dataframe(filtered_work_types[available_columns(filtered_work_types, work_type_cols)], use_container_width=True)

    st.markdown("## 3. Team Capacity Risk Table")
    team_cols = [
        "team_id",
        "work_type",
        "region",
        "manager_name",
        "active_contributors",
        "available_contributors",
        "open_backlog",
        "aged_backlog_72h",
        "new_items_7d",
        "completed_items_7d",
        "avg_daily_inflow_7d",
        "avg_daily_throughput_7d",
        "throughput_gap",
        "estimated_days_to_clear_backlog",
        "sla_adherence_7d",
        "rework_rate_7d",
        "high_complexity_share",
        "expert_complexity_share",
        "low_tenure_share",
        "capacity_gap",
        "utilization_rate",
        "quality_risk_overlay",
        "escalation_risk_overlay",
        "capacity_risk_score",
        "capacity_risk_level",
        "recommended_manager_action",
    ]
    st.dataframe(filtered_teams[available_columns(filtered_teams, team_cols)], use_container_width=True)

    st.markdown("## 4. Capacity Forecast View")
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        render_chart(filtered_work_types, x="work_type", y="capacity_risk_score", title="Capacity Risk by Work Type")
    with chart_col2:
        render_chart(filtered_teams.sort_values("capacity_gap").head(12), x="team_id", y="capacity_gap", title="Capacity Gap by Team")

    chart_col3, chart_col4 = st.columns(2)
    with chart_col3:
        render_chart(filtered_teams.sort_values("utilization_rate", ascending=False).head(12), x="team_id", y="utilization_rate", title="Utilization by Team")
    with chart_col4:
        render_chart(filtered_work_types, x="work_type", y="open_backlog", title="Open Backlog by Work Type")

    chart_col5, chart_col6 = st.columns(2)
    with chart_col5:
        render_chart(filtered_teams.sort_values("aged_backlog_72h", ascending=False).head(12), x="team_id", y="aged_backlog_72h", title="Aged Backlog by Team")
    with chart_col6:
        if not filtered_work_types.empty:
            selected_trend_work_type = st.selectbox(
                "Select work type for SLA and flow trends",
                filtered_work_types["work_type"].dropna().astype(str).tolist(),
                key="module_d_trend_work_type",
            )
            sla_trend = build_capacity_trend(capacity_data, "work_type", selected_trend_work_type)
            render_chart(sla_trend, x="period", y="sla_adherence", title=f"SLA Adherence Trend for {selected_trend_work_type}", chart_type="line")

    chart_col7, chart_col8 = st.columns(2)
    with chart_col7:
        if not filtered_work_types.empty:
            flow_trend = build_capacity_trend(capacity_data, "work_type", selected_trend_work_type)
            flow_melted = flow_trend.melt(id_vars="period", value_vars=["new_items", "completed_items"], var_name="flow_type", value_name="items") if not flow_trend.empty else pd.DataFrame()
            if not flow_melted.empty:
                st.plotly_chart(px.line(flow_melted, x="period", y="items", color="flow_type", markers=True, title=f"Inflow vs Throughput Trend for {selected_trend_work_type}"), use_container_width=True)
            else:
                st.info("No inflow vs throughput trend available.")
    with chart_col8:
        high_complexity_backlog = capacity_data[
            capacity_data["task_complexity"].astype(str).str.lower().isin(["high", "expert"])
            & ~capacity_data["status"].astype(str).isin(["completed", "done", "closed", "resolved"])
        ] if not capacity_data.empty else pd.DataFrame()
        high_complexity_by_team = high_complexity_backlog.groupby("team_id").size().reset_index(name="high_complexity_backlog") if not high_complexity_backlog.empty else pd.DataFrame(columns=["team_id", "high_complexity_backlog"])
        render_chart(high_complexity_by_team.sort_values("high_complexity_backlog", ascending=False).head(12), x="team_id", y="high_complexity_backlog", title="High-Complexity Backlog by Team")

    st.markdown("## Skill / Complexity Capacity Segment Table")
    segment_cols = [
        "work_type",
        "skill_level",
        "task_complexity",
        "active_contributors",
        "completed_items_7d",
        "open_backlog",
        "sla_miss_rate_7d",
        "rework_rate_7d",
        "quality_score",
        "capacity_gap",
        "risk_level",
        "recommended_action",
    ]
    st.dataframe(filtered_skill_complexity[available_columns(filtered_skill_complexity, segment_cols)], use_container_width=True)

    st.markdown("## 5. Team / Work-Type Drilldown")
    d1, d2 = st.columns(2)
    with d1:
        st.markdown("### Work-Type Drilldown")
        if filtered_work_types.empty:
            st.info("No work types match the selected filters.")
        else:
            selected_work_type_drilldown = st.selectbox(
                "Select work type",
                filtered_work_types["work_type"].dropna().astype(str).tolist(),
                key="module_d_work_type_drilldown",
            )
            work_type_row = filtered_work_types[filtered_work_types["work_type"].astype(str) == selected_work_type_drilldown].iloc[0]
            m1, m2, m3 = st.columns(3)
            m1.metric("Forecasted SLA risk", work_type_row.get("forecasted_sla_risk", "n/a"))
            m2.metric("Capacity gap", format_float(work_type_row.get("capacity_gap")))
            m3.metric("Risk score", format_float(work_type_row.get("capacity_risk_score")))
            st.markdown(f"**Open backlog:** {format_float(work_type_row.get('open_backlog'), 0)}")
            st.markdown(f"**Aged backlog:** {format_float(work_type_row.get('aged_backlog_72h'), 0)}")
            st.markdown(f"**Recent inflow:** {format_float(work_type_row.get('new_items_7d'), 0)}")
            st.markdown(f"**Recent throughput:** {format_float(work_type_row.get('completed_items_7d'), 0)}")
            st.markdown(f"**Throughput gap:** {format_float(work_type_row.get('throughput_gap'))} items/day")
            st.markdown(f"**SLA trend:** {format_pct(work_type_row.get('sla_adherence_7d'))}")
            st.markdown(f"**Rework drag:** {format_pct(work_type_row.get('rework_rate_7d'))}")
            st.markdown(f"**Complexity mix:** high/expert {format_pct(work_type_row.get('high_complexity_share'))}")
            st.markdown(f"**Active contributors:** {format_float(work_type_row.get('active_contributors'), 0)}")
            st.markdown(f"**Top risk drivers:** {work_type_row.get('risk_drivers', 'n/a')}")
            st.markdown(f"**Recommended capacity action:** {work_type_row.get('recommended_capacity_action', 'n/a')}")

    with d2:
        st.markdown("### Team Drilldown")
        if filtered_teams.empty:
            st.info("No teams match the selected filters.")
        else:
            selected_team_drilldown = st.selectbox(
                "Select team",
                filtered_teams["team_id"].dropna().astype(str).tolist(),
                key="module_d_team_drilldown",
            )
            team_row = filtered_teams[filtered_teams["team_id"].astype(str) == selected_team_drilldown].iloc[0]
            t1, t2, t3 = st.columns(3)
            t1.metric("Risk level", team_row.get("capacity_risk_level", "n/a"))
            t2.metric("Utilization", format_pct(team_row.get("utilization_rate")))
            t3.metric("Capacity gap", format_float(team_row.get("capacity_gap")))
            st.markdown(f"**Manager:** {team_row.get('manager_name', 'Unknown')}")
            st.markdown(f"**Work type:** `{team_row.get('work_type', 'Unknown')}`")
            st.markdown(f"**Active contributors:** {format_float(team_row.get('active_contributors'), 0)}")
            st.markdown(f"**Open backlog:** {format_float(team_row.get('open_backlog'), 0)}")
            st.markdown(f"**Aged backlog:** {format_float(team_row.get('aged_backlog_72h'), 0)}")
            st.markdown(f"**Recent throughput:** {format_float(team_row.get('completed_items_7d'), 0)}")
            st.markdown(f"**Complexity mix:** high/expert {format_pct(team_row.get('high_complexity_share'))}")
            st.markdown(f"**Low-tenure share:** {format_pct(team_row.get('low_tenure_share'))}")
            st.markdown(f"**Quality risk overlay:** {format_float(team_row.get('quality_risk_overlay'))}")
            st.markdown(f"**Escalation risk overlay:** {format_float(team_row.get('escalation_risk_overlay'))}")
            st.markdown(f"**Recommended manager action:** {team_row.get('recommended_manager_action', 'n/a')}")

    st.markdown("## 6. Weekly Staffing and Capacity Review Queue")
    st.caption(
        "This queue prioritizes staffing, routing, cross-training, backlog burn-down, and SLA recovery decisions. "
        "It is not a worker productivity leaderboard."
    )
    queue_cols = [
        "queue_rank",
        "card_type",
        "subject_id",
        "team_id",
        "work_type",
        "region",
        "risk_level",
        "priority_score",
        "capacity_risk_score",
        "capacity_gap",
        "aged_backlog_72h",
        "throughput_gap",
        "sla_miss_rate_7d",
        "utilization_rate",
        "high_complexity_share",
        "quality_risk_overlay",
        "escalation_risk_overlay",
        "team_blast_radius",
        "recommended_action",
    ]
    if filtered_queue.empty:
        st.info("No weekly staffing and capacity review items match the current filters.")
    else:
        st.dataframe(filtered_queue[available_columns(filtered_queue, queue_cols)], use_container_width=True)

    st.markdown("## 7. Capacity Action Card Generator")
    if filtered_queue.empty:
        st.info("Select a broader filter scope to generate capacity action cards.")
    else:
        card_queue = filtered_queue.copy()
        card_queue["card_selector"] = card_queue["card_type"].astype(str) + " | " + card_queue["subject_id"].astype(str)
        selected_card = st.selectbox(
            "Select queue item for card",
            card_queue["card_selector"].tolist(),
            key="module_d_card_selector",
        )
        queue_row = card_queue[card_queue["card_selector"] == selected_card].iloc[0]
        if queue_row["card_type"] == "Team":
            subject = team_summary[team_summary["team_id"].astype(str) == str(queue_row["subject_id"])].iloc[0]
            card = generate_capacity_action_card(subject, card_type="Team")
        else:
            subject = work_type_summary[work_type_summary["work_type"].astype(str) == str(queue_row["subject_id"])].iloc[0]
            card = generate_capacity_action_card(subject, card_type="Work Type")
        card_markdown = format_capacity_action_card_markdown(card)
        st.markdown(card_markdown)
        st.download_button(
            label="Download Capacity Action Card",
            data=card_markdown,
            file_name=f"{card['subject_id']}_capacity_action_card.md",
            mime="text/markdown",
        )

    st.markdown("## Module D Weekly Staffing and Capacity Briefing")
    briefing = generate_capacity_review_briefing(
        filtered_work_types,
        filtered_teams,
        filtered_skill_complexity,
        filtered_queue,
    )
    st.markdown(briefing)
    st.download_button(
        label="Download Weekly Capacity Briefing",
        data=briefing,
        file_name="module_d_weekly_capacity_briefing.md",
        mime="text/markdown",
    )

    st.markdown("---")
    st.markdown(
        "**Integration story:** Operations Health shows where the operation is unhealthy. Escalation Recurrence shows whether "
        "escalations are recurring system failures. Quality Risk shows whether workforce quality risk is emerging. "
        "Capacity & SLA shows whether capacity, staffing, throughput, and skill mix are sufficient to protect SLA and quality before customer impact."
    )


if __name__ == "__main__":
    main()
