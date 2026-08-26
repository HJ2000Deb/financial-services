---
name: debretts-target-dossier
description: Build the one-page dossier Debrett's takes into a first call or a pitch — what the business does, how it is owned, how it has traded, who the buyers would be, and the three questions worth asking. Use before any origination call, management meeting or pitch. Triggers on "dossier", "background note", "profile this company", "prep me for the call", "who are they".
---

# Target dossier

One page, read in four minutes on the way to the call. Its job is to make you the
best-briefed person in the room, not to demonstrate research.

## Structure

### 1. The business in three sentences
What it sells, to whom, and why customers choose it. If you cannot write this from the
sources without hedging, say so — that gap is itself the first question for the call.

### 2. Ownership and control
Shareholders and percentages where filed. Directors, tenure, ages where filed. Sponsor and
investment date if backed. Any recent change at board level, with the filing date.

### 3. Trading
| Metric | FY-2 | FY-1 | FY / LTM | Basis | Source |
|---|---|---|---|---|---|
| Revenue | | | | Statutory / management | |
| Gross margin | | | | | |
| EBITDA | | | | Reported / adjusted | |
| Net debt | | | | | |

Label the basis on every line. An adjusted figure without its adjustments is not a figure.

### 4. What has changed
The two or three developments in the last 18 months that a buyer would care about: a
contract win, a site move, a capex programme, a director departure, a funding round, a
competitor consolidating. Each with a date and a source.

### 5. Who would buy it
Three to five named buyer types, with one named example each and one line of rationale.
Not a buyer universe — that is `debretts-buyer-universe`. Enough to show a founder we
have thought about their market.

### 6. The three questions
The three questions whose answers would most change our view. Not warm-up questions. For
a founder-owned business they are usually about succession intent, the real margin, and
customer concentration.

### 7. Open items
Every `[UNVERIFIED]` field, and what would clear it.

## Sources

Grata and PitchBook for company, financial and investor data. Companies House for
statutory accounts, directors and shareholdings. The company's own site and recent press
for what has changed. The CRM and Outlook for our own relationship history — check
whether anyone at Debrett's has spoken to them before, and read what was said.

## Guardrails

- Facts only, each with a source and a date accessed. No inferred revenue, no estimated
  EBITDA, no implied valuation.
- Nothing about an individual beyond what is publicly filed or published.
- If the dossier is for a pitch rather than an origination call, add the market context
  from `debretts-pitch-narrative` rather than expanding this page.
