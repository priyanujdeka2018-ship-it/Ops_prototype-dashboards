// Module C · Workforce Quality — 3-level progressive disclosure.
// L1: region overview · L2 (?wt=X): work-type teams · L3 (?wt=X&tm=Y): team detail
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useDash } from "@/dashboards/app-context";
// @ts-expect-error jsx
import { Breadcrumb, ThreadNav, PillRow, Panel, AurRiskBadge, RiskMeter, DriverBars, CoachingCard, aurMono, aurSerif } from "@/dashboards/atoms.jsx";
// @ts-expect-error jsx
import { deriveQuality, WORK_TYPE_LABELS, classifyMetric, fmt } from "@/dashboards/data-utils.jsx";
import { Loading } from "./_dash.index";

export const Route = createFileRoute("/_dash/workforce")({
  head: () => ({ meta: [
    { title: "Workforce Quality · Scale Ops" },
    { name: "description", content: "Module C: per-team quality risk for coaching and calibration, not punitive ranking." },
  ]}),
  component: Workforce,
});

function Workforce() {
  const { data, AUR } = useDash();
  const { wt, tm } = Route.useSearch() as any;
  if (!data) return <Loading AUR={AUR} />;
  const q = deriveQuality(data);
  if (tm) return <TeamLevel q={q} tm={tm} AUR={AUR} />;
  if (wt) return <WorkTypeLevel data={data} q={q} wt={wt} AUR={AUR} />;
  return <Overview q={q} AUR={AUR} />;
}

const statusColor = (AUR: any, s: string) => s === "good" ? AUR.good : s === "warn" ? AUR.warn : s === "bad" ? AUR.bad : AUR.text;

