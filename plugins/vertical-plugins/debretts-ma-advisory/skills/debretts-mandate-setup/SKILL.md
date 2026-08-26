---
name: debretts-mandate-setup
description: Stand up a new mandate properly — the Project name, the document load list, the standing instructions, the deal folder structure and the timetable skeleton — so nobody has to explain the deal twice. Use at engagement-letter signature or when a mandate has been running out of a blank chat. Triggers on "new mandate", "set up the deal", "kick off Project", "new engagement", "standing instructions".
---

# Mandate set-up

A mandate that lives in a Project is explained once. A mandate that lives in ad-hoc chats
is explained every morning. Ninety minutes here saves the rest of the deal.

## Step 1 — Name the Project

Sector or mandate family first, so the list sorts sensibly:

```
Industrials — Project Kestrel
Business Services — Project Ardent
```

Codenames only in anything that could reach a third party. Record the mapping of codename
to client in the firm's mandate register, not in the Project name.

## Step 2 — Load the documents once

Ask for each of these by name and note which are outstanding:

| Document | Why it matters | Status |
|---|---|---|
| Engagement letter | Scope, fee basis, any client restriction on AI use | |
| Latest statutory accounts (3 years) | The audited base | |
| Management accounts (current YTD) | The live trading picture | |
| Adjusted EBITDA bridge | Every buyer will rebuild this | |
| Customer and revenue analysis | Concentration, churn, contract length | |
| Organisation chart and management CVs | Continuity and gaps | |
| Existing teaser or IM, if any | What has already been said in the market | |
| Process letter and timetable, if live | Deadlines that drive everything else | |
| Data room index, if open | The gap analysis starts here | |

If a client's engagement terms restrict AI use, stop and raise it with Holly before
loading anything.

## Step 3 — Write the standing instructions

Paste the mandate template from
[`docs/standing-instructions/mandate.md`](../../docs/standing-instructions/mandate.md)
and complete every square bracket. It should state:

- Who we are on this deal — sell-side or buy-side, and for whom.
- The reader for most output — usually the partner internally, the vendor externally.
- The deal parameters: sector, size, geography, vendor objectives, constraints.
- House standards: British English, sterling, no invented figures, `[UNVERIFIED]` flags.
- The codename rule and what may not appear in external documents.

## Step 4 — Build the working structure

```
Project Kestrel/
  01-engagement/        engagement letter, KYC, conflicts check
  02-data-pack/         accounts, management accounts, EBITDA bridge
  03-marketing/         teaser, IM, management presentation
  04-buyers/            buyer universe, approach log, NDA log
  05-diligence/         data room index, Q&A log, gap analysis
  06-offers/            indicative offers, comparison, bid letters
  07-completion/        SPA drafts, disclosure, completion checklist
  out/                  everything Claude produces, dated
```

Anything Claude produces lands in `out/` with a date in the filename, and moves into the
numbered folder only when a human has reviewed it.

## Step 5 — Set the timetable and the automations

Draft the timetable working backwards from the vendor's date, then register which
recurring flows apply to this mandate — see
[`docs/automations.json`](../../docs/automations.json). At minimum:

- Weekly process update to the vendor, drafted Friday morning for partner review.
- Q&A log reconciliation the day before each buyer deadline.
- Buyer approach log refreshed after every wave.

## Step 6 — Keep it current

Claude cannot tell which draft is the live one. Remove superseded documents from the
Project the day they are superseded. Stale context produces confidently wrong answers.

## Output

1. The Project name, and the standing instructions ready to paste.
2. The document load list with status against each line.
3. The folder structure created, and the timetable skeleton.
4. A short list of what is missing and who to ask for it.
