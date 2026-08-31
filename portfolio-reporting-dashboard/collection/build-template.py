#!/usr/bin/env python3
"""Generate the quarterly return template workbook sent to portfolio companies.

    python3 build-template.py

Writes debretts-quarterly-return-template.xlsx. The workbook is generated rather
than hand-edited so the metric definitions, the validation rules and the cell
addresses the importer reads stay in one place and stay in step.

The template ships blank. It carries no portfolio data, no company names and no
internal commentary — it goes to third parties.
"""

from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

OUT = Path(__file__).resolve().parent / "debretts-quarterly-return-template.xlsx"

# Debrett's palette. Albert Sans will not be installed on a recipient's machine,
# so the workbook is set in Arial — the only permitted fallback.
NAVY = "16243C"
CORN = "E7D3AE"
OFF_WHITE = "F4F3EE"
TEAL = "3E92AC"
CRITICAL = "D03B3B"       # reserved for the validation flags only
FONT = "Arial"

MONEY = "#,##0;(#,##0);-"
WHOLE = "#,##0;(#,##0);-"
DATE = "DD MMMM YYYY"

# The six metrics, in the order the dashboard and the SharePoint list expect.
# (key, label, unit, may_be_negative)
METRICS = [
    ("revenue", "Revenue", "£000", False),
    ("grossProfit", "Gross profit", "£000", False),
    ("ebitda", "EBITDA", "£000", True),
    ("cash", "Cash at quarter end", "£000", False),
    ("headcount", "Headcount", "FTE", False),
    ("customers", "Customers", "count", False),
]

DEFINITIONS = [
    (
        "Revenue", "£000",
        "Revenue recognised in the quarter under your normal accounting policy, "
        "net of discounts, credits and refunds.",
        "All trading revenue, whether invoiced or accrued.",
        "VAT and other sales taxes; grant income; interest; proceeds of disposals; "
        "intercompany trading.",
        "Reporting billings or cash collected rather than revenue recognised.",
    ),
    (
        "Gross profit", "£000",
        "Revenue less the direct cost of delivering it.",
        "Cost of goods, direct delivery staff, hosting and infrastructure "
        "attributable to delivery, third-party licence costs.",
        "Central overhead, sales and marketing, general and administrative costs, "
        "depreciation and amortisation.",
        "Deducting all operating costs, which gives operating profit, not gross profit.",
    ),
    (
        "EBITDA", "£000",
        "Earnings before interest, tax, depreciation and amortisation, and before "
        "exceptional items. Show a loss as a negative figure.",
        "The normal trading result for the quarter.",
        "Interest, tax, depreciation, amortisation, share-based payment charges, "
        "and one-off items.",
        "Netting off an exceptional item silently. Give the figure before exceptionals "
        "and describe the exceptional in the commentary.",
    ),
    (
        "Cash at quarter end", "£000",
        "Cash and cash equivalents held on the last day of the quarter.",
        "Bank balances, money market and instant-access deposits.",
        "Undrawn facilities; restricted cash held for third parties (note it "
        "separately in the commentary); trade receivables.",
        "Reporting average cash for the quarter, or a balance at a date other than "
        "the quarter end.",
    ),
    (
        "Headcount", "FTE",
        "Full-time equivalents on the payroll on the last day of the quarter.",
        "Permanent and fixed-term employees, expressed as full-time equivalents.",
        "Contractors, agency staff and non-executive directors — note these "
        "separately if they are material.",
        "Counting people rather than full-time equivalents, so two half-time staff "
        "read as two.",
    ),
    (
        "Customers", "count",
        "Active paying customers, sites or contracts on the last day of the quarter, "
        "on the basis agreed with us at onboarding.",
        "Whichever unit we agreed — customers, sites, contracts or accounts.",
        "Free trials, lapsed accounts, and separate entities of one group counted "
        "more than once.",
        "Changing the counting basis between quarters. If you must change it, restate "
        "the prior quarter too and say so in the commentary.",
    ),
]


