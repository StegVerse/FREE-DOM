# Contributing to FREE-DOM

Thank you for contributing to the FREE-DOM project.

## 🧭 File Placement Rules

| Folder | Purpose | Notes |
|--------|----------|-------|
| `data/master/` | Canonical verified datasets | Updated automatically by workflows |
| `data/pending/events/` | New event rows awaiting verification | Use `pending_updates_template.csv` |
| `data/pending/people/` | New person/event associations | Use `pending_people_template.csv` |
| `data/pending/unverified/` | Leads not yet confirmed | Use `pending_unverified_template.csv` |
| `data/unverified/` | Consolidated unverified datasets | Auto-managed |
| `data/sources/` | Whitelisted RSS/news feeds | Maintained manually |
| `data/logs/ai_agent/` | AI Search Agent logs | Auto-generated |
| `data/summary/` | Aggregated dashboards | Auto-generated |
| `data/archive/` | Processed import archives | Automatically versioned |

## 🧩 Adding New Data

1. Copy a template from `data/pending/...`.
2. Fill out rows carefully (dates as `YYYY-MM-DD`).
3. Commit directly to `main`.
4. The **Auto Update** workflow merges and archives your submission.
5. The **AI Search Agent** enriches data nightly with verified public-source links.

## 🧪 Manual Workflow Runs

- **Run “AI Search Agent”** → performs RSS sweep & builds new summary dashboards.
- **Run “Auto Update”** → merges pending CSVs, regenerates CHECKLIST.md & CHANGELOG.md.

> Each workflow commits automatically only when file changes are detected.
