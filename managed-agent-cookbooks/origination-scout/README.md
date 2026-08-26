# Origination Scout — managed-agent template

## Overview

Sector sweep → scored shortlist → dossiers → outreach drafts. Same source as the
[`origination-scout`](../../plugins/agent-plugins/origination-scout) Cowork plugin — this
directory is the Managed Agent cookbook for `POST /v1/agents`.

Designed to run on a schedule: monthly per active sector for a full sweep, weekly for the
signal watch. See
[`automations.json`](../../plugins/vertical-plugins/debretts-ma-advisory/docs/automations.json)
(`origination-sweep`, `signal-watch`).

## Deploy

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export GRATA_MCP_URL=... PITCHBOOK_MCP_URL=... CRM_MCP_URL=...
../../scripts/deploy-managed-agent.sh origination-scout
```

## Steering events

See [`steering-examples.json`](./steering-examples.json). Two modes: `Sweep sector: ...`
for a full screen, `Signal watch: ...` for change detection on names already on the list.
Outreach is only drafted in response to an explicit approval event naming the companies.

## Security & handoffs

Untrusted input is the whole point of this agent: it reads third-party company data and
published news, and the orchestrator never touches either directly. Exactly one worker
holds `Write`, and it holds no connectors — so nothing read from an external source can be
written anywhere it could act.

| Leaf | Model | Tools | Connectors |
|---|---|---|---|
| `screener` | Haiku | `Read`, `Grep` | Grata, PitchBook (read-only) |
| `signal-checker` | Haiku | `Read`, `Grep` | Grata, PitchBook (read-only) |
| **`shortlist-writer`** (Write-holder) | Sonnet | `Read`, `Write`, `Edit` | None |

The orchestrator holds the CRM connector for the exclusion list and relationship history,
and no write tool. Structured `output_schema` on both readers is a containment boundary as
well as a convenience: prose from an external source cannot reach the writer except through
a typed field, and any field the screener could not source arrives as `null` with
`sourced: false`, which the writer renders as `[UNVERIFIED]` rather than as a number.

**No send tool anywhere in this agent.** Outreach lands in `./out/` for a person to send.

**Handoff:** where a sweep surfaces a name the firm should pitch for rather than call, the
orchestrator emits a `handoff_request` for `pitch-agent`; `scripts/orchestrate.py` routes it
as a new steering event. See that script for the allowlist and payload-validation pattern.
