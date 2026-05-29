"""Reusable Streamlit UI helpers for the Scale Regional Ops Command Center.

The visual language is adapted from the attached React reference package:
Aurora editorial dark canvas, translucent cards, pill navigation, mono eyebrow
labels, serif executive headings, and teal / amber / red risk states.
"""

from __future__ import annotations

from html import escape
from typing import Sequence

import streamlit as st


SCALE_ACCENT = "#B79DFF"
SCALE_ACCENT_DEEP = "#7C5CFC"
SCALE_GOOD = "#5EEAD4"
SCALE_WARN = "#FBBF77"
SCALE_BAD = "#F87171"
SCALE_BG = "#0A0A12"
SCALE_SURFACE = "rgba(255,255,255,0.035)"
SCALE_SURFACE_HI = "rgba(255,255,255,0.065)"
SCALE_BORDER = "rgba(255,255,255,0.10)"
SCALE_TEXT = "#F5F5F0"
SCALE_TEXT_DIM = "#B7B5AA"
SCALE_TEXT_FAINT = "#6E6C66"


def _safe(value: object, default: str = "n/a") -> str:
    if value is None:
        return default
    text = str(value)
    if text.strip().lower() in {"", "none", "nan", "n/a", "<na>"}:
        return default
    return escape(text)


