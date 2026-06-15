// Aurora · Scale Regional Ops Command Center
// Editorial dark · Instrument Serif headers · Geist body · electric accent.
// Wired interactivity: tab nav, work-type filter, pattern click → detail,
// briefing modal, about modal. Accent color is configurable.

// Build a theme object from a single accent hex
function buildAurTheme(accent) {
  // map accent to a deeper companion for gradients (lazy: tint of accent darker)
  const accentDeepMap = {
    "#B79DFF": "#7C5CFC",
    "#5EEAD4": "#0EB8A0",
    "#FF8FB1": "#F43F8C",
    "#7DD3FC": "#0284C7",
    "#FBBF77": "#EA8A1E",
  };
  return {
    bg: "#0A0A12",
    surface: "rgba(255,255,255,0.025)",
    surfaceHi: "rgba(255,255,255,0.045)",
    border: "rgba(255,255,255,0.08)",
    borderHi: "rgba(255,255,255,0.15)",
    text: "#F5F5F0",
    textDim: "#B7B5AA",
    textFaint: "#6E6C66",
    accent,
    accentDeep: accentDeepMap[accent] || "#7C5CFC",
    accentGlow: accent + "30",
    good: "#5EEAD4",
    warn: "#FBBF77",
    bad: "#F87171",
  };
}

const aurSans = `"Geist", "Geist Sans", ui-sans-serif, system-ui, sans-serif`;
const aurSerif = `"Instrument Serif", "Source Serif Pro", Georgia, serif`;
const aurMono = `"Geist Mono", "JetBrains Mono", ui-monospace, monospace`;

// ─── Atoms ──────────────────────────────────────────────────────────────────

function AurChip({ children, color, bg, AUR }) {
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 6, padding: "3px 10px", borderRadius: 999, background: bg || AUR.surface, color: color || AUR.textDim, fontFamily: aurMono, fontSize: 10.5, letterSpacing: 0.5, textTransform: "uppercase", border: `1px solid ${AUR.border}` }}>
      {children}
    </span>
  );
}

function AurStatusPill({ status, AUR }) {
  const map = {
    Accelerating: { c: AUR.bad, label: "Accelerating" },
    Recurring: { c: AUR.warn, label: "Recurring" },
    New: { c: AUR.accent, label: "New" },
    Watchlist: { c: AUR.warn, label: "Watchlist" },
    Resolved: { c: AUR.good, label: "Resolved" },
    Dormant: { c: AUR.textFaint, label: "Dormant" },
    "Low activity": { c: AUR.textFaint, label: "Low" },
  };
  const s = map[status] || map["Low activity"];
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 6, fontFamily: aurMono, fontSize: 10.5, color: s.c, letterSpacing: 0.3 }}>
      <span style={{ width: 6, height: 6, borderRadius: "50%", background: s.c, boxShadow: `0 0 8px ${s.c}88` }} />
      {s.label}
    </span>
  );
}

function AurRiskBadge({ level, AUR }) {
  const c = level === "High" ? AUR.bad : level === "Medium" ? AUR.warn : AUR.textDim;
  return (
    <span style={{
      fontFamily: aurMono, fontSize: 11, color: c,
      padding: "3px 10px", borderRadius: 999,
      background: `${c}15`, border: `1px solid ${c}40`,
      letterSpacing: 0.5, textTransform: "uppercase",
    }}>{level}</span>
  );
}

function AurKpi({ label, value, sub, status = "good", trendData, large = false, AUR }) {
  const colorMap = { good: AUR.good, warn: AUR.warn, bad: AUR.bad, info: AUR.accent };
  const c = colorMap[status] || AUR.text;
  return (
    <div style={{
      background: AUR.surface,
      border: `1px solid ${AUR.border}`,
      borderRadius: 14,
      padding: large ? "20px 22px" : "16px 18px",
      backdropFilter: "blur(20px)",
      position: "relative", overflow: "hidden",
      transition: "border-color 200ms ease",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 10 }}>
        <div style={{ minWidth: 0 }}>
          <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.7, textTransform: "uppercase" }}>{label}</div>
          <div style={{ fontFamily: aurSerif, fontSize: large ? 44 : 32, fontWeight: 400, color: AUR.text, letterSpacing: -1, fontVariantNumeric: "tabular-nums", marginTop: 6, lineHeight: 1 }}>{value}</div>
          <div style={{ fontFamily: aurSans, fontSize: 11.5, color: AUR.textDim, marginTop: 8 }}>{sub}</div>
        </div>
        {trendData && (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 4 }}>
            <span style={{ width: 8, height: 8, borderRadius: "50%", background: c, boxShadow: `0 0 12px ${c}99` }} />
            <Sparkline values={trendData} color={c} width={60} height={22} fill strokeWidth={1.5} />
          </div>
        )}
      </div>
    </div>
  );
}

function AurSection({ eyebrow, title, lede, right, children, AUR }) {
  return (
    <section style={{ marginTop: 40 }}>
      <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", marginBottom: 18, gap: 24 }}>
        <div style={{ maxWidth: 760 }}>
          <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 1.4, textTransform: "uppercase", marginBottom: 8 }}>{eyebrow}</div>
          <h2 style={{ fontFamily: aurSerif, fontSize: 32, fontWeight: 400, color: AUR.text, letterSpacing: -0.7, margin: 0, lineHeight: 1.1 }}>{title}</h2>
          {lede && <p style={{ fontFamily: aurSans, fontSize: 14, color: AUR.textDim, marginTop: 10, lineHeight: 1.55, maxWidth: 640 }}>{lede}</p>}
        </div>
        {right}
      </div>
      {children}
    </section>
  );
}

function AurButton({ children, variant = "ghost", onClick, active = false, AUR }) {
  const base = { fontFamily: aurSans, fontSize: 12.5, padding: "8px 14px", borderRadius: 999, cursor: "pointer", display: "inline-flex", alignItems: "center", gap: 6, fontWeight: 500, transition: "all 180ms ease", whiteSpace: "nowrap" };
  const variants = {
    primary: { ...base, background: AUR.accent, color: "#1a0033", border: "none" },
    ghost: { ...base, background: active ? AUR.accentGlow : "transparent", color: active ? AUR.accent : AUR.text, border: `1px solid ${active ? AUR.accent + "55" : AUR.border}` },
    accent: { ...base, background: AUR.accentGlow, color: AUR.accent, border: `1px solid ${AUR.accent}55` },
  };
  return <button style={variants[variant]} onClick={onClick}>{children}</button>;
}

// ─── Cell helpers ──────────────────────────────────────────────────────────

function MetricCell({ value, status, AUR }) {
  const c = status === "good" ? AUR.good : status === "warn" ? AUR.warn : status === "bad" ? AUR.bad : AUR.textFaint;
  return (
    <div style={{
      border: `1px solid ${c}40`,
      background: `${c}10`,
      borderRadius: 10,
      padding: "12px 8px",
      textAlign: "center",
      fontFamily: aurMono,
      fontSize: 14,
      color: c,
      fontWeight: 500,
      fontVariantNumeric: "tabular-nums",
    }}>{value}</div>
  );
}

