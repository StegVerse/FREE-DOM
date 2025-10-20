# FREE-DOM: Factually Recounting Epstein’s Era — Deconstruction of Morality

A public, evidence-first research repository designed to support fiction authors and investigative journalists by maintaining **structured, factual timelines** of publicly verifiable events, court dockets, and related data.

---

## 🧩 Workflow Status

| Workflow | Status | Description |
|-----------|---------|--------------|
| **AI Search Agent** | [![AI Search Agent](https://github.com/StegVerse/FREE-DOM/actions/workflows/ai_search_agent.yml/badge.svg)](https://github.com/StegVerse/FREE-DOM/actions/workflows/ai_search_agent.yml) | Runs daily OSINT sweeps from whitelisted sources and updates leads + summaries. |
| **Auto Update** | [![Auto Update](https://github.com/StegVerse/FREE-DOM/actions/workflows/auto_update.yml/badge.svg)](https://github.com/StegVerse/FREE-DOM/actions/workflows/auto_update.yml) | Merges pending datasets into master, rebuilds checklist/changelog, and validates schema. |

---

## 📂 Repository Layout

data/
master/              ← Canonical verified datasets
pending/             ← New or partially verified submissions
unverified/          ← Leads and unconfirmed information
sources/             ← RSS/news feeds monitored by the AI Search Agent
logs/ai_agent/       ← Raw JSONL logs of agent sweeps
summary/             ← Aggregated hit summaries and source indexes
archive/             ← Processed import snapshots for audit
scripts/               ← Automation scripts and utilities
.github/workflows/     ← CI/CD for ingestion and validation

---

## ⚙️ Workflows Overview

- **AI Search Agent** – performs daily public-source sweeps (RSS/news only) and appends leads to records.  
- **Auto Update** – merges pending data into master, updates CHECKLIST.md and CHANGELOG.md, and validates schema.  
- **Validation Layer** – ensures CSV consistency and master integrity.

---

## 🧠 Purpose

FREE-DOM exists to preserve factual record-keeping while empowering creative, educational, and investigative work **without directly naming real individuals** in narrative form.  
It keeps transparency high, maintains auditability, and prevents misinformation.

---

## 📊 Repository Architecture

![FREE-DOM Repo Diagram](docs/FREE_DOM_repo_diagram.png)

<details>
<summary>ASCII Diagram</summary>

```txt
(see docs/FREE_DOM_repo_diagram.txt for full ASCII)

</details>

<details>
<summary>ASCII Version</summary>
(see docs/FREE_DOM_devops_pipeline.txt for full ASCII)
</details>

🧩 Data Folder Reference
Folder
Purpose
Managed By
data/master/
Verified datasets
Auto Update
data/pending/
New entries awaiting merge
Human + Auto Update
data/unverified/
Leads needing confirmation
Auto Update
data/sources/
RSS/news feeds
Manual
data/logs/ai_agent/
Raw agent logs
AI Search Agent
data/summary/
Aggregated dashboards & VERSION
AI Search Agent / Auto Update
data/archive/
Processed batch history

🧮 Scripts
	•	scripts/search_agent.py — performs OSINT sweeps and lead enrichment.
	•	scripts/build_ai_agent_summary.py — builds hit summaries & source indexes.
	•	scripts/import_pending.py — merges pending data into master datasets.
	•	scripts/build_checklist.py — generates verification checklist.
	•	scripts/build_changelog.py — semantic versioning + changelog and snapshots.
	•	scripts/update_timeline.py — validates dataset integrity.

🧱 Contributing

Please read the CONTRIBUTING.md file before submitting updates.
All contributions should respect:
	•	factual accuracy (publicly verifiable sources only),
	•	anonymity and non-implication of real individuals,
	•	reproducibility and version traceability.

⸻

📊 Repository Live Status
Metric
Source
Current Value
Version
data/summary/VERSION
auto-updated by CI
Data Freshness (AI Search Agent)
data/summary/ai_agent_summary.csv
auto-updated
Workflow Sync (Auto Update)
GitHub Actions
🟢 Passing
Files Verified
CHECKLIST.md
auto-count
New Leads Pending Review
data/unverified/
auto-count

Last sync performed automatically via scheduled GitHub Action.

⸻

© FREE-DOM Project — a StegVerse initiative for truth, structure, and awareness.

