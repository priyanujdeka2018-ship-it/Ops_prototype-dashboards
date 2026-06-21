// Work-type drilldown — Module A detail view. Selected work type lives in
// search params so it's deep-linkable from the health heatmap row arrows.
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { zodValidator, fallback } from "@tanstack/zod-adapter";
import { z } from "zod";
import { useDash } from "@/dashboards/app-context";
// @ts-expect-error jsx
import { AurSection, AurKpi, AurStatusPill, AurRiskBadge, aurMono, aurSerif, aurSans } from "@/dashboards/atoms.jsx";
// @ts-expect-error jsx
import { classifyMetric, WORK_TYPE_LABELS, ROOT_CAUSE_LABELS } from "@/dashboards/data-utils.jsx";
import { Loading } from "./_dash.index";

const search = z.object({
  wt: fallback(z.string(), "expert_review").default("expert_review"),
});

export const Route = createFileRoute("/_dash/drilldown")({
  validateSearch: zodValidator(search),
  head: () => ({ meta: [
    { title: "Work-type Drilldown · Scale Ops" },
    { name: "description", content: "One work type, every team. Find the team carrying the cluster." },
  ]}),
  component: Drill,
});

function Drill() {
  const { data: d, AUR, densityPreset } = useDash();
  const { wt } = Route.useSearch();
  const navigate = useNavigate({ from: "/drilldown" });
  if (!d) return <Loading AUR={AUR} />;

  const workType = d.workTypeRollup.find((r: any) => r.work_type === wt) ? wt : d.workTypeRollup[0].work_type;
  const wtRollup = d.workTypeRollup.find((r: any) => r.work_type === workType);
  const teams = d.teams.filter((t: any) => t.work_type === workType);
  const wtPatterns = d.patterns.filter((p: any) => p.work_type === workType).slice(0, 5);
  const wtEscalations = d.escalations.filter((e: any) => e.work_type === workType);

  const wtRootMix: Record<string, number> = {};
  for (const e of wtEscalations) wtRootMix[e.root_cause_category] = (wtRootMix[e.root_cause_category] || 0) + 1;
  const wtRootSorted = Object.entries(wtRootMix).sort((a, b) => b[1] - a[1]);
  const wtRootMax = wtRootSorted[0]?.[1] || 1;

  return (
    <>
      <AurSection AUR={AUR} density={densityPreset}
        eyebrow={`Module A · ${WORK_TYPE_LABELS[workType]} drilldown`}
        title="Team comparison."
        lede="One work type, every team. SLA, CSAT, quality, escalation pressure — read across to find the one team carrying the cluster."
        right={
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            {d.workTypeRollup.map((w: any) => (
              <button key={w.work_type} onClick={() => navigate({ search: ((prev: any) => ({ ...prev, wt: w.work_type })) as any })}
                style={{
                  background: workType === w.work_type ? AUR.accentGlow : "transparent",
                  color: workType === w.work_type ? AUR.accent : AUR.textDim,
                  border: `1px solid ${workType === w.work_type ? AUR.accent + "55" : AUR.border}`,
                  borderRadius: 999, padding: "6px 14px", fontFamily: aurSans, fontSize: 12.5, cursor: "pointer", fontWeight: 500,
                }}>{WORK_TYPE_LABELS[w.work_type]}</button>
            ))}
          </div>
        }
      >
        <div style={{ display: "grid", gridTemplateColumns: "repeat(6, 1fr)", gap: 12, marginBottom: 18 }}>
          <AurKpi AUR={AUR} label="SLA"      value={`${wtRollup.sla.toFixed(1)}%`}     sub="target ≥ 92%" status={classifyMetric("sla", wtRollup.sla)} />
          <AurKpi AUR={AUR} label="CSAT"     value={wtRollup.csat.toFixed(2)}          sub="target ≥ 4.3" status={classifyMetric("csat", wtRollup.csat)} />
          <AurKpi AUR={AUR} label="Quality"  value={wtRollup.quality.toFixed(1)}       sub="100-pt"        status={classifyMetric("quality", wtRollup.quality)} />
          <AurKpi AUR={AUR} label="Esc / 1k" value={wtRollup.escalation_rate_per_1000} sub={`${wtRollup.escalations} total`} status={classifyMetric("escalation_rate", wtRollup.escalation_rate_per_1000)} />
          <AurKpi AUR={AUR} label="Open"     value={wtRollup.open_escalations}         sub="needs closure" status={classifyMetric("open", wtRollup.open_escalations)} />
          <AurKpi AUR={AUR} label="Sev 1"    value={wtRollup.sev1}                     sub="critical"      status={classifyMetric("sev1", wtRollup.sev1)} />
        </div>

        <div style={{ background: AUR.surface, border: `1px solid ${AUR.border}`, borderRadius: 16, overflow: "hidden" }}>
          <div style={{ display: "grid", gridTemplateColumns: "1.8fr 0.8fr 0.5fr 0.6fr 0.6fr 0.6fr 0.6fr 0.6fr", padding: "14px 22px", borderBottom: `1px solid ${AUR.border}`, fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase" }}>
            <div>Team · manager</div><div>City</div><div style={{ textAlign: "right" }}>Heads</div><div style={{ textAlign: "right" }}>SLA</div><div style={{ textAlign: "right" }}>CSAT</div><div style={{ textAlign: "right" }}>Quality</div><div style={{ textAlign: "right" }}>Open</div><div style={{ textAlign: "right" }}>Sev1</div>
          </div>
          {teams.map((t: any, i: number, arr: any[]) => (
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

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: densityPreset.gap, marginTop: densityPreset.sectionGap }}>
        <AurSection AUR={AUR} density={{ ...densityPreset, sectionGap: 0 }} eyebrow="Delay reasons" title="Why escalations stick.">
          <div style={{ background: AUR.surface, border: `1px solid ${AUR.border}`, borderRadius: 14, padding: 20 }}>
            <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase", marginBottom: 12 }}>Root-cause mix · {wtEscalations.length} escalations</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {wtRootSorted.map(([rc, c]: any) => (
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

        <AurSection AUR={AUR} density={{ ...densityPreset, sectionGap: 0 }} eyebrow="Top patterns in this work type" title="What's recurring.">
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {wtPatterns.map((p: any) => (
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