// ─── Tabs ──────────────────────────────────────────────────────────────────

function OverviewTab({ d, k, AUR, onJumpToWorkType, onJumpToPatterns }) {
  const rollup = d.workTypeRollup;
  const rootCausesTop = Object.entries(d.rootCauseCounts).sort((a, b) => b[1] - a[1]).slice(0, 6);
  const maxRoot = rootCausesTop[0][1];

  // Build leadership alerts from real data signals
  const alerts = [];
  const expertRow = rollup.find(r => r.work_type === "expert_review");
  if (expertRow && expertRow.sev1 >= 3) {
    alerts.push({
      sev: "High", color: AUR.bad, wt: "expert_review",
      title: "Expert Review · SLA breach + sev1 cluster",
      body: `${expertRow.sev1} sev1 escalations this period across ${expertRow.teams} teams. SLA at ${expertRow.sla.toFixed(1)}% against a 95% target.`,
      action: "Stand up a war room with EXPERT_01/02 managers by EOD.",
    });
  }
  // accelerating pattern alert
  const acc = d.patterns.find(p => p.recurrence_status === "Accelerating" && p.risk_level === "High");
  if (acc) {
    alerts.push({
      sev: "High", color: AUR.bad, wt: acc.work_type,
      title: `${WORK_TYPE_LABELS[acc.work_type]} · ${ROOT_CAUSE_LABELS[acc.root_cause]} accelerating`,
      body: `${acc.escalation_count} escalations across this pattern · last-14-day count ${acc.last_14d} exceeds prior-14-day count of ${acc.prior_14d}. Same operational gap is failing at scale.`,
      action: ROOT_CAUSE_DECISION[acc.root_cause] || "Approve structural fix this week.",
    });
  }
  // recurring + open
  const rec = d.patterns.find(p => p.recurrence_status === "Recurring" && p.open_count >= 3 && (!acc || p.pattern_id !== acc.pattern_id));
  if (rec) {
    const fix = ROOT_CAUSE_FIX[rec.root_cause] || { fix: "Manager review" };
    alerts.push({
      sev: "Medium", color: AUR.warn, wt: rec.work_type,
      title: `${WORK_TYPE_LABELS[rec.work_type]} · ${ROOT_CAUSE_LABELS[rec.root_cause]} recurrence`,
      body: `${rec.escalation_count} escalations · ${rec.open_count} open · avg ${rec.avg_days_to_resolve}d to resolve. Spans ${rec.unique_teams} teams.`,
      action: fix.fix + ".",
    });
  }

  return (
    <>
      <AurSection
        AUR={AUR}
        eyebrow="Module A · Regional Health"
        title="Where the region is breathing — and where it isn't."
        lede="Every work-type metric, classified against Scale ops thresholds. Red is a breach. Amber is a watch. Teal holds the line. Click a row to drill in."
        right={<div style={{ display: "flex", gap: 8 }}>
          <AurChip AUR={AUR} color={AUR.good}><span style={{ width: 6, height: 6, borderRadius: "50%", background: AUR.good }} />On target</AurChip>
          <AurChip AUR={AUR} color={AUR.warn}><span style={{ width: 6, height: 6, borderRadius: "50%", background: AUR.warn }} />Watch</AurChip>
          <AurChip AUR={AUR} color={AUR.bad}><span style={{ width: 6, height: 6, borderRadius: "50%", background: AUR.bad }} />Breach</AurChip>
        </div>}
      >
        <div style={{ background: AUR.surface, border: `1px solid ${AUR.border}`, borderRadius: 16, padding: 24, backdropFilter: "blur(20px)" }}>
          <div style={{ display: "grid", gridTemplateColumns: "240px repeat(6, 1fr) 40px", gap: 14, alignItems: "center" }}>
            <div />
            {[
              { l: "SLA" }, { l: "CSAT" }, { l: "Quality" }, { l: "Esc / 1k" }, { l: "Open" }, { l: "Sev 1" }
            ].map((m, i) => (
              <div key={i} style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase", textAlign: "center" }}>{m.l}</div>
            ))}
            <div />
            {rollup.map((row) => (
              <React.Fragment key={row.work_type}>
                <div>
                  <div style={{ fontFamily: aurSerif, fontSize: 19, fontWeight: 400, color: AUR.text, letterSpacing: -0.3 }}>{WORK_TYPE_LABELS[row.work_type]}</div>
                  <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.4, marginTop: 2 }}>{row.teams} teams · {row.contributors} heads</div>
                </div>
                <MetricCell AUR={AUR} value={`${row.sla.toFixed(1)}%`} status={classifyMetric("sla", row.sla)} />
                <MetricCell AUR={AUR} value={row.csat.toFixed(2)} status={classifyMetric("csat", row.csat)} />
                <MetricCell AUR={AUR} value={row.quality.toFixed(1)} status={classifyMetric("quality", row.quality)} />
                <MetricCell AUR={AUR} value={row.escalation_rate_per_1000} status={classifyMetric("escalation_rate", row.escalation_rate_per_1000)} />
                <MetricCell AUR={AUR} value={row.open_escalations} status={classifyMetric("open", row.open_escalations)} />
                <MetricCell AUR={AUR} value={row.sev1} status={classifyMetric("sev1", row.sev1)} />
                <button onClick={() => onJumpToWorkType(row.work_type)} style={{ background: "transparent", border: "none", color: AUR.textFaint, cursor: "pointer", padding: 6, fontFamily: aurSans, fontSize: 18 }}>→</button>
              </React.Fragment>
            ))}
          </div>
        </div>
      </AurSection>

      <div style={{ display: "grid", gridTemplateColumns: "1.45fr 1fr", gap: 20, marginTop: 32 }}>
        <AurSection AUR={AUR} eyebrow="Leadership attention" title="Three things that matter this week.">
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {alerts.slice(0, 3).map((a, i) => (
              <div key={i} style={{ background: AUR.surface, border: `1px solid ${AUR.border}`, borderRadius: 14, padding: 20 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
                  <span style={{ width: 8, height: 8, borderRadius: "50%", background: a.color, boxShadow: `0 0 12px ${a.color}99` }} />
                  <span style={{ fontFamily: aurMono, fontSize: 10.5, color: a.color, letterSpacing: 0.7, textTransform: "uppercase" }}>{a.sev} severity · {WORK_TYPE_LABELS[a.wt]}</span>
                </div>
                <div style={{ fontFamily: aurSerif, fontSize: 20, fontWeight: 400, color: AUR.text, letterSpacing: -0.4, marginBottom: 6 }}>{a.title}</div>
                <div style={{ color: AUR.textDim, lineHeight: 1.55, marginBottom: 10, fontSize: 13.5 }}>{a.body}</div>
                <div style={{ display: "flex", alignItems: "baseline", gap: 8, color: AUR.accent, fontSize: 13 }}>
                  <span style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase" }}>Action</span>
                  <span>{a.action}</span>
                </div>
              </div>
            ))}
          </div>
        </AurSection>

        <AurSection AUR={AUR} eyebrow="Module B · Recurring themes" title="What keeps coming back." right={
          <button onClick={onJumpToPatterns} style={{ background: "transparent", border: `1px solid ${AUR.border}`, color: AUR.text, fontFamily: aurSans, fontSize: 12.5, padding: "6px 14px", borderRadius: 999, cursor: "pointer" }}>View detector →</button>
        }>
          <div style={{ background: AUR.surface, border: `1px solid ${AUR.border}`, borderRadius: 14, padding: 20 }}>
            <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", marginBottom: 16, paddingBottom: 14, borderBottom: `1px solid ${AUR.border}` }}>
              <div>
                <div style={{ fontFamily: aurSerif, fontSize: 48, fontWeight: 400, letterSpacing: -1.4, lineHeight: 1, color: AUR.text }}>{d.totals.escalations}</div>
                <div style={{ fontFamily: aurMono, fontSize: 11, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase", marginTop: 6 }}>14 wks · {d.totals.open} open · {d.totals.sev1} sev1</div>
              </div>
              <Sparkline values={d.weeklyTrend.map((w) => w.count)} color={AUR.accent} width={140} height={48} fill strokeWidth={1.5} />
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {rootCausesTop.map(([rc, c]) => (
                <div key={rc} style={{ display: "grid", gridTemplateColumns: "1fr 36px", gap: 10, alignItems: "center" }}>
                  <div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 4 }}>
                      <span style={{ color: AUR.text, fontSize: 13 }}>{ROOT_CAUSE_LABELS[rc] || rc}</span>
                    </div>
                    <div style={{ height: 4, background: AUR.surfaceHi, borderRadius: 2, overflow: "hidden" }}>
                      <div style={{ width: `${(c / maxRoot) * 100}%`, height: "100%", background: `linear-gradient(90deg, ${AUR.accent}, ${AUR.accentDeep})`, borderRadius: 2 }} />
                    </div>
                  </div>
                  <span style={{ fontFamily: aurMono, fontSize: 13, color: AUR.text, fontVariantNumeric: "tabular-nums", textAlign: "right" }}>{c}</span>
                </div>
              ))}
            </div>
          </div>
        </AurSection>
      </div>
    </>
  );
}

