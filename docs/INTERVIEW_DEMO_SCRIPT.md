# Interview Demo Script: Scale Regional Ops Command Center

## Prototype

**Module A: Regional Operations Health Dashboard**  
**Module B v1: Escalation Pattern Recurrence Detector**  
**Module B v2: Semantic Escalation Clustering and Structural Fix Cards**  
**Module C: Distributed Workforce Quality Scorer**

This prototype is designed for a Scale AI Operations / Regional Lead style role. It shows how I would create a single operating view for distributed AI data operations across SLA, backlog, CSAT, quality, rework, escalation risk, recurring escalation patterns, and workforce quality risk.

## Opening Talk Track

“In my first 60 days, I would want a single regional operating view that surfaces SLA, backlog, CSAT, quality, and escalation risk before customer impact lands. I built this prototype to show the operating system I would bring to the role.”

Then add:

“Module A tells me where regional health is degrading. Module B tells me whether escalations are isolated incidents or recurring operating-system failures. Module C tells me whether distributed workforce quality risk is emerging and what coaching, calibration, training, or staffing action should happen next.”

## Business Problem

A regional operations leader manages distributed AI data operations across work types such as:

- Image annotation
- RLHF evaluation
- Code review
- Audio evaluation
- Expert review

Operational health is often spread across ticketing reports, spreadsheets, dashboards, and manager updates. By the time SLA, backlog, CSAT, quality, or escalation issues are visible, customer impact may already have occurred.

Module A centralizes those signals into one weekly operating view. Module B checks whether escalations are one-off incidents or repeat patterns requiring structural fixes. Module C checks whether quality risk is emerging across contributors, teams, cohorts, work types, and operating conditions.

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

### 5. Module B v1: Escalation Pattern Recurrence Detector

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

### 11. Module B v2: Semantic Clustering and Fix Cards

Open the Streamlit sidebar page:

```text
2 Module B v2 Semantic Clusters
```

Say:

“Module B v1 uses deterministic pattern keys for explainability. Module B v2 adds semantic clustering with TF-IDF and cosine similarity so I can detect recurring escalation themes even when the wording differs.”

Demo these sections:

1. Filters and clustering settings
2. Semantic Cluster Summary
3. Cluster Charts
4. Cluster Drilldown
5. Structural Fix Card
6. Weekly Retro Queue

Talk track:

“This is how I move from reactive escalation handling to pattern-based prevention. I can identify a recurring cluster, inspect the source escalations, understand the blast radius, and generate a structural fix card with the owner, metric, decision needed, and follow-up date.”

### 12. Module C: Distributed Workforce Quality Scorer

Open the Streamlit sidebar page:

```text
3 Module C Workforce Quality Scorer
```

Say:

“Module C looks below the regional metric and checks whether quality risk is concentrated by team, contributor cohort, work type, tenure, skill level, task complexity, rework, reviewer override, or peer disagreement.”

Emphasize:

“I do not want to use quality data as a punitive scoreboard. I want to use it as an operating signal.”

### 13. Module C Executive Workforce Quality Summary

Point out the KPI tiles:

- Total contributors
- Active contributors
- High-risk contributors
- High-risk teams
- Average quality score
- Gold task fail rate
- Reviewer override rate
- Average peer agreement
- Top affected work type
- Top risk driver

Say:

“This is the workforce quality operating summary. It tells me where quality risk is showing up and which driver is most important this week.”

### 14. Contributor Quality Risk Table

Show the contributor table.

Say:

“This is not a punitive leaderboard. It is a coaching and calibration signal. I am looking for patterns such as low gold-task pass rate, reviewer overrides, low peer agreement, rework, recent quality drop, or low-tenure contributors handling high-complexity work.”

Call out:

- Sampled quality events
- Average quality score
- Gold task fail rate
- Reviewer override rate
- Peer agreement score
- Rework rate
- Quality delta
- Risk status
- Recommended action

### 15. Team Quality Risk Table

Show the team table.

Say:

“At the team level, I can see whether risk is isolated to one contributor or whether it is becoming a manager-level quality-system issue.”

Call out:

- Active contributors
- High-risk contributor count
- Quality drift flag
- Team risk score
- Team risk level
- Recommended manager action

