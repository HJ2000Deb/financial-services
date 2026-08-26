---
description: Run the Debrett'\''s verification pass before anything leaves the firm
argument-hint: "[file path]"
---

Load the `debretts-verify` skill and run the verification pass over the file given.

Use `scripts/extract_claims.py` to build the checklist mechanically, classify every claim as Given, Sourced, Derived or Unverified, and return the verification log, the open items with the action that would clear each, and one line on readiness. Do not rewrite the document.
