// Module B · Pattern Detector — list (with filters) or detail (?pid=).
// Breadcrumb on top, ThreadNav at the bottom, affected-team chips route into Health.
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useDash } from "@/dashboards/app-context";
// @ts-expect-error jsx
import { AurStatusPill, AurRiskBadge, Breadcrumb, ThreadNav, PillRow, Panel, aurMono, aurSerif } from "@/dashboards/atoms.jsx";
// @ts-expect-error jsx
import { WORK_TYPE_LABELS, ROOT_CAUSE_LABELS, ROOT_CAUSE_FIX, ROOT_CAUSE_DECISION, fmt } from "@/dashboards/data-utils.jsx";
import { Loading } from "./_dash.index";

export const Route = createFileRoute("/_dash/patterns")({
  head: () => ({ meta: [
    { title: "Pattern Detector · Scale Ops" },
    { name: "description", content: "Module B: detect when escalations are recurring operating-system failures, not isolated events." },
  ]}),
  component: Patterns,
});

function Patterns() {
  const { data, AUR } = useDash();
  const { pid } = Route.useSearch() as any;
  if (!data) return <Loading AUR={AUR} />;
  if (pid) return <Detail data={data} pid={pid} AUR={AUR} />;
  return <List data={data} AUR={AUR} />;
}

function List({ data, AUR }: any) {
  const { densityPreset } = useDash();
  const search = Route.useSearch() as any;
  const navigate = useNavigate();
  const setQ = (patch: any) => navigate({ to: "/patterns", search: ((prev: any) => ({ ...prev, ...patch })) as any });
  const risk = search.risk || "all";
  const status = search.status || "all";
  const wt = search.wt || "all";

  const filtered = data.patterns.filter((p: any) => {
    if (risk !== "all" && p.risk_level !== risk) return false;
    if (status !== "all" && p.recurrence_status !== status) return false;
    if (wt !== "all" && p.work_type !== wt) return false;
    return true;
  });
  const highCount = data.patterns.filter((p: any) => p.risk_level === "High").length;
  const statusOptions = ["all", ...Array.from(new Set(data.patterns.map((p: any) => p.recurrence_status)))];

  return (
    <>
      <Breadcrumb AUR={AUR} items={[
        { label: "Module B · Patterns" },
        ...(wt !== "all" ? [{ label: WORK_TYPE_LABELS[wt] }] : []),
      ]} />
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", gap: 24, flexWrap: "wrap" }}>
        <div>
          <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 0.8, textTransform: "uppercase", marginBottom: 10 }}>Module B · Pattern Detector</div>
          <h1 style={{ fontFamily: aurSerif, fontSize: 36, fontWeight: 400, letterSpacing: -1, margin: 0, lineHeight: 1.1, color: AUR.text }}>
            {data.patterns.length} recurring patterns. {highCount} demand action.
          </h1>
          <p style={{ color: AUR.textDim, fontSize: 14, marginTop: 12, maxWidth: 720, lineHeight: 1.6 }}>
            Every escalation grouped on work-type + root-cause. Risk score is deterministic — escalation count, severity weight, open volume, segment spread, slow-resolution penalty, acceleration bonus.
          </p>
        </div>
        <PillRow AUR={AUR} options={["all","High","Medium","Low"]} value={risk} onChange={(v: string) => setQ({ risk: v === "all" ? undefined : v })} getLabel={(o: string) => o === "all" ? "All risk" : o} />
      </div>

      <div style={{ display: "flex", gap: 18, marginTop: 18, flexWrap: "wrap", alignItems: "center" }}>
        <PillRow AUR={AUR} options={statusOptions} value={status} onChange={(v: string) => setQ({ status: v === "all" ? undefined : v })}
          getLabel={(o: string) => o === "all" ? "All status" : o}
          getCount={(o: string) => o === "all" ? data.patterns.length : data.patterns.filter((p: any) => p.recurrence_status === o).length} />
        <div style={{ width: 1, height: 22, background: AUR.border }} />
        <PillRow AUR={AUR} options={["all", ...data.workTypeRollup.map((w: any) => w.work_type)]} value={wt} onChange={(v: string) => setQ({ wt: v === "all" ? undefined : v })} getLabel={(o: string) => o === "all" ? "All work types" : WORK_TYPE_LABELS[o]} />
      </div>

      <Panel AUR={AUR} pad={0} style={{ overflow: "hidden", marginTop: 20 }}>
        <div style={{ display: "grid", gridTemplateColumns: "2.4fr 0.5fr 0.5fr 0.5fr 1fr 0.8fr 0.7fr 28px", padding: "16px 22px", borderBottom: `1px solid ${AUR.border}` }}>
          {["Pattern","Esc","Sev1","Open","Status","Risk","Score",""].map((h, i) => (
            <span key={i} style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase", textAlign: (i >= 1 && i <= 3) || i === 6 ? "right" : "left" }}>{h}</span>
          ))}
        </div>
        {filtered.length === 0 && <div style={{ padding: 36, textAlign: "center", color: AUR.textFaint, fontStyle: "italic" }}>No patterns match these filters.</div>}
        {filtered.map((p: any, i: number) => (
          <Link key={p.pattern_id} to="/patterns" search={((prev: any) => ({ ...prev, pid: p.pattern_id })) as any}
            style={{
              display: "grid", gridTemplateColumns: "2.4fr 0.5fr 0.5fr 0.5fr 1fr 0.8fr 0.7fr 28px",
              padding: "18px 22px", borderBottom: i === filtered.length - 1 ? "none" : `1px solid ${AUR.border}`,
              alignItems: "center", textDecoration: "none", color: AUR.text,
            }}>
            <div>
              <div style={{ fontFamily: aurSerif, fontSize: 18, color: AUR.text, letterSpacing: -0.2 }}>
                {ROOT_CAUSE_LABELS[p.root_cause]} <span style={{ color: AUR.textFaint }}>in</span> {WORK_TYPE_LABELS[p.work_type]}
              </div>
              <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, marginTop: 3 }}>{p.unique_teams} teams · {p.unique_segments} segments · latest {fmt.date(p.latest_seen)}</div>
            </div>
            <span style={{ fontFamily: aurMono, fontSize: 13, color: AUR.text, textAlign: "right" }}>{p.escalation_count}</span>
            <span style={{ fontFamily: aurMono, fontSize: 13, color: p.sev1_count > 0 ? AUR.bad : AUR.textFaint, textAlign: "right" }}>{p.sev1_count}</span>
            <span style={{ fontFamily: aurMono, fontSize: 13, color: p.open_count > 5 ? AUR.warn : AUR.text, textAlign: "right" }}>{p.open_count}</span>
            <AurStatusPill AUR={AUR} status={p.recurrence_status} />
            <AurRiskBadge AUR={AUR} level={p.risk_level} />
            <span style={{ fontFamily: aurSerif, fontSize: 22, color: p.risk_score > 120 ? AUR.bad : p.risk_score > 50 ? AUR.warn : AUR.text, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{Math.round(p.risk_score)}</span>
            <span style={{ color: AUR.textFaint, textAlign: "right", fontSize: 15 }}>→</span>
          </Link>
        ))}
      </Panel>

      <ThreadNav AUR={AUR} density={densityPreset} items={[
        { kicker: "Module B v2", title: "See these as semantic clusters", hint: "Same data, grouped by meaning instead of label.", to: "/clusters" },
        { kicker: "Module A", title: "Back to regional health", hint: "Where does the underlying SLA / quality pressure sit?", to: "/health" },
      ]} />
    </>
  );
}

