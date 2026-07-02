// Module B v2 · Semantic Clusters — cards with Breadcrumb on top and
// "Open related patterns →" links + ThreadNav at the bottom.
// Reads the payload's `clusters` collection: real TF-IDF + cosine components
// computed by src/escalation_semantic_clusters.py in the pipeline.
import { createFileRoute, Link } from "@tanstack/react-router";
import { useDash } from "@/dashboards/app-context";
// @ts-expect-error jsx
import { AurStatusPill, Breadcrumb, ThreadNav, Panel, aurMono, aurSerif } from "@/dashboards/atoms.jsx";
// @ts-expect-error jsx
import { ROOT_CAUSE_FIX, ROOT_CAUSE_DECISION } from "@/dashboards/data-utils.jsx";
import { Loading } from "./_dash.index";

export const Route = createFileRoute("/_dash/clusters")({
  head: () => ({ meta: [
    { title: "Semantic Clusters · Scale Ops" },
    { name: "description", content: "Module B v2: TF-IDF + cosine clusters that catch repeat themes across different root-cause labels." },
  ]}),
  component: Clusters,
});

function Clusters() {
  const { data, AUR, densityPreset } = useDash();
  if (!data) return <Loading AUR={AUR} />;
  const clusters = (data.clusters ?? []).slice(0, 6);

  return (
    <>
      <Breadcrumb AUR={AUR} items={[{ label: "Module B v2 · Clusters" }]} />
      <div>
        <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 0.8, textTransform: "uppercase", marginBottom: 10 }}>Module B v2 · Semantic Clusters</div>
        <h1 style={{ fontFamily: aurSerif, fontSize: 36, fontWeight: 400, letterSpacing: -1, margin: 0, lineHeight: 1.1, color: AUR.text }}>When different teams describe the same breakdown.</h1>
        <p style={{ color: AUR.textDim, fontSize: 14, marginTop: 12, maxWidth: 720, lineHeight: 1.6 }}>
          TF-IDF and cosine similarity find repeat themes that don't share a root-cause label. Each cluster becomes a structural fix card with an owner, a metric to watch, and a decision.
        </p>
      </div>

      {clusters.length === 0 ? (
        <Panel AUR={AUR} style={{ marginTop: densityPreset.sectionGap, textAlign: "center", padding: "48px 24px" }}>
          <div style={{ fontFamily: aurSerif, fontSize: 20, color: AUR.text, marginBottom: 6 }}>No semantic clusters in this scenario</div>
          <div style={{ fontSize: 13, color: AUR.textDim }}>Escalation summaries are too dissimilar to form clusters — a healthy sign.</div>
        </Panel>
      ) : (
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(420px, 1fr))", gap: densityPreset.gap, marginTop: densityPreset.sectionGap }}>
        {clusters.map((c: any) => {
          const fix = ROOT_CAUSE_FIX[c.root_cause] || { fix: "Manager review", owner: "Regional ops", metric: "Escalation count" };
          const decision = ROOT_CAUSE_DECISION[c.root_cause] || "Assign owner + prevention plan";
          const accent = c.risk_level === "High" ? AUR.bad : c.risk_level === "Medium" ? AUR.warn : AUR.accent;
          return (
            <Panel key={c.cluster_id} AUR={AUR} style={{ overflow: "hidden", position: "relative" }}>
              <div style={{ position: "absolute", top: 0, right: 0, width: 130, height: 130, background: `radial-gradient(circle at top right, ${accent}22, transparent 62%)`, pointerEvents: "none" }} />
              <div style={{ position: "relative" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
                  <span style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase" }}>Cluster · {c.cluster_id}{c.cluster_kind === "watchlist_pair" ? " · watchlist" : ""}</span>
                  <AurStatusPill AUR={AUR} status={c.recurrence_status} />
                </div>
                <div style={{ fontFamily: aurSerif, fontSize: 24, color: AUR.text, letterSpacing: -0.4, marginBottom: 8, lineHeight: 1.15 }}>
                  {c.cluster_name}
                </div>
                <div style={{ color: AUR.textDim, fontSize: 13, lineHeight: 1.55, marginBottom: 14 }}>
                  <strong style={{ color: AUR.text }}>{c.incident_count} related incidents</strong> · {c.open_count} open · {c.sev1_count} sev1 + {c.sev2_count} sev2 · spans {c.team_count} teams across {c.segment_count} segments.
                </div>
                {c.sample_summaries[0] && (
                  <div style={{ fontSize: 12.5, color: AUR.textDim, fontStyle: "italic", borderLeft: `2px solid ${AUR.border}`, paddingLeft: 13, marginBottom: 16, lineHeight: 1.5 }}>"{c.sample_summaries[0]}"</div>
                )}
                <div style={{ display: "grid", gridTemplateColumns: "70px 1fr", gap: "10px 14px", fontSize: 12.5, marginBottom: 14 }}>
                  <span style={{ fontFamily: aurMono, fontSize: 10, color: AUR.textFaint, textTransform: "uppercase", letterSpacing: 0.5 }}>Fix</span><span style={{ color: AUR.text }}>{fix.fix}</span>
                  <span style={{ fontFamily: aurMono, fontSize: 10, color: AUR.textFaint, textTransform: "uppercase", letterSpacing: 0.5 }}>Owner</span><span style={{ color: AUR.text }}>{fix.owner}</span>
                  <span style={{ fontFamily: aurMono, fontSize: 10, color: AUR.textFaint, textTransform: "uppercase", letterSpacing: 0.5 }}>Watch</span><span style={{ color: AUR.text }}>{fix.metric}</span>
                </div>
                <div style={{ padding: "12px 15px", background: AUR.accentGlow, borderRadius: 11, borderLeft: `2px solid ${AUR.accent}`, marginBottom: 14 }}>
                  <div style={{ fontFamily: aurMono, fontSize: 10, color: AUR.accent, letterSpacing: 0.6, textTransform: "uppercase", marginBottom: 5 }}>Decision needed this week</div>
                  <div style={{ fontSize: 13, color: AUR.text, lineHeight: 1.45 }}>{decision}</div>
                </div>
                <Link to="/patterns" search={((prev: any) => ({ ...prev, workType: c.work_type })) as any} style={{ color: AUR.accent, fontFamily: aurMono, fontSize: 12, letterSpacing: 0.5, textTransform: "uppercase", textDecoration: "none" }}>Open related patterns →</Link>
              </div>
            </Panel>
          );
        })}
      </div>
      )}

      <ThreadNav AUR={AUR} density={densityPreset} items={[
        { kicker: "Module B", title: "Back to the ranked detector", hint: "All patterns, scored and filterable.", to: "/patterns" },
        { kicker: "Workbench", title: "Audit the raw cluster rows", hint: "Every cluster, sortable and exportable.", to: "/workbench" },
      ]} />
    </>
  );
}
