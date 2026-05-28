# Module C Demo Script: Distributed Workforce Quality Scorer

## Positioning Line

> Module C extends the command center from regional health and escalation recurrence into distributed workforce quality risk. It helps managers identify coaching, calibration, training, and staffing actions before quality drift becomes customer impact.

Stronger version:

> I do not want to use quality data as a punitive scoreboard. I want to use it as an operating signal. Module C identifies where quality risk is emerging across teams, cohorts, and work types, then turns that signal into coaching and calibration actions.

## Transition From Modules A and B

After showing Modules A and B, say:

> Module A tells me where operational health is degrading. Module B tells me whether escalations are recurring. Module C tells me whether quality risk is emerging in the distributed workforce and what manager action is needed.

## Recommended Demo Flow

### 1. Start With Module A

Show the regional health dashboard and call out a quality or rework pressure area.

Say:

> Module A shows me the operating symptom. For example, if code review quality is degrading or rework is rising, I know where to inspect next.

### 2. Connect to Module B

Show a recurring escalation pattern, especially one related to quality defect, reviewer misalignment, policy ambiguity, or workflow handoff.

Say:

> Module B tells me whether this is a one-off issue or a recurring operating-system failure. If reviewer misalignment or quality defects repeat, I need to understand whether the workforce quality system is drifting.

### 3. Open Module C

Open the Streamlit sidebar page:

```text
3 Module C Workforce Quality Scorer
```

Say:

> Module C looks below the regional metric and checks whether quality risk is concentrated by team, contributor cohort, work type, tenure, skill level, task complexity, rework, reviewer override, or peer disagreement.

### 4. Executive Workforce Quality Summary

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

> This is the workforce quality operating summary. It tells me where quality risk is showing up and which driver is most important this week.

### 5. Contributor Quality Risk Table

Show the contributor table.

Say:

> This is not a punitive leaderboard. It is a coaching and calibration signal. I am looking for patterns such as low gold-task pass rate, reviewer overrides, low peer agreement, rework, recent quality drop, or low-tenure contributors handling high-complexity work.

Call out these fields:

- Sampled quality events
- Average quality score
- Gold task fail rate
- Reviewer override rate
- Peer agreement score
- Rework rate
- Quality delta
- Risk status
- Recommended action

### 6. Team Quality Risk Table

Show the team table.

Say:

> At the team level, I can see whether risk is isolated to one contributor or whether it is becoming a manager-level quality-system issue.

Call out:

- Active contributors
- High-risk contributor count
- Quality drift flag
- Team risk score
- Team risk level
- Recommended manager action

### 7. Quality Drift View

Show the charts:

- Quality risk by work type
- High-risk contributors by team
- Gold task fail rate by team
- Reviewer override rate by team
- Rework rate by work type
- Quality trend for selected team

Say:

> This helps me separate the failure mode. If gold-task fail rate is high, I may need targeted coaching. If reviewer overrides are high and peer agreement is low, I may need calibration. If rework is concentrated in a work type, I may need SOP or task-instruction review.

### 8. Contributor Drilldown

Select one contributor with high or medium risk.

Say:

> The drilldown shows the evidence behind the signal: quality history, gold pass/fail history, reviewer overrides, peer agreement, rework, and task complexity mix. The goal is to decide the right support action, not to shame the contributor.

### 9. Team Drilldown

Select one high-risk or drifting team.

Say:

> The team drilldown gives the manager conversation: quality trend, high-risk contributor count, top drivers, recent quality events, and recommended manager action.

### 10. Weekly Coaching and Calibration Queue

Show the queue.

Say:

> This queue is designed for the weekly operating rhythm. It combines risk score, quality delta, gold-task failure, reviewer overrides, rework, peer agreement, sample size, and team blast radius. It prioritizes where managers should review coaching, calibration, training, staffing, or SOP action.

Emphasize:

> I would never present this as a punitive leaderboard. The label is intentional: Weekly Coaching and Calibration Queue.

### 11. Quality Coaching Card Generator

Generate a card for a high-risk contributor or team.

Say:

> This converts the signal into a manager-ready action card: risk summary, evidence, likely driver, recommended action, owner, metric to monitor, decision needed, and follow-up date.

Example explanation:

> If the driver is reviewer calibration drift, the action is a calibration huddle and QA sampling increase. If the driver is low tenure plus high complexity, the action is a training update and gradual ramp.

### 12. Weekly Quality Briefing

Show the Module C weekly briefing.

Say:

> This is the quality section I would bring into a weekly operating review. It is deterministic and explainable first. Later, an LLM could polish the narrative, but the operating logic remains transparent.

## Strong Closing Line

> Module A shows where the operation is unhealthy. Module B shows whether escalations are recurring system failures. Module C shows whether distributed workforce quality risk is emerging and what coaching, calibration, or staffing action should happen next.

## Interview Emphasis

Use these points if challenged:

- Synthetic data only; no real Scale AI data.
- Deterministic scoring before AI summarization.
- Explainable risk drivers, not black-box ranking.
- Quality risk is used for coaching, calibration, training, staffing, and SOP review.
- The weekly queue creates manager action and follow-up metrics.
- Module C connects directly to Module A health degradation and Module B escalation recurrence.

## Possible Interview Question: Why Not Rank Contributors?

Answer:

> Ranking contributors can create the wrong incentive. I would rather use quality signals to identify where the operating system needs support: calibration, coaching, better task instructions, training, ramp management, or staffing changes. The unit of action is the manager review and quality system, not punishment.
