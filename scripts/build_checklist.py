#!/usr/bin/env python3
from __future__ import annotations
import csv, pathlib, re
from typing import List, Dict

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CHECKLIST = ROOT / "CHECKLIST.md"

# Master timeline + people files (with deep search fields)
MT_FIELDS = ["date","location","event","participants_on_record","source_urls","notes","deep_search_event","deep_search_notes"]
PEOPLE_FIELDS = ["date","location","event","person","role","source_urls","deep_search_person","deep_search_notes"]

# Smart verification regexes
RE_CSPAN_DIRECT = re.compile(r"c-span\.org/(video|clip|program)/", re.I)
RE_YT_DIRECT = re.compile(r"(youtube\.com/watch|youtu\.be/)", re.I)
RE_COMMITTEE_DIRECT = re.compile(r"(media\.house\.gov|oversight\.house\.gov/.+/(video|watch|hearing|press)|democrats-oversight\.house\.gov/.+/)", re.I)
RE_REUTERS_GENERIC = re.compile(r"^https?://www\.reuters\.com/world/(us|americas)/?$", re.I)
RE_CSPAN_GENERIC = re.compile(r"^https?://www\.c-span\.org/?$", re.I)
RE_OVERSIGHT_GENERIC = re.compile(r"^https?://(www\.)?oversight\.house\.gov/?$", re.I)

def read_csv(path: pathlib.Path, fields: List[str]) -> List[Dict]:
    if not path.exists(): return []
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    out = []
    for r in rows:
        out.append({k: (r.get(k,"") or "").strip() for k in fields if k in r})
    return out

def has_tbd(text: str) -> bool:
    return bool(re.search(r"\bTBD\b|to be determined|add (specific|direct)|add .* ID|ID pending", text, flags=re.I))

def looks_like_direct_video_link(urls: str) -> bool:
    return bool(RE_CSPAN_DIRECT.search(urls) or RE_YT_DIRECT.search(urls) or RE_COMMITTEE_DIRECT.search(urls))

def is_generic_placeholder(urls: str) -> bool:
    return bool(RE_CSPAN_GENERIC.search(urls) or RE_OVERSIGHT_GENERIC.search(urls) or RE_REUTERS_GENERIC.search(urls))

def build_sections(mt: List[Dict], pe: List[Dict]) -> Dict[str, List[List[str]]]:
    cspan, sdny, media, oversight = [], [], [], []
    deep_event, deep_people = [], []

    for r in mt:
        date, loc, event = r.get("date",""), r.get("location",""), r.get("event","")
        srcs, notes = r.get("source_urls",""), r.get("notes","")

        # C-SPAN pending
        if "C-SPAN" in event.upper():
            verified = "✅" if looks_like_direct_video_link(srcs) else "☐"
            if verified == "☐" and (has_tbd(notes) or is_generic_placeholder(srcs) or not srcs):
                cspan.append([event, date, loc, "TBD", verified, notes])

        # SDNY Docket
        if "SDNY DOCKET" in loc.upper() and ("ECF" in event.upper() or "UNSEAL" in event.upper()):
            verified_link = "✅" if ("courtlistener.com/docket" in srcs and not has_tbd(notes)) else "☐"
            if verified_link == "☐":
                m = re.search(r"ECF\s*([0-9]+(?:\.[0-9]+)?)", event, re.I)
                ecf = m.group(1) if m else "—"
                sdny.append([ecf, event, date, verified_link, srcs or ""])

        # Media sets
        if any(tok in event for tok in ["Reuters","GETTY","Wire","wire","Wire:"]):
            generic = is_generic_placeholder(srcs)
            verified = "✅" if (srcs and not generic) else "☐"
            if verified == "☐" and (has_tbd(notes) or generic or not srcs):
                media.append([date, loc, event, "TBD", verified, notes])

        # House Oversight video
        if "HOUSE OVERSIGHT" in loc.upper() and "VIDEO" in event.upper():
            verified = "✅" if looks_like_direct_video_link(srcs) else "☐"
            if verified == "☐":
                oversight.append([date, event, "TBD", verified, notes])

        # Deep search tracker – events
        dse = (r.get("deep_search_event","") or "").lower()
        if not dse or dse == "pending":
            deep_event.append([date, loc, event, r.get("participants_on_record",""), r.get("deep_search_notes","")])

    # Deep search tracker – people at events
    for r in pe:
        dsp = (r.get("deep_search_person","") or "").lower()
        if not dsp or dsp == "pending":
            deep_people.append([r.get("date",""), r.get("location",""), r.get("event",""), r.get("person",""), r.get("role",""), r.get("deep_search_notes","")])

    # sort sections
    for lst in (cspan, sdny, media, oversight, deep_event, deep_people):
        lst.sort(key=lambda x: tuple(str(s).lower() for s in x))

    return {
        "cspan": cspan, "sdny": sdny, "media": media, "oversight": oversight,
        "deep_event": deep_event, "deep_people": deep_people
    }

