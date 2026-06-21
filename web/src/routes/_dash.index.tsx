// Home — Command Center landing. KPI strip, **Leadership Attention** alerts,
// module gateways. Each alert is clickable and threads into the relevant
// module's deep level.
import { createFileRoute, Link } from "@tanstack/react-router";
import { useDash } from "@/dashboards/app-context";
// @ts-expect-error jsx
import { AurKpi, AurSection, aurMono, aurSerif, aurSans, Panel } from "@/dashboards/atoms.jsx";
// @ts-expect-error jsx
import { fmt, classifyMetric, buildLeadershipAlerts, deriveQuality, deriveCapacity, WORK_TYPE_LABELS } from "@/dashboards/data-utils.jsx";

export const Route = createFileRoute("/_dash/")({
  head: () => ({
    meta: [
      { title: "Scale Ops · Regional Command Center" },
      { name: "description", content: "One operating view across SLA, CSAT, escalations, workforce quality, and capacity for a regional operations leader." },
    ],
  }),
  component: Home,
});

function Home() {
  const { data, AUR, densityPreset } = useDash();
  if (!data) return <Loading AUR={AUR} />;
  const k = data.kpis, d = data;
  const q = deriveQuality(d);
  const c = deriveCapacity(d);
  const alerts = buildLeadershipAlerts(d, AUR);

  const slaStatus = classifyMetric("sla", k.sla_adherence);
  const breachWts = d.workTypeRollup.filter((w: any) => classifyMetric("sla", w.sla) === "bad" || classifyMetric("quality", w.quality) === "bad" || w.sev1 > 2);
  const headline = slaStatus === "good" && breachWts.length === 0
    ? "The region is holding the line. A few watch-items, nothing on fire."
    : `${breachWts.length} work ${breachWts.length === 1 ? "type is" : "types are"} breaching, and escalation pressure is building. Here's where to look first.`;

  const gateways = [
    { to: "/health",    eyebrow: "Module A",   title: "Regional Health",   stat: String(breachWts.length), statLabel: breachWts.length === 1 ? "work type breaching" : "work types breaching", status: breachWts.length ? "bad" : "good", body: "SLA, CSAT, quality and escalation pressure across every work type and team." },
    { to: "/patterns",  eyebrow: "Module B",   title: "Escalation Patterns", stat: String(d.patterns.filter((p:any) => p.risk_level === "High").length), statLabel: "high-risk patterns", status: d.patterns.filter((p:any) => p.risk_level === "High").length ? "bad" : "warn", body: "Which breakdowns recur — scored, ranked, and turned into fixes." },
    { to: "/clusters",  eyebrow: "Module B v2", title: "Semantic Clusters", stat: String(d.patterns.filter((p:any) => p.recurrence_status === "Accelerating" || p.recurrence_status === "Recurring").length), statLabel: "live themes", status: "warn", body: "Repeat themes detected even when teams describe the same breakdown differently." },
    { to: "/workforce", eyebrow: "Module C",   title: "Workforce Quality", stat: String(q.region.highRiskTeams), statLabel: "teams at quality risk", status: q.region.highRiskTeams > 2 ? "bad" : q.region.highRiskTeams ? "warn" : "good", body: "Where quality is drifting, and who needs coaching, calibration or support." },
    { to: "/capacity",  eyebrow: "Module D",   title: "Capacity & SLA",    stat: String(c.region.atRisk), statLabel: "work types at SLA risk", status: c.region.atRisk > 2 ? "bad" : c.region.atRisk ? "warn" : "good", body: "Next-week SLA forecast, staffing gaps, and where to rebalance." },
    { to: "/drilldown", eyebrow: "Module A·d", title: "Work-type Drilldown", stat: "5", statLabel: "alt cross-cut", status: "muted", body: "One work type, every team — alt entry point used for deep comparisons." },
  ];

  return (
    <>
      <div style={{ marginBottom: densityPreset.sectionGap }}>
        <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 0.8, textTransform: "uppercase", marginBottom: 14 }}>
          {data.region} Region · Week of {data.weekStart} → {fmt.date(data.refDate)}
        </div>
        <h1 style={{ fontFamily: aurSerif, fontSize: 48, fontWeight: 400, letterSpacing: -1.5, margin: 0, lineHeight: 1.04, maxWidth: 920, color: AUR.text }}>{headline}</h1>
      </div>

      {/* KPI strip */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: densityPreset.gap }}>
        <AurKpi AUR={AUR} label="SLA Adherence" value={fmt.pct(k.sla_adherence)} sub="target ≥ 95.0%" status={classifyMetric("sla", k.sla_adherence)} trendData={d.kpiTrends.sla} />
        <AurKpi AUR={AUR} label="CSAT · 7-day"  value={fmt.dec(k.csat_7d, 2)}    sub="target ≥ 4.40" status={classifyMetric("csat", k.csat_7d)} trendData={d.kpiTrends.csat} />
        <AurKpi AUR={AUR} label="Backlog"       value={fmt.num(k.backlog)} sub={`${c.region.agedShare}% aged >72h`} status={k.aged_backlog_72h > 800 ? "bad" : k.aged_backlog_72h > 250 ? "warn" : "good"} trendData={d.kpiTrends.backlog} />
        <AurKpi AUR={AUR} label="Escalations"   value={d.totals.escalations} sub={`${d.totals.open} open · ${d.totals.sev1} sev1`} status={d.totals.sev1 > 20 ? "bad" : d.totals.sev1 > 8 ? "warn" : "good"} trendData={d.weeklyTrend.map((w:any) => w.count)} />
        <AurKpi AUR={AUR} label="Avg Quality"   value={fmt.dec(k.avg_quality, 1)} sub="100-pt scale" status={classifyMetric("quality", k.avg_quality)} trendData={d.kpiTrends.quality} />
      </div>

      {/* Leadership attention */}
      <AurSection AUR={AUR} density={densityPreset} eyebrow="Leadership attention" title="Three things that matter this week.">
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          {alerts.length === 0 && <Panel AUR={AUR}><div style={{ color: AUR.textFaint, fontStyle: "italic", textAlign: "center", padding: 24 }}>No leadership alerts this period. The region is holding the line.</div></Panel>}
          {alerts.map((a: any, i: number) => (
            <Link key={i} to={a.to as any} search={((prev: any) => ({ ...prev, ...a.focus })) as any} style={{ textDecoration: "none" }}>
              <Panel AUR={AUR} hoverable accentEdge={a.severity === "High"}>
                <div style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: 20, alignItems: "center" }}>
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
                      <span style={{ width: 8, height: 8, borderRadius: "50%", background: a.color, boxShadow: `0 0 12px ${a.color}99` }} />
                      <span style={{ fontFamily: aurMono, fontSize: 10.5, color: a.color, letterSpacing: 0.7, textTransform: "uppercase" }}>{a.severity} · {a.tag}</span>
                    </div>
                    <div style={{ fontFamily: aurSerif, fontSize: 22, fontWeight: 400, color: AUR.text, letterSpacing: -0.4, marginBottom: 8, lineHeight: 1.2 }}>{a.title}</div>
                    <div style={{ color: AUR.textDim, fontSize: 13.5, lineHeight: 1.6, maxWidth: 720 }}>{a.body}</div>
                    <div style={{ display: "flex", alignItems: "baseline", gap: 9, marginTop: 12 }}>
                      <span style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase" }}>Action</span>
                      <span style={{ color: AUR.accent, fontSize: 13 }}>{a.action}</span>
                    </div>
                  </div>
                  <span style={{ color: AUR.textFaint, fontSize: 22, alignSelf: "center" }}>→</span>
                </div>
              </Panel>
            </Link>
          ))}
        </div>
      </AurSection>

      {/* module gateways */}
      <AurSection AUR={AUR} density={densityPreset}
        eyebrow="The operating view"
        title="Five modules, one region."
        lede="Every module reads the same live data. Open one to drill in — the threads will carry you across."
      >
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: densityPreset.gap }}>
          {gateways.map((g) => (
            <Link key={g.to} to={g.to as any} search={((prev:any) => ({ s: prev.s, t: prev.t, d: prev.d })) as any} style={{ textDecoration: "none" }}>
              <Panel AUR={AUR} hoverable style={{ display: "flex", flexDirection: "column", gap: 12, minHeight: 188 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <span style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 0.8, textTransform: "uppercase" }}>{g.eyebrow}</span>
                  <span style={{ width: 8, height: 8, borderRadius: "50%", background: g.status === "good" ? AUR.good : g.status === "warn" ? AUR.warn : g.status === "bad" ? AUR.bad : AUR.textFaint }} />
                </div>
                <div style={{ display: "flex", alignItems: "baseline", gap: 12 }}>
                  <span style={{ fontFamily: aurSerif, fontSize: 46, color: AUR.text, letterSpacing: -1, fontVariantNumeric: "tabular-nums" }}>{g.stat}</span>
                  <span style={{ fontFamily: aurMono, fontSize: 11, color: AUR.textDim, maxWidth: 110, lineHeight: 1.3 }}>{g.statLabel}</span>
                </div>
                <div style={{ fontFamily: aurSerif, fontSize: 23, color: AUR.text, letterSpacing: -0.4 }}>{g.title}</div>
                <div style={{ color: AUR.textDim, fontSize: 13, lineHeight: 1.55, flex: 1 }}>{g.body}</div>
                <div style={{ color: AUR.accent, fontFamily: aurMono, fontSize: 11, letterSpacing: 0.5, textTransform: "uppercase", marginTop: 4 }}>Open module →</div>
              </Panel>
            </Link>
          ))}
        </div>
      </AurSection>
    </>
  );
}

export function Loading({ AUR }: { AUR: any }) {
  return <div style={{ padding: 40, color: AUR.textDim, fontFamily: aurSans }}>Loading scenario…</div>;
}