function PatternsTab({ d, AUR, selectedPatternId, setSelectedPatternId, statusFilter, setStatusFilter, riskFilter, setRiskFilter }) {
  const filtered = d.patterns.filter(p => {
    if (statusFilter !== "all" && p.recurrence_status !== statusFilter) return false;
    if (riskFilter !== "all" && p.risk_level !== riskFilter) return false;
    return true;
  });

  const selected = d.patterns.find(p => p.pattern_id === selectedPatternId);

  return (
    <AurSection
      AUR={AUR}
      eyebrow="Module B · Pattern Detector"
      title={`${d.patterns.length} recurring patterns. ${d.patterns.filter(p => p.risk_level === "High").length} demand action.`}
      lede="Every escalation grouped on work_type + root_cause. Risk score is deterministic and explainable — escalation count, severity weight, open count, segment spread, slow-resolution penalty, acceleration bonus."
      right={
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
          {["all", "High", "Medium", "Low"].map(r => (
            <button key={r} onClick={() => setRiskFilter(r)} style={{
              background: riskFilter === r ? AUR.accentGlow : "transparent",
              color: riskFilter === r ? AUR.accent : AUR.textDim,
              border: `1px solid ${riskFilter === r ? AUR.accent + "55" : AUR.border}`,
              borderRadius: 999, padding: "6px 12px", fontFamily: aurMono, fontSize: 10.5, letterSpacing: 0.5, textTransform: "uppercase", cursor: "pointer",
            }}>{r === "all" ? "All risk" : r}</button>
          ))}
        </div>
      }
    >
      <div style={{ display: "flex", gap: 6, marginBottom: 14, flexWrap: "wrap" }}>
        {["all", "Accelerating", "Recurring", "Watchlist", "New", "Resolved", "Dormant", "Low activity"].map(s => {
          const count = s === "all" ? d.patterns.length : d.patterns.filter(p => p.recurrence_status === s).length;
          if (s !== "all" && count === 0) return null;
          return (
            <button key={s} onClick={() => setStatusFilter(s)} style={{
              background: statusFilter === s ? AUR.surfaceHi : "transparent",
              color: statusFilter === s ? AUR.text : AUR.textDim,
              border: `1px solid ${statusFilter === s ? AUR.borderHi : AUR.border}`,
              borderRadius: 999, padding: "5px 12px", fontFamily: aurSans, fontSize: 12, cursor: "pointer",
            }}>{s === "all" ? "All status" : s} <span style={{ color: AUR.textFaint, marginLeft: 4 }}>{count}</span></button>
          );
        })}
      </div>

      <div style={{ background: AUR.surface, border: `1px solid ${AUR.border}`, borderRadius: 16, overflow: "hidden" }}>
        <div style={{ display: "grid", gridTemplateColumns: "2.3fr 0.5fr 0.5fr 0.5fr 1fr 0.8fr 0.6fr", padding: "14px 22px", borderBottom: `1px solid ${AUR.border}`, fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase" }}>
          <div>Pattern</div><div style={{ textAlign: "right" }}>Esc</div><div style={{ textAlign: "right" }}>Sev1</div><div style={{ textAlign: "right" }}>Open</div><div>Status</div><div>Risk</div><div style={{ textAlign: "right" }}>Score</div>
        </div>
        {filtered.length === 0 && (
          <div style={{ padding: 32, textAlign: "center", color: AUR.textFaint, fontStyle: "italic" }}>No patterns match these filters.</div>
        )}
        {filtered.map((p, i) => (
          <button
            key={p.pattern_id}
            onClick={() => setSelectedPatternId(selectedPatternId === p.pattern_id ? null : p.pattern_id)}
            style={{
              display: "grid", gridTemplateColumns: "2.3fr 0.5fr 0.5fr 0.5fr 1fr 0.8fr 0.6fr",
              padding: "14px 22px", borderBottom: i === filtered.length - 1 ? "none" : `1px solid ${AUR.border}`,
              alignItems: "center", width: "100%", textAlign: "left",
              background: selectedPatternId === p.pattern_id ? AUR.surfaceHi : "transparent",
              border: "none",
              borderLeft: selectedPatternId === p.pattern_id ? `3px solid ${AUR.accent}` : "3px solid transparent",
              borderRight: "none",
              borderTop: "none",
              borderBottomColor: i === filtered.length - 1 ? "transparent" : AUR.border,
              borderBottomWidth: 1, borderBottomStyle: "solid",
              fontFamily: aurSans,
              cursor: "pointer",
              color: AUR.text,
              transition: "background 150ms ease",
            }}
          >
            <div>
              <div style={{ fontFamily: aurSerif, fontSize: 17, fontWeight: 400, color: AUR.text, letterSpacing: -0.2 }}>
                {ROOT_CAUSE_LABELS[p.root_cause]} <span style={{ color: AUR.textFaint }}>in</span> {WORK_TYPE_LABELS[p.work_type]}
              </div>
              <div style={{ fontFamily: aurMono, fontSize: 11, color: AUR.textFaint, letterSpacing: 0.4, marginTop: 2 }}>{p.unique_teams} teams · {p.unique_segments} segments · first seen {fmt.date(p.first_seen)} · latest {fmt.date(p.latest_seen)}</div>
            </div>
            <div style={{ textAlign: "right", fontFamily: aurMono, color: AUR.text, fontVariantNumeric: "tabular-nums" }}>{p.escalation_count}</div>
            <div style={{ textAlign: "right", fontFamily: aurMono, color: p.sev1_count > 0 ? AUR.bad : AUR.textFaint, fontVariantNumeric: "tabular-nums" }}>{p.sev1_count}</div>
            <div style={{ textAlign: "right", fontFamily: aurMono, color: p.open_count > 5 ? AUR.warn : AUR.text, fontVariantNumeric: "tabular-nums" }}>{p.open_count}</div>
            <div><AurStatusPill AUR={AUR} status={p.recurrence_status} /></div>
            <div><AurRiskBadge AUR={AUR} level={p.risk_level} /></div>
            <div style={{ textAlign: "right", fontFamily: aurSerif, fontSize: 22, color: p.risk_score > 50 ? AUR.bad : p.risk_score > 20 ? AUR.warn : AUR.text, fontVariantNumeric: "tabular-nums", letterSpacing: -0.5 }}>{p.risk_score}</div>
          </button>
        ))}
      </div>

      {selected && (
        <div style={{ marginTop: 20, background: `linear-gradient(135deg, ${AUR.accentGlow}, transparent 60%)`, border: `1px solid ${AUR.accent}55`, borderRadius: 16, padding: 26 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 18 }}>
            <div>
              <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 0.8, textTransform: "uppercase", marginBottom: 6 }}>Pattern drilldown · {selected.pattern_id}</div>
              <div style={{ fontFamily: aurSerif, fontSize: 26, fontWeight: 400, color: AUR.text, letterSpacing: -0.5, lineHeight: 1.15 }}>
                {ROOT_CAUSE_LABELS[selected.root_cause]} <span style={{ color: AUR.textFaint }}>in</span> {WORK_TYPE_LABELS[selected.work_type]}
              </div>
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <AurStatusPill AUR={AUR} status={selected.recurrence_status} />
              <AurRiskBadge AUR={AUR} level={selected.risk_level} />
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: 24 }}>
            <div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 10, marginBottom: 18 }}>
                {[
                  { l: "Escalations", v: selected.escalation_count },
                  { l: "Sev 1 / 2", v: `${selected.sev1_count} / ${selected.sev2_count}` },
                  { l: "Open", v: selected.open_count },
                  { l: "Avg days", v: selected.avg_days_to_resolve },
                  { l: "Last 14d", v: `${selected.last_14d} (prior ${selected.prior_14d})` },
                ].map((m, i) => (
                  <div key={i} style={{ background: AUR.surface, borderRadius: 10, padding: "10px 12px", border: `1px solid ${AUR.border}` }}>
                    <div style={{ fontFamily: aurMono, fontSize: 10, color: AUR.textFaint, letterSpacing: 0.5, textTransform: "uppercase" }}>{m.l}</div>
                    <div style={{ fontFamily: aurSerif, fontSize: 22, color: AUR.text, marginTop: 2, fontVariantNumeric: "tabular-nums" }}>{m.v}</div>
                  </div>
                ))}
              </div>
              <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase", marginBottom: 8 }}>Recent escalation summaries</div>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {selected.sample_summaries.map((s, i) => (
                  <div key={i} style={{ fontSize: 13, color: AUR.textDim, paddingLeft: 14, borderLeft: `2px solid ${AUR.border}`, lineHeight: 1.5, fontStyle: "italic" }}>"{s}"</div>
                ))}
              </div>
              <div style={{ marginTop: 14, fontFamily: aurMono, fontSize: 11, color: AUR.textFaint }}>
                Affected teams: <span style={{ color: AUR.text }}>{selected.teams.join(", ")}</span>
              </div>
            </div>
            <div>
              <div style={{ background: AUR.surface, border: `1px solid ${AUR.border}`, borderRadius: 12, padding: 18 }}>
                <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase", marginBottom: 12 }}>Recommended structural fix</div>
                {(() => {
                  const fix = ROOT_CAUSE_FIX[selected.root_cause] || { fix: "Manager review", owner: "Regional ops", metric: "Escalation count" };
                  const decision = ROOT_CAUSE_DECISION[selected.root_cause] || "Assign owner + prevention plan";
                  return (
                    <>
                      <div style={{ display: "grid", gridTemplateColumns: "70px 1fr", gap: "10px 14px", fontSize: 13, marginBottom: 14 }}>
                        <span style={{ color: AUR.textFaint, fontFamily: aurMono, fontSize: 10.5, textTransform: "uppercase", letterSpacing: 0.5 }}>Fix</span>
                        <span style={{ color: AUR.text }}>{fix.fix}</span>
                        <span style={{ color: AUR.textFaint, fontFamily: aurMono, fontSize: 10.5, textTransform: "uppercase", letterSpacing: 0.5 }}>Owner</span>
                        <span style={{ color: AUR.text }}>{fix.owner}</span>
                        <span style={{ color: AUR.textFaint, fontFamily: aurMono, fontSize: 10.5, textTransform: "uppercase", letterSpacing: 0.5 }}>Metric</span>
                        <span style={{ color: AUR.text }}>{fix.metric}</span>
                      </div>
                      <div style={{ padding: "12px 14px", background: AUR.accentGlow, borderRadius: 10, borderLeft: `2px solid ${AUR.accent}` }}>
                        <div style={{ fontFamily: aurMono, fontSize: 10, color: AUR.accent, letterSpacing: 0.6, textTransform: "uppercase", marginBottom: 4 }}>Decision needed this week</div>
                        <div style={{ fontSize: 13, color: AUR.text, lineHeight: 1.45 }}>{decision}</div>
                      </div>
                    </>
                  );
                })()}
              </div>
            </div>
          </div>
        </div>
      )}
    </AurSection>
  );
}

