// Module D · Capacity & SLA Forecasting — 3-level progressive disclosure.
// L1: region forecast · L2 (?wt=X): work-type capacity · L3 (?wt=X&tm=Y): team load
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useDash } from "@/dashboards/app-context";
// @ts-expect-error jsx
import { Breadcrumb, ThreadNav, PillRow, Panel, AurRiskBadge, ForecastPill, DriverBars, AurChip, aurMono, aurSerif } from "@/dashboards/atoms.jsx";
// @ts-expect-error jsx
import { deriveCapacity, WORK_TYPE_LABELS, classifyMetric, fmt } from "@/dashboards/data-utils.jsx";
import { Loading } from "./_dash.index";

export const Route = createFileRoute("/_dash/capacity")({
  head: () => ({ meta: [
    { title: "Capacity & SLA Forecast · Scale Ops" },
    { name: "description", content: "Module D: SLA forecast, backlog pressure and staffing gap per work type and team." },
  ]}),
  component: Capacity,
});

function Capacity() {
  const { data, AUR } = useDash();
  const { wt, tm } = Route.useSearch() as any;
  if (!data) return <Loading AUR={AUR} />;
  const cap = deriveCapacity(data);
  if (tm) return <TeamLevel cap={cap} tm={tm} AUR={AUR} />;
  if (wt) return <WorkTypeLevel data={data} cap={cap} wt={wt} AUR={AUR} />;
  return <Overview cap={cap} AUR={AUR} />;
}

const statusColor = (AUR: any, s: string) => s === "good" ? AUR.good : s === "warn" ? AUR.warn : s === "bad" ? AUR.bad : AUR.text;

