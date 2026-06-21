// AppShell: roomy sidebar (logo + region/scenario + nav rail + scenario/accent/
// density controls + briefing + about), minimal top bar (status chips only).
// All env controls live in the sidebar to keep screen real estate for the
// user's trail of thought.
import React, { useState } from "react";
import { Link, useNavigate, useRouterState } from "@tanstack/react-router";
import { useDash, type ScenarioId, type ThemeId, type DensityId } from "./app-context";
// @ts-expect-error jsx module
import { aurMono, aurSans, aurSerif, AurChip, AurButton } from "./atoms.jsx";
// @ts-expect-error jsx module
import { THEME_PRESETS, DENSITY_PRESETS } from "./data-utils.jsx";
// @ts-expect-error jsx module
import { BriefingModal, AboutModal } from "./modals.jsx";

const NAV = [
  { to: "/",          badge: "00", label: "Home",       desc: "Command center" },
  { to: "/health",    badge: "A",  label: "Health",     desc: "Regional rollup" },
  { to: "/patterns",  badge: "B",  label: "Patterns",   desc: "Recurrence" },
  { to: "/clusters",  badge: "B2", label: "Clusters",   desc: "Semantic" },
  { to: "/workforce", badge: "C",  label: "Workforce",  desc: "Quality risk" },
  { to: "/capacity",  badge: "D",  label: "Capacity",   desc: "SLA forecast" },
  { to: "/drilldown", badge: "A·d",label: "Drilldown",  desc: "Work-type detail" },
  { to: "/about",     badge: "··", label: "About",      desc: "Audience + production" },
] as const;

