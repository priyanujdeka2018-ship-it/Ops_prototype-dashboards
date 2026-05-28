"""
Business rules, health thresholds, and deterministic anomaly detection.

Phase 5 adds rule-based anomaly detection for:
- SLA drop > 5 percentage points week over week
- CSAT below 4.2
- Aged backlog > threshold
- Escalation rate > rolling baseline + 2 standard deviations
- Quality decline for 3 consecutive periods
- Rework spike > 20% versus prior period
"""

from __future__ import annotations

from datetime import datetime
import pandas as pd


OPEN_STATUSES = ["queued", "in_progress", "blocked"]


HEALTH_THRESHOLDS = {
    "sla_adherence": {
        "green": 0.95,
        "amber": 0.90,
    },
    "csat": {
        "green": 4.4,
        "amber": 4.2,
    },
    "quality_score": {
        "green": 90.0,
        "amber": 85.0,
    },
    "rework_rate": {
        "green": 0.06,
        "amber": 0.10,
    },
    "escalation_rate_per_1000": {
        "green": 8.0,
        "amber": 15.0,
    },
    "aged_backlog_72h": {
        "green": 25,
        "amber": 60,
    },
}


def classify_higher_is_better(value: float, green_threshold: float, amber_threshold: float) -> str:
    if value >= green_threshold:
        return "green"
    if value >= amber_threshold:
        return "amber"
    return "red"


def classify_lower_is_better(value: float, green_threshold: float, amber_threshold: float) -> str:
    if value <= green_threshold:
        return "green"
    if value <= amber_threshold:
        return "amber"
    return "red"


def classify_metric(metric_name: str, value: float | None) -> str:
    if value is None:
        return "unknown"

    thresholds = HEALTH_THRESHOLDS.get(metric_name)

    if thresholds is None:
        raise ValueError(f"No thresholds configured for metric: {metric_name}")

    if metric_name in {"sla_adherence", "csat", "quality_score"}:
        return classify_higher_is_better(
            value=value,
            green_threshold=thresholds["green"],
            amber_threshold=thresholds["amber"],
        )

    if metric_name in {"rework_rate", "escalation_rate_per_1000", "aged_backlog_72h"}:
        return classify_lower_is_better(
            value=value,
            green_threshold=thresholds["green"],
            amber_threshold=thresholds["amber"],
        )

    raise ValueError(f"Unsupported metric classification: {metric_name}")


def _bool_true(series: pd.Series) -> pd.Series:
    """Handle bools or string booleans from CSV."""
    return series.astype(str).str.lower().isin(["true", "1", "yes"])


def _safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _severity_from_status(status: str) -> str:
    if status == "red":
        return "High"
    if status == "amber":
        return "Medium"
    return "Low"


def _add_anomaly(
    rows: list[dict],
    anomaly_type: str,
    work_type: str,
    severity: str,
    metric: str,
    current_value: float,
    previous_value: float | None,
    description: str,
    recommended_action: str,
) -> None:
    rows.append(
        {
            "severity": severity,
            "work_type": work_type,
            "anomaly_type": anomaly_type,
            "metric": metric,
            "current_value": current_value,
            "previous_value": previous_value,
            "description": description,
            "recommended_action": recommended_action,
        }
    )


