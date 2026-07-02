// Analyst Workbench — the audit surface.
//
// The five dashboards (Health / Patterns / Clusters / Workforce / Capacity) are
// the *decision surface*: curated views that tell leadership what to do next.
// This workbench is the *audit surface*: the same payload, exposed as raw,
// sortable, filterable tables so an analyst can verify any number a dashboard
// shows. One payload (useScaleData via DashProvider), one source of truth —
// identical numbers by construction, not by reconciliation.
import React, { useMemo, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getPaginationRowModel,
  flexRender,
  createColumnHelper,
  type SortingState,
} from "@tanstack/react-table";
import { useDash } from "@/dashboards/app-context";
// @ts-expect-error jsx
import { Breadcrumb, PillRow, Panel, aurMono, aurSerif, aurSans, AurChip } from "@/dashboards/atoms.jsx";
// @ts-expect-error jsx
import { WORK_TYPE_LABELS } from "@/dashboards/data-utils.jsx";
import { Loading } from "./_dash.index";

export const Route = createFileRoute("/_dash/workbench")({
  head: () => ({ meta: [
    { title: "Analyst Workbench · Scale Ops" },
    { name: "description", content: "Raw, filterable tables over the same payload the dashboards read — sort, filter, and export any collection for audit." },
  ]}),
  component: Workbench,
});

// Each collection maps the cross-cutting filters (work_type / team / severity /
// status) onto its own column names; a filter is only shown where the column
// exists in that collection.
type CollectionDef = {
  id: string;
  label: string;
  desc: string;
  rows: (data: any) => any[];
  filterCols: Partial<Record<"work_type" | "team" | "severity" | "status", string>>;
};

const COLLECTIONS: CollectionDef[] = [
  { id: "teams", label: "Teams", desc: "One row per team", rows: (d) => d.teams ?? [],
    filterCols: { work_type: "work_type", team: "team_id" } },
  { id: "escalations", label: "Escalations", desc: "Raw escalation log", rows: (d) => d.escalations ?? [],
    filterCols: { work_type: "work_type", team: "team_id", severity: "severity", status: "status" } },
  { id: "patterns", label: "Patterns", desc: "Recurrence patterns", rows: (d) => d.patterns ?? [],
    filterCols: { work_type: "work_type", status: "recurrence_status" } },
  { id: "clusters", label: "Clusters", desc: "Semantic clusters", rows: (d) => d.clusters ?? [],
    filterCols: {} },
  { id: "contributors", label: "Contributors", desc: "Workforce quality", rows: (d) => d.workforce?.contributors ?? [],
    filterCols: { work_type: "work_type", team: "team_id", status: "status" } },
  { id: "workTypeRollup", label: "Work types", desc: "Per-work-type rollup", rows: (d) => d.workTypeRollup ?? [],
    filterCols: { work_type: "work_type" } },
];

const FILTERS = [
  { key: "work_type", label: "All work types" },
  { key: "team",      label: "All teams" },
  { key: "severity",  label: "All severities" },
  { key: "status",    label: "All statuses" },
] as const;

// Flatten a cell for display and CSV: arrays join, objects stringify.
function cellText(v: any): string {
  if (v == null) return "";
  if (Array.isArray(v)) return v.map(cellText).join("; ");
  if (typeof v === "object") return JSON.stringify(v);
  return String(v);
}

