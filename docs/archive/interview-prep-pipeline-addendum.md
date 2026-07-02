# Interview Prep Addendum — Pipeline & Scalability Questions

Use alongside the main interview-prep-ops-dashboard.md. These answers
assume the pipeline sprint is complete.

-----

## Live demo moment — rehearse this sequence

1. Aurora is open showing “Current” scenario. Walk through KPIs.
1. Say: *“Let me show you the pipeline behind this.”*
1. Open terminal, run: `python -m src.pipeline --scenario crisis`
1. Point to the manifest output — row counts, validation, timestamp.
1. Refresh Aurora, click “Crisis” scenario.
1. Say: *“Same scoring engine, different operating conditions. The KPIs,
   patterns, and team risk all recomputed in under 5 seconds. In production
   this is a scheduled Airflow DAG reading from the warehouse — the only
   change is the data source adapter.”*

-----

## “How do you handle data refresh and staleness?”

“Every pipeline run stamps `generated_at` into the payload — you can see
it in the Aurora footer right now. In production I’d add two things: a
staleness threshold that turns the badge amber if data is older than the
refresh SLA (say 4 hours for a daily cadence), and an alerting hook that
pages the on-call if the pipeline fails or validates below row-count
thresholds. The validation step already exists — it checks required keys
and non-zero counts before the pipeline reports PASS.”

## “How would this connect to real systems at Scale?”

“The `src/` scoring modules are data-source-agnostic — they take pandas
DataFrames and return scored results. Today those DataFrames come from
CSVs; in production, a scheduled job queries the labeling platform API,
the QA database, JIRA for escalations, and the CSAT survey tool. Each
source gets a thin adapter that returns a DataFrame in the expected schema.
The scoring engine, the 83 tests, and the Aurora frontend don’t change.
Scaling to high volume means paginated warehouse queries and possibly
partitioning by region — the pipeline is already parameterized by region.”

## “What if you need real-time, not batch?”

“The batch pipeline is the right tool for the weekly operating review —
leadership doesn’t need sub-second latency on a staffing decision. But
for live escalation alerts, I’d add a lightweight event listener
(websocket or SSE) that watches the ticketing system’s event stream and
pushes new escalations into the Aurora view without waiting for the next
batch run. The batch numbers stay authoritative for KPIs and trends; the
real-time layer only handles the ‘something just broke’ signal. Two
paths, not one path trying to do both.”

## “What breaks first at 10x volume?”

“CSV I/O. That’s the first thing to swap — move to partitioned Parquet
or direct warehouse queries. The pandas scoring logic is vectorized and
handles tens of thousands of rows fine. The next bottleneck would be the
single-region assumption — at 10x you’re probably multi-region, so the
pipeline needs to run per-region in parallel and the dashboard needs a
region aggregation view. The architecture already supports that: the
region parameter exists in the pipeline and the Aurora picker.”

## “Why not just use Airflow / dbt / a real orchestrator?”

“For the same reason I didn’t use Tableau — the prototype demonstrates
the *operating logic*, not the infrastructure. In production I’d
absolutely use Airflow for scheduling, dbt for transforms if we’re
warehouse-native, and a proper CI/CD pipeline for the scoring engine.
The point of the prototype is that the decision logic is tested, version-
controlled, and separated from both the infrastructure and the UI.
Dropping it into Airflow is a deployment decision, not an architecture
change.”