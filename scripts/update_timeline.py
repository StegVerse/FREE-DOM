import sys, csv, pathlib
from datetime import datetime

root = pathlib.Path(__file__).resolve().parents[1]
data_dir = root / "data"

required_mt_headers = [
    "date","location","event","participants_on_record","source_urls","notes"
]
required_ph_headers = [
    "date","place","media_type","what_is_documented","people_on_record","source_urls","scene_notes"
]
required_org_headers = [
    "entity_name","type","jurisdiction","identifier_or_ein","founded","active_years","public_sources","notes"
]

def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def check_headers(rows, required):
    missing = [h for h in required if h not in rows[0].keys()]
    if missing:
        print(f"::error ::Missing headers in {required}: {missing}")
        sys.exit(1)

def check_dates(rows, field):
    for i, r in enumerate(rows, start=2):
        val = r.get(field, "").strip()
        if not val:
            print(f"::warning ::Row {i} has empty {field}")
            continue
        # Allow ranges like 2019-07-20–2019-08-20 or year-only YYYY
        if "–" in val or "-" not in val:
            continue
        try:
            datetime.strptime(val, "%Y-%m-%d")
        except ValueError:
            # Allow YYYY-MM or YYYY only
            try:
                datetime.strptime(val, "%Y-%m")
            except ValueError:
                try:
                    datetime.strptime(val, "%Y")
                except ValueError:
                    print(f"::warning ::Row {i} has non-standard date: {val}")

def summarize(rows, label):
    print(f"{label}: {len(rows)} rows")
    # Count unique places/locations quick glance
    key = "location" if "location" in rows[0] else ("place" if "place" in rows[0] else None)
    if key:
        uniq = len(set(r[key] for r in rows))
        print(f"{label}: {uniq} unique {key}")

def main():
    mt = read_csv(data_dir / "master_timeline.csv")
    ph = read_csv(data_dir / "photo_video_anchors.csv")
    org = read_csv(data_dir / "organizations.csv")

    check_headers(mt, required_mt_headers)
    check_headers(ph, required_ph_headers)
    check_headers(org, required_org_headers)

    check_dates(mt, "date")
    check_dates(ph, "date")

    summarize(mt, "master_timeline")
    summarize(ph, "photo_video_anchors")
    summarize(org, "organizations")

if __name__ == "__main__":
    main()
