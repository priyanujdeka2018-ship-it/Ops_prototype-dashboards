// Module A · Regional Health — three progressive levels with breadcrumb
// on top and "follow the thread" cards at the bottom.
// L1: work-type board · L2 (?wt=X): team comparison · L3 (?wt=X&tm=Y): team
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useDash } from "@/dashboards/app-context";
// @ts-expect-error jsx
import { AurSection, AurChip, MetricCell, Breadcrumb, ThreadNav, PillRow, Panel, aurMono, aurSerif, aurSans } from "@/dashboards/atoms.jsx";
// @ts-expect-error jsx
import { classifyMetric, WORK_TYPE_LABELS, ROOT_CAUSE_LABELS, SEVERITY_LABELS, fmt } from "@/dashboards/data-utils.jsx";
import { Loading } from "./_dash.index";

export const Route = createFileRoute("/_dash/health")({
  head: () => ({ meta: [
    { title: "Regional Health · Scale Ops" },
    { name: "description", content: "Module A: SLA, CSAT, quality and escalation pressure across every work type and team." },
  ]}),
  component: Health,
});

function Health() {
  const { data, AUR } = useDash();
  const { wt, tm } = Route.useSearch() as any;
  if (!data) return <Loading AUR={AUR} />;
  if (tm && wt) return <TeamLevel data={data} wt={wt} tm={tm} AUR={AUR} />;
  if (wt) return <WorkTypeLevel data={data} wt={wt} AUR={AUR} />;
  return <Board data={data} AUR={AUR} />;
}

const HEALTH_METRICS = [
  { key: "sla",                       label: "SLA",      cls: "sla",             fmt: (v: number) => `${v.toFixed(1)}%` },
  { key: "csat",                      label: "CSAT",     cls: "csat",            fmt: (v: number) => v.toFixed(2) },
  { key: "quality",                   label: "Quality",  cls: "quality",         fmt: (v: number) => v.toFixed(1) },
  { key: "escalation_rate_per_1000",  label: "Esc/1k",   cls: "escalation_rate", fmt: (v: number) => String(v) },
  { key: "open_escalations",          label: "Open",     cls: "open",            fmt: (v: number) => String(v) },
  { key: "sev1",                      label: "Sev1",     cls: "sev1",            fmt: (v: number) => String(v) },
];

// ─── L1 · Board ─────────────────────────────────────────────────────────────
function Board({ data, AUR }: any) {
  const { densityPreset } = useDash();
  const rollup = [...data.workTypeRollup].sort((a: any, b: any) => b.escalation_rate_per_1000 - a.escalation_rate_per_1000);

  return (
    <>
      <Breadcrumb AUR={AUR} items={[{ label: "Module A · Health" }]} />
      <div>
        <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 0.8, textTransform: "uppercase", marginBottom: 12 }}>Module A · Regional Health</div>
        <h1 style={{ fontFamily: aurSerif, fontSize: 40, fontWeight: 400, letterSpacing: -1, margin: 0, lineHeight: 1.05, color: AUR.text }}>Where the region is breathing — and where it isn't.</h1>
        <p style={{ fontFamily: aurSans, fontSize: 14.5, color: AUR.textDim, marginTop: 14, lineHeight: 1.6, maxWidth: 720 }}>
          Every work-type metric classified against Scale ops thresholds. Teal holds the line, amber is a watch, red is a breach. Open any work type to read across its teams.
        </p>
        <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
          <AurChip AUR={AUR} color={AUR.good}><span style={{ width: 6, height: 6, borderRadius: "50%", background: AUR.good }} />On target</AurChip>
          <AurChip AUR={AUR} color={AUR.warn}><span style={{ width: 6, height: 6, borderRadius: "50%", background: AUR.warn }} />Watch</AurChip>
          <AurChip AUR={AUR} color={AUR.bad}><span style={{ width: 6, height: 6, borderRadius: "50%", background: AUR.bad }} />Breach</AurChip>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: densityPreset.gap, marginTop: densityPreset.sectionGap }}>
        {rollup.map((w: any) => {
          const worst = classifyMetric("sla", w.sla) === "bad" || classifyMetric("quality", w.quality) === "bad" || w.sev1 > 2;
          const watch = !worst && (classifyMetric("sla", w.sla) === "warn" || classifyMetric("quality", w.quality) === "warn" || w.open_escalations > 8);
          const status = worst ? "bad" : watch ? "warn" : "good";
          const dotColor = status === "bad" ? AUR.bad : status === "warn" ? AUR.warn : AUR.good;
          return (
            <NavCard key={w.work_type} to="/health" search={{ wt: w.work_type, tm: undefined }} AUR={AUR}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
                <div>
                  <div style={{ fontFamily: aurSerif, fontSize: 23, color: AUR.text, letterSpacing: -0.4 }}>{WORK_TYPE_LABELS[w.work_type]}</div>
                  <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.4, marginTop: 3 }}>{w.teams} teams · {w.contributors} heads · {w.escalations} escalations</div>
                </div>
                <span style={{ width: 8, height: 8, borderRadius: "50%", background: dotColor, boxShadow: `0 0 10px ${dotColor}99` }} />
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(6, 1fr)", gap: 7 }}>
                {HEALTH_METRICS.map((m) => (
                  <div key={m.key}>
                    <MetricCell AUR={AUR} value={m.fmt(w[m.key])} status={classifyMetric(m.cls, w[m.key])} />
                    <div style={{ textAlign: "center", marginTop: 5, fontFamily: aurMono, fontSize: 9, color: AUR.textFaint, letterSpacing: 0.4, textTransform: "uppercase" }}>{m.label}</div>
                  </div>
                ))}
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 8, color: AUR.accent, fontFamily: aurMono, fontSize: 11, marginTop: 16, letterSpacing: 0.5, textTransform: "uppercase" }}>Read the teams →</div>
            </NavCard>
          );
        })}
      </div>

      <ThreadNav AUR={AUR} density={densityPreset} items={[
        { kicker: "Module B", title: "What keeps coming back", hint: "Open the pattern detector across all work types.", to: "/patterns" },
        { kicker: "Module C", title: "Where quality is drifting", hint: "Per-team risk ranked for calibration.", to: "/workforce" },
        { kicker: "Module D", title: "Can capacity hold next week", hint: "SLA forecast across work types.", to: "/capacity" },
      ]} />
    </>
  );
}

