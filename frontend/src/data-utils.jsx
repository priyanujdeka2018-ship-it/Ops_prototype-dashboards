// Shared data loader + formatting helpers for Scale Ops Command Center
// Exposes (to window): useScaleData, fmt, statusColor, ROOT_CAUSE_LABELS, etc.

const ROOT_CAUSE_LABELS = {
  policy_ambiguity: "Policy ambiguity",
  reviewer_misalignment: "Reviewer misalignment",
  quality_defect: "Quality defect",
  tooling_issue: "Tooling issue",
  customer_requirement_change: "Customer requirement change",
  sla_miss: "SLA miss",
  workflow_handoff_gap: "Workflow handoff gap",
  capacity_shortfall: "Capacity shortfall",
};

const WORK_TYPE_LABELS = {
  image_annotation: "Image annotation",
  rlhf_evaluation: "RLHF evaluation",
  code_review: "Code review",
  audio_evaluation: "Audio evaluation",
  expert_review: "Expert review",
};

const ROOT_CAUSE_FIX = {
  policy_ambiguity: {
    fix: "SOP rewrite + calibration huddle",
    owner: "Policy Ops lead + frontline manager",
    metric: "Reviewer agreement rate; repeat escalations",
  },
  reviewer_misalignment: {
    fix: "Reviewer calibration + QA sampling boost",
    owner: "Quality lead + reviewer manager",
    metric: "Disagreement rate; QA defect rate",
  },
  quality_defect: {
    fix: "Gold task refresh + QA containment",
    owner: "QA lead",
    metric: "Quality score; gold task pass rate",
  },
  tooling_issue: {
    fix: "Tooling change + workaround comm",
    owner: "Tooling / product ops",
    metric: "Tooling escalations; outage incidents",
  },
  customer_requirement_change: {
    fix: "Customer instruction propagation",
    owner: "Customer ops lead + training",
    metric: "Instruction-change escalations; CSAT",
  },
  sla_miss: {
    fix: "Staffing / capacity correction",
    owner: "Regional ops manager",
    metric: "SLA adherence; aged backlog",
  },
  workflow_handoff_gap: {
    fix: "Queue routing + named handoff owner",
    owner: "Workflow ops lead",
    metric: "Handoff delay; reopen rate",
  },
  capacity_shortfall: {
    fix: "Staffing rebalance / surge coverage",
    owner: "Workforce planning lead",
    metric: "Backlog age; utilization",
  },
};

// Decision for fix card — derived from root cause
const ROOT_CAUSE_DECISION = {
  policy_ambiguity: "Approve SOP clarification + require examples for ambiguous cases",
  reviewer_misalignment: "Calibration: one team or regional reviewers?",
  quality_defect: "Approve gold-task refresh + temporary QA sampling boost",
  tooling_issue: "Prioritize fix or approve interim operational workaround",
  customer_requirement_change: "Confirm source of truth, audit propagation",
  sla_miss: "Approve temp staffing rebalance / surge coverage",
  workflow_handoff_gap: "Clarify handoff ownership, update routing rules",
  capacity_shortfall: "Approve capacity rebalance / cross-trained backup",
};

const SEVERITY_LABELS = { sev1: "Sev 1", sev2: "Sev 2", sev3: "Sev 3", sev4: "Sev 4" };

// Status color tokens, neutral hex — themes can override via CSS variables
const STATUS_COLORS = {
  good: "#10B981",
  warn: "#F59E0B",
  bad: "#EF4444",
  info: "#22D3EE",
  muted: "#64748B",
};

// classify metric → 'good' | 'warn' | 'bad' based on Scale-ish thresholds
// Thresholds mirror src/rules.py HEALTH_THRESHOLDS (sla/quality on the
// percent scale used by data.json).
function classifyMetric(metric, value) {
  switch (metric) {
    case "sla":
      return value >= 95 ? "good" : value >= 90 ? "warn" : "bad";
    case "csat":
      return value >= 4.4 ? "good" : value >= 4.2 ? "warn" : "bad";
    case "quality":
      return value >= 90 ? "good" : value >= 85 ? "warn" : "bad";
    case "escalation_rate":
      return value <= 8 ? "good" : value <= 15 ? "warn" : "bad";
    case "open":
      return value <= 5 ? "good" : value <= 15 ? "warn" : "bad";
    case "sev1":
      return value === 0 ? "good" : value <= 2 ? "warn" : "bad";
    default:
      return "muted";
  }
}

const fmt = {
  pct: (v) => `${(v).toFixed(1)}%`,
  num: (v) => v.toLocaleString("en-US"),
  dec: (v, d = 1) => Number(v).toFixed(d),
  short: (v) =>
    v >= 1000 ? (v / 1000).toFixed(1) + "k" : String(Math.round(v)),
  date: (iso) => {
    const d = new Date(iso);
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  },
  rel: (days) => {
    if (days === 0) return "today";
    if (days === 1) return "1d ago";
    if (days < 30) return `${days}d ago`;
    return `${Math.floor(days / 7)}w ago`;
  },
};

// React hook to load the scenario-specific payload, refetching when the
// scenario changes. Falls back to data.json if the scenario file is absent
// (single-scenario deploys), so older deploys keep working.
function useScaleData(scenario = "current") {
  const [data, setData] = React.useState(null);
  const [err, setErr] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  React.useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setErr(null);
    const primary = `data/data-${scenario}.json`;
    fetch(primary)
      .then((r) => (r.ok ? r.json() : fetch("data/data.json").then((f) => f.json())))
      .then((d) => { if (!cancelled) { setData(d); setLoading(false); } })
      .catch((e) => { if (!cancelled) { setErr(String(e)); setLoading(false); } });
    return () => { cancelled = true; };
  }, [scenario]);
  return { data, err, loading, scenario };
}

// Sparkline: takes array of numbers, renders an inline SVG
function Sparkline({ values, color = "currentColor", width = 80, height = 24, fill = false, strokeWidth = 1.5 }) {
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
      {fill && <path d={areaPath} fill={color} opacity={0.15} />}
      <path d={path} fill="none" stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

// Scenario amplifier — applies tweak scenario (healthy/degrading/crisis) to KPIs
function applyScenario(data, scenario) {
  if (!data) return data;
  const out = { ...data, kpis: { ...data.kpis } };
  if (scenario === "healthy") {
    out.kpis = {
      ...out.kpis,
      sla_adherence: 96.4,
      csat_7d: 4.62,
      backlog: 840,
      aged_backlog_72h: 84,
      escalation_rate_per_1000: 6.2,
      avg_quality: 95.3,
      rework_rate: 2.4,
      fcr_proxy: 92.7,
    };
  } else if (scenario === "crisis") {
    out.kpis = {
      ...out.kpis,
      sla_adherence: 82.1,
      csat_7d: 3.78,
      backlog: 1934,
      aged_backlog_72h: 1247,
      escalation_rate_per_1000: 28.0,
      avg_quality: 84.4,
      rework_rate: 9.7,
      fcr_proxy: 76.1,
    };
  }
  return out;
}

Object.assign(window, {
  ROOT_CAUSE_LABELS,
  WORK_TYPE_LABELS,
  ROOT_CAUSE_FIX,
  ROOT_CAUSE_DECISION,
  SEVERITY_LABELS,
  STATUS_COLORS,
  classifyMetric,
  fmt,
  useScaleData,
  Sparkline,
  applyScenario,
});