def quarters(start_year: int = 2024, end_year: int = 2030) -> list[str]:
    return [f"{y} Q{q}" for y in range(start_year, end_year + 1) for q in range(1, 5)]


# ----------------------------------------------------------------- styling --

def title_bar(ws, row: int, last_col: int, text: str, sub: str | None = None) -> None:
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    c = ws.cell(row=row, column=1, value=text)
    c.font = Font(name=FONT, size=13, bold=True, color=OFF_WHITE)
    c.fill = PatternFill("solid", fgColor=NAVY)
    c.alignment = Alignment(vertical="center", indent=1)
    ws.row_dimensions[row].height = 30
    if sub:
        ws.merge_cells(start_row=row + 1, start_column=1, end_row=row + 1, end_column=last_col)
        s = ws.cell(row=row + 1, column=1, value=sub)
        s.font = Font(name=FONT, size=9, italic=True, color="4E5B72")
        s.alignment = Alignment(vertical="center", indent=1)
        ws.row_dimensions[row + 1].height = 20


def section(ws, row: int, last_col: int, text: str) -> None:
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    c = ws.cell(row=row, column=1, value=text.upper())
    c.font = Font(name=FONT, size=9, bold=True, color=TEAL)
    c.alignment = Alignment(vertical="center")
    ws.row_dimensions[row].height = 24


def header_row(ws, row: int, labels: list[str]) -> None:
    thin = Side(style="thin", color="B7BCC6")
    for i, label in enumerate(labels, start=1):
        c = ws.cell(row=row, column=i, value=label)
        c.font = Font(name=FONT, size=9, bold=True, color="16243C")
        c.alignment = Alignment(vertical="bottom", wrap_text=True)
        c.border = Border(bottom=thin)


def input_cell(ws, row: int, col: int, number_format: str | None = None) -> None:
    """Corn Silk marks every cell the company fills in. Named in the legend."""
    c = ws.cell(row=row, column=col)
    c.fill = PatternFill("solid", fgColor=CORN)
    c.font = Font(name=FONT, size=11, color=NAVY)
    _edge = Side(style="thin", color="C9B98F")
    c.border = Border(left=_edge, right=_edge, top=_edge, bottom=_edge)
    if number_format:
        c.number_format = number_format
    return c


def body(ws, row: int, col: int, value, *, bold=False, size=10, italic=False, wrap=False, colour=NAVY):
    c = ws.cell(row=row, column=col, value=value)
    c.font = Font(name=FONT, size=size, bold=bold, italic=italic, color=colour)
    c.alignment = Alignment(vertical="top", wrap_text=wrap)
    return c


def print_setup(ws, landscape: bool = True) -> None:
    """Fit each sheet to one page wide so a printed copy stays readable."""
    ws.page_setup.orientation = "landscape" if landscape else "portrait"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_options.horizontalCentered = False
    ws.page_margins.left = ws.page_margins.right = 0.4
    ws.page_margins.top = ws.page_margins.bottom = 0.5


# ------------------------------------------------------------------ sheets --

