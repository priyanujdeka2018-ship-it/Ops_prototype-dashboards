# Interview Demo Script: Scale Regional Ops Command Center

## Prototype

**Module A: Regional Operations Health Dashboard**  
**Module B: Escalation Pattern Recurrence Detector**

This prototype is designed for a Scale AI Operations / Regional Lead style role. It shows how I would create a single operating view for distributed AI data operations across SLA, backlog, CSAT, quality, rework, escalation risk, and recurring escalation patterns.

## Opening Talk Track

“In my first 60 days, I would want a single regional operating view that surfaces SLA, backlog, CSAT, quality, and escalation risk before customer impact lands. I built this prototype to show the operating system I would bring to the role.”

Then add:

“Module A tells me where regional health is degrading. Module B tells me whether escalations are isolated incidents or recurring operating-system failures. This helps leadership move from reactive escalation handling to pattern-based prevention.”

## Business Problem

A regional operations leader manages distributed AI data operations across work types such as:

- Image annotation
- RLHF evaluation
- Code review
- Audio evaluation
- Expert review

Operational health is often spread across ticketing reports, spreadsheets, dashboards, and manager updates. By the time SLA, backlog, CSAT, quality, or escalation issues are visible, customer impact may already have occurred.

Module A centralizes those signals into one weekly operating view. Module B goes one level deeper: it checks whether escalations are one-off incidents or repeat patterns that require structural fixes.

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

### 5. Module B: Escalation Pattern Recurrence Detector

Move to the Module B section.

Say:

“After Module A shows me where health is degrading, Module B helps me decide whether the escalations are isolated fires or repeat failure modes. This is the difference between closing tickets and fixing the operating system.”

Point out the pattern key selector:

- Work type + root cause
- Work type + team + root cause
- Customer segment + work type + root cause
- Team + severity + root cause

Say:

“I can tune the pattern definition depending on the leadership question. If I want a systemic view, I use work type plus root cause. If I want a frontline manager conversation, I narrow it to team plus root cause.”

### 6. Recurring Escalation Pattern Summary

Point out the summary cards.

Say:

“This gives me the number of escalation events in scope, recurring patterns, high-risk patterns, top affected work type, and top root cause. This is designed for a weekly ops retro.”

Emphasize that Module B reuses the same `escalation_events.csv` as Module A, so it is not a disconnected demo.

### 7. Pattern Risk Table

Move to the Pattern Risk Table.

Say:

“The table scores patterns using deterministic recurrence logic. It looks at escalation count, severity, open escalations, customer-segment blast radius, acceleration, and slow resolution. I’m not just sorting by the loudest escalation.”

Point out fields:

- Pattern key
- Escalation count
- Severity mix
- Unique teams impacted
- Unique customer segments impacted
- Open count
- Average days to resolve
- Recurrence status
- Risk score
- Risk level
- Recommended action

Say:

“This lets me separate one-off customer issues from repeat operational breakdowns.”

### 8. Pattern Drilldown

Select a high-risk pattern.

Say:

“Here I can drill into the selected pattern: affected teams, customer segments, severity mix, open count, average days to resolve, recent escalation summaries, and the trend over time.”

Use this example talk track:

“If RLHF evaluation has SLA pressure and rising escalations, Module B can show whether the repeat driver is policy ambiguity, reviewer misalignment, customer requirement changes, tooling issues, or capacity shortfall.”

### 9. Recommended Leadership Actions

Move to the recommended actions panel.

Say:

“This is the action loop. A recurring pattern should not end with ‘ticket closed.’ It should create a structural fix: SOP clarification, calibration, routing change, staffing review, tooling fix, or customer instruction propagation.”

### 10. Escalation Pattern Briefing Generator

Click **Generate Escalation Pattern Briefing**.

Say:

“This creates the escalation-pattern section I would bring to the weekly ops retro. It gives an executive TL;DR, top recurring patterns, likely systemic causes, recommended leadership actions, risks if not addressed, and questions for frontline managers.”

Emphasize:

“No LLM is required. The summary is deterministic and explainable first. Later, an LLM could polish the narrative, but the operating logic is already useful.”

### 11. Work Type Drilldown

Select a work type, such as `rlhf_evaluation`, `code_review`, or `audio_evaluation`.

Say:

“Once a work type is flagged, I can drill into trends: SLA movement, backlog age bands, quality movement, escalation trend, and team-level comparisons.”

Use this to show how Module A and Module B connect:

“Module A identifies the unhealthy work type. Module B checks whether its escalations are recurring and what structural action is needed.”

### 12. Team Drilldown

Select a team.

Say:

“At the team level, I can see team KPIs, contributor count, top delay reasons, and recent escalations. This is what I would use with frontline managers to move from diagnosis to action.”

Explain that this supports a weekly operating rhythm:

- Identify issue
- Check whether it is recurring
- Assign owner
- Define containment and prevention action
- Review next week for movement

## What This Shows About My Operating Style

This prototype demonstrates that I think in terms of:

- Leading indicators, not just lagging metrics
- Operating cadence and accountability
- Regional health across multiple work types
- Structured escalation management
- Repeat-pattern detection
- Frontline manager enablement
- Explainable decision support before introducing AI summarization
- Building scalable operating systems, not one-off dashboards

## 30/60/90-Day Relevance

### First 30 Days

I would map existing workflows, data sources, escalation paths, SLA definitions, quality review mechanisms, and escalation root-cause categories.

### First 60 Days

I would build a single regional operating view similar to Module A, starting with deterministic metrics and simple anomaly rules.

### First 90 Days

I would use the dashboard and recurrence detector to run weekly operating reviews, identify recurring escalation patterns, and build manager-level action loops.

## Future Modules

### Module C: Distributed Workforce Quality Scorer

Would score contributor and team quality risk using gold-task pass rate, reviewer overrides, peer agreement, rework, task complexity, and tenure.

## Closing Talk Track

“This prototype is not meant to be a production system. It is a working MVP of how I would think about the regional operating system: one view of health, early anomaly detection, recurring escalation detection, manager action loops, and weekly briefings that keep leadership ahead of customer impact.”
