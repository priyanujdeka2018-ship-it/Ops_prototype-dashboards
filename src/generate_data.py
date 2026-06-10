"""
Synthetic data generation for the Scale Regional Ops Health Dashboard.

Generates realistic but fake data for:
- work_items.csv
- teams.csv
- contributors.csv
- sla_events.csv
- quality_events.csv
- escalation_events.csv
- csat_events.csv

No real Scale AI data is used.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import random

import numpy as np
import pandas as pd


RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

REGION = "APAC"

WORK_TYPES = [
    "image_annotation",
    "rlhf_evaluation",
    "code_review",
    "audio_evaluation",
    "expert_review",
]

WORK_TYPE_PROFILES = {
    "image_annotation": {
        "volume_weight": 0.35,
        "base_sla": 0.965,
        "base_quality": 92,
        "base_csat": 4.55,
        "base_rework": 0.05,
        "sla_hours": 24,
    },
    "rlhf_evaluation": {
        "volume_weight": 0.25,
        "base_sla": 0.925,
        "base_quality": 88,
        "base_csat": 4.30,
        "base_rework": 0.08,
        "sla_hours": 36,
    },
    "code_review": {
        "volume_weight": 0.18,
        "base_sla": 0.935,
        "base_quality": 87,
        "base_csat": 4.35,
        "base_rework": 0.09,
        "sla_hours": 48,
    },
    "audio_evaluation": {
        "volume_weight": 0.14,
        "base_sla": 0.915,
        "base_quality": 89,
        "base_csat": 4.25,
        "base_rework": 0.07,
        "sla_hours": 48,
    },
    "expert_review": {
        "volume_weight": 0.08,
        "base_sla": 0.895,
        "base_quality": 91,
        "base_csat": 4.20,
        "base_rework": 0.06,
        "sla_hours": 72,
    },
}

CUSTOMER_SEGMENTS = ["startup", "mid_market", "enterprise", "strategic"]
PRIORITIES = ["low", "medium", "high", "urgent"]
TASK_COMPLEXITIES = ["low", "medium", "high", "expert"]
SHIFT_TYPES = ["day", "night", "follow_the_sun", "weekend", "hybrid"]
LOCATION_TYPES = ["remote", "hub", "hybrid", "vendor_site"]
SKILL_LEVELS = ["junior", "intermediate", "senior", "expert"]

DELAY_REASONS = [
    "volume_spike",
    "reviewer_shortage",
    "tool_latency",
    "customer_clarification_pending",
    "quality_rework",
    "specialist_unavailable",
    "policy_ambiguity",
    "handoff_delay",
]

ROOT_CAUSES = [
    "sla_miss",
    "quality_defect",
    "policy_ambiguity",
    "capacity_shortfall",
    "tooling_issue",
    "customer_requirement_change",
    "reviewer_misalignment",
    "workflow_handoff_gap",
]

FEEDBACK_THEMES = [
    "timeliness",
    "accuracy",
    "communication",
    "calibration",
    "responsiveness",
    "tooling",
    "handoff_quality",
]

MANAGER_NAMES = [
    "Ananya Rao",
    "Vikram Menon",
    "Priya Sharma",
    "Rahul Iyer",
    "Neha Kapoor",
    "Arjun Mehta",
    "Meera Nair",
    "Kabir Sinha",
    "Ritika Bose",
    "Sanjay Das",
    "Isha Verma",
    "Karan Khanna",
    "Aditi Pillai",
    "Rohan Gupta",
    "Sneha Reddy",
]

CITIES = ["Bangalore", "Hyderabad", "Pune", "Gurgaon", "Mumbai", "Chennai"]

# Deliberate repeat escalation patterns so Module B v1 recurrence scoring and
# Module B v2 semantic clustering surface clear repeat clusters in the demo.
# Each pattern spans multiple weeks with rising weekly volume; severity
# escalates from sev4/sev3 early to sev2/sev1 in the most recent weeks.
RECURRING_ESCALATION_PATTERNS = [
    {
        "work_type": "rlhf_evaluation",
        "root_cause": "policy_ambiguity",
        "weekly_counts": [2, 2, 3, 3, 4, 5, 6, 7],
        "summaries": [
            "RLHF raters disagree on refusal policy for borderline prompts; guidance unclear.",
            "Preference ranking blocked because policy guidance for sensitive prompts is ambiguous.",
            "Customer flagged inconsistent RLHF ratings traced to ambiguous policy wording.",
            "Raters keep escalating borderline prompt policy questions; no canonical examples published.",
            "Policy ambiguity in the RLHF evaluation rubric causing repeated rating disputes.",
        ],
    },
    {
        "work_type": "code_review",
        "root_cause": "quality_defect",
        "weekly_counts": [2, 2, 2, 3, 4, 4, 5, 6],
        "summaries": [
            "Recurring quality defects in code review batch; gold tasks failing on edge cases.",
            "Customer rejected code review deliverable after missed defects in error handling.",
            "Defect leakage in the code review queue rising; rework loops repeating weekly.",
            "Code review quality defect cluster: reviewers missing security-sensitive bugs.",
            "Repeated quality defects found post-delivery in code review samples.",
        ],
    },
    {
        "work_type": "expert_review",
        "root_cause": "customer_requirement_change",
        "weekly_counts": [1, 2, 2, 3, 3, 4, 5, 5],
        "summaries": [
            "Expert review specs changed by customer mid-batch; rubric now out of date.",
            "Customer requirement change invalidated expert review guidance for the active queue.",
            "Expert reviewers working from stale requirements after a customer spec update.",
            "Requirement churn from the customer forcing repeated expert review rework.",
            "Another customer requirement change hit expert review; instructions not propagated.",
        ],
    },
    {
        "work_type": "audio_evaluation",
        "root_cause": "capacity_shortfall",
        "weekly_counts": [1, 1, 2, 2, 3, 4, 5, 6],
        "summaries": [
            "Audio evaluation backlog growing; not enough specialist reviewers on shift.",
            "Capacity shortfall in the audio evaluation queue; SLA buffer exhausted.",
            "Audio eval staffing gap repeating during weekend coverage; queue aging past 72 hours.",
            "Specialist shortage for audio evaluation; aged backlog climbing week over week.",
            "Audio evaluation throughput below inflow again due to capacity shortfall.",
        ],
    },
    {
        "work_type": "rlhf_evaluation",
        "root_cause": "reviewer_misalignment",
        "weekly_counts": [1, 1, 2, 2, 3, 3, 4, 4],
        "summaries": [
            "RLHF reviewer agreement dropping; calibration drift between rater cohorts.",
            "Reviewer misalignment in RLHF evaluations; overrides spiking on the same task family.",
            "Two RLHF reviewer pods scoring the same prompts differently; calibration overdue.",
            "RLHF reviewer disagreement recurring on preference ranking; alignment huddle needed.",
            "Misaligned RLHF reviewers producing conflicting labels for identical prompt types.",
        ],
    },
]


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def random_datetime_between(start_date: datetime, end_date: datetime) -> datetime:
    seconds = int((end_date - start_date).total_seconds())
    return start_date + timedelta(seconds=random.randint(0, seconds))


def is_recent(date_value: datetime, end_date: datetime, days: int = 14) -> bool:
    return date_value >= end_date - timedelta(days=days)


def generate_teams() -> pd.DataFrame:
    rows = []
    team_counter = 1

    teams_per_work_type = {
        "image_annotation": 4,
        "rlhf_evaluation": 3,
        "code_review": 3,
        "audio_evaluation": 3,
        "expert_review": 2,
    }

    for work_type, team_count in teams_per_work_type.items():
        short_name = work_type.split("_")[0].upper()

        for idx in range(1, team_count + 1):
            team_id = f"TEAM_{REGION}_{short_name}_{idx:02d}"
            active_contributors = random.randint(18, 45)

            if work_type == "expert_review":
                active_contributors = random.randint(10, 22)

            rows.append(
                {
                    "team_id": team_id,
                    "region": REGION,
                    "city": random.choice(CITIES),
                    "manager_name": MANAGER_NAMES[(team_counter - 1) % len(MANAGER_NAMES)],
                    "work_type": work_type,
                    "active_contributors": active_contributors,
                    "shift_type": random.choice(SHIFT_TYPES),
                }
            )
            team_counter += 1

    return pd.DataFrame(rows)


def generate_contributors(teams: pd.DataFrame) -> pd.DataFrame:
    rows = []
    contributor_counter = 1

    for _, team in teams.iterrows():
        for _ in range(int(team["active_contributors"])):
            contributor_id = f"CONTR_{contributor_counter:05d}"
            tenure_days = int(np.random.gamma(shape=3.2, scale=90))
            tenure_days = max(10, min(900, tenure_days))

            rows.append(
                {
                    "contributor_id": contributor_id,
                    "team_id": team["team_id"],
                    "tenure_days": tenure_days,
                    "skill_level": np.random.choice(
                        SKILL_LEVELS,
                        p=[0.22, 0.43, 0.25, 0.10],
                    ),
                    "location_type": np.random.choice(
                        LOCATION_TYPES,
                        p=[0.45, 0.25, 0.20, 0.10],
                    ),
                    "active_status": np.random.choice(
                        ["active", "inactive", "on_leave", "training"],
                        p=[0.86, 0.04, 0.04, 0.06],
                    ),
                }
            )
            contributor_counter += 1

    return pd.DataFrame(rows)


def adjusted_profile(work_type: str, created_at: datetime, end_date: datetime) -> dict:
    profile = WORK_TYPE_PROFILES[work_type].copy()

    # Scenario 2: RLHF stress in recent period.
    if work_type == "rlhf_evaluation" and is_recent(created_at, end_date, 14):
        profile["base_sla"] -= 0.10
        profile["base_csat"] -= 0.18
        profile["base_rework"] += 0.035

    # Scenario 3: Code review quality and rework pressure in recent period.
    if work_type == "code_review" and is_recent(created_at, end_date, 21):
        profile["base_quality"] -= 5
        profile["base_rework"] += 0.055
        profile["base_sla"] -= 0.025

    # Scenario 4: Audio backlog and SLA pressure in recent period.
    if work_type == "audio_evaluation" and is_recent(created_at, end_date, 18):
        profile["base_sla"] -= 0.07
        profile["base_csat"] -= 0.10

    # Scenario 5: Expert review has high-severity escalation risk.
    if work_type == "expert_review":
        profile["base_sla"] -= 0.015

    return profile


def generate_work_items(
    teams: pd.DataFrame,
    contributors: pd.DataFrame,
    n_items: int = 14000,
) -> pd.DataFrame:
    end_date = datetime.now().replace(microsecond=0, second=0, minute=0)
    start_date = end_date - timedelta(days=90)

    team_lookup = teams.groupby("work_type")["team_id"].apply(list).to_dict()
    contributor_lookup = contributors.groupby("team_id")["contributor_id"].apply(list).to_dict()

    work_type_weights = [WORK_TYPE_PROFILES[w]["volume_weight"] for w in WORK_TYPES]

    rows = []

    for i in range(1, n_items + 1):
        work_type = np.random.choice(WORK_TYPES, p=work_type_weights)
        team_id = random.choice(team_lookup[work_type])
        contributor_id = random.choice(contributor_lookup[team_id])

        created_at = random_datetime_between(start_date, end_date)
        profile = adjusted_profile(work_type, created_at, end_date)

        priority = np.random.choice(PRIORITIES, p=[0.18, 0.50, 0.24, 0.08])
        complexity = np.random.choice(TASK_COMPLEXITIES, p=[0.30, 0.43, 0.20, 0.07])

        if work_type == "expert_review":
            complexity = np.random.choice(TASK_COMPLEXITIES, p=[0.05, 0.20, 0.40, 0.35])

        sla_due_at = created_at + timedelta(hours=profile["sla_hours"])

        is_open_probability = 0.08
        if is_recent(created_at, end_date, 10):
            is_open_probability = 0.16
        if work_type == "audio_evaluation" and is_recent(created_at, end_date, 18):
            is_open_probability = 0.24

        is_open = random.random() < is_open_probability

        if is_open:
            status = np.random.choice(["queued", "in_progress", "blocked"], p=[0.32, 0.53, 0.15])
            completed_at = None
            date_completed = None
            sla_met = False if datetime.now() > sla_due_at else None
        else:
            sla_met = random.random() < profile["base_sla"]

            if sla_met:
                completion_hours = random.uniform(1, profile["sla_hours"] * 0.95)
            else:
                completion_hours = profile["sla_hours"] + random.uniform(1, 36)

            completed_at = created_at + timedelta(hours=completion_hours)
            date_completed = completed_at
            status = "completed"

        rework_probability = profile["base_rework"]
        if complexity == "high":
            rework_probability += 0.025
        if complexity == "expert":
            rework_probability += 0.045

        rework_required = random.random() < rework_probability if status == "completed" else False

        rows.append(
            {
                "work_item_id": f"WI_{i:06d}",
                "date_created": created_at,
                "date_completed": date_completed,
                "region": REGION,
                "work_type": work_type,
                "team_id": team_id,
                "contributor_id": contributor_id,
                "customer_segment": np.random.choice(
                    CUSTOMER_SEGMENTS,
                    p=[0.22, 0.31, 0.32, 0.15],
                ),
                "priority": priority,
                "status": status,
                "sla_due_at": sla_due_at,
                "completed_at": completed_at,
                "sla_met": sla_met,
                "rework_required": rework_required,
                "task_complexity": complexity,
            }
        )

    return pd.DataFrame(rows)


def generate_sla_events(work_items: pd.DataFrame) -> pd.DataFrame:
    rows = []

    completed = work_items[work_items["status"] == "completed"].copy()

    for i, (_, item) in enumerate(completed.iterrows(), start=1):
        due_at = pd.to_datetime(item["sla_due_at"])
        completed_at = pd.to_datetime(item["completed_at"])
        sla_met = bool(item["sla_met"])

        delay_hours = 0.0
        delay_reason = None

        if not sla_met:
            delay_hours = round(max(0, (completed_at - due_at).total_seconds() / 3600), 2)

            if item["work_type"] == "rlhf_evaluation":
                delay_reason = np.random.choice(
                    ["policy_ambiguity", "reviewer_shortage", "handoff_delay"],
                    p=[0.45, 0.40, 0.15],
                )
            elif item["work_type"] == "audio_evaluation":
                delay_reason = np.random.choice(
                    ["specialist_unavailable", "volume_spike", "tool_latency"],
                    p=[0.55, 0.30, 0.15],
                )
            elif item["work_type"] == "code_review":
                delay_reason = np.random.choice(
                    ["quality_rework", "reviewer_shortage", "customer_clarification_pending"],
                    p=[0.45, 0.30, 0.25],
                )
            else:
                delay_reason = random.choice(DELAY_REASONS)

        rows.append(
            {
                "event_id": f"SLA_{i:06d}",
                "work_item_id": item["work_item_id"],
                "due_at": due_at,
                "completed_at": completed_at,
                "sla_met": sla_met,
                "delay_hours": delay_hours,
                "delay_reason": delay_reason,
            }
        )

    return pd.DataFrame(rows)


def generate_quality_events(work_items: pd.DataFrame) -> pd.DataFrame:
    rows = []
    completed = work_items[work_items["status"] == "completed"].copy()

    sampled = completed.sample(frac=0.62, random_state=RANDOM_SEED).reset_index(drop=True)

    for i, item in sampled.iterrows():
        created_at = pd.to_datetime(item["date_created"]).to_pydatetime()
        end_date = datetime.now()
        profile = adjusted_profile(item["work_type"], created_at, end_date)

        score = np.random.normal(profile["base_quality"], 5.0)

        if item["task_complexity"] == "high":
            score -= np.random.uniform(1, 3)
        if item["task_complexity"] == "expert":
            score -= np.random.uniform(2, 5)
        if bool(item["rework_required"]):
            score -= np.random.uniform(4, 10)

        score = round(float(np.clip(score, 55, 99)), 1)

        gold_task_pass = score >= np.random.normal(84, 4)
        reviewer_override = random.random() < (0.04 if score >= 85 else 0.12)
        peer_agreement = round(float(np.clip(np.random.normal(0.86, 0.08), 0.55, 0.99)), 2)

        if item["work_type"] == "code_review" and is_recent(created_at, end_date, 21):
            peer_agreement = round(max(0.50, peer_agreement - 0.08), 2)

        rows.append(
            {
                "quality_event_id": f"QE_{i + 1:06d}",
                "work_item_id": item["work_item_id"],
                "contributor_id": item["contributor_id"],
                "reviewer_id": f"REV_{random.randint(1, 30):04d}",
                "quality_score": score,
                "gold_task_pass": bool(gold_task_pass),
                "reviewer_override": bool(reviewer_override),
                "peer_agreement_score": peer_agreement,
            }
        )

    return pd.DataFrame(rows)


def _pattern_severity(progress: float) -> str:
    """Severity escalates as a recurring pattern progresses week over week."""
    if progress < 0.34:
        return str(np.random.choice(["sev4", "sev3"], p=[0.55, 0.45]))
    if progress < 0.67:
        return str(np.random.choice(["sev3", "sev2"], p=[0.60, 0.40]))
    return str(np.random.choice(["sev2", "sev1"], p=[0.60, 0.40]))


def _pattern_escalation_rows(teams: pd.DataFrame, end_date: datetime) -> list[dict]:
    rows = []

    for pattern in RECURRING_ESCALATION_PATTERNS:
        work_type = pattern["work_type"]
        teams_for_type = teams[teams["work_type"] == work_type]["team_id"].tolist()
        weekly_counts = pattern["weekly_counts"]
        n_weeks = len(weekly_counts)

        for week_idx, count in enumerate(weekly_counts):
            week_start = end_date - timedelta(days=7 * (n_weeks - week_idx))
            progress = week_idx / max(n_weeks - 1, 1)
            is_recent_week = week_idx >= n_weeks - 2

            for _ in range(count):
                date = (week_start + timedelta(days=random.randint(0, 6))).date()
                severity = _pattern_severity(progress)

                if is_recent_week:
                    status = np.random.choice(["open", "in_progress", "resolved"], p=[0.30, 0.30, 0.40])
                else:
                    status = np.random.choice(["open", "in_progress", "resolved"], p=[0.08, 0.12, 0.80])
                days_to_resolve = None if status != "resolved" else int(np.random.gamma(2.2, 2.0) + 1)

                rows.append(
                    {
                        "date": date,
                        "work_type": work_type,
                        "team_id": random.choice(teams_for_type),
                        "severity": severity,
                        "customer_segment": np.random.choice(
                            CUSTOMER_SEGMENTS,
                            p=[0.10, 0.24, 0.38, 0.28],
                        ),
                        "escalation_summary": random.choice(pattern["summaries"]),
                        "root_cause_category": pattern["root_cause"],
                        "status": status,
                        "days_to_resolve": days_to_resolve,
                    }
                )

    return rows


def generate_escalation_events(
    teams: pd.DataFrame,
    work_items: pd.DataFrame,
    n_events: int = 250,
) -> pd.DataFrame:
    # Anchor to the work-item timeline so escalations stay aligned with the
    # other CSVs even when only escalation_events.csv is regenerated.
    end_date = (
        pd.to_datetime(work_items["date_created"])
        .max()
        .to_pydatetime()
        .replace(microsecond=0, second=0, minute=0)
    )
    start_date = end_date - timedelta(days=90)

    rows = _pattern_escalation_rows(teams, end_date)
    n_background = max(0, n_events - len(rows))

    for i in range(1, n_background + 1):
        work_type = np.random.choice(
            WORK_TYPES,
            p=[0.18, 0.28, 0.20, 0.16, 0.18],
        )
        teams_for_type = teams[teams["work_type"] == work_type]["team_id"].tolist()
        team_id = random.choice(teams_for_type)

        date = random_datetime_between(start_date, end_date).date()

        if work_type == "expert_review":
            severity = np.random.choice(["sev1", "sev2", "sev3", "sev4"], p=[0.12, 0.34, 0.38, 0.16])
            root_cause = np.random.choice(
                ["customer_requirement_change", "policy_ambiguity", "sla_miss"],
                p=[0.50, 0.25, 0.25],
            )
        elif work_type == "rlhf_evaluation":
            severity = np.random.choice(["sev1", "sev2", "sev3", "sev4"], p=[0.04, 0.20, 0.48, 0.28])
            root_cause = np.random.choice(
                ["policy_ambiguity", "reviewer_misalignment", "capacity_shortfall"],
                p=[0.50, 0.25, 0.25],
            )
        elif work_type == "code_review":
            severity = np.random.choice(["sev1", "sev2", "sev3", "sev4"], p=[0.03, 0.18, 0.50, 0.29])
            root_cause = np.random.choice(
                ["quality_defect", "reviewer_misalignment", "workflow_handoff_gap"],
                p=[0.45, 0.40, 0.15],
            )
        else:
            severity = np.random.choice(["sev1", "sev2", "sev3", "sev4"], p=[0.02, 0.12, 0.46, 0.40])
            root_cause = random.choice(ROOT_CAUSES)

        status = np.random.choice(["open", "in_progress", "resolved"], p=[0.15, 0.20, 0.65])
        days_to_resolve = None if status != "resolved" else int(np.random.gamma(2.2, 2.0) + 1)

        rows.append(
            {
                "date": date,
                "work_type": work_type,
                "team_id": team_id,
                "severity": severity,
                "customer_segment": np.random.choice(
                    CUSTOMER_SEGMENTS,
                    p=[0.10, 0.24, 0.38, 0.28],
                ),
                "escalation_summary": f"{work_type.replace('_', ' ').title()} escalation linked to {root_cause.replace('_', ' ')}.",
                "root_cause_category": root_cause,
                "status": status,
                "days_to_resolve": days_to_resolve,
            }
        )

    events = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    events.insert(0, "escalation_id", [f"ESC_{i:06d}" for i in range(1, len(events) + 1)])
    return events


def generate_csat_events(
    teams: pd.DataFrame,
    n_events: int = 650,
) -> pd.DataFrame:
    rows = []
    end_date = datetime.now().replace(microsecond=0, second=0, minute=0)
    start_date = end_date - timedelta(days=90)

    for i in range(1, n_events + 1):
        work_type = np.random.choice(
            WORK_TYPES,
            p=[0.25, 0.25, 0.18, 0.17, 0.15],
        )
        team_id = random.choice(teams[teams["work_type"] == work_type]["team_id"].tolist())
        date = random_datetime_between(start_date, end_date).date()

        profile = adjusted_profile(work_type, datetime.combine(date, datetime.min.time()), end_date)

        score = np.random.normal(profile["base_csat"], 0.22)
        score = round(float(np.clip(score, 2.8, 5.0)), 1)

        if score < 4.2:
            feedback_theme = np.random.choice(
                ["timeliness", "calibration", "accuracy", "communication"],
                p=[0.35, 0.30, 0.20, 0.15],
            )
        else:
            feedback_theme = random.choice(FEEDBACK_THEMES)

        rows.append(
            {
                "csat_id": f"CSAT_{i:06d}",
                "date": date,
                "work_type": work_type,
                "team_id": team_id,
                "customer_segment": np.random.choice(
                    CUSTOMER_SEGMENTS,
                    p=[0.15, 0.28, 0.36, 0.21],
                ),
                "csat_score": score,
                "feedback_theme": feedback_theme,
            }
        )

    return pd.DataFrame(rows)


def save_csv(df: pd.DataFrame, filename: str) -> None:
    path = DATA_DIR / filename
    df.to_csv(path, index=False)
    print(f"Saved {filename}: {len(df):,} rows")


def main() -> None:
    ensure_data_dir()

    print("Generating synthetic Scale Regional Ops data...")

    teams = generate_teams()
    contributors = generate_contributors(teams)
    work_items = generate_work_items(teams, contributors)
    sla_events = generate_sla_events(work_items)
    quality_events = generate_quality_events(work_items)
    escalation_events = generate_escalation_events(teams, work_items)
    csat_events = generate_csat_events(teams)

    save_csv(teams, "teams.csv")
    save_csv(contributors, "contributors.csv")
    save_csv(work_items, "work_items.csv")
    save_csv(sla_events, "sla_events.csv")
    save_csv(quality_events, "quality_events.csv")
    save_csv(escalation_events, "escalation_events.csv")
    save_csv(csat_events, "csat_events.csv")

    print("\nPhase 2 complete.")
    print(f"Data directory: {DATA_DIR}")


def regenerate_escalations_only() -> None:
    """Rebuild escalation_events.csv from the existing teams and work items
    without touching any other CSV."""
    teams = pd.read_csv(DATA_DIR / "teams.csv")
    work_items = pd.read_csv(DATA_DIR / "work_items.csv")
    escalation_events = generate_escalation_events(teams, work_items)
    save_csv(escalation_events, "escalation_events.csv")


if __name__ == "__main__":
    import sys

    if "--escalations-only" in sys.argv:
        regenerate_escalations_only()
    else:
        main()
