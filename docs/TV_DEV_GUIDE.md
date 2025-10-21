# TV Integration — Developer Guide

This repo uses **StegVerse/TV** (Token Vault) for short‑lived, scoped credentials.
No long‑lived secrets are stored in GitHub Actions or committed to the repo.

## How it works (CI)
1. GitHub Actions obtains a signed **OIDC ID token** for the running job (`permissions: id-token: write`).
2. The job exchanges that OIDC token with TV for a **short‑lived access token** bound to a specific role (least privilege).
3. The job calls TV's KV API to fetch just the keys needed for the step and writes them to `/tmp/tv.json` (JSON).
4. CI consumes the values **without printing** them and deletes the file at the end of the job.

## How it works (local dev)
1. Install the TV CLI and authenticate: `tv login` (or equivalent).
2. A short‑lived dev token is written to `~/.config/stegverse-tv/dev.json`:
   ```json
   { "access_token": "…", "exp": 1735699200 }
   ```
3. Run the fetcher:
   ```bash
   python scripts/tv_fetch.py --tv-url https://TV_BASE_URL --role free-dom/dev/min --profile dev --keys secure_submission_url --out /tmp/tv.json
   ```
4. Use `/tmp/tv.json` as needed; delete it when done.

## Safety Rules
- **Do not** echo secrets to logs. Avoid `set -x`.
- Use `::add-mask::VALUE` if a value must appear in logs (avoid if possible).
- Fail‑closed: a failed TV fetch should stop the workflow.
- Keep roles **narrow** (e.g., `free-dom/ci/auto-update` with read‑only to just the required keys).
- Rotate TV policies/keys in the private `stegverse-tv-config` repository.

## Files
- `scripts/tv_fetch.py` — obtains short‑lived secrets via OIDC → TV exchange.
- `.github/workflows/auto_update_tv_patch.yml` — example workflow wiring.
- This guide — add to your repo as `docs/TV_DEV_GUIDE.md`.
