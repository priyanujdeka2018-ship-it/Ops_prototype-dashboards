// Atom design primitives — themed via AUR object built from a theme preset.
import React from "react";
import { Link } from "@tanstack/react-router";

export const aurSans  = `"Geist", "Geist Sans", ui-sans-serif, system-ui, sans-serif`;
export const aurSerif = `"Instrument Serif", "Source Serif Pro", Georgia, serif`;
export const aurMono  = `"Geist Mono", "JetBrains Mono", ui-monospace, monospace`;

export function buildAurTheme(themePreset) {
  return {
    bg: "#0A0A12",
    surface: "rgba(255,255,255,0.025)",
    surfaceHi: "rgba(255,255,255,0.045)",
    border: "rgba(255,255,255,0.08)",
    borderHi: "rgba(255,255,255,0.15)",
    text: "#F5F5F0",
    textDim: "#B7B5AA",
    textFaint: "#6E6C66",
    accent: themePreset.accent,
    accentDeep: themePreset.accentDeep,
    accentGlow: themePreset.accent + "30",
    accentSoft: themePreset.accent + "18",
    inkOnAccent: themePreset.inkOnAccent,
    good: "#5EEAD4",
    warn: "#FBBF77",
    bad: "#F87171",
  };
}

const statusColor = (s, AUR) => s === "good" ? AUR.good : s === "warn" ? AUR.warn : s === "bad" ? AUR.bad : s === "info" ? AUR.accent : AUR.textFaint;

export function AurChip({ children, color, bg, AUR }) {
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 6, padding: "3px 10px",
      borderRadius: 999, background: bg || AUR.surface, color: color || AUR.textDim,
      fontFamily: aurMono, fontSize: 10.5, letterSpacing: 0.5, textTransform: "uppercase",
      border: `1px solid ${AUR.border}`,
    }}>{children}</span>
  );
}

export function AurStatusPill({ status, AUR }) {
  const map = {
    Accelerating:   { c: AUR.bad,  label: "Accelerating" },
    Recurring:      { c: AUR.warn, label: "Recurring" },
    Watchlist:      { c: AUR.warn, label: "Watchlist" },
    New:            { c: AUR.accent, label: "New" },
    Resolved:       { c: AUR.good, label: "Resolved" },
    Dormant:        { c: AUR.textFaint, label: "Dormant" },
    "Low activity": { c: AUR.textFaint, label: "Low activity" },
  };
  const m = map[status] || { c: AUR.textFaint, label: status };
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 6, padding: "3px 10px",
      borderRadius: 999, background: m.c + "18", color: m.c, fontFamily: aurMono,
      fontSize: 10.5, letterSpacing: 0.5, textTransform: "uppercase", border: `1px solid ${m.c}40`,
    }}>
      <span style={{ width: 6, height: 6, borderRadius: "50%", background: m.c }} />
      {m.label}
    </span>
  );
}

export function AurRiskBadge({ level, AUR }) {
  const c = level === "High" ? AUR.bad : level === "Medium" ? AUR.warn : level === "Insufficient" ? AUR.textFaint : AUR.good;
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", padding: "3px 10px", borderRadius: 999,
      background: c + "18", color: c, fontFamily: aurMono, fontSize: 10.5,
      letterSpacing: 0.5, textTransform: "uppercase", border: `1px solid ${c}40`, whiteSpace: "nowrap",
    }}>{level}</span>
  );
}

export function ForecastPill({ forecast, AUR }) {
  const c = forecast === "Recovery needed" ? AUR.bad
    : forecast === "At risk" ? AUR.bad
    : forecast === "Watchlist" ? AUR.warn
    : forecast === "Likely stable" ? AUR.good
    : AUR.textFaint;
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 6, padding: "4px 11px",
      borderRadius: 999, background: c + "14", color: c, fontFamily: aurMono,
      fontSize: 10.5, letterSpacing: 0.3, border: `1px solid ${c}40`, whiteSpace: "nowrap",
    }}>
      <span style={{ width: 6, height: 6, borderRadius: "50%", background: c, boxShadow: `0 0 8px ${c}88` }} />
      SLA {forecast.toLowerCase()}
    </span>
  );
}

import { Sparkline } from "./data-utils";

