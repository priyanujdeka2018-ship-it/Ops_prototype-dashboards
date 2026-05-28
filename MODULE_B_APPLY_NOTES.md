# Module B Patch Apply Notes

GitHub write access was blocked by the connector, so these files are packaged for manual apply.

Copy these files into the repo root, replacing existing files where names match:

- `app.py`
- `README.md`
- `docs/INTERVIEW_DEMO_SCRIPT.md`
- `docs/FINAL_CHECKLIST.md`

Add these new files:

- `src/escalation_patterns.py`
- `src/escalation_briefing.py`
- `docs/MODULE_B_HANDOFF.md`

Then validate:

```bash
python -m py_compile app.py src/*.py
python -m streamlit run app.py
```

Module B uses the existing `data/escalation_events.csv` schema and does not require paid APIs or new dependencies.