// ─── L1 · Overview ──────────────────────────────────────────────────────────
function Overview({ q, AUR }: any) {
  const { densityPreset } = useDash();
  const stats = [
    { label: "Avg quality", value: fmt.dec(q.region.avgQuality, 1), sub: "target ≥ 90 · 100-pt", status: classifyMetric("quality", q.region.avgQuality) },
    { label: "Teams at risk", value: String(q.region.highRiskTeams), sub: `of ${q.region.teamCount} teams`, status: q.region.highRiskTeams > 2 ? "bad" : q.region.highRiskTeams ? "warn" : "good" },
    { label: "Flagged contributors", value: String(q.region.flaggedContributors), sub: `${q.region.highRiskContributors} high-risk`, status: q.region.highRiskContributors > 6 ? "bad" : q.region.flaggedContributors ? "warn" : "good" },
    { label: "Rework rate", value: fmt.pct(q.region.reworkRate), sub: "region · of completed", status: q.region.reworkRate < 4 ? "good" : q.region.reworkRate < 7 ? "warn" : "bad" },
  ];
  const maxScore = Math.max(...q.byWorkType.map((w: any) => w.avgScore), 1);

  return (
    <>
      <Breadcrumb AUR={AUR} items={[{ label: "Module C · Workforce Quality" }]} />
      <div>
        <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 0.8, textTransform: "uppercase", marginBottom: 10 }}>Module C · Workforce Quality</div>
        <h1 style={{ fontFamily: aurSerif, fontSize: 36, fontWeight: 400, letterSpacing: -1, margin: 0, lineHeight: 1.1, color: AUR.text }}>Where quality is drifting — and who needs support.</h1>
        <p style={{ color: AUR.textDim, fontSize: 14, marginTop: 12, maxWidth: 720, lineHeight: 1.6 }}>
          A coaching, calibration and staffing-risk detector — not a punitive scoreboard. Gold-task fails, reviewer overrides, rework and drift become support actions before drift becomes customer impact.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginTop: 22 }}>
        {stats.map((s, i) => <SummaryTile key={i} AUR={AUR} {...s} />)}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.05fr 1fr", gap: 14, marginTop: densityPreset.sectionGap }}>
        <div>
          <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase", marginBottom: 16 }}>Quality risk by work type</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {q.byWorkType.map((w: any) => (
              <Link key={w.work_type} to="/workforce" search={((prev: any) => ({ ...prev, wt: w.work_type, tm: undefined })) as any} style={{ textDecoration: "none", color: "inherit" }}>
                <Panel AUR={AUR} hoverable pad={18}>
                  <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr auto", gap: 16, alignItems: "center" }}>
                    <div>
                      <div style={{ fontFamily: aurSerif, fontSize: 19, color: AUR.text, letterSpacing: -0.3 }}>{WORK_TYPE_LABELS[w.work_type]}</div>
                      <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, marginTop: 3 }}>quality {w.quality} · {w.highTeams} teams at risk · {w.flagged} flagged</div>
                    </div>
                    <div>
                      <RiskMeter AUR={AUR} score={w.avgScore} max={maxScore * 1.15} />
                      <div style={{ fontFamily: aurMono, fontSize: 10, color: AUR.textFaint, marginTop: 6 }}>risk index {w.avgScore}</div>
                    </div>
                    <AurRiskBadge AUR={AUR} level={w.level} />
                  </div>
                </Panel>
              </Link>
            ))}
          </div>
        </div>

        <div>
          <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase", marginBottom: 16 }}>Weekly coaching & calibration queue</div>
          <Panel AUR={AUR} pad={0} style={{ overflow: "hidden" }}>
            {q.queue.map((t: any, i: number) => (
              <Link key={t.team_id} to="/workforce" search={((prev: any) => ({ ...prev, wt: t.work_type, tm: t.team_id })) as any}
                style={{
                  display: "grid", gridTemplateColumns: "1fr auto auto", gap: 14, alignItems: "center",
                  padding: "16px 20px", borderBottom: i === q.queue.length - 1 ? "none" : `1px solid ${AUR.border}`,
                  textDecoration: "none", color: AUR.text,
                }}>
                <div>
                  <span style={{ fontFamily: aurMono, fontSize: 12, color: AUR.text }}>{t.team_id.replace("TEAM_APAC_", "")}</span>
                  <div style={{ fontSize: 12, color: AUR.textFaint, marginTop: 3 }}>{t.manager} · top driver: {t.drivers[0].k.toLowerCase()}</div>
                </div>
                <span style={{ fontFamily: aurSerif, fontSize: 20, color: t.riskLevel === "High" ? AUR.bad : t.riskLevel === "Medium" ? AUR.warn : AUR.text }}>{t.riskScore}</span>
                <AurRiskBadge AUR={AUR} level={t.riskLevel} />
              </Link>
            ))}
          </Panel>
          <div style={{ marginTop: 14, padding: "14px 16px", background: AUR.accentSoft, borderRadius: 12, borderLeft: `2px solid ${AUR.accent}` }}>
            <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 0.6, textTransform: "uppercase", marginBottom: 5 }}>Operating principle</div>
            <div style={{ fontSize: 13, color: AUR.textDim, lineHeight: 1.5 }}>This queue drives coaching, calibration and staffing decisions — never individual ranking or punishment.</div>
          </div>
        </div>
      </div>

      <ThreadNav AUR={AUR} density={densityPreset} items={[
        { kicker: "Module A", title: "Health board across the region", hint: "Where the breakdowns are surfacing.", to: "/health" },
        { kicker: "Module D", title: "Capacity feeding quality risk", hint: "When heads are stretched, quality slips first.", to: "/capacity" },
      ]} />
    </>
  );
}

