---
name: debretts-buyer-universe
description: Build a scored, prioritised buyer universe for a sell-side mandate and the buyer-specific angle for each approach — strategics, sponsors and sponsor-backed platforms, tiered into waves with the rationale a partner can interrogate. Use at marketing stage, and whenever the process needs broadening. Triggers on "buyer universe", "buyer list", "who would buy this", "strategic buyers", "financial sponsors", "approach list", "broaden the process".
---

# Buyer universe

A list of 200 names is a research exercise. Thirty to forty names, each with a reason that
survives a partner's questioning, is a process. Every name on the list answers: why would
this buyer pay more for this business than the next one?

Scoring model and weights: [reference/scoring-model.md](reference/scoring-model.md).

## Step 1 — Establish what is being sold

From the mandate Project, not from memory: what the business does, revenue and EBITDA with
basis, growth, the equity story pillars, the vendor's objectives (price, continuity,
confidentiality, speed), and the exclusion list. **Always ask the vendor for names to
include and to exclude before building the list.**

## Step 2 — Build the categories

**Strategic buyers**

| Category | Rationale that makes them pay |
|---|---|
| Direct competitors | Share, cost synergy, removing a competitor |
| Adjacent players | Product or capability extension, cross-sell into their base |
| Vertical integrators | Customers or suppliers capturing margin or securing supply |
| Platform builders | A named consolidation strategy with a gap this business fills |
| Overseas entrants | UK or European market access without a build |

**Financial buyers**

| Category | Rationale |
|---|---|
| Platform sponsors | Sector thesis, no platform yet, cheque size fits |
| Add-on buyers | A named portfolio company this bolts onto — name it |
| Growth or minority | Where the vendor wants partial exit or continuity |

Source names from connected systems: Grata (`search_buyers`, `find_similar_companies`,
`get_company_acquisitions`), PitchBook (`pitchbook_search`,
`pitchbook_get_investor_investments`, `pitchbook_get_company_deals`), plus our own CRM
history. Names recalled without a source are `[UNVERIFIED]` and cannot be approached.

## Step 3 — Score each name

Score 1–5 on strategic fit, ability to pay, acquisitiveness, deliverability and
relationship, weighted per the scoring model. Then apply the two overrides:

- **Antitrust flag** — a direct competitor whose share makes a referral likely. Flag, do
  not silently drop; the vendor decides.
- **Confidentiality flag** — a buyer whose process leaks, or a customer or supplier whose
  knowledge of a sale would damage trading. Flag before the first call.

## Step 4 — Tier into waves

| Tier | Names | Who | When |
|---|---|---|---|
| 1 | 6–10 | Highest fit, proven acquirers, clear rationale, deliverable | Wave one |
| 2 | 10–15 | Good fit, less obvious, or slower to move | Wave two |
| 3 | 10–20 | Possible, lower probability, or process-broadening | Only if needed |

## Step 5 — Write the buyer-specific angle

For every Tier 1 and Tier 2 name, one short paragraph — the argument we make to *that*
buyer. It must name something specific to them: their stated strategy, their last
acquisition, a gap in their footprint, a customer they have lost.

Then the contact map for Tier 1: decision maker and title, relationship status (existing,
cold, needs introduction), best route in, known constraints (size, geography, structure),
and who at Debrett's owns the approach.

## Step 6 — Output

1. **Workbook** — Strategics tab, Sponsors tab, both sorted by tier and score, with the
   scoring columns visible so a partner can re-weight; Contact map tab; Summary tab with
   counts by tier and category. Build with `xlsx-author`; formulas live, no hardcoded
   scores.
2. **One-page summary** — counts, the shape of the process this list implies, and the
   three names we most want.
3. **Buyer angles** — one paragraph per Tier 1 and 2 name.
4. **Flags** — antitrust, confidentiality, and every `[UNVERIFIED]` field.

## Step 7 — Keep it live

The universe is a working document. After every wave: log the response, move names between
tiers on evidence, and record why. Reconcile against the NDA log and the approach log
(`debretts-outreach`) before every process update to the vendor.

## Guardrails

- No invented buyers, portfolio companies, fund sizes, deal history or contacts.
- A sponsor's cheque size and sector focus come from a connected source or are flagged.
- No approach is made from this skill. Outreach is drafted separately and sent by a human.
- Check the vendor's exclusion list twice: before building and before the first approach.
