"""
Module B v2: Semantic escalation clustering.

This module detects recurring escalation patterns even when teams describe
similar problems using different wording. It uses TF-IDF and cosine similarity
so the MVP remains runnable without paid APIs.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import timedelta
from typing import Iterable

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


REQUIRED_COLUMNS = [
    "escalation_id",
    "date",
    "work_type",
    "team_id",
    "severity",
    "customer_segment",
    "escalation_summary",
    "root_cause_category",
    "status",
    "days_to_resolve",
]

OPEN_STATUSES = {"open", "in_progress", "blocked", "reopened"}
RESOLVED_STATUSES = {"resolved", "closed", "done"}

SEVERITY_WEIGHTS = {
    "sev1": 5.0,
    "sev2": 3.0,
    "sev3": 1.5,
    "sev4": 0.5,
}

ROOT_CAUSE_TO_CLUSTER_NAME = {
    "policy_ambiguity": "Policy / SOP ambiguity recurrence",
    "reviewer_misalignment": "Reviewer calibration drift recurrence",
    "quality_defect": "Quality defect recurrence",
    "tooling_issue": "Tooling or workflow system recurrence",
    "customer_requirement_change": "Customer instruction propagation recurrence",
    "sla_miss": "SLA miss recurrence",
    "workflow_handoff_gap": "Workflow handoff gap recurrence",
    "capacity_shortfall": "Capacity shortfall recurrence",
    "gold_task_mismatch": "Gold task mismatch recurrence",
    "duplicate_assignment": "Duplicate work assignment recurrence",
    "onboarding_gap": "New labeler onboarding gap recurrence",
}


def _normalize_text(value: object) -> str:
    if pd.isna(value):
        return "unknown"
    text = str(value).strip().lower()
    return text if text else "unknown"


def _slug(value: object) -> str:
    return _normalize_text(value).replace(" ", "_")


def validate_escalation_events(escalation_events: pd.DataFrame) -> None:
    missing = [col for col in REQUIRED_COLUMNS if col not in escalation_events.columns]
    if missing:
        raise ValueError(
            "Missing required escalation event columns: " + ", ".join(missing)
        )


def prepare_escalation_events(escalation_events: pd.DataFrame) -> pd.DataFrame:
    validate_escalation_events(escalation_events)

    df = escalation_events.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df[df["date"].notna()].copy()

    for col in [
        "work_type",
        "team_id",
        "severity",
        "customer_segment",
        "root_cause_category",
        "status",
    ]:
        df[col] = df[col].map(_slug)

    df["escalation_summary"] = df["escalation_summary"].fillna("").astype(str)
    df["days_to_resolve"] = pd.to_numeric(df["days_to_resolve"], errors="coerce")
    df["is_open"] = df["status"].isin(OPEN_STATUSES)
    df["is_resolved"] = df["status"].isin(RESOLVED_STATUSES)
    df["severity_weight"] = df["severity"].map(SEVERITY_WEIGHTS).fillna(1.0)

    return df.reset_index(drop=True)


def vectorize_escalation_summaries(escalation_events: pd.DataFrame):
    """
    Convert escalation summaries into TF-IDF vectors.

    Later upgrade path:
    - Replace this with sentence-transformers embeddings.
    - Or replace with OpenAI embeddings.
    """
    df = prepare_escalation_events(escalation_events)

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95,
    )

    matrix = vectorizer.fit_transform(df["escalation_summary"].astype(str))
    return df, vectorizer, matrix


def _connected_components(edges: dict[int, set[int]], n_nodes: int) -> list[list[int]]:
    visited = set()
    components = []

    for node in range(n_nodes):
        if node in visited:
            continue

        stack = [node]
        component = []

        while stack:
            current = stack.pop()
            if current in visited:
                continue

            visited.add(current)
            component.append(current)

            for neighbor in edges[current]:
                if neighbor not in visited:
                    stack.append(neighbor)

        components.append(sorted(component))

    return components


def cluster_escalations(
    escalation_events: pd.DataFrame,
    similarity_threshold: float = 0.35,
    min_cluster_size: int = 3,
) -> pd.DataFrame:
    """
    Cluster semantically similar escalations using TF-IDF cosine similarity.

    A simple graph method is used:
    - Each escalation is a node.
    - Two escalations are connected if cosine similarity >= threshold.
    - Connected components become semantic clusters.
    """
    df, vectorizer, matrix = vectorize_escalation_summaries(escalation_events)

    if df.empty:
        return df.assign(
            semantic_cluster_id=[],
            semantic_cluster_size=[],
            semantic_cluster_status=[],
            semantic_similarity_threshold=[],
        )

    similarity = cosine_similarity(matrix)

    edges: dict[int, set[int]] = defaultdict(set)
    n = len(df)

    for i in range(n):
        edges[i].add(i)
        for j in range(i + 1, n):
            if similarity[i, j] >= similarity_threshold:
                edges[i].add(j)
                edges[j].add(i)

    components = _connected_components(edges, n_nodes=n)

    cluster_assignments = {}
    for cluster_number, component in enumerate(
        sorted(components, key=lambda c: (-len(c), c[0])),
        start=1,
    ):
        if len(component) >= min_cluster_size:
            cluster_id = f"SC_{cluster_number:03d}"
            cluster_status = "semantic_cluster"
        elif len(component) == 2:
            cluster_id = f"WATCH_{cluster_number:03d}"
            cluster_status = "watchlist_pair"
        else:
            cluster_id = f"ISO_{cluster_number:03d}"
            cluster_status = "isolated"

        for row_index in component:
            cluster_assignments[row_index] = {
                "semantic_cluster_id": cluster_id,
                "semantic_cluster_size": len(component),
                "semantic_cluster_status": cluster_status,
            }

    assignment_df = pd.DataFrame.from_dict(cluster_assignments, orient="index")
    clustered = pd.concat([df, assignment_df], axis=1)
    clustered["semantic_similarity_threshold"] = similarity_threshold

    return clustered


def _join_unique(values: Iterable[object], limit: int = 5) -> str:
    clean_values = sorted({_slug(value) for value in values if not pd.isna(value)})
    if not clean_values:
        return "unknown"
    if len(clean_values) > limit:
        return ", ".join(clean_values[:limit]) + f", +{len(clean_values) - limit} more"
    return ", ".join(clean_values)


def _severity_mix(group: pd.DataFrame) -> str:
    counts = group["severity"].value_counts().sort_index()
    return ", ".join(f"{severity}: {count}" for severity, count in counts.items())


def _dominant_value(group: pd.DataFrame, column: str) -> str:
    if column not in group.columns or group.empty:
        return "unknown"
    counts = group[column].dropna().astype(str).value_counts()
    if counts.empty:
        return "unknown"
    return counts.index[0]


def name_semantic_cluster(cluster_events: pd.DataFrame) -> str:
    dominant_root_cause = _dominant_value(cluster_events, "root_cause_category")
    dominant_work_type = _dominant_value(cluster_events, "work_type")

    base_name = ROOT_CAUSE_TO_CLUSTER_NAME.get(
        dominant_root_cause,
        dominant_root_cause.replace("_", " ").title() + " recurrence",
    )

    return f"{base_name} — {dominant_work_type.replace('_', ' ').title()}"


def classify_semantic_recurrence(cluster_row: pd.Series) -> str:
    if int(cluster_row.get("last_30d_count", 0)) == 0:
        return "Dormant"

    if int(cluster_row.get("days_since_first_seen", 9999)) <= 14:
        return "New"

    if (
        int(cluster_row.get("last_14d_count", 0))
        > int(cluster_row.get("prior_14d_count", 0))
        and int(cluster_row.get("last_14d_count", 0)) >= 2
    ):
        return "Accelerating"

    if int(cluster_row.get("last_60d_count", 0)) >= 3 and int(cluster_row.get("open_count", 0)) == 0:
        return "Resolved"

    if int(cluster_row.get("last_60d_count", 0)) >= 3:
        return "Recurring"

    if int(cluster_row.get("last_60d_count", 0)) == 2:
        return "Watchlist"

    return "Low activity"


def score_semantic_cluster(cluster_row: pd.Series) -> float:
    avg_days = cluster_row.get("avg_days_to_resolve", 0)
    avg_days = 0 if pd.isna(avg_days) else float(avg_days)

    slow_or_open_penalty = 0.0
    if int(cluster_row.get("open_count", 0)) > 0:
        slow_or_open_penalty += 3.0
    if avg_days >= 7:
        slow_or_open_penalty += 3.0
    elif avg_days >= 4:
        slow_or_open_penalty += 1.5

    acceleration_bonus = 0.0
    if cluster_row.get("recurrence_status") == "Accelerating":
        acceleration_bonus = 3.0
    elif cluster_row.get("recurrence_status") == "Recurring":
        acceleration_bonus = 2.0

    score = (
        float(cluster_row.get("incident_count", 0)) * 2.0
        + float(cluster_row.get("sev1_count", 0)) * 5.0
        + float(cluster_row.get("sev2_count", 0)) * 3.0
        + float(cluster_row.get("open_count", 0)) * 2.0
        + float(cluster_row.get("affected_customer_segment_count", 0)) * 1.5
        + float(cluster_row.get("affected_team_count", 0)) * 1.0
        + slow_or_open_penalty
        + acceleration_bonus
    )

    return round(score, 1)


def classify_risk_level(risk_score: float) -> str:
    if risk_score >= 24:
        return "High recurrence risk"
    if risk_score >= 12:
        return "Medium recurrence risk"
    return "Low recurrence risk"


def summarize_semantic_clusters(
    clustered_events: pd.DataFrame,
    include_isolated: bool = False,
    reference_date: pd.Timestamp | None = None,
) -> pd.DataFrame:
    """
    Summarize semantic clusters into a leadership-ready table.
    """
    if clustered_events.empty:
        return pd.DataFrame()

    df = clustered_events.copy()

    if not include_isolated:
        df = df[df["semantic_cluster_status"] != "isolated"].copy()

    if df.empty:
        return pd.DataFrame()

    reference_date = pd.to_datetime(reference_date or df["date"].max()).normalize()
    df["days_from_reference"] = (reference_date - df["date"].dt.normalize()).dt.days

    rows = []

    for cluster_id, group in df.groupby("semantic_cluster_id", dropna=False):
        first_seen = group["date"].min().normalize()
        latest_seen = group["date"].max().normalize()
        incident_count = int(group["escalation_id"].nunique())

        row = {
            "semantic_cluster_id": cluster_id,
            "cluster_name": name_semantic_cluster(group),
            "semantic_cluster_status": _dominant_value(group, "semantic_cluster_status"),
            "incident_count": incident_count,
            "severity_mix": _severity_mix(group),
            "dominant_work_type": _dominant_value(group, "work_type"),
            "dominant_root_cause": _dominant_value(group, "root_cause_category"),
            "affected_work_types": _join_unique(group["work_type"]),
            "affected_teams": _join_unique(group["team_id"]),
            "affected_customer_segments": _join_unique(group["customer_segment"]),
            "affected_team_count": int(group["team_id"].nunique()),
            "affected_customer_segment_count": int(group["customer_segment"].nunique()),
            "sev1_count": int((group["severity"] == "sev1").sum()),
            "sev2_count": int((group["severity"] == "sev2").sum()),
            "open_count": int(group["is_open"].sum()),
            "resolved_count": int(group["is_resolved"].sum()),
            "avg_days_to_resolve": round(float(group["days_to_resolve"].mean()), 1)
            if group["days_to_resolve"].notna().any()
            else 0.0,
            "first_seen_date": first_seen.date(),
            "latest_escalation_date": latest_seen.date(),
            "recurrence_window_days": int((latest_seen - first_seen).days)
            if incident_count > 1
            else 0,
            "last_14d_count": int(group["days_from_reference"].between(0, 14).sum()),
            "prior_14d_count": int(group["days_from_reference"].between(15, 28).sum()),
            "last_30d_count": int(group["days_from_reference"].between(0, 30).sum()),
            "last_60d_count": int(group["days_from_reference"].between(0, 60).sum()),
            "days_since_first_seen": int((reference_date - first_seen).days),
            "days_since_latest_escalation": int((reference_date - latest_seen).days),
            "sample_summaries": " | ".join(
                group.sort_values("date", ascending=False)["escalation_summary"]
                .dropna()
                .astype(str)
                .head(3)
            ),
        }

        row["recurrence_status"] = classify_semantic_recurrence(pd.Series(row))
        row["risk_score"] = score_semantic_cluster(pd.Series(row))
        row["risk_level"] = classify_risk_level(row["risk_score"])

        rows.append(row)

    summary = pd.DataFrame(rows)
    return summary.sort_values(
        ["risk_score", "last_60d_count", "incident_count"],
        ascending=[False, False, False],
    ).reset_index(drop=True)


def get_cluster_events(
    clustered_events: pd.DataFrame,
    semantic_cluster_id: str,
) -> pd.DataFrame:
    return (
        clustered_events[
            clustered_events["semantic_cluster_id"].astype(str) == str(semantic_cluster_id)
        ]
        .sort_values("date", ascending=False)
        .reset_index(drop=True)
    )