function ClustersTab({ d, AUR }) {
  return (
    <AurSection
      AUR={AUR}
      eyebrow="Module B v2 · Semantic clusters"
      title="When different teams describe the same breakdown."
      lede="TF-IDF + cosine similarity finds repeat themes that don't share a root-cause label. Each cluster becomes a structural fix card with an owner, a metric to watch, and a decision."
    >
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18 }}>
        {d.patterns.slice(0, 6).map((p) => {
          const fix = ROOT_CAUSE_FIX[p.root_cause] || { fix: "Manager review", owner: "Regional ops", metric: "Escalation count" };
          const decision = ROOT_CAUSE_DECISION[p.root_cause] || "Assign owner + prevention plan";
          return (
            <div key={p.pattern_id} style={{ background: AUR.surface, border: `1px solid ${AUR.border}`, borderRadius: 16, padding: 24, position: "relative", overflow: "hidden" }}>
              <div style={{ position: "absolute", top: 0, right: 0, width: 100, height: 100, background: `radial-gradient(circle at top right, ${p.risk_level === "High" ? AUR.bad : p.risk_level === "Medium" ? AUR.warn : AUR.accent}25, transparent 60%)`, pointerEvents: "none" }} />
              <div style={{ position: "relative" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10, gap: 12 }}>
                  <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase" }}>Cluster · {p.pattern_id.slice(-8)}</div>
                  <AurStatusPill AUR={AUR} status={p.recurrence_status} />
                </div>
                <div style={{ fontFamily: aurSerif, fontSize: 24, fontWeight: 400, letterSpacing: -0.5, color: AUR.text, marginBottom: 4, lineHeight: 1.15 }}>
                  {ROOT_CAUSE_LABELS[p.root_cause]} in {WORK_TYPE_LABELS[p.work_type]}
                </div>
                <div style={{ color: AUR.textDim, fontSize: 13, lineHeight: 1.55, marginBottom: 16 }}>
                  <strong style={{ color: AUR.text }}>{p.escalation_count} related incidents</strong> · {p.open_count} open · {p.sev1_count} sev1 + {p.sev2_count} sev2 · spans {p.unique_teams} teams across {p.unique_segments} customer segments.
                </div>
                {p.sample_summaries[0] && (
                  <div style={{ fontSize: 12.5, color: AUR.textDim, fontStyle: "italic", borderLeft: `2px solid ${AUR.border}`, paddingLeft: 12, marginBottom: 16, lineHeight: 1.5 }}>"{p.sample_summaries[0]}"</div>
                )}
                <div style={{ display: "grid", gridTemplateColumns: "70px 1fr", gap: "10px 14px", fontSize: 12.5, marginBottom: 14 }}>
                  <span style={{ color: AUR.textFaint, fontFamily: aurMono, fontSize: 10, textTransform: "uppercase", letterSpacing: 0.5 }}>Fix</span>
                  <span style={{ color: AUR.text }}>{fix.fix}</span>
                  <span style={{ color: AUR.textFaint, fontFamily: aurMono, fontSize: 10, textTransform: "uppercase", letterSpacing: 0.5 }}>Owner</span>
                  <span style={{ color: AUR.text }}>{fix.owner}</span>
                  <span style={{ color: AUR.textFaint, fontFamily: aurMono, fontSize: 10, textTransform: "uppercase", letterSpacing: 0.5 }}>Watch</span>
                  <span style={{ color: AUR.text }}>{fix.metric}</span>
                </div>
                <div style={{ padding: "12px 14px", background: AUR.accentGlow, borderRadius: 10, borderLeft: `2px solid ${AUR.accent}` }}>
                  <div style={{ fontFamily: aurMono, fontSize: 10, color: AUR.accent, letterSpacing: 0.6, textTransform: "uppercase", marginBottom: 4 }}>Decision needed this week</div>
                  <div style={{ fontSize: 13, color: AUR.text, lineHeight: 1.45 }}>{decision}</div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </AurSection>
  );
}

function DrilldownTab({ d, AUR, workType, setWorkType }) {
  const wtRollup = d.workTypeRollup.find(r => r.work_type === workType) || d.workTypeRollup[0];
  const teams = d.teams.filter((t) => t.work_type === workType);
  const wtPatterns = d.patterns.filter(p => p.work_type === workType).slice(0, 5);
  const wtEscalations = d.escalations.filter(e => e.work_type === workType);

  // root cause mix for this work type
  const wtRootMix = {};
  wtEscalations.forEach(e => {
    wtRootMix[e.root_cause_category] = (wtRootMix[e.root_cause_category] || 0) + 1;
  });
  const wtRootSorted = Object.entries(wtRootMix).sort((a, b) => b[1] - a[1]);
  const wtRootMax = wtRootSorted[0]?.[1] || 1;

  return (
    <>
      <AurSection
        AUR={AUR}
        eyebrow={`Module A · ${WORK_TYPE_LABELS[workType]} drilldown`}
        title="Team comparison."
        lede="One work type, every team. SLA, CSAT, quality, escalation pressure — read across to find the one team carrying the cluster."
        right={
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            {d.workTypeRollup.map((w) => (
              <button key={w.work_type} onClick={() => setWorkType(w.work_type)} style={{
                background: workType === w.work_type ? AUR.accentGlow : "transparent",
                color: workType === w.work_type ? AUR.accent : AUR.textDim,
                border: `1px solid ${workType === w.work_type ? AUR.accent + "55" : AUR.border}`,
                borderRadius: 999, padding: "6px 14px", fontFamily: aurSans, fontSize: 12.5, cursor: "pointer", fontWeight: 500,
              }}>{WORK_TYPE_LABELS[w.work_type]}</button>
            ))}
          </div>
        }
      >
        {/* Summary tiles */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(6, 1fr)", gap: 12, marginBottom: 18 }}>
          <AurKpi AUR={AUR} label="SLA" value={`${wtRollup.sla.toFixed(1)}%`} sub="target ≥ 92%" status={classifyMetric("sla", wtRollup.sla)} />
          <AurKpi AUR={AUR} label="CSAT" value={wtRollup.csat.toFixed(2)} sub="target ≥ 4.3" status={classifyMetric("csat", wtRollup.csat)} />
          <AurKpi AUR={AUR} label="Quality" value={wtRollup.quality.toFixed(1)} sub="100-pt" status={classifyMetric("quality", wtRollup.quality)} />
          <AurKpi AUR={AUR} label="Esc / 1k" value={wtRollup.escalation_rate_per_1000} sub={`${wtRollup.escalations} total`} status={classifyMetric("escalation_rate", wtRollup.escalation_rate_per_1000)} />
          <AurKpi AUR={AUR} label="Open" value={wtRollup.open_escalations} sub="needs closure" status={classifyMetric("open", wtRollup.open_escalations)} />
          <AurKpi AUR={AUR} label="Sev 1" value={wtRollup.sev1} sub="critical" status={classifyMetric("sev1", wtRollup.sev1)} />
        </div>

        <div style={{ background: AUR.surface, border: `1px solid ${AUR.border}`, borderRadius: 16, overflow: "hidden" }}>
          <div style={{ display: "grid", gridTemplateColumns: "1.8fr 0.8fr 0.5fr 0.6fr 0.6fr 0.6fr 0.6fr 0.6fr", padding: "14px 22px", borderBottom: `1px solid ${AUR.border}`, fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase" }}>
            <div>Team · manager</div><div>City</div><div style={{ textAlign: "right" }}>Heads</div><div style={{ textAlign: "right" }}>SLA</div><div style={{ textAlign: "right" }}>CSAT</div><div style={{ textAlign: "right" }}>Quality</div><div style={{ textAlign: "right" }}>Open</div><div style={{ textAlign: "right" }}>Sev1</div>
          </div>
          {teams.map((t, i, arr) => (
            <div key={t.team_id} style={{ display: "grid", gridTemplateColumns: "1.8fr 0.8fr 0.5fr 0.6fr 0.6fr 0.6fr 0.6fr 0.6fr", padding: "14px 22px", borderBottom: i === arr.length - 1 ? "none" : `1px solid ${AUR.border}`, alignItems: "center", fontSize: 13 }}>
              <div>
                <div style={{ color: AUR.text, fontFamily: aurMono, fontSize: 12 }}>{t.team_id}</div>
                <div style={{ color: AUR.textFaint, fontSize: 12, marginTop: 2 }}>{t.manager} · {t.shift} shift</div>
              </div>
              <div style={{ color: AUR.textDim }}>{t.city}</div>
              <div style={{ textAlign: "right", fontFamily: aurMono, fontVariantNumeric: "tabular-nums" }}>{t.contributors}</div>
              <div style={{ textAlign: "right", fontFamily: aurMono, fontVariantNumeric: "tabular-nums", color: classifyMetric("sla", t.sla) === "good" ? AUR.good : classifyMetric("sla", t.sla) === "warn" ? AUR.warn : AUR.bad }}>{t.sla.toFixed(1)}%</div>
              <div style={{ textAlign: "right", fontFamily: aurMono, fontVariantNumeric: "tabular-nums", color: classifyMetric("csat", t.csat) === "good" ? AUR.good : classifyMetric("csat", t.csat) === "warn" ? AUR.warn : AUR.bad }}>{t.csat.toFixed(1)}</div>
              <div style={{ textAlign: "right", fontFamily: aurMono, fontVariantNumeric: "tabular-nums", color: classifyMetric("quality", t.quality) === "good" ? AUR.good : classifyMetric("quality", t.quality) === "warn" ? AUR.warn : AUR.bad }}>{t.quality.toFixed(1)}</div>
              <div style={{ textAlign: "right", fontFamily: aurMono, fontVariantNumeric: "tabular-nums", color: t.open_escalations > 5 ? AUR.warn : AUR.text }}>{t.open_escalations}</div>
              <div style={{ textAlign: "right", fontFamily: aurMono, fontVariantNumeric: "tabular-nums", color: t.sev1_escalations > 0 ? AUR.bad : AUR.textFaint }}>{t.sev1_escalations}</div>
            </div>
          ))}
        </div>
      </AurSection>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18, marginTop: 32 }}>
        <AurSection AUR={AUR} eyebrow="Delay reasons" title="Why escalations stick.">
          <div style={{ background: AUR.surface, border: `1px solid ${AUR.border}`, borderRadius: 14, padding: 20 }}>
            <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase", marginBottom: 12 }}>Root-cause mix · {wtEscalations.length} escalations</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {wtRootSorted.map(([rc, c]) => (
                <div key={rc} style={{ display: "grid", gridTemplateColumns: "180px 1fr 30px", gap: 10, alignItems: "center" }}>
                  <span style={{ fontSize: 12.5, color: AUR.text }}>{ROOT_CAUSE_LABELS[rc] || rc}</span>
                  <div style={{ height: 6, background: AUR.surfaceHi, borderRadius: 3, overflow: "hidden" }}>
                    <div style={{ width: `${(c / wtRootMax) * 100}%`, height: "100%", background: `linear-gradient(90deg, ${AUR.accent}, ${AUR.accentDeep})` }} />
                  </div>
                  <span style={{ fontFamily: aurMono, fontSize: 12, color: AUR.text, fontVariantNumeric: "tabular-nums", textAlign: "right" }}>{c}</span>
                </div>
              ))}
            </div>
          </div>
        </AurSection>

        <AurSection AUR={AUR} eyebrow="Top patterns in this work type" title="What's recurring.">
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {wtPatterns.map(p => (
              <div key={p.pattern_id} style={{ background: AUR.surface, border: `1px solid ${AUR.border}`, borderRadius: 12, padding: "12px 16px", display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12 }}>
                <div style={{ minWidth: 0, flex: 1 }}>
                  <div style={{ fontFamily: aurSerif, fontSize: 16, color: AUR.text, lineHeight: 1.2 }}>{ROOT_CAUSE_LABELS[p.root_cause]}</div>
                  <div style={{ fontFamily: aurMono, fontSize: 11, color: AUR.textFaint, marginTop: 2 }}>{p.escalation_count} esc · {p.open_count} open · score {p.risk_score}</div>
                </div>
                <AurStatusPill AUR={AUR} status={p.recurrence_status} />
                <AurRiskBadge AUR={AUR} level={p.risk_level} />
              </div>
            ))}
          </div>
        </AurSection>
      </div>
    </>
  );
}

