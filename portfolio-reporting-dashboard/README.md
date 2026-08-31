# Debrett's Portfolio Reporting

A reporting dashboard through which Debrett's portfolio companies return quarterly
figures, and through which the investment team and the board read them. It covers
the ground the team liked in Standard Metrics — structured metric collection,
per-company tear sheets, cohort benchmarking, chase tracking and a board extract —
in the Debrett's palette and typefaces.

**The data in this build is illustrative.** Every company, figure, ownership stake,
valuation and submission date in `src/data.js` is invented to demonstrate the
interface. None of it is Debrett's portfolio data. A "Sample data" chip is fixed in
the header so nobody mistakes a screenshot for the real thing; remove it by setting
`DATA.meta.isSample` to `false` once a real feed is connected.

## Views

| View | Who it is for | What it does |
|---|---|---|
| Portfolio | Board, investment team | Aggregate revenue, EBITDA, invested and carrying value, reporting status, and the company table behind them |
| Company | Investment team | Tear sheet: trading, cash, runway, headcount, customers, management commentary |
| Benchmarks | Investment team | One company against the cohort on growth and margin, with quartile bands |
| Collection | Whoever chases the returns | On-time record by quarter, the full request grid, and a chase list that drafts the wording |
| Submit a return | The portfolio company | The company's own quarterly return, pre-filled, with variance against the prior quarter and validation before it goes in |
| Board pack | Board | A4 landscape extract — cover, portfolio summary, matters for the board — that prints or saves to PDF |

Filters sit in one row above everything and scope every figure, chart and table
below them.

## Running and building

```
python3 build.py            # bundles src/ into dist/
```

- `dist/debretts-portfolio-reporting.html` — a complete document; open it in any
  browser, no server needed.
- `dist/artifact.html` — the same page as a content-only fragment, for publishing
  as an Artifact.

Both are generated. Edit `src/`, never `dist/`.

```
node test/interaction.mjs   # 18 behavioural checks against the built page
```

Requires Playwright and a Chromium install; the test drives the real page and
covers tooltips, keyboard access, the table twins, the filters, drill-through,
form validation, the theme toggle and horizontal overflow.

## Collecting the data

`collection/` holds the two templates that feed this: the workbook portfolio
companies fill in, and a SharePoint list definition for the returns to land in.
`collection/README.md` carries the field mapping that keeps the workbook, the list
and `src/data.js` in step. There is no importer yet — returns are keyed in by hand
until one is written.

## Connecting real data

`src/data.js` is the only file that holds data. Replace it with a feed from the
system of record, keeping the shape:

```
meta      { isSample, asOf, currentPeriod, dueDate, currency, unit }
periods   string[]                        oldest → newest, quarterly
companies [{ id, name, sector, stage, hq, firstInvestment, ownership,
             invested, carryingValue, boardSeat,
             reporting: { status, submitted },
             commentary,
             series: { revenue, grossProfit, ebitda, cash, headcount, customers } }]
submissions   { [companyId]: ('received'|'late'|'outstanding')[] }
requestedMetrics [{ key, label, unit, help }]
```

All monetary values are £ thousands; each `series` array runs in step with
`periods`. Everything else in the application is derived — trailing twelve months,
year-on-year growth, margins, monthly burn, runway, quartiles and compliance are
all computed in `src/app.js`, so no derived figure has to be supplied or kept in
sync.

Three things are deliberately not wired up, and say so on screen rather than
pretending otherwise: submitting a return, uploading supporting documents, and
sending a chaser (which drafts the wording for you to send yourself).

## Brand

Follows the Debrett's brand standards. The Brand Standards skill was not available
in the session that built this, so the standards were applied from the written
minimums; check the following against the full standard before this goes in front
of anyone outside the firm.

**Two assets need dropping in.** Both are marked in the source and neither has been
drawn or approximated, because the logo and crown mark must never be redrawn,
recoloured or cropped:

- `src/body.html`, `[data-asset="debretts-logo"]` — the rail currently carries a
  text lockup where the logo belongs.
- `src/app.js`, `sheetFooter()`, `[data-asset="crown-mark"]` — the board pack
  footer carries a dashed placeholder in the centre slot.

**Type.** Playfair Display for chart headings, panel subtitles, callouts and
quotes. Albert Sans for view titles, sub-headers, body, labels, table data and
footers, with Arial as the only fallback. Figures — including the large ones — stay
in Albert Sans; a serif on a headline number reads as decoration.

**Page.** The board pack is A4 landscape, 297 × 210mm with 9.5mm margins, and
prints at those dimensions (verified: PDF MediaBox 841.92 × 594.96pt). The footer
runs document title left, crown mark centre, `DEBRETTS.COM / [page]` right, at 10pt
Albert Sans Medium caps. Nothing in the application is 16:9.

**Colour.** Two background colours and no more, in either theme: Off-White
`#F4F3EE` for content planes and Oxford Blue `#16243C` for the rail, the board pack
cover and the dark theme's ground. Panels are separated by hairlines and space
rather than a third fill. Teal `#3E92AC` carries titles and sub-headers; a darker
step `#1B6C84` carries small text and links, where the brand teal would not clear
4.5:1. No gradients, no shadows.

### Chart colour, and where it needed a decision

Two points where the brand standard and legible data visualisation had to be
reconciled. Both are flagged here rather than buried.

**Series colours are steps within the brand hues.** A four-colour palette cannot
carry a multi-series chart: Oxford Blue is too dark to sit on an Off-White plane and
Corn Silk too light, and both fall below the chroma floor at which a colour stops
doing identity work. So each series colour is a lightness-and-chroma step within one
of the three brand hues, not a new hue:

| Slot | Brand hue | Light | Dark |
|---|---|---|---|
| 1 | Teal | `#1B87A4` | `#2CA1C2` |
| 2 | Corn Silk | `#9A731B` | `#B68A2B` |
| 3 | Oxford Blue | `#3961A7` | `#5B86CE` |

These were snapped to pass every gate and validated, not eyeballed. On the adjacent
pairlist that governs lines, bars and stacks, both modes pass the lightness band,
the chroma floor, colour-vision separation (worst pair ΔE 17.7 light, 19.3 dark
against a target of 8), the normal-vision floor (19.7 / 21.6 against a floor of 15)
and 3:1 contrast against their surfaces. Under the harder all-pairs test that
scatter and bubble charts need, teal and the Oxford Blue step collapse — so the
scatter carries **one** series with the selected company emphasised and the cohort
held back in muted ink, rather than a colour per company. Quartile bands are
ordered, so they take a validated single-hue teal ramp.

**Status colour is not in the brand palette, by necessity.** A monitoring dashboard
has to be able to say "this one needs attention", and a red flag cannot be navy.
Four reserved status colours are used — good `#0CA30C`, warning `#FAB219`, serious
`#EC835A`, critical `#D03B3B` — never as fills or backgrounds, only as a small icon
beside a written label, so the meaning never rests on colour alone. This is a
deliberate departure from "no tints outside the palette" and is worth a decision
before rollout; the alternative is escalation that reads only as text.

## Accessibility

- Every chart has a table twin behind a "Show table" toggle, so no value is
  reachable only by hovering.
- Charts respond to keyboard focus with the same readout as hover; the line charts
  step through periods with the arrow keys.
- Hit targets are larger than the marks they cover.
- Status is always an icon plus a written label.
- Both themes are designed, not inverted: the palette is redefined at token level
  for `prefers-color-scheme: dark` and for an explicit `data-theme` stamp, so an
  explicit choice wins over the operating system in both directions.