// ─── L2 · Work-type ─────────────────────────────────────────────────────────
function WorkTypeLevel({ data, q, wt, AUR }: any) {
  const { densityPreset } = useDash();
  const navigate = useNavigate();
  const teams = q.teams.filter((t: any) => t.work_type === wt);
  const flagged = q.flagged.filter((c: any) => c.work_type === wt).slice(0, 6);

  return (
    <>
      <Breadcrumb AUR={AUR} items={[
        { label: "Module C · Workforce Quality", to: "/workforce", search: ((prev: any) => ({ ...prev, wt: undefined, tm: undefined })) },
        { label: WORK_TYPE_LABELS[wt] },
      ]} />
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", gap: 24, flexWrap: "wrap" }}>
        <div>
          <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 0.8, textTransform: "uppercase", marginBottom: 10 }}>Module C · {WORK_TYPE_LABELS[wt]}</div>
          <h1 style={{ fontFamily: aurSerif, fontSize: 36, fontWeight: 400, letterSpacing: -1, margin: 0, lineHeight: 1.1, color: AUR.text }}>Team quality risk, read across.</h1>
          <p style={{ color: AUR.textDim, fontSize: 14, marginTop: 12, maxWidth: 640, lineHeight: 1.6 }}>
            Quality gap to target, drift since last period, gold-task fails and rework — the signals that say where to send a calibration session next.
          </p>
        </div>
        <PillRow AUR={AUR} options={data.workTypeRollup.map((r: any) => r.work_type)} value={wt}
          onChange={(v: string) => navigate({ to: "/workforce", search: ((prev: any) => ({ ...prev, wt: v, tm: undefined })) as any })}
          getLabel={(o: string) => WORK_TYPE_LABELS[o]} />
      </div>

      <Panel AUR={AUR} pad={0} style={{ overflow: "hidden", marginTop: densityPreset.sectionGap }}>
        <div style={{ display: "grid", gridTemplateColumns: "1.5fr 0.7fr 0.7fr 0.8fr 0.7fr 0.9fr 0.7fr 28px", padding: "16px 22px", borderBottom: `1px solid ${AUR.border}` }}>
          {["Team · manager","Quality","Drift","Gold-fail","Rework","Status","Score",""].map((h, i) => (
            <span key={i} style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase", textAlign: (i >= 1 && i <= 4) || i === 6 ? "right" : "left" }}>{h}</span>
          ))}
        </div>
        {teams.map((t: any, i: number) => (
          <Link key={t.team_id} to="/workforce" search={((prev: any) => ({ ...prev, wt, tm: t.team_id })) as any}
            style={{
              display: "grid", gridTemplateColumns: "1.5fr 0.7fr 0.7fr 0.8fr 0.7fr 0.9fr 0.7fr 28px",
              padding: "16px 22px", borderBottom: i === teams.length - 1 ? "none" : `1px solid ${AUR.border}`,
              alignItems: "center", textDecoration: "none", color: AUR.text,
            }}>
            <div>
              <span style={{ fontFamily: aurMono, fontSize: 12, color: AUR.text }}>{t.team_id.replace("TEAM_APAC_", "")}</span>
              <div style={{ fontSize: 11.5, color: AUR.textFaint, marginTop: 2 }}>{t.manager} · {t.contributors} heads</div>
            </div>
            <span style={{ fontFamily: aurMono, fontSize: 12.5, color: statusColor(AUR, classifyMetric("quality", t.quality)), textAlign: "right" }}>{t.quality}</span>
            <span style={{ fontFamily: aurMono, fontSize: 12.5, color: t.driftDelta < 0 ? AUR.bad : AUR.good, textAlign: "right" }}>{t.driftDelta > 0 ? "+" : ""}{t.driftDelta}</span>
            <span style={{ fontFamily: aurMono, fontSize: 12.5, color: t.goldFailRate > 18 ? AUR.bad : t.goldFailRate > 10 ? AUR.warn : AUR.text, textAlign: "right" }}>{t.goldFailRate}%</span>
            <span style={{ fontFamily: aurMono, fontSize: 12.5, color: t.reworkRate > 10 ? AUR.warn : AUR.text, textAlign: "right" }}>{t.reworkRate}%</span>
            <span style={{ textAlign: "right" }}><AurRiskBadge AUR={AUR} level={t.riskLevel} /></span>
            <span style={{ fontFamily: aurSerif, fontSize: 20, color: t.riskLevel === "High" ? AUR.bad : t.riskLevel === "Medium" ? AUR.warn : AUR.text, textAlign: "right" }}>{t.riskScore}</span>
            <span style={{ color: AUR.textFaint, textAlign: "right", fontSize: 15 }}>→</span>
          </Link>
        ))}
      </Panel>

      {flagged.length > 0 && (
        <>
          <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase", marginTop: densityPreset.sectionGap, marginBottom: 16 }}>Contributors flagged for support · {WORK_TYPE_LABELS[wt]}</div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 12 }}>
            {flagged.map((c: any) => <CoachingCard key={c.id} c={c} AUR={AUR} />)}
          </div>
        </>
      )}

      <ThreadNav AUR={AUR} density={densityPreset} items={[
        { kicker: "Module A", title: "See the health board", hint: `SLA, CSAT and escalation pressure for ${WORK_TYPE_LABELS[wt]}.`, to: "/health", search: ((prev: any) => ({ ...prev, wt, tm: undefined })) },
        { kicker: "Module D", title: "Is capacity straining quality", hint: "When heads are stretched, quality slips first.", to: "/capacity", search: ((prev: any) => ({ ...prev, wt, tm: undefined })) },
      ]} />
    </>
  );
}

