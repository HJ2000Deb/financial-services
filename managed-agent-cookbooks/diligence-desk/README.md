# Diligence Desk — managed-agent template

## Overview

Data room index and gap analysis → Q&A pack → offer comparison → completion. Same source as
the [`diligence-desk`](../../plugins/agent-plugins/diligence-desk) Cowork plugin — this
directory is the Managed Agent cookbook for `POST /v1/agents`.

Highest-consequence agent in the set, and the only one on Opus: the documents are long, the
timetable is tight, and a wrong figure here has consequences a wrong figure in a pitch does
not.

## Deploy

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export MICROSOFT_365_MCP_URL=...
../../scripts/deploy-managed-agent.sh diligence-desk
```

## Steering events

See [`steering-examples.json`](./steering-examples.json). The daily
`Reconcile the Q&A log ... exceptions only` event is the one to schedule while a buyer
deadline is live — a clean day should cost one line of output.

## Security & handoffs

This agent reads the most untrusted input in the firm: information requests written by five
buyers' advisers. `room-reader` is the only worker that touches them, it is prompted to
report rather than act, and its `output_schema` is a typed boundary — a buyer question
cannot reach the writer as prose.

| Leaf | Model | Tools | Connectors |
|---|---|---|---|
| `room-reader` | Haiku | `Read`, `Grep`, `Glob` | None (reads the mounted room) |
| `consistency-checker` | Sonnet | `Read`, `Grep` | None |
| **`pack-writer`** (Write-holder) | Sonnet | `Read`, `Write`, `Edit`, `Bash` | None |

`consistency-checker` is the control that matters most: an answer that contradicts an earlier
one is written into the log as **blocked**, never as an answer, and the deal team decides
which is right. It is cheaper to correct an earlier answer than to defend two.

Internal output — gap analysis, weak and damaging lists, our read on a buyer, the debrief —
is written with an `INTERNAL` filename prefix so it cannot be mistaken for something to send.

**No send tool anywhere in this agent.** Every answer to a buyer and every document to a
vendor is issued by a person. No legal or tax position is produced: document summaries state
on their face that they are for comprehension, and legal questions route to the firm's legal
advisers.

**Handoff:** on completion the orchestrator emits a `handoff_request` for `origination-scout`
carrying the redacted sector learning from the debrief, so the next sweep in that sector is
better informed than the last.