export function AurKpi({ label, value, sub, status = "good", trendData, large = false, AUR }) {
  const dotColor = statusColor(status, AUR);
  return (
    <div style={{
      background: AUR.surface, border: `1px solid ${AUR.border}`, borderRadius: 14,
      padding: large ? "18px 20px" : "14px 16px", position: "relative", overflow: "hidden",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
        <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.6, textTransform: "uppercase" }}>{label}</div>
        <span style={{ width: 6, height: 6, borderRadius: "50%", background: dotColor, boxShadow: `0 0 8px ${dotColor}66` }} />
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: 12 }}>
        <div style={{ fontFamily: aurSerif, fontSize: large ? 42 : 28, fontWeight: 400, letterSpacing: -1, lineHeight: 1, color: AUR.text, fontVariantNumeric: "tabular-nums" }}>{value}</div>
        {trendData && trendData.length > 1 && (
          <Sparkline values={trendData} color={dotColor} width={large ? 80 : 60} height={large ? 28 : 22} fill strokeWidth={1.5} />
        )}
      </div>
      {sub && <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.4, marginTop: 8 }}>{sub}</div>}
    </div>
  );
}

export function AurSection({ eyebrow, title, lede, right, children, AUR, density }) {
  const gapBelow = density?.sectionGap || 32;
  return (
    <section style={{ marginTop: gapBelow }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: 18, gap: 24, flexWrap: "wrap" }}>
        <div style={{ minWidth: 0, flex: 1 }}>
          {eyebrow && <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 0.8, textTransform: "uppercase", marginBottom: 8 }}>{eyebrow}</div>}
          {title && <h2 style={{ fontFamily: aurSerif, fontSize: 30, fontWeight: 400, letterSpacing: -0.7, margin: 0, lineHeight: 1.1, color: AUR.text }}>{title}</h2>}
          {lede && <p style={{ fontFamily: aurSans, fontSize: 13.5, color: AUR.textDim, marginTop: 8, maxWidth: 720, lineHeight: 1.55 }}>{lede}</p>}
        </div>
        {right}
      </div>
      {children}
    </section>
  );
}

export function AurButton({ children, variant = "ghost", onClick, active = false, AUR }) {
  const styles = {
    ghost:   { background: active ? AUR.surfaceHi : "transparent", color: AUR.text, border: `1px solid ${active ? AUR.borderHi : AUR.border}` },
    primary: { background: AUR.accent, color: AUR.inkOnAccent, border: "none" },
    chip:    { background: active ? AUR.accentGlow : "transparent", color: active ? AUR.accent : AUR.textDim, border: `1px solid ${active ? AUR.accent + "55" : AUR.border}` },
  }[variant] || {};
  return (
    <button onClick={onClick} style={{
      ...styles, borderRadius: 999, padding: "8px 16px", fontFamily: aurSans,
      fontSize: 12.5, fontWeight: 500, cursor: "pointer", transition: "all 180ms ease",
    }}>{children}</button>
  );
}

export function MetricCell({ value, status, sub, AUR }) {
  const color = statusColor(status, AUR);
  return (
    <div style={{
      textAlign: "center", padding: "10px 8px", borderRadius: 10,
      background: color + "12", border: `1px solid ${color}28`,
    }}>
      <div style={{ fontFamily: aurMono, fontSize: 13, color, fontVariantNumeric: "tabular-nums" }}>{value}</div>
      {sub && <div style={{ fontFamily: aurMono, fontSize: 9, color: AUR.textFaint, letterSpacing: 0.4, marginTop: 3, textTransform: "uppercase" }}>{sub}</div>}
    </div>
  );
}

// ─── Breadcrumb ─────────────────────────────────────────────────────────────
export function Breadcrumb({ items, AUR }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 9, flexWrap: "wrap", marginBottom: 22 }}>
      {items.map((it, i) => {
        const last = i === items.length - 1;
        const linkStyle = {
          background: "transparent", border: "none", padding: 0, cursor: "pointer",
          fontFamily: aurMono, fontSize: 11, color: AUR.textDim, letterSpacing: 0.4, textDecoration: "none",
        };
        const staticStyle = {
          fontFamily: aurMono, fontSize: 11,
          color: last ? AUR.accent : AUR.textFaint, letterSpacing: 0.4,
        };
        return (
          <React.Fragment key={i}>
            {it.to && !last ? (
              <Link to={it.to} search={it.search || ((prev) => prev)} style={linkStyle}>{it.label}</Link>
            ) : it.onClick && !last ? (
              <button onClick={it.onClick} style={linkStyle}>{it.label}</button>
            ) : (
              <span style={staticStyle}>{it.label}</span>
            )}
            {!last && <span style={{ color: AUR.textFaint, fontSize: 11 }}>/</span>}
          </React.Fragment>
        );
      })}
    </div>
  );
}