def sheet_start_here(wb: Workbook) -> None:
    ws = wb.create_sheet("Start here")
    ws.sheet_view.showGridLines = False
    for col, width in zip("ABCDEF", (26, 14, 20, 20, 18, 40)):
        ws.column_dimensions[col].width = width

    title_bar(ws, 1, 6, "Debrett's — quarterly portfolio return",
              "Please complete the Return tab and send the workbook back to us.")

    section(ws, 4, 6, "What we need")
    body(ws, 5, 1, "Six figures and a short commentary, once a quarter.", size=10)
    body(ws, 6, 1, "Returns are due within one month of the quarter end.", size=10)
    body(ws, 7, 1, "If a figure is genuinely not available, tell us why in the commentary "
                   "rather than leaving it blank or estimating it.", size=10, wrap=True)
    ws.merge_cells("A7:F7")
    ws.row_dimensions[7].height = 28

    section(ws, 9, 6, "Three rules")
    rules = [
        "All figures in £000 sterling. If you report in another currency, convert at the "
        "closing rate on the quarter end date and state the rate you used in the commentary.",
        "Show a loss as a negative figure. Do not use brackets or a minus sign in text.",
        "Use the definitions on the Definitions tab. If your accounting policy makes one of "
        "them awkward, tell us — we would rather agree a basis than reconcile later.",
    ]
    r = 10
    for i, rule in enumerate(rules, start=1):
        body(ws, r, 1, str(i), bold=True, size=10, colour=TEAL)
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)
        body(ws, r, 2, rule, size=10, wrap=True)
        ws.row_dimensions[r].height = 30
        r += 1

    section(ws, 14, 6, "Which cells to fill in")
    legend = ws.cell(row=15, column=1)
    legend.fill = PatternFill("solid", fgColor=CORN)
    _edge = Side(style="thin", color="C9B98F")
    legend.border = Border(left=_edge, right=_edge, top=_edge, bottom=_edge)
    ws.merge_cells("B15:F15")
    body(ws, 15, 2, "Cells shaded like this are yours to complete. Everything else is "
                    "calculated or fixed — please do not overwrite it.", size=10, wrap=True)
    ws.row_dimensions[15].height = 26
    ws.merge_cells("A16:F16")
    body(ws, 16, 1, "The Check column on the Return tab tells you whether a figure has been "
                    "accepted. Every row must read OK before you send the workbook back.",
         size=10, wrap=True)
    ws.row_dimensions[16].height = 26

    section(ws, 18, 6, "Worked example")
    ws.merge_cells("A19:F19")
    body(ws, 19, 1, "For a fictional company reporting a quarter in which it turned over "
                    "£1.24m and made a small EBITDA loss:", size=10, italic=True, wrap=True)
    header_row(ws, 20, ["Metric", "Unit", "This quarter", "Prior quarter", "Change", "How it was arrived at"])
    example = [
        ("Revenue", "£000", 1240, 1180, "Invoiced and accrued revenue, net of credits, excluding VAT."),
        ("Gross profit", "£000", 806, 767, "Revenue less hosting, support staff and third-party licences."),
        ("EBITDA", "£000", -95, -140, "Before interest, tax, depreciation, amortisation and exceptionals."),
        ("Cash at quarter end", "£000", 2410, 2530, "Bank and instant-access deposits on the last day."),
        ("Headcount", "FTE", 47, 45, "Payroll FTE at quarter end; excludes three contractors."),
        ("Customers", "count", 312, 298, "Active paying accounts at quarter end."),
    ]
    for i, (metric, unit, now, prior, how) in enumerate(example):
        row = 21 + i
        body(ws, row, 1, metric, size=10)
        body(ws, row, 2, unit, size=9, colour="5F6B7E")
        c = body(ws, row, 3, now, size=10)
        c.number_format = MONEY
        c.alignment = Alignment(horizontal="right")
        p = body(ws, row, 4, prior, size=10, colour="5F6B7E")
        p.number_format = MONEY
        p.alignment = Alignment(horizontal="right")
        d = ws.cell(row=row, column=5, value=f"=C{row}-D{row}")
        d.font = Font(name=FONT, size=10, color="5F6B7E")
        d.number_format = MONEY
        body(ws, row, 6, how, size=9, colour="5F6B7E", wrap=True)
        ws.row_dimensions[row].height = 24

    ws.merge_cells("A28:F28")
    body(ws, 28, 1, "This example is illustrative. The company and the figures are invented.",
         size=9, italic=True, colour="5F6B7E")

    print_setup(ws)

    section(ws, 30, 6, "Returning the workbook")
    ws.merge_cells("A31:F31")
    body(ws, 31, 1, "Send the completed workbook to your usual contact at Debrett's. "
                    "If anything in it is unclear, ask before you estimate.", size=10, wrap=True)
    ws.row_dimensions[31].height = 26


