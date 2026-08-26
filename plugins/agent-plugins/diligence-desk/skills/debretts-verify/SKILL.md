---
name: debretts-verify
description: The Debrett's verification pass — extract every figure, name, date, multiple and precedent from a draft, attach a source to each, and flag what cannot be sourced before the document leaves the firm. Use before sending any client-facing deliverable, and whenever asked to check numbers, tie out a document, or sanity-check a draft. Triggers on "verify", "check the numbers", "tie this out", "is this sourced", "before I send this", "fact check".
---

# Debrett's verification pass

A model can produce a confident, fluent answer that is simply wrong. It does not sound
different from a correct answer, which is the whole risk. Nothing leaves the firm until
every figure, name, date and precedent has a source or a flag.

**Run this as a separate pass, not as part of drafting.** Drafting wants fluency;
verification wants suspicion. Do not do both in one read.

## Step 1 — Extract the claims

Run the extractor over the draft to build the checklist mechanically rather than by eye:

```bash
python3 scripts/extract_claims.py <file> --csv out/verification-log.csv
```

Supports `.md`, `.txt`, `.docx`, `.pptx`, `.xlsx`. It returns every currency amount,
percentage, multiple, date, basis-point figure and bare number with its location, and
for workbooks it separately lists hardcoded numeric cells — the ones with no formula
behind them, which is where model errors hide.

Where the extractor cannot run, build the same table by hand. Do not skip it.

## Step 2 — Classify each claim

| Class | Test | Action |
|---|---|---|
| **Given** | The client or a document in the mandate Project supplied it | Cite the document and page |
| **Sourced** | It came from a connected system this session | Cite system, field and date accessed |
| **Derived** | Calculated from a Given or Sourced figure | Show the calculation, not the result alone |
| **Unverified** | Everything else | Mark `[UNVERIFIED]` inline and list under Open items |

A figure recalled from training data is **Unverified**, without exception. So is a figure
from a search result you did not open, a multiple "typical for the sector", and any
precedent whose terms were press-reported.

## Step 3 — Check the things that are wrong most often

- **Period basis.** LTM against FY, reported against adjusted, statutory against
  management. Label every metric with its basis.
- **Currency and units.** £m against £000s. A model in thousands feeding a deck in
  millions is the classic error.
- **Casting.** Do the columns add? Does the bridge tie from opening to closing?
- **Consistency across files.** The figure in the deck, the model and the memo must be
  the same figure. Name the workbook cell it comes from.
- **Dates.** Financial year ends, transaction announcement against completion dates,
  data-as-at dates on any market figure.
- **Names.** Legal entity names, spelling of individuals, job titles. Check the source,
  not your memory.
- **Precedents.** Announced or completed? Enterprise or equity value? Multiple on which
  metric, and whose adjustments?

## Step 4 — Confidentiality sweep

Before an external send, confirm the draft carries no deal codename that the recipient
should not see, no other client's name, no internal fee or pipeline commentary, and no
tracked changes or comments left in the file.

## Step 5 — Report

Return three things and nothing else:

1. **Verification log** — the table from step 2, every row classified.
2. **Open items** — the `[UNVERIFIED]` list, each with the one action that would clear it
   and who can clear it.
3. **A single line on readiness** — either "ready to send once open items 1-4 are
   cleared" or "not ready: [the reason]".

Do not rewrite the document in this pass. Verification finds; the author fixes.

## The rule

Every figure, name, date and precedent that leaves the firm is verified by the person
whose name is on the work. This skill makes that check fast. It does not transfer it.
