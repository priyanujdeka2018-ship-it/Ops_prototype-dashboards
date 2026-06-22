// Shared data + derivation helpers for the Scale Ops Command Center.
// Pure functions; safe to import from any route or atom.
import React from "react";

// ─── Label dictionaries ──────────────────────────────────────────────────────

export const ROOT_CAUSE_LABELS = {
  policy_ambiguity: "Policy ambiguity",
  reviewer_misalignment: "Reviewer misalignment",
  quality_defect: "Quality defect",
  tooling_issue: "Tooling issue",
  customer_requirement_change: "Customer requirement change",
  sla_miss: "SLA miss",
  workflow_handoff_gap: "Workflow handoff gap",
  capacity_shortfall: "Capacity shortfall",
};

export const WORK_TYPE_LABELS = {
  image_annotation: "Image annotation",
  rlhf_evaluation: "RLHF evaluation",
  code_review: "Code review",
  audio_evaluation: "Audio evaluation",
  expert_review: "Expert review",
};

export const ROOT_CAUSE_FIX = {
  policy_ambiguity: { fix: "SOP rewrite + calibration huddle", owner: "Policy Ops lead + frontline manager", metric: "Reviewer agreement rate; repeat escalations" },
  reviewer_misalignment: { fix: "Reviewer calibration + QA sampling boost", owner: "Quality lead + reviewer manager", metric: "Disagreement rate; QA defect rate" },
  quality_defect: { fix: "Gold task refresh + QA containment", owner: "QA lead", metric: "Quality score; gold task pass rate" },
  tooling_issue: { fix: "Tooling change + workaround comm", owner: "Tooling / product ops", metric: "Tooling escalations; outage incidents" },
  customer_requirement_change: { fix: "Customer instruction propagation", owner: "Customer ops lead + training", metric: "Instruction-change escalations; CSAT" },
  sla_miss: { fix: "Staffing / capacity correction", owner: "Regional ops manager", metric: "SLA adherence; aged backlog" },
  workflow_handoff_gap: { fix: "Queue routing + named handoff owner", owner: "Workflow ops lead", metric: "Handoff delay; reopen rate" },
  capacity_shortfall: { fix: "Staffing rebalance / surge coverage", owner: "Workforce planning lead", metric: "Backlog age; utilization" },
};

export const ROOT_CAUSE_DECISION = {
  policy_ambiguity: "Approve SOP clarification + require examples for ambiguous cases",
  reviewer_misalignment: "Calibration: one team or regional reviewers?",
  quality_defect: "Approve gold-task refresh + temporary QA sampling boost",
  tooling_issue: "Prioritize fix or approve interim operational workaround",
  customer_requirement_change: "Confirm source of truth, audit propagation",
  sla_miss: "Approve temp staffing rebalance / surge coverage",
  workflow_handoff_gap: "Clarify handoff ownership, update routing rules",
  capacity_shortfall: "Approve capacity rebalance / cross-trained backup",
};

export const SEVERITY_LABELS = { sev1: "Sev 1", sev2: "Sev 2", sev3: "Sev 3", sev4: "Sev 4" };

export const STATUS_COLORS = { good: "#10B981", warn: "#F59E0B", bad: "#EF4444", info: "#22D3EE", muted: "#64748B" };

export const THEME_PRESETS = {
  teal:   { id: "teal",   label: "Teal",   accent: "#5EEAD4", accentDeep: "#0EB8A0", inkOnAccent: "#0A1A18" },
  violet: { id: "violet", label: "Violet", accent: "#B79DFF", accentDeep: "#7C5CFC", inkOnAccent: "#1A0033" },
  rose:   { id: "rose",   label: "Rose",   accent: "#FF8FB1", accentDeep: "#F43F8C", inkOnAccent: "#2A0312" },
  sky:    { id: "sky",    label: "Sky",    accent: "#7DD3FC", accentDeep: "#0284C7", inkOnAccent: "#021627" },
  amber:  { id: "amber",  label: "Amber",  accent: "#FBBF77", accentDeep: "#EA8A1E", inkOnAccent: "#2A1804" },
};

export const DENSITY_PRESETS = {
  compact: { id: "compact", label: "Compact", padX: 32, padY: 24, gap: 12, sectionGap: 24, fontBody: 13, rowGap: 10 },
  cozy:    { id: "cozy",    label: "Cozy",    padX: 48, padY: 36, gap: 18, sectionGap: 36, fontBody: 14, rowGap: 14 },
  spacious:{ id: "spacious",label: "Spacious",padX: 64, padY: 52, gap: 24, sectionGap: 56, fontBody: 15, rowGap: 18 },
};

