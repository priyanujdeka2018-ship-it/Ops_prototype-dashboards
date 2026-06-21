"""
Pipeline orchestrator: generate CSVs and build the frontend JSON for one or
all scenarios, then print a manifest and validate every emitted file.

Usage:
    python -m src.pipeline --all-scenarios
    python -m src.pipeline --scenario crisis
"""

from __future__ import annotations

import json
import random
import shutil
import sys
from pathlib import Path

import numpy as np

from src import build_frontend_data, generate_data

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "web" / "public" / "data"

SCENARIOS = ("healthy", "current", "crisis")

# Top-level keys every emitted JSON payload must contain.
REQUIRED_KEYS = (
    "generated_at",
    "scenario",
    "pipeline_version",
    "row_counts",
    "refDate",
    "region",
    "kpis",
    "kpiTrends",
    "totals",
    "weeklyTrend",
    "patterns",
    "teams",
    "workTypeRollup",
    "escalations",
    "workforce",
    "capacity",
    "leadership",
)


def run_scenario(scenario: str) -> dict:
    """Generate CSVs and build JSON for one scenario, returning its payload.

    The RNG is re-seeded per scenario so each scenario is independently
    reproducible regardless of how many scenarios run in the same process.
    """
    np.random.seed(generate_data.RANDOM_SEED)
    random.seed(generate_data.RANDOM_SEED)

    print(f"\n=== Scenario: {scenario} ===")
    generate_data.main(scenario=scenario)
    return build_frontend_data.main(scenario=scenario)


def validate_file(scenario: str) -> tuple[bool, str]:
    """Validate the JSON written for a scenario. Returns (ok, detail)."""
    path = OUTPUT_DIR / f"data-{scenario}.json"
    if not path.exists():
        return False, "file missing"
    try:
        payload = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        return False, f"invalid JSON: {exc}"

    missing = [k for k in REQUIRED_KEYS if k not in payload]
    if missing:
        return False, f"missing keys: {', '.join(missing)}"

    escalation_count = int(payload["totals"].get("escalations", 0))
    pattern_count = len(payload.get("patterns", []))
    if escalation_count <= 0:
        return False, "escalation count is 0"
    if pattern_count <= 0:
        return False, "pattern count is 0"

    return True, f"{escalation_count} escalations, {pattern_count} patterns"


def print_manifest(payloads: dict[str, dict]) -> None:
    headers = ["Scenario", "Escalations", "Patterns", "Teams", "Generated At"]
    rows = [
        [
            scenario,
            str(p["totals"]["escalations"]),
            str(len(p["patterns"])),
            str(p["totals"]["teams"]),
            p["generated_at"],
        ]
        for scenario, p in payloads.items()
    ]
    widths = [max(len(headers[i]), *(len(r[i]) for r in rows)) for i in range(len(headers))]

    def fmt(cells: list[str]) -> str:
        return " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(cells))

    print("\nManifest")
    print(fmt(headers))
    print("-+-".join("-" * w for w in widths))
    for row in rows:
        print(fmt(row))


def print_validation() -> bool:
    print("\nValidation")
    all_ok = True
    for scenario in SCENARIOS:
        if not (OUTPUT_DIR / f"data-{scenario}.json").exists():
            continue
        ok, detail = validate_file(scenario)
        all_ok = all_ok and ok
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] data-{scenario}.json — {detail}")
    return all_ok


def _parse_args(argv: list[str]) -> tuple[list[str], bool]:
    all_scenarios = "--all-scenarios" in argv
    scenario = build_frontend_data._parse_scenario(argv)
    scenarios = list(SCENARIOS) if all_scenarios else [scenario]
    return scenarios, all_scenarios


def main(scenarios: list[str] | None = None) -> bool:
    if scenarios is None:
        scenarios = ["current"]
    for scenario in scenarios:
        if scenario not in SCENARIOS:
            raise ValueError(f"Unknown scenario '{scenario}'. Valid: {', '.join(SCENARIOS)}")

    payloads = {scenario: run_scenario(scenario) for scenario in scenarios}

    # Leave data.json (the default fetch target) on the neutral "current"
    # baseline when it was built, rather than whichever scenario ran last.
    if "current" in scenarios:
        shutil.copyfile(OUTPUT_DIR / "data-current.json", OUTPUT_DIR / "data.json")

    print_manifest(payloads)
    ok = print_validation()
    print("\nPipeline complete." if ok else "\nPipeline finished with validation FAILURES.")
    return ok


if __name__ == "__main__":
    selected, _ = _parse_args(sys.argv)
    success = main(selected)
    sys.exit(0 if success else 1)
