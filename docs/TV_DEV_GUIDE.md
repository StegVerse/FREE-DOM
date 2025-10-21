# TV Integration — Developer Guide

This repo uses StegVerse/TV (Token Vault) for short-lived, scoped credentials.
No long-lived secrets are stored in GitHub Actions or committed to the repo.

CI flow:
1. GitHub Actions obtains a signed OIDC ID token (permissions: id-token: write).
2. The job exchanges that OIDC token with TV for a short-lived access token bound to a specific role.
3. The job fetches keys and writes them to /tmp/tv.json (JSON). The file is deleted at the end of the run.

Local dev:
1. Install TV CLI and authenticate: tv login (or equivalent).
2. Short-lived dev token is written to ~/.config/stegverse-tv/dev.json
3. Run:
   python scripts/tv_fetch.py --tv-url https://TV_BASE_URL --role free-dom/dev/min --profile dev --keys secure_submission_url --out /tmp/tv.json

Safety rules:
- Do not echo secrets to logs.
- Use ::add-mask::VALUE if a value must appear in logs (avoid).
- Fail-closed on TV failures.
- Keep roles narrow (e.g., free-dom/ci/auto-update).
- Rotate policies/keys in the private token-vault-config repo.
