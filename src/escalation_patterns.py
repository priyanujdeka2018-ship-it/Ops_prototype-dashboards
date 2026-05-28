"""
Escalation pattern detection for Module B: Escalation Pattern Recurrence Detector.

This module is intentionally deterministic. It groups escalation events into repeat-pattern
keys, scores recurrence risk, classifies pattern status, and recommends leadership actions
without using paid APIs or LLM calls.
"""

from __future__ import annotations

import hashlib
from typing import Iterable

import pandas as pd


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

SEVERITY_SCORE = {
    "sev1": 5.0,
    "sev2": 3.0,
    "sev3": 1.5,
    "sev4": 0.5,
}

PATTERN_GRAINS = {
    "work_type_root_cause": ["work_type", "root_cause_category"],
    "work_type_team_root_cause": ["work_type", "team_id", "root_cause_category"],
    "customer_work_type_root_cause": [
        "customer_segment",
        "work_type",
        "root_cause_category",
    ],
    "team_severity_root_cause": ["team_id", "severity", "root_cause_category"],
}

ROOT_CAUSE_ACTION_MAP = {
    "policy_ambiguity": "Clarify SOP/customer policy, publish examples, and run a calibration huddle.",
    "reviewer_misalignment": "Run reviewer calibration, inspect disagreement samples, and increase QA sampling until alignment recovers.",
    "quality_defect": "Start quality containment, inspect failed samples, refresh gold tasks, and assign a QA owner.",
    "tooling_issue": "Assign tooling owner, confirm incident scope, and add a workaround or product fix ETA.",
    "customer_requirement_change": "Confirm customer requirement delta, propagate updated instructions, and audit affected queues.",
    "sla_miss": "Review capacity, queue aging, and staffing coverage; rebalance work or add short-term surge support.",
    "workflow_handoff_gap": "Define named handoff owner, update routing rules, and add escalation handoff SLA checks.",
    "capacity_shortfall": "Rebalance staffing, add backup coverage, and monitor backlog aging until volume normalizes.",
}


class MissingEscalationColumnsError(ValueError):
    """Raised when the escalation events table does not have the required schema."""


def _normalize_text(value: object) -> str:
    if pd.isna(value):
        return "unknown"
    text = str(value).strip().lower().replace(" ", "_")
    return text or "unknown"


def _pattern_id(pattern_key: str) -> str:
    digest = hashlib.md5(pattern_key.encode("utf-8")).hexdigest()[:8]
    return f"PAT_{digest.upper()}"


def validate_escalation_events(escalation_events: pd.DataFrame) -> None:
    """Validate that Module B can run on the escalation event table."""
    missing = [col for col in REQUIRED_COLUMNS if col not in escalation_events.columns]
    if missing:
        raise MissingEscalationColumnsError(
            "Missing required escalation_events columns: " + ", ".join(missing)
        )


def prepare_escalation_events(escalation_events: pd.DataFrame) -> pd.DataFrame:
    """Clean types and normalize categorical fields used by pattern detection."""
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
        df[col] = df[col].map(_normalize_text)

    df["days_to_resolve"] = pd.to_numeric(df["days_to_resolve"], errors="coerce")
    df["is_open"] = df["status"].isin(OPEN_STATUSES)
    df["is_resolved"] = df["status"].isin(RESOLVED_STATUSES)
    df["severity_weight"] = df["severity"].map(SEVERITY_SCORE).fillna(1.0)

    return df


def build_pattern_keys(escalation_events: pd.DataFrame) -> pd.DataFrame:
    """
    Add deterministic repeat-pattern keys to each escalation event.

    The output preserves every original row and appends pattern-key columns such as:
    - pattern_key_work_type_root_cause
    - pattern_key_work_type_team_root_cause
    - pattern_key_customer_work_type_root_cause
    - pattern_key_team_severity_root_cause
    """
    df = prepare_escalation_events(escalation_events)

    for grain_name, columns in PATTERN_GRAINS.items():
        key_col = f"pattern_key_{grain_name}"
        df[key_col] = df[columns].astype(str).agg(" | ".join, axis=1)

    return df


