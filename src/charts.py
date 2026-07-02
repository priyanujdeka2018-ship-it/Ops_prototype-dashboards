"""
Plotly chart builders (legacy dashboard helpers; not used by the pipeline).
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px


STATUS_ORDER = {
    "green": 3,
    "amber": 2,
    "red": 1,
    "unknown": 0,
}


def health_heatmap(health_df: pd.DataFrame):
    """
    Build a health heatmap.

    Expected columns:
    - work_type
    - metric
    - status
    """
    df = health_df.copy()
    df["status_score"] = df["status"].map(STATUS_ORDER).fillna(0)

    fig = px.imshow(
        df.pivot(index="work_type", columns="metric", values="status_score"),
        text_auto=False,
        aspect="auto",
        color_continuous_scale=[
            [0.0, "#808080"],
            [0.33, "#D9534F"],
            [0.66, "#F0AD4E"],
            [1.0, "#2E8B57"],
        ],
        labels={"color": "Health"},
    )

    fig.update_layout(
        title="Regional Health Heatmap",
        xaxis_title="Metric",
        yaxis_title="Work Type",
        height=420,
    )

    return fig


def bar_chart(df: pd.DataFrame, x: str, y: str, title: str):
    fig = px.bar(df, x=x, y=y, title=title)
    fig.update_layout(height=380)
    return fig


def line_chart(df: pd.DataFrame, x: str, y: str, title: str):
    fig = px.line(df, x=x, y=y, markers=True, title=title)
    fig.update_layout(height=380)
    return fig


def stacked_bar_chart(df: pd.DataFrame, x: str, y: str, color: str, title: str):
    fig = px.bar(df, x=x, y=y, color=color, title=title)
    fig.update_layout(height=380)
    return fig