// ─── L1 · Region forecast ───────────────────────────────────────────────────
function Overview({ cap, AUR }: any) {
  const { densityPreset } = useDash();
  const stats = [
    { label: "Open backlog", value: fmt.num(cap.region.backlog), sub: `${cap.region.agedShare}% aged >72h`, status: cap.region.agedShare > 50 ? "bad" : cap.region.agedShare > 20 ? "warn" : "good" },
    { label: "At SLA risk", value: String(cap.region.atRisk), sub: "work types next week", status: cap.region.atRisk > 2 ? "bad" : cap.region.atRisk ? "warn" : "good" },
    { label: "Head gap", value: cap.region.totalHeadGap > 0 ? `+${cap.region.totalHeadGap}` : "0", sub: "trained heads short", status: cap.region.totalHeadGap > 12 ? "bad" : cap.region.totalHeadGap ? "warn" : "good" },
    { label: "Region SLA", value: fmt.pct(cap.region.avgSla), sub: "target ≥ 95%", status: classifyMetric("sla", cap.region.avgSla) },
  ];

  return (
    <>
      <Breadcrumb AUR={AUR} items={[{ label: "Module D · Capacity & SLA" }]} />
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", gap: 24, flexWrap: "wrap" }}>
        <div>
          <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 0.8, textTransform: "uppercase", marginBottom: 10 }}>Module D · Capacity & SLA</div>
          <h1 style={{ fontFamily: aurSerif, fontSize: 36, fontWeight: 400, letterSpacing: -1, margin: 0, lineHeight: 1.1, color: AUR.text }}>Will the region hold SLA next week?</h1>
          <p style={{ color: AUR.textDim, fontSize: 14, marginTop: 12, maxWidth: 720, lineHeight: 1.6 }}>
            Backlog, inflow, throughput, complexity and contributor availability become an early-warning view — so managers can rebalance, cross-train or add coverage before customer impact lands.
          </p>
        </div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <AurChip AUR={AUR} color={AUR.good}><span style={{ width: 6, height: 6, borderRadius: "50%", background: AUR.good }} />Stable</AurChip>
          <AurChip AUR={AUR} color={AUR.warn}><span style={{ width: 6, height: 6, borderRadius: "50%", background: AUR.warn }} />Watchlist</AurChip>
          <AurChip AUR={AUR} color={AUR.bad}><span style={{ width: 6, height: 6, borderRadius: "50%", background: AUR.bad }} />At risk</AurChip>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginTop: 22 }}>
        {stats.map((s, i) => <SummaryTile key={i} AUR={AUR} {...s} />)}
      </div>

      <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase", marginTop: densityPreset.sectionGap, marginBottom: 16 }}>Capacity & SLA forecast by work type</div>
      <Panel AUR={AUR} pad={0} style={{ overflow: "hidden" }}>
        <div style={{ display: "grid", gridTemplateColumns: "1.5fr 1.1fr 0.7fr 0.8fr 1fr 0.7fr 28px", padding: "16px 22px", borderBottom: `1px solid ${AUR.border}` }}>
          {["Work type","Utilization","SLA now","Proj.","Forecast","Risk",""].map((h, i) => (
            <span key={i} style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase", textAlign: (i >= 2 && i <= 3) ? "right" : "left" }}>{h}</span>
          ))}
        </div>
        {cap.byWorkType.map((w: any, i: number) => (
          <Link key={w.work_type} to="/capacity" search={((prev: any) => ({ ...prev, wt: w.work_type, tm: undefined })) as any}
            style={{
              display: "grid", gridTemplateColumns: "1.5fr 1.1fr 0.7fr 0.8fr 1fr 0.7fr 28px",
              padding: "18px 22px", borderBottom: i === cap.byWorkType.length - 1 ? "none" : `1px solid ${AUR.border}`,
              alignItems: "center", textDecoration: "none", color: AUR.text,
            }}>
            <div>
              <div style={{ fontFamily: aurSerif, fontSize: 18, color: AUR.text, letterSpacing: -0.3 }}>{WORK_TYPE_LABELS[w.work_type]}</div>
              <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, marginTop: 3 }}>{w.contributors} heads · {w.backlogPressure}wk backlog{w.headGap > 0 ? ` · short ${w.headGap}` : ""}</div>
            </div>
            <div style={{ paddingRight: 18 }}>
              <div style={{ height: 6, background: AUR.surfaceHi, borderRadius: 6, overflow: "hidden" }}>
                <div style={{ width: `${Math.min(100, (w.utilization / 140) * 100)}%`, height: "100%", background: w.utilization > 110 ? AUR.bad : w.utilization > 100 ? AUR.warn : AUR.good }} />
              </div>
              <div style={{ fontFamily: aurMono, fontSize: 10, color: AUR.textFaint, marginTop: 5 }}>{w.utilization}% util</div>
            </div>
            <span style={{ fontFamily: aurMono, fontSize: 12.5, color: statusColor(AUR, classifyMetric("sla", w.sla)), textAlign: "right" }}>{w.sla.toFixed(1)}</span>
            <span style={{ fontFamily: aurMono, fontSize: 12.5, color: w.projected < 90 ? AUR.bad : w.projected < 95 ? AUR.warn : AUR.good, textAlign: "right" }}>{w.projected}</span>
            <ForecastPill AUR={AUR} forecast={w.forecast} />
            <AurRiskBadge AUR={AUR} level={w.riskLevel} />
            <span style={{ color: AUR.textFaint, textAlign: "right", fontSize: 15 }}>→</span>
          </Link>
        ))}
      </Panel>

      <div style={{ marginTop: densityPreset.sectionGap, padding: "14px 16px", background: AUR.accentSoft, borderRadius: 12, borderLeft: `2px solid ${AUR.accent}` }}>
        <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 0.6, textTransform: "uppercase", marginBottom: 5 }}>Operating principle</div>
        <div style={{ fontSize: 13, color: AUR.textDim, lineHeight: 1.5 }}>A capacity-planning, workload-balancing and SLA-protection system — not a productivity-surveillance tool.</div>
      </div>

      <ThreadNav AUR={AUR} density={densityPreset} items={[
        { kicker: "Module A", title: "Where is SLA breaking", hint: "Health board across work types.", to: "/health" },
        { kicker: "Module B", title: "What keeps escalating", hint: "Pattern detector and structural fixes.", to: "/patterns" },
        { kicker: "Module C", title: "Is quality drifting too", hint: "When capacity strains, quality slips first.", to: "/workforce" },
      ]} />
    </>
  );
}

