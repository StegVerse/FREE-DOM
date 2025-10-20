# Contributing to FREE-DOM

Thank you for contributing to FREE-DOM.

## File Placement Rules

| Folder | Purpose | Notes |
|--------|----------|-------|
| `data/master/` | Canonical verified datasets | Updated by workflows only |
| `data/pending/events/` | New event rows awaiting verification | Use `pending_updates_template.csv` |
| `data/pending/people/` | New person/event associations | Use `pending_people_template.csv` |
| `data/pending/unverified/` | Leads not yet confirmed | Use `pending_unverified_template.csv` |
| `data/unverified/` | Consolidated unverified datasets | Auto-managed |
| `data/sources/` | Whitelisted RSS/news sources | Maintained manually |
| `data/logs/ai_agent/` | Agent run logs | Generated automatically |
| `data/summary/` | Summary dashboards | Auto-generated |
| `data/archive/` | Processed imports for audit | Created automatically |

## Adding New Data

1. Duplicate the appropriate template in `data/pending/…`.
2. Fill rows carefully (dates in `YYYY-MM-DD` format).
3. Commit directly to `main`.
4. The **Auto Update** workflow will merge and archive.
5. The **AI Search Agent** will run daily to enrich leads.

## Manual Runs

To trigger jobs manually:
- **Run “AI Search Agent”** → performs RSS sweep & updates summaries.
- **Run “Auto Update”** → merges pending data & regenerates checklist/changelog.

Each workflow commits only when file changes are detected.