// ─── Modals ────────────────────────────────────────────────────────────────

function BriefingModal({ d, k, AUR, onClose }) {
  return (
    <div style={{ position: "fixed", inset: 0, background: "rgba(10,10,18,0.85)", display: "grid", placeItems: "center", padding: 32, zIndex: 100, backdropFilter: "blur(8px)" }} onClick={onClose}>
      <div onClick={(e) => e.stopPropagation()} style={{ background: AUR.bg, border: `1px solid ${AUR.borderHi}`, borderRadius: 18, padding: 36, maxWidth: 820, width: "100%", maxHeight: "90vh", overflow: "auto" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20 }}>
          <div>
            <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 1.2, textTransform: "uppercase", marginBottom: 6 }}>Weekly Ops Briefing · APAC</div>
            <div style={{ fontFamily: aurSerif, fontSize: 32, fontWeight: 400, letterSpacing: -0.7 }}>Week of {d.weekStart} → {d.refDate}</div>
          </div>
          <button onClick={onClose} style={{ background: "transparent", border: `1px solid ${AUR.border}`, color: AUR.text, fontFamily: aurSans, fontSize: 12.5, padding: "6px 14px", borderRadius: 999, cursor: "pointer" }}>Close</button>
        </div>
        <div style={{ color: AUR.textDim, fontSize: 14, lineHeight: 1.7 }}>
          <p><span style={{ color: AUR.accent, fontFamily: aurMono, fontSize: 10.5, letterSpacing: 0.6, textTransform: "uppercase" }}>Headline</span><br /> Region SLA at {fmt.pct(k.sla_adherence)}, CSAT 7-day at {fmt.dec(k.csat_7d, 2)}. {d.totals.escalations} escalations this period · {d.totals.open} open · {d.totals.sev1} sev1.</p>
          <p style={{ marginTop: 18 }}><span style={{ color: AUR.accent, fontFamily: aurMono, fontSize: 10.5, letterSpacing: 0.6, textTransform: "uppercase" }}>Top 3 anomalies</span></p>
          <ol style={{ paddingLeft: 22, color: AUR.text }}>
            {d.patterns.slice(0, 3).map((p) => (
              <li key={p.pattern_id} style={{ marginBottom: 6 }}>
                <strong>{ROOT_CAUSE_LABELS[p.root_cause]} in {WORK_TYPE_LABELS[p.work_type]} · {p.recurrence_status.toLowerCase()}.</strong>{" "}
                {p.escalation_count} escalations · {p.open_count} open · {p.sev1_count} sev1. {ROOT_CAUSE_DECISION[p.root_cause] || "Assign owner + prevention plan"}.
              </li>
            ))}
          </ol>
          <p style={{ marginTop: 18 }}><span style={{ color: AUR.accent, fontFamily: aurMono, fontSize: 10.5, letterSpacing: 0.6, textTransform: "uppercase" }}>Recurring themes (Module B)</span><br /> {Object.entries(d.rootCauseCounts).sort((a,b)=>b[1]-a[1]).slice(0,4).map(([k,v]) => `${ROOT_CAUSE_LABELS[k] || k} (${v})`).join(", ")}.</p>
          <p style={{ marginTop: 18 }}><span style={{ color: AUR.accent, fontFamily: aurMono, fontSize: 10.5, letterSpacing: 0.6, textTransform: "uppercase" }}>Decisions this week</span><br /> {d.patterns.slice(0, 3).map((p) => `${ROOT_CAUSE_DECISION[p.root_cause] || "Assign owner + prevention plan"} (${WORK_TYPE_LABELS[p.work_type]})`).join(". ")}.</p>
        </div>
        <div style={{ display: "flex", gap: 8, marginTop: 24 }}>
          <button style={{ background: AUR.accent, color: "#1a0033", border: "none", borderRadius: 999, padding: "8px 16px", fontFamily: aurSans, fontSize: 12.5, fontWeight: 500, cursor: "pointer" }}>Download Markdown</button>
          <button style={{ background: "transparent", color: AUR.text, border: `1px solid ${AUR.border}`, borderRadius: 999, padding: "8px 16px", fontFamily: aurSans, fontSize: 12.5, cursor: "pointer" }}>Share to leadership</button>
        </div>
      </div>
    </div>
  );
}

