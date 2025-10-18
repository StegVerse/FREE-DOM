from __future__ import annotations
import csv
import pathlib
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ARCHIVE = DATA / "archive"

MASTER = DATA / "master_timeline.csv"
PEOPLE = DATA / "verified_people_events.csv"

REQ_MASTER = ["date","location","event","participants_on_record","source_urls","notes"]
OPT_MASTER = ["deep_search_event","deep_search_notes"]  # new
ALL_MASTER = REQ_MASTER + OPT_MASTER

REQ_PEOPLE = ["date","location","event","person","role","source_urls","deep_search_person","deep_search_notes"]

def read_csv(path: pathlib.Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write_csv(path: pathlib.Path, rows: list[dict], headers: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        for r in rows:
            w.writerow({h: r.get(h,"") for h in headers})

def ensure_file(path: pathlib.Path, headers: list[str]) -> None:
    if not path.exists():
        write_csv(path, [], headers)

def normalize_master_row(r: dict) -> dict:
    out = {}
    for k in ALL_MASTER:
        v = (r.get(k,"") or "").strip()
        if k in ("location","event"):
            v = " ".join(v.split())
        out[k] = v
    # default deep search state if missing
    if not out.get("deep_search_event"):
        out["deep_search_event"] = "pending"
    return out

def key_master(r: dict) -> tuple:
    return (r.get("date","").strip(), r.get("location","").strip(), r.get("event","").strip())

def parse_date_key(d: str) -> tuple:
    if "–" in d:
        d = d.split("–",1)[0].strip()
    for fmt in ("%Y-%m-%d","%Y-%m","%Y"):
        try:
            dt = datetime.strptime(d, fmt)
            return (0, dt.year, dt.month if fmt != "%Y" else 1, dt.day if fmt == "%Y-%m-%d" else 1, d)
        except ValueError:
            pass
    return (1, 9999, 12, 31, d or "~")

def merge_master():
    ensure_file(MASTER, ALL_MASTER)
    master_rows = read_csv(MASTER)
    merged, seen = [], set()
    for r in master_rows:
        # Backfill new columns for legacy rows
        for k in OPT_MASTER:
            r.setdefault(k, "")
        nr = normalize_master_row(r)
        k = key_master(nr)
        if k not in seen:
            merged.append(nr); seen.add(k)

    for p in sorted(DATA.glob("pending_updates_*.csv")):
        chunk = read_csv(p)
        if not chunk: continue
        # Fill missing new columns
        for r in chunk:
            for k in OPT_MASTER:
                r.setdefault(k, "")
            nr = normalize_master_row(r)
            k = key_master(nr)
            if k not in seen:
                merged.append(nr); seen.add(k)

    merged.sort(key=lambda r: (parse_date_key(r["date"]), r["location"].lower(), r["event"].lower()))
    write_csv(MASTER, merged, ALL_MASTER)

    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    for p in sorted(DATA.glob("pending_updates_*.csv")):
        (ARCHIVE / f"{p.stem}.processed_{ts}.csv").parent.mkdir(parents=True, exist_ok=True)
        p.replace(ARCHIVE / f"{p.stem}.processed_{ts}.csv")

def key_people(r: dict) -> tuple:
    return (r.get("date","").strip(), r.get("location","").strip(), r.get("event","").strip(), r.get("person","").strip())

def normalize_people_row(r: dict) -> dict:
    out = {}
    for k in REQ_PEOPLE:
        out[k] = (r.get(k,"") or "").strip()
    if not out.get("deep_search_person"):
        out["deep_search_person"] = "pending"
    return out

def merge_people():
    ensure_file(PEOPLE, REQ_PEOPLE)
    existing = read_csv(PEOPLE)
    merged, seen = [], set()
    for r in existing:
        nr = normalize_people_row(r)
        k = key_people(nr)
        if k not in seen:
            merged.append(nr); seen.add(k)

    for p in sorted(DATA.glob("pending_people_*.csv")):
        chunk = read_csv(p)
        if not chunk: continue
        if any(h not in chunk[0].keys() for h in REQ_PEOPLE):
            raise SystemExit(f"{p.name} missing required headers")
        for r in chunk:
            nr = normalize_people_row(r)
            k = key_people(nr)
            if k not in seen:
                merged.append(nr); seen.add(k)

    merged.sort(key=lambda r: (parse_date_key(r["date"]), r["location"].lower(), r["event"].lower(), r["person"].lower()))
    write_csv(PEOPLE, merged, REQ_PEOPLE)

    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    for p in sorted(DATA.glob("pending_people_*.csv")):
        (ARCHIVE / f"{p.stem}.processed_{ts}.csv").parent.mkdir(parents=True, exist_ok=True)
        p.replace(ARCHIVE / f"{p.stem}.processed_{ts}.csv")

def main():
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    merge_master()
    merge_people()
    print("Merged pending updates and people successfully.")

if __name__ == "__main__":
    main()
