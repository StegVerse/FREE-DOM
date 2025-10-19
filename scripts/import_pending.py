from __future__ import annotations
import csv
import pathlib
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ARCHIVE = DATA / "archive"

MASTER = DATA / "master_timeline.csv"
PEOPLE = DATA / "verified_people_events.csv"

UNVER_EVENTS = DATA / "unverified_events.csv"
UNVER_PEOPLE = DATA / "unverified_people.csv"
UNVER_CONN = DATA / "unverified_connections.csv"

REQ_MASTER = ["date","location","event","participants_on_record","source_urls","notes"]
OPT_MASTER = ["deep_search_event","deep_search_notes"]
ALL_MASTER = REQ_MASTER + OPT_MASTER

REQ_PEOPLE = ["date","location","event","person","role","source_urls","deep_search_person","deep_search_notes"]

REQ_UNVER_EVENTS = ["date","location","event","primary_source","secondary_source","confidence","notes","next_step"]
REQ_UNVER_PEOPLE = ["person","possible_event_date","location","alleged_association","source","confidence","notes","next_step"]
REQ_UNVER_CONN = ["entity_a","entity_b","connection_type","source","confidence","notes","next_step"]

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

def parse_date_key(d: str) -> tuple:
    if "–" in d:
        d = d.split("–",1)[0].strip()
    for fmt in ("%Y-%m-%d","%Y-%m","%Y"):
        try:
            from datetime import datetime
            dt = datetime.strptime(d, fmt)
            return (0, dt.year, dt.month if fmt != "%Y" else 1, dt.day if fmt == "%Y-%m-%d" else 1, d)
        except ValueError:
            pass
    return (1, 9999, 12, 31, d or "~")

# ---------- MASTER (events) ----------
def normalize_master_row(r: dict) -> dict:
    out = {}
    for k in ALL_MASTER:
        v = (r.get(k,"") or "").strip()
        if k in ("location","event"):
            v = " ".join(v.split())
        out[k] = v
    if not out.get("deep_search_event"):
        out["deep_search_event"] = "pending"
    return out

def key_master(r: dict) -> tuple:
    return (r.get("date","").strip(), r.get("location","").strip(), r.get("event","").strip())

def merge_master():
    ensure_file(MASTER, ALL_MASTER)
    master_rows = read_csv(MASTER)
    merged, seen = [], set()
    for r in master_rows:
        for k in OPT_MASTER:
            r.setdefault(k, "")
        nr = normalize_master_row(r)
        k = key_master(nr)
        if k not in seen:
            merged.append(nr); seen.add(k)
    for p in sorted(DATA.glob("pending_updates_*.csv")):
        chunk = read_csv(p)
        if not chunk: continue
        for r in chunk:
            for k in OPT_MASTER:
                r.setdefault(k, "")
            nr = normalize_master_row(r)
            k = key_master(nr)
            if k not in seen:
                merged.append(nr); seen.add(k)
    merged.sort(key=lambda r: (parse_date_key(r["date"]), r["location"].lower(), r["event"].lower()))
    write_csv(MASTER, merged, ALL_MASTER)
    return [p for p in sorted(DATA.glob("pending_updates_*.csv"))]

# ---------- PEOPLE ----------
def normalize_people_row(r: dict) -> dict:
    out = {}
    for k in REQ_PEOPLE:
        out[k] = (r.get(k,"") or "").strip()
    if not out.get("deep_search_person"):
        out["deep_search_person"] = "pending"
    return out

def key_people(r: dict) -> tuple:
    return (r.get("date","").strip(), r.get("location","").strip(), r.get("event","").strip(), r.get("person","").strip())

