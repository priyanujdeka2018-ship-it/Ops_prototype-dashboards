#!/usr/bin/env bash
set -e

echo "Repo:"
pwd

echo ""
echo "Current git state:"
git status --short

echo ""
echo "Removing temporary files..."
rm -f module_c_dropin.zip
rm -f *.zip
rm -f .DS_Store

find . -type d -name "__pycache__" -prune -exec rm -rf {} +
find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
find . -type d -name ".ipynb_checkpoints" -prune -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name ".DS_Store" -delete

echo ""
echo "Ensuring .gitignore has cleanup rules..."
touch .gitignore

add_gitignore_rule () {
  rule="$1"
  grep -qxF "$rule" .gitignore || echo "$rule" >> .gitignore
}

add_gitignore_rule "__pycache__/"
add_gitignore_rule "*.pyc"
add_gitignore_rule "*.pyo"
add_gitignore_rule ".pytest_cache/"
add_gitignore_rule ".ipynb_checkpoints/"
add_gitignore_rule ".DS_Store"
add_gitignore_rule "*.zip"
add_gitignore_rule ".env"
add_gitignore_rule ".venv/"
add_gitignore_rule "venv/"

echo ""
echo "Checking required Module A-D-ready structure..."
test -f app.py
test -f README.md
test -f requirements.txt
test -d data
test -d src
test -d pages
test -d docs

test -f src/workforce_quality.py
test -f src/quality_briefing.py
test -f pages/3_Module_C_Workforce_Quality_Scorer.py
test -f docs/MODULE_C_HANDOFF.md
test -f docs/MODULE_C_DEMO_SCRIPT.md

echo ""
echo "Python syntax validation..."
python -m py_compile app.py src/*.py pages/*.py

echo ""
echo "Final git state:"
git status --short

echo ""
echo "Cleanup complete."
