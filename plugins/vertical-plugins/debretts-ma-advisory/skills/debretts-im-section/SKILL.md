---
name: debretts-im-section
description: Draft an information memorandum section by section against the Debrett's IM structure, working only from the data pack, with every figure sourced and every gap flagged. Use for IM and management presentation drafting at preparation stage. Triggers on "IM", "information memorandum", "draft the IM", "IM section", "management presentation", "sell-side document".
---

# IM drafting, section by section

An IM is written one section at a time, from the data pack, against a structure agreed
before drafting starts. Drafting the whole document in one pass produces a document that
reads consistently and is wrong in six places.

The section list, the length of each and what belongs in each is in
[reference/im-structure.md](reference/im-structure.md).

## Before drafting anything

1. Confirm the equity story is settled — `debretts-equity-story`. The IM argues the story;
   it does not discover it.
2. Confirm the data pack is loaded in the mandate Project and current.
3. Confirm the reader: the IM is written for a buyer's deal team, who are technical,
   sceptical and reading eight of these.
4. Agree the section order and page budget with the partner. Write it down.

## Drafting one section

1. **Read the source material for that section only.** Do not carry impressions across
   sections; they are how unsupported claims get in.
2. **List the facts available**, each with basis and source, before writing prose.
3. **Draft to the page budget.** If it will not fit, the section has more than one job —
   split it or cut it, do not compress the type.
4. **Mark every figure** with basis and source in a comment or a footnote, so the
   verification pass can be mechanical.
5. **Flag every gap** as `[GAP: what is missing, who can supply it]` in the draft. Never
   write around a gap with a general statement.
6. **Stop and hand back** for review before starting the next section. One section per
   review cycle keeps the corrections cheap.

## House rules for IM prose

- Buyer's deal team as reader: they want evidence, not persuasion. State, evidence, move.
- Every number is labelled: reported or adjusted, statutory or management, audited or
  unaudited, and its period.
- Charts are native and editable, palette-compliant, with a source line. Never a picture
  of a chart.
- No forward-looking statement in Debrett's voice. Projections are the vendor's, labelled
  as such, with the assumptions stated.
- Consistency: the same figure in the IM, the model and the teaser. Name the workbook cell
  it comes from.
- British English, sterling, house register — `debretts-house-style`.

## Financial section

Build the tables from the model, not by transcription. Every summary table shows: three
historical years plus LTM, the basis of each line, and the bridge from statutory to
adjusted EBITDA with each adjustment named, quantified and reasoned. An adjustment nobody
can explain in one sentence will not survive diligence and should not be in the IM.

## Anticipating the diligence to come

As each section is drafted, keep a running list of the questions that section will
provoke. That list becomes the Q&A pack under `debretts-qa-pack` and the gap analysis
under `debretts-dataroom-index`. Drafting is the cheapest time to notice them.

## Output per section

1. The drafted section, to the page budget, in the house template.
2. A source table: every figure, its basis, its source, the cell or page it came from.
3. `[GAP]` list for that section, with an owner and a date against each.
4. The questions this section will provoke, for the Q&A pack.

## Guardrails

- Nothing enters the IM that is not in the data pack or confirmed by management in
  writing.
- No competitor's confidential information, and no other client's material, ever.
- The IM does not leave the firm until `debretts-verify` has run over the whole document
  and the vendor has approved it in writing.
