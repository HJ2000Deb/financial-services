"""
UK Pension Salary Sacrifice Model - Builder Part 1
Sheets: ASSUMPTIONS, EMPLOYEE_DATA, TAX_NI_TABLES
"""
import openpyxl
from openpyxl.styles import (
    PatternFill, Font, Alignment, Border, Side, numbers
)
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import DataBarRule, ColorScaleRule, CellIsRule, FormulaRule
from openpyxl.chart import BarChart, Reference, LineChart, PieChart
from openpyxl.chart.series import SeriesLabel
import copy

# ── Palette ────────────────────────────────────────────────────────────────────
NAVY       = "1F3864"
MID_BLUE   = "2E75B6"
LIGHT_BLUE = "BDD7EE"
PALE_BLUE  = "DEEAF1"
GOLD       = "C9A227"
LIGHT_GOLD = "FFF2CC"
GREEN      = "375623"
LIGHT_GREEN= "E2EFDA"
RED        = "C00000"
LIGHT_RED  = "FFE0E0"
WHITE      = "FFFFFF"
GREY_DARK  = "404040"
GREY_MID   = "808080"
GREY_LIGHT = "F2F2F2"
GREY_BORDER= "BFBFBF"

def fill(hex_colour):
    return PatternFill("solid", fgColor=hex_colour)

def font(bold=False, colour=WHITE, size=11, italic=False):
    return Font(bold=bold, color=colour, size=size, italic=italic, name="Calibri")

def border(style="thin", colour=GREY_BORDER):
    s = Side(style=style, color=colour)
    return Border(left=s, right=s, top=s, bottom=s)

def align(h="left", v="center", wrap=False):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)

def thick_bottom(colour=MID_BLUE):
    thick = Side(style="medium", color=colour)
    thin  = Side(style="thin",   color=GREY_BORDER)
    return Border(bottom=thick, left=thin, right=thin, top=thin)

# Named number formats
FMT_GBP    = '£#,##0.00'
FMT_GBP0   = '£#,##0'
FMT_PCT    = '0.00%'
FMT_PCT1   = '0.0%'
FMT_NUM    = '#,##0'
FMT_NUM2   = '#,##0.00'
FMT_TEXT   = '@'

def apply_header(ws, row, col, value, width=None, height=None,
                 bg=NAVY, fg=WHITE, size=11, bold=True, h_align="center"):
    cell = ws.cell(row=row, column=col, value=value)
    cell.fill = fill(bg)
    cell.font = font(bold=bold, colour=fg, size=size)
    cell.alignment = align(h=h_align, v="center", wrap=True)
    cell.border = border()
    if width:
        ws.column_dimensions[get_column_letter(col)].width = width
    if height:
        ws.row_dimensions[row].height = height
    return cell

def apply_input(ws, row, col, value=None, fmt=None, bg=LIGHT_GOLD,
                bold=False, locked=False):
    cell = ws.cell(row=row, column=col, value=value)
    cell.fill = fill(bg)
    cell.font = font(bold=bold, colour=GREY_DARK, size=11)
    cell.alignment = align(h="right", v="center")
    cell.border = border()
    if fmt:
        cell.number_format = fmt
    return cell

def apply_label(ws, row, col, value, bg=PALE_BLUE, bold=False, indent=0):
    cell = ws.cell(row=row, column=col, value=value)
    cell.fill = fill(bg)
    cell.font = font(bold=bold, colour=GREY_DARK, size=11)
    cell.alignment = Alignment(horizontal="left", vertical="center",
                               indent=indent)
    cell.border = border()
    return cell

def apply_formula(ws, row, col, formula, fmt=None, bg=WHITE,
                  bold=False, fg=GREY_DARK):
    cell = ws.cell(row=row, column=col, value=formula)
    cell.fill = fill(bg)
    cell.font = font(bold=bold, colour=fg, size=11)
    cell.alignment = align(h="right", v="center")
    cell.border = border()
    if fmt:
        cell.number_format = fmt
    return cell

