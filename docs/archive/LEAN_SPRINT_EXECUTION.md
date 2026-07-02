# Scale Ops Command Center — Lean Sprint: Retire Streamlit · Analyst Workbench · Docs

> Place at `docs/LEAN_SPRINT_EXECUTION.md`. Branch off `main` @ `d9edc30`. One PR.
> Execute against **live HEAD** — every precondition below was verified 2026-07-02 but must be
> re-verified before acting on it.
> **Scope:** §1 retire Streamlit, §2 Analyst Workbench, §3 docs collapse.
> **Out of scope (deliberately deferred):** vintage collapse (`data-pre-fix`/`data-post-fix` and
> the vintage selector stay — they are the before/after demo asset) and the `/api/rebuild` live
> fork. No rearchitecture.
> **Guardrails:** full pytest suite green (report the *collected* case count — do not assume
> "90"); `cd web && bun install && bun run build` succeeds; `render.yaml` untouched; the SPA
> fallback rewrite untouched.

---

## 0. Preconditions (verify, don't assume)

1. `main` HEAD is `d9edc30` or a descendant.
2. `render.yaml` already contains **one** static service (`scale-regional-ops-command-center`,
   `runtime: static`). The old refactor brief's instruction to "delete the Streamlit service
   block" is obsolete — there is none. Verify, change nothing.
3. Run `pytest -q`; record the collected count **N** as the baseline for §4.

---

## 1. Retire Streamlit

1. Delete `app.py`, `pages/`, `.streamlit/`.
2. Delete the four Streamlit-only `src/` modules — verified at review time as imported **only**
   by `app.py`/`pages/` and covered by **zero** tests:
   - `src/data_loader.py`
   - `src/ui_components.py`
   - `src/briefing.py`
   - `src/fix_cards.py`

   **Re-verify before each deletion** (imports may have changed since review):
   ```
   grep -rn "data_loader\|ui_components\|briefing\|fix_cards" src/ tests/ web/ scripts/ conftest.py
   ```
   must return only self-references and docstring mentions. If anything else imports one of
   these, stop and report instead of deleting.
   *Rationale: after the UI that reaches them is gone, they are unreachable, untested code —
   dead weight. They remain in git history if ever wanted.*
3. `requirements.txt`: remove `streamlit==1.58.0`. Then prune any dependency used **only** by
   the deleted modules (check imports before removing); keep everything the pipeline and tests
   import.
4. Scrub stale Streamlit mentions in *surviving* files — docstring-only edits, no logic:
   `src/build_frontend_data.py:4`, `src/escalation_patterns.py:250`, and any others
   `grep -rni streamlit src/ tests/` surfaces.
5. Gate: `pytest -q` still collects and passes **N** (Streamlit had no coverage, so the count
   must not change — if it drops, stop and report).

---

## 2. Analyst Workbench — the one additive (the audit surface)

1. **Dependency:** `cd web && bun add @tanstack/react-table`. Commit the `bun.lock` change
   (the lock resolves against public npm — see the `render.yaml` buildCommand comment). Verify
   `bun run build` still succeeds before writing any UI.
   *Why react-table: sort/filter/pagination for free, fits the existing TanStack stack.
   Alternative — hand-rolled tables — rejected for the cost of rebuilding those behaviors.*
2. **Route:** new file `web/src/routes/_dash.workbench.tsx` (TanStack file-based routing
   auto-registers it). **Sidebar:** add one entry to the nav array in
   `web/src/dashboards/shell.tsx` (~line 20), matching the existing item shape
   (`to / badge / label / desc`).
3. **Data:** read the **same** `useScaleData(scenario, vintage)` hook the dashboards use —
   `web/src/dashboards/data-utils.jsx:97`. Do **not** fetch independently. Identical numbers by
   construction is the whole point.
4. **Tables** over the payload's raw collections — verified keys in the current payload:
   `teams`, `escalations`, `patterns`, `clusters`, `workforce.contributors`, `workTypeRollup`.
   One tab / segmented control per collection. Handle empty collections gracefully
   (`clusters` is 0 rows in the `current` scenario — render an empty state, don't crash).
5. **Filters** (cross-cutting, only where the column exists): `work_type`, `team`, `severity`,
   `status`. Don't gold-plate — no saved views, no column chooser.
6. **Export:** client-side CSV **and** JSON of the currently *filtered* rows
   (`Blob` + anchor download; no extra library).
7. **Framing comment** at the top of the route file: the five dashboards are the *decision
   surface*; the workbench is the *audit surface*; one payload, one source.
8. **Style:** match the existing shell — reuse primitives from `web/src/components/ui/` and
   `web/src/dashboards/atoms.jsx`. Do **not** create `web/src/components/nav/`; Breadcrumb and
   ThreadNav already exist elsewhere, and a flat audit table needs no trail.

---

## 3. Docs collapse + README

1. Write **`docs/ARCHITECTURE.md`** — the one canonical doc: the CSV → Python pipeline → JSON
   payload → React → static-deploy arc; the single-source-of-truth decision; the
   `{section, focus}` IA model; the decision-vs-audit split; a short "deliberately deferred"
   section (vintage collapse, `/api/rebuild`) with one line of rationale each.
2. Create **`docs/archive/`** and move the historical execution/module docs into it:
   `CONSOLIDATION_EXECUTION.md`, `MODULE_B_HANDOFF.md`, `MODULE_B_V2_DEMO_SCRIPT.md`,
   `MODULE_C_DEMO_SCRIPT.md`, `MODULE_C_HANDOFF.md`, `MODULE_D_DEMO_SCRIPT.md`,
   `MODULE_D_HANDOFF.md`, `PHASE_1_DATA_MODEL.md`, `FINAL_CHECKLIST.md`,
   `INTERVIEW_DEMO_SCRIPT.md`, `interview-prep-ops-dashboard.md`,
   `interview-prep-pipeline-addendum.md`, and this brief once executed.
   `PRODUCTION_ARCHITECTURE.md`: fold its content into `ARCHITECTURE.md`'s scaling section and
   archive it, **or** keep it top-level if folding loses substance — your call, state it in the
   PR description.
3. Rewrite **`README.md`** so a reviewer navigates the repo in ~2 minutes: what each top-level
   dir is, how to run the pipeline (`scripts/rebuild.sh`), how to run and deploy the web app,
   where the tests live, link to `ARCHITECTURE.md`. Remove all Streamlit run instructions.

---

## 4. Definition of done

- `pytest -q` green; **exact collected count reported in the PR description**.
- `cd web && bun install && bun run build` succeeds; `git diff render.yaml` is empty.
- `grep -ri streamlit` → zero hits outside `docs/archive/`.
- Workbench renders all six collections, filters work, CSV/JSON export downloads the filtered
  rows, and one spot-checked figure (e.g., a team's quality score) matches the Workforce
  dashboard.
- `README.md` + `docs/ARCHITECTURE.md` present; `docs/archive/` populated.
- No committed `data/*.csv` introduced; no new JS scoring.
- PR description lists: test count, dependency added (`@tanstack/react-table` + version),
  files deleted, and any judgment calls made.

---

## 5. Owner's post-deploy smoke test (browser — not Claude Code's job)

- Refresh while drilled into a team → view survives (SPA rewrite rule holds).
- Leadership alert → click-through shows the **same number** in the deep view.
- Scenario flip updates every module **and** the freshness stamp.
- Workbench numbers match a dashboard; exported CSV/JSON open clean.
