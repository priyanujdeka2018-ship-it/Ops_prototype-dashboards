"""
Module D: Capacity, Staffing, and SLA Forecasting.

This module builds deterministic work-type, team, and skill/complexity capacity
features from the synthetic command-center data. It is intended for capacity
planning, workload balancing, SLA protection, and quality preservation; it is
not a productivity surveillance tool.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


RECENT_WINDOW_DAYS = 7
PRIOR_WINDOW_DAYS = 14
AGED_BACKLOG_HOURS = 72
SAFE_UTILIZATION = 0.86
HIGH_UTILIZATION = 0.90
SLA_TARGET = 0.92
REWORK_TARGET = 0.08
QUALITY_TARGET = 90.0

OPEN_STATUSES = {"queued", "in_progress", "blocked", "open", "pending"}
COMPLETED_STATUSES = {"completed", "done", "closed", "resolved"}

COMPLEXITY_WEIGHTS = {
    "low": 0.75,
    "medium": 1.00,
    "high": 1.45,
    "expert": 1.90,
}

SKILL_CAPACITY_UNITS = {
    "junior": 4.0,
    "intermediate": 5.5,
    "senior": 7.0,
    "expert": 8.0,
    "unknown": 5.0,
}


@dataclass(frozen=True)
class RiskResult:
    score: float
    drivers: tuple[str, ...]


def _safe_df(df: pd.DataFrame | None) -> pd.DataFrame:
    if df is None:
        return pd.DataFrame()
    return df.copy()


def _ensure_columns(df: pd.DataFrame, defaults: dict[str, object]) -> pd.DataFrame:
    out = df.copy()
    for column, default in defaults.items():
        if column not in out.columns:
            out[column] = default
    return out


def _to_bool(series: pd.Series) -> pd.Series:
    if series.empty:
        return pd.Series(dtype="boolean")
    if pd.api.types.is_bool_dtype(series):
        return series.astype("boolean")
    lowered = series.astype(str).str.strip().str.lower()
    return lowered.map(
        {
            "true": True,
            "1": True,
            "yes": True,
            "y": True,
            "false": False,
            "0": False,
            "no": False,
            "n": False,
            "nan": pd.NA,
            "none": pd.NA,
            "": pd.NA,
        }
    ).astype("boolean")


def _rate_true(series: pd.Series) -> float:
    values = _to_bool(series).dropna()
    if values.empty:
        return np.nan
    return float(values.mean())


def _rate_false(series: pd.Series) -> float:
    values = _to_bool(series).dropna()
    if values.empty:
        return np.nan
    return float((~values).mean())


def _mode_or_unknown(series: pd.Series) -> str:
    values = series.dropna().astype(str)
    if values.empty:
        return "Unknown"
    return values.mode().iloc[0]


def _is_missing(value: object) -> bool:
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


def _fmt_pct(value: float | int | None) -> str:
    if _is_missing(value):
        return "n/a"
    return f"{float(value) * 100:.1f}%"


def _fmt_float(value: float | int | None, decimals: int = 1) -> str:
    if _is_missing(value):
        return "n/a"
    return f"{float(value):.{decimals}f}"


def _stringify_drivers(drivers: Iterable[str]) -> str:
    values = [driver for driver in drivers if driver]
    return ", ".join(values) if values else "Within expected range"


def _complexity_score(value: object) -> float:
    return COMPLEXITY_WEIGHTS.get(str(value).strip().lower(), 1.0)


def _skill_capacity_unit(value: object) -> float:
    return SKILL_CAPACITY_UNITS.get(str(value).strip().lower(), SKILL_CAPACITY_UNITS["unknown"])


def _safe_divide(numerator: float | int, denominator: float | int) -> float:
    if _is_missing(denominator):
        return np.nan
    try:
        denominator_value = float(denominator)
    except (TypeError, ValueError):
        return np.nan
    if denominator_value == 0:
        return np.nan
    try:
        return float(numerator) / denominator_value
    except (TypeError, ValueError):
        return np.nan


def _latest_reference_date(*frames: pd.DataFrame) -> pd.Timestamp:
    candidates: list[pd.Timestamp] = []
    for frame in frames:
        if frame is None or frame.empty:
            continue
        for column in ["date_created", "date_completed", "completed_at", "sla_due_at", "due_at", "date", "event_date"]:
            if column in frame.columns:
                dates = pd.to_datetime(frame[column], errors="coerce")
                if not dates.dropna().empty:
                    candidates.append(dates.max())
    if candidates:
        return max(candidates).normalize()
    return pd.Timestamp.today().normalize()


def _empty_capacity_base() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "work_item_id",
            "date_created",
            "date_completed",
            "region",
            "work_type",
            "team_id",
            "contributor_id",
            "customer_segment",
            "status",
            "sla_due_at",
            "completed_at",
            "sla_met",
            "rework_required",
            "task_complexity",
            "complexity_score",
            "manager_name",
            "tenure_days",
            "skill_level",
            "location_type",
            "active_status",
            "event_date",
        ]
    )


def _fallback_work_items_from_sla(sla_events: pd.DataFrame, teams: pd.DataFrame) -> pd.DataFrame:
    sla = _safe_df(sla_events)
    if sla.empty:
        return pd.DataFrame()

    sla = _ensure_columns(
        sla,
        {
            "event_id": pd.NA,
            "work_item_id": pd.NA,
            "due_at": pd.NaT,
            "completed_at": pd.NaT,
            "sla_met": pd.NA,
            "delay_hours": 0.0,
        },
    )
    out = sla.rename(columns={"due_at": "sla_due_at"}).copy()
    out["work_item_id"] = out["work_item_id"].fillna(out["event_id"])
    out["date_created"] = pd.to_datetime(out["sla_due_at"], errors="coerce") - pd.Timedelta(days=1)
    out["date_completed"] = pd.to_datetime(out["completed_at"], errors="coerce")
    out["status"] = "completed"
    out["rework_required"] = False
    out["task_complexity"] = "medium"

    team_defaults = {"team_id": "Unknown", "work_type": "Unknown", "region": "Unknown"}
    t = _ensure_columns(_safe_df(teams), team_defaults)
    if not t.empty:
        first_team = t[["team_id", "work_type", "region"]].drop_duplicates().iloc[0].to_dict()
        out["team_id"] = first_team.get("team_id", "Unknown")
        out["work_type"] = first_team.get("work_type", "Unknown")
        out["region"] = first_team.get("region", "Unknown")
    else:
        out["team_id"] = "Unknown"
        out["work_type"] = "Unknown"
        out["region"] = "Unknown"
    out["contributor_id"] = pd.NA
    out["customer_segment"] = "Unknown"
    return out


def prepare_capacity_data(
    contributors: pd.DataFrame | None,
    work_items: pd.DataFrame | None,
    teams: pd.DataFrame | None,
    sla_events: pd.DataFrame | None = None,
    quality_events: pd.DataFrame | None = None,
    escalation_events: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """
    Return a work-item grain table enriched with team, contributor, SLA, and quality context.

    The function handles partial synthetic data. If work_items.csv is missing or empty,
    it degrades to SLA-event-derived completed rows when possible, then uses quality,
    contributor, and team data for overlays and capacity estimates.
    """
    c = _safe_df(contributors)
    wi = _safe_df(work_items)
    t = _safe_df(teams)
    sla = _safe_df(sla_events)
    q = _safe_df(quality_events)

    if wi.empty:
        wi = _fallback_work_items_from_sla(sla, t)
    if wi.empty and q.empty and c.empty and t.empty:
        return _empty_capacity_base()

    wi = _ensure_columns(
        wi,
        {
            "work_item_id": pd.NA,
            "date_created": pd.NaT,
            "date_completed": pd.NaT,
            "region": pd.NA,
            "work_type": pd.NA,
            "team_id": pd.NA,
            "contributor_id": pd.NA,
            "customer_segment": pd.NA,
            "status": pd.NA,
            "sla_due_at": pd.NaT,
            "completed_at": pd.NaT,
            "sla_met": pd.NA,
            "rework_required": False,
            "task_complexity": "medium",
        },
    )

    if not sla.empty and "work_item_id" in sla.columns and "work_item_id" in wi.columns:
        sla_context = sla.copy()
        sla_context = sla_context.rename(columns={"due_at": "sla_due_at_sla"})
        sla_context = _ensure_columns(
            sla_context,
            {
                "work_item_id": pd.NA,
                "sla_due_at_sla": pd.NaT,
                "completed_at": pd.NaT,
                "sla_met": pd.NA,
            },
        )
        sla_context = sla_context[["work_item_id", "sla_due_at_sla", "completed_at", "sla_met"]].drop_duplicates("work_item_id")
        sla_context = sla_context.rename(columns={"completed_at": "completed_at_sla", "sla_met": "sla_met_sla"})
        wi = wi.merge(sla_context, on="work_item_id", how="left")
        wi["sla_due_at"] = wi["sla_due_at"].combine_first(wi["sla_due_at_sla"])
        wi["completed_at"] = wi["completed_at"].combine_first(wi["completed_at_sla"])
        wi["sla_met"] = wi["sla_met"].combine_first(wi["sla_met_sla"])
        wi = wi.drop(columns=["sla_due_at_sla", "completed_at_sla", "sla_met_sla"])

    t = _ensure_columns(
        t,
        {
            "team_id": pd.NA,
            "region": pd.NA,
            "manager_name": "Unknown",
            "work_type": pd.NA,
            "active_contributors": np.nan,
            "shift_type": "Unknown",
        },
    )
    if not t.empty:
        team_context = t[
            ["team_id", "region", "manager_name", "work_type", "active_contributors", "shift_type"]
        ].drop_duplicates("team_id")
        team_context = team_context.rename(
            columns={"region": "region_team", "work_type": "work_type_team", "active_contributors": "active_contributors_team"}
        )
        wi = wi.merge(team_context, on="team_id", how="left")
        wi["work_type"] = wi["work_type"].combine_first(wi["work_type_team"])
        wi["region"] = wi["region"].combine_first(wi["region_team"])
        wi = wi.drop(columns=["work_type_team", "region_team"])
    else:
        wi = _ensure_columns(wi, {"manager_name": "Unknown", "active_contributors_team": np.nan, "shift_type": "Unknown"})

    c = _ensure_columns(
        c,
        {
            "contributor_id": pd.NA,
            "team_id": pd.NA,
            "tenure_days": np.nan,
            "skill_level": "Unknown",
            "location_type": "Unknown",
            "active_status": "Unknown",
        },
    )
    if not c.empty:
        contributor_context = c[
            ["contributor_id", "team_id", "tenure_days", "skill_level", "location_type", "active_status"]
        ].drop_duplicates("contributor_id")
        contributor_context = contributor_context.rename(columns={"team_id": "team_id_contributor"})
        wi = wi.merge(contributor_context, on="contributor_id", how="left")
        wi["team_id"] = wi["team_id"].combine_first(wi["team_id_contributor"])
        wi = wi.drop(columns=["team_id_contributor"])
    else:
        wi = _ensure_columns(
            wi,
            {
                "tenure_days": np.nan,
                "skill_level": "Unknown",
                "location_type": "Unknown",
                "active_status": "Unknown",
            },
        )

    if not q.empty and "work_item_id" in q.columns:
        quality_context = _ensure_columns(
            q,
            {
                "work_item_id": pd.NA,
                "quality_score": np.nan,
                "gold_task_pass": pd.NA,
                "reviewer_override": pd.NA,
                "peer_agreement_score": np.nan,
            },
        )
        quality_context = (
            quality_context.groupby("work_item_id", as_index=False)
            .agg(
                quality_score=("quality_score", "mean"),
                reviewer_override_rate=("reviewer_override", lambda s: _rate_true(s)),
                peer_agreement_score=("peer_agreement_score", "mean"),
            )
        )
        wi = wi.merge(quality_context, on="work_item_id", how="left")
    else:
        wi = _ensure_columns(
            wi,
            {
                "quality_score": np.nan,
                "reviewer_override_rate": np.nan,
                "peer_agreement_score": np.nan,
            },
        )

    for column in ["date_created", "date_completed", "sla_due_at", "completed_at"]:
        wi[column] = pd.to_datetime(wi[column], errors="coerce")

    fallback_completed = wi["date_completed"].combine_first(wi["completed_at"])
    wi["completed_at"] = wi["completed_at"].combine_first(fallback_completed)
    wi["date_completed"] = wi["date_completed"].combine_first(fallback_completed)

    wi["status"] = wi["status"].fillna("Unknown").astype(str).str.lower()
    inferred_completed = wi["completed_at"].notna()
    wi.loc[wi["status"].isin(["nan", "none", "unknown"]) & inferred_completed, "status"] = "completed"
    wi["sla_met"] = _to_bool(wi["sla_met"])
    wi["rework_required"] = _to_bool(wi["rework_required"]).fillna(False)
    wi["task_complexity"] = wi["task_complexity"].fillna("medium").astype(str).str.lower()
    wi["complexity_score"] = wi["task_complexity"].map(_complexity_score).fillna(1.0)
    wi["work_type"] = wi["work_type"].fillna("Unknown").astype(str)
    wi["team_id"] = wi["team_id"].fillna("Unknown").astype(str)
    wi["region"] = wi["region"].fillna("Unknown").astype(str)
    wi["manager_name"] = wi["manager_name"].fillna("Unknown").astype(str)
    wi["skill_level"] = wi["skill_level"].fillna("Unknown").astype(str)
    wi["location_type"] = wi["location_type"].fillna("Unknown").astype(str)
    wi["active_status"] = wi["active_status"].fillna("Unknown").astype(str)
    wi["customer_segment"] = wi["customer_segment"].fillna("Unknown").astype(str)
    wi["event_date"] = wi["date_completed"].combine_first(wi["completed_at"]).combine_first(wi["date_created"])

    return wi


def _active_contributor_capacity(contributors: pd.DataFrame, teams: pd.DataFrame) -> pd.DataFrame:
    c = _safe_df(contributors)
    t = _safe_df(teams)
    if c.empty:
        t = _ensure_columns(
            t,
            {
                "team_id": "Unknown",
                "work_type": "Unknown",
                "region": "Unknown",
                "manager_name": "Unknown",
                "active_contributors": 0,
            },
        )
        if t.empty:
            return pd.DataFrame(columns=["team_id", "active_contributors", "available_contributors", "capacity_units"])
        out = t[["team_id", "work_type", "region", "manager_name", "active_contributors"]].copy()
        out["available_contributors"] = pd.to_numeric(out["active_contributors"], errors="coerce").fillna(0)
        out["capacity_units"] = out["available_contributors"] * SKILL_CAPACITY_UNITS["unknown"]
        out["junior_share"] = np.nan
        out["low_tenure_share"] = np.nan
        out["senior_expert_contributors"] = np.nan
        return out

    c = _ensure_columns(
        c,
        {
            "contributor_id": pd.NA,
            "team_id": "Unknown",
            "tenure_days": np.nan,
            "skill_level": "Unknown",
            "active_status": "Unknown",
        },
    )
    active = c[c["active_status"].astype(str).str.lower().eq("active")].copy()
    if active.empty:
        active = c.copy()

    active["capacity_unit"] = active["skill_level"].map(_skill_capacity_unit).fillna(SKILL_CAPACITY_UNITS["unknown"])
    active["is_available"] = active["active_status"].astype(str).str.lower().eq("active")
    active["is_junior"] = active["skill_level"].astype(str).str.lower().eq("junior")
    active["is_low_tenure"] = pd.to_numeric(active["tenure_days"], errors="coerce").fillna(9999) < 90
    active["is_senior_expert"] = active["skill_level"].astype(str).str.lower().isin(["senior", "expert"])

    out = (
        active.groupby("team_id", as_index=False)
        .agg(
            active_contributors=("contributor_id", "nunique"),
            available_contributors=("is_available", "sum"),
            capacity_units=("capacity_unit", "sum"),
            junior_share=("is_junior", "mean"),
            low_tenure_share=("is_low_tenure", "mean"),
            senior_expert_contributors=("is_senior_expert", "sum"),
        )
    )

    t = _ensure_columns(
        t,
        {"team_id": "Unknown", "work_type": "Unknown", "region": "Unknown", "manager_name": "Unknown"},
    )
    if not t.empty:
        context = t[["team_id", "work_type", "region", "manager_name"]].drop_duplicates("team_id")
        out = out.merge(context, on="team_id", how="left")
    return out


def _time_windows(capacity_data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Timestamp]:
    if capacity_data.empty:
        return capacity_data, capacity_data, capacity_data, _latest_reference_date(capacity_data)
    max_date = _latest_reference_date(capacity_data)
    dates_created = pd.to_datetime(capacity_data["date_created"], errors="coerce")
    dates_completed = pd.to_datetime(capacity_data["completed_at"], errors="coerce")
    recent_inflow = capacity_data[dates_created > max_date - pd.Timedelta(days=RECENT_WINDOW_DAYS)].copy()
    recent_completed = capacity_data[dates_completed > max_date - pd.Timedelta(days=RECENT_WINDOW_DAYS)].copy()
    completed_14d = capacity_data[dates_completed > max_date - pd.Timedelta(days=PRIOR_WINDOW_DAYS)].copy()
    return recent_inflow, recent_completed, completed_14d, max_date


def _base_group_features(capacity_data: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    if capacity_data.empty:
        return pd.DataFrame(columns=group_cols)

    recent_inflow, recent_completed, completed_14d, max_date = _time_windows(capacity_data)
    open_mask = ~capacity_data["status"].isin(COMPLETED_STATUSES)
    open_items = capacity_data[open_mask].copy()
    aged_cutoff = max_date - pd.Timedelta(hours=AGED_BACKLOG_HOURS)
    open_items["is_aged_backlog"] = pd.to_datetime(open_items["date_created"], errors="coerce") <= aged_cutoff

    base_keys = capacity_data[group_cols].drop_duplicates().copy()

    def grouped_count(df: pd.DataFrame, name: str) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame(columns=group_cols + [name])
        return df.groupby(group_cols, as_index=False).agg(**{name: ("work_item_id", "nunique")})

    def grouped_rate(df: pd.DataFrame, source_col: str, name: str, mode: str = "true") -> pd.DataFrame:
        if df.empty or source_col not in df.columns:
            return pd.DataFrame(columns=group_cols + [name])
        func = _rate_true if mode == "true" else _rate_false
        return df.groupby(group_cols, as_index=False).agg(**{name: (source_col, func)})

    features = base_keys.copy()
    for metric_df in [
        grouped_count(open_items, "open_backlog"),
        grouped_count(open_items[open_items["is_aged_backlog"]], "aged_backlog_72h"),
        grouped_count(recent_inflow, "new_items_7d"),
        grouped_count(recent_completed, "completed_items_7d"),
        grouped_count(completed_14d, "completed_items_14d"),
        grouped_rate(recent_completed, "sla_met", "sla_adherence_7d", "true"),
        grouped_rate(recent_completed, "sla_met", "sla_miss_rate_7d", "false"),
        grouped_rate(recent_completed, "rework_required", "rework_rate_7d", "true"),
    ]:
        features = features.merge(metric_df, on=group_cols, how="left")

    complexity = capacity_data.groupby(group_cols, as_index=False).agg(
        avg_task_complexity_score=("complexity_score", "mean"),
        high_complexity_share=("task_complexity", lambda s: s.astype(str).str.lower().isin(["high", "expert"]).mean()),
        expert_complexity_share=("task_complexity", lambda s: s.astype(str).str.lower().eq("expert").mean()),
    )
    features = features.merge(complexity, on=group_cols, how="left")

    for column in [
        "open_backlog",
        "aged_backlog_72h",
        "new_items_7d",
        "completed_items_7d",
        "completed_items_14d",
    ]:
        features[column] = pd.to_numeric(features[column], errors="coerce").fillna(0).astype(int)

    features["avg_daily_inflow_7d"] = features["new_items_7d"] / RECENT_WINDOW_DAYS
    features["avg_daily_throughput_7d"] = features["completed_items_7d"] / RECENT_WINDOW_DAYS
    features["throughput_gap"] = features["avg_daily_throughput_7d"] - features["avg_daily_inflow_7d"]
    features["estimated_days_to_clear_backlog"] = features.apply(
        lambda row: _safe_divide(row["open_backlog"], row["avg_daily_throughput_7d"]), axis=1
    )
    features["estimated_days_to_clear_backlog"] = features["estimated_days_to_clear_backlog"].replace([np.inf, -np.inf], np.nan)

    return features


def _quality_overlay(quality_events: pd.DataFrame, work_items: pd.DataFrame, teams: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    q = _safe_df(quality_events)
    if q.empty:
        return pd.DataFrame(columns=group_cols + ["quality_score", "quality_risk_overlay"])

    q = _ensure_columns(q, {"work_item_id": pd.NA, "quality_score": np.nan})
    wi = _safe_df(work_items)
    wi = _ensure_columns(wi, {"work_item_id": pd.NA, "team_id": pd.NA, "work_type": pd.NA, "region": pd.NA})
    if not wi.empty and "work_item_id" in q.columns:
        q = q.merge(wi[["work_item_id", "team_id", "work_type", "region"]].drop_duplicates("work_item_id"), on="work_item_id", how="left")

    t = _safe_df(teams)
    t = _ensure_columns(t, {"team_id": pd.NA, "work_type": pd.NA, "region": pd.NA})
    if not t.empty:
        q = q.merge(t[["team_id", "work_type", "region"]].drop_duplicates("team_id"), on="team_id", how="left", suffixes=("", "_team"))
        q["work_type"] = q.get("work_type", pd.Series(index=q.index, dtype=object)).combine_first(q.get("work_type_team", pd.Series(index=q.index, dtype=object)))
        q["region"] = q.get("region", pd.Series(index=q.index, dtype=object)).combine_first(q.get("region_team", pd.Series(index=q.index, dtype=object)))
        q = q.drop(columns=[col for col in ["work_type_team", "region_team"] if col in q.columns])

    q = _ensure_columns(q, {col: "Unknown" for col in group_cols})
    q["quality_score"] = pd.to_numeric(q["quality_score"], errors="coerce")
    overlay = q.groupby(group_cols, as_index=False).agg(quality_score=("quality_score", "mean"))
    overlay["quality_risk_overlay"] = overlay["quality_score"].apply(
        lambda value: 0.0 if pd.isna(value) or value >= QUALITY_TARGET else min(12.0, (QUALITY_TARGET - float(value)) * 0.8)
    )
    return overlay


def _escalation_overlay(escalation_events: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    e = _safe_df(escalation_events)
    if e.empty:
        return pd.DataFrame(columns=group_cols + ["escalation_risk_overlay"])
    e = _ensure_columns(
        e,
        {
            "date": pd.NaT,
            "work_type": "Unknown",
            "team_id": "Unknown",
            "region": "Unknown",
            "root_cause_category": "Unknown",
            "severity": "sev4",
            "status": "Unknown",
        },
    )
    max_date = _latest_reference_date(e)
    dates = pd.to_datetime(e["date"], errors="coerce")
    recent = e[dates > max_date - pd.Timedelta(days=30)].copy()
    if recent.empty:
        recent = e.copy()

    risk_roots = {"capacity_shortfall", "sla_miss", "workflow_handoff_gap"}
    recent["capacity_related"] = recent["root_cause_category"].astype(str).str.lower().isin(risk_roots)
    recent["open_like"] = ~recent["status"].astype(str).str.lower().isin(["resolved", "closed"])
    recent["severity_weight"] = recent["severity"].astype(str).str.lower().map({"sev1": 4.0, "sev2": 2.5, "sev3": 1.2, "sev4": 0.6}).fillna(1.0)
    recent = _ensure_columns(recent, {col: "Unknown" for col in group_cols})
    overlay = recent.groupby(group_cols, as_index=False).agg(
        capacity_related_escalations=("capacity_related", "sum"),
        open_escalations=("open_like", "sum"),
        severity_drag=("severity_weight", "sum"),
    )
    overlay["escalation_risk_overlay"] = (
        overlay["capacity_related_escalations"] * 2.0 + overlay["open_escalations"] * 1.5 + overlay["severity_drag"] * 0.35
    ).clip(0, 14)
    return overlay[group_cols + ["escalation_risk_overlay"]]


def score_work_type_capacity_risk(row: pd.Series | dict[str, object]) -> RiskResult:
    data = row.to_dict() if isinstance(row, pd.Series) else dict(row)
    drivers: list[str] = []
    score = 0.0

    open_backlog = float(data.get("open_backlog", 0) or 0)
    completed_7d = float(data.get("completed_items_7d", 0) or 0)
    aged_backlog = float(data.get("aged_backlog_72h", 0) or 0)
    throughput_gap = float(data.get("throughput_gap", 0) or 0)
    sla_miss_rate = data.get("sla_miss_rate_7d")
    utilization = data.get("utilization_rate")
    high_complexity_share = data.get("high_complexity_share")
    expert_share = data.get("expert_complexity_share")
    rework_rate = data.get("rework_rate_7d")
    escalation_overlay = float(data.get("escalation_risk_overlay", 0) or 0)
    quality_overlay = float(data.get("quality_risk_overlay", 0) or 0)

    if open_backlog > max(30, completed_7d * 0.75):
        score += min(18, 6 + open_backlog / max(completed_7d, 1))
        drivers.append("Backlog pressure")
    if aged_backlog > 0:
        aged_share = aged_backlog / max(open_backlog, 1)
        score += min(18, 4 + aged_share * 24)
        drivers.append("Aged backlog over 72h")
    if throughput_gap < 0:
        score += min(16, abs(throughput_gap) * 5)
        drivers.append("Backlog growing faster than throughput")
    if pd.notna(sla_miss_rate) and float(sla_miss_rate) > 1 - SLA_TARGET:
        score += min(18, 4 + float(sla_miss_rate) * 40)
        drivers.append("SLA miss rate rising")
    if pd.notna(utilization) and float(utilization) > HIGH_UTILIZATION:
        score += min(16, (float(utilization) - HIGH_UTILIZATION) * 100 + 8)
        drivers.append("Utilization above safe threshold")
    if pd.notna(high_complexity_share) and float(high_complexity_share) > 0.35:
        score += 8
        drivers.append("High-complexity work mix")
    if pd.notna(expert_share) and float(expert_share) > 0.18:
        score += 6
        drivers.append("Expert capacity demand")
    if pd.notna(rework_rate) and float(rework_rate) > REWORK_TARGET:
        score += min(12, float(rework_rate) * 45)
        drivers.append("High rework drag")
    if escalation_overlay > 0:
        score += escalation_overlay
        drivers.append("Recurring escalation overlay")
    if quality_overlay > 0:
        score += quality_overlay
        drivers.append("Quality risk overlay")

    return RiskResult(round(float(min(score, 100)), 1), tuple(drivers))


def score_team_capacity_risk(row: pd.Series | dict[str, object]) -> RiskResult:
    data = row.to_dict() if isinstance(row, pd.Series) else dict(row)
    drivers: list[str] = []
    result = score_work_type_capacity_risk(data)
    score = result.score
    drivers.extend(result.drivers)

    low_tenure = data.get("low_tenure_share")
    high_complexity = data.get("high_complexity_share")
    junior_share = data.get("junior_share")
    if pd.notna(low_tenure) and pd.notna(high_complexity) and float(low_tenure) > 0.25 and float(high_complexity) > 0.30:
        score += 10
        drivers.append("Low-tenure team handling high-complexity work")
    if pd.notna(junior_share) and pd.notna(high_complexity) and float(junior_share) > 0.30 and float(high_complexity) > 0.30:
        score += 8
        drivers.append("Junior-heavy team complexity mismatch")

    return RiskResult(round(float(min(score, 100)), 1), tuple(dict.fromkeys(drivers)))


def _risk_level(score: float | int | None, data_points: float | int | None = None) -> str:
    if data_points is not None and pd.notna(data_points) and float(data_points) <= 0:
        return "Insufficient data"
    if score is None or pd.isna(score):
        return "Insufficient data"
    if float(score) >= 55:
        return "High capacity risk"
    if float(score) >= 30:
        return "Medium capacity risk"
    return "Low capacity risk"


def classify_sla_forecast_status(row: pd.Series | dict[str, object]) -> str:
    data = row.to_dict() if isinstance(row, pd.Series) else dict(row)
    data_points = float(data.get("new_items_7d", 0) or 0) + float(data.get("completed_items_7d", 0) or 0) + float(data.get("open_backlog", 0) or 0)
    if data_points == 0:
        return "Insufficient data"

    open_backlog = float(data.get("open_backlog", 0) or 0)
    aged_backlog = float(data.get("aged_backlog_72h", 0) or 0)
    throughput_gap = float(data.get("throughput_gap", 0) or 0)
    sla_adherence = data.get("sla_adherence_7d")
    utilization = data.get("utilization_rate")
    high_complexity_share = data.get("high_complexity_share")
    rework_rate = data.get("rework_rate_7d")
    capacity_gap = float(data.get("capacity_gap", 0) or 0)
    quality_overlay = float(data.get("quality_risk_overlay", 0) or 0)
    escalation_overlay = float(data.get("escalation_risk_overlay", 0) or 0)

    severe_conditions = 0
    watch_conditions = 0

    if open_backlog > 0 and throughput_gap < 0:
        watch_conditions += 1
        if abs(throughput_gap) >= 5 or capacity_gap < 0:
            severe_conditions += 1
    if aged_backlog > max(10, open_backlog * 0.20):
        watch_conditions += 1
        severe_conditions += 1
    if pd.notna(sla_adherence) and float(sla_adherence) < 0.85:
        severe_conditions += 1
    elif pd.notna(sla_adherence) and float(sla_adherence) < SLA_TARGET:
        watch_conditions += 1
    if pd.notna(utilization) and float(utilization) > 0.95:
        severe_conditions += 1
    elif pd.notna(utilization) and float(utilization) > HIGH_UTILIZATION:
        watch_conditions += 1
    if pd.notna(high_complexity_share) and float(high_complexity_share) > 0.40:
        watch_conditions += 1
    if pd.notna(rework_rate) and float(rework_rate) > 0.13:
        watch_conditions += 1
    if quality_overlay >= 8 or escalation_overlay >= 8:
        watch_conditions += 1

    if severe_conditions >= 3:
        return "SLA recovery needed"
    if severe_conditions >= 1 and watch_conditions >= 2:
        return "SLA at risk"
    if watch_conditions >= 2:
        return "SLA watchlist"
    return "SLA likely stable"


def recommend_capacity_action(row: pd.Series | dict[str, object], scope: str = "work_type") -> str:
    data = row.to_dict() if isinstance(row, pd.Series) else dict(row)
    throughput_gap = float(data.get("throughput_gap", 0) or 0)
    aged_backlog = float(data.get("aged_backlog_72h", 0) or 0)
    utilization = data.get("utilization_rate")
    high_complexity = data.get("high_complexity_share")
    low_tenure = data.get("low_tenure_share")
    junior_share = data.get("junior_share")
    rework_rate = data.get("rework_rate_7d")
    capacity_gap = float(data.get("capacity_gap", 0) or 0)
    quality_overlay = float(data.get("quality_risk_overlay", 0) or 0)
    escalation_overlay = float(data.get("escalation_risk_overlay", 0) or 0)

    if escalation_overlay >= 8:
        return "Assign structural fix owner before scaling volume"
    if quality_overlay >= 8:
        return "Pair capacity action with calibration and coaching"
    if pd.notna(rework_rate) and float(rework_rate) > 0.13:
        return "Run quality and workflow review before adding volume"
    if pd.notna(low_tenure) and pd.notna(high_complexity) and float(low_tenure) > 0.25 and float(high_complexity) > 0.30:
        return "Shift complex work to senior contributors and accelerate training ramp"
    if pd.notna(junior_share) and pd.notna(high_complexity) and float(junior_share) > 0.30 and float(high_complexity) > 0.30:
        return "Rebalance high-complexity queue toward senior reviewers"
    if capacity_gap < 0 and throughput_gap < 0:
        return "Add short-term staffing or reroute work from overloaded queue"
    if aged_backlog > 0:
        return "Run a backlog burn-down sprint with daily SLA recovery check"
    if pd.notna(utilization) and float(utilization) > HIGH_UTILIZATION:
        return "Add coverage or rebalance workload across teams"
    if pd.notna(utilization) and float(utilization) < 0.65:
        return "Cross-route work from overloaded queues into this available capacity"
    if scope == "team":
        return "Continue monitoring team capacity and protect quality while routing new work"
    return "Continue monitoring capacity, inflow, throughput, SLA, and rework"


def build_work_type_capacity_features(
    capacity_data: pd.DataFrame | None,
    contributors: pd.DataFrame | None = None,
    teams: pd.DataFrame | None = None,
    quality_events: pd.DataFrame | None = None,
    escalation_events: pd.DataFrame | None = None,
) -> pd.DataFrame:
    data = _safe_df(capacity_data)
    if data.empty:
        return pd.DataFrame(
            columns=[
                "work_type",
                "region",
                "open_backlog",
                "aged_backlog_72h",
                "new_items_7d",
                "completed_items_7d",
                "completed_items_14d",
                "avg_daily_inflow_7d",
                "avg_daily_throughput_7d",
                "throughput_gap",
                "estimated_days_to_clear_backlog",
                "sla_adherence_7d",
                "sla_miss_rate_7d",
                "rework_rate_7d",
                "avg_task_complexity_score",
                "high_complexity_share",
                "expert_complexity_share",
                "active_contributors",
                "available_contributors",
                "capacity_units",
                "required_capacity_units",
                "capacity_gap",
                "utilization_rate",
                "forecasted_sla_risk",
                "capacity_risk_score",
                "capacity_risk_level",
                "recommended_capacity_action",
            ]
        )

    group_cols = ["work_type", "region"]
    features = _base_group_features(data, group_cols)

    team_capacity = _active_contributor_capacity(_safe_df(contributors), _safe_df(teams))
    if not team_capacity.empty:
        team_capacity = _ensure_columns(team_capacity, {"work_type": "Unknown", "region": "Unknown", "active_contributors": 0, "available_contributors": 0, "capacity_units": 0})
        capacity_rollup = team_capacity.groupby(group_cols, as_index=False).agg(
            active_contributors=("active_contributors", "sum"),
            available_contributors=("available_contributors", "sum"),
            capacity_units=("capacity_units", "sum"),
            senior_expert_contributors=("senior_expert_contributors", "sum"),
        )
        features = features.merge(capacity_rollup, on=group_cols, how="left")
    else:
        features["active_contributors"] = 0
        features["available_contributors"] = 0
        features["capacity_units"] = features["completed_items_7d"] * features["avg_task_complexity_score"].fillna(1.0)

    features["active_contributors"] = pd.to_numeric(features["active_contributors"], errors="coerce").fillna(0)
    features["available_contributors"] = pd.to_numeric(features["available_contributors"], errors="coerce").fillna(features["active_contributors"])
    features["capacity_units"] = pd.to_numeric(features["capacity_units"], errors="coerce").fillna(0)
    features["required_capacity_units"] = (
        (features["new_items_7d"] + features["open_backlog"] * 0.40)
        * features["avg_task_complexity_score"].fillna(1.0)
        * (1 + features["rework_rate_7d"].fillna(0))
    )
    features["capacity_gap"] = features["capacity_units"] - features["required_capacity_units"]
    features["utilization_rate"] = features.apply(
        lambda row: _safe_divide(row["required_capacity_units"], row["capacity_units"]), axis=1
    ).clip(lower=0)

    q_overlay = _quality_overlay(_safe_df(quality_events), data, _safe_df(teams), group_cols)
    e_overlay = _escalation_overlay(_safe_df(escalation_events), group_cols)
    for overlay in [q_overlay, e_overlay]:
        if not overlay.empty:
            features = features.merge(overlay, on=group_cols, how="left")
    features["quality_risk_overlay"] = pd.to_numeric(features.get("quality_risk_overlay", 0), errors="coerce").fillna(0)
    features["escalation_risk_overlay"] = pd.to_numeric(features.get("escalation_risk_overlay", 0), errors="coerce").fillna(0)

    risk_results = features.apply(score_work_type_capacity_risk, axis=1)
    features["capacity_risk_score"] = [result.score for result in risk_results]
    features["risk_drivers"] = [_stringify_drivers(result.drivers) for result in risk_results]
    features["capacity_risk_level"] = features.apply(
        lambda row: _risk_level(row["capacity_risk_score"], row["new_items_7d"] + row["completed_items_7d"] + row["open_backlog"]),
        axis=1,
    )
    features["forecasted_sla_risk"] = features.apply(classify_sla_forecast_status, axis=1)
    features["recommended_capacity_action"] = features.apply(recommend_capacity_action, axis=1)

    return features.sort_values("capacity_risk_score", ascending=False).reset_index(drop=True)


def build_team_capacity_features(
    capacity_data: pd.DataFrame | None,
    contributors: pd.DataFrame | None = None,
    teams: pd.DataFrame | None = None,
    quality_events: pd.DataFrame | None = None,
    escalation_events: pd.DataFrame | None = None,
) -> pd.DataFrame:
    data = _safe_df(capacity_data)
    if data.empty:
        return pd.DataFrame(columns=["team_id", "work_type", "region", "capacity_risk_score", "capacity_risk_level"])

    group_cols = ["team_id", "work_type", "region"]
    features = _base_group_features(data, group_cols)

    manager = data.groupby("team_id", as_index=False).agg(manager_name=("manager_name", _mode_or_unknown))
    features = features.merge(manager, on="team_id", how="left")

    team_capacity = _active_contributor_capacity(_safe_df(contributors), _safe_df(teams))
    if not team_capacity.empty:
        cols = [
            "team_id",
            "active_contributors",
            "available_contributors",
            "capacity_units",
            "junior_share",
            "low_tenure_share",
            "senior_expert_contributors",
        ]
        features = features.merge(team_capacity[[col for col in cols if col in team_capacity.columns]], on="team_id", how="left")
    for column in ["active_contributors", "available_contributors", "capacity_units", "junior_share", "low_tenure_share", "senior_expert_contributors"]:
        if column not in features.columns:
            features[column] = 0 if column in ["active_contributors", "available_contributors", "capacity_units"] else np.nan

    features["active_contributors"] = pd.to_numeric(features["active_contributors"], errors="coerce").fillna(0)
    features["available_contributors"] = pd.to_numeric(features["available_contributors"], errors="coerce").fillna(features["active_contributors"])
    features["capacity_units"] = pd.to_numeric(features["capacity_units"], errors="coerce").fillna(0)
    features["required_capacity_units"] = (
        (features["new_items_7d"] + features["open_backlog"] * 0.40)
        * features["avg_task_complexity_score"].fillna(1.0)
        * (1 + features["rework_rate_7d"].fillna(0))
    )
    features["capacity_gap"] = features["capacity_units"] - features["required_capacity_units"]
    features["utilization_rate"] = features.apply(
        lambda row: _safe_divide(row["required_capacity_units"], row["capacity_units"]), axis=1
    ).clip(lower=0)

    q_overlay = _quality_overlay(_safe_df(quality_events), data, _safe_df(teams), group_cols)
    e_overlay = _escalation_overlay(_safe_df(escalation_events), group_cols)
    for overlay in [q_overlay, e_overlay]:
        if not overlay.empty:
            features = features.merge(overlay, on=group_cols, how="left")
    features["quality_risk_overlay"] = pd.to_numeric(features.get("quality_risk_overlay", 0), errors="coerce").fillna(0)
    features["escalation_risk_overlay"] = pd.to_numeric(features.get("escalation_risk_overlay", 0), errors="coerce").fillna(0)

    risk_results = features.apply(score_team_capacity_risk, axis=1)
    features["capacity_risk_score"] = [result.score for result in risk_results]
    features["risk_drivers"] = [_stringify_drivers(result.drivers) for result in risk_results]
    features["capacity_risk_level"] = features.apply(
        lambda row: _risk_level(row["capacity_risk_score"], row["new_items_7d"] + row["completed_items_7d"] + row["open_backlog"]),
        axis=1,
    )
    features["forecasted_sla_risk"] = features.apply(classify_sla_forecast_status, axis=1)
    features["recommended_manager_action"] = features.apply(lambda row: recommend_capacity_action(row, scope="team"), axis=1)

    ordered = [
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
        "sla_miss_rate_7d",
        "rework_rate_7d",
        "high_complexity_share",
        "expert_complexity_share",
        "junior_share",
        "low_tenure_share",
        "capacity_units",
        "required_capacity_units",
        "capacity_gap",
        "utilization_rate",
        "quality_risk_overlay",
        "escalation_risk_overlay",
        "forecasted_sla_risk",
        "capacity_risk_score",
        "capacity_risk_level",
        "risk_drivers",
        "recommended_manager_action",
    ]
    return features[[col for col in ordered if col in features.columns]].sort_values("capacity_risk_score", ascending=False).reset_index(drop=True)


def build_skill_complexity_capacity_features(
    capacity_data: pd.DataFrame | None,
    contributors: pd.DataFrame | None = None,
    quality_events: pd.DataFrame | None = None,
) -> pd.DataFrame:
    data = _safe_df(capacity_data)
    if data.empty:
        return pd.DataFrame(columns=["work_type", "skill_level", "task_complexity", "risk_level"])

    group_cols = ["work_type", "skill_level", "task_complexity"]
    features = _base_group_features(data, group_cols)

    active = data[data["active_status"].astype(str).str.lower().eq("active")].copy()
    active_contributors = active.groupby(group_cols, as_index=False).agg(active_contributors=("contributor_id", "nunique")) if not active.empty else pd.DataFrame(columns=group_cols + ["active_contributors"])
    features = features.merge(active_contributors, on=group_cols, how="left")
    features["active_contributors"] = pd.to_numeric(features["active_contributors"], errors="coerce").fillna(0)

    features["capacity_units"] = features["active_contributors"] * features["skill_level"].map(_skill_capacity_unit).fillna(SKILL_CAPACITY_UNITS["unknown"])
    features["required_capacity_units"] = (
        (features["new_items_7d"] + features["open_backlog"] * 0.40)
        * features["avg_task_complexity_score"].fillna(1.0)
        * (1 + features["rework_rate_7d"].fillna(0))
    )
    features["capacity_gap"] = features["capacity_units"] - features["required_capacity_units"]

    q = _safe_df(quality_events)
    if not q.empty and "work_item_id" in q.columns:
        q_context = q.merge(data[["work_item_id", "work_type", "skill_level", "task_complexity"]].drop_duplicates("work_item_id"), on="work_item_id", how="left")
        q_context = _ensure_columns(q_context, {"quality_score": np.nan})
        quality = q_context.groupby(group_cols, as_index=False).agg(quality_score=("quality_score", "mean"))
        features = features.merge(quality, on=group_cols, how="left")
    else:
        features["quality_score"] = np.nan

    def classify(row: pd.Series) -> str:
        def num(column: str, default: float = 0.0) -> float:
            value = row.get(column, default)
            if _is_missing(value):
                return default
            try:
                return float(value)
            except (TypeError, ValueError):
                return default

        total_activity = num("new_items_7d") + num("completed_items_7d") + num("open_backlog")
        capacity_gap = num("capacity_gap")
        sla_miss_rate = num("sla_miss_rate_7d")
        rework_rate = num("rework_rate_7d")

        if total_activity == 0:
            return "Insufficient data"
        if capacity_gap < -10 or sla_miss_rate > 0.15 or rework_rate > 0.15:
            return "High capacity risk"
        if capacity_gap < 0 or sla_miss_rate > 0.08 or rework_rate > 0.10:
            return "Medium capacity risk"
        return "Low capacity risk"

    features["risk_level"] = features.apply(classify, axis=1)
    features["recommended_action"] = features.apply(recommend_capacity_action, axis=1)

    ordered = [
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
    return features[[col for col in ordered if col in features.columns]].sort_values(["risk_level", "capacity_gap"], ascending=[True, True]).reset_index(drop=True)


def get_weekly_capacity_review_queue(
    work_type_capacity_summary: pd.DataFrame,
    team_capacity_summary: pd.DataFrame,
) -> pd.DataFrame:
    """Return prioritized work types and teams for the Weekly Staffing and Capacity Review Queue."""
    queue_rows: list[dict[str, object]] = []

    work_types = _safe_df(work_type_capacity_summary)
    for _, row in work_types.iterrows():
        capacity_gap_penalty = max(0.0, -float(row.get("capacity_gap", 0) or 0)) * 0.25
        priority = (
            float(row.get("capacity_risk_score", 0) or 0)
            + capacity_gap_penalty
            + float(row.get("aged_backlog_72h", 0) or 0) * 0.30
            + max(0.0, -float(row.get("throughput_gap", 0) or 0)) * 4.0
            + float(row.get("sla_miss_rate_7d", 0) or 0) * 20.0
            + float(row.get("high_complexity_share", 0) or 0) * 8.0
            + float(row.get("quality_risk_overlay", 0) or 0)
            + float(row.get("escalation_risk_overlay", 0) or 0)
        )
        queue_rows.append(
            {
                "card_type": "Work Type",
                "subject_id": row.get("work_type", "Unknown"),
                "work_type": row.get("work_type", "Unknown"),
                "team_id": "All teams",
                "region": row.get("region", "Unknown"),
                "risk_level": row.get("capacity_risk_level", "Insufficient data"),
                "priority_score": round(priority, 1),
                "capacity_risk_score": row.get("capacity_risk_score", 0),
                "capacity_gap": row.get("capacity_gap", 0),
                "aged_backlog_72h": row.get("aged_backlog_72h", 0),
                "throughput_gap": row.get("throughput_gap", 0),
                "sla_miss_rate_7d": row.get("sla_miss_rate_7d", np.nan),
                "utilization_rate": row.get("utilization_rate", np.nan),
                "high_complexity_share": row.get("high_complexity_share", np.nan),
                "quality_risk_overlay": row.get("quality_risk_overlay", 0),
                "escalation_risk_overlay": row.get("escalation_risk_overlay", 0),
                "team_blast_radius": np.nan,
                "recommended_action": row.get("recommended_capacity_action", "Review capacity"),
            }
        )

    teams = _safe_df(team_capacity_summary)
    for _, row in teams.iterrows():
        capacity_gap_penalty = max(0.0, -float(row.get("capacity_gap", 0) or 0)) * 0.30
        team_blast_radius = float(row.get("active_contributors", 0) or 0)
        priority = (
            float(row.get("capacity_risk_score", 0) or 0)
            + capacity_gap_penalty
            + float(row.get("aged_backlog_72h", 0) or 0) * 0.35
            + max(0.0, -float(row.get("throughput_gap", 0) or 0)) * 4.5
            + float(row.get("sla_miss_rate_7d", 0) or 0) * 22.0
            + float(row.get("utilization_rate", 0) or 0) * 6.0
            + float(row.get("high_complexity_share", 0) or 0) * 8.0
            + float(row.get("quality_risk_overlay", 0) or 0)
            + float(row.get("escalation_risk_overlay", 0) or 0)
            + team_blast_radius * 0.05
        )
        queue_rows.append(
            {
                "card_type": "Team",
                "subject_id": row.get("team_id", "Unknown"),
                "work_type": row.get("work_type", "Unknown"),
                "team_id": row.get("team_id", "Unknown"),
                "region": row.get("region", "Unknown"),
                "manager_name": row.get("manager_name", "Unknown"),
                "risk_level": row.get("capacity_risk_level", "Insufficient data"),
                "priority_score": round(priority, 1),
                "capacity_risk_score": row.get("capacity_risk_score", 0),
                "capacity_gap": row.get("capacity_gap", 0),
                "aged_backlog_72h": row.get("aged_backlog_72h", 0),
                "throughput_gap": row.get("throughput_gap", 0),
                "sla_miss_rate_7d": row.get("sla_miss_rate_7d", np.nan),
                "utilization_rate": row.get("utilization_rate", np.nan),
                "high_complexity_share": row.get("high_complexity_share", np.nan),
                "quality_risk_overlay": row.get("quality_risk_overlay", 0),
                "escalation_risk_overlay": row.get("escalation_risk_overlay", 0),
                "team_blast_radius": team_blast_radius,
                "recommended_action": row.get("recommended_manager_action", "Review capacity"),
            }
        )

    queue = pd.DataFrame(queue_rows)
    if queue.empty:
        return pd.DataFrame(
            columns=[
                "queue_rank",
                "card_type",
                "subject_id",
                "team_id",
                "work_type",
                "risk_level",
                "priority_score",
                "recommended_action",
            ]
        )
    queue = queue[queue["risk_level"].astype(str).ne("Low capacity risk") | (queue["priority_score"] >= 30)].copy()
    queue = queue.sort_values("priority_score", ascending=False).reset_index(drop=True)
    queue["queue_rank"] = range(1, len(queue) + 1)
    return queue


def build_capacity_trend(capacity_data: pd.DataFrame | None, grain: str, value: str, days: int = 30) -> pd.DataFrame:
    """Build daily inflow, throughput, backlog, and SLA trend for a selected grain value."""
    data = _safe_df(capacity_data)
    if data.empty or grain not in data.columns:
        return pd.DataFrame(columns=["period", "new_items", "completed_items", "open_backlog", "sla_adherence"])
    scoped = data[data[grain].astype(str) == str(value)].copy()
    if scoped.empty:
        return pd.DataFrame(columns=["period", "new_items", "completed_items", "open_backlog", "sla_adherence"])

    max_date = _latest_reference_date(scoped)
    start = max_date - pd.Timedelta(days=days - 1)
    periods = pd.date_range(start=start, end=max_date, freq="D")
    rows = []
    created = pd.to_datetime(scoped["date_created"], errors="coerce")
    completed = pd.to_datetime(scoped["completed_at"], errors="coerce")
    for period in periods:
        day_start = period.normalize()
        day_end = day_start + pd.Timedelta(days=1)
        created_mask = (created >= day_start) & (created < day_end)
        completed_mask = (completed >= day_start) & (completed < day_end)
        open_mask = (created <= day_end) & (completed.isna() | (completed > day_end))
        completed_day = scoped[completed_mask]
        rows.append(
            {
                "period": day_start.date().isoformat(),
                "new_items": int(created_mask.sum()),
                "completed_items": int(completed_mask.sum()),
                "open_backlog": int(open_mask.sum()),
                "sla_adherence": _rate_true(completed_day["sla_met"]) if not completed_day.empty else np.nan,
            }
        )
    return pd.DataFrame(rows)
