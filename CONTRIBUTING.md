# 🤝 Contributing to FREE-DOM

Thank you for your interest in contributing to **FREE-DOM**, a StegVerse initiative.  
This project depends on factual accuracy, technical reproducibility, and ethical rigor.

---

## ⚙️ Contribution Workflow

1. **Fork** the repository and create a new branch:  
   ```bash
   git checkout -b feature/your-branch-name
   ```

2. **Add or modify data** in the correct subdirectory:
   - `data/pending/` — new or partially verified submissions  
   - `data/unverified/` — leads needing confirmation  
   - `data/master/` — (CI-managed) fully verified datasets

3. **Run local checks** (optional but recommended):
   ```bash
   python scripts/build_checklist.py
   python scripts/build_changelog.py
   python scripts/update_timeline.py
   ```

4. **Commit and push** your changes:
   ```bash
   git add .
   git commit -m "Add: new verified entries"
   git push origin feature/your-branch-name
   ```

5. **Open a Pull Request** and include:
   - Source reliability
   - Verification stage (pending / confirmed)
   - Notes on any leads or anomalies

---

## 🧠 Standards of Evidence

| Requirement | Description |
|--------------|-------------|
| **Factual Accuracy** | Publicly verifiable information only |
| **Non-Implicative** | No accusations, assumptions, or speculation |
| **Traceability** | Provide reproducible data sources (URLs/dockets/RSS) |
| **Format Compliance** | Pass CSV schema validation via CI |

---

## 🧩 Ethics & Legal

- Respect privacy and anonymity at all times.  
- Avoid identifying living individuals directly.  
- Use neutral, descriptive language.  
- Maintain public source traceability.

---

## 🧰 Scripts

- [`search_agent.py`](scripts/search_agent.py) — automated public OSINT sweeps  
- [`build_checklist.py`](scripts/build_checklist.py) — regenerates pending verification items  
- [`build_changelog.py`](scripts/build_changelog.py) — versions & logs changes automatically

---

## 🧾 Review

All PRs are automatically validated by GitHub Actions:
- Schema checks
- Duplicate detection
- Basic lead verification

Maintainers merge PRs that pass checks and meet ethical standards.

---

Thank you for strengthening the public record — one verifiable entry at a time.

© FREE-DOM Project — a StegVerse initiative for truth, structure, and awareness.
