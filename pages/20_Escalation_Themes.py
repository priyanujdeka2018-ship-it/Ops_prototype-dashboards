from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.charts import bar_chart, line_chart
from src.escalation_semantic_clusters import (
    cluster_escalations,
    get_cluster_events,
    summarize_semantic_clusters,
)
from src.fix_cards import generate_fix_card, format_fix_card_markdown


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


st.set_page_config(
    page_title="Escalation Themes",
    page_icon="🧭",
    layout="wide",
)


@st.cache_data
def load_escalations() -> pd.DataFrame:
    path = DATA_DIR / "escalation_events.csv"
    if not path.exists():
        st.error(f"Missing file: {path}")
        st.stop()

    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


def optional_filter(df: pd.DataFrame, column: str, label: str, key: str) -> str:
    if column not in df.columns or df.empty:
        return "All"
    values = sorted(df[column].dropna().astype(str).unique())
    return st.selectbox(label, ["All"] + values, key=key)


def apply_filter(df: pd.DataFrame, column: str, selected: str) -> pd.DataFrame:
    if selected == "All" or column not in df.columns:
        return df
    return df[df[column].astype(str) == selected].copy()


def main() -> None:
    st.title("Escalation Themes")

    st.markdown(
        """
        This view extends deterministic escalation recurrence into semantic clustering.
        It uses TF-IDF and cosine similarity to group escalations that describe similar
        operating breakdowns even when the wording is different.
        """
    )

    escalations = load_escalations()

    with st.expander("Filters and clustering settings", expanded=True):
        c1, c2, c3 = st.columns(3)

        with c1:
            selected_work_type = optional_filter(
                escalations, "work_type", "Work type", "v2_work_type"
            )
            selected_team = optional_filter(
                escalations, "team_id", "Team", "v2_team"
            )

        with c2:
            selected_customer = optional_filter(
                escalations, "customer_segment", "Customer segment", "v2_customer"
            )
            selected_severity = optional_filter(
                escalations, "severity", "Severity", "v2_severity"
            )

        with c3:
            selected_root_cause = optional_filter(
                escalations, "root_cause_category", "Root cause", "v2_root_cause"
            )
            selected_status = optional_filter(
                escalations, "status", "Status", "v2_status"
            )

        s1, s2 = st.columns(2)
        with s1:
            similarity_threshold = st.slider(
                "Semantic similarity threshold",
                min_value=0.10,
                max_value=0.90,
                value=0.35,
                step=0.05,
                help="Higher values create stricter clusters. Lower values group more escalations together.",
            )
        with s2:
            min_cluster_size = st.slider(
                "Minimum recurring cluster size",
                min_value=2,
                max_value=8,
                value=3,
                step=1,
                help="Clusters smaller than this become watchlist or isolated records.",
            )

    filtered = escalations.copy()

    for column, selected in [
        ("work_type", selected_work_type),
        ("team_id", selected_team),
        ("customer_segment", selected_customer),
        ("severity", selected_severity),
        ("root_cause_category", selected_root_cause),
        ("status", selected_status),
    ]:
        filtered = apply_filter(filtered, column, selected)

    if filtered.empty:
        st.info("No escalation events match the selected filters.")
        return

    clustered_events = cluster_escalations(
        filtered,
        similarity_threshold=similarity_threshold,
        min_cluster_size=min_cluster_size,
    )

    cluster_summary = summarize_semantic_clusters(
        clustered_events,
        include_isolated=False,
    )

    if cluster_summary.empty:
        st.info("No semantic clusters found. Lower the similarity threshold or reduce the minimum cluster size.")
        return

    recurring = cluster_summary[
        cluster_summary["recurrence_status"].isin(["Recurring", "Accelerating", "Resolved"])
    ]
    high_risk = cluster_summary[cluster_summary["risk_level"] == "High recurrence risk"]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Filtered Escalations", f"{len(filtered):,}")
    k2.metric("Semantic Clusters", f"{len(cluster_summary):,}")
    k3.metric("Recurring Clusters", f"{len(recurring):,}")
    k4.metric("High-Risk Clusters", f"{len(high_risk):,}")

    st.markdown("## Semantic Cluster Summary")

    display_cols = [
        "semantic_cluster_id",
        "cluster_name",
        "incident_count",
        "severity_mix",
        "dominant_work_type",
        "dominant_root_cause",
        "affected_team_count",
        "affected_customer_segment_count",
        "open_count",
        "avg_days_to_resolve",
        "last_60d_count",
        "recurrence_status",
        "risk_score",
        "risk_level",
    ]

    st.dataframe(cluster_summary[display_cols], use_container_width=True)

    st.markdown("## Cluster Charts")

    c1, c2 = st.columns(2)

    with c1:
        root_cause_chart = (
            cluster_summary.groupby("dominant_root_cause", as_index=False)
            .agg(incident_count=("incident_count", "sum"))
            .sort_values("incident_count", ascending=False)
        )
        st.plotly_chart(
            bar_chart(
                root_cause_chart,
                x="dominant_root_cause",
                y="incident_count",
                title="Semantic Clusters by Root Cause",
            ),
            use_container_width=True,
        )

    with c2:
        work_type_chart = (
            cluster_summary.groupby("dominant_work_type", as_index=False)
            .agg(incident_count=("incident_count", "sum"))
            .sort_values("incident_count", ascending=False)
        )
        st.plotly_chart(
            bar_chart(
                work_type_chart,
                x="dominant_work_type",
                y="incident_count",
                title="Semantic Clusters by Work Type",
            ),
            use_container_width=True,
        )

    st.markdown("## Cluster Drilldown")

    selected_cluster_id = st.selectbox(
        "Select semantic cluster",
        cluster_summary["semantic_cluster_id"].tolist(),
    )

    selected_cluster = cluster_summary[
        cluster_summary["semantic_cluster_id"] == selected_cluster_id
    ].iloc[0]

    cluster_events = get_cluster_events(clustered_events, selected_cluster_id)

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Risk Level", selected_cluster["risk_level"])
    d2.metric("Incidents", int(selected_cluster["incident_count"]))
    d3.metric("Open", int(selected_cluster["open_count"]))
    d4.metric("Avg Days to Resolve", selected_cluster["avg_days_to_resolve"])

    st.markdown(f"**Cluster name:** {selected_cluster['cluster_name']}")
    st.markdown(f"**Recurrence status:** {selected_cluster['recurrence_status']}")
    st.markdown(f"**Affected teams:** {selected_cluster['affected_teams']}")
    st.markdown(f"**Affected customer segments:** {selected_cluster['affected_customer_segments']}")

    if not cluster_events.empty:
        timeline = (
            cluster_events.sort_values("date")
            .groupby("date")
            .size()
            .reset_index(name="incident_count")
        )

        st.plotly_chart(
            line_chart(
                timeline,
                x="date",
                y="incident_count",
                title="Selected Semantic Cluster Over Time",
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
            "root_cause_category",
            "status",
            "days_to_resolve",
            "escalation_summary",
        ]

        st.markdown("### Recent Escalations in Cluster")
        st.dataframe(cluster_events[recent_cols].head(20), use_container_width=True)

    st.markdown("## Structural Fix Card")

    fix_card = generate_fix_card(selected_cluster, cluster_events)
    fix_card_markdown = format_fix_card_markdown(fix_card)

    st.markdown(fix_card_markdown)

    st.download_button(
        label="Download Structural Fix Card",
        data=fix_card_markdown,
        file_name=f"{selected_cluster_id}_structural_fix_card.md",
        mime="text/markdown",
    )

    st.markdown("## Weekly Retro Queue")

    retro_queue = cluster_summary.sort_values(
        ["risk_score", "open_count", "last_60d_count"],
        ascending=[False, False, False],
    ).head(10)

    st.dataframe(
        retro_queue[
            [
                "semantic_cluster_id",
                "cluster_name",
                "incident_count",
                "open_count",
                "last_60d_count",
                "recurrence_status",
                "risk_score",
                "risk_level",
                "dominant_root_cause",
            ]
        ],
        use_container_width=True,
    )


if __name__ == "__main__":
    main()
