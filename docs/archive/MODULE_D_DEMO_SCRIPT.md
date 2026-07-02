# Module D Demo Script: Capacity, Staffing, and SLA Forecasting

## Positioning Line

> Module D extends the command center from health, escalation recurrence, and workforce quality into capacity and SLA forecasting. It helps managers see whether backlog, inflow, throughput, staffing, skill mix, or complexity pressure will create SLA risk next week.

Stronger version:

> I do not want staffing decisions to be reactive after SLA misses happen. Module D turns backlog, inflow, throughput, complexity, and contributor availability into an early-warning view so managers can rebalance work, cross-train, or add coverage before customer impact lands.

## Where Module D Fits

After showing Modules A, B, and C, say:

> Module A tells me where operational health is degrading. Module B tells me whether escalations are recurring. Module C tells me whether quality risk is emerging in the distributed workforce. Module D tells me whether we have enough trained capacity to protect SLA and quality next week.

## Demo Flow

### 1. Open Module D

Open the Streamlit sidebar page:

```text
4 Module D Capacity SLA Forecasting
```

Say:

> This page is deliberately framed as capacity planning, workload balancing, SLA protection, and quality preservation. It is not a productivity surveillance dashboard.

### 2. Executive Capacity and SLA Forecast Summary

Point out the KPI tiles:

- Total open backlog
- Aged backlog over 72h
- High-risk work types
- High-risk teams
- Average utilization rate
- Average SLA adherence 7d
- Projected SLA at-risk work types
- Largest capacity gap
- Top overloaded team
- Recommended next staffing action

Say:

> This gives a regional leader the weekly staffing picture: where demand, backlog, utilization, and SLA risk are moving before customer impact lands.

### 3. Work-Type Capacity Risk Table

Show the table.

Call out:

- Open backlog
- Aged backlog over 72h
- New items 7d
- Completed items 7d
- Inflow vs throughput gap
- Estimated days to clear backlog
- SLA adherence 7d
- Rework rate
- Active contributors
- Capacity units
- Required capacity units
- Capacity gap
- Utilization rate
- Forecasted SLA risk
- Capacity risk score
- Recommended capacity action

Say:

> This answers whether the problem is demand growth, throughput shortage, backlog age, utilization pressure, complexity mix, or quality/rework drag.

### 4. Team Capacity Risk Table

Show the table.

Call out:

- Manager name
- Active and available contributors
- Team backlog
- Aged backlog
- Inflow and throughput
- Complexity mix
- Low-tenure share
- Quality risk overlay
- Escalation risk overlay
- Recommended manager action

Say:

> At the team level, I can see whether a manager needs more coverage, cross-training, routing support, or a quality/workflow intervention.

### 5. Capacity Forecast View

Show the charts:

- Capacity risk by work type
- Capacity gap by team
- Utilization by team
- Open backlog by work type
- Aged backlog by team
- SLA adherence trend for selected work type
- Inflow vs throughput trend for selected work type
- High-complexity backlog by team

Say:

> The chart view lets me separate the failure mode. If inflow is rising and throughput is flat, I need staffing or routing. If rework is high, adding volume may make the issue worse. If high-complexity backlog is concentrated in one team, I need senior reviewer coverage or cross-training.

### 6. Work-Type Drilldown

Select a work type such as `audio_evaluation`, `rlhf_evaluation`, or `code_review`.

Say:

> Here I can inspect open backlog, aged backlog, recent inflow, recent throughput, throughput gap, SLA trend, rework drag, complexity mix, active contributors, capacity gap, top risk drivers, and the recommended capacity action.

Example:

> If Module A showed audio evaluation backlog pressure, Module D tells me whether the cause is rising inflow, insufficient throughput, aged backlog, high-complexity work, or team capacity imbalance.

### 7. Team Drilldown

Select a team with high or medium capacity risk.

Say:

> This is the manager conversation. I can see utilization, capacity gap, backlog, complexity mix, low-tenure share, quality risk overlay, escalation risk overlay, and recommended action.

Example:

> If a team has high utilization and high-complexity backlog, I would not simply push harder. I would rebalance complex work, add coverage, or cross-train senior contributors.

### 8. Weekly Staffing and Capacity Review Queue

Show the queue.

Say:

> This queue is for weekly staffing and capacity review. It combines capacity risk score, capacity gap, aged backlog, throughput gap, SLA miss rate, utilization, complexity, quality risk, escalation risk, and team blast radius.

Emphasize:

> This is not a worker productivity leaderboard. It is a management decision queue for staffing, routing, cross-training, backlog burn-down, and SLA recovery.

### 9. Capacity Action Card Generator

Generate a card for a high-risk team or work type.

Say:

> This turns the signal into an action card: risk level, capacity signal summary, evidence, likely driver, recommended staffing or routing action, owner, metric to monitor, decision needed, and follow-up date.

Example explanation:

> If backlog is growing faster than throughput, the action may be short-term staffing or work rerouting. If rework is high, the action is quality and workflow review before adding volume. If recurring escalations are active, a structural fix owner is required before scaling volume.

### 10. Module D Weekly Staffing and Capacity Briefing

Show the generated briefing.

Say:

> This is the staffing and capacity section I would bring into the weekly operating review. It is deterministic and explainable first. Later, an LLM could polish the narrative, but the operating logic remains transparent.

## Cross-Module Story

Use this sequence:

1. Module A shows audio evaluation backlog and SLA pressure.
2. Module B shows recurring capacity shortfall or SLA miss escalations.
3. Module C shows whether quality/rework is creating capacity drag.
4. Module D shows whether the issue is driven by inflow growth, throughput gap, high utilization, aged backlog, or insufficient skilled capacity.
5. Module D generates a staffing or routing action card.
6. The weekly operating review has a clear owner, decision, metric to monitor, and follow-up date.

## Closing Line

> Module A shows where the operation is unhealthy. Module B shows whether escalations are recurring system failures. Module C shows whether distributed workforce quality risk is emerging. Module D shows whether capacity, staffing, throughput, and skill mix are sufficient to protect SLA and quality before customer impact.
