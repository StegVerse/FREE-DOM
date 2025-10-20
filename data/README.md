# FREE-DOM: Factually Recounting Epstein’s Era — Deconstruction of Morality

This repository maintains structured, factual event data for the FREE-DOM project.

## Repository Layout

data/
master/              ← Canonical datasets (fully verified)
pending/             ← New or partially verified submissions
unverified/          ← Leads or unconfirmed info
sources/             ← RSS/news sources the AI agent monitors
logs/ai_agent/       ← Raw JSONL logs from the AI Search Agent
summary/             ← Automatically generated dashboards
archive/             ← Processed imports (historical snapshots)

## Workflows
- **AI Search Agent** – gathers public-source leads daily, logs results, and builds summary dashboards.
- **Auto Update** – merges pending data into master, regenerates CHECKLIST.md & CHANGELOG.md, and validates CSVs.

## Scripts
- `scripts/search_agent.py` – public-source sweep (RSS/news only)
- `scripts/build_ai_agent_summary.py` – builds dashboards
- `scripts/import_pending.py` – merges new CSVs
- `scripts/build_checklist.py` – generates verification checklist
- `scripts/build_changelog.py` – records historical changes
- `scripts/update_timeline.py` – validates master timeline

All scripts are idempotent and can run safely multiple times.

---