// ─── L2 · Work-type ─────────────────────────────────────────────────────────
function WorkTypeLevel({ data, cap, wt, AUR }: any) {
  const { densityPreset } = useDash();
  const navigate = useNavigate();
  const w = cap.byWorkType.find((x: any) => x.work_type === wt);
  if (!w) return <div style={{ padding: 40, color: AUR.textFaint, textAlign: "center", fontStyle: "italic" }}>Work type not found.</div>;
  const teams = cap.teams.filter((t: any) => t.work_type === wt).sort((a: any, b: any) => b.riskScore - a.riskScore);

  const tiles = [
    { label: "SLA now",      value: `${w.sla.toFixed(1)}%`, status: classifyMetric("sla", w.sla) },
    { label: "Proj. next wk",value: `${w.projected}%`, status: w.projected < 90 ? "bad" : w.projected < 95 ? "warn" : "good" },
    { label: "Utilization",  value: `${w.utilization}%`, status: w.utilization > 110 ? "bad" : w.utilization > 100 ? "warn" : "good" },
    { label: "Backlog",      value: `${w.backlogPressure}wk`, sub: `${fmt.num(w.backlog)} items`, status: w.backlogPressure > 1.5 ? "bad" : w.backlogPressure > 1 ? "warn" : "good" },
    { label: "Inflow / wk",  value: fmt.num(w.inflow), sub: `vs ${fmt.num(w.throughput)} done`, status: w.inflow > w.throughput ? "warn" : "good" },
    { label: "Head gap",     value: w.headGap > 0 ? `+${w.headGap}` : "0", sub: w.headGap > 0 ? "to clear load" : "balanced", status: w.headGap > 4 ? "bad" : w.headGap > 0 ? "warn" : "good" },
  ];

  return (
    <>
      <Breadcrumb AUR={AUR} items={[
        { label: "Module D · Capacity & SLA", to: "/capacity", search: ((prev: any) => ({ ...prev, wt: undefined, tm: undefined })) },
        { label: WORK_TYPE_LABELS[wt] },
      ]} />
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", gap: 24, flexWrap: "wrap" }}>
        <div>
          <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 0.8, textTransform: "uppercase", marginBottom: 10 }}>Module D · {WORK_TYPE_LABELS[wt]}</div>
          <h1 style={{ fontFamily: aurSerif, fontSize: 36, fontWeight: 400, letterSpacing: -1, margin: 0, lineHeight: 1.1, color: AUR.text }}>Capacity outlook & SLA forecast.</h1>
          <p style={{ color: AUR.textDim, fontSize: 14, marginTop: 12, maxWidth: 720, lineHeight: 1.6 }}>
            {w.complexity}% of this queue is high-complexity work. The forecast and risk score below are built from backlog, utilization, SLA trend and quality + escalation overlays.
          </p>
        </div>
        <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap", maxWidth: 540 }}>
          <PillRow AUR={AUR} options={data.workTypeRollup.map((r: any) => r.work_type)} value={wt}
            onChange={(v: string) => navigate({ to: "/capacity", search: ((prev: any) => ({ ...prev, wt: v, tm: undefined })) as any })}
            getLabel={(o: string) => WORK_TYPE_LABELS[o]} />
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(6, 1fr)", gap: 12, marginTop: 22 }}>
        {tiles.map((s, i) => <SummaryTile key={i} AUR={AUR} {...s} />)}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginTop: densityPreset.sectionGap }}>
        <Panel AUR={AUR}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 18 }}>
            <span style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase" }}>Capacity risk breakdown</span>
            <span style={{ fontFamily: aurSerif, fontSize: 34, color: w.riskLevel === "High" ? AUR.bad : w.riskLevel === "Medium" ? AUR.warn : AUR.text }}>{w.riskScore}</span>
          </div>
          <DriverBars AUR={AUR} drivers={w.drivers} max={6} />
        </Panel>

        <Panel AUR={AUR} glow accentEdge style={{ display: "flex", flexDirection: "column" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
            <span style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 0.8, textTransform: "uppercase" }}>Recommended capacity action</span>
            <ForecastPill AUR={AUR} forecast={w.forecast} />
          </div>
          <div style={{ fontFamily: aurSerif, fontSize: 24, color: AUR.text, letterSpacing: -0.4, lineHeight: 1.25, marginBottom: 16 }}>{w.action}.</div>
          <div style={{ display: "grid", gridTemplateColumns: "84px 1fr", gap: "11px 16px", fontSize: 13.5, marginTop: "auto" }}>
            <span style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, textTransform: "uppercase", letterSpacing: 0.5 }}>Owner</span><span style={{ color: AUR.text }}>Workforce planning lead + {WORK_TYPE_LABELS[wt]} managers</span>
            <span style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, textTransform: "uppercase", letterSpacing: 0.5 }}>Watch</span><span style={{ color: AUR.text }}>SLA adherence · aged backlog · utilization</span>
            <span style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, textTransform: "uppercase", letterSpacing: 0.5 }}>Decision</span><span style={{ color: AUR.accent }}>{w.headGap > 0 ? `Approve +${w.headGap} heads / surge coverage this week` : "Approve load rebalance + cross-training plan"}</span>
          </div>
        </Panel>
      </div>

      <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase", marginTop: densityPreset.sectionGap, marginBottom: 16 }}>Team load · {WORK_TYPE_LABELS[wt]}</div>
      <Panel AUR={AUR} pad={0} style={{ overflow: "hidden" }}>
        <div style={{ display: "grid", gridTemplateColumns: "1.5fr 1.2fr 0.7fr 0.8fr 1.1fr 0.7fr 28px", padding: "16px 22px", borderBottom: `1px solid ${AUR.border}` }}>
          {["Team · manager","Utilization","SLA","Backlog","Flag","Risk",""].map((h, i) => (
            <span key={i} style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase", textAlign: (i >= 2 && i <= 3) ? "right" : "left" }}>{h}</span>
          ))}
        </div>
        {teams.map((t: any, i: number) => (
          <Link key={t.team_id} to="/capacity" search={((prev: any) => ({ ...prev, wt, tm: t.team_id })) as any}
            style={{
              display: "grid", gridTemplateColumns: "1.5fr 1.2fr 0.7fr 0.8fr 1.1fr 0.7fr 28px",
              padding: "16px 22px", borderBottom: i === teams.length - 1 ? "none" : `1px solid ${AUR.border}`,
              alignItems: "center", textDecoration: "none", color: AUR.text,
            }}>
            <div>
              <span style={{ fontFamily: aurMono, fontSize: 12, color: AUR.text }}>{t.team_id.replace("TEAM_APAC_", "")}</span>
              <div style={{ fontSize: 11.5, color: AUR.textFaint, marginTop: 2 }}>{t.manager} · {t.contributors} heads · {t.shift}</div>
            </div>
            <div style={{ paddingRight: 18 }}>
              <div style={{ height: 6, background: AUR.surfaceHi, borderRadius: 6, overflow: "hidden" }}>
                <div style={{ width: `${Math.min(100, (t.utilization / 140) * 100)}%`, height: "100%", background: t.utilization > 110 ? AUR.bad : t.utilization > 100 ? AUR.warn : AUR.good }} />
              </div>
              <div style={{ fontFamily: aurMono, fontSize: 10, color: AUR.textFaint, marginTop: 5 }}>{t.utilization}%</div>
            </div>
            <span style={{ fontFamily: aurMono, fontSize: 12.5, color: statusColor(AUR, classifyMetric("sla", t.sla)), textAlign: "right" }}>{t.sla.toFixed(1)}</span>
            <span style={{ fontFamily: aurMono, fontSize: 12.5, color: AUR.text, textAlign: "right" }}>{fmt.num(t.backlog)}</span>
            <span style={{ fontSize: 11, color: t.lowTenureHighComplex ? AUR.warn : AUR.textFaint }}>{t.lowTenureHighComplex ? "junior ↔ complex" : "—"}</span>
            <AurRiskBadge AUR={AUR} level={t.riskLevel} />
            <span style={{ color: AUR.textFaint, textAlign: "right", fontSize: 15 }}>→</span>
          </Link>
        ))}
      </Panel>

      <ThreadNav AUR={AUR} density={densityPreset} items={[
        { kicker: "Module A", title: "Health for this work type", hint: `SLA, CSAT and escalations for ${WORK_TYPE_LABELS[wt]}.`, to: "/health", search: ((prev: any) => ({ ...prev, wt, tm: undefined })) },
        { kicker: "Module C", title: "Is quality slipping under load", hint: "Quality risk often trails capacity strain.", to: "/workforce", search: ((prev: any) => ({ ...prev, wt, tm: undefined })) },
        { kicker: "Module B", title: "Recurring escalations here", hint: "Capacity shortfalls show up as repeat patterns.", to: "/patterns", search: ((prev: any) => ({ ...prev, wt, tm: undefined, pid: undefined })) },
      ]} />
    </>
  );
}

