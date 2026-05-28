"""
Reusable metric calculations for the Scale Regional Ops Health Dashboard.
"""

from __future__ import annotations

from datetime import datetime
import pandas as pd


OPEN_STATUSES = ["queued", "in_progress", "blocked"]


def safe_divide(numerator: float, denominator: float) -> float:
    """Avoid divide-by-zero errors."""
    if denominator == 0:
        return 0.0
    return numerator / denominator


def sla_adherence(work_items: pd.DataFrame) -> float:
    """Completed work items with SLA met divided by completed work items."""
    completed = work_items[work_items["status"] == "completed"]
    return safe_divide(completed["sla_met"].eq(True).sum(), len(completed))


def backlog_count(work_items: pd.DataFrame) -> int:
    """Count open backlog items."""
    return int(work_items["status"].isin(OPEN_STATUSES).sum())


def aged_backlog_count(work_items: pd.DataFrame, as_of: datetime | None = None, hours: int = 72) -> int:
    """Count open backlog items older than a threshold."""
    if as_of is None:
        as_of = datetime.now()

    df = work_items.copy()
    df["date_created"] = pd.to_datetime(df["date_created"])
    open_items = df[df["status"].isin(OPEN_STATUSES)].copy()
    open_items["age_hours"] = (as_of - open_items["date_created"]).dt.total_seconds() / 3600

    return int((open_items["age_hours"] > hours).sum())


def average_quality_score(quality_events: pd.DataFrame) -> float:
    """Average quality score."""
    if quality_events.empty:
        return 0.0
    return float(quality_events["quality_score"].mean())


def rework_rate(work_items: pd.DataFrame) -> float:
    """Completed work items requiring rework divided by completed work items."""
    completed = work_items[work_items["status"] == "completed"]
    return safe_divide(completed["rework_required"].eq(True).sum(), len(completed))


def csat_trailing_average(csat_events: pd.DataFrame, days: int = 7) -> float:
    """Average CSAT score over trailing N days."""
    if csat_events.empty:
        return 0.0

    df = csat_events.copy()
    df["date"] = pd.to_datetime(df["date"])

    max_date = df["date"].max()
    start_date = max_date - pd.Timedelta(days=days)

    trailing = df[df["date"] >= start_date]

    if trailing.empty:
        return 0.0

    return float(trailing["csat_score"].mean())


def escalation_rate_per_1000(escalation_events: pd.DataFrame, work_items: pd.DataFrame) -> float:
    """Escalations per 1,000 work items."""
    return safe_divide(len(escalation_events), len(work_items)) * 1000


def fcr_proxy(work_items: pd.DataFrame) -> float:
    """
    First-contact-resolution proxy.

    For MVP:
    completed items with SLA met and no rework divided by completed items.
    """
    completed = work_items[work_items["status"] == "completed"]
    good = completed[
        (completed["sla_met"].eq(True))
        & (completed["rework_required"].eq(False))
    ]
    return safe_divide(len(good), len(completed))


def executive_kpis(
    work_items: pd.DataFrame,
    quality_events: pd.DataFrame,
    escalation_events: pd.DataFrame,
    csat_events: pd.DataFrame,
) -> dict:
    """Calculate top-level executive KPI tiles."""
    return {
        "sla_adherence": sla_adherence(work_items),
        "csat_trailing_7d": csat_trailing_average(csat_events, days=7),
        "backlog_count": backlog_count(work_items),
        "aged_backlog_72h": aged_backlog_count(work_items, hours=72),
        "escalation_rate_per_1000": escalation_rate_per_1000(escalation_events, work_items),
        "average_quality_score": average_quality_score(quality_events),
        "rework_rate": rework_rate(work_items),
        "fcr_proxy": fcr_proxy(work_items),
    }


def group_metrics_by_work_type(
    work_items: pd.DataFrame,
    quality_events: pd.DataFrame,
    escalation_events: pd.DataFrame,
    csat_events: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate dashboard metrics by work type."""
    rows = []

    for work_type in sorted(work_items["work_type"].dropna().unique()):
        wi = work_items[work_items["work_type"] == work_type]
        qe = quality_events[
            quality_events["work_item_id"].isin(wi["work_item_id"])
        ]
        ee = escalation_events[escalation_events["work_type"] == work_type]
        ce = csat_events[csat_events["work_type"] == work_type]

        rows.append(
            {
                "work_type": work_type,
                "sla_adherence": sla_adherence(wi),
                "backlog_count": backlog_count(wi),
                "aged_backlog_72h": aged_backlog_count(wi),
                "csat_trailing_7d": csat_trailing_average(ce, days=7),
                "average_quality_score": average_quality_score(qe),
                "escalation_rate_per_1000": escalation_rate_per_1000(ee, wi),
                "rework_rate": rework_rate(wi),
                "fcr_proxy": fcr_proxy(wi),
                "work_item_count": len(wi),
                "escalation_count": len(ee),
            }
        )

    return pd.DataFrame(rows)


def group_metrics_by_team(
    work_items: pd.DataFrame,
    quality_events: pd.DataFrame,
    escalation_events: pd.DataFrame,
    csat_events: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate dashboard metrics by team."""
    rows = []

    for team_id in sorted(work_items["team_id"].dropna().unique()):
        wi = work_items[work_items["team_id"] == team_id]
        work_type = wi["work_type"].mode().iloc[0] if not wi.empty else None

        qe = quality_events[
            quality_events["work_item_id"].isin(wi["work_item_id"])
        ]
        ee = escalation_events[escalation_events["team_id"] == team_id]
        ce = csat_events[csat_events["team_id"] == team_id]

        rows.append(
            {
                "team_id": team_id,
                "work_type": work_type,
                "sla_adherence": sla_adherence(wi),
                "backlog_count": backlog_count(wi),
                "aged_backlog_72h": aged_backlog_count(wi),
                "csat_trailing_7d": csat_trailing_average(ce, days=7),
                "average_quality_score": average_quality_score(qe),
                "escalation_rate_per_1000": escalation_rate_per_1000(ee, wi),
                "rework_rate": rework_rate(wi),
                "fcr_proxy": fcr_proxy(wi),
                "work_item_count": len(wi),
                "escalation_count": len(ee),
            }
        )

    return pd.DataFrame(rows)
