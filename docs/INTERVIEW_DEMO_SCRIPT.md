# Interview Demo Script: Scale Regional Ops Command Center

## Prototype

**Module A: Regional Operations Health Dashboard**

This prototype is designed for a Scale AI Operations / Regional Lead style role. It shows how I would create a single operating view for distributed AI data operations across SLA, backlog, CSAT, quality, rework, and escalation risk.

## Opening Talk Track

“In my first 60 days, I would want a single regional operating view that surfaces SLA, backlog, CSAT, quality, and escalation risk before customer impact lands. I built this prototype to show the operating system I would bring to the role.”

## Business Problem

A regional operations leader manages distributed AI data operations across work types such as:

- Image annotation
- RLHF evaluation
- Code review
- Audio evaluation
- Expert review

Operational health is often spread across ticketing reports, spreadsheets, dashboards, and manager updates. By the time SLA, backlog, CSAT, quality, or escalation issues are visible, customer impact may already have occurred.

This dashboard centralizes those signals into one weekly operating view.

## Demo Flow

### 1. Executive KPI Tiles

Start with the KPI tiles.

Say:

“This is the leadership-level view. I can immediately see SLA adherence, CSAT, backlog, aged backlog, escalation rate, quality, rework, and a first-contact-resolution proxy. These are the operating metrics I would want in my weekly regional review.”

Point out:

- SLA adherence
- CSAT trailing 7-day average
- Backlog count
- Aged backlog over 72 hours
- Escalation rate per 1,000 work items
- Average quality score
- Rework rate
- FCR proxy

### 2. Regional Health Heatmap

Move to the health heatmap.

Say:

“The heatmap translates raw metrics into green, amber, and red operating health. It lets me quickly identify which work types need attention, rather than forcing leaders to inspect multiple reports.”

Explain that rows are work types and columns are operating dimensions:

- SLA
- Backlog over 72 hours
- CSAT
- Quality
- Escalation rate
- Rework

### 3. Anomaly Detection Panel

Move to the anomaly detection panel.

Say:

“This section is deliberately deterministic. Before adding any LLM, I want simple, explainable rules that a regional ops team can trust.”

Rules included:

- SLA drop greater than 5 percentage points week over week
- CSAT below 4.2
- Aged backlog above threshold
- Escalation rate above rolling baseline plus two standard deviations
- Quality decline for three consecutive periods
- Rework spike greater than 20 percent versus prior period

Say:

“This is the early-warning layer. It helps identify where leadership attention is required before customer impact compounds.”

### 4. Weekly Ops Briefing Generator

Click **Generate Weekly Ops Briefing**.

Say:

“This generates the weekly leadership update I would send. It converts metrics and anomalies into a structured operating narrative: TL;DR, top anomalies, causal hypotheses, recommended actions, risks, and questions for frontline managers.”

Emphasize:

“This is deterministic for now. Later, an LLM could improve the language, but the core logic and source metrics remain explainable.”

### 5. Work Type Drilldown

Select a work type, such as `rlhf_evaluation`, `code_review`, or `audio_evaluation`.

Say:

“Once a work type is flagged, I can drill into trends: SLA movement, backlog age bands, quality movement, escalation trend, and team-level comparisons.”

Use this to show how you would diagnose a problem.

Example:

“For RLHF evaluation, I would check whether SLA pressure is linked to policy ambiguity, reviewer shortage, or queue handoff delay.”

### 6. Team Drilldown

Select a team.

Say:

“At the team level, I can see team KPIs, contributor count, top delay reasons, and recent escalations. This is what I would use with frontline managers to move from diagnosis to action.”

Explain that this supports a weekly operating rhythm:

- Identify issue
- Assign owner
- Define containment action
- Review next week for movement

## What This Shows About My Operating Style

This prototype demonstrates that I think in terms of:

- Leading indicators, not just lagging metrics
- Operating cadence and accountability
- Regional health across multiple work types
- Structured escalation management
- Frontline manager enablement
- Explainable decision support before introducing AI summarization
- Building scalable operating systems, not one-off dashboards

## 30/60/90-Day Relevance

### First 30 Days

I would map existing workflows, data sources, escalation paths, SLA definitions, and quality review mechanisms.

### First 60 Days

I would build a single regional operating view similar to this prototype, starting with deterministic metrics and simple anomaly rules.

### First 90 Days

I would use the dashboard to run weekly operating reviews, identify recurring escalation patterns, and build manager-level action loops.

## Future Modules

This prototype intentionally focuses only on Module A.

Future modules:

### Module B: Escalation Pattern Recurrence Detector

Would detect repeat escalation patterns by customer segment, work type, root cause, team, and severity.

### Module C: Distributed Workforce Quality Scorer

Would score contributor and team quality risk using gold-task pass rate, reviewer overrides, peer agreement, rework, task complexity, and tenure.

## Closing Talk Track

“This prototype is not meant to be a production system. It is a working MVP of how I would think about the regional operating system: one view of health, early anomaly detection, manager action loops, and a weekly briefing that keeps leadership ahead of customer impact.”