function AboutModal({ AUR, onClose }) {
  return (
    <div style={{ position: "fixed", inset: 0, background: "rgba(10,10,18,0.85)", display: "grid", placeItems: "center", padding: 32, zIndex: 100, backdropFilter: "blur(8px)" }} onClick={onClose}>
      <div onClick={(e) => e.stopPropagation()} style={{ background: AUR.bg, border: `1px solid ${AUR.borderHi}`, borderRadius: 18, padding: 40, maxWidth: 760, width: "100%", maxHeight: "90vh", overflow: "auto" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
          <div>
            <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 1.2, textTransform: "uppercase", marginBottom: 6 }}>About this prototype</div>
            <div style={{ fontFamily: aurSerif, fontSize: 36, fontWeight: 400, letterSpacing: -0.9, lineHeight: 1.1 }}>A 60-day operating view, built for the interview.</div>
          </div>
          <button onClick={onClose} style={{ background: "transparent", border: `1px solid ${AUR.border}`, color: AUR.text, fontFamily: aurSans, fontSize: 12.5, padding: "6px 14px", borderRadius: 999, cursor: "pointer", flexShrink: 0 }}>Close</button>
        </div>
        <div style={{ color: AUR.textDim, fontSize: 15, lineHeight: 1.75 }}>
          <p>Two real ops problems sit underneath this dashboard:</p>
          <p style={{ marginTop: 16 }}><span style={{ color: AUR.accent, fontFamily: aurMono, fontSize: 11, letterSpacing: 0.6, textTransform: "uppercase" }}>Module A</span><br /> Regional Ops Command Center. A single view across SLA, backlog, CSAT, quality and escalation risk — sized for a regional manager's morning check-in, not an analytics audit. The goal is to compress what used to take three dashboards into one frame, with anomalies bubbled to the top and a one-click weekly briefing.</p>
          <p style={{ marginTop: 16 }}><span style={{ color: AUR.accent, fontFamily: aurMono, fontSize: 11, letterSpacing: 0.6, textTransform: "uppercase" }}>Module B</span><br /> Escalation Pattern Recurrence Detector. Most ops dashboards count escalations; this one detects when the <em>same operational breakdown</em> is happening over and over. Patterns are scored deterministically — escalation count, severity, open volume, segment spread, slow-resolution penalty, acceleration bonus — and the highest-risk ones become structural fix cards with an owner, a watch metric, and a weekly decision.</p>
          <p style={{ marginTop: 16 }}><span style={{ color: AUR.accent, fontFamily: aurMono, fontSize: 11, letterSpacing: 0.6, textTransform: "uppercase" }}>Module B v2</span><br /> Semantic clusters. Different teams describe the same breakdown in different words. TF-IDF + cosine similarity finds repeat themes that don't share a root-cause label, so the fix cards capture <em>true</em> recurrence — not just label collisions.</p>
          <p style={{ marginTop: 16 }}><span style={{ color: AUR.accent, fontFamily: aurMono, fontSize: 11, letterSpacing: 0.6, textTransform: "uppercase" }}>How this was built</span><br /> The Streamlit version (in the GitHub repo) is the working backend. This is the operating front for it: how a regional lead actually wants to land in the morning, not a dashboarding tool. The 250-escalation APAC dataset is generated by the repo's data pipeline; the SLA/CSAT/quality numbers are synthesized but anchored to escalation pressure per team.</p>
        </div>
      </div>
    </div>
  );
}