def install_scale_theme() -> None:
    """Inject command-center styling once per page."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500;600&family=Instrument+Serif:ital@0;1&display=swap');

        :root {{
          --scale-bg: {SCALE_BG};
          --scale-surface: {SCALE_SURFACE};
          --scale-surface-hi: {SCALE_SURFACE_HI};
          --scale-border: {SCALE_BORDER};
          --scale-text: {SCALE_TEXT};
          --scale-text-dim: {SCALE_TEXT_DIM};
          --scale-text-faint: {SCALE_TEXT_FAINT};
          --scale-accent: {SCALE_ACCENT};
          --scale-accent-deep: {SCALE_ACCENT_DEEP};
          --scale-good: {SCALE_GOOD};
          --scale-warn: {SCALE_WARN};
          --scale-bad: {SCALE_BAD};
        }}

        .stApp {{
          background:
            radial-gradient(circle at 18% 0%, rgba(183,157,255,0.18), transparent 32%),
            radial-gradient(circle at 85% 12%, rgba(94,234,212,0.10), transparent 34%),
            linear-gradient(180deg, #0A0A12 0%, #10111A 48%, #08090F 100%);
          color: var(--scale-text);
        }}

        .block-container {{
          padding-top: 2.1rem;
          padding-bottom: 3.2rem;
          max-width: 1500px;
        }}

        html, body, [class*="css"] {{
          font-family: "Geist", "Geist Sans", ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }}

        h1, h2, h3 {{
          letter-spacing: -0.035em;
        }}

        .scale-hero {{
          border: 1px solid var(--scale-border);
          background:
            linear-gradient(135deg, rgba(183,157,255,0.13), rgba(94,234,212,0.045) 45%, rgba(255,255,255,0.025)),
            rgba(255,255,255,0.025);
          border-radius: 26px;
          padding: 30px 32px 28px;
          margin: 0 0 22px 0;
          box-shadow: 0 24px 80px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.05);
          backdrop-filter: blur(20px);
        }}

        .scale-eyebrow {{
          font-family: "Geist Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
          color: var(--scale-accent);
          text-transform: uppercase;
          letter-spacing: 0.18em;
          font-size: 0.72rem;
          margin-bottom: 0.65rem;
        }}

        .scale-title {{
          font-family: "Instrument Serif", "Source Serif Pro", Georgia, serif;
          font-size: clamp(2.2rem, 4.6vw, 4.8rem);
          line-height: 0.95;
          font-weight: 400;
          color: var(--scale-text);
          margin: 0;
          letter-spacing: -0.055em;
        }}

        .scale-lede {{
          color: var(--scale-text-dim);
          font-size: 1rem;
          line-height: 1.58;
          max-width: 900px;
          margin-top: 1rem;
        }}

        .scale-hero-grid {{
          display: grid;
          grid-template-columns: 1.1fr 1fr;
          gap: 18px;
          margin-top: 24px;
        }}

        .scale-info-card, .scale-card {{
          border: 1px solid var(--scale-border);
          border-radius: 18px;
          background: var(--scale-surface);
          padding: 18px 20px;
          box-shadow: inset 0 1px 0 rgba(255,255,255,0.035);
        }}

        .scale-info-card h4, .scale-card h4 {{
          margin: 0 0 8px 0;
          color: var(--scale-text);
          font-size: 0.94rem;
          font-weight: 600;
        }}

        .scale-info-card p, .scale-card p {{
          margin: 0;
          color: var(--scale-text-dim);
          line-height: 1.52;
          font-size: 0.92rem;
        }}

        .scale-chip-row {{
          display: flex;
          align-items: center;
          gap: 8px;
          flex-wrap: wrap;
          margin-top: 18px;
        }}

        .scale-chip {{
          display: inline-flex;
          align-items: center;
          gap: 7px;
          padding: 5px 11px;
          border-radius: 999px;
          border: 1px solid var(--scale-border);
          background: var(--scale-surface);
          color: var(--scale-text-dim);
          font-family: "Geist Mono", ui-monospace, monospace;
          font-size: 0.68rem;
          letter-spacing: 0.08em;
          text-transform: uppercase;
        }}

        .scale-dot {{
          width: 7px;
          height: 7px;
          border-radius: 999px;
          display: inline-block;
          box-shadow: 0 0 10px currentColor;
        }}

        .scale-section-head {{
          display: flex;
          align-items: flex-end;
          justify-content: space-between;
          gap: 20px;
          margin: 30px 0 16px 0;
        }}

        .scale-section-title {{
          font-family: "Instrument Serif", Georgia, serif;
          font-size: clamp(1.6rem, 2.4vw, 2.35rem);
          font-weight: 400;
          color: var(--scale-text);
          margin: 0;
          letter-spacing: -0.04em;
          line-height: 1.05;
        }}

        .scale-section-caption {{
          color: var(--scale-text-dim);
          line-height: 1.52;
          margin-top: 8px;
          max-width: 760px;
        }}

        .scale-metric-grid {{
          display: grid;
          grid-template-columns: repeat(5, minmax(0, 1fr));
          gap: 14px;
          margin: 14px 0;
        }}

        .scale-metric {{
          border: 1px solid var(--scale-border);
          background: var(--scale-surface);
          border-radius: 18px;
          padding: 16px 16px 15px;
          min-height: 112px;
          position: relative;
          overflow: hidden;
        }}

        .scale-metric::after {{
          content: "";
          position: absolute;
          inset: auto -40px -60px auto;
          width: 130px;
          height: 130px;
          background: radial-gradient(circle, rgba(183,157,255,0.13), transparent 62%);
        }}

        .scale-metric-label {{
          font-family: "Geist Mono", ui-monospace, monospace;
          font-size: 0.68rem;
          letter-spacing: 0.10em;
          text-transform: uppercase;
          color: var(--scale-text-faint);
          display: flex;
          align-items: center;
          gap: 7px;
        }}

        .scale-metric-value {{
          font-family: "Instrument Serif", Georgia, serif;
          color: var(--scale-text);
          font-size: 2rem;
          line-height: 1;
          margin-top: 10px;
          letter-spacing: -0.04em;
          font-variant-numeric: tabular-nums;
          position: relative;
          z-index: 1;
        }}

        .scale-metric-sub {{
          color: var(--scale-text-dim);
          font-size: 0.76rem;
          margin-top: 10px;
          line-height: 1.35;
          position: relative;
          z-index: 1;
        }}

        .scale-risk-card {{
          border: 1px solid var(--scale-border);
          background: var(--scale-surface);
          border-radius: 18px;
          padding: 18px 20px;
          margin: 12px 0;
        }}

        .scale-risk-card.high {{
          border-color: rgba(248,113,113,0.38);
          background: linear-gradient(135deg, rgba(248,113,113,0.10), rgba(255,255,255,0.025));
        }}

        .scale-risk-card.medium {{
          border-color: rgba(251,191,119,0.34);
          background: linear-gradient(135deg, rgba(251,191,119,0.10), rgba(255,255,255,0.025));
        }}

        .scale-risk-topline {{
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 14px;
          margin-bottom: 10px;
        }}

        .scale-risk-title {{
          color: var(--scale-text);
          font-size: 1.05rem;
          font-weight: 600;
        }}

        .scale-risk-meta {{
          color: var(--scale-text-faint);
          font-family: "Geist Mono", ui-monospace, monospace;
          font-size: 0.72rem;
          letter-spacing: 0.03em;
        }}

        .scale-risk-action {{
          color: var(--scale-accent);
          line-height: 1.5;
          margin-top: 10px;
        }}

        .scale-action-card {{
          border: 1px solid rgba(183,157,255,0.35);
          border-radius: 24px;
          background: linear-gradient(135deg, rgba(183,157,255,0.14), rgba(94,234,212,0.055) 55%, rgba(255,255,255,0.03));
          padding: 24px;
          margin: 16px 0;
          box-shadow: 0 22px 70px rgba(0,0,0,0.28);
        }}

        .scale-action-grid {{
          display: grid;
          grid-template-columns: repeat(3, minmax(0, 1fr));
          gap: 12px;
          margin-top: 14px;
        }}

        .scale-action-field {{
          border: 1px solid var(--scale-border);
          border-radius: 14px;
          background: rgba(255,255,255,0.025);
          padding: 13px 14px;
        }}

        .scale-field-label {{
          font-family: "Geist Mono", ui-monospace, monospace;
          color: var(--scale-text-faint);
          text-transform: uppercase;
          letter-spacing: 0.10em;
          font-size: 0.66rem;
          margin-bottom: 6px;
        }}

        .scale-field-value {{
          color: var(--scale-text);
          line-height: 1.45;
        }}

        .scale-empty {{
          border: 1px dashed var(--scale-border);
          background: rgba(255,255,255,0.025);
          color: var(--scale-text-dim);
          border-radius: 18px;
          padding: 20px;
          text-align: center;
        }}

        .scale-footer-note {{
          border: 1px solid var(--scale-border);
          border-radius: 999px;
          background: rgba(10,10,18,0.68);
          color: var(--scale-text-dim);
          padding: 9px 16px;
          display: inline-flex;
          gap: 10px;
          align-items: center;
          font-family: "Geist Mono", ui-monospace, monospace;
          font-size: 0.72rem;
          letter-spacing: 0.04em;
          margin-top: 20px;
        }}

        div[data-testid="stExpander"] details {{
          border: 1px solid var(--scale-border);
          border-radius: 18px;
          background: var(--scale-surface);
        }}

        div[data-testid="stMetric"] {{
          border: 1px solid var(--scale-border);
          border-radius: 16px;
          background: var(--scale-surface);
          padding: 12px 14px;
        }}

        div[data-testid="stMetricLabel"] p {{
          color: var(--scale-text-faint);
          font-family: "Geist Mono", ui-monospace, monospace;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          font-size: 0.68rem;
        }}

        div[data-testid="stMetricValue"] {{
          color: var(--scale-text);
          font-family: "Instrument Serif", Georgia, serif;
          letter-spacing: -0.04em;
        }}

        button[data-baseweb="tab"] {{
          border-radius: 999px !important;
          border: 1px solid var(--scale-border) !important;
          background: rgba(255,255,255,0.025) !important;
          margin-right: 6px !important;
          padding: 6px 14px !important;
        }}

        button[data-baseweb="tab"][aria-selected="true"] {{
          border-color: rgba(183,157,255,0.55) !important;
          background: rgba(183,157,255,0.18) !important;
        }}

        div[data-testid="stDataFrame"] {{
          border: 1px solid var(--scale-border);
          border-radius: 18px;
          overflow: hidden;
          background: var(--scale-surface);
        }}

        @media (max-width: 1200px) {{
          .scale-metric-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
          .scale-hero-grid {{ grid-template-columns: 1fr; }}
          .scale-action-grid {{ grid-template-columns: 1fr; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_module_hero(
    eyebrow: str,
    title: str,
    lede: str,
    answer: str,
    why: str,
    chips: Sequence[tuple[str, str]] | None = None,
) -> None:
    chip_html = ""
    for label, color in chips or []:
        chip_html += (
            '<span class="scale-chip">'
            f'<span class="scale-dot" style="color:{escape(color)}; background:{escape(color)}"></span>'
            f'{_safe(label)}'
            '</span>'
        )
    st.markdown(
        f"""
        <div class="scale-hero">
          <div class="scale-eyebrow">{_safe(eyebrow)}</div>
          <h1 class="scale-title">{_safe(title)}</h1>
          <div class="scale-lede">{_safe(lede)}</div>
          <div class="scale-chip-row">{chip_html}</div>
          <div class="scale-hero-grid">
            <div class="scale-info-card">
              <h4>What this module answers</h4>
              <p>{_safe(answer)}</p>
            </div>
            <div class="scale-info-card">
              <h4>Why it matters</h4>
              <p>{_safe(why)}</p>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(eyebrow: str, title: str, caption: str | None = None) -> None:
    caption_html = f'<div class="scale-section-caption">{_safe(caption)}</div>' if caption else ""
    st.markdown(
        f"""
        <div class="scale-section-head">
          <div>
            <div class="scale-eyebrow">{_safe(eyebrow)}</div>
            <h2 class="scale-section-title">{_safe(title)}</h2>
            {caption_html}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(message: str) -> None:
    st.markdown(f'<div class="scale-empty">{_safe(message)}</div>', unsafe_allow_html=True)


def render_pill_row(items: Sequence[tuple[str, str]]) -> None:
    html = '<div class="scale-chip-row">'
    for label, color in items:
        html += (
            '<span class="scale-chip">'
            f'<span class="scale-dot" style="color:{escape(color)}; background:{escape(color)}"></span>'
            f'{_safe(label)}'
            '</span>'
        )
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_metric_grid(metrics: Sequence[dict[str, object]]) -> None:
    html = '<div class="scale-metric-grid">'
    for metric in metrics:
        color = escape(str(metric.get("color", SCALE_ACCENT)))
        html += f"""
          <div class="scale-metric">
            <div class="scale-metric-label">
              <span class="scale-dot" style="color:{color}; background:{color}"></span>
              {_safe(metric.get('label'))}
            </div>
            <div class="scale-metric-value">{_safe(metric.get('value'))}</div>
            <div class="scale-metric-sub">{_safe(metric.get('sub', ''))}</div>
          </div>
        """
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def risk_color(level: object) -> str:
    text = str(level or "").lower()
    if "high" in text or "breach" in text or "risk" in text and "low" not in text and "medium" not in text:
        return SCALE_BAD
    if "medium" in text or "watch" in text or "recovery" in text:
        return SCALE_WARN
    return SCALE_GOOD


def risk_class(level: object) -> str:
    text = str(level or "").lower()
    if "high" in text or "breach" in text:
        return "high"
    if "medium" in text or "watch" in text or "recovery" in text:
        return "medium"
    return "low"


def render_priority_card(
    title: object,
    risk_level: object,
    meta: object,
    action: object,
    evidence: object | None = None,
) -> None:
    color = risk_color(risk_level)
    css_class = risk_class(risk_level)
    evidence_html = f'<p>{_safe(evidence)}</p>' if evidence else ""
    st.markdown(
        f"""
        <div class="scale-risk-card {css_class}">
          <div class="scale-risk-topline">
            <div class="scale-risk-title">{_safe(title)}</div>
            <span class="scale-chip"><span class="scale-dot" style="color:{color}; background:{color}"></span>{_safe(risk_level)}</span>
          </div>
          <div class="scale-risk-meta">{_safe(meta)}</div>
          {evidence_html}
          <div class="scale-risk-action"><span class="scale-field-label">Recommended action</span><br>{_safe(action)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_operating_principle() -> None:
    st.markdown(
        f"""
        <div class="scale-footer-note">
          <span class="scale-dot" style="color:{SCALE_GOOD}; background:{SCALE_GOOD}"></span>
          <span>Synthetic data only · deterministic rules · explainable scoring · not worker surveillance</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_action_card(card: dict[str, object]) -> None:
    fields = [
        ("Signal summary", card.get("capacity_signal_summary")),
        ("Evidence", card.get("evidence")),
        ("Likely driver", card.get("likely_driver")),
        ("Recommended action", card.get("recommended_staffing_or_routing_action")),
        ("Owner", card.get("owner_suggestion")),
        ("Metric to monitor", card.get("metric_to_monitor")),
        ("Decision needed", card.get("decision_needed")),
        ("Follow-up date", card.get("follow_up_date")),
    ]
    fields_html = ""
    for label, value in fields:
        fields_html += f"""
          <div class="scale-action-field">
            <div class="scale-field-label">{_safe(label)}</div>
            <div class="scale-field-value">{_safe(value)}</div>
          </div>
        """

    color = risk_color(card.get("risk_level"))
    st.markdown(
        f"""
        <div class="scale-action-card">
          <div class="scale-risk-topline">
            <div>
              <div class="scale-eyebrow">Capacity action card</div>
              <h2 class="scale-section-title">{_safe(card.get('card_type'))} · {_safe(card.get('subject_id'))}</h2>
            </div>
            <span class="scale-chip"><span class="scale-dot" style="color:{color}; background:{color}"></span>{_safe(card.get('risk_level'))}</span>
          </div>
          <div class="scale-action-grid">{fields_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- Second-pass command-center polish ---
def install_command_center_polish() -> None:
    """Global UI refinements layered on top of the original Aurora package."""
    import streamlit as st

    st.markdown(
        """
        <style>
        /* App frame */
        .stApp {
            overflow-x: hidden;
        }

        .main .block-container {
            max-width: 1180px;
            padding-top: 2rem;
            padding-left: 2rem;
            padding-right: 2rem;
            padding-bottom: 4rem;
        }

        @media (max-width: 900px) {
            .main .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
        }

        /* Sidebar brand */
        .ops-sidebar-brand {
            border: 1px solid rgba(255,255,255,0.12);
            background:
                radial-gradient(circle at 20% 0%, rgba(0, 220, 190, 0.18), transparent 44%),
                rgba(255,255,255,0.045);
            border-radius: 18px;
            padding: 14px 14px 13px 14px;
            margin: 0 0 18px 0;
        }

        .ops-sidebar-brand-title {
            font-weight: 750;
            font-size: 0.98rem;
            letter-spacing: -0.01em;
            color: #f4f7fb;
            margin-bottom: 3px;
        }

        .ops-sidebar-brand-subtitle {
            font-size: 0.74rem;
            color: rgba(230,237,246,0.62);
            line-height: 1.35;
        }

        /* Streamlit sidebar nav polish */
        section[data-testid="stSidebar"] {
            border-right: 1px solid rgba(255,255,255,0.10);
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
            padding-top: 0.4rem;
        }

        section[data-testid="stSidebar"] a {
            border-radius: 999px !important;
            margin: 4px 0 !important;
            min-height: 38px;
            transition: all 140ms ease;
        }

        section[data-testid="stSidebar"] a:hover {
            background: rgba(255,255,255,0.075) !important;
        }

        section[data-testid="stSidebar"] [aria-current="page"] {
            background: rgba(0, 220, 190, 0.16) !important;
            border: 1px solid rgba(0, 220, 190, 0.32) !important;
        }

        /* Typography */
        h1, h2, h3 {
            letter-spacing: -0.035em;
        }

        h1 {
            font-size: clamp(2rem, 4vw, 4.2rem) !important;
            line-height: 0.98 !important;
        }

        h2 {
            font-size: clamp(1.45rem, 2.4vw, 2.35rem) !important;
            margin-top: 2.2rem !important;
        }

        h3 {
            font-size: clamp(1.1rem, 1.7vw, 1.45rem) !important;
            margin-top: 1.4rem !important;
        }

        p, li {
            line-height: 1.55;
        }

        /* Metric cards */
        div[data-testid="stMetric"] {
            min-height: 112px;
            border-radius: 18px;
            padding: 15px 16px 14px 16px;
            overflow: hidden;
        }

        div[data-testid="stMetricLabel"] {
            min-height: 34px;
        }

        div[data-testid="stMetricLabel"] p {
            white-space: normal !important;
            overflow-wrap: anywhere;
            line-height: 1.2;
            font-size: 0.78rem;
            opacity: 0.76;
        }

        div[data-testid="stMetricValue"] {
            white-space: normal !important;
            overflow-wrap: anywhere;
            line-height: 1.05;
            font-size: clamp(1.4rem, 2.5vw, 2.35rem) !important;
            letter-spacing: -0.04em;
        }

        div[data-testid="stMetricDelta"] {
            font-size: 0.76rem;
        }

        /* Dataframes */
        div[data-testid="stDataFrame"] {
            border-radius: 18px;
            border: 1px solid rgba(255,255,255,0.12);
            overflow: hidden;
            box-shadow: 0 18px 48px rgba(0,0,0,0.18);
            margin-top: 0.55rem;
            margin-bottom: 1.6rem;
        }

        div[data-testid="stDataFrame"] div[role="grid"] {
            font-size: 0.86rem;
        }

        /* Charts */
        div[data-testid="stPlotlyChart"] {
            border-radius: 18px;
            border: 1px solid rgba(255,255,255,0.10);
            background: rgba(255,255,255,0.025);
            padding: 8px;
            margin-bottom: 1.3rem;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.10);
            padding-bottom: 8px;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 999px;
            padding: 8px 16px;
            background: rgba(255,255,255,0.045);
            border: 1px solid rgba(255,255,255,0.10);
        }

        .stTabs [aria-selected="true"] {
            background: rgba(0, 220, 190, 0.16) !important;
            border-color: rgba(0, 220, 190, 0.38) !important;
        }

        /* Expanders */
        details[data-testid="stExpander"] {
            border-radius: 18px !important;
            border: 1px solid rgba(255,255,255,0.11) !important;
            background: rgba(255,255,255,0.035) !important;
            margin-bottom: 1rem;
        }

        details[data-testid="stExpander"] summary {
            font-weight: 650;
        }

        /* Inputs */
        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div {
            border-radius: 14px !important;
            background: rgba(255,255,255,0.055) !important;
            border-color: rgba(255,255,255,0.12) !important;
        }

        /* Buttons */
        .stButton button,
        .stDownloadButton button {
            border-radius: 999px !important;
            border: 1px solid rgba(0, 220, 190, 0.32) !important;
            background: rgba(0, 220, 190, 0.11) !important;
            color: #f5fbff !important;
            padding: 0.55rem 1.1rem !important;
            font-weight: 680 !important;
        }

        .stButton button:hover,
        .stDownloadButton button:hover {
            border-color: rgba(0, 220, 190, 0.65) !important;
            background: rgba(0, 220, 190, 0.18) !important;
        }

        /* Info/warning/success callouts */
        div[data-testid="stAlert"] {
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.11);
        }

        /* Remove excessive top whitespace in pages */
        div.block-container > div:first-child {
            margin-top: 0 !important;
        }

        /* Better horizontal behavior on small screens */
        @media (max-width: 760px) {
            div[data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
            }

            div[data-testid="stMetric"] {
                min-height: 96px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_brand() -> None:
    import streamlit as st

    st.sidebar.markdown(
        """
        <div class="ops-sidebar-brand">
            <div class="ops-sidebar-brand-title">Scale Ops Command Center</div>
            <div class="ops-sidebar-brand-subtitle">
                Synthetic-data executive demo · deterministic rules · no paid APIs
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --- Executive polish helpers: pass 3 ---
def compact_label(value: object, max_chars: int = 28) -> str:
    """Shorten long operational labels for KPI cards while preserving table detail."""
    if value is None:
        return "n/a"

    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "n/a"}:
        return "n/a"

    replacements = {
        "code_review": "Code",
        "audio_evaluation": "Audio",
        "image_annotation": "Image",
        "content_moderation": "Content",
        "data_labeling": "Labeling",
        "High quality risk": "High risk",
        "Medium quality risk": "Watch",
        "Low quality risk": "Stable",
        "High capacity risk": "High risk",
        "Medium capacity risk": "Watch",
        "Low capacity risk": "Stable",
        "Low gold task pass rate": "Gold-task risk",
        "Reviewer override spike": "Override risk",
        "Low peer agreement": "Agreement risk",
        "High rework rate": "Rework risk",
        "Aged backlog": "Aged backlog",
        "SLA at risk": "SLA risk",
    }

    if text in replacements:
        return replacements[text]

    lowered = text.lower()
    for old, new in replacements.items():
        if old.lower() in lowered:
            return new

    if len(text) <= max_chars:
        return text

    return text[: max_chars - 1].rstrip() + "…"


def render_demo_caption(text: str) -> None:
    """Render a concise interview-demo talk track below the page hero."""
    import html
    import streamlit as st

    st.markdown(
        f"""
        <div style="
            margin: -0.35rem 0 1.15rem 0;
            padding: 0.85rem 1rem;
            border-radius: 999px;
            border: 1px solid rgba(255,255,255,0.12);
            background: rgba(255,255,255,0.045);
            color: rgba(238,244,250,0.82);
            font-size: 0.92rem;
            line-height: 1.35;
        ">
            <strong style="color: rgba(255,255,255,0.92);">Demo line:</strong>
            {html.escape(text)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_decision_strip(
    signal: str,
    driver: str,
    decision: str,
    monitor: str,
) -> None:
    """Render four executive decision cards at the top of a page."""
    import html
    import streamlit as st

    cards = [
        ("Signal", signal),
        ("Driver", driver),
        ("Decision", decision),
        ("Monitor", monitor),
    ]

    st.markdown(
        """
        <style>
        .decision-strip {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.85rem;
            margin: 0.6rem 0 1.35rem 0;
        }
        .decision-card {
            min-height: 112px;
            border: 1px solid rgba(255,255,255,0.12);
            background:
                linear-gradient(135deg, rgba(255,255,255,0.075), rgba(255,255,255,0.032));
            border-radius: 18px;
            padding: 0.95rem 1rem;
            box-shadow: 0 18px 40px rgba(0,0,0,0.18);
        }
        .decision-label {
            color: rgba(160, 247, 235, 0.95);
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.13em;
            font-weight: 750;
            margin-bottom: 0.45rem;
        }
        .decision-value {
            color: rgba(247,250,255,0.96);
            font-size: 1rem;
            line-height: 1.28;
            font-weight: 620;
            overflow-wrap: anywhere;
        }
        @media (max-width: 1050px) {
            .decision-strip {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }
        @media (max-width: 640px) {
            .decision-strip {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    html_cards = "".join(
        f"""
        <div class="decision-card">
            <div class="decision-label">{html.escape(label)}</div>
            <div class="decision-value">{html.escape(str(value))}</div>
        </div>
        """
        for label, value in cards
    )

    st.markdown(
        f'<div class="decision-strip">{html_cards}</div>',
        unsafe_allow_html=True,
    )


def render_data_table(df, columns=None, height: int = 420):
    """Consistent dataframe rendering without unsafe regex edits."""
    import streamlit as st

    if df is None or df.empty:
        st.info("No records match the current filters.")
        return

    display_df = df.copy()
    if columns:
        available = [column for column in columns if column in display_df.columns]
        if available:
            display_df = display_df[available]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=height,
    )


# --- Safe override for executive decision cards ---
def render_decision_strip(
    signal: str,
    driver: str,
    decision: str,
    monitor: str,
) -> None:
    """Render executive decision cards in a stable 2x2 Streamlit layout.

    This intentionally avoids a pure HTML grid because long executive text can
    break inside Streamlit's markdown/CSS stack.
    """
    import html
    import streamlit as st

    st.markdown(
        """
        <style>
        .exec-decision-card {
            min-height: 138px;
            border: 1px solid rgba(255,255,255,0.13);
            background:
                radial-gradient(circle at top left, rgba(0, 220, 190, 0.12), transparent 46%),
                linear-gradient(135deg, rgba(255,255,255,0.075), rgba(255,255,255,0.035));
            border-radius: 20px;
            padding: 1rem 1.05rem;
            margin-bottom: 0.8rem;
            box-shadow: 0 18px 42px rgba(0,0,0,0.18);
        }

        .exec-decision-label {
            color: rgba(144, 245, 231, 0.96);
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.14em;
            font-weight: 800;
            margin-bottom: 0.45rem;
        }

        .exec-decision-value {
            color: rgba(247,250,255,0.95);
            font-size: 0.98rem;
            line-height: 1.42;
            font-weight: 560;
            overflow-wrap: anywhere;
        }

        @media (max-width: 780px) {
            .exec-decision-card {
                min-height: auto;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    def card(label: str, value: str) -> None:
        st.markdown(
            f"""
            <div class="exec-decision-card">
                <div class="exec-decision-label">{html.escape(label)}</div>
                <div class="exec-decision-value">{html.escape(value)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    top_left, top_right = st.columns(2, gap="medium")
    with top_left:
        card("Signal", signal)
    with top_right:
        card("Driver", driver)

    bottom_left, bottom_right = st.columns(2, gap="medium")
    with bottom_left:
        card("Decision", decision)
    with bottom_right:
        card("Monitor", monitor)


# --- Universal safe executive decision cards ---
def render_decision_strip(
    signal: str,
    driver: str,
    decision: str,
    monitor: str,
) -> None:
    """Stable 2x2 decision-card layout for all pages.

    Avoids fragile HTML grid behavior with long executive text.
    """
    import html
    import streamlit as st

    st.markdown(
        """
        <style>
        .exec-decision-card {
            min-height: 126px;
            border: 1px solid rgba(255,255,255,0.13);
            background:
                radial-gradient(circle at top left, rgba(0, 220, 190, 0.13), transparent 44%),
                linear-gradient(135deg, rgba(255,255,255,0.075), rgba(255,255,255,0.033));
            border-radius: 20px;
            padding: 1rem 1.05rem;
            margin-bottom: 0.82rem;
            box-shadow: 0 18px 42px rgba(0,0,0,0.18);
        }

        .exec-decision-label {
            color: rgba(144, 245, 231, 0.96);
            font-size: 0.70rem;
            text-transform: uppercase;
            letter-spacing: 0.14em;
            font-weight: 800;
            margin-bottom: 0.45rem;
        }

        .exec-decision-value {
            color: rgba(247,250,255,0.95);
            font-size: 0.95rem;
            line-height: 1.38;
            font-weight: 560;
            overflow-wrap: anywhere;
            word-break: normal;
        }

        @media (max-width: 780px) {
            .exec-decision-card {
                min-height: auto;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    def card(label: str, value: str) -> None:
        st.markdown(
            f"""
            <div class="exec-decision-card">
                <div class="exec-decision-label">{html.escape(label)}</div>
                <div class="exec-decision-value">{html.escape(str(value))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    row1_col1, row1_col2 = st.columns(2, gap="medium")
    with row1_col1:
        card("Signal", signal)
    with row1_col2:
        card("Driver", driver)

    row2_col1, row2_col2 = st.columns(2, gap="medium")
    with row2_col1:
        card("Decision", decision)
    with row2_col2:
        card("Monitor", monitor)


# --- Safe overrides for Aurora metric and risk cards ---
def _compact_card_text(value: object, max_chars: int = 34) -> str:
    """Compact long values so Aurora cards do not visually break."""
    if value is None:
        return "n/a"

    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "n/a"}:
        return "n/a"

    replacements = {
        "code_review": "Code",
        "audio_evaluation": "Audio",
        "image_annotation": "Image",
        "content_moderation": "Content",
        "data_labeling": "Labeling",
        "High capacity risk": "High risk",
        "Medium capacity risk": "Watch",
        "Low capacity risk": "Stable",
        "SLA recovery needed": "Recovery",
        "SLA at risk": "At risk",
        "Within expected range": "Stable",
        "Review staffing, routing, or backlog burn-down plan": "Review staffing plan",
        "Add temporary coverage or rebalance queue ownership": "Add / rebalance coverage",
        "Review capacity": "Review capacity",
        "Review capacity allocation": "Review allocation",
    }

    if text in replacements:
        return replacements[text]

    lowered = text.lower()
    for old, new in replacements.items():
        if old.lower() in lowered:
            return new

    if len(text) <= max_chars:
        return text

    return text[: max_chars - 1].rstrip() + "…"


def render_metric_grid(metrics) -> None:
    """Stable Aurora metric grid.

    Replaces the original pure HTML grid, which can break when metric values
    contain long work-type names or recommended actions.
    """
    import html
    import streamlit as st

    st.markdown(
        """
        <style>
        .safe-scale-metric {
            min-height: 132px;
            border: 1px solid rgba(255,255,255,0.13);
            background:
                radial-gradient(circle at top left, rgba(0, 220, 190, 0.10), transparent 45%),
                linear-gradient(135deg, rgba(255,255,255,0.072), rgba(255,255,255,0.032));
            border-radius: 20px;
            padding: 0.95rem 1rem;
            margin-bottom: 0.85rem;
            overflow: hidden;
            box-shadow: 0 18px 42px rgba(0,0,0,0.16);
        }

        .safe-scale-metric-label {
            display: flex;
            align-items: center;
            gap: 0.42rem;
            min-height: 28px;
            color: rgba(230,237,246,0.74);
            font-size: 0.72rem;
            line-height: 1.18;
            text-transform: uppercase;
            letter-spacing: 0.10em;
            font-weight: 760;
            margin-bottom: 0.45rem;
        }

        .safe-scale-dot {
            width: 8px;
            height: 8px;
            min-width: 8px;
            border-radius: 999px;
            display: inline-block;
            box-shadow: 0 0 18px currentColor;
        }

        .safe-scale-metric-value {
            color: rgba(248,251,255,0.96);
            font-size: clamp(1.15rem, 2vw, 1.7rem);
            line-height: 1.08;
            font-weight: 760;
            letter-spacing: -0.035em;
            overflow-wrap: anywhere;
            word-break: normal;
            margin-bottom: 0.4rem;
        }

        .safe-scale-metric-sub {
            color: rgba(210,220,235,0.62);
            font-size: 0.78rem;
            line-height: 1.28;
            overflow-wrap: anywhere;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    metric_list = list(metrics or [])
    if not metric_list:
        return

    # Four columns is a better balance than the original dense 5-column HTML grid.
    for start in range(0, len(metric_list), 4):
        row = metric_list[start : start + 4]
        cols = st.columns(len(row), gap="medium")

        for col, metric in zip(cols, row):
            label = _compact_card_text(metric.get("label"), 30)
            value = _compact_card_text(metric.get("value"), 24)
            sub = _compact_card_text(metric.get("sub", ""), 42)
            color = str(metric.get("color", "#62f4df"))

            with col:
                st.markdown(
                    f"""
                    <div class="safe-scale-metric">
                        <div class="safe-scale-metric-label">
                            <span class="safe-scale-dot" style="color:{html.escape(color)}; background:{html.escape(color)}"></span>
                            {html.escape(label)}
                        </div>
                        <div class="safe-scale-metric-value" title="{html.escape(str(metric.get("value", "")))}">
                            {html.escape(value)}
                        </div>
                        <div class="safe-scale-metric-sub">{html.escape(sub)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def render_priority_card(
    title: object,
    risk_level: object,
    meta: object,
    action: object,
    evidence: object | None = None,
) -> None:
    """Stable risk/action card.

    Keeps Aurora styling but prevents the original risk-card HTML from breaking
    below the Capacity SLA overview strip.
    """
    import html
    import streamlit as st

    level = _compact_card_text(risk_level, 24)
    title_text = _compact_card_text(title, 42)
    meta_text = _compact_card_text(meta, 90)
    evidence_text = _compact_card_text(evidence, 110) if evidence else ""
    action_text = _compact_card_text(action, 90)

    color = "#f36f6f"
    level_lower = str(risk_level or "").lower()
    if "medium" in level_lower or "watch" in level_lower or "recovery" in level_lower:
        color = "#f4c96b"
    elif "low" in level_lower or "stable" in level_lower:
        color = "#62f4df"

    evidence_html = (
        f'<div class="safe-risk-evidence">{html.escape(evidence_text)}</div>'
        if evidence_text
        else ""
    )

    st.markdown(
        f"""
        <div style="
            border: 1px solid rgba(255,255,255,0.13);
            border-left: 4px solid {html.escape(color)};
            background: linear-gradient(135deg, rgba(255,255,255,0.072), rgba(255,255,255,0.032));
            border-radius: 20px;
            padding: 1rem 1.1rem;
            margin: 0.75rem 0;
            box-shadow: 0 18px 42px rgba(0,0,0,0.16);
            overflow: hidden;
        ">
            <div style="
                display: flex;
                align-items: flex-start;
                justify-content: space-between;
                gap: 0.8rem;
                margin-bottom: 0.45rem;
            ">
                <div style="
                    color: rgba(248,251,255,0.96);
                    font-size: 1.05rem;
                    font-weight: 760;
                    line-height: 1.25;
                    overflow-wrap: anywhere;
                ">{html.escape(title_text)}</div>

                <div style="
                    white-space: nowrap;
                    border: 1px solid rgba(255,255,255,0.14);
                    background: rgba(255,255,255,0.06);
                    border-radius: 999px;
                    padding: 0.25rem 0.55rem;
                    color: rgba(248,251,255,0.92);
                    font-size: 0.72rem;
                    font-weight: 720;
                ">{html.escape(level)}</div>
            </div>

            <div style="
                color: rgba(210,220,235,0.65);
                font-size: 0.82rem;
                line-height: 1.35;
                margin-bottom: 0.55rem;
                overflow-wrap: anywhere;
            ">{html.escape(meta_text)}</div>

            {evidence_html}

            <div style="
                border-top: 1px solid rgba(255,255,255,0.10);
                padding-top: 0.65rem;
                color: rgba(248,251,255,0.92);
                font-size: 0.9rem;
                line-height: 1.38;
                overflow-wrap: anywhere;
            ">
                <span style="
                    color: rgba(144,245,231,0.95);
                    text-transform: uppercase;
                    letter-spacing: 0.12em;
                    font-size: 0.68rem;
                    font-weight: 800;
                ">Recommended action</span><br>
                {html.escape(action_text)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
