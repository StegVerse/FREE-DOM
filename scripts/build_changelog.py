#!/usr/bin/env python3
"""
Rebuilds CHANGELOG.md and data/CHANGELOG_batches.csv from known batch files.
Looks only at files present in the repo (no network).
"""

from __future__ import annotations
import csv, pathlib
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT_CSV = DATA / "CHANGELOG_batches.csv"
OUT_MD  = ROOT / "CHANGELOG.md"

# Append any new pending_* files you introduce later.
BATCH_META = [
    # people
    ("pending_people_01.csv", "people", "—", "—"),
    ("pending_people_02.csv", "people", "—", "—"),
    ("pending_people_03.csv", "people", "—", "—"),
    ("pending_people_04.csv", "people", "—", "—"),
    # events
    ("pending_updates_07.csv", "events", "2025-09-19", "2025-10-18"),
    ("pending_updates_08.csv", "events", "2019-07-07", "2025-10-17"),
    ("pending_updates_09.csv", "events", "2023-12-18", "2024-01-08"),
    ("pending_updates_10.csv", "events", "2024-01-03", "2024-01-03"),
    ("pending_updates_11.csv", "events", "2024-01", "2024-01"),
    ("pending_updates_12.csv", "events", "2024-01", "2024-01"),
    ("pending_updates_13.csv", "events", "2024-01", "2024-01"),
    ("pending_updates_14.csv", "events", "2024-01", "2024-01"),
    ("pending_updates_15.csv", "events", "2024-01", "2024-01"),
    ("pending_updates_16.csv", "events", "2024-01", "2024-01"),
    ("pending_updates_17.csv", "events", "2024-01", "2024-01"),
    ("pending_updates_18.csv", "events", "2024-01", "2024-01"),
    ("pending_updates_19.csv", "events", "2024-01", "2024-01"),
    ("pending_updates_20.csv", "events", "2024-01", "2024-01"),
    ("pending_updates_21.csv", "events", "2024-01", "2024-01"),
]

def count_rows(path: pathlib.Path) -> int:
    if not path.exists():
        return 0
    try:
        with path.open(encoding="utf-8") as f:
            return max(0, sum(1 for _ in f) - 1)  # minus header
    except Exception:
        return 0

def main():
    DATA.mkdir(parents=True, exist_ok=True)

    rows = []
    cumulative_event_rows = 0
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    for fname, category, start, end in BATCH_META:
        p = DATA / fname
        n = count_rows(p)
        if category == "events":
            cumulative_event_rows += n
        rows.append([now, fname, category, start, end, n,
                     cumulative_event_rows if category == "events" else ""])

    # CSV
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["timestamp_utc","batch_file","category","range_start","range_end","entries_in_batch","cumulative_event_entries"])
        w.writerows(rows)

    # Markdown
    total_people = sum(int(r[5]) for r in rows if r[2] == "people")
    total_events = sum(int(r[5]) for r in rows if r[2] == "events")

    md = []
    md.append("# FREE-DOM • Data Batches Changelog\n")
    md.append(f"[![Changelog Build](https://github.com/StegVerse/FREE-DOM/actions/workflows/auto_update.yml/badge.svg)](https://github.com/StegVerse/FREE-DOM/actions/workflows/auto_update.yml)\n")
    md.append(f"_Auto-generated: {now} (UTC)_\n")
    md.append("\n## Summary\n")
    md.append(f"- **People batches:** {total_people} rows\n")
    md.append(f"- **Event batches:** {total_events} rows\n")
    md.append("\n## Batches\n")
    md.append("| Batch | Category | Coverage | Entries | Cumulative (events) |")
    md.append("|---|---|---|---:|---:|")
    for ts, name, cat, start, end, n, cum in rows:
        coverage = start if (end == "—" or not end or end == start) else f"{start} → {end}"
        md.append(f"| `{name}` | {cat} | {coverage or '—'} | {n} | {cum if cat=='events' else ''} |")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_CSV} and {OUT_MD}")

if __name__ == "__main__":
    main()
