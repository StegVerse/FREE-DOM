"""
Auto-build CHECKLIST.md from data/*.csv, listing only rows that still need IDs.
Adds items when TBD appears; removes them as soon as they're resolved in CSVs.

Heuristics:
- C-SPAN items: event contains 'C-SPAN' or 'C-SPAN' and notes or source URLs suggest IDs not yet filled.
- CourtListener/SDNY docket: location contains 'SDNY Docket' and event mentions 'ECF' or 'Unsealing Order'.
- Getty/Reuters: event mentions 'Reuters', 'Getty', 'Wire' AND notes contain 'TBD' or similar.
- House Oversight video clips: location contains 'House Oversight' and event contains 'Video' AND source is generic (not a direct video URL).

When resolved (e.g., a specific ID/URL is added and notes no longer say TBD), the row disappears from the checklist.
"""

from __future__ import annotations
import csv
import pathlib
import re
from typing import List, Dict

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CHECKLIST = ROOT / "CHECKLIST.md"

# CSV schemas we expect
MT_FIELDS = ["date","location","event","participants_on_record","source_urls","notes"]

def read_csvs() -> List[Dict]:
    rows: List[Dict] = []
    for path in DATA.glob("*.csv"):
        if path.name.startswith("pending_updates_"):
            # Pending files get merged separately; the master is our source of truth.
            continue
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                # normalize keys we care about
                row = {k: (r.get(k,"") or "").strip() for k in MT_FIELDS if k in r}
                # Skip rows that don't match master schema
                if not row:
                    continue
                rows.append(row)
    return rows

def has_tbd(text: str) -> bool:
    return bool(re.search(r"\bTBD\b|to be determined|add (specific|direct)|add .* ID", text, flags=re.I))

def looks_like_direct_video_link(urls: str) -> bool:
    # naive heuristic: a direct c-span program/clip, youtube watch URL, or committee media URL
    return any(tag in urls for tag in ["c-span.org/video","c-span.org/clip","youtube.com/watch","youtu.be","media.house.gov"])

def is_generic(urls: str) -> bool:
    # generic hosts we used as placeholders
    return any(u in urls for u in ["https://www.c-span.org/", "https://oversight.house.gov/", "https://www.reuters.com/world/us/", "https://www.reuters.com/world/americas/"])

def extract_ecf(event: str) -> str:
    m = re.search(r"ECF\s*([0-9]+(?:\.[0-9]+)?)", event)
    return m.group(1) if m else ""

def build_sections(rows: List[Dict]) -> Dict[str, List[List[str]]]:
    cspan, sdny, getty_reuters, oversight = [], [], [], []

    for r in rows:
        date = r.get("date","")
        location = r.get("location","")
        event = r.get("event","")
        srcs = r.get("source_urls","")
        notes = r.get("notes","")

        # C-SPAN
        if ("C-SPAN" in event.upper() or "C-SPAN" in event) and (has_tbd(notes) or is_generic(srcs)) and not looks_like_direct_video_link(srcs):
            cspan.append([event, date, location, "TBD", "☐", notes])

        # SDNY Docket / CourtListener
        if "SDNY DOCKET" in location.upper() and ("ECF" in event.upper() or "UNSEAL" in event.upper()):
            ecf = extract_ecf(event) or "—"
            verified_link = "✅" if ("courtlistener.com/docket" in srcs and not has_tbd(notes)) else "☐"
            sdny.append([ecf, event, date, verified_link, srcs or ""])

        # Getty/Reuters/Wire
        if any(tok in event for tok in ["Reuters", "GETTY", "Wire", "wire", "Wire:"]):
            # Need an asset/gallery ID or non-generic link
            if has_tbd(notes) or is_generic(srcs):
                getty_reuters.append([date, location, event, "TBD", "☐", notes])

        # House Oversight video clips
        if "HOUSE OVERSIGHT" in location.upper() and "VIDEO" in event.upper():
            # If only generic homepage is present or notes say add link/ID -> pending
            if is_generic(srcs) or has_tbd(notes):
                oversight.append([date, event, "TBD", "☐", notes])

    # sort for consistency
    cspan.sort(key=lambda x: (x[1], x[0]))
    sdny.sort(key=lambda x: (x[2], x[0]))
    getty_reuters.sort(key=lambda x: (x[0], x[1]))
    oversight.sort(key=lambda x: (x[0], x[1]))

    return {
        "cspan": cspan,
        "sdny": sdny,
        "media": getty_reuters,
        "oversight": oversight
    }

def render_table(headers: List[str], rows: List[List[str]]) -> str:
    if not rows:
        return "_All items resolved._\n"
    out = ["|" + "|".join(headers) + "|", "|" + "|".join(["---"]*len(headers)) + "|"]
    for r in rows:
        out.append("|" + "|".join(r) + "|")
    return "\n".join(out) + "\n"

def build_markdown(sections: Dict[str, List[List[str]]]) -> str:
    md = []
    md.append("# FREE-DOM – Reference Completion Checklist (Auto-Generated)\n")
    md.append("This file is rebuilt on every push. It lists only items with pending IDs/links; once you add exact IDs or direct links in the CSVs, the corresponding rows disappear automatically.\n")
    md.append("---\n")

    md.append("## 🗓️ C-SPAN Segments Needing Program/Clip IDs\n")
    md.append(render_table(["Event Title","Date","Location","Program/Clip ID","Verified","Notes"], sections["cspan"]))

    md.append("\n## ⚖️ CourtListener / SDNY Docket Items\n")
    md.append(render_table(["ECF #","Description","Date","Verified Link","Source"], sections["sdny"]))

    md.append("\n## 📰 Getty / Reuters / Wire Photo Sets Needing Asset IDs\n")
    md.append(render_table(["Date","Location","Set Title","Asset ID","Verified","Notes"], sections["media"]))

    md.append("\n## 🏛️ House Oversight Committee Video Clips (Direct URLs/IDs Pending)\n")
    md.append(render_table(["Date","Title","Video ID/URL","Verified","Notes"], sections["oversight"]))

    md.append("\n---\n")
    md.append("_Last built by `scripts/build_checklist.py`._\n")
    return "\n".join(md)

def main():
    rows = read_csvs()
    sections = build_sections(rows)
    content = build_markdown(sections)

    prev = CHECKLIST.read_text(encoding="utf-8") if CHECKLIST.exists() else ""
    if content.strip() != prev.strip():
        CHECKLIST.write_text(content, encoding="utf-8")
        print(f"Updated {CHECKLIST}")
    else:
        print("CHECKLIST.md unchanged")

if __name__ == "__main__":
    main()
