#!/usr/bin/env bash
# One-command pipeline rebuild → regenerates CSVs + writes web/public/data/.
# Usage:  ./scripts/rebuild.sh [scenario]     scenario: healthy|current|crisis (default current)
#
# Demo motion: tweak a scenario multiplier in src/generate_data.py (or append an
# escalation) → ./scripts/rebuild.sh → click "Refresh data" in the app → the whole
# board moves, identically across every module (one Python source of truth).
#
# Pre-baked vintages (the always-works switcher on the deployed URL) are built with
# the emitter's --label flag, e.g.:
#   python -m src.generate_data --scenario crisis  && python -m src.build_frontend_data --label pre-fix
#   python -m src.generate_data --scenario healthy && python -m src.build_frontend_data --label post-fix
set -euo pipefail
cd "$(dirname "$0")/.."
python -m src.pipeline --scenario "${1:-current}"
echo "Rebuilt web/public/data/ for scenario '${1:-current}'. Click 'Refresh data' in the app."