// ─── L2 · Work-type ─────────────────────────────────────────────────────────
function WorkTypeLevel({ data, wt, AUR }: any) {
  const { densityPreset } = useDash();
  const w = data.workTypeRollup.find((r: any) => r.work_type === wt);
  if (!w) return <div style={{ color: AUR.textFaint, padding: 40, fontStyle: "italic", textAlign: "center" }}>Work type not found.</div>;
  const teams = data.teams.filter((t: any) => t.work_type === wt).sort((a: any, b: any) => b.open_escalations - a.open_escalations);
  const esc = data.escalations.filter((e: any) => e.work_type === wt);
  const rootMix: Record<string, number> = {};
  esc.forEach((e: any) => { rootMix[e.root_cause_category] = (rootMix[e.root_cause_category] || 0) + 1; });
  const rootSorted = Object.entries(rootMix).sort((a, b) => b[1] - a[1]);
  const rootMax = rootSorted[0] ? rootSorted[0][1] : 1;

  const summary = [
    { label: "SLA",     value: `${w.sla.toFixed(1)}%`, sub: "target ≥ 95%", status: classifyMetric("sla", w.sla) },
    { label: "CSAT",    value: w.csat.toFixed(2),      sub: "target ≥ 4.4", status: classifyMetric("csat", w.csat) },
    { label: "Quality", value: w.quality.toFixed(1),   sub: "100-pt",       status: classifyMetric("quality", w.quality) },
    { label: "Esc / 1k",value: String(w.escalation_rate_per_1000), sub: `${w.escalations} total`, status: classifyMetric("escalation_rate", w.escalation_rate_per_1000) },
    { label: "Open",    value: String(w.open_escalations), sub: "need closure", status: classifyMetric("open", w.open_escalations) },
    { label: "Sev 1",   value: String(w.sev1),         sub: "critical",     status: classifyMetric("sev1", w.sev1) },
  ];

  return (
    <>
      <Breadcrumb AUR={AUR} items={[
        { label: "Module A · Health", to: "/health", search: ((prev: any) => ({ ...prev, wt: undefined, tm: undefined })) },
        { label: WORK_TYPE_LABELS[wt] },
      ]} />
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", gap: 24, flexWrap: "wrap", marginBottom: 24 }}>
        <div>
          <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 0.8, textTransform: "uppercase", marginBottom: 10 }}>Module A · {WORK_TYPE_LABELS[wt]}</div>
          <h1 style={{ fontFamily: aurSerif, fontSize: 36, fontWeight: 400, letterSpacing: -1, margin: 0, lineHeight: 1.1, color: AUR.text }}>One work type, every team.</h1>
          <p style={{ fontFamily: aurSans, fontSize: 14, color: AUR.textDim, marginTop: 12, maxWidth: 640, lineHeight: 1.6 }}>
            Read across to find the team carrying the cluster. Click any row to step into the team.
          </p>
        </div>
        <WorkTypeSwitcher data={data} wt={wt} AUR={AUR} />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(6, 1fr)", gap: 12 }}>
        {summary.map((s, i) => <SummaryTile key={i} AUR={AUR} {...s} />)}
      </div>

      <Panel AUR={AUR} pad={0} style={{ overflow: "hidden", marginTop: densityPreset.sectionGap }}>
        <div style={{ display: "grid", gridTemplateColumns: "1.7fr 0.8fr 0.5fr 0.7fr 0.7fr 0.7fr 0.6fr 0.6fr 28px", padding: "16px 22px", borderBottom: `1px solid ${AUR.border}` }}>
          {["Team · manager","City","Heads","SLA","CSAT","Quality","Open","Sev1",""].map((h, i) => (
            <span key={i} style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase", textAlign: i >= 3 && i <= 7 ? "right" : "left" }}>{h}</span>
          ))}
        </div>
        {teams.map((t: any, i: number) => (
          <NavRow key={t.team_id} to="/health" search={{ wt, tm: t.team_id }} AUR={AUR} cols="1.7fr 0.8fr 0.5fr 0.7fr 0.7fr 0.7fr 0.6fr 0.6fr 28px" last={i === teams.length - 1}>
            <div>
              <span style={{ fontFamily: aurMono, fontSize: 12, color: AUR.text }}>{t.team_id.replace("TEAM_APAC_", "")}</span>
              <div style={{ color: AUR.textFaint, fontSize: 11.5, marginTop: 2 }}>{t.manager} · {t.shift}</div>
            </div>
            <span style={{ color: AUR.textDim, fontSize: 12.5 }}>{t.city}</span>
            <span style={{ fontFamily: aurMono, fontSize: 12.5, color: AUR.text, textAlign: "right" }}>{t.contributors}</span>
            <span style={{ fontFamily: aurMono, fontSize: 12.5, color: statusColor(AUR, classifyMetric("sla", t.sla)), textAlign: "right" }}>{t.sla.toFixed(1)}%</span>
            <span style={{ fontFamily: aurMono, fontSize: 12.5, color: statusColor(AUR, classifyMetric("csat", t.csat)), textAlign: "right" }}>{t.csat.toFixed(1)}</span>
            <span style={{ fontFamily: aurMono, fontSize: 12.5, color: statusColor(AUR, classifyMetric("quality", t.quality)), textAlign: "right" }}>{t.quality.toFixed(1)}</span>
            <span style={{ fontFamily: aurMono, fontSize: 12.5, color: t.open_escalations > 5 ? AUR.warn : AUR.text, textAlign: "right" }}>{t.open_escalations}</span>
            <span style={{ fontFamily: aurMono, fontSize: 12.5, color: t.sev1_escalations > 0 ? AUR.bad : AUR.textFaint, textAlign: "right" }}>{t.sev1_escalations}</span>
            <span style={{ color: AUR.textFaint, textAlign: "right", fontSize: 15 }}>→</span>
          </NavRow>
        ))}
      </Panel>

      <Panel AUR={AUR} style={{ marginTop: densityPreset.sectionGap }}>
        <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase", marginBottom: 16 }}>Why escalations stick · root-cause mix · {esc.length} escalations</div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px 40px" }}>
          {rootSorted.map(([rc, n]) => (
            <div key={rc} style={{ display: "grid", gridTemplateColumns: "180px 1fr 30px", gap: 12, alignItems: "center" }}>
              <span style={{ fontSize: 12.5, color: AUR.text }}>{ROOT_CAUSE_LABELS[rc] || rc}</span>
              <div style={{ height: 6, background: AUR.surfaceHi, borderRadius: 6, overflow: "hidden" }}>
                <div style={{ width: `${(n / rootMax) * 100}%`, height: "100%", background: `linear-gradient(90deg, ${AUR.accent}, ${AUR.accentDeep})` }} />
              </div>
              <span style={{ fontFamily: aurMono, fontSize: 12, color: AUR.text, textAlign: "right" }}>{n}</span>
            </div>
          ))}
        </div>
      </Panel>

      <ThreadNav AUR={AUR} density={densityPreset} items={[
        { kicker: "Module B", title: "What keeps coming back here", hint: `Open the pattern detector filtered to ${WORK_TYPE_LABELS[wt]}.`, to: "/patterns", search: ((prev: any) => ({ ...prev, wt, tm: undefined, pid: undefined })) },
        { kicker: "Module C", title: "Who's driving quality risk", hint: "Team-level quality drift and coaching signals.", to: "/workforce", search: ((prev: any) => ({ ...prev, wt, tm: undefined })) },
        { kicker: "Module D", title: "Can capacity hold next week", hint: "SLA forecast and staffing gap.", to: "/capacity", search: ((prev: any) => ({ ...prev, wt, tm: undefined })) },
      ]} />
    </>
  );
}

