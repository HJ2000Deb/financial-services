---
name: debretts-dataroom-index
description: Build the data room index for a sell-side process and run the gap analysis against it — what a buyer will ask for, what is loaded, what is missing, and what a buyer would flag in what is there. Use when opening a data room or preparing for diligence. Triggers on "data room", "VDR index", "gap analysis", "diligence prep", "what will they ask for", "is the data room ready".
---

# Data room index and gap analysis

Two jobs: the index a buyer navigates, and the honest internal view of what is missing or
damaging in it. The second is the valuable one.

## Step 1 — Build the index

Standard structure for a UK mid-market sale. Number it and keep the numbering stable for
the whole process — every Q&A response cites it.

| # | Folder | Typical contents |
|---|---|---|
| 01 | Corporate | Incorporation documents, register, share capital history, group structure, minutes |
| 02 | Financial | Statutory accounts (3 years), management accounts, EBITDA bridge, budget, working capital and capex analysis, banking facilities |
| 03 | Tax | Returns and computations, correspondence, VAT, PAYE, R&D claims, any open enquiry |
| 04 | Commercial | Top customer contracts, standard terms, pricing, pipeline, top supplier contracts |
| 05 | Operations | Sites, leases, plant register, capacity, quality accreditations, IT systems |
| 06 | People | Contracts for senior staff, standard contracts, org chart, pension, benefits, disputes |
| 07 | Legal | Litigation and disputes, insurance, licences and permits, regulatory correspondence |
| 08 | IP and data | Registered IP, licences, software, data protection compliance, breaches |
| 09 | Property | Titles, leases, dilapidations, surveys, environmental |
| 10 | Insurance | Policies, claims history |
| 11 | Management information | KPI packs, board packs, cohort and churn analysis |

## Step 2 — Populate and mark status

| Ref | Document | Status | Owner | Due | Sensitivity |
|---|---|---|---|---|---|
| | | Loaded / Requested / Missing / Redaction needed / Phase 2 only | | | Open / Clean team |

Sensitivity matters: customer names, pricing and employee data are Phase 2 or clean-team,
not open from day one.

## Step 3 — Gap analysis

Three separate lists, and do not merge them:

1. **Missing** — a buyer will ask, we do not have it. Owner and date against each.
2. **Weak** — we have it, and it will not withstand questioning: unaudited management data
   on a load-bearing claim, an adjustment nobody can source, a contract that is unsigned,
   a lease near expiry with no renewal.
3. **Damaging** — we have it, it is true, and it hurts: a concentration, a dispute, a
   customer loss, an environmental issue. For each, the disclosure plan — what we say,
   when, and to whom. Never the option of hoping nobody looks.

## Step 4 — What a buyer would flag, before they do

Read the room as the buyer's diligence provider will, and list the twenty things they will
raise. For each: what they will ask, what the honest answer is, and whether we have the
document to support it. This list is the input to `debretts-qa-pack` and it is where a
process is won or lost — every item answered in advance is a week off the timetable and a
point of leverage kept.

## Output

1. The index, numbered, with status, owner and sensitivity against every line.
2. Three gap lists — missing, weak, damaging — each with an owner and a date.
3. The buyer-flag list of twenty items with draft answers.
4. A readiness line: what must be resolved before the room opens, and what can follow.

## Guardrails

- Internal only. The gap analysis, the weak list and the damaging list never leave the
  firm. Check before any send that includes them.
- Never load a document to an open room that contains employee personal data, customer
  pricing or a third party's confidential information without a redaction pass.
- Redactions are logged: what was redacted, why, and who approved it.
- Nothing is described as complete until the vendor has confirmed it in writing.
