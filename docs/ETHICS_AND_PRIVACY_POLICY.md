# 🛡️ Ethics & Privacy Policy
**FREE-DOM Project — a StegVerse initiative for truth, structure, and awareness**  
**Effective:** 2025-10-20

This document defines how the FREE-DOM project handles sensitive information, including:
- personally identifying information (PII),
- submissions from victims, witnesses, and other individuals,
- material that alleges criminal activity, and
- photographs or videos that appear to show identifiable people.

Our goal is to preserve an accurate, auditable historical record **without** compromising privacy, safety, or due process.

---

## 1) Core Principles
- **Do no harm.** We will not publish material that could expose vulnerable people, interfere with investigations, or imply guilt.
- **Publicly verifiable sources only.** The public datasets include only information that can be independently verified.
- **Anonymize aggressively.** Any private submissions are anonymized before analysis; identifiers are never added to public data.
- **Respect legal boundaries.** We do not act as investigators or law enforcement; credible criminal allegations are referred to appropriate authorities.

---

## 2) Sensitive Submissions — Intake & Triage
When submissions include names of living individuals (victims, witnesses, or alleged perpetrators), explicit allegations, or identifying imagery:

1. **Receipt:** The material is tagged as **sensitive** and stored in a secure, access-controlled location that is **not** part of the public repository.
2. **Acknowledgment:** If contact details are provided, we acknowledge receipt and provide this policy link.
3. **Classification:** We classify content by type (testimony, photograph, document, etc.) and risk level (low/medium/high).

> **We will not publish raw identifiers** from private submissions in public datasets.

---

## 3) Review & Decision Flow
Each sensitive submission follows this process:

1. **Human Review:** An ethics reviewer determines whether the submission contains (a) verifiable facts, and (b) identifiers.
2. **Decision:** One or more actions may follow:
   - **Anonymize & Integrate:** Extract only non-identifying, verifiable facts (e.g., dates/locations/event metadata) into public datasets.
   - **Retain Privately:** Keep the full submission in a secure store for up to **90 days** for potential follow-up.
   - **Refer to Authorities:** If a credible allegation of criminal activity is present, notify appropriate authorities or qualified journalists who handle such matters.
3. **Recordkeeping:** We maintain a minimal audit record (timestamp, type, action) **without** storing identifiers in the public repo.

---

## 4) Photographs & Videos (Identification Claims)
When a submission claims to identify people in media:

- We do **not** publish names or labels of real individuals in public datasets.
- We may store media privately, record a media hash/reference, and track the claim status (e.g., `observer_claim: pending`).
- Only **non-identifying** metadata is eligible for public integration (date, place, event context, public URL if already widely published).

Example (public dataset entry):
```csv
image_id,public_url,event_date,event_location,notes,claim_verification_status
epstein_event_2003_04_12,https://example.tld/photo.jpg,2003-04-12,Location X,"Context only; no named labels",pending
```

---

## 5) Inclusion / Exclusion Criteria for Public Data
**Eligible (after review & anonymization)**  
- Dates, locations, event names, and entities already documented in public records  
- Links to widely reported public coverage (major outlets, court filings, FOIA materials)  
- Aggregated/statistical descriptions that do not identify individuals

**Ineligible (exclude from public repo)**  
- Names or contact details of living private individuals (victims, witnesses, alleged perpetrators) from private submissions  
- Graphic content or materials that could re-traumatize victims  
- Any content that violates platform terms, local laws, or due process

---

## 6) Secure Storage & Retention
- Submissions classified as sensitive are stored in an encrypted, access-controlled location **outside** the public repository.
- Default retention is **90 days** unless legal or safety considerations require longer retention or immediate deletion.
- Access is limited to designated ethics reviewers; access logs are maintained where feasible.

---

## 7) Escalation & Referrals
- Credible allegations of criminal activity may be referred to law enforcement, child protection entities, or specialized investigative journalists.
- We do not guarantee follow-up, case investigation, or outcomes. Our role is limited to curation of non-identifying, verifiable public data.

---

## 8) Contributor Responsibilities
- Do not upload names or identifiable information about living individuals to the public repository.
- Use the pending CSV templates for event data and leave identifying details out.
- When in doubt, contact maintainers privately and request a secure submission path.

---

## 9) Policy Changes
This policy may be updated. Material changes will be noted in the project [CHANGELOG](../CHANGELOG.md) and dated.

---

© FREE-DOM Project — a StegVerse initiative for truth, structure, and awareness.