function Detail({ data, pid, AUR }: any) {
  const { densityPreset } = useDash();
  const p = data.patterns.find((x: any) => x.pattern_id === pid);
  if (!p) return <div style={{ padding: 40, color: AUR.textFaint, textAlign: "center", fontStyle: "italic" }}>Pattern not found.</div>;
  const fix = ROOT_CAUSE_FIX[p.root_cause] || { fix: "Manager review", owner: "Regional ops", metric: "Escalation count" };
  const decision = ROOT_CAUSE_DECISION[p.root_cause] || "Assign owner + prevention plan";
  const tiles = [
    { l: "Escalations", v: p.escalation_count },
    { l: "Sev 1 / 2", v: `${p.sev1_count} / ${p.sev2_count}` },
    { l: "Open", v: p.open_count },
    { l: "Avg days", v: p.avg_days_to_resolve },
    { l: "Last 14d", v: `${p.last_14d}` },
    { l: "Prior 14d", v: `${p.prior_14d}` },
  ];

  return (
    <>
      <Breadcrumb AUR={AUR} items={[
        { label: "Module B · Patterns", to: "/patterns", search: ((prev: any) => ({ ...prev, pid: undefined })) },
        { label: `${ROOT_CAUSE_LABELS[p.root_cause]} · ${WORK_TYPE_LABELS[p.work_type]}` },
      ]} />
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", gap: 24, flexWrap: "wrap" }}>
        <div>
          <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 0.8, textTransform: "uppercase", marginBottom: 10 }}>Pattern drilldown · {p.pattern_id}</div>
          <h1 style={{ fontFamily: aurSerif, fontSize: 36, fontWeight: 400, letterSpacing: -1, margin: 0, lineHeight: 1.1, color: AUR.text }}>
            {ROOT_CAUSE_LABELS[p.root_cause]} in {WORK_TYPE_LABELS[p.work_type]}
          </h1>
          <p style={{ color: AUR.textDim, fontSize: 14, marginTop: 12, lineHeight: 1.6 }}>
            First seen {fmt.date(p.first_seen)}, latest {fmt.date(p.latest_seen)}. Spans {p.unique_teams} teams across {p.unique_segments} customer segments.
          </p>
        </div>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <AurStatusPill AUR={AUR} status={p.recurrence_status} />
          <AurRiskBadge AUR={AUR} level={p.risk_level} />
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(6, 1fr)", gap: 12, marginTop: 22 }}>
        {tiles.map((m, i) => (
          <Panel key={i} AUR={AUR} pad={16}>
            <div style={{ fontFamily: aurMono, fontSize: 10, color: AUR.textFaint, letterSpacing: 0.5, textTransform: "uppercase" }}>{m.l}</div>
            <div style={{ fontFamily: aurSerif, fontSize: 26, color: AUR.text, marginTop: 6, fontVariantNumeric: "tabular-nums" }}>{m.v}</div>
          </Panel>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.35fr 1fr", gap: 14, marginTop: densityPreset.sectionGap }}>
        <Panel AUR={AUR}>
          <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase", marginBottom: 16 }}>Recent escalation summaries</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            {p.sample_summaries.map((s: string, i: number) => (
              <div key={i} style={{ fontSize: 14, color: AUR.textDim, paddingLeft: 16, borderLeft: `2px solid ${AUR.accent}55`, lineHeight: 1.55, fontStyle: "italic" }}>"{s}"</div>
            ))}
          </div>
          <div style={{ marginTop: 22 }}>
            <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase", marginBottom: 12 }}>Affected teams · click to open</div>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              {p.teams.map((tid: string) => (
                <Link key={tid} to="/health" search={((prev: any) => ({ ...prev, wt: p.work_type, tm: tid })) as any}
                  style={{ background: AUR.surfaceHi, border: `1px solid ${AUR.border}`, borderRadius: 999, padding: "7px 14px", fontFamily: aurMono, fontSize: 11.5, color: AUR.text, textDecoration: "none" }}>
                  {tid.replace("TEAM_APAC_", "")} →
                </Link>
              ))}
            </div>
          </div>
        </Panel>

        <Panel AUR={AUR} glow accentEdge>
          <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 0.8, textTransform: "uppercase", marginBottom: 16 }}>Recommended structural fix</div>
          <div style={{ display: "grid", gridTemplateColumns: "72px 1fr", gap: "12px 16px", fontSize: 13.5, marginBottom: 18 }}>
            <span style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, textTransform: "uppercase", letterSpacing: 0.5 }}>Fix</span><span style={{ color: AUR.text }}>{fix.fix}</span>
            <span style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, textTransform: "uppercase", letterSpacing: 0.5 }}>Owner</span><span style={{ color: AUR.text }}>{fix.owner}</span>
            <span style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, textTransform: "uppercase", letterSpacing: 0.5 }}>Metric</span><span style={{ color: AUR.text }}>{fix.metric}</span>
          </div>
          <div style={{ padding: "14px 16px", background: AUR.accentGlow, borderRadius: 12, borderLeft: `2px solid ${AUR.accent}` }}>
            <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 0.6, textTransform: "uppercase", marginBottom: 6 }}>Decision needed this week</div>
            <div style={{ fontSize: 13.5, color: AUR.text, lineHeight: 1.5 }}>{decision}</div>
          </div>
        </Panel>
      </div>

      <ThreadNav AUR={AUR} density={densityPreset} items={[
        { kicker: "Module B v2", title: "See this as a semantic cluster", hint: "How the fix card reads when grouped by meaning.", to: "/clusters" },
        { kicker: "Module C", title: "Is quality drift feeding this", hint: `Quality risk across ${WORK_TYPE_LABELS[p.work_type]} teams.`, to: "/workforce", search: ((prev: any) => ({ ...prev, wt: p.work_type, tm: undefined })) },
        { kicker: "Module D", title: "Is capacity feeding this", hint: `Backlog and SLA pressure on ${WORK_TYPE_LABELS[p.work_type]}.`, to: "/capacity", search: ((prev: any) => ({ ...prev, wt: p.work_type, tm: undefined })) },
      ]} />
    </>
  );
}
