# Debrett's M&A advisory

The firm's house method, as skills, slash commands and connectors. Nineteen skills mapped
to the six stages of the deal cycle, plus the three cross-cutting standards that apply to
everything Debrett's writes.

A Project supplies knowledge — this mandate, these documents, this client. A skill supplies
method — this is how Debrett's builds a buyer universe. Most good work uses both at once.

## Across the deal cycle

| Stage | Skills | Commands |
|---|---|---|
| **1. Origination** | `debretts-sector-screen` · `debretts-target-dossier` · `debretts-outreach` | `/screen` `/dossier` `/outreach` |
| **2. Pitch and mandate** | `debretts-pitch-narrative` · `debretts-mandate-setup` | `/pitch` `/mandate` |
| **3. Preparation** | `debretts-equity-story` · `debretts-im-section` | `/equity-story` `/im` |
| **4. Marketing** | `debretts-buyer-universe` · `debretts-process-docs` | `/buyers` `/process-docs` |
| **5. Diligence and offers** | `debretts-dataroom-index` · `debretts-qa-pack` · `debretts-offer-comparison` | `/dataroom` `/qa` `/offers` |
| **6. Close and completion** | `debretts-completion` | `/completion` |
| **Every week, every mandate** | `debretts-process-update` · `debretts-meeting-debrief` · `debretts-pipeline-review` | `/update` `/debrief` `/pipeline` |
| **Cross-cutting** | `debretts-house-style` · `debretts-verify` · `debretts-golden-prompt` | `/verify` `/prompt` |

The pattern holds throughout: Claude does the assembly, you do the judgement. Most useful
early, where the blank page is the obstacle. Most dangerous late, where a wrong figure has
consequences.

## The three that apply to everything

- **`debretts-house-style`** — British English, senior-professional register, sterling and
  UK dates, and the brand standards for every document, deck and spreadsheet. A4
  landscape, Oxford Blue and Corn Silk, Playfair Display and Albert Sans.
- **`debretts-verify`** — the verification pass. Extracts every figure, name, date and
  precedent from a draft, classifies each as Given, Sourced, Derived or Unverified, and
  flags what cannot be sourced. Ships with `scripts/extract_claims.py`, which reads `.md`,
  `.docx`, `.pptx` and `.xlsx` — and, for workbooks, lists the hardcoded cells with no
  formula behind them.
- **`debretts-golden-prompt`** — Role, Task, Context, Format, Constraints. Also the
  third-repeat rule: a prompt written three times is a skill waiting to be built.

## Team-account operating documents

The plugin is half of the system. The other half is how the team account is set up:

| Document | What it settles |
|---|---|
| [`docs/automation-map.md`](docs/automation-map.md) | Every stage → skill → agent → trigger, and what stays manual |
| [`docs/project-taxonomy.md`](docs/project-taxonomy.md) | The four Project families, naming, and what lives in each |
| [`docs/standing-instructions/`](docs/standing-instructions/) | Standing instructions ready to paste, one per Project family |
| [`docs/model-routing.md`](docs/model-routing.md) | Haiku, Sonnet, Opus — which task goes where, and the usage habits |
| [`docs/connectors-and-governance.md`](docs/connectors-and-governance.md) | Which connectors, who configures them, and the data boundaries |
| [`docs/automations.json`](docs/automations.json) | The scheduled and event-driven flows, machine-readable |
| [`docs/rollout.md`](docs/rollout.md) | 30, 60, 90 days, with an owner against each line |

## Agents

Four named agents run the multi-step work end to end. Each is a self-contained plugin that
bundles the skills above, and each also ships as a managed-agent cookbook:

| Agent | Stage | What it does |
|---|---|---|
| [`origination-scout`](../../agent-plugins/origination-scout) | 1 | Sector sweep → scored shortlist → dossiers → outreach drafts |
| [`im-drafter`](../../agent-plugins/im-drafter) | 3 | Data pack → equity story → IM section by section, with the gap list |
| [`buyer-universe-builder`](../../agent-plugins/buyer-universe-builder) | 4 | Scored buyer universe → buyer angles → process document set |
| [`diligence-desk`](../../agent-plugins/diligence-desk) | 5–6 | Data room index and gaps → Q&A pack → offer comparison → completion |

Reserve agents for genuinely multi-step work. Chat is cheaper, faster to steer, and where
most work should happen most days.

## Connectors

`.mcp.json` declares the servers this vertical expects. **Connectors are configured
centrally, never by individuals.**

| Server | Used for | URL |
|---|---|---|
| `pitchbook` | Sponsors, funds, deals, investors | Published endpoint |
| `grata` | Private company search, financials, buyers, transactions | `${GRATA_MCP_URL}` |
| `microsoft365` | SharePoint, Outlook, Teams — deal folders and correspondence | `${MICROSOFT_365_MCP_URL}` |
| `crm` | Pipeline, relationships, approach history | `${CRM_MCP_URL}` |

The three placeholder URLs are set by whoever provisions the tenancy; they are deliberately
not hardcoded here. A server with no URL simply does not load, and the skills fall back to
asking for the document.

## Personal settings

Copy `.claude/debretts-ma-advisory.local.md.example` to
`.claude/debretts-ma-advisory.local.md` and complete it — your coverage, your default
screen, your live mandates, your exclusions. Gitignored, personal to you, and not a
substitute for the mandate Project.

## Adding a skill

Skills are edited here, in `plugins/vertical-plugins/debretts-ma-advisory/skills/`, and
propagated into the agent bundles:

```bash
python3 scripts/sync-agent-skills.py   # copy into every agent that bundles the skill
python3 scripts/check.py               # lint manifests, resolve references, detect drift
```
