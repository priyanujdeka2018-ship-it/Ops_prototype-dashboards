// About — audience-aware framing for the interview. Each role gets a lens
// showing what they'd open first, which KPIs they care about, and how AI
// would land in a production version.
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { zodValidator, fallback } from "@tanstack/zod-adapter";
import { z } from "zod";
import { useDash } from "@/dashboards/app-context";
// @ts-expect-error jsx
import { AurSection, aurMono, aurSerif, aurSans } from "@/dashboards/atoms.jsx";
// @ts-expect-error jsx
import { AUDIENCE_LENS } from "@/dashboards/data-utils.jsx";

const search = z.object({
  who: fallback(z.string(), "regional_ops_lead").default("regional_ops_lead"),
});

export const Route = createFileRoute("/_dash/about")({
  validateSearch: zodValidator(search),
  head: () => ({ meta: [
    { title: "About · Scale Ops Command Center" },
    { name: "description", content: "Why this dashboard exists, how each role would use it, and what changes for a production deployment." },
  ]}),
  component: About,
});

function About() {
  const { AUR, densityPreset } = useDash();
  const { who } = Route.useSearch();
  const navigate = useNavigate({ from: "/about" });
  const active = AUDIENCE_LENS.find((a: any) => a.id === who) || AUDIENCE_LENS[0];

  return (
    <>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontFamily: aurSerif, fontSize: 40, fontWeight: 400, letterSpacing: -1.2, margin: 0, lineHeight: 1.05, maxWidth: 880, color: AUR.text }}>
          Built for a 60-day operating view — and for the interview that comes first.
        </h1>
        <p style={{ color: AUR.textDim, fontSize: 15, marginTop: 14, maxWidth: 760, lineHeight: 1.6 }}>
          Five modules, five operating questions. Below: how each role would land here on Monday morning, and how AI augments the job without making decisions for them.
        </p>
      </div>

      <AurSection AUR={AUR} density={densityPreset} eyebrow="Audience" title="Switch lens.">
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          {AUDIENCE_LENS.map((a: any) => (
            <button key={a.id} onClick={() => navigate({ search: ((prev: any) => ({ ...prev, who: a.id })) as any })}
              style={{
                background: who === a.id ? AUR.accent : "transparent",
                color: who === a.id ? AUR.inkOnAccent : AUR.text,
                border: `1px solid ${who === a.id ? AUR.accent : AUR.border}`,
                borderRadius: 999, padding: "8px 18px", fontFamily: aurSans, fontSize: 13, fontWeight: 500, cursor: "pointer",
              }}
            >{a.title}</button>
          ))}
        </div>
      </AurSection>

      <AurSection AUR={AUR} density={densityPreset} eyebrow={active.title} title={active.blurb}>
        <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: densityPreset.gap }}>
          <div style={{ background: AUR.surface, border: `1px solid ${AUR.border}`, borderRadius: 14, padding: 24 }}>
            <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 0.7, textTransform: "uppercase", marginBottom: 10 }}>How AI lands in production</div>
            <p style={{ color: AUR.text, fontSize: 14.5, lineHeight: 1.65, margin: 0 }}>{active.ai_leverage}</p>

            <div style={{ marginTop: 24, paddingTop: 20, borderTop: `1px solid ${AUR.border}` }}>
              <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.7, textTransform: "uppercase", marginBottom: 10 }}>Where decisions stay human</div>
              <ul style={{ color: AUR.textDim, fontSize: 14, lineHeight: 1.7, paddingLeft: 20, margin: 0 }}>
                <li>Risk scoring is deterministic, explainable, reversible.</li>
                <li>LLM scope is bounded: summarization + clustering + briefing draft.</li>
                <li>Every recommendation names an owner and a watch metric.</li>
                <li>Nothing auto-fires. Manager opens, reviews, approves.</li>
              </ul>
            </div>
          </div>

          <div style={{ background: AUR.surface, border: `1px solid ${AUR.border}`, borderRadius: 14, padding: 24 }}>
            <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 0.7, textTransform: "uppercase", marginBottom: 10 }}>First clicks for this role</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {active.opens.map((to: string) => (
                <Link key={to} to={to as any} search={((prev:any)=>prev) as any}
                  style={{ textDecoration: "none", color: AUR.text, padding: "12px 14px", border: `1px solid ${AUR.border}`, borderRadius: 10, display: "flex", justifyContent: "space-between", alignItems: "center" }}
                >
                  <span style={{ fontFamily: aurSerif, fontSize: 18 }}>{to}</span>
                  <span style={{ color: AUR.accent, fontFamily: aurMono, fontSize: 11, letterSpacing: 0.5, textTransform: "uppercase" }}>Open →</span>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </AurSection>

      <AurSection AUR={AUR} density={densityPreset} eyebrow="Production notes" title="What changes between this prototype and a live deploy.">
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: densityPreset.gap }}>
          {[
            { t: "Data pipeline", b: "Streamlit/Python pipeline in the repo generates the JSON snapshots. In production: nightly Airflow DAG → object storage → cached read at the edge. Forecast jobs run with confidence bands and quality gates." },
            { t: "Auth & permissions", b: "Single-tenant prototype. Production: SSO + role-based scopes so a quality lead sees only their region's teams, a workforce planner sees only their work types." },
            { t: "AI scope", b: "Embedding-based clustering on escalation summaries (Module B v2) and LLM-drafted weekly briefing. Everything else — risk scores, thresholds, recommendations — stays deterministic. Audit trail on every AI-generated artifact." },
            { t: "Performance", b: "Static JSON keeps this prototype instant. In production: server functions per module, query cache, intentful preloading on hover so navigating between modules feels free." },
            { t: "Extensibility", b: "New modules slot in as new routes under the same shell. Theme, density, and scenario are search params, so any deep link carries presentation context." },
            { t: "Failure modes", b: "Snapshot is missing → fallback to last known. AI summary fails → show the deterministic table. Threshold breach during incident → escalate via the same briefing channel, not a new tool." },
          ].map((n) => (
            <div key={n.t} style={{ background: AUR.surface, border: `1px solid ${AUR.border}`, borderRadius: 14, padding: 22 }}>
              <div style={{ fontFamily: aurSerif, fontSize: 19, color: AUR.text, marginBottom: 8 }}>{n.t}</div>
              <div style={{ color: AUR.textDim, fontSize: 13.5, lineHeight: 1.6 }}>{n.b}</div>
            </div>
          ))}
        </div>
      </AurSection>
    </>
  );
}