// ─── L3 · Team ──────────────────────────────────────────────────────────────
function TeamLevel({ data, wt, tm, AUR }: any) {
  const { densityPreset } = useDash();
  const t = data.teams.find((x: any) => x.team_id === tm);
  if (!t) return <div style={{ color: AUR.textFaint, padding: 40, textAlign: "center", fontStyle: "italic" }}>Team not found.</div>;
  const esc = data.escalations.filter((e: any) => e.team_id === tm);
  const recent = [...esc].sort((a: any, b: any) => b.date.localeCompare(a.date)).slice(0, 6);
  const rootMix: Record<string, number> = {};
  esc.forEach((e: any) => { rootMix[e.root_cause_category] = (rootMix[e.root_cause_category] || 0) + 1; });
  const rootSorted = Object.entries(rootMix).sort((a, b) => b[1] - a[1]);
  const rootMax = rootSorted[0] ? rootSorted[0][1] : 1;

  const tiles = [
    { label: "SLA",       value: `${t.sla.toFixed(1)}%`,     status: classifyMetric("sla", t.sla) },
    { label: "CSAT",      value: t.csat.toFixed(2),          status: classifyMetric("csat", t.csat) },
    { label: "Quality",   value: t.quality.toFixed(1),       status: classifyMetric("quality", t.quality) },
    { label: "Open esc",  value: String(t.open_escalations), status: classifyMetric("open", t.open_escalations) },
    { label: "Sev 1",     value: String(t.sev1_escalations), status: classifyMetric("sev1", t.sev1_escalations) },
  ];

  return (
    <>
      <Breadcrumb AUR={AUR} items={[
        { label: "Module A · Health", to: "/health", search: ((prev: any) => ({ ...prev, wt: undefined, tm: undefined })) },
        { label: WORK_TYPE_LABELS[t.work_type], to: "/health", search: ((prev: any) => ({ ...prev, wt: t.work_type, tm: undefined })) },
        { label: t.team_id.replace("TEAM_APAC_", "") },
      ]} />
      <div>
        <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 0.8, textTransform: "uppercase", marginBottom: 10 }}>{t.city} · {t.shift} shift · {t.contributors} contributors</div>
        <h1 style={{ fontFamily: aurSerif, fontSize: 36, fontWeight: 400, letterSpacing: -1, margin: 0, lineHeight: 1.1, color: AUR.text }}>{t.manager}'s team</h1>
        <p style={{ color: AUR.textDim, fontSize: 14, marginTop: 12, lineHeight: 1.6, maxWidth: 720 }}>
          {t.team_id} · {WORK_TYPE_LABELS[t.work_type]}. {esc.length} escalations on record, {t.open_escalations} still open.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 12, marginTop: 20 }}>
        {tiles.map((s, i) => <SummaryTile key={i} AUR={AUR} {...s} />)}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.3fr 1fr", gap: 14, marginTop: densityPreset.sectionGap }}>
        <Panel AUR={AUR}>
          <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase", marginBottom: 16 }}>Recent escalations</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {recent.length === 0 && <div style={{ color: AUR.textFaint, fontStyle: "italic", padding: 12 }}>No escalations on record.</div>}
            {recent.map((e: any) => (
              <div key={e.escalation_id} style={{ display: "grid", gridTemplateColumns: "auto 1fr auto", gap: 12, alignItems: "start", paddingBottom: 12, borderBottom: `1px solid ${AUR.border}` }}>
                <span style={{ width: 7, height: 7, borderRadius: "50%", marginTop: 5, background: e.severity === "sev1" ? AUR.bad : e.severity === "sev2" ? AUR.warn : AUR.textFaint }} />
                <div>
                  <div style={{ fontSize: 13, color: AUR.textDim, lineHeight: 1.45 }}>{e.escalation_summary}</div>
                  <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, marginTop: 4 }}>{SEVERITY_LABELS[e.severity]} · {ROOT_CAUSE_LABELS[e.root_cause_category]} · {e.customer_segment} · {fmt.date(e.date)}</div>
                </div>
                <AurChip AUR={AUR} color={e.status === "open" ? AUR.warn : e.status === "in_progress" ? AUR.accent : AUR.good}>{e.status.replace("_", " ")}</AurChip>
              </div>
            ))}
          </div>
        </Panel>
        <Panel AUR={AUR}>
          <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase", marginBottom: 16 }}>Root-cause mix</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {rootSorted.length === 0 && <div style={{ color: AUR.textFaint, fontStyle: "italic" }}>No escalations to break down.</div>}
            {rootSorted.map(([rc, n]) => (
              <div key={rc} style={{ display: "grid", gridTemplateColumns: "1fr 28px", gap: 12, alignItems: "center" }}>
                <div>
                  <div style={{ fontSize: 12.5, color: AUR.text, marginBottom: 5 }}>{ROOT_CAUSE_LABELS[rc] || rc}</div>
                  <div style={{ height: 6, background: AUR.surfaceHi, borderRadius: 6, overflow: "hidden" }}>
                    <div style={{ width: `${(n / rootMax) * 100}%`, height: "100%", background: `linear-gradient(90deg, ${AUR.accent}, ${AUR.accentDeep})` }} />
                  </div>
                </div>
                <span style={{ fontFamily: aurMono, fontSize: 12, color: AUR.text, textAlign: "right" }}>{n}</span>
              </div>
            ))}
          </div>
        </Panel>
      </div>

      <ThreadNav AUR={AUR} density={densityPreset} items={[
        { kicker: "Module C", title: "This team's quality detail", hint: "Drift, gold-task fails, override rate and coaching cards.", to: "/workforce", search: ((prev: any) => ({ ...prev, wt: t.work_type, tm: t.team_id })) },
        { kicker: "Module D", title: "This team's capacity load", hint: "Utilization, backlog share and staffing risk.", to: "/capacity", search: ((prev: any) => ({ ...prev, wt: t.work_type, tm: t.team_id })) },
        { kicker: "Module A", title: `Back to ${WORK_TYPE_LABELS[t.work_type]}`, hint: "Return to the full team comparison.", to: "/health", search: ((prev: any) => ({ ...prev, wt: t.work_type, tm: undefined })) },
      ]} />
    </>
  );
}

