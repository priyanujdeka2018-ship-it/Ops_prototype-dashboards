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
from src.ui_components import (
    SCALE_ACCENT,
    SCALE_BAD,
    SCALE_GOOD,
    SCALE_WARN,
    install_scale_theme,
    render_action_card as render_scale_action_card,
    render_empty_state as render_scale_empty_state,
    render_metric_grid,
    render_module_hero,
    render_demo_caption,
    render_decision_strip,
    render_operating_principle as render_scale_operating_principle,
    render_pill_row,
    render_priority_card,
    render_section_header as render_scale_section_header,
)


DATA_DIR = Path(__file__).resolve().parent.parent / "data"

WORK_TYPE_COLUMNS = [
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
    "risk_drivers",
    "recommended_capacity_action",
]

TEAM_COLUMNS = [
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
    "risk_drivers",
    "recommended_manager_action",
]

SEGMENT_COLUMNS = [
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

QUEUE_COLUMNS = [
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


def display_value(value: object, default: str = "n/a") -> str:
    if is_missing(value):
        return default
    return str(value)


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


def has_columns(df: pd.DataFrame, columns: list[str]) -> bool:
    return not df.empty and all(column in df.columns for column in columns)


def sorted_unique_values(df: pd.DataFrame, column: str) -> list[str]:
    if df.empty or column not in df.columns:
        return []
    return sorted(df[column].dropna().astype(str).unique().tolist())


def sort_if_available(df: pd.DataFrame, column: str, ascending: bool = False) -> pd.DataFrame:
    if df.empty or column not in df.columns:
        return df
    return df.sort_values(column, ascending=ascending).copy()


def render_module_header() -> None:
    install_scale_theme()
    render_module_hero(
        eyebrow="Capacity & SLA Forecast",
        title="Protect SLA before customer impact lands.",
        lede=(
            "A manager-ready capacity planning view for backlog, inflow, throughput, utilization, "
            "staffing coverage, and skill mix. Styled from the attached Aurora command-center reference."
        ),
        answer=(
            "Whether staffing, throughput, utilization, backlog, and skill mix are sufficient to protect "
            "next-week SLA and quality before customer impact lands."
        ),
        why=(
            "It turns operating signals into decisions: rebalance work, cross-train, add coverage, run "
            "backlog burn-downs, or adjust routing before SLA risk becomes visible to customers."
        ),
        chips=[
            ("Synthetic data", SCALE_GOOD),
            ("Deterministic rules", SCALE_ACCENT),
            ("Explainable scoring", SCALE_WARN),
            ("No surveillance", SCALE_BAD),
        ],
    )


def render_operating_principle() -> None:
    render_scale_operating_principle()


def render_section_header(number: int, title: str, caption: str | None = None) -> None:
    render_scale_section_header(f"Capacity SLA · Section {number}", title, caption)


def render_empty_state(message: str) -> None:
    render_scale_empty_state(message)


def render_table(df: pd.DataFrame, columns: list[str], empty_message: str) -> None:
    selected_columns = available_columns(df, columns)
    if df.empty or not selected_columns:
        render_empty_state(empty_message)
        return
    st.dataframe(df[selected_columns], use_container_width=True)


def render_chart(df: pd.DataFrame, x: str, y: str, title: str, chart_type: str = "bar") -> None:
    if df.empty or x not in df.columns or y not in df.columns:
        render_empty_state(f"No data available for {title}.")
        return
    if chart_type == "line":
        st.plotly_chart(line_chart(df, x=x, y=y, title=title), use_container_width=True)
    else:
        st.plotly_chart(bar_chart(df, x=x, y=y, title=title), use_container_width=True)


def render_driver_badges(value: object) -> None:
    if is_missing(value):
        st.caption("Risk drivers: n/a")
        return
    drivers = [driver.strip() for driver in str(value).split(",") if driver.strip()]
    if not drivers:
        st.caption("Risk drivers: n/a")
        return
    st.markdown(" ".join(f"`{driver}`" for driver in drivers[:5]))


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
        largest_gap = f"{display_value(largest_gap_row.get('team_id'))} ({format_float(largest_gap_row.get('capacity_gap', 0))})"
    else:
        largest_gap = "n/a"

    if not teams.empty and "utilization_rate" in teams.columns:
        top_overloaded_team = display_value(teams.sort_values("utilization_rate", ascending=False).iloc[0].get("team_id"))
    else:
        top_overloaded_team = "n/a"

    if not work_types.empty and "capacity_risk_score" in work_types.columns:
        top_row = work_types.sort_values("capacity_risk_score", ascending=False).iloc[0]
        recommended_action = display_value(top_row.get("recommended_capacity_action"), "Review capacity")
    else:
        recommended_action = "Review capacity"

    render_metric_grid(
        [
            {"label": "Open backlog", "value": f"{total_open:,}", "sub": "Current unresolved work", "color": SCALE_ACCENT},
            {"label": "Aged backlog >72h", "value": f"{aged_backlog:,}", "sub": "Aging queue pressure", "color": SCALE_WARN if aged_backlog else SCALE_GOOD},
            {"label": "High-risk work types", "value": f"{high_work_types:,}", "sub": "Require staffing action", "color": SCALE_BAD if high_work_types else SCALE_GOOD},
            {"label": "High-risk teams", "value": f"{high_teams:,}", "sub": "Manager review needed", "color": SCALE_BAD if high_teams else SCALE_GOOD},
            {"label": "Avg utilization", "value": format_pct(avg_utilization), "sub": "Capacity load signal", "color": SCALE_WARN},
            {"label": "Avg SLA adherence", "value": format_pct(avg_sla), "sub": "7-day SLA performance", "color": SCALE_GOOD},
            {"label": "SLA at-risk types", "value": f"{sla_at_risk:,}", "sub": "Forecasted SLA risk", "color": SCALE_BAD if sla_at_risk else SCALE_GOOD},
            {"label": "Largest capacity gap", "value": largest_gap, "sub": "Most constrained team", "color": SCALE_WARN},
            {"label": "Top overloaded team", "value": top_overloaded_team, "sub": "Utilization hotspot", "color": SCALE_WARN},
            {"label": "Next staffing action", "value": recommended_action, "sub": "Highest scoring work type", "color": SCALE_ACCENT},
        ]
    )


def filter_queue(queue: pd.DataFrame, selected_work_type: str, selected_team: str, selected_region: str, selected_risk: str) -> pd.DataFrame:
    filtered = queue.copy()
    filtered = apply_filter(filtered, "work_type", selected_work_type)
    filtered = apply_filter(filtered, "team_id", selected_team)
    filtered = apply_filter(filtered, "region", selected_region)
    if selected_risk != "All" and not filtered.empty and "risk_level" in filtered.columns:
        filtered = filtered[filtered["risk_level"].astype(str) == selected_risk].copy()
    if not filtered.empty and "priority_score" in filtered.columns:
        filtered = filtered.sort_values("priority_score", ascending=False).copy()
        filtered["queue_rank"] = range(1, len(filtered) + 1)
    return filtered


def render_priority_snapshot(queue: pd.DataFrame) -> None:
    """Render stable executive priority cards for the Capacity SLA overview.

    Uses native Streamlit containers instead of Aurora HTML cards because long
    actions/evidence strings can break the layout in this specific overview block.
    """
    st.markdown("### Highest-priority risks and actions")
    st.caption(
        "Manager-ready staffing, routing, cross-training, and backlog decisions from the current filter scope."
    )

    if queue.empty:
        render_empty_state("No high-priority staffing or capacity items match the selected filters.")
        return

    def _container():
        try:
            return st.container(border=True)
        except TypeError:
            return st.container()

    for _, row in queue.head(3).iterrows():
        card_type = display_value(row.get("card_type"))
        subject_id = display_value(row.get("subject_id"))
        risk_level = display_value(row.get("risk_level"))
        region = display_value(row.get("region"))
        work_type = display_value(row.get("work_type"))
        action = display_value(row.get("recommended_action"), "Review capacity")

        priority_score = format_float(row.get("priority_score"))
        capacity_gap = format_float(row.get("capacity_gap"))
        aged_backlog = format_float(row.get("aged_backlog_72h"), 0)
        throughput_gap = format_float(row.get("throughput_gap"))

        with _container():
            header_left, header_right = st.columns([3, 1])

            with header_left:
                st.markdown(f"#### {card_type} · {subject_id}")
                st.caption(f"Region: {region} · Work type: {work_type}")

            with header_right:
                st.markdown(f"**Risk:** {risk_level}")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Priority score", priority_score)
            m2.metric("Capacity gap", capacity_gap)
            m3.metric("Aged backlog", aged_backlog)
            m4.metric("Throughput gap", throughput_gap)

            st.markdown("**Recommended action**")
            st.write(action)

            st.markdown(
                f"**Evidence:** Capacity gap `{capacity_gap}` · aged backlog `{aged_backlog}` · "
                f"throughput gap `{throughput_gap}`."
            )


def render_overview_tab(work_types: pd.DataFrame, teams: pd.DataFrame, queue: pd.DataFrame) -> None:
    render_section_header(
        1,
        "Executive Summary",
        "The first screen is designed for the interview demo: summary metrics, top operating risks, and manager actions.",
    )
    render_metric_row(work_types, teams)
    render_pill_row([("On target", SCALE_GOOD), ("Watch", SCALE_WARN), ("Breach", SCALE_BAD), ("Decision needed", SCALE_ACCENT)])
    st.divider()
    render_priority_snapshot(queue)
    st.divider()
    render_operating_principle()
    st.markdown(
        "**Command center flow:** Operations Health shows where the operation is unhealthy. Escalation Recurrence shows recurring "
        "operating-system failures. Module B v2 groups similar escalation themes. Quality Risk checks quality drift. "
        "Capacity SLA tests whether staffing, throughput, utilization, and skill mix can protect SLA next week."
    )


def render_work_type_tab(work_types: pd.DataFrame) -> None:
    render_section_header(
        2,
        "Work-Type Risk",
        "Use this view to decide which work types need staffing, routing, cross-training, or burn-down action.",
    )
    c1, c2 = st.columns(2)
    with c1:
        render_chart(sort_if_available(work_types, "capacity_risk_score").head(12), "work_type", "capacity_risk_score", "Capacity Risk by Work Type")
    with c2:
        render_chart(sort_if_available(work_types, "open_backlog").head(12), "work_type", "open_backlog", "Open Backlog by Work Type")

    st.markdown("### Work-type capacity risk table")
    render_table(work_types, WORK_TYPE_COLUMNS, "No work-type capacity risks match the selected filters.")

    if not work_types.empty and "risk_drivers" in work_types.columns:
        st.markdown("### Risk-driver quick read")
        top_rows = sort_if_available(work_types, "capacity_risk_score").head(5)
        for _, row in top_rows.iterrows():
            st.markdown(f"**{display_value(row.get('work_type'))}** - {display_value(row.get('capacity_risk_level'))}")
            render_driver_badges(row.get("risk_drivers"))


def render_team_tab(teams: pd.DataFrame) -> None:
    render_section_header(
        3,
        "Team Risk",
        "Use this view to identify overloaded or under-covered teams without turning the module into individual surveillance.",
    )
    c1, c2 = st.columns(2)
    with c1:
        render_chart(sort_if_available(teams, "capacity_gap", ascending=True).head(12), "team_id", "capacity_gap", "Capacity Gap by Team")
    with c2:
        render_chart(sort_if_available(teams, "utilization_rate").head(12), "team_id", "utilization_rate", "Utilization by Team")

    st.markdown("### Team capacity risk table")
    render_table(teams, TEAM_COLUMNS, "No team capacity risks match the selected filters.")


def render_forecasts_tab(capacity_data: pd.DataFrame, work_types: pd.DataFrame, teams: pd.DataFrame, skill_complexity: pd.DataFrame) -> None:
    render_section_header(
        4,
        "Forecasts and Skill-Mix Coverage",
        "Forecast views connect backlog, inflow, throughput, aged work, utilization, and high-complexity coverage.",
    )
    c1, c2 = st.columns(2)
    with c1:
        render_chart(sort_if_available(teams, "aged_backlog_72h").head(12), "team_id", "aged_backlog_72h", "Aged Backlog by Team")
    with c2:
        if work_types.empty or "work_type" not in work_types.columns:
            render_empty_state("No work types are available for SLA and flow trends.")
        else:
            trend_options = sorted_unique_values(work_types, "work_type")
            selected_trend_work_type = st.selectbox(
                "Select work type for SLA and flow trends",
                trend_options,
                key="module_d_trend_work_type",
            )
            sla_trend = build_capacity_trend(capacity_data, "work_type", selected_trend_work_type)
            render_chart(sla_trend, "period", "sla_adherence", f"SLA Adherence Trend for {selected_trend_work_type}", chart_type="line")

    c3, c4 = st.columns(2)
    with c3:
        if work_types.empty or "work_type" not in work_types.columns:
            render_empty_state("No inflow vs throughput trend available.")
        else:
            trend_options = sorted_unique_values(work_types, "work_type")
            selected_flow_work_type = st.selectbox(
                "Select work type for inflow vs throughput",
                trend_options,
                key="module_d_flow_work_type",
            )
            flow_trend = build_capacity_trend(capacity_data, "work_type", selected_flow_work_type)
            if not flow_trend.empty and {"period", "new_items", "completed_items"}.issubset(flow_trend.columns):
                flow_melted = flow_trend.melt(
                    id_vars="period",
                    value_vars=["new_items", "completed_items"],
                    var_name="flow_type",
                    value_name="items",
                )
                st.plotly_chart(
                    px.line(
                        flow_melted,
                        x="period",
                        y="items",
                        color="flow_type",
                        markers=True,
                        title=f"Inflow vs Throughput Trend for {selected_flow_work_type}",
                    ),
                    use_container_width=True,
                )
            else:
                render_empty_state("No inflow vs throughput trend available.")
    with c4:
        if has_columns(capacity_data, ["task_complexity", "status", "team_id"]):
            high_complexity_backlog = capacity_data[
                capacity_data["task_complexity"].astype(str).str.lower().isin(["high", "expert"])
                & ~capacity_data["status"].astype(str).isin(["completed", "done", "closed", "resolved"])
            ]
            high_complexity_by_team = high_complexity_backlog.groupby("team_id").size().reset_index(name="high_complexity_backlog") if not high_complexity_backlog.empty else pd.DataFrame(columns=["team_id", "high_complexity_backlog"])
            render_chart(sort_if_available(high_complexity_by_team, "high_complexity_backlog").head(12), "team_id", "high_complexity_backlog", "High-Complexity Backlog by Team")
        else:
            render_empty_state("No high-complexity backlog data is available.")

    st.markdown("### Skill / complexity capacity segment table")
    render_table(skill_complexity, SEGMENT_COLUMNS, "No skill or complexity capacity segments match the selected filters.")


def render_drilldown_tab(work_types: pd.DataFrame, teams: pd.DataFrame) -> None:
    render_section_header(
        5,
        "Drilldown",
        "Use drilldowns to explain why a work type or team is flagged and what manager decision is needed.",
    )
    d1, d2 = st.columns(2)
    with d1:
        st.markdown("### Work-type drilldown")
        if work_types.empty or "work_type" not in work_types.columns:
            render_empty_state("No work types match the selected filters.")
        else:
            selected_work_type_drilldown = st.selectbox(
                "Select work type",
                sorted_unique_values(work_types, "work_type"),
                key="module_d_work_type_drilldown",
            )
            work_type_row = work_types[work_types["work_type"].astype(str) == selected_work_type_drilldown].iloc[0]
            m1, m2, m3 = st.columns(3)
            m1.metric("SLA forecast", display_value(work_type_row.get("forecasted_sla_risk")))
            m2.metric("Capacity gap", format_float(work_type_row.get("capacity_gap")))
            m3.metric("Risk score", format_float(work_type_row.get("capacity_risk_score")))
            st.markdown(f"**Open backlog:** {format_float(work_type_row.get('open_backlog'), 0)}")
            st.markdown(f"**Aged backlog:** {format_float(work_type_row.get('aged_backlog_72h'), 0)}")
            st.markdown(f"**Recent inflow:** {format_float(work_type_row.get('new_items_7d'), 0)}")
            st.markdown(f"**Recent throughput:** {format_float(work_type_row.get('completed_items_7d'), 0)}")
            st.markdown(f"**Throughput gap:** {format_float(work_type_row.get('throughput_gap'))} items/day")
            st.markdown(f"**SLA adherence:** {format_pct(work_type_row.get('sla_adherence_7d'))}")
            st.markdown(f"**Rework drag:** {format_pct(work_type_row.get('rework_rate_7d'))}")
            st.markdown(f"**High/expert complexity mix:** {format_pct(work_type_row.get('high_complexity_share'))}")
            st.markdown(f"**Active contributors:** {format_float(work_type_row.get('active_contributors'), 0)}")
            st.markdown("**Risk drivers**")
            render_driver_badges(work_type_row.get("risk_drivers"))
            st.markdown(f"**Recommended staffing action:** {display_value(work_type_row.get('recommended_capacity_action'))}")

    with d2:
        st.markdown("### Team drilldown")
        if teams.empty or "team_id" not in teams.columns:
            render_empty_state("No teams match the selected filters.")
        else:
            selected_team_drilldown = st.selectbox(
                "Select team",
                sorted_unique_values(teams, "team_id"),
                key="module_d_team_drilldown",
            )
            team_row = teams[teams["team_id"].astype(str) == selected_team_drilldown].iloc[0]
            t1, t2, t3 = st.columns(3)
            t1.metric("Risk level", display_value(team_row.get("capacity_risk_level")))
            t2.metric("Utilization", format_pct(team_row.get("utilization_rate")))
            t3.metric("Capacity gap", format_float(team_row.get("capacity_gap")))
            st.markdown(f"**Manager:** {display_value(team_row.get('manager_name'), 'Unknown')}")
            st.markdown(f"**Work type:** `{display_value(team_row.get('work_type'), 'Unknown')}`")
            st.markdown(f"**Active contributors:** {format_float(team_row.get('active_contributors'), 0)}")
            st.markdown(f"**Open backlog:** {format_float(team_row.get('open_backlog'), 0)}")
            st.markdown(f"**Aged backlog:** {format_float(team_row.get('aged_backlog_72h'), 0)}")
            st.markdown(f"**Recent throughput:** {format_float(team_row.get('completed_items_7d'), 0)}")
            st.markdown(f"**High/expert complexity mix:** {format_pct(team_row.get('high_complexity_share'))}")
            st.markdown(f"**Low-tenure share:** {format_pct(team_row.get('low_tenure_share'))}")
            st.markdown(f"**Quality risk overlay:** {format_float(team_row.get('quality_risk_overlay'))}")
            st.markdown(f"**Escalation risk overlay:** {format_float(team_row.get('escalation_risk_overlay'))}")
            st.markdown("**Risk drivers**")
            render_driver_badges(team_row.get("risk_drivers"))
            st.markdown(f"**Recommended manager action:** {display_value(team_row.get('recommended_manager_action'))}")


def render_review_queue_tab(queue: pd.DataFrame) -> None:
    render_section_header(
        6,
        "Weekly Staffing and Capacity Review Queue",
        "Prioritized manager queue for staffing, routing, cross-training, backlog burn-down, and SLA recovery decisions.",
    )
    render_operating_principle()
    render_table(queue, QUEUE_COLUMNS, "No weekly staffing and capacity review items match the current filters.")


def render_capacity_action_card(card: dict[str, object]) -> None:
    render_scale_action_card(card)


def render_action_cards_tab(queue: pd.DataFrame, work_type_summary: pd.DataFrame, team_summary: pd.DataFrame) -> None:
    render_section_header(
        7,
        "Capacity Action Cards",
        "Manager-ready action artifact for the selected capacity risk. The card is deterministic and explainable.",
    )
    if queue.empty:
        render_empty_state("Select a broader filter scope to generate capacity action cards.")
        return

    card_queue = queue.copy()
    card_queue["card_selector"] = card_queue["card_type"].astype(str) + " | " + card_queue["subject_id"].astype(str)
    selected_card = st.selectbox(
        "Select queue item for card",
        card_queue["card_selector"].tolist(),
        key="module_d_card_selector",
    )
    queue_row = card_queue[card_queue["card_selector"] == selected_card].iloc[0]
    card_type = display_value(queue_row.get("card_type"))
    subject_id = display_value(queue_row.get("subject_id"))

    if card_type == "Team":
        subject_matches = team_summary[team_summary["team_id"].astype(str) == subject_id] if "team_id" in team_summary.columns else pd.DataFrame()
        if subject_matches.empty:
            render_empty_state("The selected team is no longer available in the current filtered data.")
            return
        card = generate_capacity_action_card(subject_matches.iloc[0], card_type="Team")
    else:
        subject_matches = work_type_summary[work_type_summary["work_type"].astype(str) == subject_id] if "work_type" in work_type_summary.columns else pd.DataFrame()
        if subject_matches.empty:
            render_empty_state("The selected work type is no longer available in the current filtered data.")
            return
        card = generate_capacity_action_card(subject_matches.iloc[0], card_type="Work Type")

    render_capacity_action_card(card)
    card_markdown = format_capacity_action_card_markdown(card)
    st.download_button(
        label="Download Capacity Action Card",
        data=card_markdown,
        file_name=f"{display_value(card.get('subject_id'), 'capacity')}_capacity_action_card.md",
        mime="text/markdown",
    )


def render_briefing_tab(work_types: pd.DataFrame, teams: pd.DataFrame, skill_complexity: pd.DataFrame, queue: pd.DataFrame) -> None:
    render_section_header(
        8,
        "Weekly Capacity Briefing",
        "Copy-ready briefing for a weekly staffing and capacity review.",
    )
    briefing = generate_capacity_review_briefing(
        work_types,
        teams,
        skill_complexity,
        queue,
    )
    st.markdown(briefing)
    st.download_button(
        label="Download Weekly Capacity Briefing",
        data=briefing,
        file_name="module_d_weekly_capacity_briefing.md",
        mime="text/markdown",
    )


def main() -> None:
    render_module_header()

    render_demo_caption(
        "This prevents reactive staffing decisions after SLA misses have already landed."
    )

    render_decision_strip(
        signal="Next-week SLA risk from backlog, inflow, throughput, staffing, and skill mix.",
        driver="Capacity gaps, aged backlog, utilization pressure, rework drag, and complex-work coverage.",
        decision="Approve staffing, routing, cross-training, or backlog burn-down before customer impact.",
        monitor="Capacity gap, utilization, SLA adherence, aged backlog, and high-complexity coverage.",
    )

    data = load_capacity_inputs()
    outputs = build_module_d_outputs(data)
    capacity_data = outputs["capacity_data"]
    work_type_summary = outputs["work_types"]
    team_summary = outputs["teams"]
    skill_complexity_summary = outputs["skill_complexity"]
    review_queue = outputs["queue"]

    if capacity_data.empty and work_type_summary.empty and team_summary.empty:
        st.error("No capacity, SLA, quality, or team data is available for Capacity SLA.")
        return

    with st.expander("Filters", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            selected_work_type = optional_filter(work_type_summary, "work_type", "Work type", "module_d_work_type")
            selected_team = optional_filter(team_summary, "team_id", "Team", "module_d_team")
        with c2:
            selected_region = optional_filter(work_type_summary, "region", "Region", "module_d_region")
            selected_risk = optional_filter(work_type_summary, "capacity_risk_level", "Risk level", "module_d_risk")
        with c3:
            selected_skill = optional_filter(skill_complexity_summary, "skill_level", "Skill level", "module_d_skill")
            selected_complexity = optional_filter(skill_complexity_summary, "task_complexity", "Complexity", "module_d_complexity")

    filtered_work_types = work_type_summary.copy()
    for column, selected in [("work_type", selected_work_type), ("region", selected_region)]:
        filtered_work_types = apply_filter(filtered_work_types, column, selected)
    if selected_risk != "All" and not filtered_work_types.empty and "capacity_risk_level" in filtered_work_types.columns:
        filtered_work_types = filtered_work_types[filtered_work_types["capacity_risk_level"].astype(str) == selected_risk].copy()

    filtered_teams = team_summary.copy()
    for column, selected in [("work_type", selected_work_type), ("team_id", selected_team), ("region", selected_region)]:
        filtered_teams = apply_filter(filtered_teams, column, selected)
    if selected_risk != "All" and not filtered_teams.empty and "capacity_risk_level" in filtered_teams.columns:
        filtered_teams = filtered_teams[filtered_teams["capacity_risk_level"].astype(str) == selected_risk].copy()

    filtered_skill_complexity = skill_complexity_summary.copy()
    for column, selected in [("work_type", selected_work_type), ("skill_level", selected_skill), ("task_complexity", selected_complexity)]:
        filtered_skill_complexity = apply_filter(filtered_skill_complexity, column, selected)
    if selected_risk != "All" and not filtered_skill_complexity.empty and "risk_level" in filtered_skill_complexity.columns:
        filtered_skill_complexity = filtered_skill_complexity[filtered_skill_complexity["risk_level"].astype(str) == selected_risk].copy()

    filtered_queue = filter_queue(review_queue, selected_work_type, selected_team, selected_region, selected_risk)

    tabs = st.tabs(
        [
            "Overview",
            "Work-Type Risk",
            "Team Risk",
            "Forecasts",
            "Drilldown",
            "Review Queue",
            "Action Cards",
            "Briefing",
        ]
    )

    with tabs[0]:
        render_overview_tab(filtered_work_types, filtered_teams, filtered_queue)
    with tabs[1]:
        render_work_type_tab(filtered_work_types)
    with tabs[2]:
        render_team_tab(filtered_teams)
    with tabs[3]:
        render_forecasts_tab(capacity_data, filtered_work_types, filtered_teams, filtered_skill_complexity)
    with tabs[4]:
        render_drilldown_tab(filtered_work_types, filtered_teams)
    with tabs[5]:
        render_review_queue_tab(filtered_queue)
    with tabs[6]:
        render_action_cards_tab(filtered_queue, work_type_summary, team_summary)
    with tabs[7]:
        render_briefing_tab(filtered_work_types, filtered_teams, filtered_skill_complexity, filtered_queue)


if __name__ == "__main__":
    main()
