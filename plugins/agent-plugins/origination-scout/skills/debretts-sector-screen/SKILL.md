---
name: debretts-sector-screen
description: Screen a sector for origination candidates against Debrett's criteria — size, ownership, succession, growth plateau and sponsor hold period — and return a scored shortlist with the reason each name is on it. Use for origination sweeps, sector mapping, and building a target longlist before outreach. Triggers on "screen the sector", "find targets", "origination", "who should we be talking to", "sector map", "longlist".
---

# Sector screen

Origination is a filter problem, not a search problem. The market has thousands of
companies; Debrett's can hold a conversation with forty. This skill produces the forty
and the reason for each.

## Step 1 — Fix the screen before running it

Never screen without these five answers written down:

| Parameter | Typical Debrett's screen | This screen |
|---|---|---|
| Sector and sub-sector | Named, not "industrials" | |
| Revenue or EBITDA band | £1m–£15m EBITDA | |
| Geography | UK-headquartered, European customers acceptable | |
| Ownership | Founder or family owned, or sponsor-backed past year five | |
| Exclusions | Existing clients, live processes, conflicts | |

Full criteria and the scoring weights are in
[reference/screening-criteria.md](reference/screening-criteria.md).

## Step 2 — Run the screen against a connected source

Use the connectors, not recall. Company facts asserted from memory are `[UNVERIFIED]`
and cannot go on a shortlist.

- **Grata** — `search_companies` and `ai_search_companies` for the initial universe;
  `find_similar_companies` from a known good name; `get_company_financials` and
  `get_legal_entities` to size candidates from filings.
- **PitchBook** — `pitchbook_search` and `pitchbook_get_company_investors` for
  sponsor-backed names, fund vintage and hold period.
- **Companies House filings** where a private company's size must be confirmed.

Record for every candidate: source, field, and date accessed.

## Step 3 — Score against the timing signals

Debrett's edge in origination is timing, not discovery. Score each candidate 0–3 on:

| Signal | What to look for | Weight |
|---|---|---|
| **Succession** | Founder age, no obvious internal successor, recent director resignations | 3 |
| **Plateau** | Revenue flat or decelerating for two years after a growth run | 2 |
| **Sponsor clock** | Sponsor-backed, hold period past year four, fund near end of life | 3 |
| **Capital need** | Capex or working capital demand the balance sheet cannot fund | 2 |
| **Consolidation** | Named buyers active in the sub-sector in the past 18 months | 2 |
| **Relationship** | Existing Debrett's relationship or a warm route in | 2 |

Score is the weighted sum. Anything scoring on succession or the sponsor clock is worth a
call even if the rest is thin; anything scoring only on consolidation is not.

## Step 4 — Return the shortlist

| Company | Sub-sector | Revenue / EBITDA (basis, source) | Ownership | Signals scored | Score | Route in | Priority |
|---|---|---|---|---|---|---|---|

Priority A: call this month. B: this quarter. C: monitor, revisit at next sweep.

Then, separately:

- **Why each A is an A** — two sentences, naming the signal and the evidence.
- **Excluded and why** — names deliberately left off, so the next sweep does not
  rediscover them.
- **Open items** — every `[UNVERIFIED]` field and what would clear it.

## Step 5 — Hand off

- Priority A names → `debretts-target-dossier` for a one-page profile before any call.
- Approved names → the CRM, with the signal and score in the record so the next sweep
  can compare.
- Nothing goes to a client or a target from this skill. Outreach is a separate step
  under `debretts-outreach`, and a human sends it.

## Guardrails

- No invented revenues, EBITDA, ownership or shareholder names. Sized from filings or
  a connected source, or flagged.
- Do not infer that a company is for sale. A signal is a reason to call, not a fact
  about intent.
- Check the exclusion list before every sweep — approaching a company that is already in
  a Debrett's process is a real cost.