// ─── helpers ────────────────────────────────────────────────────────────────
function statusColor(AUR: any, status: string) {
  return status === "good" ? AUR.good : status === "warn" ? AUR.warn : status === "bad" ? AUR.bad : AUR.text;
}

function SummaryTile({ label, value, sub, status, AUR }: any) {
  return (
    <Panel AUR={AUR} pad={16}>
      <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase" }}>{label}</div>
      <div style={{ fontFamily: aurSerif, fontSize: 30, color: statusColor(AUR, status), marginTop: 8, lineHeight: 1, fontVariantNumeric: "tabular-nums" }}>{value}</div>
      {sub && <div style={{ fontSize: 11.5, color: AUR.textDim, marginTop: 8 }}>{sub}</div>}
    </Panel>
  );
}

function WorkTypeSwitcher({ data, wt, AUR }: any) {
  const navigate = useNavigate();
  const opts = data.workTypeRollup.map((r: any) => r.work_type);
  return (
    <div style={{ maxWidth: 540 }}>
      <PillRow AUR={AUR} options={opts} value={wt} onChange={(v: string) =>
        navigate({ to: "/health", search: ((prev: any) => ({ ...prev, wt: v, tm: undefined })) as any })
      } getLabel={(o: string) => WORK_TYPE_LABELS[o]} />
    </div>
  );
}

function NavCard({ to, search, AUR, children }: any) {
  return (
    <Link to={to} search={((prev: any) => ({ ...prev, ...search })) as any} style={{ textDecoration: "none", color: "inherit" }}>
      <Panel AUR={AUR} hoverable>{children}</Panel>
    </Link>
  );
}

function NavRow({ to, search, AUR, children, cols, last }: any) {
  return (
    <Link to={to} search={((prev: any) => ({ ...prev, ...search })) as any} style={{
      display: "grid", gridTemplateColumns: cols, padding: "16px 22px",
      borderBottom: last ? "none" : `1px solid ${AUR.border}`,
      alignItems: "center", textDecoration: "none", color: AUR.text,
    }}>{children}</Link>
  );
}