def section_title(ws, row, col, text, col_span=1, bg=MID_BLUE, size=12):
    cell = ws.cell(row=row, column=col, value=text)
    cell.fill = fill(bg)
    cell.font = font(bold=True, colour=WHITE, size=size)
    cell.alignment = align(h="left", v="center")
    cell.border = border(style="medium", colour=MID_BLUE)
    ws.row_dimensions[row].height = 22
    if col_span > 1:
        ws.merge_cells(start_row=row, start_column=col,
                       end_row=row, end_column=col+col_span-1)
    return cell

def freeze(ws, cell_ref):
    ws.freeze_panes = cell_ref

def set_col_width(ws, col, width):
    ws.column_dimensions[get_column_letter(col)].width = width

def set_row_height(ws, row, height):
    ws.row_dimensions[row].height = height


# ══════════════════════════════════════════════════════════════════════════════
# SHEET 1 — ASSUMPTIONS
# ══════════════════════════════════════════════════════════════════════════════
def build_assumptions(wb):
    ws = wb.create_sheet("ASSUMPTIONS")
    ws.sheet_view.showGridLines = False
    ws.tab_color = NAVY

    # Column widths
    widths = [2, 32, 20, 20, 20, 20, 2]
    for i, w in enumerate(widths, 1):
        set_col_width(ws, i, w)

    # ── Title banner ──────────────────────────────────────────────────────────
    ws.merge_cells("A1:G1")
    c = ws["A1"]
    c.value = "UK PENSION SALARY SACRIFICE MODEL — ASSUMPTIONS & INPUTS"
    c.fill = fill(NAVY)
    c.font = font(bold=True, colour=WHITE, size=16)
    c.alignment = align(h="center", v="center")
    set_row_height(ws, 1, 40)

    ws.merge_cells("A2:G2")
    c = ws["A2"]
    c.value = "All yellow cells are inputs. Blue cells are calculated. Do not edit grey/white formula cells."
    c.fill = fill(MID_BLUE)
    c.font = font(bold=False, colour=WHITE, size=10, italic=True)
    c.alignment = align(h="center", v="center")
    set_row_height(ws, 2, 18)

    # ── Section A: Tax Year & General ────────────────────────────────────────
    section_title(ws, 4, 2, "A. TAX YEAR & GENERAL SETTINGS", col_span=4)

    rows_A = [
        ("Tax Year",                    "2024/25",    FMT_TEXT,  False),
        ("Payroll Frequency",           "Monthly",    FMT_TEXT,  False),
        ("Number of Pay Periods p.a.",  12,           FMT_NUM,   False),
        ("Company Name",                "Example Co Ltd", FMT_TEXT, False),
        ("Model Version",               "v1.0",       FMT_TEXT,  False),
        ("Model Date",                  "09/05/2026", FMT_TEXT,  False),
    ]
    for i, (label, val, fmt, _) in enumerate(rows_A, 5):
        apply_label(ws, i, 2, label, bg=PALE_BLUE)
        apply_input(ws, i, 3, val, fmt=fmt)
        set_row_height(ws, i, 18)

    # ── Section B: Income Tax Bands ───────────────────────────────────────────
    section_title(ws, 12, 2, "B. INCOME TAX BANDS (England, Wales & NI)", col_span=4)

    hdrs = ["Band", "Lower Limit £", "Upper Limit £", "Rate %"]
    for j, h in enumerate(hdrs, 2):
        apply_header(ws, 13, j, h, bg=MID_BLUE)
    set_row_height(ws, 13, 20)

    tax_bands = [
        ("Personal Allowance",  0,       12570,   0.00),
        ("Basic Rate",          12570,   50270,   0.20),
        ("Higher Rate",         50270,   125140,  0.40),
        ("Additional Rate",     125140,  9999999, 0.45),
        ("PA Taper (£2 per £1 over £100k)", 100000, 125140, "Tapered"),
    ]
    for i, (band, lo, hi, rate) in enumerate(tax_bands, 14):
        apply_input(ws, i, 2, band,  fmt=FMT_TEXT, bg=LIGHT_GOLD)
        apply_input(ws, i, 3, lo,    fmt=FMT_GBP0, bg=LIGHT_GOLD)
        apply_input(ws, i, 4, hi if hi < 9999999 else "Unlimited", fmt=FMT_TEXT, bg=LIGHT_GOLD)
        apply_input(ws, i, 5, rate if isinstance(rate, float) else rate,
                    fmt=FMT_PCT if isinstance(rate, float) else FMT_TEXT,
                    bg=LIGHT_GOLD)
        set_row_height(ws, i, 18)

    # ── Section C: National Insurance (Employee) ──────────────────────────────
    section_title(ws, 21, 2, "C. EMPLOYEE NATIONAL INSURANCE", col_span=4)

    hdrs = ["Band", "Weekly Lower £", "Weekly Upper £", "Rate %"]
    for j, h in enumerate(hdrs, 2):
        apply_header(ws, 22, j, h, bg=MID_BLUE)

    ni_ee_bands = [
        ("Below LEL",          0,      123,    0.00),
        ("LEL to PT",          123,    242,    0.00),
        ("PT to UEL",          242,    967,    0.08),
        ("Above UEL",          967,    999999, 0.02),
    ]
    for i, (band, lo, hi, rate) in enumerate(ni_ee_bands, 23):
        apply_input(ws, i, 2, band, fmt=FMT_TEXT, bg=LIGHT_GOLD)
        apply_input(ws, i, 3, lo,   fmt=FMT_NUM2, bg=LIGHT_GOLD)
        apply_input(ws, i, 4, hi if hi < 999999 else "No limit", fmt=FMT_TEXT, bg=LIGHT_GOLD)
        apply_input(ws, i, 5, rate, fmt=FMT_PCT, bg=LIGHT_GOLD)
        set_row_height(ws, i, 18)

    # ── Section D: Employer NI ────────────────────────────────────────────────
    section_title(ws, 29, 2, "D. EMPLOYER NATIONAL INSURANCE", col_span=4)

    hdrs = ["Band", "Weekly Lower £", "Weekly Upper £", "Rate %"]
    for j, h in enumerate(hdrs, 2):
        apply_header(ws, 30, j, h, bg=MID_BLUE)

    ni_er_bands = [
        ("Below ST",           0,      175,    0.00),
        ("At or above ST",     175,    999999, 0.138),
    ]
    for i, (band, lo, hi, rate) in enumerate(ni_er_bands, 31):
        apply_input(ws, i, 2, band, fmt=FMT_TEXT, bg=LIGHT_GOLD)
        apply_input(ws, i, 3, lo,   fmt=FMT_NUM2, bg=LIGHT_GOLD)
        apply_input(ws, i, 4, hi if hi < 999999 else "No limit", fmt=FMT_TEXT, bg=LIGHT_GOLD)
        apply_input(ws, i, 5, rate, fmt=FMT_PCT, bg=LIGHT_GOLD)
        set_row_height(ws, i, 18)

    # Employment Allowance
    apply_label(ws, 33, 2, "Employment Allowance (£)",    bg=PALE_BLUE)
    apply_input(ws, 33, 3, 5000, fmt=FMT_GBP0)
    apply_label(ws, 34, 2, "Employment Allowance Eligible?", bg=PALE_BLUE)
    apply_input(ws, 34, 3, "Yes", fmt=FMT_TEXT)
    for r in [33, 34]:
        set_row_height(ws, r, 18)

    # ── Section E: Pension Basis ───────────────────────────────────────────────
    section_title(ws, 37, 2, "E. PENSION CONTRIBUTION BASIS", col_span=4)

    apply_label(ws, 38, 2, "Qualifying Earnings Lower Limit £ p.a.", bg=PALE_BLUE)
    apply_input(ws, 38, 3, 6240,  fmt=FMT_GBP0)
    apply_label(ws, 39, 2, "Qualifying Earnings Upper Limit £ p.a.", bg=PALE_BLUE)
    apply_input(ws, 39, 3, 50270, fmt=FMT_GBP0)
    apply_label(ws, 40, 2, "Annual Allowance £",                     bg=PALE_BLUE)
    apply_input(ws, 40, 3, 60000, fmt=FMT_GBP0)
    apply_label(ws, 41, 2, "Money Purchase Annual Allowance £",       bg=PALE_BLUE)
    apply_input(ws, 41, 3, 10000, fmt=FMT_GBP0)
    apply_label(ws, 42, 2, "Lifetime Allowance",                      bg=PALE_BLUE)
    apply_input(ws, 42, 3, "Abolished Apr 2024", fmt=FMT_TEXT)
    for r in range(38, 43):
        set_row_height(ws, r, 18)

    # ── Section F: Default Contribution Rates ─────────────────────────────────
    section_title(ws, 45, 2, "F. DEFAULT CONTRIBUTION RATES", col_span=4)

    apply_label(ws, 46, 2, "Default Employee Contribution Rate",  bg=PALE_BLUE)
    apply_input(ws, 46, 3, 0.05, fmt=FMT_PCT)
    apply_label(ws, 47, 2, "Default Employer Contribution Rate",  bg=PALE_BLUE)
    apply_input(ws, 47, 3, 0.03, fmt=FMT_PCT)
    apply_label(ws, 48, 2, "Pension Calculation Basis",           bg=PALE_BLUE)
    apply_input(ws, 48, 3, "Qualifying Earnings", fmt=FMT_TEXT)
    apply_label(ws, 49, 2, "  (Options: Qualifying Earnings / Full Salary / Full incl. Bonus)", bg=GREY_LIGHT, bold=False)
    for r in range(46, 50):
        set_row_height(ws, r, 18)

    # ── Section G: Employer NI Saving Sharing ─────────────────────────────────
    section_title(ws, 52, 2, "G. EMPLOYER NI SAVING DISPOSITION", col_span=4)

    apply_label(ws, 53, 2, "Employer NI Saving Treatment",           bg=PALE_BLUE)
    apply_input(ws, 53, 3, "Share with Employees", fmt=FMT_TEXT)
    apply_label(ws, 54, 2, "  (Options: Retain / Share / Reinvest in Pension)", bg=GREY_LIGHT)
    apply_label(ws, 55, 2, "% of Saving Shared/Reinvested",          bg=PALE_BLUE)
    apply_input(ws, 55, 3, 0.50, fmt=FMT_PCT)
    apply_label(ws, 56, 2, "Sharing Method",                          bg=PALE_BLUE)
    apply_input(ws, 56, 3, "Pro-rata to Salary", fmt=FMT_TEXT)
    apply_label(ws, 57, 2, "  (Options: Equal Split / Pro-rata to Salary / Pro-rata to Saving)", bg=GREY_LIGHT)
    for r in range(53, 58):
        set_row_height(ws, r, 18)

    # ── Section H: Scenario Selector ──────────────────────────────────────────
    section_title(ws, 60, 2, "H. ACTIVE SCENARIO", col_span=4)

    apply_label(ws, 61, 2, "Active Scenario (1–4)",     bg=PALE_BLUE)
    apply_input(ws, 61, 3, 1, fmt=FMT_NUM)
    apply_label(ws, 62, 2, "Salary Sacrifice: On/Off",  bg=PALE_BLUE)
    apply_input(ws, 62, 3, "On", fmt=FMT_TEXT)
    for r in [61, 62]:
        set_row_height(ws, r, 18)

    # ── Named Ranges note ─────────────────────────────────────────────────────
    ws.merge_cells("B65:F65")
    c = ws["B65"]
    c.value = ("KEY NAMED RANGES  |  TAX_PA=C15  TAX_BR_RATE=E15  TAX_HR_RATE=E16  "
               "TAX_AR_RATE=E17  NI_PT_WK=D24  NI_UEL_WK=D25  NI_EE_MAIN=E25  "
               "NI_EE_UP=E26  NI_ER_ST=D32  NI_ER_RATE=E32  "
               "QE_LO=C38  QE_HI=C39  DEF_EE=C46  DEF_ER=C47  "
               "PENSION_BASIS=C48  NI_TREATMENT=C53  NI_SHARE_PCT=C55")
    c.fill = fill(GREY_LIGHT)
    c.font = font(bold=False, colour=GREY_DARK, size=9, italic=True)
    c.alignment = align(h="left", v="center", wrap=True)
    set_row_height(ws, 65, 40)

    # Define named ranges (stored as strings for documentation; actual defined
    # names are added at workbook level after all sheets exist)
    return ws