def sheet_return(wb: Workbook) -> None:
    ws = wb.create_sheet("Return")
    ws.sheet_view.showGridLines = False
    for col, width in zip("ABCDEF", (26, 12, 18, 18, 16, 42)):
        ws.column_dimensions[col].width = width

    title_bar(ws, 1, 6, "Quarterly return",
              "Complete the shaded cells. Figures in £000 sterling; show a loss as a negative.")

    # -- company details ---------------------------------------------------
    section(ws, 4, 6, "Company details")
    details = [
        ("Company name", "text"),
        ("Reporting period", "period"),
        ("Period end date", "date"),
        ("Prepared by", "text"),
        ("Email", "text"),
        ("Date prepared", "date"),
    ]
    for i, (label, kind) in enumerate(details):
        row = 5 + i
        body(ws, row, 1, label, size=10)
        ws.merge_cells(start_row=row, start_column=3, end_row=row, end_column=4)
        cell = input_cell(ws, row, 3, DATE if kind == "date" else None)
        # merged range needs the fill applied across both cells to read as one box
        input_cell(ws, row, 4, None)
        ws.row_dimensions[row].height = 20
        if kind == "period":
            cell.number_format = "@"

    # -- figures -----------------------------------------------------------
    section(ws, 12, 6, "Figures for the quarter")
    header_row(ws, 13, ["Metric", "Unit", "This quarter", "Prior quarter",
                        "Change", "Check"])
    ws.row_dimensions[13].height = 30

    first_metric_row = 14
    for i, (_key, label, unit, negative_ok) in enumerate(METRICS):
        row = first_metric_row + i
        body(ws, row, 1, label, size=10)
        body(ws, row, 2, unit, size=9, colour="5F6B7E")
        input_cell(ws, row, 3, MONEY if unit == "£000" else WHOLE)
        prior = ws.cell(row=row, column=4)
        prior.number_format = MONEY if unit == "£000" else WHOLE
        prior.font = Font(name=FONT, size=10, color="5F6B7E")
        change = ws.cell(row=row, column=5, value=f'=IF(OR(C{row}="",D{row}=""),"",C{row}-D{row})')
        change.number_format = MONEY if unit == "£000" else WHOLE
        change.font = Font(name=FONT, size=10, color="5F6B7E")
        ws.row_dimensions[row].height = 20

    r_rev, r_gp, r_eb, r_cash, r_head, r_cust = range(first_metric_row, first_metric_row + 6)

    checks = {
        r_rev: f'=IF(C{r_rev}="","Enter a figure",IF(C{r_rev}<0,"Revenue cannot be negative","OK"))',
        r_gp: (f'=IF(C{r_gp}="","Enter a figure",'
               f'IF(C{r_rev}="","Enter revenue first",'
               f'IF(C{r_gp}>C{r_rev},"Cannot exceed revenue","OK")))'),
        r_eb: (f'=IF(C{r_eb}="","Enter a figure",'
               f'IF(C{r_gp}="","Enter gross profit first",'
               f'IF(C{r_eb}>C{r_gp},"Cannot exceed gross profit","OK")))'),
        r_cash: f'=IF(C{r_cash}="","Enter a figure",IF(C{r_cash}<0,"Cannot be negative","OK"))',
        r_head: f'=IF(C{r_head}="","Enter a figure",IF(C{r_head}<0,"Cannot be negative","OK"))',
        r_cust: f'=IF(C{r_cust}="","Enter a figure",IF(C{r_cust}<0,"Cannot be negative","OK"))',
    }
    for row, formula in checks.items():
        c = ws.cell(row=row, column=6, value=formula)
        c.font = Font(name=FONT, size=10, color="5F6B7E")
        c.alignment = Alignment(vertical="center")

    # Flag a failed check in the reserved critical red — the one place in the
    # workbook where a colour outside the palette carries meaning.
    ws.conditional_formatting.add(
        f"F{r_rev}:F{r_cust}",
        FormulaRule(formula=[f'AND(F{r_rev}<>"OK",F{r_rev}<>"")'],
                    font=Font(name=FONT, size=10, bold=True, color=CRITICAL)),
    )

    # -- commentary --------------------------------------------------------
    section(ws, 21, 6, "Management commentary")
    ws.merge_cells("A22:F22")
    body(ws, 22, 1, "What moved in the quarter, what you expect next quarter, and anything "
                    "the board should know. Three or four sentences is enough — this is "
                    "quoted directly in the board pack.", size=9, italic=True,
         colour="5F6B7E", wrap=True)
    ws.row_dimensions[22].height = 26
    ws.merge_cells("A23:F28")
    comment = ws.cell(row=23, column=1)
    comment.fill = PatternFill("solid", fgColor=CORN)
    comment.alignment = Alignment(vertical="top", wrap_text=True)
    comment.font = Font(name=FONT, size=10, color=NAVY)
    for row in range(23, 29):
        for col in range(1, 7):
            ws.cell(row=row, column=col).fill = PatternFill("solid", fgColor=CORN)
        ws.row_dimensions[row].height = 18

    # -- ready to send -----------------------------------------------------
    section(ws, 30, 6, "Before you send")
    ws.merge_cells("A31:B31")
    body(ws, 31, 1, "Status", bold=True, size=10)
    ws.merge_cells("C31:F31")
    status = ws.cell(row=31, column=3, value=(
        f'=IF(COUNTIF(F{r_rev}:F{r_cust},"OK")<6,'
        f'"Some figures need attention — see the Check column",'
        f'IF(OR(C5="",C6="",C7="",C8=""),'
        f'"Complete the company details above",'
        f'IF(A23="","Add a short management commentary",'
        f'"Ready to send")))'
    ))
    status.font = Font(name=FONT, size=11, bold=True, color=NAVY)
    status.alignment = Alignment(vertical="center", indent=1)
    ws.row_dimensions[31].height = 26
    ws.conditional_formatting.add(
        "C31:F31",
        FormulaRule(formula=['$C$31<>"Ready to send"'],
                    font=Font(name=FONT, size=11, bold=True, color=CRITICAL)),
    )

    # -- validation --------------------------------------------------------
    period_dv = DataValidation(type="list", formula1="Lists!$A$2:$A$29", allow_blank=True,
                               showErrorMessage=True, errorTitle="Reporting period",
                               error="Choose a quarter from the list, for example 2026 Q2.")
    ws.add_data_validation(period_dv)
    period_dv.add(ws["C6"])

    date_dv = DataValidation(type="date", operator="between",
                             formula1="DATE(2020,1,1)", formula2="DATE(2035,12,31)",
                             showErrorMessage=True, errorTitle="Date",
                             error="Enter a date, for example 30 June 2026.")
    ws.add_data_validation(date_dv)
    date_dv.add(ws["C7"])
    date_dv.add(ws["C10"])

    non_negative = DataValidation(type="decimal", operator="greaterThanOrEqual", formula1="0",
                                  showErrorMessage=True, errorTitle="Figure",
                                  error="Enter a number. This metric cannot be negative.")
    ws.add_data_validation(non_negative)
    any_number = DataValidation(type="decimal", operator="between",
                                formula1="-1000000000", formula2="1000000000",
                                showErrorMessage=True, errorTitle="Figure",
                                error="Enter a number. Show a loss as a negative.")
    ws.add_data_validation(any_number)
    for i, (_key, _label, _unit, negative_ok) in enumerate(METRICS):
        target = ws.cell(row=first_metric_row + i, column=3)
        (any_number if negative_ok else non_negative).add(target)

    print_setup(ws)
    ws.freeze_panes = "A14"


