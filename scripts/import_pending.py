"""
Merge any data/pending_updates_*.csv files into data/master_timeline.csv,
deduplicate by (date, location, event), lightly normalize fields, sort,
and archive the processed pending files.

Safe to re-run; no side effects if no pending files exist.
"""

from __future__ import annotations
import csv
import pathlib
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ARCHIVE = DATA / "archive"
MASTER = DATA / "master_timeline.csv"

REQUIRED_HEADERS = [
    "date","location","event","participants_on_record","source_urls","notes"
]

def read_csv(path: pathlib.Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write_csv(path: pathlib.Path, rows: list[dict], headers: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        for r in rows:
            w.writerow(r)

def load_master() -> list[dict]:
    if not MASTER.exists():
        # create an empty master with headers
        write_csv(MASTER, [], REQUIRED_HEADERS)
        return []
    rows = read_csv(MASTER)
    # If headers missing, raise loudly
    if rows and any(h not in rows[0].keys() for h in REQUIRED_HEADERS):
        raise SystemExit("master_timeline.csv missing required headers")
    return rows

def normalize_row(r: dict) -> dict:
    """Trim whitespace and normalize basic fields; keep data as-is otherwise."""
    out = {}
    for k in REQUIRED_HEADERS:
        v = (r.get(k, "") or "").strip()
        # collapse internal whitespace in some fields
        if k in ("location","event"):
            v = " ".join(v.split())
        out[k] = v
    return out

def compose_key(r: dict) -> tuple:
    # Key used for deduping. We deliberately ignore notes/sources differences.
    return (r.get("date","").strip(), r.get("location","").strip(), r.get("event","").strip())

def parse_date_key(d: str) -> tuple:
    """
    Return a sortable key for 'date' that tolerates:
      - YYYY-MM-DD
      - YYYY-MM
      - YYYY
      - ranges like '2019-07-20–2019-08-20' (use start)
    Non-parsable values sort last, preserving original string for stability.
    """
    if "–" in d:
        d = d.split("–", 1)[0].strip()

    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            dt = datetime.strptime(d, fmt)
            return (0, dt.year, dt.month if fmt != "%Y" else 1, dt.day if fmt == "%Y-%m-%d" else 1, d)
        except ValueError:
            continue
    return (1, 9999, 12, 31, d or "~")

def merge_rows(master: list[dict], pendings: list[list[dict]]) -> list[dict]:
    merged = []
    seen = set()
    # seed with master
    for r in master:
        nr = normalize_row(r)
        k = compose_key(nr)
        if k not in seen:
            merged.append(nr); seen.add(k)

    # add pendings
    for chunk in pendings:
        # basic header check
        if not chunk:
            continue
        if any(h not in chunk[0].keys() for h in REQUIRED_HEADERS):
            raise SystemExit("A pending_updates file is missing required headers")
        for r in chunk:
            nr = normalize_row(r)
            k = compose_key(nr)
            if k not in seen:
                merged.append(nr); seen.add(k)

    # sort by parsed date, then location, then event
    merged.sort(key=lambda r: (parse_date_key(r["date"]), r["location"].lower(), r["event"].lower()))
    return merged

def main():
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    master_rows = load_master()

    pending_paths = sorted(DATA.glob("pending_updates_*.csv"))
    if not pending_paths:
        print("No pending update files found; nothing to do.")
        return

    pending_batches = [ read_csv(p) for p in pending_paths ]
    new_master = merge_rows(master_rows, pending_batches)

    # Only write if changed
    if new_master != master_rows:
        write_csv(MASTER, new_master, REQUIRED_HEADERS)
        print(f"Updated {MASTER} with {len(new_master)} rows.")
    else:
        print("No changes after merge (all rows were duplicates).")

    # Archive pending files with timestamp
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    for p in pending_paths:
        archived = ARCHIVE / f"{p.stem}.processed_{ts}.csv"
        p.replace(archived)
        print(f"Archived {p.name} -> {archived.name}")

if __name__ == "__main__":
    main()
