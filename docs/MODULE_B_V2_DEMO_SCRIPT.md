# Module B v2 Demo Script: Semantic Escalation Clustering and Structural Fix Cards

## Prototype Context

The Scale Regional Ops Command Center now has three interview-ready layers:

1. Module A: Regional Operations Health Dashboard
2. Module B v1: Deterministic Escalation Pattern Recurrence Detector
3. Module B v2: Semantic Escalation Clustering and Structural Fix Cards

Module A shows where regional health is degrading.

Module B v1 checks whether escalations are recurring using explainable pattern keys.

Module B v2 adds semantic clustering so the prototype can detect recurring escalation themes even when teams describe the same problem differently.

## Interview Positioning

Use this line:

"I built Module B in two layers. First, I used deterministic pattern keys for explainability. Then I added semantic clustering with TF-IDF so the system can detect recurring escalation patterns even when teams describe the same operating breakdown differently."

## Business Problem

Escalations are often treated as individual fires.

In reality, the same operating failure can appear across different work types, teams, customer segments, severity levels, root cause labels, and escalation wording.

A regional operations leader needs to know whether an escalation is isolated or part of a repeated failure mode.

## What Module B v2 Adds

Module B v2 adds:

- TF-IDF vectorization of escalation summaries
- Cosine similarity clustering
- Semantic cluster summary table
- Cluster recurrence status
- Risk scoring
- Cluster drilldown
- Structural fix card generator
- Weekly retro queue

It does not use paid APIs or LLM calls.

## Demo Flow

### 1. Start With Module A

Open the main Streamlit app with:

streamlit run app.py

Say:

"Module A gives me the operating health view. If I see pressure in SLA, quality, CSAT, or escalation rate, I use Module B to understand whether the issue is recurring."

### 2. Show Module B v1

In the main app, scroll to:

Module B: Escalation Pattern Recurrence Detector

Say:

"This is the deterministic version. It groups repeat escalation patterns using explainable keys like work type plus root cause, team plus root cause, or customer segment plus work type plus root cause."

Point out:

- Recurring escalation pattern summary
- Pattern risk table
- Pattern drilldown
- Recommended leadership actions
- Escalation pattern briefing

Say:

"This mode is useful because it is transparent. A manager can understand exactly why a pattern is grouped."

### 3. Open Module B v2 Page

In the Streamlit sidebar, select:

2 Module B v2 Semantic Clusters

Say:

"This is the semantic layer. It uses TF-IDF and cosine similarity to detect similar escalation summaries even when the wording differs."

### 4. Explain the Clustering Controls

Show:

- Work type filter
- Team filter
- Customer segment filter
- Severity filter
- Root cause filter
- Status filter
- Semantic similarity threshold
- Minimum recurring cluster size

Say:

"The similarity threshold lets me tune how strict the clustering should be. A higher threshold creates tighter clusters. A lower threshold captures broader recurring themes."

### 5. Review Semantic Cluster Summary

Point to:

- Semantic cluster ID
- Cluster name
- Incident count
- Severity mix
- Dominant work type
- Dominant root cause
- Affected teams
- Affected customer segments
- Open count
- Average days to resolve
- Last 60 day count
- Recurrence status
- Risk score
- Risk level

Say:

"This table helps separate isolated escalations from repeat operating-system failures."

### 6. Use Cluster Drilldown

Select a high-risk cluster.

Say:

"Here I can see the actual escalation records behind the cluster, the timeline of incidents, affected teams, affected customer segments, and open escalations."

Point out:

- Risk level
- Incident count
- Open count
- Average days to resolve
- Trend over time
- Recent escalation summaries

### 7. Show Structural Fix Card

Scroll to:

Structural Fix Card

Say:

"This is the most important leadership artifact. The output is not just a chart. It becomes a decision card for the weekly ops retro."

Explain each section:

- Problem statement
- Evidence
- Likely root cause
- Durable fix recommendation
- Owner suggestion
- Metric to monitor
- Decision needed
- Follow-up date

Say:

"This converts repeated escalation pain into a durable operating fix."

### 8. Show Weekly Retro Queue

Scroll to:

Weekly Retro Queue

Say:

"This is what I would use in the weekly operating review. It ranks the recurring patterns that deserve leadership attention first."

## Strong Interview Talk Track

Use this:

"I do not treat escalations as isolated fires. I built a recurrence detector that first uses deterministic pattern keys for explainability, then adds semantic clustering to catch repeated operating breakdowns even when the wording differs. The output is a structural fix card that gives leadership the problem statement, evidence, likely root cause, owner, metric, decision needed, and follow-up date."

## What This Shows

This prototype shows that I can:

- Detect repeated operating failure modes
- Separate one-off escalations from systemic patterns
- Use deterministic analytics before adding LLMs
- Convert escalation data into weekly leadership decisions
- Connect work type, team, customer segment, severity, and root cause
- Build an operating loop from detection to ownership to follow-up

## Optional Future Enhancements

Future upgrades could include:

- Sentence-transformers embeddings
- OpenAI embeddings
- LLM-written fix card summaries
- Exportable fix card history
- Integration with Module C quality drift scoring
- Scheduled weekly retro report generation