export function AppShell({ children }: { children: React.ReactNode }) {
  const { AUR, densityPreset, density, theme, scenario, data, loading } = useDash();
  const [showBriefing, setShowBriefing] = useState(false);
  const [showAbout, setShowAbout] = useState(false);
  const navigate = useNavigate();
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  const updateSearch = (patch: Partial<{ s: ScenarioId; t: ThemeId; d: DensityId }>) => {
    navigate({ to: pathname as any, search: ((prev: any) => ({ ...prev, ...patch })) as any });
  };

  const padX = densityPreset.padX;
  const padY = densityPreset.padY;

  return (
    <div style={{
      minHeight: "100vh", background: AUR.bg, color: AUR.text,
      fontFamily: aurSans, fontSize: densityPreset.fontBody,
      display: "grid", gridTemplateColumns: "264px 1fr", position: "relative",
    }}>
      {/* ambient glow */}
      <div style={{ position: "fixed", top: -200, right: -200, width: 700, height: 700, borderRadius: "50%", background: `radial-gradient(circle, ${AUR.accent}30 0%, transparent 65%)`, pointerEvents: "none", zIndex: 0 }} />
      <div style={{ position: "fixed", bottom: -300, left: -150, width: 800, height: 800, borderRadius: "50%", background: `radial-gradient(circle, ${AUR.good}15 0%, transparent 60%)`, pointerEvents: "none", zIndex: 0 }} />

      {/* sidebar */}
      <aside style={{
        position: "sticky", top: 0, height: "100vh", padding: "22px 14px 18px",
        borderRight: `1px solid ${AUR.border}`, background: "rgba(8,8,14,0.65)",
        backdropFilter: "blur(12px)", zIndex: 2, display: "flex", flexDirection: "column",
        overflowY: "auto",
      }}>
        <Link to="/" search={((prev: any) => prev) as any} style={{ display: "flex", alignItems: "center", gap: 10, textDecoration: "none", color: AUR.text, padding: "0 8px 16px" }}>
          <div style={{ width: 30, height: 30, borderRadius: 8, background: `linear-gradient(135deg, ${AUR.accent}, ${AUR.accentDeep})`, display: "grid", placeItems: "center", fontFamily: aurSerif, fontSize: 16, color: AUR.inkOnAccent }}>S</div>
          <div>
            <div style={{ fontFamily: aurSerif, fontSize: 15, color: AUR.text, lineHeight: 1.1 }}>Scale Ops</div>
            <div style={{ fontFamily: aurMono, fontSize: 9, color: AUR.textFaint, letterSpacing: 0.5, textTransform: "uppercase" }}>Command Center</div>
          </div>
        </Link>

        {/* Region / scenario summary */}
        <div style={{ margin: "0 4px 14px", padding: "11px 13px", borderRadius: 12, background: AUR.surface, border: `1px solid ${AUR.border}`, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div>
            <div style={{ fontFamily: aurMono, fontSize: 9, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase" }}>Region</div>
            <div style={{ fontFamily: aurSerif, fontSize: 18, color: AUR.text, letterSpacing: -0.3 }}>{data ? data.region : "APAC"}</div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{ width: 7, height: 7, borderRadius: "50%", background: scenario === "healthy" ? AUR.good : scenario === "crisis" ? AUR.bad : AUR.warn, boxShadow: `0 0 8px ${scenario === "healthy" ? AUR.good : scenario === "crisis" ? AUR.bad : AUR.warn}` }} />
            <span style={{ fontFamily: aurMono, fontSize: 10, color: scenario === "healthy" ? AUR.good : scenario === "crisis" ? AUR.bad : AUR.warn, textTransform: "capitalize" }}>{scenario}</span>
          </div>
        </div>

        {/* nav rail */}
        <nav style={{ display: "flex", flexDirection: "column", gap: 2, padding: "0 2px", marginBottom: 14 }}>
          <div style={{ fontFamily: aurMono, fontSize: 9.5, color: AUR.textFaint, letterSpacing: 0.8, textTransform: "uppercase", padding: "6px 10px 6px" }}>Modules</div>
          {NAV.map((n) => {
            const active = pathname === n.to || (n.to !== "/" && pathname.startsWith(n.to));
            return (
              <Link
                key={n.to} to={n.to as any}
                search={((prev: any) => ({ s: prev.s, t: prev.t, d: prev.d })) as any}
                style={{
                  textDecoration: "none", padding: "9px 10px", borderRadius: 10,
                  background: active ? AUR.accentSoft : "transparent",
                  border: `1px solid ${active ? AUR.accent + "44" : "transparent"}`,
                  display: "flex", alignItems: "center", gap: 11, transition: "background 150ms ease",
                }}
              >
                <span style={{ width: 26, height: 22, flexShrink: 0, borderRadius: 6, display: "grid", placeItems: "center", fontFamily: aurMono, fontSize: 10, fontWeight: 600, color: active ? AUR.inkOnAccent : AUR.textDim, background: active ? AUR.accent : AUR.surfaceHi, letterSpacing: 0.3 }}>{n.badge}</span>
                <span style={{ minWidth: 0 }}>
                  <span style={{ display: "block", fontSize: 13, color: active ? AUR.text : AUR.textDim, fontWeight: active ? 600 : 400 }}>{n.label}</span>
                  <span style={{ display: "block", fontFamily: aurMono, fontSize: 9.5, color: active ? AUR.accent : AUR.textFaint, letterSpacing: 0.4, marginTop: 1 }}>{n.desc}</span>
                </span>
              </Link>
            );
          })}
        </nav>

        {/* Controls — sidebar location keeps top bar clear */}
        <div style={{ padding: "12px 4px 0", borderTop: `1px solid ${AUR.border}`, display: "flex", flexDirection: "column", gap: 14 }}>
          <SideControl label="Scenario" AUR={AUR}>
            <SegRow AUR={AUR}>
              {(["healthy","current","crisis"] as ScenarioId[]).map((s) => (
                <SegBtn key={s} active={scenario === s} AUR={AUR} onClick={() => updateSearch({ s })}>{s[0].toUpperCase() + s.slice(1)}</SegBtn>
              ))}
            </SegRow>
          </SideControl>

          <SideControl label="Accent" AUR={AUR}>
            <div style={{ display: "flex", gap: 7, padding: "2px 4px" }}>
              {Object.values(THEME_PRESETS).map((tp: any) => (
                <button key={tp.id} title={tp.label} onClick={() => updateSearch({ t: tp.id })} style={{
                  width: 20, height: 20, borderRadius: "50%", background: tp.accent, cursor: "pointer",
                  border: theme === tp.id ? `2px solid ${AUR.text}` : `2px solid transparent`,
                  boxShadow: theme === tp.id ? `0 0 10px ${tp.accent}99` : "none",
                  padding: 0,
                }} />
              ))}
            </div>
          </SideControl>

          <SideControl label="Density" AUR={AUR}>
            <SegRow AUR={AUR}>
              {(Object.values(DENSITY_PRESETS) as any[]).map((dp) => (
                <SegBtn key={dp.id} active={density === dp.id} AUR={AUR} onClick={() => updateSearch({ d: dp.id })}>{dp.label}</SegBtn>
              ))}
            </SegRow>
          </SideControl>
        </div>

        <div style={{ marginTop: "auto", padding: "14px 4px 0", borderTop: `1px solid ${AUR.border}`, display: "flex", flexDirection: "column", gap: 8 }}>
          <button onClick={() => setShowBriefing(true)} style={{
            background: AUR.accent, color: AUR.inkOnAccent, border: "none", borderRadius: 10,
            padding: "10px 12px", fontFamily: aurSans, fontSize: 12.5, fontWeight: 600, cursor: "pointer",
            display: "flex", alignItems: "center", justifyContent: "center", gap: 7,
          }}>↗ Weekly briefing</button>
          <button onClick={() => setShowAbout(true)} style={{
            background: "transparent", border: `1px solid ${AUR.border}`, color: AUR.textDim,
            borderRadius: 10, padding: "9px 12px", fontFamily: aurSans, fontSize: 12, cursor: "pointer",
          }}>About this prototype</button>
        </div>
      </aside>

      {/* main */}
      <div style={{ position: "relative", zIndex: 1, padding: `${padY}px ${padX}px ${padY + 24}px`, minWidth: 0 }}>
        <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 24, marginBottom: 24, flexWrap: "wrap" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
            <AurChip AUR={AUR} color={AUR.good}><span style={{ width: 6, height: 6, borderRadius: "50%", background: AUR.good, boxShadow: `0 0 8px ${AUR.good}` }} />Live</AurChip>
            {data && <AurChip AUR={AUR}>{data.region}</AurChip>}
            {data && <AurChip AUR={AUR}>Week of {data.weekStart} → {data.refDate}</AurChip>}
            {loading && <span style={{ fontFamily: aurMono, fontSize: 10, color: AUR.textFaint }}>loading scenario…</span>}
          </div>
        </header>

        <main style={{ maxWidth: 1480 }}>{children}</main>
      </div>

      {showBriefing && data && <BriefingModal d={data} k={data.kpis} AUR={AUR} onClose={() => setShowBriefing(false)} />}
      {showAbout && <AboutModal AUR={AUR} onClose={() => setShowAbout(false)} />}
    </div>
  );
}

function SideControl({ label, children, AUR }: any) {
  return (
    <div>
      <div style={{ fontFamily: aurMono, fontSize: 9, color: AUR.textFaint, letterSpacing: 0.7, textTransform: "uppercase", marginBottom: 6, padding: "0 4px" }}>{label}</div>
      {children}
    </div>
  );
}

function SegRow({ children, AUR }: any) {
  return <div style={{ display: "flex", gap: 2, padding: 3, background: AUR.surface, border: `1px solid ${AUR.border}`, borderRadius: 999 }}>{children}</div>;
}

function SegBtn({ active, AUR, onClick, children }: any) {
  return (
    <button onClick={onClick} style={{
      flex: 1, background: active ? AUR.accent : "transparent",
      color: active ? AUR.inkOnAccent : AUR.textDim,
      border: "none", borderRadius: 999, padding: "5px 8px",
      fontFamily: aurSans, fontSize: 10.5, fontWeight: 500, cursor: "pointer",
      transition: "all 180ms ease", whiteSpace: "nowrap",
    }}>{children}</button>
  );
}
