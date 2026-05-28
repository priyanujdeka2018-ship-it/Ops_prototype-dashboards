"""
Business rules and threshold logic for the Scale Regional Ops Health Dashboard.

These rules are intentionally deterministic for the MVP. Later, they can be
augmented with statistical models or LLM-generated recommendations.
"""

from __future__ import annotations


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


def classify_higher_is_better(
    value: float,
    green_threshold: float,
    amber_threshold: float,
) -> str:
    """Classify a metric where higher values are better."""
    if value >= green_threshold:
        return "green"
    if value >= amber_threshold:
        return "amber"
    return "red"


def classify_lower_is_better(
    value: float,
    green_threshold: float,
    amber_threshold: float,
) -> str:
    """Classify a metric where lower values are better."""
    if value <= green_threshold:
        return "green"
    if value <= amber_threshold:
        return "amber"
    return "red"


def classify_metric(metric_name: str, value: float | None) -> str:
    """Return green, amber, red, or unknown for a metric."""
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

    if metric_name in {
        "rework_rate",
        "escalation_rate_per_1000",
        "aged_backlog_72h",
    }:
        return classify_lower_is_better(
            value=value,
            green_threshold=thresholds["green"],
            amber_threshold=thresholds["amber"],
        )

    raise ValueError(f"Unsupported metric classification: {metric_name}")
