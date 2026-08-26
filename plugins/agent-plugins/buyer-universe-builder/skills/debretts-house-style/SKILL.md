---
name: debretts-house-style
description: Debrett's house standards for anything the firm writes — British English, senior-professional register, sterling and UK date conventions, brand rules for decks and documents, and the no-invented-figures rule. Use whenever drafting or reviewing a client-facing or internal document, deck, email or spreadsheet for Debrett's. Triggers on "house style", "Debrett's style", "tone of voice", "brand standards", "does this read like us", "tidy this up for the client".
---

# Debrett's house style

Apply this to every deliverable. It is the difference between output that needs
twenty minutes of rework and output a partner can send.

## Language

- British English. Organisation, analyse, adviser, realise, programme, licence (noun).
- UK dates: `26 AUGUST 2026` in headers and footers, `26 August 2026` in body text. Never MM/DD.
- Sterling by default. Format as `£8.0m`, `£8m EBITDA`, `£125k`, `7.5x EBITDA`. State the currency
  where a figure could be read as another (`€12m`, `US$40m`).
- Firm name: **Debrett's** or **Debrett's advisory team**. Never "Debrett's Advisory".

## Register

Write for a senior professional audience — a partner, a founder, a credit committee.

- Lead with the conclusion. The first sentence carries the answer, not the context.
- Be specific. "EBITDA fell 180bps on mix" beats "margins came under pressure".
- First person plural for the firm: "we", "our view". Address the client as "you" and
  "your business".
- No consultancy filler: no "in today's fast-moving landscape", no "leverage synergies",
  no "unlock value", no "deep dive".
- No superlatives about the firm or the asset unless the evidence is on the page.
- No exclamation marks. No emoji. No rhetorical questions as headings.
- Sentences under 25 words where possible. Paragraphs of three to five sentences.

## Naming the reader

Every document is written for one reader. State which before drafting:

| Reader | What they want | Length |
|---|---|---|
| Partner (internal) | The view, the risk, the recommendation | One page, bullets acceptable |
| Founder / vendor | Plain English, no jargon, what happens next | Two pages, prose |
| Buyer / sponsor | Evidence, numbers, addressable risk | As long as the evidence requires |
| Credit committee | Downside case, covenants, sensitivities | Structured, tabular |

## Figures and evidence

- Never invent a figure, valuation, multiple, buyer, adviser, deal term, client name or
  track record. If it is not in the source material or a connected system, say so.
- Anything not sourced is marked `[UNVERIFIED]` inline, and listed at the end of the
  document under **Open items**. Do not silently estimate.
- Never assert credentials, permissions, memberships or transaction experience that
  have not been verified.
- Flag weak evidence plainly and proportionately: "one comparable transaction, 2023,
  different scale — directional only".

## Brand rules for documents and decks

Full standards live in [reference/brand-standards.md](reference/brand-standards.md). The
minimums that apply to every file:

- A4 landscape, 297 x 210mm, 9.5mm margins. Never 16:9.
- Playfair Display for chart headings, subtitles, callouts and quotes.
- Albert Sans for slide titles, sub-headers, body, labels and footers. Arial is the only
  fallback; never Calibri.
- Oxford Blue `#16243C` and Corn Silk `#E7D3AE` primary. Content pages Off-White
  `#F4F3EE`; covers, dividers and thank-you pages navy. Teal `#3E92AC` for titles and
  sub-headers. Maximum two background colours per document.
- No gradients, no shadows, no tints outside the palette. Never stretch, recolour or
  crop the logo.
- Footer: document title left, crown mark centre, `DEBRETTS.COM / [page]` right, 10pt
  Albert Sans Medium caps.

## Before anything leaves the firm

1. Run the `debretts-verify` pass over every figure, name, date and precedent.
2. Check no internal or confidential detail has carried through — deal codenames on
   external documents, other clients' names, internal fee or pipeline commentary.
3. Confirm the reader named at the top is the reader it is written for.