// ─── Top-level ─────────────────────────────────────────────────────────────

function AuroraDashboard({ data, scenario, setScenario, loading, region, accent = "#B79DFF", showAbout, setShowAbout }) {
  const [tab, setTab] = React.useState("overview");
  const [showBriefing, setShowBriefing] = React.useState(false);
  const [workType, setWorkType] = React.useState("expert_review");
  const [selectedPatternId, setSelectedPatternId] = React.useState(null);
  const [statusFilter, setStatusFilter] = React.useState("all");
  const [riskFilter, setRiskFilter] = React.useState("all");
  const AUR = React.useMemo(() => buildAurTheme(accent), [accent]);

  // The fetched payload is already the scenario's real pipeline data, so use
  // it directly — no synthetic applyScenario() transform.
  const d = data;
  if (!d) return <div style={{ padding: 40, color: AUR.textDim, fontFamily: aurSans }}>Loading…</div>;
  const k = d.kpis;

  return (
    <div style={{
      minHeight: "100vh",
      background: AUR.bg,
      color: AUR.text,
      fontFamily: aurSans,
      padding: "36px 48px 72px",
      boxSizing: "border-box",
      position: "relative", overflow: "hidden",
      fontSize: 14,
    }}>
      <div style={{ position: "fixed", top: -200, right: -200, width: 700, height: 700, borderRadius: "50%", background: `radial-gradient(circle, ${AUR.accent}30 0%, transparent 65%)`, pointerEvents: "none", zIndex: 0 }} />
      <div style={{ position: "fixed", bottom: -300, left: -150, width: 800, height: 800, borderRadius: "50%", background: `radial-gradient(circle, ${AUR.good}15 0%, transparent 60%)`, pointerEvents: "none", zIndex: 0 }} />

      <div style={{ position: "relative", zIndex: 1, maxWidth: 1480, margin: "0 auto" }}>
        {/* Header */}
        <header style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 32, gap: 24 }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 14 }}>
              <div style={{ width: 34, height: 34, borderRadius: 9, background: `linear-gradient(135deg, ${AUR.accent}, ${AUR.accentDeep})`, display: "grid", placeItems: "center", fontFamily: aurSerif, fontSize: 19, color: AUR.bg }}>S</div>
              <div style={{ fontFamily: aurMono, fontSize: 11, color: AUR.textDim, letterSpacing: 0.6, textTransform: "uppercase" }}>Scale · Regional Ops</div>
              <AurChip AUR={AUR} color={AUR.good}><span style={{ width: 6, height: 6, borderRadius: "50%", background: AUR.good, boxShadow: `0 0 8px ${AUR.good}` }} />Live</AurChip>
              <AurChip AUR={AUR}>{region}</AurChip>
              <AurChip AUR={AUR}>Week of {d.weekStart} → {d.refDate}</AurChip>
            </div>
            {d.generated_at && (
              <div style={{ fontFamily: aurMono, fontSize: 10, color: AUR.textFaint, letterSpacing: 0.4, marginBottom: 12 }}>
                Pipeline: {d.scenario} · {d.generated_at}
              </div>
            )}
            <h1 style={{ fontFamily: aurSerif, fontSize: 42, fontWeight: 400, letterSpacing: -1.4, margin: 0, lineHeight: 1.05, maxWidth: 880 }}>
              The operating system <em style={{ color: AUR.accent, fontStyle: "italic" }}>before</em> customer impact lands.
            </h1>
            <p style={{ fontFamily: aurSans, fontSize: 15, color: AUR.textDim, marginTop: 12, maxWidth: 720, lineHeight: 1.5 }}>
              One regional view across SLA, backlog, CSAT, quality and escalation risk — with deterministic recurrence detection on every escalation.
            </p>
          </div>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 12 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ fontFamily: aurMono, fontSize: 10, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase" }}>
                Scenario{loading ? " · loading…" : ""}
              </span>
              <div style={{ display: "flex", gap: 4, padding: 4, background: AUR.surface, border: `1px solid ${AUR.border}`, borderRadius: 999 }}>
                {[
                  { id: "healthy", label: "Healthy" },
                  { id: "current", label: "Current" },
                  { id: "crisis", label: "Crisis" },
                ].map((s) => (
                  <button key={s.id} onClick={() => setScenario && setScenario(s.id)} style={{
                    background: scenario === s.id ? AUR.accent : "transparent",
                    color: scenario === s.id ? "#1a0033" : AUR.textDim,
                    border: "none", borderRadius: 999, padding: "6px 14px",
                    fontFamily: aurSans, fontSize: 12, fontWeight: 500, cursor: "pointer",
                    transition: "all 180ms ease",
                  }}>{s.label}</button>
                ))}
              </div>
            </div>
            <AurButton AUR={AUR} variant="primary" onClick={() => setShowBriefing(true)}>Generate weekly briefing →</AurButton>
          </div>
        </header>

        {/* Tab nav */}
        <nav style={{ display: "flex", gap: 4, padding: 4, background: AUR.surface, border: `1px solid ${AUR.border}`, borderRadius: 999, width: "fit-content", marginBottom: 24 }}>
          {[
            { id: "overview", label: "Health overview" },
            { id: "patterns", label: "Pattern detector" },
            { id: "clusters", label: "Semantic clusters" },
            { id: "drilldown", label: "Work-type drilldown" },
          ].map((t) => (
            <button key={t.id} onClick={() => setTab(t.id)} style={{
              background: tab === t.id ? AUR.accent : "transparent",
              color: tab === t.id ? "#1a0033" : AUR.textDim,
              border: "none",
              borderRadius: 999,
              padding: "8px 18px",
              fontFamily: aurSans,
              fontSize: 13,
              fontWeight: 500,
              cursor: "pointer",
              transition: "all 180ms ease",
            }}>{t.label}</button>
          ))}
        </nav>

        {/* KPI strip — always visible */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14 }}>
          <AurKpi AUR={AUR} large label="SLA Adherence" value={fmt.pct(k.sla_adherence)} sub="target ≥ 95.0%" status={classifyMetric("sla", k.sla_adherence)} trendData={d.kpiTrends.sla} />
          <AurKpi AUR={AUR} large label="CSAT · 7-day" value={fmt.dec(k.csat_7d, 2)} sub="target ≥ 4.40" status={classifyMetric("csat", k.csat_7d)} trendData={d.kpiTrends.csat} />
          <AurKpi AUR={AUR} large label="Backlog" value={fmt.num(k.backlog)} sub={`${k.aged_backlog_72h} aged >72h`} status={k.aged_backlog_72h > 800 ? "bad" : "warn"} trendData={d.kpiTrends.backlog} />
          <AurKpi AUR={AUR} large label="Avg Quality" value={fmt.dec(k.avg_quality)} sub={`100-pt · rework ${k.rework_rate.toFixed(1)}%`} status={classifyMetric("quality", k.avg_quality)} trendData={d.kpiTrends.quality} />
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14, marginTop: 14 }}>
          <AurKpi AUR={AUR} label="Escalation rate / 1k" value={fmt.dec(k.escalation_rate_per_1000, 1)} sub="target ≤ 8" status={classifyMetric("escalation_rate", k.escalation_rate_per_1000)} trendData={d.kpiTrends.esc_rate} />
          <AurKpi AUR={AUR} label="FCR proxy" value={fmt.pct(k.fcr_proxy)} sub="1st-pass resolved" status={k.fcr_proxy > 88 ? "good" : "warn"} trendData={d.kpiTrends.fcr} />
          <AurKpi AUR={AUR} label="Open escalations" value={d.totals.open} sub={`${d.totals.sev1} sev1 · ${d.totals.sev2} sev2`} status={d.totals.sev1 > 5 ? "bad" : d.totals.sev1 > 2 ? "warn" : "good"} />
          <AurKpi AUR={AUR} label="Recurring patterns" value={d.patterns.filter((p) => ["Recurring", "Accelerating"].includes(p.recurrence_status)).length} sub={`${d.patterns.filter((p) => p.risk_level === "High").length} high-risk · ${d.patterns.filter((p) => p.recurrence_status === "Accelerating").length} accelerating`} status="warn" />
        </div>

        {/* Tab content */}
        {tab === "overview" && <OverviewTab d={d} k={k} AUR={AUR} onJumpToWorkType={(wt) => { setWorkType(wt); setTab("drilldown"); }} onJumpToPatterns={() => setTab("patterns")} />}
        {tab === "patterns" && <PatternsTab d={d} AUR={AUR} selectedPatternId={selectedPatternId} setSelectedPatternId={setSelectedPatternId} statusFilter={statusFilter} setStatusFilter={setStatusFilter} riskFilter={riskFilter} setRiskFilter={setRiskFilter} />}
        {tab === "clusters" && <ClustersTab d={d} AUR={AUR} />}
        {tab === "drilldown" && <DrilldownTab d={d} AUR={AUR} workType={workType} setWorkType={setWorkType} />}
      </div>

      {showBriefing && <BriefingModal d={d} k={k} AUR={AUR} onClose={() => setShowBriefing(false)} />}
      {showAbout && <AboutModal AUR={AUR} onClose={() => setShowAbout(false)} />}
    </div>
  );
}

Object.assign(window, { AuroraDashboard, buildAurTheme, aurSans, aurSerif, aurMono });
