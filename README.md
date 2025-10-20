# FREE-DOM: Factually Recounting Epstein’s Era — Deconstruction of Morality

A public, evidence-first research repository built to support fiction authors and investigative journalists by maintaining **structured, factual timelines** of publicly verifiable events, court dockets, and related materials.

## ⚙️ Workflows

- **AI Search Agent** – performs daily public OSINT sweeps (RSS, major media) and appends leads.
- **Auto Update** – merges pending rows into master datasets, updates CHECKLIST.md and CHANGELOG.md.
- **Validation** – ensures CSV consistency and proper schema alignment.

## 🧠 Purpose

FREE-DOM is designed for fiction writers seeking to base their narratives on verifiable, historically accurate data while **avoiding direct identification** of real persons in narrative form.

The system maintains transparency and verifiability without crossing ethical or legal boundaries.

## 📊 Repository Architecture

![FREE-DOM Repo Diagram](docs/FREE_DOM_repo_diagram.png)

<details>
<summary>ASCII Version (click to expand)</summary>

## 📂 Repository Layout - data/

```
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
```

---