# ══════════════════════════════════════════════════════════════════════════════
# SHEET 2 — EMPLOYEE_DATA
# ══════════════════════════════════════════════════════════════════════════════
def build_employee_data(wb):
    ws = wb.create_sheet("EMPLOYEE_DATA")
    ws.sheet_view.showGridLines = False
    ws.tab_color = MID_BLUE

    # Column definitions: (header, width, format)
    columns = [
        ("A",  "Emp ID",                    8,  FMT_TEXT),
        ("B",  "First Name",               14,  FMT_TEXT),
        ("C",  "Last Name",                14,  FMT_TEXT),
        ("D",  "Department",               16,  FMT_TEXT),
        ("E",  "Job Title",                18,  FMT_TEXT),
        ("F",  "Employment Type",          14,  FMT_TEXT),
        ("G",  "Start Date",               12,  'DD/MM/YYYY'),
        ("H",  "Annual Basic Salary £",    18,  FMT_GBP0),
        ("I",  "Annual Bonus £",           16,  FMT_GBP0),
        ("J",  "Total Annual Earnings £",  18,  FMT_GBP0),
        ("K",  "EE Contrib Rate %",        15,  FMT_PCT),
        ("L",  "ER Contrib Rate %",        15,  FMT_PCT),
        ("M",  "Override Rates? Y/N",      16,  FMT_TEXT),
        ("N",  "Sacrifice On? Y/N",        14,  FMT_TEXT),
        ("O",  "Pension Basis Override",   20,  FMT_TEXT),
        ("P",  "NI Category",              12,  FMT_TEXT),
        ("Q",  "Scottish Taxpayer? Y/N",   18,  FMT_TEXT),
        ("R",  "Notes",                    24,  FMT_TEXT),
    ]

    # Banner
    ws.merge_cells(f"A1:{get_column_letter(len(columns))}1")
    c = ws["A1"]
    c.value = "EMPLOYEE DATA — Input Sheet  |  Yellow = editable inputs  |  Blue = auto-calculated"
    c.fill = fill(NAVY)
    c.font = font(bold=True, colour=WHITE, size=13)
    c.alignment = align(h="center", v="center")
    set_row_height(ws, 1, 36)

    # Column headers (row 2)
    for col_idx, (_, header, width, _) in enumerate(columns, 1):
        apply_header(ws, 2, col_idx, header, width=width, height=36, bg=MID_BLUE)
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    freeze(ws, "A3")

    # Sample employees (25 rows)
    employees = [
        # ID, First, Last, Dept, Title, Type, StartDate, Salary, Bonus
        ("E001","Alice","Hartley","Finance","CFO","Full-time","01/04/2020",180000,20000),
        ("E002","James","Patel","Finance","Finance Director","Full-time","15/06/2018",120000,15000),
        ("E003","Priya","Sharma","Finance","Senior Accountant","Full-time","01/09/2021",62000,5000),
        ("E004","Tom","Williams","Finance","Accountant","Full-time","01/03/2023",42000,2000),
        ("E005","Emma","Clarke","Finance","Finance Assistant","Full-time","01/07/2024",28000,0),
        ("E006","David","Johnson","HR","HR Director","Full-time","01/01/2019",95000,10000),
        ("E007","Sarah","Thompson","HR","HR Manager","Full-time","01/04/2020",58000,4000),
        ("E008","Luke","Evans","HR","HR Advisor","Full-time","01/08/2022",38000,1500),
        ("E009","Nina","Roberts","HR","HR Administrator","Part-time","01/11/2023",22000,0),
        ("E010","Ben","Morris","Operations","Operations Director","Full-time","01/06/2017",110000,12000),
        ("E011","Kate","Wilson","Operations","Operations Manager","Full-time","01/02/2019",72000,6000),
        ("E012","Sam","Brown","Operations","Senior Analyst","Full-time","01/05/2021",54000,3500),
        ("E013","Jess","Taylor","Operations","Analyst","Full-time","01/09/2022",40000,2000),
        ("E014","Chris","Anderson","Operations","Analyst","Full-time","01/01/2024",36000,1000),
        ("E015","Fiona","Jackson","Operations","Administrator","Full-time","01/03/2023",30000,0),
        ("E016","Mark","White","Sales","Sales Director","Full-time","01/07/2016",130000,25000),
        ("E017","Amy","Harris","Sales","Senior Account Mgr","Full-time","01/09/2019",70000,15000),
        ("E018","Ryan","Martin","Sales","Account Manager","Full-time","01/04/2021",50000,10000),
        ("E019","Zoe","Garcia","Sales","Account Manager","Full-time","01/11/2022",48000,8000),
        ("E020","Harry","Lee","Sales","Sales Executive","Full-time","01/06/2023",32000,5000),
        ("E021","Lily","Walker","Tech","CTO","Full-time","01/01/2018",160000,18000),
        ("E022","Dan","Hall","Tech","Lead Developer","Full-time","01/03/2020",90000,8000),
        ("E023","Mia","Allen","Tech","Developer","Full-time","01/06/2021",65000,5000),
        ("E024","Joe","Young","Tech","Developer","Full-time","01/09/2022",58000,4000),
        ("E025","Ella","King","Tech","Junior Developer","Full-time","01/01/2025",35000,0),
    ]

    for row_idx, emp in enumerate(employees, 3):
        emp_id, first, last, dept, title, emp_type, start, salary, bonus = emp
        bg_row = PALE_BLUE if row_idx % 2 == 1 else WHITE

        data = [emp_id, first, last, dept, title, emp_type, start, salary, bonus]
        fmts = [FMT_TEXT,FMT_TEXT,FMT_TEXT,FMT_TEXT,FMT_TEXT,
                FMT_TEXT,'DD/MM/YYYY',FMT_GBP0,FMT_GBP0]

        for col_idx, (val, fmt) in enumerate(zip(data, fmts), 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.fill = fill(LIGHT_GOLD)
            cell.font = font(bold=False, colour=GREY_DARK, size=10)
            cell.alignment = align(h="right" if col_idx >= 8 else "left", v="center")
            cell.border = border()
            cell.number_format = fmt

        # Col J: Total Earnings formula
        j_cell = ws.cell(row=row_idx, column=10,
                         value=f"=H{row_idx}+I{row_idx}")
        j_cell.fill = fill(LIGHT_BLUE)
        j_cell.font = font(bold=True, colour=GREY_DARK, size=10)
        j_cell.alignment = align(h="right", v="center")
        j_cell.border = border()
        j_cell.number_format = FMT_GBP0

        # Col K: EE rate (default from ASSUMPTIONS)
        k_cell = ws.cell(row=row_idx, column=11,
                         value=f'=IF(M{row_idx}="Y",K{row_idx},ASSUMPTIONS!$C$46)')
        k_cell.fill = fill(LIGHT_GOLD)
        k_cell.font = font(bold=False, colour=GREY_DARK, size=10)
        k_cell.alignment = align(h="right", v="center")
        k_cell.border = border()
        k_cell.number_format = FMT_PCT
        # Override with actual default
        k_cell.value = 0.05

        # Col L: ER rate
        l_cell = ws.cell(row=row_idx, column=12, value=0.03)
        l_cell.fill = fill(LIGHT_GOLD)
        l_cell.font = font(bold=False, colour=GREY_DARK, size=10)
        l_cell.alignment = align(h="right", v="center")
        l_cell.border = border()
        l_cell.number_format = FMT_PCT

        # Col M: Override?
        m_cell = ws.cell(row=row_idx, column=13, value="N")
        m_cell.fill = fill(LIGHT_GOLD)
        m_cell.font = font(bold=False, colour=GREY_DARK, size=10)
        m_cell.alignment = align(h="center", v="center")
        m_cell.border = border()

        # Col N: Sacrifice on?
        n_cell = ws.cell(row=row_idx, column=14, value="Y")
        n_cell.fill = fill(LIGHT_GOLD)
        n_cell.font = font(bold=False, colour=GREY_DARK, size=10)
        n_cell.alignment = align(h="center", v="center")
        n_cell.border = border()

        # Col O: Pension basis override
        o_cell = ws.cell(row=row_idx, column=15, value="")
        o_cell.fill = fill(LIGHT_GOLD)
        o_cell.font = font(bold=False, colour=GREY_DARK, size=10)
        o_cell.alignment = align(h="center", v="center")
        o_cell.border = border()

        # Col P: NI Category
        p_cell = ws.cell(row=row_idx, column=16, value="A")
        p_cell.fill = fill(LIGHT_GOLD)
        p_cell.font = font(bold=False, colour=GREY_DARK, size=10)
        p_cell.alignment = align(h="center", v="center")
        p_cell.border = border()

        # Col Q: Scottish taxpayer
        q_cell = ws.cell(row=row_idx, column=17, value="N")
        q_cell.fill = fill(LIGHT_GOLD)
        q_cell.font = font(bold=False, colour=GREY_DARK, size=10)
        q_cell.alignment = align(h="center", v="center")
        q_cell.border = border()

        # Col R: Notes
        r_cell = ws.cell(row=row_idx, column=18, value="")
        r_cell.fill = fill(WHITE)
        r_cell.font = font(bold=False, colour=GREY_DARK, size=10)
        r_cell.border = border()

        set_row_height(ws, row_idx, 18)

    # Totals row
    total_row = len(employees) + 3
    ws.merge_cells(f"A{total_row}:G{total_row}")
    c = ws[f"A{total_row}"]
    c.value = "TOTALS"
    c.fill = fill(NAVY)
    c.font = font(bold=True, colour=WHITE, size=11)
    c.alignment = align(h="right", v="center")
    c.border = border()

    for col_idx, fmt in [(8, FMT_GBP0), (9, FMT_GBP0), (10, FMT_GBP0)]:
        col_letter = get_column_letter(col_idx)
        cell = ws.cell(row=total_row, column=col_idx,
                       value=f"=SUM({col_letter}3:{col_letter}{total_row-1})")
        cell.fill = fill(NAVY)
        cell.font = font(bold=True, colour=WHITE, size=11)
        cell.alignment = align(h="right", v="center")
        cell.border = border()
        cell.number_format = fmt

    set_row_height(ws, total_row, 22)

    return ws


# ══════════════════════════════════════════════════════════════════════════════
# SHEET 3 — TAX_NI_TABLES  (lookup helper tables)
# ══════════════════════════════════════════════════════════════════════════════
def build_tax_ni_tables(wb):
    ws = wb.create_sheet("TAX_NI_TABLES")
    ws.sheet_view.showGridLines = False
    ws.tab_color = GREY_MID

    set_col_width(ws, 1, 2)
    set_col_width(ws, 2, 28)
    set_col_width(ws, 3, 18)
    set_col_width(ws, 4, 18)
    set_col_width(ws, 5, 18)

    ws.merge_cells("A1:E1")
    c = ws["A1"]
    c.value = "TAX & NI LOOKUP TABLES — Referenced by Calculation Engine"
    c.fill = fill(NAVY)
    c.font = font(bold=True, colour=WHITE, size=13)
    c.alignment = align(h="center", v="center")
    set_row_height(ws, 1, 36)

    # Annual NI thresholds (from weekly × 52)
    section_title(ws, 3, 2, "ANNUAL NI THRESHOLDS (Weekly × 52)", col_span=3)

    headers = ["Threshold", "Weekly £", "Annual £"]
    for j, h in enumerate(headers, 2):
        apply_header(ws, 4, j, h, bg=MID_BLUE)

    ni_thresholds = [
        ("Lower Earnings Limit (LEL)",      "=ASSUMPTIONS!D23*52",  "=C5*52"),
        ("Primary Threshold (PT)",           "=ASSUMPTIONS!D24*52",  "=C6*52"),
        ("Upper Earnings Limit (UEL)",       "=ASSUMPTIONS!D25*52",  "=C7*52"),
        ("Secondary Threshold (ST)",         "=ASSUMPTIONS!D31*52",  "=C8*52"),
    ]

    # Store actual weekly values
    weekly_vals = [123, 242, 967, 175]
    for i, ((label, wk_f, an_f), wk_v) in enumerate(zip(ni_thresholds, weekly_vals), 5):
        apply_label(ws, i, 2, label, bg=PALE_BLUE)
        c_wk = ws.cell(row=i, column=3, value=wk_v)
        c_wk.fill = fill(LIGHT_BLUE)
        c_wk.font = font(bold=False, colour=GREY_DARK, size=11)
        c_wk.alignment = align(h="right", v="center")
        c_wk.border = border()
        c_wk.number_format = FMT_GBP0

        c_an = ws.cell(row=i, column=4, value=f"=C{i}*52")
        c_an.fill = fill(LIGHT_BLUE)
        c_an.font = font(bold=True, colour=GREY_DARK, size=11)
        c_an.alignment = align(h="right", v="center")
        c_an.border = border()
        c_an.number_format = FMT_GBP0
        set_row_height(ws, i, 18)

    # Tax rate quick reference
    section_title(ws, 11, 2, "INCOME TAX QUICK REFERENCE", col_span=3)
    hdrs = ["Description", "Value", "Source"]
    for j, h in enumerate(hdrs, 2):
        apply_header(ws, 12, j, h, bg=MID_BLUE)

    tax_ref = [
        ("Personal Allowance",         12570, "ASSUMPTIONS!C15"),
        ("Basic Rate (20%)",           0.20,  "ASSUMPTIONS!E15"),
        ("Higher Rate (40%)",          0.40,  "ASSUMPTIONS!E16"),
        ("Additional Rate (45%)",      0.45,  "ASSUMPTIONS!E17"),
        ("HR Threshold (annual)",      50270, "ASSUMPTIONS!C16"),
        ("AR Threshold (annual)",      125140,"ASSUMPTIONS!C17"),
        ("PA Taper Start",             100000,"ASSUMPTIONS!C18"),
    ]
    for i, (desc, val, src) in enumerate(tax_ref, 13):
        apply_label(ws, i, 2, desc, bg=PALE_BLUE)
        c_val = ws.cell(row=i, column=3, value=val)
        c_val.fill = fill(LIGHT_BLUE)
        c_val.font = font(bold=False, colour=GREY_DARK, size=11)
        c_val.alignment = align(h="right", v="center")
        c_val.border = border()
        c_val.number_format = FMT_PCT if isinstance(val, float) and val < 1 else FMT_GBP0

        c_src = ws.cell(row=i, column=4, value=src)
        c_src.fill = fill(GREY_LIGHT)
        c_src.font = font(bold=False, colour=GREY_MID, size=9, italic=True)
        c_src.alignment = align(h="left", v="center")
        c_src.border = border()
        set_row_height(ws, i, 18)

    # NI rate quick reference
    section_title(ws, 22, 2, "NI RATES QUICK REFERENCE", col_span=3)
    hdrs = ["Description", "Rate", "Source"]
    for j, h in enumerate(hdrs, 2):
        apply_header(ws, 23, j, h, bg=MID_BLUE)

    ni_rates_ref = [
        ("EE NI: PT to UEL",           0.08,  "ASSUMPTIONS!E25"),
        ("EE NI: Above UEL",           0.02,  "ASSUMPTIONS!E26"),
        ("ER NI: At/above ST",         0.138, "ASSUMPTIONS!E32"),
        ("PT Annual",                  12570, "=D6"),
        ("UEL Annual",                 50270, "=D7"),
        ("ST Annual",                  9100,  "=D8"),
    ]
    for i, (desc, val, src) in enumerate(ni_rates_ref, 24):
        apply_label(ws, i, 2, desc, bg=PALE_BLUE)
        c_val = ws.cell(row=i, column=3, value=val)
        c_val.fill = fill(LIGHT_BLUE)
        c_val.font = font(bold=False, colour=GREY_DARK, size=11)
        c_val.alignment = align(h="right", v="center")
        c_val.border = border()
        c_val.number_format = FMT_PCT if isinstance(val, float) and val < 1 else FMT_GBP0
        set_row_height(ws, i, 18)

    return ws


if __name__ == "__main__":
    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)

    build_assumptions(wb)
    build_employee_data(wb)
    build_tax_ni_tables(wb)

    out = "/home/user/financial-services/models/pension_salary_sacrifice_model_PART1_TEST.xlsx"
    wb.save(out)
    print(f"Saved: {out}")