function toCsv(rows: any[], keys: string[]): string {
  const esc = (s: string) => (/[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s);
  const lines = [keys.map(esc).join(",")];
  for (const r of rows) lines.push(keys.map((k) => esc(cellText(r[k]))).join(","));
  return lines.join("\n");
}

function download(filename: string, mime: string, content: string) {
  const url = URL.createObjectURL(new Blob([content], { type: mime }));
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

const PAGE_SIZE = 25;

function Workbench() {
  const { data, AUR, densityPreset, scenario } = useDash();
  const [collectionId, setCollectionId] = useState("teams");
  const [filters, setFilters] = useState<Record<string, string | undefined>>({});
  const [sorting, setSorting] = useState<SortingState>([]);

  const collection = COLLECTIONS.find((c) => c.id === collectionId)!;
  const allRows = useMemo(() => (data ? collection.rows(data) : []), [data, collection]);

  // Filter before the table so export sees exactly what the table shows.
  const filteredRows = useMemo(() => {
    return allRows.filter((r) =>
      FILTERS.every(({ key }) => {
        const col = collection.filterCols[key];
        const want = filters[key];
        return !col || !want || cellText(r[col]) === want;
      }),
    );
  }, [allRows, filters, collection]);

  const keys = useMemo(() => (allRows.length ? Object.keys(allRows[0]) : []), [allRows]);

  const columns = useMemo(() => {
    const helper = createColumnHelper<any>();
    return keys.map((k) =>
      helper.accessor((row) => row[k], {
        id: k,
        header: k,
        cell: (info) => cellText(info.getValue()),
        sortingFn: "basic",
      }),
    );
  }, [keys]);

  const table = useReactTable({
    data: filteredRows,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: { pagination: { pageSize: PAGE_SIZE } },
  });

  if (!data) return <Loading AUR={AUR} />;

  const filterOptions = (key: (typeof FILTERS)[number]["key"]) => {
    const col = collection.filterCols[key];
    if (!col) return null;
    const vals = Array.from(new Set(allRows.map((r) => cellText(r[col])).filter(Boolean))).sort();
    return vals.length > 1 ? vals : null;
  };

  const exportRows = () => filteredRows;
  const stamp = `${collection.id}-${scenario}`;

  const pageIndex = table.getState().pagination.pageIndex;
  const pageCount = table.getPageCount();

  return (
    <>
      <Breadcrumb AUR={AUR} items={[{ label: "Workbench · Audit tables" }]} />
      <div>
        <div style={{ fontFamily: aurMono, fontSize: 10.5, color: AUR.accent, letterSpacing: 0.8, textTransform: "uppercase", marginBottom: 10 }}>Analyst Workbench · Audit surface</div>
        <h1 style={{ fontFamily: aurSerif, fontSize: 36, fontWeight: 400, letterSpacing: -1, margin: 0, lineHeight: 1.1, color: AUR.text }}>Every number, in the raw.</h1>
        <p style={{ color: AUR.textDim, fontSize: 14, marginTop: 12, maxWidth: 720, lineHeight: 1.6 }}>
          The dashboards decide; this page audits. Same payload, same scenario — the tables below are the untouched collections behind every chart, sortable and exportable.
        </p>
      </div>

      {/* collection tabs */}
      <div style={{ marginTop: densityPreset.sectionGap, display: "flex", flexDirection: "column", gap: 12 }}>
        <PillRow
          AUR={AUR}
          options={COLLECTIONS.map((c) => c.id)}
          value={collectionId}
          onChange={(id: string) => { setCollectionId(id); setFilters({}); setSorting([]); }}
          getLabel={(id: string) => COLLECTIONS.find((c) => c.id === id)!.label}
          getCount={(id: string) => (data ? COLLECTIONS.find((c) => c.id === id)!.rows(data).length : 0)}
        />

        {/* cross-cutting filters — rendered only where the collection has the column */}
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center" }}>
          {FILTERS.map(({ key, label }) => {
            const opts = filterOptions(key);
            if (!opts) return null;
            return (
              <select
                key={key}
                value={filters[key] ?? ""}
                onChange={(e) => setFilters((f) => ({ ...f, [key]: e.target.value || undefined }))}
                style={{
                  background: AUR.surface, color: filters[key] ? AUR.accent : AUR.textDim,
                  border: `1px solid ${filters[key] ? AUR.accent + "55" : AUR.border}`,
                  borderRadius: 999, padding: "6px 12px", fontFamily: aurSans, fontSize: 12, cursor: "pointer",
                }}
              >
                <option value="">{label}</option>
                {opts.map((v) => (
                  <option key={v} value={v}>{key === "work_type" ? (WORK_TYPE_LABELS[v] || v) : v}</option>
                ))}
              </select>
            );
          })}
          <span style={{ fontFamily: aurMono, fontSize: 11, color: AUR.textFaint }}>
            {filteredRows.length.toLocaleString("en-US")} of {allRows.length.toLocaleString("en-US")} rows
          </span>
          <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
            <ExportBtn AUR={AUR} disabled={!filteredRows.length} onClick={() => download(`${stamp}.csv`, "text/csv", toCsv(exportRows(), keys))}>⤓ CSV</ExportBtn>
            <ExportBtn AUR={AUR} disabled={!filteredRows.length} onClick={() => download(`${stamp}.json`, "application/json", JSON.stringify(exportRows(), null, 2))}>⤓ JSON</ExportBtn>
          </div>
        </div>
      </div>

      {allRows.length === 0 ? (
        <Panel AUR={AUR} style={{ marginTop: densityPreset.gap, textAlign: "center", padding: "48px 24px" }}>
          <div style={{ fontFamily: aurSerif, fontSize: 20, color: AUR.text, marginBottom: 6 }}>No rows in this collection</div>
          <div style={{ fontSize: 13, color: AUR.textDim }}>
            The current payload has no <span style={{ fontFamily: aurMono }}>{collection.label.toLowerCase()}</span> rows for the <span style={{ fontFamily: aurMono }}>{scenario}</span> scenario.
          </div>
        </Panel>
      ) : (
        <Panel AUR={AUR} pad={0} style={{ marginTop: densityPreset.gap, overflow: "hidden" }}>
          <div style={{ overflowX: "auto" }}>
            <table style={{ borderCollapse: "collapse", width: "100%", fontSize: 12.5 }}>
              <thead>
                {table.getHeaderGroups().map((hg) => (
                  <tr key={hg.id}>
                    {hg.headers.map((h) => {
                      const dir = h.column.getIsSorted();
                      return (
                        <th
                          key={h.id}
                          onClick={h.column.getToggleSortingHandler()}
                          style={{
                            position: "sticky", top: 0, textAlign: "left", cursor: "pointer", whiteSpace: "nowrap",
                            padding: "10px 14px", background: AUR.surfaceHi, color: dir ? AUR.accent : AUR.textFaint,
                            fontFamily: aurMono, fontSize: 10, letterSpacing: 0.5, textTransform: "uppercase",
                            borderBottom: `1px solid ${AUR.border}`, userSelect: "none",
                          }}
                        >
                          {flexRender(h.column.columnDef.header, h.getContext())}
                          {dir === "asc" ? " ↑" : dir === "desc" ? " ↓" : ""}
                        </th>
                      );
                    })}
                  </tr>
                ))}
              </thead>
              <tbody>
                {table.getRowModel().rows.map((row) => (
                  <tr key={row.id}>
                    {row.getVisibleCells().map((cell) => (
                      <td key={cell.id} style={{
                        padding: "8px 14px", borderBottom: `1px solid ${AUR.border}`, color: AUR.textDim,
                        fontFamily: aurMono, fontSize: 11.5, whiteSpace: "nowrap", maxWidth: 380,
                        overflow: "hidden", textOverflow: "ellipsis", fontVariantNumeric: "tabular-nums",
                      }}>
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {pageCount > 1 && (
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "10px 14px", borderTop: `1px solid ${AUR.border}` }}>
              <span style={{ fontFamily: aurMono, fontSize: 11, color: AUR.textFaint }}>
                Page {pageIndex + 1} of {pageCount}
              </span>
              <div style={{ display: "flex", gap: 8 }}>
                <ExportBtn AUR={AUR} disabled={!table.getCanPreviousPage()} onClick={() => table.previousPage()}>← Prev</ExportBtn>
                <ExportBtn AUR={AUR} disabled={!table.getCanNextPage()} onClick={() => table.nextPage()}>Next →</ExportBtn>
              </div>
            </div>
          )}
        </Panel>
      )}

      <div style={{ marginTop: densityPreset.gap, display: "flex", gap: 8, flexWrap: "wrap" }}>
        <AurChip AUR={AUR}>{collection.desc}</AurChip>
        <AurChip AUR={AUR}>Scenario · {scenario}</AurChip>
        <AurChip AUR={AUR}>Export = filtered rows</AurChip>
      </div>
    </>
  );
}

function ExportBtn({ children, onClick, disabled, AUR }: any) {
  return (
    <button onClick={onClick} disabled={disabled} style={{
      background: "transparent", border: `1px solid ${AUR.border}`, color: disabled ? AUR.textFaint : AUR.textDim,
      borderRadius: 999, padding: "6px 13px", fontFamily: aurSans, fontSize: 12,
      cursor: disabled ? "default" : "pointer", opacity: disabled ? 0.5 : 1, whiteSpace: "nowrap",
    }}>{children}</button>
  );
}
