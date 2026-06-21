// Briefing + About modals. Pure presentational, theme-aware.
import React from "react";
// @ts-expect-error jsx module
import { aurMono, aurSerif, aurSans } from "./atoms.jsx";
// @ts-expect-error jsx module
import { ROOT_CAUSE_LABELS, WORK_TYPE_LABELS, ROOT_CAUSE_DECISION, fmt } from "./data-utils.jsx";

function ModalShell({ onClose, AUR, children, maxWidth = 820 }) {
  return (
    <div onClick={onClose} style={{
      position: "fixed", inset: 0, background: "rgba(10,10,18,0.85)",
      display: "grid", placeItems: "center", padding: 32, zIndex: 100, backdropFilter: "blur(8px)",
    }}>
      <div onClick={(e) => e.stopPropagation()} style={{
        background: AUR.bg, border: `1px solid ${AUR.borderHi}`, borderRadius: 18,
        padding: 36, maxWidth, width: "100%", maxHeight: "90vh", overflow: "auto",
      }}>{children}</div>
    </div>
  );
}

export function BriefingModal({ d, k, AUR, onClose }) {
  return (
    <ModalShell onClose={onClose} AUR={AUR}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20 }}>
        <div>
          <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 1.2, textTransform: "uppercase", marginBottom: 6 }}>Weekly Ops Briefing · {d.region}</div>
          <div style={{ fontFamily: aurSerif, fontSize: 32, fontWeight: 400, letterSpacing: -0.7, color: AUR.text }}>Week of {d.weekStart} → {d.refDate}</div>
        </div>
        <button onClick={onClose} style={{ background: "transparent", border: `1px solid ${AUR.border}`, color: AUR.text, fontFamily: aurSans, fontSize: 12.5, padding: "6px 14px", borderRadius: 999, cursor: "pointer" }}>Close</button>
      </div>
      <div style={{ color: AUR.textDim, fontSize: 14, lineHeight: 1.7 }}>
        <p><Eyebrow AUR={AUR}>Headline</Eyebrow><br /> Region SLA at {fmt.pct(k.sla_adherence)}, CSAT 7-day at {fmt.dec(k.csat_7d, 2)}. {d.totals.escalations} escalations this period · {d.totals.open} open · {d.totals.sev1} sev1.</p>
        <p style={{ marginTop: 18 }}><Eyebrow AUR={AUR}>Top 3 anomalies</Eyebrow></p>
        <ol style={{ paddingLeft: 22, color: AUR.text }}>
          {d.patterns.slice(0, 3).map((p) => (
            <li key={p.pattern_id} style={{ marginBottom: 6 }}>
              <strong>{ROOT_CAUSE_LABELS[p.root_cause]} in {WORK_TYPE_LABELS[p.work_type]} · {p.recurrence_status.toLowerCase()}.</strong>{" "}
              {p.escalation_count} escalations · {p.open_count} open · {p.sev1_count} sev1. {ROOT_CAUSE_DECISION[p.root_cause] || "Assign owner + prevention plan"}.
            </li>
          ))}
        </ol>
        <p style={{ marginTop: 18 }}><Eyebrow AUR={AUR}>Recurring themes</Eyebrow><br /> {Object.entries(d.rootCauseCounts).sort((a,b)=>b[1]-a[1]).slice(0,4).map(([key,v]) => `${ROOT_CAUSE_LABELS[key] || key} (${v})`).join(", ")}.</p>
        <p style={{ marginTop: 18 }}><Eyebrow AUR={AUR}>Decisions this week</Eyebrow><br /> {d.patterns.slice(0, 3).map((p) => `${ROOT_CAUSE_DECISION[p.root_cause] || "Assign owner + prevention plan"} (${WORK_TYPE_LABELS[p.work_type]})`).join(". ")}.</p>
      </div>
      <div style={{ display: "flex", gap: 8, marginTop: 24 }}>
        <button style={{ background: AUR.accent, color: AUR.inkOnAccent, border: "none", borderRadius: 999, padding: "8px 16px", fontFamily: aurSans, fontSize: 12.5, fontWeight: 500, cursor: "pointer" }}>Download Markdown</button>
        <button style={{ background: "transparent", color: AUR.text, border: `1px solid ${AUR.border}`, borderRadius: 999, padding: "8px 16px", fontFamily: aurSans, fontSize: 12.5, cursor: "pointer" }}>Share to leadership</button>
      </div>
    </ModalShell>
  );
}

export function AboutModal({ AUR, onClose }) {
  return (
    <ModalShell onClose={onClose} AUR={AUR} maxWidth={760}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
        <div>
          <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 1.2, textTransform: "uppercase", marginBottom: 6 }}>About this prototype</div>
          <div style={{ fontFamily: aurSerif, fontSize: 32, fontWeight: 400, letterSpacing: -0.8, lineHeight: 1.1, color: AUR.text }}>An operating system for regional ops.</div>
        </div>
        <button onClick={onClose} style={{ background: "transparent", border: `1px solid ${AUR.border}`, color: AUR.text, fontFamily: aurSans, fontSize: 12.5, padding: "6px 14px", borderRadius: 999, cursor: "pointer", flexShrink: 0 }}>Close</button>
      </div>
      <div style={{ color: AUR.textDim, fontSize: 14.5, lineHeight: 1.7 }}>
        <p>Five operating views, one regional command center. The full architecture and the audience-by-audience walkthrough are on the <strong style={{ color: AUR.text }}>About page</strong>. Use the scenario toggle (top right) to see the same modules under Healthy, Current, and Crisis conditions.</p>
      </div>
    </ModalShell>
  );
}

function Eyebrow({ children, AUR }) {
  return <span style={{ color: AUR.accent, fontFamily: aurMono, fontSize: 10.5, letterSpacing: 0.6, textTransform: "uppercase" }}>{children}</span>;
}