def sheet_history(wb: Workbook) -> None:
    ws = wb.create_sheet("History")
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 16
    for col in "BCDEFG":
        ws.column_dimensions[col].width = 18

    title_bar(ws, 1, 7, "History — optional",
              "Complete this only when we first ask you for back history. "
              "Leave it blank on a routine quarterly return.")

    header_row(ws, 4, ["Period", "Revenue (£000)", "Gross profit (£000)", "EBITDA (£000)",
                       "Cash (£000)", "Headcount (FTE)", "Customers"])
    ws.row_dimensions[4].height = 30

    period_dv = DataValidation(type="list", formula1="Lists!$A$2:$A$29", allow_blank=True,
                               showErrorMessage=True, errorTitle="Reporting period",
                               error="Choose a quarter from the list, for example 2026 Q2.")
    ws.add_data_validation(period_dv)

    for row in range(5, 17):
        cell = input_cell(ws, row, 1)
        cell.number_format = "@"
        period_dv.add(cell)
        for col in range(2, 8):
            fmt = MONEY if col <= 5 else WHOLE
            input_cell(ws, row, col, fmt)
        ws.row_dimensions[row].height = 20

    ws.merge_cells("A18:G18")
    body(ws, 18, 1, "One row per quarter, oldest first. Use the same definitions as the "
                    "Return tab; if the basis of a figure changed part-way through, say so "
                    "when you send the workbook back.", size=9, italic=True,
         colour="5F6B7E", wrap=True)
    ws.row_dimensions[18].height = 30
    print_setup(ws)
    ws.freeze_panes = "A5"


