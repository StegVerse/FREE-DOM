"""
Auto-build CHECKLIST.md from data/*.csv, listing only rows that still need IDs.
Adds items when TBD/generic links appear; removes them once direct IDs/links are present.

Smart verification:
- C-SPAN: marks verified if source_urls contain '/video/' or '/clip/' or '/program/'.
- YouTube: marks verified if source_urls contain 'youtube.com/watch' or 'youtu.be'.
- Committee/Oversight: marks verified if a direct page/media URL is present (not just homepage).
- Reuters/Getty: marks verified if URLs are not the generic world/us or world/americas index pages.

Rows come from any CSV in data/ with the master schema; pending_* files are ignored (they get merged first).
"""

from __future__ import annotations
import csv
import pathlib
import re
from typing import List, Dict

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CHECKLIST = ROOT / "CHECKLIST.md"

MT_FIELDS = ["date","location","event","participants_on_record","source_urls","notes"]

# --- Heuristics / regexes ---
RE_CSPAN_DIRECT = re.compile(r"c-span\.org/(video|clip|program)/", re.I)
RE_YT_DIRECT = re.compile(r"(youtube\.com/watch|youtu\.be/)", re.I)
RE_COMMITTEE_DIRECT = re.compile(r"(media\.house\.gov|oversight\.house\.gov/.+/(video|watch|hearing|press)|democrats-oversight\.house\.gov/.+/)", re.I)
RE_REUTERS_GENERIC = re.compile(r"^https?://www\.reuters\.com/world/(us|americas)/?$", re.I)
RE_CSPAN_GENERIC = re.compile(r"^https?://www\.c-span\.org/?$", re.I)
RE_OVERSIGHT_GENERIC = re.compile(r"^https?://(www\.)?oversight\.house\.gov/?$", re.I)

def read_csvs() -> List[Dict]:
    rows: List[Dict] = []
    for path in DATA.glob("*.csv"):
        if path.name.startswith("pending_updates_"):
            continue
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                # Only accept rows that resemble master schema
                row = {k: (r.get(k,"") or "").strip() for k in MT_FIELDS if k in r}
                if not row:
                    continue
                rows.append(row)
    return rows

def has_tbd(text: str) -> bool:
    return bool(re.search(r"\bTBD\b|to be determined|add (specific|direct)|add .* ID|ID pending", text, flags=re.I))

def looks_like_direct_video_link(urls: str) -> bool:
    return bool(RE_CSPAN_DIRECT.search(urls) or RE_YT_DIRECT.search(urls) or RE_COMMITTEE_DIRECT.search(urls))

def is_generic_placeholder(urls: str) -> bool:
    return bool(RE_CSPAN_GENERIC.search(urls) or RE_OVERSIGHT_GENERIC.search(urls) or RE_REUTERS_GENERIC.search(urls))

def extract_ecf(event: str) -> str:
    m = re.search(r"ECF\s*([0-9]+(?:\.[0-9]+)?)", event, re.I)
    return m.group(1) if m else ""

def build_sections(rows: List[Dict]) -> Dict[str, List[List[str]]]:
    cspan, sdny, media, oversight = [], [], [], []

    for r in rows:
        date = r.get("date","")
        location = r.get("location","")
        event = r.get("event","")
        srcs = r.get("source_urls","")
        notes = r.get("notes","")

        # --- C-SPAN (pending IDs) ---
        if "C-SPAN" in event.upper():
            verified = "✅" if looks_like_direct_video_link(srcs) else "☐"
            # show only pending ones (unverified or explicitly TBD)
            if verified == "☐" and (has_tbd(notes) or is_generic_placeholder(srcs) or not srcs):
                cspan.append([event, date, location, "TBD", verified, notes])

        # --- SDNY Docket / CourtListener ---
        if "SDNY DOCKET" in location.upper() and ("ECF" in event.upper() or "UNSEAL" in event.upper()):
            ecf = extract_ecf(event) or "—"
            verified_link = "✅" if ("courtlistener.com/docket" in srcs and not has_tbd(notes)) else "☐"
            # show only when not verified
            if verified_link == "☐":
                sdny.append([ecf, event, date, verified_link, srcs or ""])

        # --- Getty / Reuters / Wire (pending asset IDs) ---
        mentions_media = any(tok in event for tok in ["Reuters", "GETTY", "Wire", "wire", "Wire:"])
        if mentions_media:
            # verify if link is specific (not generic placeholder)
            generic = is_generic_placeholder(srcs)
            verified = "✅" if (srcs and not generic) else "☐"
            if verified == "☐" and (has_tbd(notes) or generic or not srcs):
                media.append([date, location, event, "TBD", verified, notes])

        # --- House Oversight video clips (pending direct URLs/IDs) ---
        if "HOUSE OVERSIGHT" in location.upper() and "VIDEO" in event.upper():
            verified = "✅" if looks_like_direct_video_link(srcs) else ("☐" if is_generic_placeholder(srcs) or not srcs else "☐")
            if verified == "☐":
                oversight.append([date, event, "TBD", verified, notes])

    # sort sections for stability
    cspan.sort(key=lambda x: (x[1], x[0]))
    sdny.sort(key=lambda x: (x[2], x[0]))
    media.sort(key=lambda x: (x[0], x[1]))
    oversight.sort(key=lambda x: (x[0], x[1]))

    return {"cspan": cspan, "sdny": sdny, "media": media, "oversight": oversight}

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
