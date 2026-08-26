# Buyer Universe Builder — managed-agent template

## Overview

Scored buyer universe → buyer-specific angles → the process document set. Same source as the
[`buyer-universe-builder`](../../plugins/agent-plugins/buyer-universe-builder) Cowork plugin
— this directory is the Managed Agent cookbook for `POST /v1/agents`.

Two gates are built into the flow: the vendor approves the list before any process document
quotes it, and a partner approves the process-letter wording before it is issued.

## Deploy

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export GRATA_MCP_URL=... PITCHBOOK_MCP_URL=... CRM_MCP_URL=... MICROSOFT_365_MCP_URL=...
../../scripts/deploy-managed-agent.sh buyer-universe-builder
```

## Steering events

See [`steering-examples.json`](./steering-examples.json). The `timetable changed` event is
the one worth wiring to your document store: the whole set regenerates together, and the
agent returns a change log naming who holds a superseded version.

## Security & handoffs

Finding and scoring are separated deliberately. The finder reads third-party data and returns
typed rows; the scorer holds no connectors and cannot go back to the source to fill a gap,
so an unsourced fund size stays unsourced instead of becoming a plausible number.

| Leaf | Model | Tools | Connectors |
|---|---|---|---|
| `buyer-finder` | Haiku | `Read`, `Grep` | Grata, PitchBook (read-only) |
| `scorer` | Sonnet | `Read`, `Grep` | None |
| **`doc-writer`** (Write-holder) | Sonnet | `Read`, `Write`, `Edit`, `Bash` | None |

The orchestrator holds the CRM (relationship history, exclusion list) and Microsoft 365
(deal folder) connectors, and no write tool.

**No send tool anywhere in this agent.** No approach is ever made by the agent: outreach is
drafted with the bundled outreach skill and sent by a person after partner approval.

**Handoff:** once the first wave is out, the orchestrator emits a `handoff_request` for
`diligence-desk` so the data room index and the anticipated Q&A pack exist before the first
buyer asks. `scripts/orchestrate.py` routes it.
