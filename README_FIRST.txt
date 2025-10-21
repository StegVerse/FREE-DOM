📦 FREE-DOM TV Integration Pack (iPhone‑ready)

This folder contains everything you need to add Token Vault (TV) integration to the FREE-DOM repo.

✅ Folder structure
  scripts/                → place inside your repo's scripts folder
  .github/workflows/      → place inside your repo's .github/workflows folder
  docs/                   → place inside your repo's docs folder

🪄 Upload order (after unzipping in Files app)
  1) Upload scripts/tv_fetch.py
  2) Upload .github/workflows/auto_update_tv_patch.yml
  3) Upload docs/TV_DEV_GUIDE.md

After committing, open the workflow file and replace TV_BASE_URL with your vault URL, and adjust the --role and --keys flags as needed.
