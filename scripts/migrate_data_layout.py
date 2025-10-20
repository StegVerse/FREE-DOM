#!/usr/bin/env python3
from __future__ import annotations
import shutil, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
D = ROOT / "data"

# New structure
(D / "master").mkdir(parents=True, exist_ok=True)
(D / "pending" / "events").mkdir(parents=True, exist_ok=True)
(D / "pending" / "people").mkdir(parents=True, exist_ok=True)
(D / "pending" / "unverified").mkdir(parents=True, exist_ok=True)
(D / "unverified").mkdir(parents=True, exist_ok=True)
(D / "sources").mkdir(parents=True, exist_ok=True)
(D / "logs" / "ai_agent").mkdir(parents=True, exist_ok=True)
(D / "summary").mkdir(parents=True, exist_ok=True)
(D / "archive").mkdir(parents=True, exist_ok=True)

def mv(src: pathlib.Path, dst: pathlib.Path):
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))

# Master files
mv(D / "master_timeline.csv", D / "master" / "master_timeline.csv")
mv(D / "verified_people_events.csv", D / "master" / "verified_people_events.csv")

# Pending batches (legacy names)
for p in D.glob("pending_updates_*.csv"):
    mv(p, D / "pending" / "events" / p.name)
for p in D.glob("pending_people_*.csv"):
    mv(p, D / "pending" / "people" / p.name)
for p in D.glob("pending_unverified_*.csv"):
    mv(p, D / "pending" / "unverified" / p.name)

# Unverified canonicals
mv(D / "unverified_events.csv", D / "unverified" / "unverified_events.csv")
mv(D / "unverified_people.csv", D / "unverified" / "unverified_people.csv")
mv(D / "unverified_connections.csv", D / "unverified" / "unverified_connections.csv")

# Sources + logs + summary (if present)
mv(D / "sources_whitelist.csv", D / "sources" / "sources_whitelist.csv")
for p in D.glob("ai_agent_logs/agent_run_*.jsonl"):
    mv(p, D / "logs" / "ai_agent" / p.name)
mv(D / "CHANGELOG_batches.csv", D / "summary" / "CHANGELOG_batches.csv")
mv(D / "ai_agent_summary.csv", D / "summary" / "ai_agent_summary.csv")
mv(D / "ai_agent_sources_index.csv", D / "summary" / "ai_agent_sources_index.csv")

print("Migration complete.")
