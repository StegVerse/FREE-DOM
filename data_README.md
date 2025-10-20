# Data Folder Overview

This directory houses all factual data, pending leads, and AI-agent results for the FREE-DOM project.

## Structure

| Subfolder | Contents | Description |
|------------|-----------|--------------|
| `master/` | `master_timeline.csv`, `verified_people_events.csv` | Canonical, validated datasets used in all outputs |
| `pending/` | `events/`, `people/`, `unverified/` | New incoming data awaiting validation or AI search enrichment |
| `unverified/` | CSVs of events, people, or connections lacking confirmation | Used to track uncertain data |
| `sources/` | `sources_whitelist.csv` | List of approved RSS/news feeds monitored by the AI agent |
| `logs/ai_agent/` | `agent_run_*.jsonl` | Machine logs from each public-source scan |
| `summary/` | `ai_agent_summary.csv`, `ai_agent_sources_index.csv` | Summaries of sources, hits, and coverage metrics |
| `archive/` | Archived imports after merge | Permanent, timestamped records of older batches |

## How It Works

1. You or the AI add **pending CSVs** in the relevant subfolder.  
2. The **Auto Update workflow** merges them into `data/master/`.  
3. The **AI Search Agent** sweeps all public sources to verify leads.  
4. Verified leads move from `unverified/` → `master/`.  
5. Everything else remains in the pipeline until confirmed.

---