def merge_people():
    ensure_file(PEOPLE, REQ_PEOPLE)
    existing = read_csv(PEOPLE)
    merged, seen = [], set()
    for r in existing:
        nr = normalize_people_row(r)
        k = key_people(nr)
        if k not in seen:
            merged.append(nr); seen.add(k)
    pending = []
    for p in sorted(DATA.glob("pending_people_*.csv")):
        chunk = read_csv(p)
        if not chunk: continue
        pending.append(p)
        if any(h not in chunk[0].keys() for h in REQ_PEOPLE):
            raise SystemExit(f"{p.name} missing required headers")
        for r in chunk:
            nr = normalize_people_row(r)
            k = key_people(nr)
            if k not in seen:
                merged.append(nr); seen.add(k)
    merged.sort(key=lambda r: (parse_date_key(r["date"]), r["location"].lower(), r["event"].lower(), r["person"].lower()))
    write_csv(PEOPLE, merged, REQ_PEOPLE)
    return pending

# ---------- UNVERIFIED ----------
def merge_unverified():
    ensure_file(UNVER_EVENTS, REQ_UNVER_EVENTS)
    ensure_file(UNVER_PEOPLE, REQ_UNVER_PEOPLE)
    ensure_file(UNVER_CONN, REQ_UNVER_CONN)

    ue = read_csv(UNVER_EVENTS); up = read_csv(UNVER_PEOPLE); uc = read_csv(UNVER_CONN)

    def add_unique(rows, item, key_fields):
        key = tuple((item.get(k,"") or "").strip() for k in key_fields)
        if key not in seen:
            rows.append(item); seen.add(key)

    seen = set()
    # seed sets:
    for r in ue: add_unique([], r, REQ_UNVER_EVENTS)
    for r in up: add_unique([], r, REQ_UNVER_PEOPLE)
    for r in uc: add_unique([], r, REQ_UNVER_CONN)
    # rebuild seen based on the three lists
    seen = set()

    # helper to dedupe by the whole row (ordered headers)
    def dedupe(existing, headers):
        seen_local = set()
        out = []
        for r in existing:
            key = tuple((r.get(h,"") or "").strip() for h in headers)
            if key not in seen_local:
                out.append({h: r.get(h,"") for h in headers}); seen_local.add(key)
        return out

    # merge pending_unverified_*.csv (flexible schema with 'type' column)
    pendings = []
    for p in sorted(DATA.glob("pending_unverified_*.csv")):
        rows = read_csv(p)
        if not rows: continue
        pendings.append(p)
        for r in rows:
            t = (r.get("type","") or "").strip().lower()
            if t == "event":
                item = {h: (r.get(h,"") or "").strip() for h in REQ_UNVER_EVENTS}
                ue.append(item)
            elif t == "person":
                item = {h: (r.get(h,"") or "").strip() for h in REQ_UNVER_PEOPLE}
                up.append(item)
            elif t == "connection":
                item = {h: (r.get(h,"") or "").strip() for h in REQ_UNVER_CONN}
                uc.append(item)

    ue = dedupe(ue, REQ_UNVER_EVENTS)
    up = dedupe(up, REQ_UNVER_PEOPLE)
    uc = dedupe(uc, REQ_UNVER_CONN)

    # sort
    ue.sort(key=lambda r: (r["date"].lower(), r["location"].lower(), r["event"].lower()))
    up.sort(key=lambda r: (r["possible_event_date"].lower(), r["location"].lower(), r["person"].lower()))
    uc.sort(key=lambda r: (r["entity_a"].lower(), r["entity_b"].lower(), r["connection_type"].lower()))

    write_csv(UNVER_EVENTS, ue, REQ_UNVER_EVENTS)
    write_csv(UNVER_PEOPLE, up, REQ_UNVER_PEOPLE)
    write_csv(UNVER_CONN, uc, REQ_UNVER_CONN)
    return pendings

def archive(files):
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    for p in files:
        (ARCHIVE / f"{p.stem}.processed_{ts}.csv").parent.mkdir(parents=True, exist_ok=True)
        p.replace(ARCHIVE / f"{p.stem}.processed_{ts}.csv")

def main():
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    pu = merge_master()
    pp = merge_people()
    pu2 = merge_unverified()
    archive(pu + pp + pu2)
    print("Merged events, people, and unverified leads successfully.")

if __name__ == "__main__":
    main()