export const AUDIENCE_LENS = [
  { id: "regional_ops_lead", title: "Regional Ops Lead", blurb: "Owns SLA, backlog, escalations across a region.", opens: ["/health","/capacity"], priorityKpis: ["sla_adherence","backlog","aged_backlog_72h"], ai_leverage: "AI scans 250+ escalation summaries each morning, surfaces recurring patterns, drafts the weekly briefing." },
  { id: "quality_lead", title: "Quality Lead", blurb: "Defends quality scores, runs calibration, owns rework.", opens: ["/workforce","/patterns"], priorityKpis: ["avg_quality","rework_rate"], ai_leverage: "Embeddings cluster escalations by how teams describe breakdowns, not just by label." },
  { id: "workforce_planner", title: "Workforce Planner", blurb: "Allocates capacity across work types and shifts.", opens: ["/capacity","/workforce"], priorityKpis: ["backlog","escalation_rate_per_1000"], ai_leverage: "Forecasts backlog 7-14 days out from inflow + throughput + complexity." },
  { id: "customer_ops_lead", title: "Customer Ops Lead", blurb: "Owns CSAT, escalation experience, customer comms.", opens: ["/patterns","/clusters"], priorityKpis: ["csat_7d","fcr_proxy"], ai_leverage: "Semantic clustering catches friction across customers before a 4th account is at risk." },
  { id: "engineering_manager", title: "Engineering Manager", blurb: "Wants production architecture & failure modes.", opens: ["/about"], priorityKpis: [], ai_leverage: "All scoring is deterministic and explainable; LLM is scoped to summarization + clustering, not decisions." },
];

export function classifyMetric(metric, value) {
  switch (metric) {
    case "sla":             return value >= 95 ? "good" : value >= 90 ? "warn" : "bad";
    case "csat":            return value >= 4.4 ? "good" : value >= 4.2 ? "warn" : "bad";
    case "quality":         return value >= 90 ? "good" : value >= 85 ? "warn" : "bad";
    case "escalation_rate": return value <= 8 ? "good" : value <= 15 ? "warn" : "bad";
    case "open":            return value <= 5 ? "good" : value <= 15 ? "warn" : "bad";
    case "sev1":            return value === 0 ? "good" : value <= 2 ? "warn" : "bad";
    case "rework":          return value <= 5 ? "good" : value <= 8 ? "warn" : "bad";
    case "utilization":     return value <= 86 ? "good" : value <= 92 ? "warn" : "bad";
    default:                return "muted";
  }
}

export const fmt = {
  pct:  (v) => `${Number(v).toFixed(1)}%`,
  num:  (v) => Number(v).toLocaleString("en-US"),
  dec:  (v, d = 1) => Number(v).toFixed(d),
  short:(v) => (v >= 1000 ? (v / 1000).toFixed(1) + "k" : String(Math.round(v))),
  date: (iso) => { const d = new Date(iso); return d.toLocaleDateString("en-US", { month: "short", day: "numeric" }); },
  rel:  (days) => (days === 0 ? "today" : days === 1 ? "1d ago" : days < 30 ? `${days}d ago` : `${Math.floor(days / 7)}w ago`),
};

export function useScaleData(scenario = "current", vintage) {
  const [data, setData] = React.useState(null);
  const [err, setErr] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [reloadKey, setReloadKey] = React.useState(0);
  React.useEffect(() => {
    let cancelled = false;
    setLoading(true); setErr(null);
    // A vintage (pre-baked snapshot) overrides the scenario fetch target.
    const label = vintage || scenario;
    const bust = reloadKey ? `?r=${reloadKey}` : "";  // bypass cache after a rebuild
    fetch(`/data/data-${label}.json${bust}`)
      .then((r) => (r.ok ? r.json() : fetch(`/data/data.json${bust}`).then((f) => f.json())))
      .then((d) => { if (!cancelled) { setData(d); setLoading(false); } })
      .catch((e) => { if (!cancelled) { setErr(String(e)); setLoading(false); } });
    return () => { cancelled = true; };
  }, [scenario, vintage, reloadKey]);
  const meta = data
    ? { generated_at: data.generated_at, row_counts: data.row_counts, pipeline_version: data.pipeline_version }
    : null;
  const refresh = React.useCallback(() => setReloadKey((k) => k + 1), []);
  return { data, err, loading, scenario, vintage, meta, refresh };
}

export function Sparkline({ values, color = "currentColor", width = 80, height = 24, fill = false, strokeWidth = 1.5 }) {
  if (!values || values.length < 2) return null;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const stepX = width / (values.length - 1);
  const points = values.map((v, i) => [i * stepX, height - ((v - min) / range) * (height - 4) - 2]);
  const path = points.map((p, i) => (i === 0 ? `M${p[0].toFixed(1)},${p[1].toFixed(1)}` : `L${p[0].toFixed(1)},${p[1].toFixed(1)}`)).join(" ");
  const areaPath = path + ` L${width},${height} L0,${height} Z`;
  return (
    <svg width={width} height={height} style={{ display: "block" }} viewBox={`0 0 ${width} ${height}`}>
      {fill && <path d={areaPath} fill={color} opacity={0.18} />}
      <path d={path} fill="none" stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
