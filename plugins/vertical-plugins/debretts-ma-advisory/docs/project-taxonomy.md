# Project taxonomy

A Project holds knowledge: the mandate, the documents, the standing instructions. Load it
once and nobody explains the deal again. Four families, and every conversation should
start inside one of them rather than in a blank chat.

## The four families

### 1. Firm Standards — one, firm-wide, read-only to most

Brand standards, tone of voice, templates, house methodology, the prompt library and the
worked examples. Nobody drafts here; every other Project inherits from it.

Contains: brand standards and template files · tone-of-voice examples · IM, teaser and
process-letter templates · the engagement letter forms · the prompt library · worked
examples of output that stood up in a partner meeting.

Owner: Holly. Changes are additive and announced.

### 2. Sector Knowledge — one per active sector

Market notes, precedent activity, buyer maps and the sector's own vocabulary. This is the
Project that makes the second mandate in a sector faster than the first.

Naming: `Sector — Industrials`, `Sector — Business Services`.

Contains: sector map and sub-sector definitions · precedent transactions with sources and
dates · the standing buyer map, refreshed each mandate · sector-specific screening
criteria · market notes with dates · post-completion debriefs, redacted of client detail.

Owner: the partner who covers the sector. Reviewed quarterly; stale market notes are
removed, not archived in place.

### 3. Live Mandates — one per deal, closed at completion

The data pack, the process documents, the logs, the timetable. Shared with the deal team
and nobody else.

Naming: sector or mandate family first, so the list sorts sensibly —
`Industrials — Project Kestrel`.

Contains: engagement letter · data pack · equity story and IM drafts · buyer universe ·
approach, NDA and Q&A logs · timetable · offers and comparison · completion documents.

Owner: the deal executive. Set up with `/mandate`. Superseded drafts are removed the day
they are superseded — Claude cannot tell which version is live.

At completion: archive the Project, write the debrief, and push what is reusable up into
Sector Knowledge and Firm Standards. A mandate Project that stays open after completion is
a confidentiality risk with no upside.

### 4. BD and Origination — one per sector, or one firm-wide

Target lists, sweep history, outreach history, pitch material. Distinct from Sector
Knowledge: this is our activity, not the market's facts.

Naming: `Origination — Industrials`.

Contains: current screen and its criteria · shortlists with scores and dates · exclusion
list · approach log and outreach history · pitch material and outcomes · the list of names
deliberately excluded, so the next sweep does not rediscover them.

Owner: the origination lead.

## Rules that apply to all four

1. **Name it so it sorts.** Sector or mandate family first, always.
2. **Load documents once.** Re-pasting the same data pack into new conversations is the
   single largest waste of the firm's allowance.
3. **Standing instructions are mandatory.** A Project without them is a folder. Templates:
   [`standing-instructions/`](standing-instructions/).
4. **Keep it current.** Remove superseded drafts. Stale context produces confidently wrong
   answers, which is the expensive kind.
5. **One client per Project.** Never mix two mandates, and never let a debrief that names
   another client sit in a shared Project.
6. **Start fresh when the task changes.** A new task in an old conversation inherits
   confusion and re-reads the whole history every turn.

## What goes where

| Question | Project |
|---|---|
| "How does Debrett's write an IM?" | Firm Standards |
| "What has traded in this sub-sector, and at what?" | Sector Knowledge |
| "What did the buyer ask on Tuesday?" | Live Mandate |
| "Have we approached this company before?" | BD and Origination |
| "What is our house tone for a founder letter?" | Firm Standards |
| "What did we learn on the last deal in this sector?" | Sector Knowledge (debrief, redacted) |
