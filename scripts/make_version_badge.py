#!/usr/bin/env python3
"""
Generate a static SVG badge for the current repo version.

Reads:  data/summary/VERSION   (e.g., "v1.2.3")
Writes: docs/badges/version.svg
"""

from __future__ import annotations
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
VERSION_PATH = ROOT / "data" / "summary" / "VERSION"
BADGE_DIR = ROOT / "docs" / "badges"
BADGE_OUT = BADGE_DIR / "version.svg"

def read_version() -> str:
    raw = "v1.0.0"
    if VERSION_PATH.exists():
        t = VERSION_PATH.read_text(encoding="utf-8").strip()
        if re.match(r"^v?\d+\.\d+\.\d+$", t):
            raw = t if t.startswith("v") else f"v{t}"
    return raw

def make_badge_svg(text: str) -> str:
    # Minimal Shields-like static badge (no external service needed)
    label = "version"
    value = text
    # width estimates based on monospace (keeps it simple)
    def w(s): return 6 * len(s) + 20
    lw, vw = w(label), w(value)
    total = lw + vw
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total}" height="20" role="img" aria-label="{label}: {value}">
  <linearGradient id="g" x2="0" y2="100%">
    <stop offset="0" stop-color="#fff" stop-opacity=".7"/>
    <stop offset=".1" stop-opacity=".1"/>
    <stop offset=".9" stop-opacity=".3"/>
    <stop offset="1" stop-opacity=".5"/>
  </linearGradient>
  <mask id="m">
    <rect width="{total}" height="20" rx="3" fill="#fff"/>
  </mask>
  <g mask="url(#m)">
    <rect width="{lw}" height="20" fill="#555"/>
    <rect x="{lw}" width="{vw}" height="20" fill="#2ea44f"/>
    <rect width="{total}" height="20" fill="url(#g)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="{lw/2:.1f}" y="14">{label}</text>
    <text x="{lw+vw/2:.1f}" y="14">{value}</text>
  </g>
</svg>"""

def main():
    BADGE_DIR.mkdir(parents=True, exist_ok=True)
    version = read_version()
    svg = make_badge_svg(version)
    BADGE_OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {BADGE_OUT} for {version}")

if __name__ == "__main__":
    main()
