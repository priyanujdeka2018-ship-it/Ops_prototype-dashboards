# Module B Handoff: Escalation Pattern Recurrence Detector

## Current Prototype Context

The repo now contains two modules in the Scale Regional Ops Command Center prototype:

1. **Module A: Regional Operations Health Dashboard**
2. **Module B: Escalation Pattern Recurrence Detector**

Module A tells a regional operations leader where regional health is degrading. Module B tells the leader whether escalations are isolated incidents or recurring operating-system failures.

## Business Goal

A regional operations leader needs to know when escalations are not isolated events but repeat patterns across work types, teams, customer segments, severity levels, and root causes.

Module B answers:

1. Which escalation patterns are repeating?
2. Which work types, teams, customer segments, and root causes are recurring?
3. Which patterns are becoming more severe or more frequent?
4. Which patterns are unresolved or slow to resolve?
5. What should leadership do about repeat escalations?

## Integration With Module A

Module B reuses the existing Module A escalation file:

- `data/escalation_events.csv`

It uses the shared fields already present in Module A:

- `escalation_id`
- `date`
- `work_type`
- `team_id`
- `severity`
- `customer_segment`
- `escalation_summary`
- `root_cause_category`
- `status`
- `days_to_resolve`

This keeps Module B integrated with the existing app instead of creating a disconnected prototype.

## Added Files

- `src/escalation_patterns.py`
- `src/escalation_briefing.py`
- `docs/MODULE_B_HANDOFF.md`

## Pattern Key Builder

Module B creates deterministic pattern keys using four possible grains:

1. `work_type + root_cause_category`
2. `work_type + team_id + root_cause_category`
3. `customer_segment + work_type + root_cause_category`
4. `team_id + severity + root_cause_category`

The Streamlit UI lets the user choose the grain depending on whether they want a broad systemic view or a narrower team/customer drilldown.

## Recurrence Scoring

For each pattern, Module B calculates:

- `escalation_count`
- `unique_teams_impacted`
- `unique_customer_segments_impacted`
- `sev1_count`
- `sev2_count`
- `open_count`
- `resolved_count`
- `avg_days_to_resolve`
- `latest_escalation_date`
- `first_seen_date`
- `recurrence_window_days`
- `last_14d_count`
- `prior_14d_count`
- `last_30d_count`
- `last_60d_count`

The deterministic risk score is based on:

```text
score = escalation_count * 2
      + sev1_count * 5
      + sev2_count * 3
      + open_count * 2
      + unique_customer_segments_impacted * 1.5
      + unresolved_or_slow_resolution_penalty
      + acceleration_bonus
```

Risk levels:

- `High recurrence risk`
- `Medium recurrence risk`
- `Low recurrence risk`

## Pattern Status Rules

Module B classifies each pattern as:

- `New`: first seen in the last 14 days
- `Recurring`: 3+ escalations in the last 60 days
- `Accelerating`: last 14-day count is greater than prior 14-day count
- `Dormant`: no escalation in the last 30 days
- `Resolved`: recurring pattern with no open escalations
- `Watchlist`: 2 escalations in the last 60 days
- `Low activity`: does not meet the above thresholds

## Streamlit UI Sections

Module B is integrated into `app.py` after the Module A weekly ops briefing generator.

Sections:

1. Recurring Escalation Pattern Summary
2. Top Repeat Root Causes
3. Pattern Risk Table
4. Pattern Drilldown
5. Recommended Leadership Actions
6. Escalation Pattern Briefing Generator

Filters:

- `work_type`
- `team_id`
- `customer_segment`
- `severity`
- `root_cause_category`
- `status`

Charts:

- Top recurring root causes
- Escalation patterns by work type
- Open recurring patterns by severity
- Pattern status mix
- Trend of selected pattern over time

## Deterministic Leadership Summary

The button **Generate Escalation Pattern Briefing** creates a markdown briefing with:

- Executive TL;DR
- Top recurring patterns
- Likely systemic causes
- Recommended leadership actions
- Risks if not addressed
- Questions for frontline managers

No LLM API is used. The briefing is template-driven and explainable.

## Interview Positioning

Use this line:

> Module A tells me where regional health is degrading. Module B tells me whether escalations are isolated incidents or recurring operating-system failures. This helps leadership move from reactive escalation handling to pattern-based prevention.

## Demo Talk Track

After identifying an unhealthy work type in Module A, use Module B to check whether the issue is part of a recurring escalation pattern. For example, if RLHF evaluation has SLA pressure and rising escalations, Module B can show whether the repeat driver is policy ambiguity, reviewer misalignment, customer requirement changes, tooling issues, or capacity shortfall.

## Operating Value

Module B shows that the prototype is not just a dashboard. It detects repeat failure modes, separates one-off incidents from systemic patterns, connects escalation themes to teams, work types, and customers, and creates a leadership action loop for weekly retros.
