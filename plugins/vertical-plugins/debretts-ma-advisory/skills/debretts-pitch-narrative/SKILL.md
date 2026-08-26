---
name: debretts-pitch-narrative
description: Build the Debrett's pitch — market context and comparable activity, indicative positioning and equity story, honest differentiation against larger houses, and the objections a vendor will raise with the answer to each. Use when preparing to pitch for a mandate or a beauty parade. Triggers on "pitch", "beauty parade", "credentials meeting", "why us", "objection handling", "we are pitching against".
---

# Pitch narrative

A mid-market pitch is won on three things: that we understand this market better than the
other two firms in the room, that we have a specific view on what this business is worth
to whom, and that the vendor believes we will personally do the work.

## Step 1 — Market context

Two pages at most, all of it sourced.

- Where the sub-sector is in its cycle, with the evidence.
- Comparable activity: completed and announced transactions in the sub-sector, last 24
  months. Target, buyer, date, size and multiple **where disclosed**. Never estimated.
- Who has been buying, and what they paid for. Read across from what buyers said about
  their own deals, not from what we assume they wanted.
- What has changed in the last six months that affects timing.

Sources: PitchBook (`pitchbook_search`, `pitchbook_get_company_deals`), Grata
(`search_transactions`, `search_buyers`). Every figure carries source and date accessed;
undisclosed terms are stated as undisclosed, not inferred.

## Step 2 — Indicative positioning

How we would take this business to market:

- The equity story in one paragraph — see `debretts-equity-story` for the full build.
- Which buyer categories we would run at, and roughly how many names in each.
- Process shape: targeted approach, limited auction or full process, and why this asset
  suits that shape.
- Timetable outline, working back from the vendor's own date.
- Where the value sits, and where a buyer will attack it.

If a valuation range is given at pitch, it is expressed as a range derived on the page
from named comparables, with the assumptions visible. Never a single number, never an
unsupported range.

## Step 3 — Differentiation, honestly

Against a larger house, the true differences are: who actually runs the deal, how many
processes that person is running at once, sector depth against balance-sheet reach, and
access to the mid-market buyer that a bulge-bracket team will not call. Say which of these
we are claiming, and evidence it.

Never assert credentials, memberships, league-table positions or transaction experience
that have not been verified. If a credential is needed for the pitch and cannot be
verified, it does not go in the deck.

## Step 4 — Objections and answers

Prepare the five the vendor will actually raise. For each: the objection in their words,
the honest answer, and the evidence.

| Objection | Answer | Evidence |
|---|---|---|
| "You are smaller than the other two." | | |
| "Do you know the US buyers?" | | |
| "Your fee is higher on this basis." | | |
| "Have you done a deal in this sub-sector?" | | |
| "Who is actually doing the work?" | | |

An answer that requires a claim we cannot verify is not an answer. Change the claim.

## Step 5 — Output

- Pitch deck on the Debrett's template — A4 landscape, house palette and type. Build it
  with `pptx-author` and QC it with `ib-check-deck` before it is printed.
- A one-page internal brief for whoever is in the room: the three points to land, the
  five objections, and the two questions we must ask the vendor.

## Guardrails

- No invented multiples, deal values, buyers, advisers or track record.
- Comparable activity is disclosed-terms only. Undisclosed stays undisclosed.
- Every page passes `debretts-verify` before printing.
- Confidentiality: no other client's mandate appears in a pitch, named or describable.