def classify_pattern_status(pattern_row: pd.Series) -> str:
    """
    Classify recurrence status using deterministic operating rules.

    Rules are ordered to keep the label management-friendly:
    - Dormant: no escalation in the last 30 days
    - New: first seen in the last 14 days
    - Accelerating: last 14-day count is higher than the prior 14-day count
    - Resolved: recurring in 60 days and currently no open escalations
    - Recurring: 3+ escalations in the last 60 days
    - Watchlist: 2 escalations in the last 60 days
    - Low activity: everything else
    """
    if int(pattern_row.get("last_30d_count", 0)) == 0:
        return "Dormant"

    if int(pattern_row.get("days_since_first_seen", 9999)) <= 14:
        return "New"

    if (
        int(pattern_row.get("last_14d_count", 0))
        > int(pattern_row.get("prior_14d_count", 0))
        and int(pattern_row.get("last_14d_count", 0)) >= 2
    ):
        return "Accelerating"

    if int(pattern_row.get("last_60d_count", 0)) >= 3 and int(pattern_row.get("open_count", 0)) == 0:
        return "Resolved"

    if int(pattern_row.get("last_60d_count", 0)) >= 3:
        return "Recurring"

    if int(pattern_row.get("last_60d_count", 0)) == 2:
        return "Watchlist"

    return "Low activity"


def score_pattern_risk(pattern_row: pd.Series) -> float:
    """Calculate deterministic recurrence risk score."""
    avg_days = pattern_row.get("avg_days_to_resolve", 0)
    avg_days = 0 if pd.isna(avg_days) else float(avg_days)

    unresolved_or_slow_resolution_penalty = 0.0
    if int(pattern_row.get("open_count", 0)) > 0:
        unresolved_or_slow_resolution_penalty += 3.0
    if avg_days >= 7:
        unresolved_or_slow_resolution_penalty += 3.0
    elif avg_days >= 4:
        unresolved_or_slow_resolution_penalty += 1.5

    acceleration_bonus = 0.0
    if pattern_row.get("recurrence_status") == "Accelerating":
        acceleration_bonus = 3.0
    elif pattern_row.get("recurrence_status") == "Recurring":
        acceleration_bonus = 2.0

    score = (
        float(pattern_row.get("escalation_count", 0)) * 2.0
        + float(pattern_row.get("sev1_count", 0)) * 5.0
        + float(pattern_row.get("sev2_count", 0)) * 3.0
        + float(pattern_row.get("open_count", 0)) * 2.0
        + float(pattern_row.get("unique_customer_segments_impacted", 0)) * 1.5
        + unresolved_or_slow_resolution_penalty
        + acceleration_bonus
    )
    return round(score, 1)


def classify_risk_level(risk_score: float) -> str:
    """Bucket risk scores for leadership review."""
    if risk_score >= 20:
        return "High recurrence risk"
    if risk_score >= 10:
        return "Medium recurrence risk"
    return "Low recurrence risk"


def recommend_action(root_cause_category: str, recurrence_status: str, risk_level: str) -> str:
    """Return a deterministic leadership action based on root cause and recurrence risk."""
    base_action = ROOT_CAUSE_ACTION_MAP.get(
        root_cause_category,
        "Assign an owner, review recent examples, and define a containment plus prevention action.",
    )

    if risk_level == "High recurrence risk":
        return f"Leadership review this week: {base_action}"
    if recurrence_status in {"Accelerating", "Recurring", "Watchlist"}:
        return f"Add to weekly retro: {base_action}"
    if recurrence_status == "Resolved":
        return f"Validate durability: {base_action}"
    return f"Monitor: {base_action}"


def _join_unique(values: Iterable[object], limit: int = 4) -> str:
    clean_values = sorted({_normalize_text(value) for value in values if not pd.isna(value)})
    if not clean_values:
        return "unknown"
    if len(clean_values) > limit:
        return ", ".join(clean_values[:limit]) + f", +{len(clean_values) - limit} more"
    return ", ".join(clean_values)


def _severity_mix(group: pd.DataFrame) -> str:
    counts = group["severity"].value_counts().sort_index()
    return ", ".join(f"{severity}: {count}" for severity, count in counts.items())