### 16. Quality Drift View

Show the charts:

- Quality risk by work type
- High-risk contributors by team
- Gold task fail rate by team
- Reviewer override rate by team
- Rework rate by work type
- Quality trend for selected team

Say:

“This helps me separate the failure mode. If gold-task fail rate is high, I may need targeted coaching. If reviewer overrides are high and peer agreement is low, I may need calibration. If rework is concentrated in a work type, I may need SOP or task-instruction review.”

### 17. Contributor and Team Drilldown

Select a contributor with high or medium risk.

Say:

“The drilldown shows the evidence behind the signal: quality history, gold pass/fail history, reviewer overrides, peer agreement, rework, and task complexity mix. The goal is to decide the right support action, not to shame the contributor.”

Then select a team.

Say:

“The team drilldown gives the manager conversation: quality trend, high-risk contributor count, top drivers, recent quality events, and recommended manager action.”

### 18. Weekly Coaching and Calibration Queue

Show the queue.

Say:

“This queue is designed for the weekly operating rhythm. It combines risk score, quality delta, gold-task failure, reviewer overrides, rework, peer agreement, sample size, and team blast radius. It prioritizes where managers should review coaching, calibration, training, staffing, or SOP action.”

Emphasize:

“I would never present this as a punitive leaderboard. The label is intentional: Weekly Coaching and Calibration Queue.”

### 19. Quality Coaching Card Generator

Generate a card for a high-risk contributor or team.

Say:

“This converts the signal into a manager-ready action card: risk summary, evidence, likely driver, recommended action, owner, metric to monitor, decision needed, and follow-up date.”

Example explanation:

“If the driver is reviewer calibration drift, the action is a calibration huddle and QA sampling increase. If the driver is low tenure plus high complexity, the action is a training update and gradual ramp.”

### 20. Module C Weekly Briefing

Show the Module C weekly briefing.

Say:

“This is the quality section I would bring into a weekly operating review. It is deterministic and explainable first. Later, an LLM could polish the narrative, but the operating logic remains transparent.”

## Work Type Drilldown Connection

Select a work type, such as `rlhf_evaluation`, `code_review`, or `audio_evaluation`.

Say:

“Once a work type is flagged, I can drill into trends: SLA movement, backlog age bands, quality movement, escalation trend, team-level comparisons, and workforce quality risk.”

Use this to show how Modules A, B, and C connect:

“Module A identifies the unhealthy work type. Module B checks whether its escalations are recurring and what structural action is needed. Module C checks whether the issue is concentrated in a team, new contributor cohort, reviewer calibration drift, or high-complexity task mix.”

## Team Drilldown Connection

Select a team.

Say:

“At the team level, I can see team KPIs, contributor count, top delay reasons, recent escalations, and workforce quality risk. This is what I would use with frontline managers to move from diagnosis to action.”

Explain that this supports a weekly operating rhythm:

- Identify issue
- Check whether it is recurring
- Check whether quality risk is emerging
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
- Workforce quality coaching and calibration
- Frontline manager enablement
- Explainable decision support before introducing AI summarization
- Building scalable operating systems, not one-off dashboards

## 30/60/90-Day Relevance

### First 30 Days

I would map existing workflows, data sources, escalation paths, SLA definitions, quality review mechanisms, contributor cohorts, reviewer calibration mechanisms, and escalation root-cause categories.

### First 60 Days

I would build a single regional operating view similar to Module A, starting with deterministic metrics and simple anomaly rules, then layer in escalation recurrence and workforce quality signals.

### First 90 Days

I would use the dashboard, recurrence detector, and quality scorer to run weekly operating reviews, identify recurring escalation patterns, identify emerging workforce quality risk, and build manager-level action loops.

## Closing Talk Track

“This prototype is not meant to be a production system. It is a working MVP of how I would think about the regional operating system: one view of health, early anomaly detection, recurring escalation detection, workforce quality risk detection, manager action loops, and weekly briefings that keep leadership ahead of customer impact.”

Final line:

“Module A shows where the operation is unhealthy. Module B shows whether escalations are recurring system failures. Module C shows whether distributed workforce quality risk is emerging and what coaching, calibration, or staffing action should happen next.”
