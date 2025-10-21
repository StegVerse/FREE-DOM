#!/usr/bin/env python3
"""
tv_fetch.py — Thin client to fetch short‑lived, scoped secrets from StegVerse/TV
without storing any long‑lived credentials in the platform (GitHub Actions).

Design:
- In CI (GitHub Actions), obtain an OIDC ID token (requires `permissions: id-token: write`).
- Exchange that ID token at the TV endpoint for a short‑lived access token scoped to a role.
- Fetch only the requested keys as JSON and write them to a file (default: /tmp/tv.json).
- Never print secret values to logs; only write to the output file.
- Supports local dev via `--profile dev` which reads a short‑lived token from
  ~/.config/stegverse-tv/dev.json (issued by your TV CLI).

NOTE: Replace the placeholder TV endpoints with your actual Token Vault URLs.
"""
from __future__ import annotations
import argparse, json, os, sys, time
from pathlib import Path
from typing import Dict, Any, List

try:
    import requests  # type: ignore
except Exception:
    requests = None  # If missing, add a 'pip install requests' step in your workflow.

DEFAULT_OUT = "/tmp/tv.json"

def log(msg: str) -> None:
    # Non-secret logging
    print(f"[tv_fetch] {msg}", flush=True)

def get_github_oidc_jwt(audience: str) -> str:
    """
    Uses GitHub's OIDC env vars to obtain a signed ID token for the job.
    Requires: permissions.id-token: write in the workflow.
    """
    url = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL")
    token = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN")
    if not url or not token:
        raise RuntimeError("Missing GitHub OIDC request env vars. Ensure `permissions: id-token: write`.")
    if "?" in url:
        url = f"{url}&audience={audience}"
    else:
        url = f"{url}?audience={audience}"
    import urllib.request
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.load(resp)
    id_token = data.get("value")
    if not id_token:
        raise RuntimeError("Failed to obtain OIDC ID token from GitHub.")
    return id_token

def exchange_oidc_for_tv_token(tv_base_url: str, id_token: str, role: str) -> str:
    """
    Exchange the GitHub OIDC token for a short‑lived TV token scoped to `role`.
    TV must be configured to trust your repo/workflow via OIDC.
    """
    if requests is None:
        raise RuntimeError("The `requests` library is required. Add a `pip install requests` step.")
    url = tv_base_url.rstrip("/") + "/oidc/exchange"
    payload = {"id_token": id_token, "role": role}
    r = requests.post(url, json=payload, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f"TV OIDC exchange failed: {r.status_code} {r.text}")
    data = r.json()
    tv_token = data.get("access_token")
    if not tv_token:
        raise RuntimeError("TV did not return access_token")
    return tv_token

def get_tv_token_from_profile(profile: str) -> str:
    """
    Local dev path: read a short‑lived token issued by TV CLI.
    File: ~/.config/stegverse-tv/{profile}.json  with {"access_token": "...", "exp": 1234567890}
    """
    cfg = Path.home() / ".config" / "stegverse-tv" / f"{profile}.json"
    if not cfg.exists():
        raise RuntimeError(f"TV profile not found: {cfg}")
    data = json.loads(cfg.read_text(encoding="utf-8"))
    tok = data.get("access_token")
    if not tok:
        raise RuntimeError("TV dev token missing in profile file.")
    exp = data.get("exp")
    if exp and int(exp) < int(time.time()):
        raise RuntimeError("TV dev token expired. Renew via TV CLI.")
    return tok

def fetch_keys(tv_base_url: str, tv_token: str, keys: List[str]) -> Dict[str, Any]:
    """
    Fetch a list of keys from TV's KV API.
    Endpoint is a placeholder; adjust to your TV deployment.
    """
    if requests is None:
        raise RuntimeError("The `requests` library is required. Add a `pip install requests` step.")
    url = tv_base_url.rstrip("/") + "/kv/get"
    r = requests.post(url, headers={"Authorization": f"Bearer {tv_token}"},
                      json={"keys": keys}, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f"TV KV get failed: {r.status_code} {r.text}")
    out = r.json() or {}
    # Avoid printing values; just return them.
    return out

def main():
    p = argparse.ArgumentParser(description="Fetch short‑lived secrets from StegVerse/TV.")
    p.add_argument("--tv-url", required=True, help="Base URL for Token Vault (e.g., https://tv.stegverse.internal)")
    p.add_argument("--role", required=True, help="TV role to assume (e.g., free-dom/ci/auto-update)")
    p.add_argument("--aud", default="stegverse-tv", help="OIDC audience expected by TV (default: stegverse-tv)")
    p.add_argument("--keys", required=True, help="Comma-separated list of keys to fetch")
    p.add_argument("--out", default=DEFAULT_OUT, help=f"Output JSON path (default: {DEFAULT_OUT})")
    p.add_argument("--profile", help="Local dev profile (reads ~/.config/stegverse-tv/<profile>.json)")
    args = p.parse_args()

    keys = [k.strip() for k in args.keys.split(",") if k.strip()]
    if not keys:
        raise SystemExit("No keys requested. Use --keys key1,key2")

    # Determine auth path
    if args.profile:
        log(f"Using TV dev profile '{args.profile}'")
        tv_token = get_tv_token_from_profile(args.profile)
    else:
        log("Acquiring GitHub OIDC ID token…")
        id_token = get_github_oidc_jwt(audience=args.aud)
        log("Exchanging OIDC for short-lived TV token…")
        tv_token = exchange_oidc_for_tv_token(args.tv_url, id_token, role=args.role)

    log("Fetching requested keys (values will not be printed)…")
    values = fetch_keys(args.tv_url, tv_token, keys)

    out_path = Path(args.out)
    out_path.write_text(json.dumps(values), encoding="utf-8")
    log(f"Wrote secrets JSON to {out_path}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[tv_fetch] ERROR: {e}", file=sys.stderr)
        sys.exit(1)