def render_table(headers, rows):
    if not rows: return "_All items resolved._\n"
    out = ["|"+"|".join(headers)+"|", "|"+"|".join(["---"]*len(headers))+"|"]
    out += ["|"+"|".join(r)+"|" for r in rows]
    return "\n".join(out)+"\n"

def compact_read(path: str, headers: list[str]) -> list[dict]:
    p = DATA / path
    if not p.exists(): return []
    with p.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [{k:(r.get(k,"") or "").strip() for k in headers} for r in rows]

def main():
    mt = read_csv(DATA / "master_timeline.csv", MT_FIELDS)
    pe = read_csv(DATA / "verified_people_events.csv", PEOPLE_FIELDS)
    sections = build_sections(mt, pe)

    md = []
    md.append("# FREE-DOM – Reference Completion Checklist (Auto-Generated)\n")
    md.append("Built each push. Items disappear once IDs/links are added or deep searches are marked done.\n")
    md.append("---\n")

    md.append("## 🗓️ C-SPAN Segments Needing Program/Clip IDs\n")
    md.append(render_table(["Event Title","Date","Location","Program/Clip ID","Verified","Notes"], sections["cspan"]))
    md.append("\n## ⚖️ CourtListener / SDNY Docket Items\n")
    md.append(render_table(["ECF #","Description","Date","Verified Link","Source"], sections["sdny"]))
    md.append("\n## 📰 Getty / Reuters / Wire Photo Sets – Asset IDs Pending\n")
    md.append(render_table(["Date","Location","Set Title","Asset ID","Verified","Notes"], sections["media"]))
    md.append("\n## 🏛️ House Oversight Video Clips – Direct URLs/IDs Pending\n")
    md.append(render_table(["Date","Title","Video ID/URL","Verified","Notes"], sections["oversight"]))

    md.append("\n## 🔎 Deep Searches Pending – Events\n")
    md.append(render_table(["Date","Location","Event","Participants (on record)","Search Notes"], sections["deep_event"]))
    md.append("\n## 🔎 Deep Searches Pending – People at Events\n")
    md.append(render_table(["Date","Location","Event","Person","Role","Search Notes"], sections["deep_people"]))

    # Unverified sections
    ue = [r for r in compact_read("unverified_events.csv", ["date","location","event","primary_source","secondary_source","confidence","notes","next_step"]) if r.get("confidence","").lower() != "verified"]
    up = [r for r in compact_read("unverified_people.csv", ["person","possible_event_date","location","alleged_association","source","confidence","notes","next_step"]) if r.get("confidence","").lower() != "verified"]
    uc = [r for r in compact_read("unverified_connections.csv", ["entity_a","entity_b","connection_type","source","confidence","notes","next_step"]) if r.get("confidence","").lower() != "verified"]

    md.append("\n## 🔸 Unverified Events – Awaiting Verification\n")
    md.append(render_table(["Date","Location","Event","Primary Source","Secondary Source","Confidence","Next Step"], [[r["date"], r["location"], r["event"], r["primary_source"], r["secondary_source"], r["confidence"], r["next_step"]] for r in ue]))
    md.append("\n## 🔸 Unverified People – Awaiting Cross-Confirmation\n")
    md.append(render_table(["Person","Possible Date","Location","Alleged Association","Source","Confidence","Next Step"], [[r["person"], r["possible_event_date"], r["location"], r["alleged_association"], r["source"], r["confidence"], r["next_step"]] for r in up]))
    md.append("\n## 🔸 Unverified Connections – Leads Needing Validation\n")
    md.append(render_table(["Entity A","Entity B","Connection Type","Source","Confidence","Next Step"], [[r["entity_a"], r["entity_b"], r["connection_type"], r["source"], r["confidence"], r["next_step"]] for r in uc]))

    CHECKLIST.write_text("\n".join(md), encoding="utf-8")
    print("Updated CHECKLIST.md")

if __name__ == "__main__":
    main()
