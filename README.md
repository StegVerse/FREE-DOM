[![AI Search Agent](https://github.com/StegVerse/FREE-DOM/actions/workflows/ai_search_agent.yml/badge.svg?branch=main)](https://github.com/StegVerse/FREE-DOM/actions/workflows/ai_search_agent.yml?query=branch%3Amain)
# FREE-DOM
[![Changelog Build](https://github.com/StegVerse/FREE-DOM/actions/workflows/auto_update.yml/badge.svg)](https://github.com/StegVerse/FREE-DOM/actions/workflows/auto_update.yml)

**FREE-DOM: Factually Recounting Epstein’s Era — Deconstruction of Morality**

A public, evidence-first research repo designed for fiction authors: verified timelines of events, photo/video anchors, court dockets, and character-safe scene prompts.  
- 📜 **[CHANGELOG](./CHANGELOG.md)** – auto-built progress and coverage  
- ✅ **[CHECKLIST](./CHECKLIST.md)** – pending IDs, deep searches, unverified leads  
- 📂 **[`data/`](./data/)** – CSVs: `master_timeline.csv`, `verified_people_events.csv`, unverified lead tables, and pending batches
- 
https://github.com/StegVerse/FREE-DOM

**FREE-DOM** is an open-source factual archive reconstructing the verified
timeline, documents, and organizational ecosystem of the Epstein era (1990–2025).

Each dataset is compiled exclusively from verifiable public records:
- Court filings and unsealed SDNY documents  
- U.S. congressional releases and hearings  
- Verified nonprofit filings and corporate registrations  
- Photo/video evidence published by recognized outlets  

## Data Changelog
See the running data history in **[CHANGELOG.md](./CHANGELOG.md)** and the detailed CSV index **[`data/CHANGELOG_batches.csv`](./data/CHANGELOG_batches.csv)**.

No speculation or unverified claims appear in this repository.
The purpose is documentation and analysis of systemic moral collapse
across legal, political, and cultural institutions.

## Contributing
- Add only events with **clear public documentation**.
- Include at least one **source URL** per row (prefer primary sources).
- Keep descriptions neutral and factual.

## Automated Public-Source Sweep (AI Search Agent)
The AI Search Agent runs daily to find **public, reputable-source leads** for items marked `deep_search_*: pending`.  
- 🕒 Schedule: daily 10:30 UTC (and on demand)  
- 🗂️ Output: appends URL leads to:
  - `data/master_timeline.csv` → **notes**
  - `data/verified_people_events.csv` → **deep_search_notes**
- 📜 Logs: `data/ai_agent_logs/` (JSONL per run)
- 🔒 Scope: **whitelisted public sources only** (see `data/sources_whitelist.csv`) — no private networks or dark web.

## License
MIT