def detect_anomalies(
    work_items: pd.DataFrame,
    quality_events: pd.DataFrame,
    escalation_events: pd.DataFrame,
    csat_events: pd.DataFrame,
) -> pd.DataFrame:
    """Return deterministic anomaly flags for the dashboard."""
    rows: list[dict] = []

    wi = work_items.copy()
    wi["date_created"] = pd.to_datetime(wi["date_created"])
    wi["week"] = wi["date_created"].dt.to_period("W").dt.start_time

    for work_type in sorted(wi["work_type"].dropna().unique()):
        wt_items = wi[wi["work_type"] == work_type].copy()
        completed = wt_items[wt_items["status"] == "completed"].copy()

        # 1. SLA drop > 5 percentage points week over week.
        if not completed.empty:
            weekly_sla = (
                completed.groupby("week")
                .agg(
                    completed_items=("work_item_id", "count"),
                    sla_met=("sla_met", lambda x: _bool_true(x).sum()),
                )
                .reset_index()
                .sort_values("week")
            )
            weekly_sla["sla_rate"] = weekly_sla["sla_met"] / weekly_sla["completed_items"]

            if len(weekly_sla) >= 2:
                previous = float(weekly_sla.iloc[-2]["sla_rate"])
                current = float(weekly_sla.iloc[-1]["sla_rate"])
                drop = previous - current

                if drop > 0.05:
                    _add_anomaly(
                        rows,
                        anomaly_type="SLA deterioration",
                        work_type=work_type,
                        severity="High" if drop > 0.10 else "Medium",
                        metric="sla_adherence",
                        current_value=current,
                        previous_value=previous,
                        description=f"SLA dropped by {drop * 100:.1f} percentage points week over week.",
                        recommended_action="Review capacity, shift coverage, queue routing, and top SLA delay reasons for this work type.",
                    )

        # 2. Aged backlog > threshold.
        open_items = wt_items[wt_items["status"].isin(OPEN_STATUSES)].copy()
        if not open_items.empty:
            open_items["age_hours"] = (
                pd.Timestamp.now() - open_items["date_created"]
            ).dt.total_seconds() / 3600
            aged_count = int((open_items["age_hours"] > 72).sum())
            status = classify_metric("aged_backlog_72h", aged_count)

            if status in {"amber", "red"}:
                _add_anomaly(
                    rows,
                    anomaly_type="Aged backlog risk",
                    work_type=work_type,
                    severity=_severity_from_status(status),
                    metric="aged_backlog_72h",
                    current_value=float(aged_count),
                    previous_value=None,
                    description=f"{aged_count} open items are older than 72 hours.",
                    recommended_action="Ask frontline managers to clear oldest queues first and separate capacity shortage from workflow blockage.",
                )

        # 3. Rework spike > 20% versus prior week.
        if not completed.empty:
            completed["rework_bool"] = _bool_true(completed["rework_required"])
            weekly_rework = (
                completed.groupby("week")
                .agg(
                    completed_items=("work_item_id", "count"),
                    rework_items=("rework_bool", "sum"),
                )
                .reset_index()
                .sort_values("week")
            )
            weekly_rework["rework_rate"] = weekly_rework["rework_items"] / weekly_rework["completed_items"]

            if len(weekly_rework) >= 2:
                previous = float(weekly_rework.iloc[-2]["rework_rate"])
                current = float(weekly_rework.iloc[-1]["rework_rate"])

                if previous > 0 and current > previous * 1.20:
                    _add_anomaly(
                        rows,
                        anomaly_type="Rework spike",
                        work_type=work_type,
                        severity="High" if current > 0.12 else "Medium",
                        metric="rework_rate",
                        current_value=current,
                        previous_value=previous,
                        description=f"Rework rate increased by more than 20% versus the prior week.",
                        recommended_action="Review quality rubric clarity, reviewer calibration, and whether task complexity mix changed.",
                    )

        # 4. CSAT below 4.2.
        ce = csat_events[csat_events["work_type"] == work_type].copy()
        if not ce.empty:
            ce["date"] = pd.to_datetime(ce["date"])
            max_date = ce["date"].max()
            recent_csat = ce[ce["date"] >= max_date - pd.Timedelta(days=7)]

            if not recent_csat.empty:
                csat_avg = float(recent_csat["csat_score"].mean())
                if csat_avg < 4.2:
                    _add_anomaly(
                        rows,
                        anomaly_type="CSAT below threshold",
                        work_type=work_type,
                        severity="High" if csat_avg < 4.0 else "Medium",
                        metric="csat_trailing_7d",
                        current_value=csat_avg,
                        previous_value=None,
                        description=f"Trailing 7-day CSAT is {csat_avg:.2f}, below the 4.2 threshold.",
                        recommended_action="Review recent customer feedback themes and compare against SLA misses, rework, and escalation causes.",
                    )

        # 5. Quality decline for 3 consecutive periods.
        qe = quality_events[
            quality_events["work_item_id"].isin(wt_items["work_item_id"])
        ].copy()

        if not qe.empty:
            qe = qe.merge(
                wt_items[["work_item_id", "date_created"]],
                on="work_item_id",
                how="left",
            )
            qe["week"] = pd.to_datetime(qe["date_created"]).dt.to_period("W").dt.start_time
            weekly_quality = (
                qe.groupby("week")
                .agg(avg_quality=("quality_score", "mean"))
                .reset_index()
                .sort_values("week")
            )

            if len(weekly_quality) >= 3:
                q1 = float(weekly_quality.iloc[-3]["avg_quality"])
                q2 = float(weekly_quality.iloc[-2]["avg_quality"])
                q3 = float(weekly_quality.iloc[-1]["avg_quality"])

                if q1 > q2 > q3:
                    _add_anomaly(
                        rows,
                        anomaly_type="Quality decline",
                        work_type=work_type,
                        severity="High" if q3 < 85 else "Medium",
                        metric="average_quality_score",
                        current_value=q3,
                        previous_value=q1,
                        description="Quality score declined for three consecutive weekly periods.",
                        recommended_action="Run reviewer calibration, inspect gold task pass rates, and coach teams with rising rework.",
                    )

        # 6. Escalation rate > rolling baseline + 2 standard deviations.
        ee = escalation_events[escalation_events["work_type"] == work_type].copy()
        if not ee.empty and not wt_items.empty:
            ee["date"] = pd.to_datetime(ee["date"])
            ee["week"] = ee["date"].dt.to_period("W").dt.start_time

            weekly_escalations = (
                ee.groupby("week")
                .agg(escalations=("escalation_id", "count"))
                .reset_index()
                .sort_values("week")
            )

            item_weekly = (
                wt_items.groupby("week")
                .agg(work_items=("work_item_id", "count"))
                .reset_index()
            )

            weekly = weekly_escalations.merge(item_weekly, on="week", how="left")
            weekly["rate_per_1000"] = weekly.apply(
                lambda row: _safe_divide(row["escalations"], row["work_items"]) * 1000,
                axis=1,
            )

            if len(weekly) >= 5:
                baseline = weekly.iloc[:-1]["rate_per_1000"]
                current = float(weekly.iloc[-1]["rate_per_1000"])
                threshold = float(baseline.mean() + 2 * baseline.std())

                if current > threshold:
                    _add_anomaly(
                        rows,
                        anomaly_type="Escalation spike",
                        work_type=work_type,
                        severity="High",
                        metric="escalation_rate_per_1000",
                        current_value=current,
                        previous_value=threshold,
                        description="Escalation rate is above rolling baseline plus two standard deviations.",
                        recommended_action="Review recent escalation summaries and isolate repeat root-cause categories.",
                    )

    if not rows:
        return pd.DataFrame(
            columns=[
                "severity",
                "work_type",
                "anomaly_type",
                "metric",
                "current_value",
                "previous_value",
                "description",
                "recommended_action",
            ]
        )

    result = pd.DataFrame(rows)

    severity_order = {"High": 3, "Medium": 2, "Low": 1}
    result["severity_rank"] = result["severity"].map(severity_order).fillna(0)
    result = result.sort_values(["severity_rank", "work_type"], ascending=[False, True])
    result = result.drop(columns=["severity_rank"])

    return result
