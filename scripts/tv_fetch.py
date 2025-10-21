#!/usr/bin/env python3
"""
Thin client to fetch short-lived, scoped secrets from StegVerse/TV via OIDC.
- CI: use GitHub OIDC (requires permissions: id-token: write)
- Local: use --profile to read a short-lived token from ~/.config/stegverse-tv/<profile>.json
"""
import argparse, json, os, sys, time
from pathlib import Path

try:
    import requests
except Exception:
    requests = None

DEFAULT_OUT = "/tmp/tv.json"

def log(msg):
    print(f"[tv_fetch] {msg}", flush=True)

def get_github_oidc_jwt(audience):
    url = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL")
    tok = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN")
    if not url or not tok:
        raise RuntimeError("Missing GitHub OIDC request env vars. Ensure permissions: id-token: write.")
    url = f"{url}{'&' if '?' in url else '?'}audience={audience}"
    import urllib.request, json as _json
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {tok}"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = _json.load(resp)
    if "value" not in data:
        raise RuntimeError("Failed to obtain OIDC ID token from GitHub.")
    return data["value"]

def exchange_oidc_for_tv_token(tv_base_url, id_token, role):
    if requests is None:
        raise RuntimeError("requests is required. Add 'pip install requests' in your workflow.")
    url = tv_base_url.rstrip("/") + "/oidc/exchange"
    r = requests.post(url, json={"id_token": id_token, "role": role}, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f"TV OIDC exchange failed: {r.status_code} {r.text}")
    data = r.json()
    if "access_token" not in data:
        raise RuntimeError("TV did not return access_token")
    return data["access_token"]

def get_tv_token_from_profile(profile):
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

def fetch_keys(tv_base_url, tv_token, keys):
    if requests is None:
        raise RuntimeError("requests is required. Add 'pip install requests' in your workflow.")
    url = tv_base_url.rstrip("/") + "/kv/get"
    r = requests.post(url, headers={"Authorization": f"Bearer {tv_token}"}, json={"keys": keys}, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f"TV KV get failed: {r.status_code} {r.text}")
    return r.json() or {}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tv-url", required=True)
    ap.add_argument("--role", required=True)
    ap.add_argument("--aud", default="stegverse-tv")
    ap.add_argument("--keys", required=True, help="Comma-separated list of keys to fetch")
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--profile")
    args = ap.parse_args()

    keys = [k.strip() for k in args.keys.split(",") if k.strip()]
    if not keys:
        print("No keys requested. Use --keys key1,key2", file=sys.stderr)
        sys.exit(2)

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
    Path(args.out).write_text(json.dumps(values), encoding="utf-8")
    log(f"Wrote secrets JSON to {args.out}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[tv_fetch] ERROR: {e}", file=sys.stderr)
        sys.exit(1)
