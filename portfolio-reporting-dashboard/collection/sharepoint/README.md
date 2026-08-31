# Portfolio Returns — SharePoint list

`portfolio-returns.sitescript.json` creates a list called **Portfolio Returns**, one
item per company per quarter, with the columns the dashboard reads and three views
for working the collection cycle.

**Not tested against a live tenant.** It was written to the site-script schema and
its JSON is valid, but nobody has run it against Debrett's SharePoint. Deploy it to
a test site first and check the columns and views come out as described below.

## Deploying it

In the SharePoint Online Management Shell, signed in as a SharePoint administrator:

```powershell
Connect-SPOService -Url https://<tenant>-admin.sharepoint.com

$script = Get-Content ./portfolio-returns.sitescript.json -Raw
$site = Add-SPOSiteScript -Title "Portfolio Returns" -Content $script `
    -Description "Quarterly returns from Debrett's portfolio companies"

Add-SPOSiteDesign -Title "Portfolio Returns" -WebTemplate 64 `
    -SiteScripts $site.Id -Description "Creates the Portfolio Returns list"
```

Then apply the site design to the site that should hold the list, from **Settings →
Apply a site template**, or with `Invoke-SPOSiteDesign`.

If PowerShell is not available to you, build the list by hand from the table below —
it takes about ten minutes. The **internal name** column is what matters: the
importer reads those, and SharePoint fixes an internal name permanently at creation,
so getting them right first time saves rebuilding the list.

## Columns

| Display name | Internal name | Type | Required | Notes |
|---|---|---|---|---|
| Title | `Title` | Single line of text | yes | Record key — set it to `Company — Period`, e.g. `Example Ltd — 2026 Q2` |
| Company ID | `CompanyId` | Single line of text | yes | Stable short key, lower case, no spaces. Must match the dashboard's `id` |
| Company | `CompanyName` | Single line of text | yes | Name as it appears in the board pack |
| Period | `Period` | Single line of text | yes | Format `2026 Q2` |
| Period end | `PeriodEnd` | Date and time (date only) | yes | Last day of the quarter |
| Revenue (£000) | `Revenue` | Number, 0 dp | yes | |
| Gross profit (£000) | `GrossProfit` | Number, 0 dp | yes | |
| EBITDA (£000) | `EBITDA` | Number, 0 dp | yes | May be negative |
| Cash at period end (£000) | `Cash` | Number, 0 dp | yes | |
| Headcount (FTE) | `Headcount` | Number, 0 dp | yes | |
| Customers | `Customers` | Number, 0 dp | yes | |
| Management commentary | `Commentary` | Multiple lines, plain text | no | Quoted directly in the board pack |
| Status | `SubmissionStatus` | Choice | yes | Draft / Submitted / Accepted / Queried, default Draft |
| Submitted on | `SubmittedOn` | Date and time | no | Date received |
| Source workbook | `SourceWorkbook` | Hyperlink | no | Link to the returned workbook |
| Internal notes | `InternalNotes` | Multiple lines, plain text | no | **Debrett's only** |

## Views

- **All returns** (default) — everything, newest period first, then company.
- **Awaiting review** — Status is Submitted, oldest first. The working queue.
- **Queried** — Status is Queried, with internal notes. What is stuck and why.

## Before any portfolio company touches this list

The list holds every company's figures in one place. Two things must be settled
first, and neither is done by the site script:

1. **Item-level permissions.** In *List settings → Advanced settings*, set **Read
   access** and **Create and Edit access** to *items created by the user*. Without
   this, any company you grant access to reads the whole portfolio.
2. **Internal notes must not be reachable.** Remove `InternalNotes` from every view
   a guest can open, and remember that column-level security in SharePoint is a view
   convention, not a permission boundary — a determined guest can still query the
   field. If the notes are genuinely sensitive, keep them in a separate list that
   guests have no access to at all.

Guest access also needs external sharing enabled for the site and a guest account
per company. That is an administrator decision, not something this template settles.

## Working cycle

1. Company returns the workbook, or fills the list directly if guest access is on.
2. Whoever receives it sets **Status** to Submitted and fills **Submitted on**.
3. Reviewer checks the figures against the definitions, then sets **Accepted**, or
   **Queried** with a note saying what is wrong.
4. The dashboard reads Accepted items only. A Queried item stays out of the board
   pack until it is resolved — which is the point.
