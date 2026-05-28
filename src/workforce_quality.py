"""
Module C: Distributed Workforce Quality Scorer.

This module builds deterministic contributor-, team-, and work-type-level
quality risk features from the synthetic command-center data. It is intended
for coaching, calibration, staffing, and quality-system review; it is not an
individual punitive-ranking engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import log1p
from typing import Iterable

import numpy as np
import pandas as pd


RECENT_WINDOW_DAYS = 30
PRIOR_WINDOW_DAYS = 30
MIN_CONTRIBUTOR_SAMPLE = 3
MIN_TEAM_SAMPLE = 5
QUALITY_TARGET = 90.0
PEER_AGREEMENT_TARGET = 0.82


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


def _fmt_pct(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{float(value) * 100:.1f}%"


def _fmt_float(value: float | int | None, decimals: int = 1) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{float(value):.{decimals}f}"


def _stringify_drivers(drivers: Iterable[str]) -> str:
    values = [driver for driver in drivers if driver]
    return ", ".join(values) if values else "Within expected range"


def _add_event_date(quality: pd.DataFrame) -> pd.DataFrame:
    q = quality.copy()
    candidate_columns = [
        "date_completed",
        "completed_at",
        "date_created",
        "event_date",
        "due_at",
    ]

    event_date = pd.Series(pd.NaT, index=q.index, dtype="datetime64[ns]")
    for column in candidate_columns:
        if column in q.columns:
            event_date = event_date.combine_first(pd.to_datetime(q[column], errors="coerce"))

    if event_date.isna().all():
        max_date = pd.Timestamp.today().normalize()
        if len(q) == 0:
            q["event_date"] = pd.to_datetime([])
            return q
        synthetic_age = pd.Series(np.arange(len(q))[::-1] % 90, index=q.index)
        q["event_date"] = max_date - pd.to_timedelta(synthetic_age, unit="D")
        return q

    max_date = event_date.max()
    fallback_age = pd.Series(np.arange(len(q))[::-1] % 90, index=q.index)
    fallback_dates = max_date - pd.to_timedelta(fallback_age, unit="D")
    q["event_date"] = event_date.fillna(fallback_dates)
    return q


def prepare_quality_data(
    contributors: pd.DataFrame | None,
    quality_events: pd.DataFrame | None,
    work_items: pd.DataFrame | None,
    teams: pd.DataFrame | None,
    escalation_events: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """
    Return a quality-event grain table enriched with contributor, team, and work-item context.

    The function intentionally handles partial synthetic data. If work_items.csv is empty,
    team/work-type context is inferred through contributors and teams, while rework and
    task-complexity fields receive conservative defaults.
    """
    q = _safe_df(quality_events)
    c = _safe_df(contributors)
    wi = _safe_df(work_items)
    t = _safe_df(teams)

    if q.empty:
        return pd.DataFrame(
            columns=[
                "quality_event_id",
                "work_item_id",
                "contributor_id",
                "team_id",
                "work_type",
                "region",
                "quality_score",
                "gold_task_pass",
                "reviewer_override",
                "peer_agreement_score",
                "rework_required",
                "task_complexity",
                "tenure_days",
                "skill_level",
                "location_type",
                "active_status",
                "customer_segment",
                "manager_name",
                "event_date",
            ]
        )

    q = _ensure_columns(
        q,
        {
            "quality_event_id": pd.NA,
            "work_item_id": pd.NA,
            "contributor_id": pd.NA,
            "reviewer_id": pd.NA,
            "quality_score": np.nan,
            "gold_task_pass": pd.NA,
            "reviewer_override": pd.NA,
            "peer_agreement_score": np.nan,
        },
    )

    wi_defaults = {
        "work_item_id": pd.NA,
        "date_created": pd.NaT,
        "date_completed": pd.NaT,
        "region": pd.NA,
        "work_type": pd.NA,
        "team_id": pd.NA,
        "contributor_id": pd.NA,
        "customer_segment": pd.NA,
        "status": pd.NA,
        "rework_required": False,
        "task_complexity": "medium",
    }
    wi = _ensure_columns(wi, wi_defaults)

    if not wi.empty and "work_item_id" in wi.columns:
        merge_cols = [
            "work_item_id",
            "date_created",
            "date_completed",
            "region",
            "work_type",
            "team_id",
            "contributor_id",
            "customer_segment",
            "status",
            "rework_required",
            "task_complexity",
        ]
        q = q.merge(
            wi[merge_cols].drop_duplicates("work_item_id"),
            on="work_item_id",
            how="left",
            suffixes=("", "_work_item"),
        )
        if "contributor_id_work_item" in q.columns:
            q["contributor_id"] = q["contributor_id"].combine_first(q["contributor_id_work_item"])
            q = q.drop(columns=["contributor_id_work_item"])

    q = _ensure_columns(
        q,
        {
            "team_id": pd.NA,
            "work_type": pd.NA,
            "region": pd.NA,
            "customer_segment": pd.NA,
            "rework_required": False,
            "task_complexity": "medium",
            "date_created": pd.NaT,
            "date_completed": pd.NaT,
            "status": pd.NA,
        },
    )

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
            [
                "contributor_id",
                "team_id",
                "tenure_days",
                "skill_level",
                "location_type",
                "active_status",
            ]
        ].drop_duplicates("contributor_id")
        contributor_context = contributor_context.rename(columns={"team_id": "team_id_contributor"})
        q = q.merge(contributor_context, on="contributor_id", how="left")
        q["team_id"] = q["team_id"].combine_first(q["team_id_contributor"])
        q = q.drop(columns=["team_id_contributor"])
    else:
        q = _ensure_columns(
            q,
            {
                "tenure_days": np.nan,
                "skill_level": "Unknown",
                "location_type": "Unknown",
                "active_status": "Unknown",
            },
        )

    t = _ensure_columns(
        t,
        {
            "team_id": pd.NA,
            "region": pd.NA,
            "manager_name": "Unknown",
            "work_type": pd.NA,
            "active_contributors": np.nan,
        },
    )
    if not t.empty:
        team_context = t[
            ["team_id", "region", "manager_name", "work_type", "active_contributors"]
        ].drop_duplicates("team_id")
        team_context = team_context.rename(
            columns={"region": "region_team", "work_type": "work_type_team"}
        )
        q = q.merge(team_context, on="team_id", how="left")
        q["work_type"] = q["work_type"].combine_first(q["work_type_team"])
        q["region"] = q["region"].combine_first(q["region_team"])
        q = q.drop(columns=["work_type_team", "region_team"])
    else:
        q = _ensure_columns(q, {"manager_name": "Unknown", "active_contributors": np.nan})

    q["quality_score"] = pd.to_numeric(q["quality_score"], errors="coerce")
    q["peer_agreement_score"] = pd.to_numeric(q["peer_agreement_score"], errors="coerce")
    q["tenure_days"] = pd.to_numeric(q["tenure_days"], errors="coerce")
    q["gold_task_pass"] = _to_bool(q["gold_task_pass"])
    q["reviewer_override"] = _to_bool(q["reviewer_override"])
    q["rework_required"] = _to_bool(q["rework_required"]).fillna(False)
    q["task_complexity"] = q["task_complexity"].fillna("medium").astype(str)
    q["work_type"] = q["work_type"].fillna("Unknown").astype(str)
    q["team_id"] = q["team_id"].fillna("Unknown").astype(str)
    q["region"] = q["region"].fillna("Unknown").astype(str)
    q["skill_level"] = q["skill_level"].fillna("Unknown").astype(str)
    q["location_type"] = q["location_type"].fillna("Unknown").astype(str)
    q["active_status"] = q["active_status"].fillna("Unknown").astype(str)
    q["customer_segment"] = q["customer_segment"].fillna("Unknown").astype(str)
    q["manager_name"] = q["manager_name"].fillna("Unknown").astype(str)
    q = _add_event_date(q)

    return q


def _recent_prior_windows(quality: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if quality.empty or "event_date" not in quality.columns:
        return quality.iloc[0:0].copy(), quality.iloc[0:0].copy()
    dates = pd.to_datetime(quality["event_date"], errors="coerce")
    if dates.isna().all():
        return quality.iloc[0:0].copy(), quality.iloc[0:0].copy()
    max_date = dates.max()
    recent_start = max_date - pd.Timedelta(days=RECENT_WINDOW_DAYS)
    prior_start = recent_start - pd.Timedelta(days=PRIOR_WINDOW_DAYS)
    recent = quality[dates > recent_start].copy()
    prior = quality[(dates <= recent_start) & (dates > prior_start)].copy()
    return recent, prior


def _completed_items_by_contributor(work_items: pd.DataFrame, quality: pd.DataFrame) -> pd.DataFrame:
    wi = _safe_df(work_items)
    if not wi.empty and {"contributor_id", "work_item_id"}.issubset(wi.columns):
        candidate = wi.copy()
        if "status" in candidate.columns:
            completed = candidate[candidate["status"].astype(str).eq("completed")].copy()
            if completed.empty:
                completed = candidate
        else:
            completed = candidate
        return (
            completed.groupby("contributor_id", as_index=False)
            .agg(completed_items=("work_item_id", "nunique"))
        )
    if not quality.empty:
        return (
            quality.groupby("contributor_id", as_index=False)
            .agg(completed_items=("work_item_id", "nunique"))
        )
    return pd.DataFrame(columns=["contributor_id", "completed_items"])


def _contributor_risk_details(row: pd.Series) -> RiskResult:
    sample = int(row.get("sampled_quality_events", 0) or 0)
    if sample < MIN_CONTRIBUTOR_SAMPLE:
        return RiskResult(score=0.0, drivers=("Insufficient sample",))

    avg_quality = float(row.get("avg_quality_score", np.nan))
    fail_rate = float(row.get("gold_task_fail_rate", 0) or 0)
    override_rate = float(row.get("reviewer_override_rate", 0) or 0)
    peer_agreement = float(row.get("avg_peer_agreement_score", np.nan))
    rework_rate = float(row.get("rework_rate", 0) or 0)
    quality_delta = float(row.get("quality_delta", 0) or 0)
    tenure_days = float(row.get("tenure_days", np.nan))
    high_complexity_share = float(row.get("high_complexity_share", 0) or 0)
    expert_complexity_share = float(row.get("expert_complexity_share", 0) or 0)

    score = 0.0
    drivers: list[str] = []

    if not pd.isna(avg_quality):
        quality_gap = max(0.0, QUALITY_TARGET - avg_quality)
        score += quality_gap * 1.2
        if quality_gap >= 4:
            drivers.append("Average quality below target")

    score += fail_rate * 30
    if fail_rate >= 0.15:
        drivers.append("Low gold task pass rate")

    score += override_rate * 25
    if override_rate >= 0.10:
        drivers.append("High reviewer override rate")

    if not pd.isna(peer_agreement):
        peer_penalty = max(0.0, PEER_AGREEMENT_TARGET - peer_agreement) * 45
        score += peer_penalty
        if peer_agreement < 0.78:
            drivers.append("Low peer agreement")

    score += rework_rate * 25
    if rework_rate >= 0.12:
        drivers.append("High rework rate")

    if quality_delta <= -4:
        score += min(18.0, abs(quality_delta) * 1.8)
        drivers.append("Recent quality drop")

    if not pd.isna(tenure_days) and tenure_days < 90 and high_complexity_share >= 0.25:
        score += 8 + expert_complexity_share * 6
        drivers.append("Low tenure plus high complexity")

    if sample < 8:
        score += 5
        drivers.append("Low sample size")

    return RiskResult(score=round(float(min(score, 100.0)), 1), drivers=tuple(dict.fromkeys(drivers)))


def score_contributor_quality_risk(row: pd.Series) -> float:
    """Return deterministic contributor quality risk score from 0 to 100."""
    return _contributor_risk_details(row).score


def classify_quality_status(row: pd.Series) -> str:
    sample = int(row.get("sampled_quality_events", 0) or 0)
    if sample < MIN_CONTRIBUTOR_SAMPLE:
        return "Insufficient sample"

    quality_delta = row.get("quality_delta", np.nan)
    override_rate = float(row.get("reviewer_override_rate", 0) or 0)
    peer_agreement = row.get("avg_peer_agreement_score", np.nan)

    if not pd.isna(quality_delta) and quality_delta <= -4:
        return "Declining"
    if override_rate >= 0.12 or (not pd.isna(peer_agreement) and peer_agreement < 0.76):
        return "Volatile"
    if not pd.isna(quality_delta) and quality_delta >= 4:
        return "Improving"
    return "Stable"


def _risk_level(score: float, sample: int, min_sample: int, high: float, medium: float) -> str:
    if sample < min_sample:
        return "Insufficient sample"
    if score >= high:
        return "High quality risk"
    if score >= medium:
        return "Medium quality risk"
    return "Low quality risk"


def recommend_quality_action(row: pd.Series) -> str:
    details = _contributor_risk_details(row)
    drivers = set(details.drivers)

    if "Insufficient sample" in drivers:
        return "Increase QA sampling before making a coaching decision"
    if "Low gold task pass rate" in drivers:
        return "Gold task review + targeted coaching"
    if "High reviewer override rate" in drivers:
        return "Reviewer calibration + manager review"
    if "Low peer agreement" in drivers:
        return "Calibration huddle"
    if "High rework rate" in drivers:
        return "Workflow coaching + task instruction review"
    if "Recent quality drop" in drivers:
        return "Manager coaching check-in"
    if "Low tenure plus high complexity" in drivers:
        return "Training module update + gradual ramp"
    if "Average quality below target" in drivers:
        return "Targeted quality coaching and sampling review"
    return "Continue standard monitoring"


def build_contributor_quality_features(
    contributors: pd.DataFrame | None,
    quality_events: pd.DataFrame | None,
    work_items: pd.DataFrame | None,
    teams: pd.DataFrame | None,
) -> pd.DataFrame:
    quality = prepare_quality_data(contributors, quality_events, work_items, teams)
    c = _safe_df(contributors)
    t = _safe_df(teams)

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
    t = _ensure_columns(
        t,
        {"team_id": pd.NA, "work_type": "Unknown", "region": "Unknown"},
    )

    if c.empty:
        base = quality[
            ["contributor_id", "team_id", "work_type", "tenure_days", "skill_level", "location_type", "active_status"]
        ].drop_duplicates("contributor_id")
    else:
        base = c[
            [
                "contributor_id",
                "team_id",
                "tenure_days",
                "skill_level",
                "location_type",
                "active_status",
            ]
        ].drop_duplicates("contributor_id")
        if not t.empty:
            team_context = t[["team_id", "work_type", "region"]].drop_duplicates("team_id")
            base = base.merge(team_context, on="team_id", how="left")
        else:
            base["work_type"] = "Unknown"
            base["region"] = "Unknown"

    if quality.empty:
        summary = base.copy()
        for column, default in {
            "completed_items": 0,
            "sampled_quality_events": 0,
            "avg_quality_score": np.nan,
            "gold_task_fail_rate": np.nan,
            "reviewer_override_rate": np.nan,
            "avg_peer_agreement_score": np.nan,
            "rework_rate": np.nan,
            "high_complexity_share": 0.0,
            "expert_complexity_share": 0.0,
            "recent_quality_score": np.nan,
            "prior_quality_score": np.nan,
            "quality_delta": np.nan,
            "recent_rework_rate": np.nan,
        }.items():
            summary[column] = default
    else:
        grouped = quality.groupby("contributor_id")
        agg = grouped.agg(
            team_id_quality=("team_id", _mode_or_unknown),
            work_type_quality=("work_type", _mode_or_unknown),
            sampled_quality_events=("quality_event_id", "count"),
            avg_quality_score=("quality_score", "mean"),
            gold_task_fail_rate=("gold_task_pass", _rate_false),
            reviewer_override_rate=("reviewer_override", _rate_true),
            avg_peer_agreement_score=("peer_agreement_score", "mean"),
            rework_rate=("rework_required", _rate_true),
            high_complexity_share=("task_complexity", lambda s: s.astype(str).isin(["high", "expert"]).mean()),
            expert_complexity_share=("task_complexity", lambda s: s.astype(str).eq("expert").mean()),
        ).reset_index()

        recent, prior = _recent_prior_windows(quality)
        recent_score = (
            recent.groupby("contributor_id")
            .agg(
                recent_quality_score=("quality_score", "mean"),
                recent_rework_rate=("rework_required", _rate_true),
            )
            .reset_index()
            if not recent.empty
            else pd.DataFrame(columns=["contributor_id", "recent_quality_score", "recent_rework_rate"])
        )
        prior_score = (
            prior.groupby("contributor_id")
            .agg(prior_quality_score=("quality_score", "mean"))
            .reset_index()
            if not prior.empty
            else pd.DataFrame(columns=["contributor_id", "prior_quality_score"])
        )
        completed = _completed_items_by_contributor(_safe_df(work_items), quality)

        summary = base.merge(agg, on="contributor_id", how="outer")
        summary["team_id"] = summary.get("team_id").combine_first(summary.get("team_id_quality"))
        summary["work_type"] = summary.get("work_type").combine_first(summary.get("work_type_quality"))
        summary = summary.drop(columns=[col for col in ["team_id_quality", "work_type_quality"] if col in summary.columns])
        summary = summary.merge(completed, on="contributor_id", how="left")
        summary = summary.merge(recent_score, on="contributor_id", how="left")
        summary = summary.merge(prior_score, on="contributor_id", how="left")
        summary["quality_delta"] = summary["recent_quality_score"] - summary["prior_quality_score"]

    numeric_defaults = {
        "completed_items": 0,
        "sampled_quality_events": 0,
        "gold_task_fail_rate": 0.0,
        "reviewer_override_rate": 0.0,
        "rework_rate": 0.0,
        "high_complexity_share": 0.0,
        "expert_complexity_share": 0.0,
    }
    for column, default in numeric_defaults.items():
        if column not in summary.columns:
            summary[column] = default
        summary[column] = pd.to_numeric(summary[column], errors="coerce").fillna(default)

    for column in ["team_id", "work_type", "skill_level", "location_type", "active_status"]:
        if column not in summary.columns:
            summary[column] = "Unknown"
        summary[column] = summary[column].fillna("Unknown").astype(str)

    summary["tenure_days"] = pd.to_numeric(summary.get("tenure_days"), errors="coerce")
    summary["avg_quality_score"] = pd.to_numeric(summary.get("avg_quality_score"), errors="coerce")
    summary["avg_peer_agreement_score"] = pd.to_numeric(summary.get("avg_peer_agreement_score"), errors="coerce")
    summary["recent_quality_score"] = pd.to_numeric(summary.get("recent_quality_score"), errors="coerce")
    summary["prior_quality_score"] = pd.to_numeric(summary.get("prior_quality_score"), errors="coerce")
    summary["quality_delta"] = pd.to_numeric(summary.get("quality_delta"), errors="coerce")
    summary["recent_rework_rate"] = pd.to_numeric(summary.get("recent_rework_rate"), errors="coerce")

    summary["risk_score"] = summary.apply(score_contributor_quality_risk, axis=1)
    summary["risk_level"] = summary.apply(
        lambda row: _risk_level(
            float(row["risk_score"]),
            int(row["sampled_quality_events"]),
            MIN_CONTRIBUTOR_SAMPLE,
            high=35,
            medium=20,
        ),
        axis=1,
    )
    summary["risk_status"] = summary.apply(classify_quality_status, axis=1)
    summary["risk_drivers"] = summary.apply(
        lambda row: _stringify_drivers(_contributor_risk_details(row).drivers), axis=1
    )
    summary["recommended_action"] = summary.apply(recommend_quality_action, axis=1)

    ordered = [
        "contributor_id",
        "team_id",
        "work_type",
        "skill_level",
        "tenure_days",
        "location_type",
        "active_status",
        "completed_items",
        "sampled_quality_events",
        "avg_quality_score",
        "gold_task_fail_rate",
        "reviewer_override_rate",
        "avg_peer_agreement_score",
        "rework_rate",
        "high_complexity_share",
        "expert_complexity_share",
        "recent_quality_score",
        "prior_quality_score",
        "quality_delta",
        "recent_rework_rate",
        "risk_status",
        "risk_score",
        "risk_level",
        "risk_drivers",
        "recommended_action",
    ]
    return summary[[col for col in ordered if col in summary.columns]].sort_values(
        ["risk_score", "sampled_quality_events"], ascending=[False, False]
    )


def _team_risk_details(row: pd.Series) -> RiskResult:
    sample = int(row.get("sampled_quality_events", 0) or 0)
    if sample < MIN_TEAM_SAMPLE:
        return RiskResult(score=0.0, drivers=("Insufficient sample",))

    avg_quality = float(row.get("avg_quality_score", np.nan))
    fail_rate = float(row.get("gold_task_fail_rate", 0) or 0)
    override_rate = float(row.get("reviewer_override_rate", 0) or 0)
    rework_rate = float(row.get("rework_rate", 0) or 0)
    high_risk_count = float(row.get("high_risk_contributor_count", 0) or 0)
    medium_risk_count = float(row.get("medium_risk_contributor_count", 0) or 0)
    low_tenure_share = float(row.get("low_tenure_share", 0) or 0)
    quality_delta = float(row.get("quality_delta", 0) or 0)

    score = 0.0
    drivers: list[str] = []

    if not pd.isna(avg_quality):
        quality_gap = max(0.0, QUALITY_TARGET - avg_quality)
        score += quality_gap * 1.1
        if quality_gap >= 4:
            drivers.append("Average team quality below target")

    score += fail_rate * 30
    if fail_rate >= 0.15:
        drivers.append("Team gold task fail rate")

    score += override_rate * 25
    if override_rate >= 0.10:
        drivers.append("Team reviewer override rate")

    score += rework_rate * 25
    if rework_rate >= 0.12:
        drivers.append("Team rework rate")

    score += min(18.0, high_risk_count * 3.0 + medium_risk_count * 1.2)
    if high_risk_count >= 2:
        drivers.append("High-risk contributor concentration")

    score += low_tenure_share * 8
    if low_tenure_share >= 0.30:
        drivers.append("Low-tenure concentration")

    if quality_delta <= -4:
        score += 10
        drivers.append("Team-wide drift")

    return RiskResult(score=round(float(min(score, 100.0)), 1), drivers=tuple(dict.fromkeys(drivers)))


def score_team_quality_risk(row: pd.Series) -> float:
    """Return deterministic team quality risk score from 0 to 100."""
    return _team_risk_details(row).score


def _recommend_team_action(row: pd.Series) -> str:
    drivers = set(_team_risk_details(row).drivers)
    if "Insufficient sample" in drivers:
        return "Increase team QA sampling before actioning"
    if "Team-wide drift" in drivers:
        return "Team calibration huddle"
    if "Team reviewer override rate" in drivers:
        return "Reviewer calibration + manager review"
    if "Team gold task fail rate" in drivers:
        return "Gold task review + targeted coaching plan"
    if "Team rework rate" in drivers:
        return "Workflow coaching + SOP review"
    if "Low-tenure concentration" in drivers:
        return "Training module update + gradual ramp"
    if "High-risk contributor concentration" in drivers:
        return "Manager coaching queue + QA sampling increase"
    if "Average team quality below target" in drivers:
        return "Team quality review and calibration plan"
    return "Continue standard monitoring"


def build_team_quality_features(
    contributors: pd.DataFrame | None,
    quality_events: pd.DataFrame | None,
    work_items: pd.DataFrame | None,
    teams: pd.DataFrame | None,
    contributor_quality_summary: pd.DataFrame | None = None,
) -> pd.DataFrame:
    quality = prepare_quality_data(contributors, quality_events, work_items, teams)
    t = _safe_df(teams)
    c = _safe_df(contributors)
    contributor_summary = (
        contributor_quality_summary.copy()
        if contributor_quality_summary is not None
        else build_contributor_quality_features(contributors, quality_events, work_items, teams)
    )

    t = _ensure_columns(
        t,
        {
            "team_id": pd.NA,
            "work_type": "Unknown",
            "region": "Unknown",
            "manager_name": "Unknown",
            "active_contributors": np.nan,
        },
    )

    if t.empty:
        base = quality[["team_id", "work_type", "region", "manager_name"]].drop_duplicates("team_id")
        base["active_contributors"] = np.nan
    else:
        base = t[["team_id", "work_type", "region", "manager_name", "active_contributors"]].drop_duplicates("team_id")

    if quality.empty:
        summary = base.copy()
        for column, default in {
            "sampled_quality_events": 0,
            "avg_quality_score": np.nan,
            "gold_task_fail_rate": 0.0,
            "reviewer_override_rate": 0.0,
            "avg_peer_agreement_score": np.nan,
            "rework_rate": 0.0,
            "recent_quality_score": np.nan,
            "prior_quality_score": np.nan,
            "quality_delta": np.nan,
        }.items():
            summary[column] = default
    else:
        agg = (
            quality.groupby("team_id")
            .agg(
                work_type_quality=("work_type", _mode_or_unknown),
                region_quality=("region", _mode_or_unknown),
                sampled_quality_events=("quality_event_id", "count"),
                avg_quality_score=("quality_score", "mean"),
                gold_task_fail_rate=("gold_task_pass", _rate_false),
                reviewer_override_rate=("reviewer_override", _rate_true),
                avg_peer_agreement_score=("peer_agreement_score", "mean"),
                rework_rate=("rework_required", _rate_true),
            )
            .reset_index()
        )
        recent, prior = _recent_prior_windows(quality)
        recent_score = (
            recent.groupby("team_id")
            .agg(recent_quality_score=("quality_score", "mean"))
            .reset_index()
            if not recent.empty
            else pd.DataFrame(columns=["team_id", "recent_quality_score"])
        )
        prior_score = (
            prior.groupby("team_id")
            .agg(prior_quality_score=("quality_score", "mean"))
            .reset_index()
            if not prior.empty
            else pd.DataFrame(columns=["team_id", "prior_quality_score"])
        )
        summary = base.merge(agg, on="team_id", how="outer")
        summary["work_type"] = summary.get("work_type").combine_first(summary.get("work_type_quality"))
        summary["region"] = summary.get("region").combine_first(summary.get("region_quality"))
        summary = summary.drop(columns=[col for col in ["work_type_quality", "region_quality"] if col in summary.columns])
        summary = summary.merge(recent_score, on="team_id", how="left")
        summary = summary.merge(prior_score, on="team_id", how="left")
        summary["quality_delta"] = summary["recent_quality_score"] - summary["prior_quality_score"]

    if not c.empty and {"team_id", "active_status", "tenure_days"}.issubset(c.columns):
        active = c[c["active_status"].astype(str).eq("active")].copy()
        active_counts = active.groupby("team_id").size().reset_index(name="active_contributors_from_roster")
        low_tenure = (
            active.assign(low_tenure=pd.to_numeric(active["tenure_days"], errors="coerce") < 90)
            .groupby("team_id")
            .agg(low_tenure_share=("low_tenure", "mean"))
            .reset_index()
        )
        summary = summary.merge(active_counts, on="team_id", how="left")
        summary["active_contributors"] = summary["active_contributors_from_roster"].combine_first(
            pd.to_numeric(summary.get("active_contributors"), errors="coerce")
        )
        summary = summary.drop(columns=["active_contributors_from_roster"])
        summary = summary.merge(low_tenure, on="team_id", how="left")
    else:
        summary["low_tenure_share"] = 0.0

    if not contributor_summary.empty:
        risk_counts = (
            contributor_summary.groupby("team_id")
            .agg(
                high_risk_contributor_count=(
                    "risk_level",
                    lambda s: s.astype(str).eq("High quality risk").sum(),
                ),
                medium_risk_contributor_count=(
                    "risk_level",
                    lambda s: s.astype(str).eq("Medium quality risk").sum(),
                ),
            )
            .reset_index()
        )
        summary = summary.merge(risk_counts, on="team_id", how="left")
    else:
        summary["high_risk_contributor_count"] = 0
        summary["medium_risk_contributor_count"] = 0

    for column, default in {
        "active_contributors": 0,
        "sampled_quality_events": 0,
        "gold_task_fail_rate": 0.0,
        "reviewer_override_rate": 0.0,
        "rework_rate": 0.0,
        "low_tenure_share": 0.0,
        "high_risk_contributor_count": 0,
        "medium_risk_contributor_count": 0,
    }.items():
        if column not in summary.columns:
            summary[column] = default
        summary[column] = pd.to_numeric(summary[column], errors="coerce").fillna(default)

    summary["quality_drift_flag"] = summary["quality_delta"].apply(
        lambda value: "Yes" if not pd.isna(value) and value <= -4 else "No"
    )
    summary["team_risk_score"] = summary.apply(score_team_quality_risk, axis=1)
    summary["team_risk_level"] = summary.apply(
        lambda row: _risk_level(
            float(row["team_risk_score"]),
            int(row["sampled_quality_events"]),
            MIN_TEAM_SAMPLE,
            high=32,
            medium=18,
        ),
        axis=1,
    )
    summary["risk_score"] = summary["team_risk_score"]
    summary["risk_level"] = summary["team_risk_level"]
    summary["risk_drivers"] = summary.apply(
        lambda row: _stringify_drivers(_team_risk_details(row).drivers), axis=1
    )
    summary["recommended_manager_action"] = summary.apply(_recommend_team_action, axis=1)

    ordered = [
        "team_id",
        "work_type",
        "region",
        "manager_name",
        "active_contributors",
        "sampled_quality_events",
        "avg_quality_score",
        "gold_task_fail_rate",
        "reviewer_override_rate",
        "avg_peer_agreement_score",
        "rework_rate",
        "low_tenure_share",
        "high_risk_contributor_count",
        "medium_risk_contributor_count",
        "recent_quality_score",
        "prior_quality_score",
        "quality_delta",
        "quality_drift_flag",
        "team_risk_score",
        "team_risk_level",
        "risk_score",
        "risk_level",
        "risk_drivers",
        "recommended_manager_action",
    ]
    return summary[[col for col in ordered if col in summary.columns]].sort_values(
        ["team_risk_score", "sampled_quality_events"], ascending=[False, False]
    )


def build_work_type_quality_features(
    contributor_quality_summary: pd.DataFrame,
    team_quality_summary: pd.DataFrame,
) -> pd.DataFrame:
    contributors = _safe_df(contributor_quality_summary)
    teams = _safe_df(team_quality_summary)

    if contributors.empty and teams.empty:
        return pd.DataFrame()

    if contributors.empty:
        contributor_rollup = pd.DataFrame(columns=["work_type"])
    else:
        contributor_rollup = (
            contributors.groupby("work_type")
            .agg(
                contributors=("contributor_id", "nunique"),
                high_risk_contributors=(
                    "risk_level",
                    lambda s: s.astype(str).eq("High quality risk").sum(),
                ),
                medium_risk_contributors=(
                    "risk_level",
                    lambda s: s.astype(str).eq("Medium quality risk").sum(),
                ),
                avg_quality_score=("avg_quality_score", "mean"),
                gold_task_fail_rate=("gold_task_fail_rate", "mean"),
                reviewer_override_rate=("reviewer_override_rate", "mean"),
                avg_peer_agreement_score=("avg_peer_agreement_score", "mean"),
                rework_rate=("rework_rate", "mean"),
                avg_risk_score=("risk_score", "mean"),
            )
            .reset_index()
        )

    if teams.empty:
        team_rollup = pd.DataFrame(columns=["work_type"])
    else:
        team_rollup = (
            teams.groupby("work_type")
            .agg(
                teams=("team_id", "nunique"),
                active_contributors=("active_contributors", "sum"),
                high_risk_teams=(
                    "team_risk_level",
                    lambda s: s.astype(str).eq("High quality risk").sum(),
                ),
                quality_drift_team_count=(
                    "quality_drift_flag",
                    lambda s: s.astype(str).eq("Yes").sum(),
                ),
                team_risk_score=("team_risk_score", "mean"),
            )
            .reset_index()
        )

    summary = contributor_rollup.merge(team_rollup, on="work_type", how="outer")
    for column in [
        "contributors",
        "high_risk_contributors",
        "medium_risk_contributors",
        "teams",
        "active_contributors",
        "high_risk_teams",
        "quality_drift_team_count",
    ]:
        if column in summary.columns:
            summary[column] = pd.to_numeric(summary[column], errors="coerce").fillna(0).astype(int)

    summary["work_type_risk_score"] = summary[[col for col in ["avg_risk_score", "team_risk_score"] if col in summary.columns]].mean(axis=1)
    summary["recommended_action"] = summary.apply(
        lambda row: "SOP review + quality sampling increase"
        if row.get("quality_drift_team_count", 0) > 0 or row.get("high_risk_teams", 0) > 0
        else "Continue monitoring through weekly quality review",
        axis=1,
    )
    return summary.sort_values("work_type_risk_score", ascending=False)


def get_weekly_quality_review_queue(
    contributor_quality_summary: pd.DataFrame,
    team_quality_summary: pd.DataFrame,
    max_items: int = 20,
) -> pd.DataFrame:
    """Build the Weekly Coaching and Calibration Queue."""
    contributors = _safe_df(contributor_quality_summary)
    teams = _safe_df(team_quality_summary)
    rows: list[dict[str, object]] = []

    for _, row in contributors.iterrows():
        sample = float(row.get("sampled_quality_events", 0) or 0)
        peer = float(row.get("avg_peer_agreement_score", 1) or 1)
        quality_delta = float(row.get("quality_delta", 0) or 0)
        priority = (
            float(row.get("risk_score", 0) or 0)
            + max(0.0, -quality_delta) * 1.5
            + float(row.get("gold_task_fail_rate", 0) or 0) * 20
            + float(row.get("reviewer_override_rate", 0) or 0) * 15
            + float(row.get("rework_rate", 0) or 0) * 15
            + max(0.0, 1 - peer) * 10
            + min(6.0, log1p(sample))
        )
        rows.append(
            {
                "card_type": "Contributor",
                "subject_id": row.get("contributor_id"),
                "team_id": row.get("team_id"),
                "work_type": row.get("work_type"),
                "risk_level": row.get("risk_level"),
                "risk_status": row.get("risk_status"),
                "risk_score": row.get("risk_score"),
                "priority_score": round(priority, 1),
                "quality_delta": row.get("quality_delta"),
                "gold_task_fail_rate": row.get("gold_task_fail_rate"),
                "reviewer_override_rate": row.get("reviewer_override_rate"),
                "rework_rate": row.get("rework_rate"),
                "avg_peer_agreement_score": row.get("avg_peer_agreement_score"),
                "sampled_quality_events": row.get("sampled_quality_events"),
                "team_blast_radius": 1,
                "risk_drivers": row.get("risk_drivers"),
                "recommended_action": row.get("recommended_action"),
            }
        )

    for _, row in teams.iterrows():
        sample = float(row.get("sampled_quality_events", 0) or 0)
        peer = float(row.get("avg_peer_agreement_score", 1) or 1)
        quality_delta = float(row.get("quality_delta", 0) or 0)
        blast_radius = float(row.get("active_contributors", 0) or 0)
        priority = (
            float(row.get("team_risk_score", 0) or 0)
            + max(0.0, -quality_delta) * 1.8
            + float(row.get("gold_task_fail_rate", 0) or 0) * 20
            + float(row.get("reviewer_override_rate", 0) or 0) * 15
            + float(row.get("rework_rate", 0) or 0) * 15
            + max(0.0, 1 - peer) * 10
            + min(10.0, log1p(blast_radius))
            + float(row.get("high_risk_contributor_count", 0) or 0) * 2
            + min(6.0, log1p(sample))
        )
        rows.append(
            {
                "card_type": "Team",
                "subject_id": row.get("team_id"),
                "team_id": row.get("team_id"),
                "work_type": row.get("work_type"),
                "risk_level": row.get("team_risk_level"),
                "risk_status": "Declining" if row.get("quality_drift_flag") == "Yes" else "Stable / watch",
                "risk_score": row.get("team_risk_score"),
                "priority_score": round(priority, 1),
                "quality_delta": row.get("quality_delta"),
                "gold_task_fail_rate": row.get("gold_task_fail_rate"),
                "reviewer_override_rate": row.get("reviewer_override_rate"),
                "rework_rate": row.get("rework_rate"),
                "avg_peer_agreement_score": row.get("avg_peer_agreement_score"),
                "sampled_quality_events": row.get("sampled_quality_events"),
                "team_blast_radius": row.get("active_contributors"),
                "risk_drivers": row.get("risk_drivers"),
                "recommended_action": row.get("recommended_manager_action"),
            }
        )

    queue = pd.DataFrame(rows)
    if queue.empty:
        return queue
    queue = queue[queue["risk_level"].astype(str) != "Insufficient sample"].copy()
    queue = queue.sort_values(
        ["priority_score", "risk_score", "sampled_quality_events"],
        ascending=[False, False, False],
    ).head(max_items)
    queue.insert(0, "queue_rank", range(1, len(queue) + 1))
    return queue


def build_quality_trend(
    quality: pd.DataFrame,
    group_column: str,
    group_value: str,
    freq: str = "W",
) -> pd.DataFrame:
    if quality.empty or group_column not in quality.columns:
        return pd.DataFrame(columns=["period", "avg_quality_score", "rework_rate", "sampled_quality_events"])
    subset = quality[quality[group_column].astype(str) == str(group_value)].copy()
    if subset.empty:
        return pd.DataFrame(columns=["period", "avg_quality_score", "rework_rate", "sampled_quality_events"])
    subset["event_date"] = pd.to_datetime(subset["event_date"], errors="coerce")
    subset = subset.dropna(subset=["event_date"])
    if subset.empty:
        return pd.DataFrame(columns=["period", "avg_quality_score", "rework_rate", "sampled_quality_events"])
    subset["period"] = subset["event_date"].dt.to_period(freq).dt.start_time
    return (
        subset.groupby("period")
        .agg(
            avg_quality_score=("quality_score", "mean"),
            rework_rate=("rework_required", _rate_true),
            sampled_quality_events=("quality_event_id", "count"),
        )
        .reset_index()
        .sort_values("period")
    )
