#!/usr/bin/env python3
"""
AI Search Agent (Public OSINT Only)
- Scans your CSVs for deep_search_*: pending
- Crawls whitelisted sources (RSS & allowed pages)
- Writes suggested links/notes back into CSVs (non-destructive: appends context)
- Logs everything under data/ai_agent_logs/
- NEVER accesses non-public or “dark web” content
"""

from __future__ import annotations
import csv, os, re, json, time, pathlib, hashlib
from datetime import datetime
from typing import List, Dict, Tuple

import pandas as pd
import feedparser
import requests
from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
LOG_DIR = DATA / "ai_agent_logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Input files (must exist with headers as per earlier setup)
MASTER = DATA / "master_timeline.csv"
PEOPLE = DATA / "verified_people_events.csv"
UNVER_EVENTS = DATA / "unverified_events.csv"
UNVER_PEOPLE = DATA / "unverified_people.csv"
UNVER_CONN = DATA / "unverified_connections.csv"

WHITELIST = DATA / "sources_whitelist.csv"

USER_AGENT = "FREE-DOM-AI-Agent/1.0 (+public sources only)"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"})

def read_whitelist() -> List[Dict[str,str]]:
    rows = []
    if WHITELIST.exists():
        with WHITELIST.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    return rows

def safe_get(url: str, timeout: int = 20):
    try:
        r = SESSION.get(url, timeout=timeout)
        if r.status_code == 200 and "text/html" in r.headers.get("content-type",""):
            return r.text
        return ""
    except Exception:
        return ""

def normalize_spaces(s: str) -> str:
    return " ".join((s or "").split())

def find_pending_master(df: pd.DataFrame) -> pd.DataFrame:
    return df[(df["deep_search_event"].fillna("").str.lower().isin(["", "pending"]))]

def find_pending_people(df: pd.DataFrame) -> pd.DataFrame:
    return df[(df["deep_search_person"].fillna("").str.lower().isin(["", "pending"]))]

def mk_log() -> pathlib.Path:
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    return LOG_DIR / f"agent_run_{ts}.jsonl"

def hash_key(*parts) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(str(p).encode("utf-8", errors="ignore"))
    return h.hexdigest()[:16]

def search_rss(feeds: List[str], keywords: List[str], limit_per_feed: int = 30) -> List[Dict]:
    results = []
    kw = [k.lower() for k in keywords if k]
    for url in feeds:
        try:
            parsed = feedparser.parse(url)
            for entry in (parsed.entries[:limit_per_feed] if hasattr(parsed, "entries") else []):
                text = " ".join([
                    entry.get("title",""),
                    entry.get("summary",""),
                    " ".join([t.get("term","") for t in entry.get("tags", []) if isinstance(t, dict)])
                ]).lower()
                if all(k in text for k in kw):
                    results.append({
                        "feed": url,
                        "title": entry.get("title","").strip(),
                        "link": entry.get("link","").strip(),
                        "published": entry.get("published","").strip()
                    })
        except Exception:
            continue
    return results

def site_keyword_scan(pages: List[str], keywords: List[str], limit_per_site: int = 10) -> List[Dict]:
    out = []
    kw = [k.lower() for k in keywords if k]
    for base in pages:
        html = safe_get(base)
        if not html: 
            continue
        soup = BeautifulSoup(html, "html.parser")
        # collect anchors that stay on same domain and include keywords in text
        anchors = soup.find_all("a", href=True)
        count = 0
        for a in anchors:
            txt = (a.get_text(" ", strip=True) or "").lower()
            if all(k in txt for k in kw) and a["href"].startswith("http"):
                out.append({"page": base, "title": a.get_text(" ", strip=True), "link": a["href"]})
                count += 1
                if count >= limit_per_site:
                    break
    return out

def load_csv(path: pathlib.Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)

def write_csv(path: pathlib.Path, df: pd.DataFrame):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)

def keywords_for_event(row: pd.Series) -> List[str]:
    # Conservative keyword extraction (no names invented): event/location words + “Epstein”/“Maxwell” for context
    base = " ".join([str(row.get("event","")), str(row.get("location",""))])
    tokens = [t for t in re.split(r"[^A-Za-z0-9]+", base) if len(t) >= 3]
    return list(dict.fromkeys([t.lower() for t in tokens]))[:6] + ["epstein", "maxwell"]

def keywords_for_person(row: pd.Series) -> List[str]:
    base = " ".join([str(row.get("person","")), str(row.get("event","")), str(row.get("location",""))])
    tokens = [t for t in re.split(r"[^A-Za-z0-9]+", base) if len(t) >= 3]
    return list(dict.fromkeys([t.lower() for t in tokens]))[:6] + ["court", "sdny", "oversight"]

def log_line(log_path: pathlib.Path, payload: Dict):
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")

def main():
    log_path = mk_log()
    wl = read_whitelist()
    rss_feeds = [r["url"] for r in wl if (r.get("type","rss").lower() == "rss")]
    site_pages = [r["url"] for r in wl if (r.get("type","rss").lower() != "rss")]

    master = load_csv(MASTER)
    people = load_csv(PEOPLE)
    unver_e = load_csv(UNVER_EVENTS)
    unver_p = load_csv(UNVER_PEOPLE)
    unver_c = load_csv(UNVER_CONN)

    if not master.empty and "deep_search_event" in master.columns:
        pending_events = find_pending_master(master)
    else:
        pending_events = pd.DataFrame()

    if not people.empty and "deep_search_person" in people.columns:
        pending_people = find_pending_people(people)
    else:
        pending_people = pd.DataFrame()

    total_hits = 0

    # Search for events
    for _, row in pending_events.iterrows():
        kws = keywords_for_event(row)
        rss_hits = search_rss(rss_feeds, kws, limit_per_feed=25)
        site_hits = site_keyword_scan(site_pages, kws, limit_per_site=8)
        hits = rss_hits[:5] + site_hits[:5]  # cap per row, keep it tidy

        if hits:
            total_hits += len(hits)
            # Append to notes (non-destructive). No claims, just references.
            notes = normalize_spaces(str(row.get("notes","")))
            append = " Leads: " + "; ".join([h["link"] for h in hits])
            ix = row.name
            master.at[ix, "notes"] = (notes + append).strip()
            # Do not auto-flip to verified; leave deep_search_event pending for human review

            log_line(log_path, {
                "type":"event", "date": str(row.get("date","")), "event": str(row.get("event","")),
                "keywords": kws, "hits": hits
            })

    # Search for people
    for _, row in pending_people.iterrows():
        kws = keywords_for_person(row)
        rss_hits = search_rss(rss_feeds, kws, limit_per_feed=25)
        site_hits = site_keyword_scan(site_pages, kws, limit_per_site=8)
        hits = rss_hits[:5] + site_hits[:5]

        if hits:
            total_hits += len(hits)
            notes = normalize_spaces(str(row.get("deep_search_notes","")))
            append = " Leads: " + "; ".join([h["link"] for h in hits])
            ix = row.name
            people.at[ix, "deep_search_notes"] = (notes + append).strip()

            log_line(log_path, {
                "type":"person", "date": str(row.get("date","")), "person": str(row.get("person","")),
                "event": str(row.get("event","")), "keywords": kws, "hits": hits
            })

    # Write outputs
    if not master.empty:
        write_csv(MASTER, master)
    if not people.empty:
        write_csv(PEOPLE, people)

    # Summary log
    log_line(log_path, {"summary": {"total_hits": total_hits}})

if __name__ == "__main__":
    main()