def sheet_definitions(wb: Workbook) -> None:
    ws = wb.create_sheet("Definitions")
    ws.sheet_view.showGridLines = False
    for col, width in zip("ABCDEF", (22, 10, 46, 40, 40, 42)):
        ws.column_dimensions[col].width = width

    title_bar(ws, 1, 6, "Definitions",
              "The basis on which we compare companies. Tell us if one of these does not "
              "fit your accounting policy.")

    header_row(ws, 4, ["Metric", "Unit", "Definition", "Include", "Exclude",
                       "The mistake we see most"])
    ws.row_dimensions[4].height = 32

    for i, (metric, unit, definition, include, exclude, mistake) in enumerate(DEFINITIONS):
        row = 5 + i
        body(ws, row, 1, metric, bold=True, size=10, wrap=True)
        body(ws, row, 2, unit, size=9, colour="5F6B7E")
        body(ws, row, 3, definition, size=9, wrap=True)
        body(ws, row, 4, include, size=9, colour="4E5B72", wrap=True)
        body(ws, row, 5, exclude, size=9, colour="4E5B72", wrap=True)
        body(ws, row, 6, mistake, size=9, italic=True, colour="4E5B72", wrap=True)
        ws.row_dimensions[row].height = 62

    section(ws, 12, 6, "Currency")
    ws.merge_cells("A13:F13")
    body(ws, 13, 1, "All figures in £000 sterling. If you report in another currency, convert "
                    "at the closing rate on the quarter end date and state the rate you used "
                    "in the commentary. Do not mix bases between quarters.",
         size=10, wrap=True)
    ws.row_dimensions[13].height = 30

    section(ws, 15, 6, "Changing a basis")
    ws.merge_cells("A16:F16")
    body(ws, 16, 1, "If you need to change how a metric is calculated, restate the prior "
                    "quarter on the same basis and say so. A series that changes basis "
                    "part-way through is worse than no series.", size=10, wrap=True)
    ws.row_dimensions[16].height = 30
    print_setup(ws)
    ws.freeze_panes = "A5"


def sheet_lists(wb: Workbook) -> None:
    ws = wb.create_sheet("Lists")
    ws["A1"] = "Reporting periods"
    ws["A1"].font = Font(name=FONT, size=9, bold=True)
    for i, q in enumerate(quarters(), start=2):
        ws.cell(row=i, column=1, value=q).font = Font(name=FONT, size=10)
    ws.column_dimensions["A"].width = 16
    ws.sheet_state = "hidden"


def main() -> None:
    wb = Workbook()
    wb.remove(wb.active)
    sheet_start_here(wb)
    sheet_return(wb)
    sheet_history(wb)
    sheet_definitions(wb)
    sheet_lists(wb)

    wb.properties.title = "Debrett's quarterly portfolio return"
    wb.properties.creator = "Debrett's"
    wb.properties.description = (
        "Template for portfolio companies to return quarterly figures. Contains no data."
    )
    wb.save(OUT)
    print(f"wrote {OUT.name}  ({OUT.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