// ─── L3 · Team ──────────────────────────────────────────────────────────────
function TeamLevel({ q, tm, AUR }: any) {
  const { densityPreset } = useDash();
  const t = q.teams.find((x: any) => x.team_id === tm);
  if (!t) return <div style={{ padding: 40, color: AUR.textFaint, textAlign: "center", fontStyle: "italic" }}>Team not found.</div>;
  const flagged = q.flagged.filter((c: any) => c.team_id === t.team_id);
  const subs = [
    { label: "Quality",   value: t.quality, status: classifyMetric("quality", t.quality) },
    { label: "Drift",     value: `${t.driftDelta > 0 ? "+" : ""}${t.driftDelta}`, status: t.driftDelta < 0 ? "bad" : "good" },
    { label: "Gold-fail", value: `${t.goldFailRate}%`, status: t.goldFailRate > 18 ? "bad" : t.goldFailRate > 10 ? "warn" : "good" },
    { label: "Override",  value: `${t.overrideRate}%`, status: t.overrideRate > 16 ? "bad" : t.overrideRate > 8 ? "warn" : "good" },
    { label: "Peer agree",value: `${t.peerAgree}%`, status: t.peerAgree < 75 ? "bad" : t.peerAgree < 85 ? "warn" : "good" },
    { label: "Rework",    value: `${t.reworkRate}%`, status: t.reworkRate > 10 ? "warn" : "good" },
  ];

  return (
    <>
      <Breadcrumb AUR={AUR} items={[
        { label: "Module C · Workforce Quality", to: "/workforce", search: ((prev: any) => ({ ...prev, wt: undefined, tm: undefined })) },
        { label: WORK_TYPE_LABELS[t.work_type], to: "/workforce", search: ((prev: any) => ({ ...prev, wt: t.work_type, tm: undefined })) },
        { label: t.team_id.replace("TEAM_APAC_", "") },
      ]} />
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", gap: 24, flexWrap: "wrap" }}>
        <div>
          <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 0.8, textTransform: "uppercase", marginBottom: 10 }}>{WORK_TYPE_LABELS[t.work_type]} · {t.contributors} contributors · {t.lowTenureShare}% low-tenure</div>
          <h1 style={{ fontFamily: aurSerif, fontSize: 36, fontWeight: 400, letterSpacing: -1, margin: 0, lineHeight: 1.1, color: AUR.text }}>{t.manager}'s team · quality risk</h1>
          <p style={{ color: AUR.textDim, fontSize: 14, marginTop: 12, maxWidth: 720, lineHeight: 1.6 }}>
            Quality {t.quality}, {t.driftDelta < 0 ? `down ${Math.abs(t.driftDelta)}pt` : `up ${t.driftDelta}pt`} since last period. The breakdown below is exactly what the deterministic scorer added up.
          </p>
        </div>
        <AurRiskBadge AUR={AUR} level={t.riskLevel} />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(6, 1fr)", gap: 12, marginTop: 22 }}>
        {subs.map((s, i) => <SummaryTile key={i} AUR={AUR} {...s} />)}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1.25fr", gap: 14, marginTop: densityPreset.sectionGap }}>
        <Panel AUR={AUR}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 18 }}>
            <span style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase" }}>Risk score breakdown</span>
            <span style={{ fontFamily: aurSerif, fontSize: 34, color: t.riskLevel === "High" ? AUR.bad : t.riskLevel === "Medium" ? AUR.warn : AUR.text }}>{t.riskScore}</span>
          </div>
          <DriverBars AUR={AUR} drivers={t.drivers} max={6} />
        </Panel>

        <div>
          <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase", marginBottom: 16 }}>Coaching cards · {flagged.length} contributor{flagged.length === 1 ? "" : "s"} flagged</div>
          {flagged.length === 0 && <Panel AUR={AUR}><div style={{ color: AUR.textFaint, fontStyle: "italic", padding: 12 }}>No contributors meet the support threshold. Quality risk here is structural — calibrate the team, not an individual.</div></Panel>}
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {flagged.map((c: any) => <CoachingCard key={c.id} c={c} AUR={AUR} />)}
          </div>
        </div>
      </div>

      <ThreadNav AUR={AUR} density={densityPreset} items={[
        { kicker: "Module A", title: "This team's health record", hint: "Escalations, root causes and SLA.", to: "/health", search: ((prev: any) => ({ ...prev, wt: t.work_type, tm: t.team_id })) },
        { kicker: "Module D", title: "This team's capacity load", hint: "Is the team simply over capacity?", to: "/capacity", search: ((prev: any) => ({ ...prev, wt: t.work_type, tm: t.team_id })) },
        { kicker: "Module C", title: `Back to ${WORK_TYPE_LABELS[t.work_type]}`, hint: "Return to the work-type comparison.", to: "/workforce", search: ((prev: any) => ({ ...prev, wt: t.work_type, tm: undefined })) },
      ]} />
    </>
  );
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
