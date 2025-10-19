#!/usr/bin/env python3
import sys, csv, pathlib
from datetime import datetime

root = pathlib.Path(__file__).resolve().parents[1]
data_dir = root / "data"

master_headers = [
    "date","location","event","participants_on_record","source_urls","notes",
    "deep_search_event","deep_search_notes"
]
people_headers = [
    "date","location","event","person","role","source_urls","deep_search_person","deep_search_notes"
]

def read_csv(path):
    if not path.exists(): return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def check_headers(rows, required, name):
    if not rows:
        # allow empty files but ensure header presence (actual headers validated by import script)
        return
    missing = [h for h in required if h not in rows[0].keys()]
    if missing:
        print(f"::error ::{name} missing headers: {missing}")
        sys.exit(1)

def check_dates(rows, field, name):
    for i, r in enumerate(rows, start=2):
        val = (r.get(field,"") or "").strip()
        if not val:
            print(f"::warning ::{name} row {i} has empty {field}")
            continue
        # allow YYYY, YYYY-MM, YYYY-MM-DD and ranges like "YYYY-MM-DD–YYYY-MM-DD"
        if "–" in val:
            parts = val.split("–")
            val = parts[0].strip()
        ok = False
        for fmt in ("%Y-%m-%d","%Y-%m","%Y"):
            try:
                datetime.strptime(val, fmt)
                ok = True; break
            except ValueError:
                pass
        if not ok:
            print(f"::warning ::{name} row {i} has non-standard date '{(r.get(field,'') or '').strip()}'")

def main():
    mt = read_csv(data_dir / "master_timeline.csv")
    check_headers(mt, master_headers, "master_timeline.csv")
    check_dates(mt, "date", "master_timeline.csv")

    pe = read_csv(data_dir / "verified_people_events.csv")
    check_headers(pe, people_headers, "verified_people_events.csv")
    check_dates(pe, "date", "verified_people_events.csv")

    # Unverified validations (tolerant if empty)
    ue = read_csv(data_dir / "unverified_events.csv")
    if ue:
        ueh = ["date","location","event","primary_source","secondary_source","confidence","notes","next_step"]
        check_headers(ue, ueh, "unverified_events.csv")
        check_dates(ue, "date", "unverified_events.csv")

    up = read_csv(data_dir / "unverified_people.csv")
    if up:
        uph = ["person","possible_event_date","location","alleged_association","source","confidence","notes","next_step"]
        check_headers(up, uph, "unverified_people.csv")

    uc = read_csv(data_dir / "unverified_connections.csv")
    if uc:
        uch = ["entity_a","entity_b","connection_type","source","confidence","notes","next_step"]
        check_headers(uc, uch, "unverified_connections.csv")

    print(f"master_timeline rows: {len(mt)}")
    print(f"verified_people_events rows: {len(pe)}")
    print(f"unverified_events rows: {len(ue)}")
    print(f"unverified_people rows: {len(up)}")
    print(f"unverified_connections rows: {len(uc)}")

if __name__ == "__main__":
    main()
