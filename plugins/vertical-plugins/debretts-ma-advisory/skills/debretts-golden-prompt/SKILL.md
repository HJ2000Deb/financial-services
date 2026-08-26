---
name: debretts-golden-prompt
description: The Debrett's Golden Prompt Framework — turn a vague request into a specific one across Role, Task, Context, Format and Constraints, and turn a prompt used three times into a reusable firm skill. Use when a request is underspecified, when output came back generic, or when someone asks how to prompt something properly. Triggers on "golden prompt", "how should I ask this", "improve my prompt", "the output was generic", "make this a skill".
---

# The Debrett's Golden Prompt Framework

Most disappointing output is a context problem, not a capability problem. Five headings,
ninety seconds to write, in this order.

| # | Heading | What goes in it |
|---|---|---|
| 1 | **Role** | Who Claude should be. "A senior M&A analyst at a UK mid-market advisory firm." |
| 2 | **Task** | The one thing you want done. One verb, one outcome — not a list of five jobs. |
| 3 | **Context** | What it could not know: the mandate, sector, audience, constraints. |
| 4 | **Format** | The shape of the answer: sections, length, table columns, tone. |
| 5 | **Constraints** | What would make it wrong. No invented figures, British English, no superlatives. |

## When someone brings you a weak prompt

1. Ask what the deliverable is, who reads it, and what would make it wrong. Those three
   answers fill four of the five headings.
2. Rewrite it under the five headings, in plain English. Do not add clever phrasing.
3. Show the rewrite before running it, so the author learns the pattern.

## Worked example

**Before** — "Write me something about buyers for this business."

**After**

```
ROLE:        You are a senior M&A analyst at a UK mid-market advisory firm.
TASK:        Build a longlist of 20 credible acquirers for a sell-side mandate.
CONTEXT:     Founder-owned specialist engineering business, £8m EBITDA, UK with
             European customers. Vendor wants management continuity.
FORMAT:      Table — Name | Type | Rationale in two sentences | Priority A, B or C.
CONSTRAINTS: No invented deal history or financials. British English. Flag anything
             uncertain as [UNVERIFIED].
```

The second prompt is not cleverer. It is more specific about the role, the deliverable
and what would make it wrong.

## Five habits that improve any prompt

1. **Name the reader.** A partner, a founder and a credit committee want three different
   documents. Say which.
2. **Give an example.** One paragraph of your own writing teaches house style better than
   any list of adjectives.
3. **Ask it to ask you.** "Before you begin, repeat my request back to me, then ask me
   every question you need answered to do this properly." One extra exchange,
   consistently a better deliverable.
4. **Show the reasoning.** Ask why a buyer is on the list, not merely that it is.
   Reasoning you can check is worth more than an answer you cannot.
5. **Iterate, don't restart.** "Keep the structure, sharpen the rationale in rows four to
   nine" beats a new prompt from scratch.

## Common failures and the one-line fix

| Failure | Fix |
|---|---|
| Vague instruction | State the deliverable, the reader and the length first |
| No context | Attach the document, or work inside the mandate Project that holds it |
| Treating the first answer as final | It is a draft. Say what is wrong and ask again |
| Taking figures at face value | Run `debretts-verify` before it leaves the firm |
| One enormous conversation | Start fresh when the task changes |
| Using it as a search engine | Ask it to search, or use a connector |

## The third repeat

If substantially the same prompt has been written three times, it is a skill waiting to
be built. Capture it:

- **Name** — verb-noun, lower case, hyphenated: `debretts-buyer-universe`.
- **Description** — what it does, when to use it, and the phrases that should trigger it.
- **Workflow** — the numbered steps the author actually follows, including the questions
  they ask before starting.
- **Output** — the exact shape of the deliverable, with the table columns named.
- **Guardrails** — what must never happen, and where a human signs off.

Draft it into `plugins/vertical-plugins/debretts-ma-advisory/skills/<name>/SKILL.md`, run
`python3 scripts/check.py`, and send it to Holly for the firm library.
