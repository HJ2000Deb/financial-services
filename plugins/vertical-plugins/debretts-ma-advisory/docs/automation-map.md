# The automation map

Every stage of the deal cycle, what runs it, what triggers it, and what stays with a
person. Read the last column first: it is the reason the rest is safe.

Three levels of automation, and the choice between them is a cost and control decision,
not a capability one:

| Level | What it means | When to use it |
|---|---|---|
| **Chat + skill** | A person asks, the skill supplies the method | Most work, most days. Cheap, fast to steer |
| **Agent** | One instruction, multi-step execution, finished files back | Genuinely multi-step work across documents and systems |
| **Scheduled** | Runs on a cadence or an event, output waits for review | Recurring assembly where lateness is the failure mode |

## Stage 1 — Origination

| Task | Runs as | Trigger | Output | Human holds |
|---|---|---|---|---|
| Sector sweep against Debrett's criteria | `origination-scout` | Monthly, per active sector | Scored shortlist, A/B/C | Which names we call |
| Target dossier before a call | `/dossier` or the agent | On demand, before any call | One page, sourced | The three questions asked |
| Signal watch on Priority B and C names | `origination-scout` | Weekly, event-driven | Change note: filings, directors, funding, acquisitions | Whether a change is a reason to call |
| Outreach drafts and sequence | `/outreach` | After a name is approved | Draft letter + four-touch sequence | **Every send** |
| Approach log maintenance | `origination-scout` | After each wave | Reconciled log | Nothing — but the log is read at pipeline review |

## Stage 2 — Pitch and mandate

| Task | Runs as | Trigger | Output | Human holds |
|---|---|---|---|---|
| Market context and comparable activity | `/pitch` | Pitch instructed | Two pages, disclosed terms only | Which comparables we stand behind |
| Positioning and equity story outline | `/pitch` + `/equity-story` | Pitch instructed | Narrative and shape of process | The valuation range, if one is given |
| Objection handling | `/pitch` | Before the meeting | Five objections, evidenced answers | Every claim about the firm |
| Mandate set-up on signature | `/mandate` | Engagement letter signed | Project, standing instructions, folders, timetable | Confirming no client AI restriction |

## Stage 3 — Preparation

| Task | Runs as | Trigger | Output | Human holds |
|---|---|---|---|---|
| Equity story pillars and counters | `im-drafter` | Data pack loaded | Pillar table, highlights, thin-spots note | Which pillars we market |
| IM drafting, section by section | `im-drafter` | Per section, partner-approved order | Section, source table, `[GAP]` list | Review at every section boundary |
| Financial summary tables and charts | `im-drafter` | After the model is signed off | Native charts, palette-compliant | The model itself |
| Anticipating diligence | `im-drafter` | Rolling, as sections complete | Question list → Q&A pack | Nothing yet — it feeds stage 5 |

## Stage 4 — Marketing

| Task | Runs as | Trigger | Output | Human holds |
|---|---|---|---|---|
| Buyer universe, scored and tiered | `buyer-universe-builder` | Vendor signs off the equity story | Workbook, live formulas, waves | Vendor approves the list |
| Buyer-specific angles | `buyer-universe-builder` | With the universe | One paragraph per Tier 1–2 name | The angle we actually use |
| Teaser, NDA log, process letters, timetable | `buyer-universe-builder` | Marketing launch, and every timetable change | The set, regenerated together | Partner approves wording; anonymity test |
| Approach and NDA log reconciliation | Scheduled | Daily while a wave is live | Exceptions only | Resolving an exception |

## Stage 5 — Diligence and offers

| Task | Runs as | Trigger | Output | Human holds |
|---|---|---|---|---|
| Data room index and gap analysis | `diligence-desk` | Before the room opens | Index + missing/weak/damaging | The disclosure plan on damaging items |
| What a buyer would flag | `diligence-desk` | With the gap analysis | Twenty items, draft answers | Which we pre-empt |
| Q&A pack, anticipated | `diligence-desk` | Room opening | Sixty questions, answers, index refs | Approving the answers |
| Q&A live, drafted and consistency-checked | `diligence-desk` | Per question, daily reconciliation | Draft answer + citation + conflict check | **Every issue to a buyer** |
| Offer comparison | `diligence-desk` | Offers received | Normalised table, terms matrix, three rankings | The recommendation, and the decision |

## Stage 6 — Close and completion

| Task | Runs as | Trigger | Output | Human holds |
|---|---|---|---|---|
| Bid letter review | `diligence-desk` | Letter received | Committed / conditional / silent | The negotiation position |
| Negotiation preparation | `/completion` | Before each session | Grid, trade order, fallbacks | Everything about the trade |
| Plain-English document summaries | `/completion` | Each draft received | Clause-referenced summary | Every legal position, to legal advisers |
| Completion checklist | `/completion` | Exclusivity | Owners, dependencies, blockers | Funds flow verified separately |
| Post-completion debrief | `/completion` | Within 10 working days | Debrief + what to capture as method | Writing it honestly |

## Recurring, across every mandate

| Cadence | Task | Runs as | Output waits for |
|---|---|---|---|
| Monday 07:00 | Pipeline review pack | Scheduled → `debretts-pipeline-review` | The partners' meeting |
| Friday 08:00 | Weekly process update per live mandate | Scheduled → `debretts-process-update` | Partner review before sending |
| Daily while a deadline is live | Q&A log reconciliation, exceptions only | Scheduled → `diligence-desk` | Deal team action |
| Monthly, per sector | Origination sweep | Scheduled → `origination-scout` | The call list |
| After every meeting | Debrief into actions and owners | `/debrief` | Owners to send follow-ups |
| Before every external send | Verification pass | `/verify` | The person whose name is on the work |

Definitions in machine-readable form: [`automations.json`](automations.json).

## What is deliberately not automated

- **Any send.** No outreach, no answer to a buyer, no update to a vendor leaves the firm
  without a person sending it. Drafts land in a compose pane or in `out/`.
- **Commercial judgement.** Whether to approach, what to recommend, what to concede.
- **Legal and tax positions.** Summarised for comprehension, routed to advisers for the
  position.
- **Anything about a person's intentions.** Signals are reasons to call, never facts.
- **The final read.** Every figure, name, date and precedent that leaves the firm is
  verified by the person whose name is on the work. Automation makes that check fast; it
  does not transfer it.

## Where the value actually lands

Not in replacing the work — in removing the first two hours of it: the blank page, the
formatting, the mechanical extraction, the reconciliation nobody wants to do on a Friday.
If someone is editing an output for longer than it would have taken to write, the prompt
was wrong, not the tool.