// ─── ThreadNav — "follow the thread" cards ──────────────────────────────────
export function ThreadNav({ items, label = "Follow the thread", AUR, density }) {
  if (!items || !items.length) return null;
  const gap = density?.sectionGap || 32;
  return (
    <div style={{ marginTop: gap, paddingTop: gap * 0.7, borderTop: `1px solid ${AUR.border}` }}>
      <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, letterSpacing: 0.8, textTransform: "uppercase", marginBottom: 16 }}>{label}</div>
      <div style={{ display: "grid", gridTemplateColumns: `repeat(${Math.min(items.length, 3)}, 1fr)`, gap: 14 }}>
        {items.map((it, i) => <ThreadCard key={i} {...it} AUR={AUR} />)}
      </div>
    </div>
  );
}

export function ThreadCard({ kicker, title, hint, to, search, onClick, AUR }) {
  const [hov, setHov] = React.useState(false);
  const inner = (
    <>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <span style={{ fontFamily: aurMono, fontSize: 10, color: AUR.accent, letterSpacing: 0.8, textTransform: "uppercase" }}>{kicker}</span>
        <span style={{ color: hov ? AUR.accent : AUR.textFaint, fontSize: 17, transition: "transform 170ms ease, color 170ms ease", transform: hov ? "translateX(3px)" : "none" }}>→</span>
      </div>
      <div style={{ fontFamily: aurSerif, fontSize: 19, color: AUR.text, letterSpacing: -0.3, lineHeight: 1.2, marginTop: 6 }}>{title}</div>
      {hint && <div style={{ fontFamily: aurSans, fontSize: 12.5, color: AUR.textDim, lineHeight: 1.5, marginTop: 6 }}>{hint}</div>}
    </>
  );
  const base = {
    textAlign: "left", cursor: "pointer", background: hov ? AUR.accentSoft : AUR.surface,
    border: `1px solid ${hov ? AUR.accent + "55" : AUR.border}`, borderRadius: 14,
    padding: "14px 18px", transition: "all 170ms ease",
    transform: hov ? "translateY(-2px)" : "none",
    display: "block", textDecoration: "none", color: AUR.text,
  };
  if (to) {
    return (
      <Link to={to} search={search || ((prev) => prev)} onMouseEnter={() => setHov(true)} onMouseLeave={() => setHov(false)} style={base}>{inner}</Link>
    );
  }
  return (
    <button onClick={onClick} onMouseEnter={() => setHov(true)} onMouseLeave={() => setHov(false)} style={{ ...base, width: "100%" }}>{inner}</button>
  );
}

// ─── RiskMeter / DriverBars ─────────────────────────────────────────────────
export function RiskMeter({ score, max = 120, AUR }) {
  const c = score >= max * 0.6 ? AUR.bad : score >= max * 0.32 ? AUR.warn : AUR.good;
  const pct = Math.max(2, Math.min(100, (score / max) * 100));
  return (
    <div style={{ height: 5, background: AUR.surfaceHi, borderRadius: 5, overflow: "hidden" }}>
      <div style={{ width: `${pct}%`, height: "100%", background: c, borderRadius: 5 }} />
    </div>
  );
}

export function DriverBars({ drivers, max = 6, AUR }) {
  const top = drivers.slice(0, max);
  const mx = Math.max(...top.map((d) => Math.abs(d.w)), 1);
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      {top.map((d, i) => {
        const neg = d.w < 0;
        const a = Math.abs(d.w);
        const c = a > mx * 0.6 ? AUR.bad : a > mx * 0.3 ? AUR.warn : AUR.accent;
        const pct = Math.max(2, Math.min(100, (a / mx) * 100));
        return (
          <div key={i} style={{ display: "grid", gridTemplateColumns: "1fr 92px", gap: 14, alignItems: "center" }}>
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 5 }}>
                <span style={{ fontSize: 12.5, color: AUR.textDim }}>{d.k}</span>
                <span style={{ fontFamily: aurMono, fontSize: 11, color: AUR.text }}>{d.v}{d.unit || ""}</span>
              </div>
              <div style={{ height: 5, background: AUR.surfaceHi, borderRadius: 5, overflow: "hidden" }}>
                <div style={{ width: `${pct}%`, height: "100%", background: neg ? AUR.textFaint : c, borderRadius: 5 }} />
              </div>
            </div>
            <span style={{ fontFamily: aurMono, fontSize: 11, color: AUR.textFaint, textAlign: "right" }}>+{Math.round(a)} pts</span>
          </div>
        );
      })}
    </div>
  );
}

