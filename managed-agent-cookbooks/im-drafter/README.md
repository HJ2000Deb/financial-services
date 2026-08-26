# IM Drafter — managed-agent template

## Overview

Data pack → equity story → IM, section by section. Same source as the
[`im-drafter`](../../plugins/agent-plugins/im-drafter) Cowork plugin — this directory is the
Managed Agent cookbook for `POST /v1/agents`.

**One section per run.** The orchestrator drafts a section, returns it with its source table
and gap list, and stops. That is a deliberate constraint, not a limitation: one section per
review cycle keeps the corrections cheap, and an IM drafted in one pass reads consistently
and is wrong in six places.

## Deploy

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export MICROSOFT_365_MCP_URL=...
../../scripts/deploy-managed-agent.sh im-drafter
```

## Steering events

See [`steering-examples.json`](./steering-examples.json). Draft the equity story first, then
section 10 (financial review), then the rest in the sequence in the house IM structure.

## Security & handoffs

The split here is about evidence discipline rather than untrusted input. The writer cannot
invent a figure because it never sees the source documents — only the pack reader's typed
facts, each with a basis and a source.

| Leaf | Model | Tools | Connectors |
|---|---|---|---|
| `pack-reader` | Haiku | `Read`, `Grep`, `Glob` | None (reads the mounted deal folder) |
| `story-critic` | Sonnet | `Read`, `Grep` | None |
| **`section-writer`** (Write-holder) | Sonnet | `Read`, `Write`, `Edit`, `Bash` | None |

`story-critic` is an adversarial reader by design: it is prompted to attack the pillar, not
to help. A pillar it kills is cheap; a pillar that dies in week nine of diligence is not.

The orchestrator holds the Microsoft 365 connector to reach the deal folder, and no write
tool. Artefacts land in `./out/im-<section>-<date>.docx` and the supporting workbook.

**Handoff:** once the IM is drafted and the story settled, the orchestrator emits a
`handoff_request` for `buyer-universe-builder` so the universe argues the same story to
named buyers. `scripts/orchestrate.py` routes it.
