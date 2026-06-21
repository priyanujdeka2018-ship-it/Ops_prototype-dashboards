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

export function useScaleData(scenario = "current") {
  const [data, setData] = React.useState(null);
  const [err, setErr] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  React.useEffect(() => {
    let cancelled = false;
    setLoading(true); setErr(null);
    const primary = `/data/data-${scenario}.json`;
    fetch(primary)
      .then((r) => (r.ok ? r.json() : fetch("/data/data.json").then((f) => f.json())))
      .then((d) => { if (!cancelled) { setData(d); setLoading(false); } })
      .catch((e) => { if (!cancelled) { setErr(String(e)); setLoading(false); } });
    return () => { cancelled = true; };
  }, [scenario]);
  return { data, err, loading, scenario };
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

// ─── Seeded RNG (stable per-key randomness) ─────────────────────────────────

function _hash(str) {
  let h = 1779033703 ^ str.length;
  for (let i = 0; i < str.length; i++) {
    h = Math.imul(h ^ str.charCodeAt(i), 3432918353);
    h = (h << 13) | (h >>> 19);
  }
  return () => {
    h = Math.imul(h ^ (h >>> 16), 2246822507);
    h = Math.imul(h ^ (h >>> 13), 3266489909);
    return ((h ^= h >>> 16) >>> 0) / 4294967296;
  };
}
export const rng  = (key) => _hash(String(key))();
export const rngR = (key, min, max) => min + rng(key) * (max - min);
const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
const round1 = (v) => Math.round(v * 10) / 10;

const SKILL_LEVELS = ["L1","L2","L3","Expert"];
const FIRST_NAMES = ["Aarav","Diya","Kabir","Anika","Vivaan","Sara","Reyansh","Myra","Arnav","Kiara","Ishaan","Aisha","Dev","Tara","Rohan","Zoya","Ved","Nia","Yash","Mira"];
const LAST_NAMES  = ["Sharma","Nair","Iyer","Khan","Reddy","Bose","Das","Mehta","Pillai","Verma","Gupta","Sinha","Rao","Menon","Kapoor"];
const Q_TARGET = 90;
const SLA_TARGET = 95;

// ─── Module C · Workforce Quality ───────────────────────────────────────────

export function deriveQuality(d) {
  if (!d?.teams) return null;
  const regionRework = d.kpis.rework_rate;

  const teams = d.teams.map((t) => {
    const r = (s) => rngR(t.team_id + s, 0, 1);
    const qualityGap = Math.max(0, Q_TARGET - t.quality);
    const escPer100 = t.contributors ? (t.escalations / t.contributors) * 100 : 0;

    const goldFailRate = clamp((Q_TARGET - t.quality) * 0.9 + r("g") * 6 + escPer100 * 0.15, 1.5, 38);
    const overrideRate = clamp((Q_TARGET - t.quality) * 0.7 + r("o") * 5 + 2, 1.5, 32);
    const peerAgree    = clamp(0.94 - qualityGap * 0.006 - r("p") * 0.05, 0.55, 0.98);
    const reworkRate   = clamp(regionRework * (0.7 + qualityGap * 0.06) + r("w") * 2, 1, 24);
    const lowTenureShare = clamp(r("lt") * 0.5 + (t.work_type === "expert_review" ? 0.12 : 0.18), 0.06, 0.62);

    const driftDelta = round1(rngR(t.team_id + "drift", -3.5, 4) - qualityGap * 0.12);
    const priorQuality = round1(clamp(t.quality - driftDelta, 60, 99));

    const drivers = [
      { k: "Quality gap to target", v: round1(qualityGap), w: qualityGap * 3.2, unit: "pt" },
      { k: "Gold-task fail rate",   v: round1(goldFailRate), w: goldFailRate * 0.7, unit: "%" },
      { k: "Reviewer override rate",v: round1(overrideRate), w: overrideRate * 0.55, unit: "%" },
      { k: "Rework rate",           v: round1(reworkRate), w: reworkRate * 1.1, unit: "%" },
      { k: "Sev1 escalations",      v: t.sev1_escalations, w: t.sev1_escalations * 4, unit: "" },
      { k: "Open escalations",      v: t.open_escalations, w: t.open_escalations * 0.6, unit: "" },
    ];
    if (driftDelta < 0) drivers.push({ k: "Quality drift (declining)", v: driftDelta, w: -driftDelta * 3, unit: "pt" });
    if (lowTenureShare > 0.35) drivers.push({ k: "Low-tenure share on complex work", v: Math.round(lowTenureShare * 100), w: (lowTenureShare - 0.35) * 30, unit: "%" });

    const riskScore = Math.round(drivers.reduce((s, dr) => s + dr.w, 0));
    const riskLevel = t.contributors < 14 ? "Insufficient" : riskScore >= 46 ? "High" : riskScore >= 24 ? "Medium" : "Low";

    return {
      team_id: t.team_id, city: t.city, manager: t.manager, shift: t.shift,
      work_type: t.work_type, contributors: t.contributors,
      quality: t.quality, priorQuality, driftDelta,
      sla: t.sla, csat: t.csat,
      goldFailRate: round1(goldFailRate), overrideRate: round1(overrideRate),
      peerAgree: round1(peerAgree * 100), reworkRate: round1(reworkRate),
      lowTenureShare: Math.round(lowTenureShare * 100),
      sev1: t.sev1_escalations, open: t.open_escalations,
      riskScore, riskLevel,
      drivers: drivers.sort((a, b) => b.w - a.w),
    };
  });

  const contributors = [];
  teams.forEach((tm) => {
    const n = clamp(Math.round(tm.contributors * 0.16), 3, 9);
    for (let i = 0; i < n; i++) {
      const seed = tm.team_id + "_c" + i;
      const fn = FIRST_NAMES[Math.floor(rng(seed + "fn") * FIRST_NAMES.length)];
      const ln = LAST_NAMES[Math.floor(rng(seed + "ln") * LAST_NAMES.length)];
      const tenure = Math.round(rngR(seed + "ten", 25, 900));
      const skillIdx = tm.work_type === "expert_review" ? 2 + Math.round(rng(seed + "sk")) : Math.floor(rng(seed + "sk") * 4);
      const cq = round1(clamp(tm.quality + rngR(seed + "q", -10, 6), 58, 99));
      const cGap = Math.max(0, Q_TARGET - cq);
      const goldPass = round1(clamp(100 - cGap * 1.4 - rng(seed + "gp") * 8, 52, 99));
      const override = round1(clamp(cGap * 0.9 + rng(seed + "ov") * 6 + 1, 1, 40));
      const rework = round1(clamp(tm.reworkRate + rngR(seed + "rw", -3, 7), 1, 32));
      const peer = round1(clamp(94 - cGap * 0.8 - rng(seed + "pa") * 6, 52, 98));
      const lowTenure = tenure < 120;
      const cScore = Math.round(cGap * 3 + (100 - goldPass) * 0.5 + override * 0.5 + rework * 1.1
        + (lowTenure && skillIdx >= 2 ? 10 : 0) + (peer < 75 ? 8 : 0));
      const cLevel = cScore >= 42 ? "High" : cScore >= 22 ? "Medium" : "Low";
      const cdrivers = [
        { k: "Quality vs target", v: round1(cGap), w: cGap * 3 },
        { k: "Gold-task pass", v: goldPass, w: (100 - goldPass) * 0.5 },
        { k: "Reviewer override", v: override, w: override * 0.5 },
        { k: "Rework", v: rework, w: rework * 1.1 },
        { k: "Peer agreement", v: peer, w: peer < 75 ? 8 : 0 },
      ].sort((a, b) => b.w - a.w);
      const top = cdrivers[0].k;
      const support = lowTenure && skillIdx >= 2 ? "Pair on complex tasks + ramp plan"
        : top === "Reviewer override" || top === "Peer agreement" ? "Reviewer calibration session"
        : top === "Gold-task pass" ? "Targeted gold-task retraining"
        : top === "Rework" ? "Workflow coaching + QA review"
        : "1:1 coaching on rubric application";
      contributors.push({
        id: "CON_" + (seed.split("").reduce((a, c) => a + c.charCodeAt(0), 0) % 9000 + 1000),
        name: `${fn} ${ln}`, team_id: tm.team_id, work_type: tm.work_type,
        tenure, skill: SKILL_LEVELS[skillIdx], quality: cq, goldPass, override, rework, peer,
        lowTenure, riskScore: cScore, riskLevel: cLevel, topDriver: top, support,
      });
    }
  });

  const flagged = contributors.filter((c) => c.riskLevel !== "Low").sort((a, b) => b.riskScore - a.riskScore);

  const byWorkType = d.workTypeRollup.map((w) => {
    const wt = teams.filter((t) => t.work_type === w.work_type);
    const highTeams = wt.filter((t) => t.riskLevel === "High").length;
    const avgScore = Math.round(wt.reduce((s, t) => s + t.riskScore, 0) / (wt.length || 1));
    const flaggedHere = flagged.filter((c) => c.work_type === w.work_type).length;
    const level = avgScore >= 42 ? "High" : avgScore >= 22 ? "Medium" : "Low";
    return { work_type: w.work_type, quality: w.quality, teams: wt.length, contributors: w.contributors, highTeams, avgScore, flagged: flaggedHere, level };
  }).sort((a, b) => b.avgScore - a.avgScore);

  const queue = [...teams].filter((t) => t.riskLevel !== "Insufficient").sort((a, b) => b.riskScore - a.riskScore).slice(0, 6);

  const region = {
    avgQuality: d.kpis.avg_quality,
    reworkRate: d.kpis.rework_rate,
    highRiskTeams: teams.filter((t) => t.riskLevel === "High").length,
    flaggedContributors: flagged.length,
    highRiskContributors: flagged.filter((c) => c.riskLevel === "High").length,
    teamCount: teams.length,
  };

  return { teams: teams.sort((a, b) => b.riskScore - a.riskScore), byWorkType, flagged, queue, region, contributors };
}

// Legacy alias — used by any older importer (drilldown, etc.)
export function deriveWorkforce(d) {
  const q = deriveQuality(d);
  if (!q) return null;
  return {
    teams: q.teams.map((t) => ({
      ...t, risk_score: t.riskScore, risk_band: t.riskLevel,
      drivers: t.drivers.map((dr) => `${dr.k}: ${dr.v}${dr.unit || ""}`),
      action: t.riskLevel === "High" ? "Calibration huddle + QA sampling boost." : t.riskLevel === "Medium" ? "Weekly check-in; refresh top gold tasks." : "Maintain.",
      sev1_escalations: t.sev1, escalations: 0, quality_gap: Math.max(0, 90 - t.quality),
    })),
    cohorts: q.byWorkType.map((c) => ({ work_type: c.work_type, n: c.teams, contributors: c.contributors, avg_quality: c.quality, avg_csat: 4.3, sev1: 0, risk_high: c.highTeams, teams: [] })),
    counts: {
      high: q.region.highRiskTeams,
      medium: q.teams.filter((t) => t.riskLevel === "Medium").length,
      low: q.teams.filter((t) => t.riskLevel === "Low").length,
    },
  };
}

// ─── Module D · Capacity, Staffing & SLA ────────────────────────────────────

const BASE_THROUGHPUT = { image_annotation: 46, audio_evaluation: 34, code_review: 26, rlhf_evaluation: 30, expert_review: 16 };
const COMPLEXITY_SHARE = { image_annotation: 0.12, audio_evaluation: 0.22, code_review: 0.34, rlhf_evaluation: 0.4, expert_review: 0.72 };

export function deriveCapacity(d) {
  if (!d) return null;
  const regionBacklog = d.kpis.backlog;
  const regionAged = d.kpis.aged_backlog_72h;
  const slaTrend = d.kpiTrends?.sla || null;
  const slaSlope = slaTrend ? slaTrend[slaTrend.length - 2] - slaTrend[Math.max(0, slaTrend.length - 4)] : 0;
  const backlogTrend = d.kpiTrends?.backlog || [];
  const weekly_delta = backlogTrend.length >= 2 ? backlogTrend[backlogTrend.length - 1] - backlogTrend[backlogTrend.length - 2] : 0;

  const wtWeights = d.workTypeRollup.map((w) => ({
    w, weight: (w.open_escalations + 1) * 1.4 + w.escalation_rate_per_1000 * 0.6 + w.contributors * 0.04,
  }));
  const weightSum = wtWeights.reduce((s, x) => s + x.weight, 0) || 1;

  const byWorkType = wtWeights.map(({ w, weight }) => {
    const share = weight / weightSum;
    const backlog = Math.round(regionBacklog * share);
    const aged = Math.round(regionAged * share);
    const basePer = BASE_THROUGHPUT[w.work_type] || 28;
    const throughput = Math.round(w.contributors * basePer * (0.78 + rng(w.work_type + "th") * 0.16));
    const inflow = Math.round(throughput * (1 + (w.escalation_rate_per_1000 / 100) + rngR(w.work_type + "in", -0.04, 0.12)));
    const utilization = Math.round(clamp((inflow / Math.max(1, throughput)) * 100, 62, 138));
    const backlogPressure = round1(backlog / Math.max(1, throughput));
    const complexity = COMPLEXITY_SHARE[w.work_type] || 0.3;
    const slaMiss = Math.max(0, SLA_TARGET - w.sla);
    const agedShare = Math.round((aged / Math.max(1, backlog)) * 100);

    const neededHeads = Math.ceil((inflow + aged / 2) / basePer);
    const headGap = neededHeads - w.contributors;

    const drivers = [
      { k: "Backlog pressure", v: backlogPressure, w: backlogPressure * 14, unit: "wk" },
      { k: "Aged backlog >72h", v: agedShare, w: agedShare * 0.4, unit: "%" },
      { k: "Utilization", v: utilization, w: Math.max(0, utilization - 100) * 1.3, unit: "%" },
      { k: "SLA miss vs target", v: round1(slaMiss), w: slaMiss * 2.2, unit: "pt" },
      { k: "Escalation overlay", v: w.escalation_rate_per_1000, w: w.escalation_rate_per_1000 * 0.5, unit: "/1k" },
      { k: "Quality overlay", v: round1(Math.max(0, Q_TARGET - w.quality)), w: Math.max(0, Q_TARGET - w.quality) * 1.1, unit: "pt" },
      { k: "High-complexity share", v: Math.round(complexity * 100), w: complexity * 14, unit: "%" },
    ];
    const riskScore = Math.round(drivers.reduce((s, dr) => s + dr.w, 0));
    const riskLevel = w.contributors < 18 && w.work_type !== "expert_review" ? "Insufficient" : riskScore >= 78 ? "High" : riskScore >= 44 ? "Medium" : "Low";

    const projected = round1(clamp(w.sla + slaSlope * 0.5 - Math.max(0, utilization - 100) * 0.18 - backlogPressure * 1.4, 60, 99));
    let forecast;
    if (projected >= SLA_TARGET && backlogPressure < 1.2) forecast = "Likely stable";
    else if (projected >= 92) forecast = "Watchlist";
    else if (projected >= 85) forecast = "At risk";
    else forecast = "Recovery needed";

    const sorted = [...drivers].sort((a, b) => b.w - a.w);
    const topK = sorted[0].k;
    const action = headGap > 0 ? `Add ${headGap} trained ${headGap === 1 ? "head" : "heads"} or surge coverage`
      : topK === "High-complexity share" ? "Cross-train mid-tier onto complex queue"
      : topK === "Utilization" ? "Rebalance load / shift coverage"
      : topK === "Quality overlay" ? "Slow intake, add QA gate before SLA risk compounds"
      : "Re-route overflow to lower-utilization team";

    return {
      work_type: w.work_type, contributors: w.contributors, teams: w.teams,
      sla: w.sla, quality: w.quality, escRate: w.escalation_rate_per_1000,
      backlog, aged, agedShare, throughput, inflow, utilization, backlogPressure,
      complexity: Math.round(complexity * 100), neededHeads, headGap,
      riskScore, riskLevel, projected, forecast, action, drivers: sorted,
      // legacy aliases
      util_band: utilization > 110 ? "overcapacity" : utilization > 100 ? "stretched" : "safe",
      sla_gap: slaMiss, open: w.open_escalations, sev1: w.sev1,
      projected_7d: backlog + Math.round(weekly_delta * share),
      projected_14d: backlog + Math.round(weekly_delta * 2 * share),
      delta_7d: Math.round(weekly_delta * share),
      recommendation: action, owner: "Workforce planning",
    };
  }).sort((a, b) => b.riskScore - a.riskScore);

  const teams = [];
  byWorkType.forEach((w) => {
    const wt = d.teams.filter((t) => t.work_type === w.work_type);
    const headSum = wt.reduce((s, t) => s + t.contributors, 0) || 1;
    const escSum = wt.reduce((s, x) => s + x.open_escalations + 1, 0) || 1;
    wt.forEach((t) => {
      const escW = (t.open_escalations + 1);
      const tShare = (t.contributors / headSum) * 0.6 + (escW / escSum) * 0.4;
      const backlog = Math.round(w.backlog * tShare);
      const basePer = BASE_THROUGHPUT[w.work_type] || 28;
      const throughput = Math.round(t.contributors * basePer * (0.78 + rng(t.team_id + "th") * 0.16));
      const utilization = Math.round(clamp((backlog / Math.max(1, throughput)) * 60 + 70 + rngR(t.team_id + "u", -6, 10), 60, 140));
      const lowTenureHighComplex = w.complexity > 50 && rng(t.team_id + "lt") > 0.55;
      const slaMiss = Math.max(0, SLA_TARGET - t.sla);
      const score = Math.round(slaMiss * 2.2 + Math.max(0, utilization - 100) * 1.3 + t.open_escalations * 0.8 + (lowTenureHighComplex ? 12 : 0));
      const level = score >= 46 ? "High" : score >= 24 ? "Medium" : "Low";
      teams.push({
        team_id: t.team_id, city: t.city, manager: t.manager, shift: t.shift, work_type: t.work_type,
        contributors: t.contributors, sla: t.sla, backlog, throughput, utilization,
        lowTenureHighComplex, openEsc: t.open_escalations, riskScore: score, riskLevel: level,
      });
    });
  });

  const region = {
    backlog: regionBacklog, aged: regionAged,
    agedShare: Math.round((regionAged / Math.max(1, regionBacklog)) * 100),
    atRisk: byWorkType.filter((w) => w.forecast === "At risk" || w.forecast === "Recovery needed").length,
    highRisk: byWorkType.filter((w) => w.riskLevel === "High").length,
    totalHeadGap: byWorkType.reduce((s, w) => s + Math.max(0, w.headGap), 0),
    avgSla: d.kpis.sla_adherence,
    weekly_delta,
    projected_7d: regionBacklog + weekly_delta,
    projected_14d: regionBacklog + weekly_delta * 2,
    utilization: Math.round(byWorkType.reduce((s, w) => s + w.utilization * w.contributors, 0) / Math.max(1, byWorkType.reduce((s, w) => s + w.contributors, 0))),
  };

  // legacy workTypes alias
  return { byWorkType, teams, region, rebalance: null, workTypes: byWorkType };
}

// Headline alerts shared by Home + Health
export function buildLeadershipAlerts(d, AUR) {
  if (!d) return [];
  const q = deriveQuality(d);
  const c = deriveCapacity(d);
  const alerts = [];
  const topPat = d.patterns.find((p) => p.risk_level === "High") || d.patterns[0];
  if (topPat) {
    alerts.push({
      severity: "High", color: AUR.bad, tag: WORK_TYPE_LABELS[topPat.work_type],
      title: `${ROOT_CAUSE_LABELS[topPat.root_cause]} in ${WORK_TYPE_LABELS[topPat.work_type]} is ${topPat.recurrence_status.toLowerCase()}`,
      body: `${topPat.escalation_count} escalations on this pattern · ${topPat.open_count} open · last-14d ${topPat.last_14d} vs prior ${topPat.prior_14d}. Same gap failing across ${topPat.unique_teams} teams.`,
      action: ROOT_CAUSE_DECISION[topPat.root_cause] || "Approve structural fix this week.",
      to: "/patterns", focus: { pid: topPat.pattern_id },
    });
  }
  const topCap = c?.byWorkType.find((w) => w.forecast === "At risk" || w.forecast === "Recovery needed");
  if (topCap) {
    alerts.push({
      severity: topCap.forecast === "Recovery needed" ? "High" : "Medium", color: topCap.forecast === "Recovery needed" ? AUR.bad : AUR.warn,
      tag: WORK_TYPE_LABELS[topCap.work_type],
      title: `${WORK_TYPE_LABELS[topCap.work_type]} SLA forecast: ${topCap.forecast.toLowerCase()} next week`,
      body: `Projected SLA ${topCap.projected}% vs 95% target · ${topCap.backlogPressure}wk backlog · ${topCap.utilization}% utilization${topCap.headGap > 0 ? ` · short ${topCap.headGap} trained heads` : ""}.`,
      action: topCap.action + ".",
      to: "/capacity", focus: { wt: topCap.work_type },
    });
  }
  const topQ = q?.teams.find((t) => t.riskLevel === "High");
  if (topQ && alerts.length < 3) {
    alerts.push({
      severity: "Medium", color: AUR.warn, tag: WORK_TYPE_LABELS[topQ.work_type],
      title: `Quality risk concentrating on ${topQ.team_id.replace("TEAM_APAC_", "")}`,
      body: `${topQ.manager}'s team · quality ${topQ.quality} (${topQ.driftDelta < 0 ? "down" : "up"} ${Math.abs(topQ.driftDelta)}pt) · gold-fail ${topQ.goldFailRate}% · rework ${topQ.reworkRate}%. Coaching signal, not a scoreboard.`,
      action: "Add to weekly coaching & calibration queue.",
      to: "/workforce", focus: { tm: topQ.team_id, wt: topQ.work_type },
    });
  }
  return alerts.slice(0, 3);
}