// ─── PillRow ────────────────────────────────────────────────────────────────
export function PillRow({ options, value, onChange, getLabel, getCount, AUR }) {
  return (
    <div style={{ display: "flex", gap: 7, flexWrap: "wrap" }}>
      {options.map((o) => {
        const active = o === value;
        return (
          <button key={String(o)} onClick={() => onChange(o)} style={{
            background: active ? AUR.accentGlow : "transparent",
            color: active ? AUR.accent : AUR.textDim,
            border: `1px solid ${active ? AUR.accent + "55" : AUR.border}`,
            borderRadius: 999, padding: "6px 13px", fontFamily: aurSans, fontSize: 12,
            cursor: "pointer", fontWeight: 500, whiteSpace: "nowrap",
          }}>
            {getLabel ? getLabel(o) : o}
            {getCount && <span style={{ color: AUR.textFaint, marginLeft: 6 }}>{getCount(o)}</span>}
          </button>
        );
      })}
    </div>
  );
}

// ─── CoachingCard ───────────────────────────────────────────────────────────
export function CoachingCard({ c, AUR }) {
  const accent = c.riskLevel === "High" ? AUR.bad : AUR.warn;
  return (
    <div style={{ background: AUR.surface, border: `1px solid ${AUR.border}`, borderRadius: 14, padding: 18 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10, gap: 12 }}>
        <div>
          <div style={{ fontFamily: aurSans, fontSize: 14.5, color: AUR.text, fontWeight: 600 }}>{c.name}</div>
          <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.textFaint, marginTop: 2 }}>{c.id} · {c.skill} · {c.tenure}d tenure{c.lowTenure ? " · ramping" : ""}</div>
        </div>
        <AurRiskBadge level={c.riskLevel} AUR={AUR} />
      </div>
      <div style={{ display: "flex", gap: 14, flexWrap: "wrap", marginBottom: 12 }}>
        {[["Quality", c.quality], ["Gold", `${c.goldPass}%`], ["Override", `${c.override}%`], ["Rework", `${c.rework}%`], ["Peer", `${c.peer}%`]].map(([l, v], i) => (
          <div key={i}>
            <div style={{ fontFamily: aurMono, fontSize: 9.5, color: AUR.textFaint, letterSpacing: 0.4, textTransform: "uppercase" }}>{l}</div>
            <div style={{ fontFamily: aurMono, fontSize: 13, color: AUR.text }}>{v}</div>
          </div>
        ))}
      </div>
      <div style={{ padding: "10px 13px", background: accent + "12", borderRadius: 10, borderLeft: `2px solid ${accent}` }}>
        <div style={{ fontFamily: aurMono, fontSize: 9.5, color: accent, letterSpacing: 0.6, textTransform: "uppercase" }}>Suggested support · driver: {c.topDriver.toLowerCase()}</div>
        <div style={{ fontSize: 13, color: AUR.text, marginTop: 4, lineHeight: 1.4 }}>{c.support}</div>
      </div>
    </div>
  );
}

// ─── Generic Panel ──────────────────────────────────────────────────────────
export function Panel({ children, glow, accentEdge, hoverable, onClick, pad = 22, AUR, style }) {
  const [hov, setHov] = React.useState(false);
  return (
    <div
      onClick={onClick}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      style={{
        background: glow ? `linear-gradient(135deg, ${AUR.accentSoft}, transparent 60%)` : AUR.surface,
        border: `1px solid ${(hoverable && hov) || accentEdge ? AUR.accent + "55" : AUR.border}`,
        borderRadius: 14, padding: pad, cursor: onClick ? "pointer" : "default",
        transition: "all 180ms ease", transform: hoverable && hov ? "translateY(-2px)" : "none",
        ...style,
      }}
    >{children}</div>
  );
}