// ─── L3 · Team ──────────────────────────────────────────────────────────────
function TeamLevel({ cap, tm, AUR }: any) {
  const { densityPreset } = useDash();
  const t = cap.teams.find((x: any) => x.team_id === tm);
  if (!t) return <div style={{ padding: 40, color: AUR.textFaint, textAlign: "center", fontStyle: "italic" }}>Team not found.</div>;
  const tiles = [
    { label: "Utilization", value: `${t.utilization}%`, status: t.utilization > 110 ? "bad" : t.utilization > 100 ? "warn" : "good" },
    { label: "SLA",         value: `${t.sla.toFixed(1)}%`, status: classifyMetric("sla", t.sla) },
    { label: "Backlog",     value: fmt.num(t.backlog), sub: "assigned items" },
    { label: "Throughput",  value: fmt.num(t.throughput), sub: "items / wk" },
    { label: "Open esc",    value: String(t.openEsc), status: classifyMetric("open", t.openEsc) },
  ];
  const action = t.utilization > 110 ? "Rebalance overflow to a lower-utilization team or add surge coverage"
    : t.lowTenureHighComplex ? "Pair junior contributors with seniors on complex work; stage a ramp plan"
    : t.riskLevel === "High" ? "Protect SLA: triage aged items and add a focused clear-down block"
    : "Hold — capacity is balanced for the current load";

  return (
    <>
      <Breadcrumb AUR={AUR} items={[
        { label: "Module D · Capacity & SLA", to: "/capacity", search: ((prev: any) => ({ ...prev, wt: undefined, tm: undefined })) },
        { label: WORK_TYPE_LABELS[t.work_type], to: "/capacity", search: ((prev: any) => ({ ...prev, wt: t.work_type, tm: undefined })) },
        { label: t.team_id.replace("TEAM_APAC_", "") },
      ]} />
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", gap: 24, flexWrap: "wrap" }}>
        <div>
          <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 0.8, textTransform: "uppercase", marginBottom: 10 }}>{WORK_TYPE_LABELS[t.work_type]} · {t.city} · {t.shift} shift</div>
          <h1 style={{ fontFamily: aurSerif, fontSize: 36, fontWeight: 400, letterSpacing: -1, margin: 0, lineHeight: 1.1, color: AUR.text }}>{t.manager}'s team · capacity load</h1>
          <p style={{ color: AUR.textDim, fontSize: 14, marginTop: 12, maxWidth: 720, lineHeight: 1.6 }}>
            {t.contributors} contributors carrying {fmt.num(t.backlog)} items at {t.utilization}% utilization.{t.lowTenureHighComplex ? " Junior contributors are absorbing complex work here — a quality-risk flag, not just a capacity one." : ""}
          </p>
        </div>
        <AurRiskBadge AUR={AUR} level={t.riskLevel} />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 12, marginTop: 22 }}>
        {tiles.map((s, i) => <SummaryTile key={i} AUR={AUR} {...s} />)}
      </div>

      <Panel AUR={AUR} glow accentEdge style={{ marginTop: densityPreset.sectionGap }}>
        <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 0.8, textTransform: "uppercase", marginBottom: 12 }}>Recommended action</div>
        <div style={{ fontFamily: aurSerif, fontSize: 24, color: AUR.text, letterSpacing: -0.4, lineHeight: 1.3 }}>{action}.</div>
      </Panel>

      <ThreadNav AUR={AUR} density={densityPreset} items={[
        { kicker: "Module A", title: "This team's health record", hint: "Escalations, root causes and SLA.", to: "/health", search: ((prev: any) => ({ ...prev, wt: t.work_type, tm: t.team_id })) },
        { kicker: "Module C", title: "This team's quality detail", hint: "Is load translating into quality drift?", to: "/workforce", search: ((prev: any) => ({ ...prev, wt: t.work_type, tm: t.team_id })) },
        { kicker: "Module D", title: `Back to ${WORK_TYPE_LABELS[t.work_type]}`, hint: "Return to the work-type outlook.", to: "/capacity", search: ((prev: any) => ({ ...prev, wt: t.work_type, tm: undefined })) },
      ]} />
    </>
  );
}

function SummaryTile({ label, value, sub, status, AUR }: any) {
  return (
    <Panel AUR={AUR} pad={16}>
      <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase" }}>{label}</div>
      <div style={{ fontFamily: aurSerif, fontSize: 30, color: status ? statusColor(AUR, status) : AUR.text, marginTop: 8, lineHeight: 1, fontVariantNumeric: "tabular-nums" }}>{value}</div>
      {sub && <div style={{ fontSize: 11.5, color: AUR.textDim, marginTop: 8 }}>{sub}</div>}
    </Panel>
  );
}
