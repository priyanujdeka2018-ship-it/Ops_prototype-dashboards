# Interview Prep — Scale Regional Ops Command Center

Current repo state (verified): Python analytics core (14 modules, 83 passing tests, pinned deps) → two presentation layers sharing one number-generating engine: the **Aurora React executive view** (static, precomputed `data.json` via `src/build_frontend_data.py`) and the **Streamlit working view** (full Module A–D drilldowns). Both deploy from one repo on Render free tier.

Your one-line system story — memorize this:

> “A tested Python decision engine with two faces: an executive command view and an analyst working view. Same engine, same numbers, deterministic and explainable end to end.”

-----

## 1. “Why this architecture?”

**Answer:** “I separated the operating logic from the presentation. All scoring — health thresholds, escalation recurrence, workforce risk, capacity gaps — lives in one tested Python core. The executive React view and the analyst Streamlit view both consume that same engine, so leadership and analysts never see different numbers. And it’s deterministic-first: every red cell traces to a rule I can defend in a business review, not a black box.”

**If pushed on “why not just one frontend”:** “The exec view is for the weekly leadership review — fast, focused, narrative. The Streamlit view is the analyst workbench with full drilldowns. In production I’d converge them, but for a prototype this demonstrates the two audiences an ops system actually serves.”

**If asked “why deterministic, why no ML/LLM at the core”:** “Because an ops leader has to defend every escalation decision. Rules first, versioned in git so threshold changes are auditable. The LLM layer belongs on top — polishing the briefing narrative — never deciding what’s red.”

## 2. “Why build this instead of using Tableau / Looker / existing BI?”

“BI tools visualize metrics. The value here is the *encoded operating judgment*: recurrence scoring that separates one-off escalations from systemic failures, a workforce risk score that composes quality gap, fail rate, override rate, peer agreement and rework into one coaching signal, and action cards with owners and follow-up dates. BI shows you the problem; this tells you the decision. Also: zero licence cost and live in days, not a procurement cycle.”

## 3. “How does it scale?” — answer all three layers

**Data scale:** “Today it runs on CSV exports with precomputed JSON — right-sized for a prototype. Because compute and presentation are decoupled, scaling is a data-source swap: point the same Python functions at Postgres or the warehouse, schedule the build job hourly, and neither frontend changes. The logic is already covered by 83 automated tests, so the migration is low-risk.”

**Org scale:** “The build is parameterized by region — multi-region is one `data.json` per region plus the region picker that already exists. Multi-team is the same pattern.”

**Process scale:** “Thresholds and weights are code, reviewed via pull request. When ops policy changes — say SLA target moves — that’s a one-line auditable change, not someone editing a dashboard nobody can verify.”

## 4. “How would you improve it?” — give a prioritized roadmap

1. **Real data integration** — connect ticketing/QA exports; schema already mirrors real ops data shapes. Biggest credibility jump.
1. **Action–outcome loop** — the strongest answer in the room: “Today it recommends actions. Next I’d track whether the action was taken and whether the metric recovered — turning the dashboard into a learning system that measures its own advice.”
1. **Operating cadence hooks** — scheduled weekly briefing email/Slack digest, so it drives the review rather than waiting to be opened.
1. **LLM narrative layer** — polish deterministic briefings into prose; facts stay rule-generated.
1. **Statistical hardening** — the workforce scorer already refuses to score insufficient samples; extend that with confidence intervals and seasonality in the capacity forecast.
1. **Auth and role views** — manager sees their team, regional lead sees everything.

## 5. Gotcha questions — prepare for these

**“The data is synthetic.”**
“Deliberately. Synthetic data let me design for the failure modes I care about — recurring escalation patterns, cohort quality drift, capacity crunches — and demo them on demand. The schemas mirror real ops exports, so swapping in real feeds is the integration step, not a rebuild.”

**“Did you write this code yourself?”** — answer honestly, it’s a strength:
“I built it AI-assisted — I owned the operating logic, metric definitions, thresholds, and architecture decisions; AI tooling wrote the implementation under my direction, with an 83-test suite verifying the scoring logic. That’s exactly how I’d run ops tooling in this role: domain judgment from me, leverage from AI, verification through tests.”

**“What’s the weakest part?”** — never say “nothing”:
“Three honest gaps: no live data feed, no authentication, and the capacity forecast is heuristic rather than statistical. All three are deliberate prototype scoping — and each has a defined path I just described.”

**“Walk me through one metric end to end.”** — rehearse this one:
“Escalation rate per 1,000 work items: count escalations, divide by work items, times 1,000. It feeds the health heatmap through fixed green/amber/red thresholds. The same escalation events then flow into Module B, which groups them into pattern keys — work type + root cause + team — and scores recurrence using frequency, spread, severity weighting and resolution lag; a score ≥ 20 is high risk and generates a leadership action with an owner.”

**“Isn’t the workforce scorer a surveillance tool?”**
“I positioned it the opposite way on purpose. It refuses to score small samples, it scores *risk conditions* — calibration drift, high-complexity mix, low-tenure cohorts — not people rankings, and its outputs are coaching and calibration actions, not penalties.”

## 6. Demo hygiene checklist (day before)

- [ ] Open both Render URLs; free tier sleeps — warm them up 15 min before the call
- [ ] Rehearse the 60-second opening talk track (docs/INTERVIEW_DEMO_SCRIPT.md)
- [ ] Pick your one end-to-end metric story (escalation rate, above) and say it aloud twice
- [ ] Have the GitHub repo open in a tab — commit history is itself evidence of disciplined iteration
- [ ] Decide your demo path: Aurora exec view for the story → Streamlit drilldown only if they ask to go deeper