def summarize_patterns(
    escalation_events: pd.DataFrame,
    pattern_grain: str = "work_type_root_cause",
    reference_date: pd.Timestamp | None = None,
) -> pd.DataFrame:
    """
    Summarize escalation recurrence patterns for a chosen pattern grain.

    Returns a DataFrame with one row per pattern and the fields needed by the
    Streamlit UI, briefing generator, and optional CSV export.
    """
    if pattern_grain not in PATTERN_GRAINS:
        valid = ", ".join(PATTERN_GRAINS)
        raise ValueError(f"Invalid pattern_grain '{pattern_grain}'. Valid values: {valid}")

    df = build_pattern_keys(escalation_events)
    if df.empty:
        return pd.DataFrame(
            columns=[
                "pattern_id",
                "pattern_key",
                "pattern_grain",
                "work_type",
                "root_cause_category",
                "team_id",
                "customer_segment",
                "escalation_count",
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
        )

    reference_date = pd.to_datetime(reference_date or df["date"].max()).normalize()
    df["days_from_reference"] = (reference_date - df["date"].dt.normalize()).dt.days

    key_col = f"pattern_key_{pattern_grain}"
    rows = []

    for pattern_key, group in df.groupby(key_col, dropna=False):
        first_seen = group["date"].min().normalize()
        latest_seen = group["date"].max().normalize()
        open_count = int(group["is_open"].sum())
        resolved_count = int(group["is_resolved"].sum())
        escalation_count = int(group["escalation_id"].nunique())
        recurrence_window_days = int((latest_seen - first_seen).days) if escalation_count > 1 else 0

        row = {
            "pattern_id": _pattern_id(str(pattern_key)),
            "pattern_key": str(pattern_key),
            "pattern_grain": pattern_grain,
            "work_type": _join_unique(group["work_type"]),
            "root_cause_category": _join_unique(group["root_cause_category"]),
            "team_id": _join_unique(group["team_id"]),
            "customer_segment": _join_unique(group["customer_segment"]),
            "severity_mix": _severity_mix(group),
            "escalation_count": escalation_count,
            "unique_teams_impacted": int(group["team_id"].nunique()),
            "unique_customer_segments_impacted": int(group["customer_segment"].nunique()),
            "sev1_count": int((group["severity"] == "sev1").sum()),
            "sev2_count": int((group["severity"] == "sev2").sum()),
            "open_count": open_count,
            "resolved_count": resolved_count,
            "avg_days_to_resolve": round(float(group["days_to_resolve"].mean()), 1)
            if group["days_to_resolve"].notna().any()
            else 0.0,
            "latest_escalation_date": latest_seen.date(),
            "first_seen_date": first_seen.date(),
            "recurrence_window_days": recurrence_window_days,
            "last_14d_count": int(group["days_from_reference"].between(0, 14).sum()),
            "prior_14d_count": int(group["days_from_reference"].between(15, 28).sum()),
            "last_30d_count": int(group["days_from_reference"].between(0, 30).sum()),
            "last_60d_count": int(group["days_from_reference"].between(0, 60).sum()),
            "days_since_first_seen": int((reference_date - first_seen).days),
            "days_since_latest_escalation": int((reference_date - latest_seen).days),
            "sample_escalation_summaries": " | ".join(
                group.sort_values("date", ascending=False)["escalation_summary"]
                .dropna()
                .astype(str)
                .head(3)
            ),
        }
        row_series = pd.Series(row)
        row["recurrence_status"] = classify_pattern_status(row_series)
        row["risk_score"] = score_pattern_risk(pd.Series(row))
        row["risk_level"] = classify_risk_level(row["risk_score"])
        row["recommended_action"] = recommend_action(
            row["root_cause_category"],
            row["recurrence_status"],
            row["risk_level"],
        )
        rows.append(row)

    summary = pd.DataFrame(rows)
    return summary.sort_values(
        ["risk_score", "last_60d_count", "latest_escalation_date"],
        ascending=[False, False, False],
    ).reset_index(drop=True)


def get_top_patterns(pattern_summary: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return the highest-risk patterns for leadership review."""
    if pattern_summary.empty:
        return pattern_summary.copy()

    return (
        pattern_summary.sort_values(
            ["risk_score", "last_60d_count", "open_count", "latest_escalation_date"],
            ascending=[False, False, False, False],
        )
        .head(n)
        .reset_index(drop=True)
    )


def get_pattern_events(
    escalation_events: pd.DataFrame,
    pattern_key: str,
    pattern_grain: str = "work_type_root_cause",
) -> pd.DataFrame:
    """Return source escalation rows belonging to one selected pattern."""
    df = build_pattern_keys(escalation_events)
    key_col = f"pattern_key_{pattern_grain}"
    if key_col not in df.columns:
        return pd.DataFrame(columns=df.columns)
    return df[df[key_col] == pattern_key].sort_values("date", ascending=False).reset_index(drop=True)
