from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.ui_components import render_demo_caption, render_decision_strip, install_scale_theme, install_command_center_polish

from src.charts import bar_chart, line_chart
from src.quality_briefing import (
    format_quality_coaching_card_markdown,
    generate_quality_coaching_card,
    generate_quality_review_briefing,
)
from src.workforce_quality import (
    build_contributor_quality_features,
    build_quality_trend,
    build_team_quality_features,
    build_work_type_quality_features,
    get_weekly_quality_review_queue,
    prepare_quality_data,
)


install_scale_theme()
install_command_center_polish()


DATA_DIR = Path(__file__).resolve().parent.parent / "data"



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
def load_quality_inputs() -> dict[str, pd.DataFrame]:
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
def build_module_c_outputs(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    quality = prepare_quality_data(
        data.get("contributors"),
        data.get("quality_events"),
        data.get("work_items"),
        data.get("teams"),
        data.get("escalation_events"),
    )
    contributors = build_contributor_quality_features(
        data.get("contributors"),
        data.get("quality_events"),
        data.get("work_items"),
        data.get("teams"),
    )
    teams = build_team_quality_features(
        data.get("contributors"),
        data.get("quality_events"),
        data.get("work_items"),
        data.get("teams"),
        contributor_quality_summary=contributors,
    )
    work_types = build_work_type_quality_features(contributors, teams)
    queue = get_weekly_quality_review_queue(contributors, teams)
    return {
        "quality": quality,
        "contributors": contributors,
        "teams": teams,
        "work_types": work_types,
        "queue": queue,
    }


def format_pct(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{float(value) * 100:.1f}%"


def format_float(value: float | int | None, decimals: int = 1) -> str:
    if value is None or pd.isna(value):
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


def top_risk_driver(contributors: pd.DataFrame, teams: pd.DataFrame) -> str:
    values: list[str] = []
    for df in [contributors, teams]:
        if not df.empty and "risk_drivers" in df.columns:
            for raw_value in df["risk_drivers"].dropna().astype(str):
                for driver in raw_value.split(","):
                    driver = driver.strip()
                    if driver and driver != "Within expected range" and driver != "Insufficient sample":
                        values.append(driver)
    if not values:
        return "Within expected range"
    return pd.Series(values).value_counts().index[0]


def render_metric_row(contributors: pd.DataFrame, teams: pd.DataFrame, work_types: pd.DataFrame) -> None:
    total_contributors = len(contributors)
    active_contributors = (
        contributors["active_status"].astype(str).eq("active").sum()
        if "active_status" in contributors.columns
        else total_contributors
    )
    high_risk_contributors = (
        contributors["risk_level"].astype(str).eq("High quality risk").sum()
        if "risk_level" in contributors.columns
        else 0
    )
    high_risk_teams = (
        teams["team_risk_level"].astype(str).eq("High quality risk").sum()
        if "team_risk_level" in teams.columns
        else 0
    )
    avg_quality = contributors["avg_quality_score"].mean() if "avg_quality_score" in contributors.columns else None
    fail_rate = contributors["gold_task_fail_rate"].mean() if "gold_task_fail_rate" in contributors.columns else None
    override_rate = contributors["reviewer_override_rate"].mean() if "reviewer_override_rate" in contributors.columns else None
    peer_agreement = contributors["avg_peer_agreement_score"].mean() if "avg_peer_agreement_score" in contributors.columns else None

    if not work_types.empty and "work_type_risk_score" in work_types.columns:
        top_work_type = work_types.sort_values("work_type_risk_score", ascending=False).iloc[0]["work_type"]
    else:
        top_work_type = "n/a"

    r1, r2, r3, r4, r5 = st.columns(5)
    r1.metric("Total contributors", f"{total_contributors:,}")
    r2.metric("Active contributors", f"{int(active_contributors):,}")
    r3.metric("High-risk contributors", f"{int(high_risk_contributors):,}")
    r4.metric("High-risk teams", f"{int(high_risk_teams):,}")
    r5.metric("Average quality score", format_float(avg_quality))

    r6, r7, r8, r9, r10 = st.columns(5)
    r6.metric("Gold task fail rate", format_pct(fail_rate))
    r7.metric("Reviewer override rate", format_pct(override_rate))
    r8.metric("Average peer agreement", format_float(peer_agreement, 2))
    r9.metric("Top affected work type", str(top_work_type))
    r10.metric("Top risk driver", top_risk_driver(contributors, teams))


def render_chart(df: pd.DataFrame, x: str, y: str, title: str, chart_type: str = "bar") -> None:
    if df.empty or x not in df.columns or y not in df.columns:
        st.info(f"No data available for {title}.")
        return
    if chart_type == "line":
        st.plotly_chart(line_chart(df, x=x, y=y, title=title), use_container_width=True)
    else:
        st.plotly_chart(bar_chart(df, x=x, y=y, title=title), use_container_width=True)


def filter_queue(queue: pd.DataFrame, selected_work_type: str, selected_team: str, selected_risk: str) -> pd.DataFrame:
    filtered = queue.copy()
    filtered = apply_filter(filtered, "work_type", selected_work_type)
    filtered = apply_filter(filtered, "team_id", selected_team)
    if selected_risk != "All" and not filtered.empty and "risk_level" in filtered.columns:
        filtered = filtered[filtered["risk_level"].astype(str) == selected_risk].copy()
    if not filtered.empty:
        filtered = filtered.sort_values("priority_score", ascending=False).copy()
        filtered["queue_rank"] = range(1, len(filtered) + 1)
    return filtered


def main() -> None:
    st.title("Quality Risk")
    st.markdown(
        "Module C extends the command center from regional health and escalation recurrence "
        "into distributed workforce quality risk. It is designed for coaching, calibration, "
        "training, staffing, and quality-system action — not punitive individual ranking."
    )

    data = load_quality_inputs()
    render_demo_caption(
        "This is calibration and coaching support, not a contributor leaderboard."
    )

    render_decision_strip(
        signal="Quality drift, rework, override, and peer-agreement signals are checked before they create operational drag.",
        driver="Team, work-type, and calibration patterns are prioritized ahead of individual contributor detail.",
        decision="Decide where managers should coach, recalibrate reviewers, or inspect workflow quality gates.",
        monitor="Gold-task fail rate, reviewer override rate, peer agreement, rework rate, and quality score.",
    )

    outputs = build_module_c_outputs(data)
    quality = outputs["quality"]
    contributor_summary = outputs["contributors"]
    team_summary = outputs["teams"]
    work_type_summary = outputs["work_types"]
    review_queue = outputs["queue"]

    if contributor_summary.empty and team_summary.empty:
        st.error("No quality data is available for Module C.")
        return

    with st.expander("Module C filters", expanded=True):
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            selected_work_type = optional_filter(contributor_summary, "work_type", "Work type", "module_c_work_type")
        with c2:
            selected_team = optional_filter(contributor_summary, "team_id", "Team", "module_c_team")
        with c3:
            selected_skill = optional_filter(contributor_summary, "skill_level", "Skill level", "module_c_skill")
        with c4:
            selected_location = optional_filter(contributor_summary, "location_type", "Location type", "module_c_location")
        with c5:
            selected_risk = optional_filter(contributor_summary, "risk_level", "Risk level", "module_c_risk")

    filtered_contributors = contributor_summary.copy()
    for column, selected in [
        ("work_type", selected_work_type),
        ("team_id", selected_team),
        ("skill_level", selected_skill),
        ("location_type", selected_location),
        ("risk_level", selected_risk),
    ]:
        filtered_contributors = apply_filter(filtered_contributors, column, selected)

    filtered_teams = team_summary.copy()
    filtered_teams = apply_filter(filtered_teams, "work_type", selected_work_type)
    filtered_teams = apply_filter(filtered_teams, "team_id", selected_team)
    if selected_risk != "All" and not filtered_teams.empty:
        filtered_teams = filtered_teams[filtered_teams["team_risk_level"].astype(str) == selected_risk].copy()

    filtered_work_types = work_type_summary.copy()
    filtered_work_types = apply_filter(filtered_work_types, "work_type", selected_work_type)
    filtered_queue = filter_queue(review_queue, selected_work_type, selected_team, selected_risk)

    st.markdown("## 1. Executive Workforce Quality Summary")
    render_metric_row(filtered_contributors, filtered_teams, filtered_work_types)

    st.markdown("## 2. Contributor Quality Risk Table")
    contributor_cols = [
        "contributor_id",
        "team_id",
        "work_type",
        "skill_level",
        "tenure_days",
        "sampled_quality_events",
        "avg_quality_score",
        "gold_task_fail_rate",
        "reviewer_override_rate",
        "avg_peer_agreement_score",
        "rework_rate",
        "quality_delta",
        "risk_score",
        "risk_level",
        "risk_status",
        "recommended_action",
    ]
    st.dataframe(
        filtered_contributors[available_columns(filtered_contributors, contributor_cols)],
        use_container_width=True,
    )

    st.markdown("## 3. Team Quality Risk Table")
    team_cols = [
        "team_id",
        "work_type",
        "active_contributors",
        "avg_quality_score",
        "gold_task_fail_rate",
        "reviewer_override_rate",
        "rework_rate",
        "high_risk_contributor_count",
        "quality_drift_flag",
        "team_risk_score",
        "team_risk_level",
        "recommended_manager_action",
    ]
    st.dataframe(
        filtered_teams[available_columns(filtered_teams, team_cols)],
        use_container_width=True,
    )

    st.markdown("## 4. Quality Drift View")
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        render_chart(
            filtered_work_types,
            x="work_type",
            y="work_type_risk_score",
            title="Quality Risk by Work Type",
        )
    with chart_col2:
        high_risk_by_team = (
            filtered_contributors[filtered_contributors["risk_level"].astype(str).eq("High quality risk")]
            .groupby("team_id")
            .size()
            .reset_index(name="high_risk_contributors")
            if not filtered_contributors.empty
            else pd.DataFrame(columns=["team_id", "high_risk_contributors"])
        )
        render_chart(
            high_risk_by_team,
            x="team_id",
            y="high_risk_contributors",
            title="High-Risk Contributors by Team",
        )

    chart_col3, chart_col4 = st.columns(2)
    with chart_col3:
        render_chart(
            filtered_teams.sort_values("gold_task_fail_rate", ascending=False).head(12),
            x="team_id",
            y="gold_task_fail_rate",
            title="Gold Task Fail Rate by Team",
        )
    with chart_col4:
        render_chart(
            filtered_teams.sort_values("reviewer_override_rate", ascending=False).head(12),
            x="team_id",
            y="reviewer_override_rate",
            title="Reviewer Override Rate by Team",
        )

    chart_col5, chart_col6 = st.columns(2)
    with chart_col5:
        render_chart(
            filtered_work_types.sort_values("rework_rate", ascending=False),
            x="work_type",
            y="rework_rate",
            title="Rework Rate by Work Type",
        )
    with chart_col6:
        if not filtered_teams.empty:
            selected_trend_team = st.selectbox(
                "Select team for quality trend",
                filtered_teams["team_id"].dropna().astype(str).tolist(),
                key="module_c_trend_team",
            )
            trend = build_quality_trend(quality, "team_id", selected_trend_team)
            render_chart(
                trend,
                x="period",
                y="avg_quality_score",
                title=f"Quality Trend for {selected_trend_team}",
                chart_type="line",
            )

    st.markdown("## 5. Contributor / Team Drilldown")
    d1, d2 = st.columns(2)

    with d1:
        st.markdown("### Contributor Drilldown")
        if filtered_contributors.empty:
            st.info("No contributors match the selected filters.")
        else:
            selected_contributor = st.selectbox(
                "Select contributor",
                filtered_contributors["contributor_id"].dropna().astype(str).tolist(),
                key="module_c_contributor_drilldown",
            )
            contributor_row = filtered_contributors[
                filtered_contributors["contributor_id"].astype(str) == selected_contributor
            ].iloc[0]
            m1, m2, m3 = st.columns(3)
            m1.metric("Risk level", contributor_row["risk_level"])
            m2.metric("Quality score", format_float(contributor_row["avg_quality_score"]))
            m3.metric("Quality delta", format_float(contributor_row["quality_delta"]))
            st.markdown(f"**Team ID:** `{contributor_row['team_id']}`")
            st.markdown(f"**Work type:** `{contributor_row['work_type']}`")
            st.markdown(f"**Skill level:** {contributor_row['skill_level']}")
            st.markdown(f"**Tenure days:** {format_float(contributor_row['tenure_days'], 0)}")
            st.markdown(f"**Risk drivers:** {contributor_row.get('risk_drivers', 'n/a')}")
            st.markdown(f"**Recommended coaching action:** {contributor_row['recommended_action']}")

            contributor_events = quality[quality["contributor_id"].astype(str) == selected_contributor].copy()
            if not contributor_events.empty:
                event_cols = available_columns(
                    contributor_events,
                    [
                        "event_date",
                        "work_item_id",
                        "quality_score",
                        "gold_task_pass",
                        "reviewer_override",
                        "peer_agreement_score",
                        "rework_required",
                        "task_complexity",
                    ],
                )
                st.markdown("#### Gold task / reviewer history")
                st.dataframe(contributor_events.sort_values("event_date", ascending=False)[event_cols].head(20), use_container_width=True)

                complexity_mix = (
                    contributor_events.groupby("task_complexity")
                    .size()
                    .reset_index(name="event_count")
                )
                render_chart(complexity_mix, "task_complexity", "event_count", "Task Complexity Mix")

    with d2:
        st.markdown("### Team Drilldown")
        if filtered_teams.empty:
            st.info("No teams match the selected filters.")
        else:
            selected_team_drilldown = st.selectbox(
                "Select team",
                filtered_teams["team_id"].dropna().astype(str).tolist(),
                key="module_c_team_drilldown",
            )
            team_row = filtered_teams[filtered_teams["team_id"].astype(str) == selected_team_drilldown].iloc[0]
            t1, t2, t3 = st.columns(3)
            t1.metric("Risk level", team_row["team_risk_level"])
            t2.metric("Quality score", format_float(team_row["avg_quality_score"]))
            t3.metric("High-risk contributors", int(team_row["high_risk_contributor_count"]))
            st.markdown(f"**Work type:** `{team_row['work_type']}`")
            st.markdown(f"**Manager:** {team_row.get('manager_name', 'Unknown')}")
            st.markdown(f"**Active contributors:** {int(team_row.get('active_contributors', 0))}")
            st.markdown(f"**Top risk drivers:** {team_row.get('risk_drivers', 'n/a')}")
            st.markdown(f"**Recommended manager action:** {team_row['recommended_manager_action']}")

            team_trend = build_quality_trend(quality, "team_id", selected_team_drilldown)
            render_chart(
                team_trend,
                x="period",
                y="avg_quality_score",
                title=f"Quality Score Trend for {selected_team_drilldown}",
                chart_type="line",
            )

            team_events = quality[quality["team_id"].astype(str) == selected_team_drilldown].copy()
            if not team_events.empty:
                event_cols = available_columns(
                    team_events,
                    [
                        "event_date",
                        "quality_event_id",
                        "contributor_id",
                        "work_item_id",
                        "quality_score",
                        "gold_task_pass",
                        "reviewer_override",
                        "peer_agreement_score",
                        "rework_required",
                        "task_complexity",
                    ],
                )
                st.markdown("#### Recent quality events")
                st.dataframe(team_events.sort_values("event_date", ascending=False)[event_cols].head(20), use_container_width=True)

    st.markdown("## 6. Weekly Coaching and Calibration Queue")
    st.caption(
        "This queue prioritizes manager review, coaching, calibration, staffing, and SOP decisions. "
        "It should not be used as a punitive leaderboard."
    )
    queue_cols = [
        "queue_rank",
        "card_type",
        "subject_id",
        "team_id",
        "work_type",
        "risk_level",
        "risk_status",
        "priority_score",
        "risk_score",
        "quality_delta",
        "gold_task_fail_rate",
        "reviewer_override_rate",
        "rework_rate",
        "avg_peer_agreement_score",
        "sampled_quality_events",
        "team_blast_radius",
        "recommended_action",
    ]
    if filtered_queue.empty:
        st.info("No coaching or calibration queue items match the current filters.")
    else:
        st.dataframe(filtered_queue[available_columns(filtered_queue, queue_cols)], use_container_width=True)

    st.markdown("## 7. Quality Coaching Card Generator")
    if filtered_queue.empty:
        st.info("Select a broader filter scope to generate coaching or calibration cards.")
    else:
        filtered_queue = filtered_queue.copy()
        filtered_queue["card_selector"] = filtered_queue["card_type"].astype(str) + " | " + filtered_queue["subject_id"].astype(str)
        selected_card = st.selectbox(
            "Select queue item for card",
            filtered_queue["card_selector"].tolist(),
            key="module_c_card_selector",
        )
        queue_row = filtered_queue[filtered_queue["card_selector"] == selected_card].iloc[0]
        if queue_row["card_type"] == "Team":
            subject = team_summary[team_summary["team_id"].astype(str) == str(queue_row["subject_id"])].iloc[0]
            card = generate_quality_coaching_card(subject, card_type="Team")
        else:
            subject = contributor_summary[contributor_summary["contributor_id"].astype(str) == str(queue_row["subject_id"])].iloc[0]
            card = generate_quality_coaching_card(subject, card_type="Contributor")
        card_markdown = format_quality_coaching_card_markdown(card)
        st.markdown(card_markdown)
        st.download_button(
            label="Download Quality Coaching Card",
            data=card_markdown,
            file_name=f"{card['subject_id']}_quality_coaching_card.md",
            mime="text/markdown",
        )

    st.markdown("## Module C Weekly Briefing")
    briefing = generate_quality_review_briefing(
        filtered_contributors,
        filtered_teams,
        filtered_work_types,
        filtered_queue,
    )
    st.markdown(briefing)
    st.download_button(
        label="Download Module C Weekly Briefing",
        data=briefing,
        file_name="module_c_weekly_quality_briefing.md",
        mime="text/markdown",
    )

    st.markdown("---")
    st.markdown(
        "**Integration story:** Operations Health shows where the operation is unhealthy. Escalation Recurrence shows "
        "whether escalations are recurring system failures. Quality Risk shows whether distributed "
        "workforce quality risk is emerging and what coaching, calibration, training, or staffing "
        "action should happen next."
    )


if __name__ == "__main__":
    main()
