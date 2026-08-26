---
name: debretts-process-docs
description: Produce and control the process documents on a sell-side mandate — teaser, NDA log, process letters, timetable and management presentation shell — as one consistent set where a change in one propagates to the others. Use at marketing stage and whenever the timetable moves. Triggers on "teaser", "process letter", "NDA log", "timetable", "process documents", "management presentation".
---

# Process documents

These documents are read against each other by every buyer's adviser. A date in the
process letter that contradicts the timetable is the cheapest possible way to look
disorganised. Treat them as one set with one source of truth.

## The set

| Document | Length | Purpose | Contains |
|---|---|---|---|
| Teaser | 1–2 pages | Anonymous invitation to sign an NDA | Description, investment highlights, size range, process contact |
| NDA log | Table | Who has signed, who has not | Buyer, entity, date sent, date signed, form, version, IM sent |
| Process letter (Phase 1) | 2 pages | Instructions for indicative offers | Deadline, content required, format, contact, reservation of rights |
| Process letter (Phase 2) | 2–3 pages | Instructions for final offers | Deadline, mark-up required, funding evidence, conditions |
| Timetable | 1 page | The dates everything else quotes | Milestones, owners, dependencies |
| Management presentation | 20–30 slides | The story, told by management | Equity story pillars, operational detail, Q&A anticipation |

## Rules that hold across the set

1. **One source of truth for dates.** The timetable. Every other document quotes it;
   nothing states a date independently. When the timetable moves, regenerate the set and
   reissue the ones already out.
2. **One source of truth for figures.** The model. Teaser and IM figures quote the same
   cells.
3. **Anonymity in the teaser.** No company name, no site, no named customer, no figure
   precise enough to identify the business. Test it as a competitor would read it: could
   they name the company in two minutes? If yes, redraft.
4. **Reservation of rights** in every process letter: no obligation to accept any offer,
   right to vary or terminate the process, no reimbursement of costs.
5. **Never a price expectation** in a process letter or a teaser.
6. **Version control.** Every document carries a version and a date in the footer. The NDA
   log records which version each buyer received.

## Teaser drafting

One page of prose plus a highlights panel. Investment highlights come from
`debretts-equity-story`, cut to five lines and de-identified. A size range, not a figure:
"revenue of £20m–£30m", "EBITDA in excess of £5m". Sector described narrowly enough to
attract the right buyer and broadly enough not to identify the company — that tension is
the whole craft of the document, and it is a judgement for the partner.

## NDA log discipline

Reconcile the NDA log against Outlook and the approach log before every process update.
Three things must always agree: who we approached, who signed, who has the IM. When they
disagree, the log is wrong and the process update is wrong with it.

## Timetable

Build backwards from the vendor's date. Show milestone, date, owner, and what it depends
on. Mark the three dates that cannot move. Where a date is driven by a buyer's own
governance (an investment committee, a board), note whose.

## Output

1. Each document in the house template — A4 landscape, house palette and type, footer per
   the brand standard.
2. The set regenerated together, all quoting the current timetable.
3. A change log when the timetable moves: what changed, who has the old version, what has
   to be reissued.

## Guardrails

- The teaser is anonymity-tested by a second person before it goes out.
- No process letter is issued without partner approval of the wording.
- `debretts-verify` runs over the whole set before the first issue and after every
  timetable change.
- Client and buyer names never appear in the wrong document. Check before every send.
