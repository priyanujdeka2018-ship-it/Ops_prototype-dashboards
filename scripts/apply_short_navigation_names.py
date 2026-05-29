from pathlib import Path
import shutil

ROOT = Path.cwd()
PAGES = ROOT / "pages"

RENAMES = {
    "2_Module_B_v2_Semantic_Clusters.py": "20_Escalation_Themes.py",
    "3_Module_C_Workforce_Quality_Scorer.py": "30_Quality_Risk.py",
    "4_Module_D_Capacity_SLA_Forecasting.py": "40_Capacity_SLA.py",
}

APP_REPLACEMENTS = {
    "Module A: Regional Operations Health Dashboard": "Operations Health",
    "Module B: Escalation Pattern Recurrence Detector": "Escalation Recurrence",
    "Module A shows where regional health is degrading. Module B checks whether escalations are isolated incidents or repeat operating-system failures.": (
        "Operations Health shows where regional health is degrading. Escalation Recurrence checks whether escalations are isolated incidents or repeat operating-system failures."
    ),
    "No escalation events available for the selected Module A scope.": "No escalation events available for the selected health scope.",
    "No escalation events match the Module B filters.": "No escalation events match the selected filters.",
    '"Module A work type filter"': '"health work type filter"',
    '"Module B pattern grain"': '"escalation pattern grain"',
}

PAGE_REPLACEMENTS = {
    "Module B v2 - Semantic Escalation Clusters": "Escalation Themes",
    "Module B v2: Semantic Escalation Pattern Recurrence Detector": "Escalation Themes",
    "This page extends Module B from deterministic pattern keys to semantic clustering.": (
        "This view extends deterministic escalation recurrence into semantic clustering."
    ),
    "Module C - Workforce Quality Scorer": "Quality Risk",
    "Module C: Distributed Workforce Quality Scorer": "Quality Risk",
    "Module D - Capacity SLA Forecasting": "Capacity & SLA",
    "Module D: Capacity, Staffing, and SLA Forecasting": "Capacity & SLA",
    "Module D filters": "Capacity filters",
    "Module D Weekly Capacity Briefing": "Weekly Capacity Briefing",
    "Download Module D Weekly Capacity Briefing": "Download Weekly Capacity Briefing",
    "Module D extends the command center": "Capacity & SLA extends the command center",
    "Module D shows whether": "Capacity & SLA shows whether",
    "Module A shows where": "Operations Health shows where",
    "Module B shows whether": "Escalation Recurrence shows whether",
    "Module C shows whether": "Quality Risk shows whether",
}

def replace_text(path: Path, replacements: dict[str, str]) -> None:
    if not path.exists():
        return
    text = path.read_text()
    original = text
    for old, new in replacements.items():
        text = text.replace(old, new)
    if text != original:
        path.write_text(text)

# 1) Clean visible names in app.py
replace_text(ROOT / "app.py", APP_REPLACEMENTS)

# 2) Clean visible names in all page files
if PAGES.exists():
    for page in PAGES.glob("*.py"):
        replace_text(page, PAGE_REPLACEMENTS)

# 3) Rename page files so Streamlit sidebar labels are short.
# Streamlit hides numeric prefixes, so 20_Escalation_Themes.py appears as "Escalation Themes".
for old_name, new_name in RENAMES.items():
    old_path = PAGES / old_name
    new_path = PAGES / new_name

    if old_path.exists():
        if new_path.exists():
            old_path.unlink()
        else:
            shutil.move(str(old_path), str(new_path))

# 4) If the newer Capacity page already exists, clean it too
replace_text(PAGES / "40_Capacity_SLA.py", PAGE_REPLACEMENTS)

print("Short navigation names applied.")
print("Expected sidebar labels:")
print("- Escalation Themes")
print("- Quality Risk")
print("- Capacity SLA")
print("")
print("Main app visible sections:")
print("- Operations Health")
print("- Escalation Recurrence")
