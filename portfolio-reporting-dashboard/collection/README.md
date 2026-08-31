# Collection kit

Two templates: the workbook portfolio companies fill in, and the SharePoint list
their returns land in. Both are shaped to the same six metrics as the dashboard, so
a figure keeps its meaning from the company's spreadsheet through to the board pack.

```
collection/
├── build-template.py                        generates the workbook
├── debretts-quarterly-return-template.xlsx  ← send this to portfolio companies
└── sharepoint/
    ├── portfolio-returns.sitescript.json    ← deploy this to SharePoint
    └── README.md                            deployment and permissions
```

## The workbook

`debretts-quarterly-return-template.xlsx` — five tabs:

| Tab | Purpose |
|---|---|
| Start here | What we need, the three rules, which cells to fill in, a worked example |
| Return | The quarter's figures, with live validation and a "ready to send" status |
| History | Optional back history, for onboarding a company for the first time |
| Definitions | The basis each metric is calculated on — the contract |
| Lists | Hidden; drives the reporting-period dropdown |

It ships blank. It contains no portfolio data and no company names.

**Regenerate it after any change** — edit `build-template.py`, never the `.xlsx`:

```
python3 build-template.py
```

The workbook is generated so the metric definitions, the validation rules and the
cell addresses the importer will read stay in one place.

### Validation

The Return tab checks each figure as it is typed and refuses to say "Ready to send"
until every check passes. It catches: a missing figure, a negative where one is
impossible, gross profit above revenue, EBITDA above gross profit, incomplete
company details, and a missing commentary. Verified by driving the workbook with
five test cases — blank, each rule violated in turn, and a complete valid return.

The Definitions tab matters more than the validation. Eight finance directors will
otherwise mean eight different things by "EBITDA", and no amount of downstream
plumbing fixes that. Agree the basis with each company before their first return.

### A note on the shading

Cells the company fills in are shaded Corn Silk, not the yellow that spreadsheet
convention would use, so the workbook stays inside the Debrett's palette. The
legend on the Start here tab says so explicitly, so the affordance is not lost.
Validation flags are the one exception — they are set in the reserved critical red,
because a warning that does not read as a warning is not a warning.

## Field mapping

The one table that keeps the three artefacts in step. All monetary values are
£ thousands throughout — no conversion happens anywhere in the chain.

| Metric | Workbook cell (Return) | SharePoint internal name | Dashboard `series` key |
|---|---|---|---|
| Revenue | `C14` | `Revenue` | `revenue` |
| Gross profit | `C15` | `GrossProfit` | `grossProfit` |
| EBITDA | `C16` | `EBITDA` | `ebitda` |
| Cash at quarter end | `C17` | `Cash` | `cash` |
| Headcount | `C18` | `Headcount` | `headcount` |
| Customers | `C19` | `Customers` | `customers` |

| Other field | Workbook cell | SharePoint internal name | Dashboard field |
|---|---|---|---|
| Company name | `C5` | `CompanyName` | `name` |
| Reporting period | `C6` | `Period` | matches an entry in `periods` |
| Period end date | `C7` | `PeriodEnd` | — |
| Prepared by | `C8` | — | — |
| Email | `C9` | — | — |
| Date prepared | `C10` | `SubmittedOn` | `reporting.submitted` |
| Management commentary | `A23` | `Commentary` | `commentary` |
| — | — | `CompanyId` | `id` |

`History` tab: one quarter per row from row 5, columns A–G in the order Period,
Revenue, Gross profit, EBITDA, Cash, Headcount, Customers.

Company ID has no home in the workbook by design — a portfolio company should not be
choosing its own key. Whoever files the return sets it, and it must stay stable for
the life of the holding.

## What is not built yet

There is no importer. Nothing yet reads a completed workbook or the SharePoint list
and writes `src/data.js`, so returns still have to be keyed in by hand. That is the
next step, and it is small: the cell addresses and internal names above are fixed
precisely so it can be written against a stable contract.
