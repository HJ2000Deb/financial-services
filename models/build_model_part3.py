"""
UK Pension Salary Sacrifice Model - Builder Part 3
Sheets: EMPLOYEE_IMPACT, EMPLOYER_ANALYSIS, DEPT_SUMMARY,
        SCENARIO_COMPARISON, AUDIT_CHECKS
"""
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, Reference, LineChart
from openpyxl.chart.series import SeriesLabel

NAVY       = "1F3864"
MID_BLUE   = "2E75B6"
LIGHT_BLUE = "BDD7EE"
PALE_BLUE  = "DEEAF1"
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
ORANGE     = "C55A11"
LIGHT_ORG  = "FCE4D6"

FMT_GBP0  = '£#,##0'
FMT_GBP   = '£#,##0.00'
FMT_PCT   = '0.00%'
FMT_PCT1  = '0.0%'
FMT_NUM   = '#,##0'
FMT_TEXT  = '@'

def fill(h): return PatternFill("solid", fgColor=h)
def fnt(bold=False, colour=WHITE, size=10, italic=False):
    return Font(bold=bold, color=colour, size=size, italic=italic, name="Calibri")
def bdr(style="thin", colour=GREY_BORDER):
    s = Side(style=style, color=colour)
    return Border(left=s, right=s, top=s, bottom=s)
def aln(h="right", v="center", wrap=False):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)

CE = "CALC_ENGINE"   # source sheet
N  = 25              # number of employees
FIRST_ROW = 4        # first data row in CALC_ENGINE

def col(n): return get_column_letter(n)

def banner(ws, text, bg=NAVY, size=13):
    last = col(ws.max_column) if ws.max_column else "Z"
    ws.merge_cells(f"A1:{last}1")
    c = ws["A1"]
    c.value = text
    c.fill = fill(bg)
    c.font = fnt(bold=True, colour=WHITE, size=size)
    c.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 36
    return c

def hdr(ws, r, c_idx, val, bg=MID_BLUE, fg=WHITE, size=10, w=None):
    cell = ws.cell(row=r, column=c_idx, value=val)
    cell.fill = fill(bg)
    cell.font = fnt(bold=True, colour=fg, size=size)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = bdr()
    if w: ws.column_dimensions[col(c_idx)].width = w
    return cell

def lbl(ws, r, c_idx, val, bg=PALE_BLUE, bold=False, h_align="left"):
    cell = ws.cell(row=r, column=c_idx, value=val)
    cell.fill = fill(bg)
    cell.font = fnt(bold=bold, colour=GREY_DARK, size=10)
    cell.alignment = aln(h=h_align, v="center")
    cell.border = bdr()
    return cell

def calc_cell(ws, r, c_idx, formula, fmt=None, bg=WHITE, bold=False):
    cell = ws.cell(row=r, column=c_idx, value=formula)
    cell.fill = fill(bg)
    cell.font = fnt(bold=bold, colour=GREY_DARK, size=10)
    cell.alignment = aln()
    cell.border = bdr()
    if fmt: cell.number_format = fmt
    return cell

def section_hdr(ws, r, c_idx, text, span=1, bg=MID_BLUE):
    cell = ws.cell(row=r, column=c_idx, value=text)
    cell.fill = fill(bg)
    cell.font = fnt(bold=True, colour=WHITE, size=11)
    cell.alignment = aln(h="left")
    cell.border = bdr(style="medium", colour=bg)
    ws.row_dimensions[r].height = 22
    if span > 1:
        ws.merge_cells(start_row=r, start_column=c_idx,
                       end_row=r, end_column=c_idx+span-1)
    return cell

def set_w(ws, c_idx, w):
    ws.column_dimensions[col(c_idx)].width = w

def set_h(ws, r, h):
    ws.row_dimensions[r].height = h


# ══════════════════════════════════════════════════════════════════════════════
# SHEET: EMPLOYEE_IMPACT
# ══════════════════════════════════════════════════════════════════════════════
def build_employee_impact(wb):
    ws = wb.create_sheet("EMPLOYEE_IMPACT")
    ws.sheet_view.showGridLines = False
    ws.tab_color = MID_BLUE
    ws.freeze_panes = "C4"

    # Column widths
    col_defs = [
        (1, "Emp ID",             8),
        (2, "Name",               18),
        (3, "Department",         14),
        (4, "Tax Band (Pre)",     13),
        (5, "Tax Band (Post)",    13),
        (6, "Basic Salary £",     14),
        (7, "Take-Home Pre £",    14),
        (8, "Take-Home Post £",   14),
        (9, "Take-Home Change £", 15),
        (10,"Take-Home Chg %",    14),
        (11,"EE Pension Pre £",   14),
        (12,"EE Pension Post £",  14),
        (13,"EE Pension Change £",15),
        (14,"PAYE Tax Pre £",     13),
        (15,"PAYE Tax Post £",    13),
        (16,"Tax Saving £",       13),
        (17,"EE NI Pre £",        12),
        (18,"EE NI Post £",       12),
        (19,"EE NI Saving £",     13),
        (20,"NI Share from ER £", 14),
        (21,"Total Pension £\n(EE+ER Post)", 16),
        (22,"AA Remaining £",     14),
        (23,"Net Benefit £\n(vs Pre)",       16),
    ]

    ws.merge_cells(f"A1:{col(23)}1")
    c = ws["A1"]
    c.value = "EMPLOYEE IMPACT ANALYSIS — Per Employee View of Salary Sacrifice Benefits"
    c.fill = fill(NAVY)
    c.font = fnt(bold=True, colour=WHITE, size=13)
    c.alignment = Alignment(horizontal="center", vertical="center")
    set_h(ws, 1, 36)

    for c_idx, label, width in col_defs:
        set_w(ws, c_idx, width)
        bg = MID_BLUE
        if c_idx in [9,10,13,16,19,20,23]: bg = GREEN
        hdr(ws, 3, c_idx, label, bg=bg, w=width)
    set_h(ws, 3, 44)

    # ── Data rows referencing CALC_ENGINE ──────────────────────────────────────
    # CALC_ENGINE column mapping:
    # A=1 ID, B=2 Name, C=3 Dept, D=4 Salary, F=6 Total
    # O=15 TaxPre, Z=26 TaxPost, P=16 EENIPre, AA=27 EENIPost
    # Q=17 EEPenPre, AB=28 EEPenPost, R=18 TakeHomePre, AC=29 TakeHomePost
    # AJ=36 THChange, AK=37 THChangePct, AL=38 EEPenChange
    # AG=33 NIShareToEE, AO=41 TotalPension, AP=42 AARem
    # AQ=43 TaxBandPre, AR=44 TaxBandPost

    CE_MAP = {
        "id":         1,   "name":       2,   "dept":       3,
        "salary":     4,   "tax_pre":   15,   "tax_post":  26,
        "ee_ni_pre":  16,  "ee_ni_post":27,   "ee_pen_pre":17,
        "ee_pen_post":28,  "th_pre":    18,   "th_post":   29,
        "th_change":  36,  "th_pct":    37,   "ee_pen_chg":38,
        "ni_share":   33,  "tot_pen":   41,   "aa_rem":    42,
        "tax_band_pre":43, "tax_band_post":44,
    }

    for i in range(N):
        r    = i + 4
        ce_r = FIRST_ROW + i
        bg_row = PALE_BLUE if i % 2 == 0 else WHITE

        def ref(ce_col):
            return f"={CE}!{col(ce_col)}{ce_r}"

        def link(c_idx, ce_col, fmt=None, bold=False):
            cell = ws.cell(row=r, column=c_idx, value=ref(ce_col))
            cell.fill = fill(bg_row)
            cell.font = fnt(bold=bold, colour=GREY_DARK, size=10)
            cell.alignment = aln(h="left" if c_idx <= 3 else "right")
            cell.border = bdr()
            if fmt: cell.number_format = fmt

        def impact(c_idx, ce_col, fmt=None, bold=True):
            cell = ws.cell(row=r, column=c_idx, value=ref(ce_col))
            cell.fill = fill(LIGHT_GREEN if i%2==0 else "D9EFD3")
            cell.font = fnt(bold=bold, colour=GREY_DARK, size=10)
            cell.alignment = aln()
            cell.border = bdr()
            if fmt: cell.number_format = fmt

        link(1, 1, fmt=FMT_TEXT)
        link(2, 2, fmt=FMT_TEXT)
        link(3, 3, fmt=FMT_TEXT)
        link(4, 43, fmt=FMT_TEXT)
        link(5, 44, fmt=FMT_TEXT)
        link(6, 4, fmt=FMT_GBP0)
        link(7, 18, fmt=FMT_GBP0, bold=True)
        link(8, 29, fmt=FMT_GBP0, bold=True)
        impact(9, 36, fmt=FMT_GBP0)
        impact(10, 37, fmt=FMT_PCT1)
        link(11, 17, fmt=FMT_GBP0)
        link(12, 28, fmt=FMT_GBP0)
        impact(13, 38, fmt=FMT_GBP0)
        link(14, 15, fmt=FMT_GBP0)
        link(15, 26, fmt=FMT_GBP0)

        # Tax saving = tax pre - tax post
        cell = ws.cell(row=r, column=16,
                       value=f"={CE}!{col(15)}{ce_r}-{CE}!{col(26)}{ce_r}")
        cell.fill = fill(LIGHT_GREEN if i%2==0 else "D9EFD3")
        cell.font = fnt(bold=True, colour=GREY_DARK, size=10)
        cell.alignment = aln()
        cell.border = bdr()
        cell.number_format = FMT_GBP0

        link(17, 16, fmt=FMT_GBP0)
        link(18, 27, fmt=FMT_GBP0)

        # EE NI saving = NI pre - NI post
        cell = ws.cell(row=r, column=19,
                       value=f"={CE}!{col(16)}{ce_r}-{CE}!{col(27)}{ce_r}")
        cell.fill = fill(LIGHT_GREEN if i%2==0 else "D9EFD3")
        cell.font = fnt(bold=True, colour=GREY_DARK, size=10)
        cell.alignment = aln()
        cell.border = bdr()
        cell.number_format = FMT_GBP0

        impact(20, 33, fmt=FMT_GBP0)
        impact(21, 41, fmt=FMT_GBP0)
        impact(22, 42, fmt=FMT_GBP0)

        # Net benefit = take-home change + EE pension change (additional pension value)
        cell = ws.cell(row=r, column=23,
                       value=f"={CE}!{col(36)}{ce_r}+{CE}!{col(38)}{ce_r}+{CE}!{col(33)}{ce_r}")
        cell.fill = fill(LIGHT_GREEN if i%2==0 else "D9EFD3")
        cell.font = fnt(bold=True, colour=GREEN, size=10)
        cell.alignment = aln()
        cell.border = bdr()
        cell.number_format = FMT_GBP0

        set_h(ws, r, 18)

    # Totals
    tr = N + 4
    ws.merge_cells(f"A{tr}:E{tr}")
    tc = ws[f"A{tr}"]
    tc.value = "COMPANY TOTALS"
    tc.fill = fill(NAVY)
    tc.font = fnt(bold=True, colour=WHITE, size=11)
    tc.alignment = aln(h="center")
    tc.border = bdr(style="medium")

    sum_cols_ei = [6,7,8,9,11,12,13,14,15,16,17,18,19,20,21,23]
    for ci in sum_cols_ei:
        cl = col(ci)
        cell = ws.cell(row=tr, column=ci,
                       value=f"=SUM({cl}4:{cl}{tr-1})")
        cell.fill = fill(NAVY)
        cell.font = fnt(bold=True, colour=WHITE, size=11)
        cell.alignment = aln()
        cell.border = bdr(style="medium")
        cell.number_format = FMT_GBP0

    # Avg % change
    cell = ws.cell(row=tr, column=10,
                   value=f"=IFERROR(I{tr}/G{tr},0)")
    cell.fill = fill(NAVY)
    cell.font = fnt(bold=True, colour=WHITE, size=11)
    cell.alignment = aln()
    cell.border = bdr(style="medium")
    cell.number_format = FMT_PCT1
    set_h(ws, tr, 24)

    return ws


# ══════════════════════════════════════════════════════════════════════════════
# SHEET: EMPLOYER_ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
def build_employer_analysis(wb):
    ws = wb.create_sheet("EMPLOYER_ANALYSIS")
    ws.sheet_view.showGridLines = False
    ws.tab_color = ORANGE

    set_w(ws, 1, 2)
    set_w(ws, 2, 32)
    set_w(ws, 3, 20)
    set_w(ws, 4, 20)
    set_w(ws, 5, 20)
    set_w(ws, 6, 2)

    ws.merge_cells("A1:F1")
    c = ws["A1"]
    c.value = "EMPLOYER COST ANALYSIS — Total Company Impact of Salary Sacrifice"
    c.fill = fill(NAVY)
    c.font = fnt(bold=True, colour=WHITE, size=13)
    c.alignment = Alignment(horizontal="center", vertical="center")
    set_h(ws, 1, 36)

    # ── Key Metrics Summary ────────────────────────────────────────────────────
    section_hdr(ws, 3, 2, "COMPANY-WIDE PAYROLL SUMMARY", span=4, bg=MID_BLUE)

    hdr(ws, 4, 2, "Metric",            bg=NAVY, w=32)
    hdr(ws, 4, 3, "Pre-Sacrifice £",   bg=NAVY, w=20)
    hdr(ws, 4, 4, "Post-Sacrifice £",  bg=NAVY, w=20)
    hdr(ws, 4, 5, "Change £",          bg=NAVY, w=20)
    set_h(ws, 4, 24)

    # Reference the CALC_ENGINE totals row (row 29 = N+4)
    CE_TOTAL = 29  # row in CALC_ENGINE with totals

    metrics = [
        ("Total Gross Payroll",         f"={CE}!D{CE_TOTAL}",  f"={CE}!W{CE_TOTAL}",  ""),
        ("Total PAYE Tax",              f"={CE}!O{CE_TOTAL}",  f"={CE}!Z{CE_TOTAL}",  ""),
        ("Total Employee NI",           f"={CE}!P{CE_TOTAL}",  f"={CE}!AA{CE_TOTAL}", ""),
        ("Total Employee Pension (EE)", f"={CE}!Q{CE_TOTAL}",  f"={CE}!AB{CE_TOTAL}", ""),
        ("Total Employee Take-Home",    f"={CE}!R{CE_TOTAL}",  f"={CE}!AC{CE_TOTAL}", ""),
        ("Total Employer Pension (ER)", f"={CE}!S{CE_TOTAL}",  f"={CE}!AD{CE_TOTAL}", ""),
        ("Total Employer NI",           f"={CE}!T{CE_TOTAL}",  f"={CE}!AE{CE_TOTAL}", ""),
        ("Total Employer Cost",         f"={CE}!U{CE_TOTAL}",  f"={CE}!AI{CE_TOTAL}", ""),
        ("Total ER NI Saving",          "",                     f"={CE}!AF{CE_TOTAL}", ""),
        ("NI Saving Shared to EEs",     "",                     f"={CE}!AG{CE_TOTAL}", ""),
        ("NI Saving Retained/Reinvest", "",                     f"={CE}!AH{CE_TOTAL}", ""),
        ("Total Pension Into Scheme",   f"={CE}!Q{CE_TOTAL}+{CE}!S{CE_TOTAL}",
                                        f"={CE}!AB{CE_TOTAL}+{CE}!AD{CE_TOTAL}", ""),
    ]

    for i, (metric, pre_f, post_f, _) in enumerate(metrics, 5):
        is_key = metric in ["Total Employee Take-Home","Total Employer Cost",
                            "Total ER NI Saving","Total Pension Into Scheme"]
        bg = PALE_BLUE if i % 2 == 0 else WHITE
        bold_row = is_key

        lbl(ws, i, 2, metric, bg=bg if not bold_row else LIGHT_BLUE, bold=bold_row)

        for ci, formula in [(3, pre_f), (4, post_f)]:
            if formula:
                cell = ws.cell(row=i, column=ci, value=formula)
            else:
                cell = ws.cell(row=i, column=ci, value="N/A")
            cell.fill = fill(LIGHT_BLUE if bold_row else bg)
            cell.font = fnt(bold=bold_row, colour=GREY_DARK, size=10)
            cell.alignment = aln()
            cell.border = bdr()
            if formula and formula.startswith("="):
                cell.number_format = FMT_GBP0

        # Change column
        if pre_f and pre_f.startswith("=") and post_f and post_f.startswith("="):
            ch_val = f"=D{i}-C{i}"
        elif post_f and post_f.startswith("=") and not pre_f:
            ch_val = f"=D{i}"
        else:
            ch_val = ""

        ch_cell = ws.cell(row=i, column=5, value=ch_val if ch_val else "")
        ch_cell.fill = fill(LIGHT_GOLD if bold_row else bg)
        ch_cell.font = fnt(bold=bold_row, colour=GREY_DARK, size=10)
        ch_cell.alignment = aln()
        ch_cell.border = bdr()
        if ch_val:
            ch_cell.number_format = FMT_GBP0
        set_h(ws, i, 18)

    # ── ER NI Saving Breakdown ────────────────────────────────────────────────
    section_hdr(ws, 19, 2, "EMPLOYER NI SAVING BREAKDOWN", span=4, bg=ORANGE)

    hdr(ws, 20, 2, "Metric",            bg=NAVY, w=32)
    hdr(ws, 20, 3, "Annual £",          bg=NAVY)
    hdr(ws, 20, 4, "Monthly £",         bg=NAVY)
    hdr(ws, 20, 5, "Per Employee Avg £",bg=NAVY)

    ni_metrics = [
        ("Gross ER NI Saving",         f"={CE}!AF{CE_TOTAL}"),
        ("NI Saving → Employees",      f"={CE}!AG{CE_TOTAL}"),
        ("NI Saving → Retained/Reinvest", f"={CE}!AH{CE_TOTAL}"),
        ("Net ER NI Saving (retained)",f"={CE}!AH{CE_TOTAL}"),
    ]
    for i, (metric, formula) in enumerate(ni_metrics, 21):
        bg = PALE_BLUE if i % 2 == 0 else WHITE
        lbl(ws, i, 2, metric, bg=bg)
        ann = ws.cell(row=i, column=3, value=formula)
        ann.fill = fill(bg); ann.font = fnt(bold=False, colour=GREY_DARK, size=10)
        ann.alignment = aln(); ann.border = bdr(); ann.number_format = FMT_GBP0

        mth = ws.cell(row=i, column=4, value=f"=C{i}/12")
        mth.fill = fill(bg); mth.font = fnt(bold=False, colour=GREY_DARK, size=10)
        mth.alignment = aln(); mth.border = bdr(); mth.number_format = FMT_GBP

        per = ws.cell(row=i, column=5, value=f"=C{i}/{N}")
        per.fill = fill(bg); per.font = fnt(bold=False, colour=GREY_DARK, size=10)
        per.alignment = aln(); per.border = bdr(); per.number_format = FMT_GBP
        set_h(ws, i, 18)

    # ── Employment Allowance ───────────────────────────────────────────────────
    section_hdr(ws, 27, 2, "EMPLOYMENT ALLOWANCE IMPACT", span=4, bg=MID_BLUE)
    ea_rows = [
        ("Employment Allowance Entitlement £", "=ASSUMPTIONS!$C$33"),
        ("ER NI Pre-Sacrifice £",              f"={CE}!T{CE_TOTAL}"),
        ("ER NI Post-Sacrifice £",             f"={CE}!AE{CE_TOTAL}"),
        ("EA Applied (Post) £",                f"=MIN(ASSUMPTIONS!$C$33,{CE}!AE{CE_TOTAL})"),
        ("Net ER NI After EA £",               f"=MAX(0,{CE}!AE{CE_TOTAL}-ASSUMPTIONS!$C$33)"),
    ]
    for i, (metric, formula) in enumerate(ea_rows, 28):
        bg = PALE_BLUE if i % 2 == 0 else WHITE
        lbl(ws, i, 2, metric, bg=bg)
        cell = ws.cell(row=i, column=3, value=formula)
        cell.fill = fill(bg); cell.font = fnt(bold=False, colour=GREY_DARK, size=10)
        cell.alignment = aln(); cell.border = bdr(); cell.number_format = FMT_GBP0
        set_h(ws, i, 18)

    # ── Affordability indicators ──────────────────────────────────────────────
    section_hdr(ws, 35, 2, "AFFORDABILITY METRICS", span=4, bg=MID_BLUE)
    aff_rows = [
        ("Total Employees",                   f"={N}"),
        ("Employees on Sacrifice",            f"=COUNTIF({CE}!K4:K{N+3},\"Yes\")"),
        ("Participation Rate %",              f"=B37/B36"),
        ("ER NI Saving as % of Payroll",      f"={CE}!AF{CE_TOTAL}/{CE}!D{CE_TOTAL}"),
        ("Avg Saving per Participating EE £", f"={CE}!AF{CE_TOTAL}/MAX(1,COUNTIF({CE}!K4:K{N+3},\"Yes\"))"),
        ("Total Pension as % of Payroll",     f"=({CE}!AB{CE_TOTAL}+{CE}!AD{CE_TOTAL})/{CE}!D{CE_TOTAL}"),
    ]
    for i, (metric, formula) in enumerate(aff_rows, 36):
        bg = PALE_BLUE if i % 2 == 0 else WHITE
        lbl(ws, i, 2, metric, bg=bg)
        fmt = FMT_PCT if "%" in metric else (FMT_GBP0 if "£" in metric else FMT_NUM)
        cell = ws.cell(row=i, column=3, value=formula)
        cell.fill = fill(bg); cell.font = fnt(bold=False, colour=GREY_DARK, size=10)
        cell.alignment = aln(); cell.border = bdr(); cell.number_format = fmt
        set_h(ws, i, 18)

    return ws


# ══════════════════════════════════════════════════════════════════════════════
# SHEET: DEPT_SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
def build_dept_summary(wb):
    ws = wb.create_sheet("DEPT_SUMMARY")
    ws.sheet_view.showGridLines = False
    ws.tab_color = "7030A0"

    set_w(ws, 1, 2)
    widths = [16, 12, 16, 16, 16, 16, 16, 16, 16, 16, 2]
    for i, w in enumerate(widths, 2):
        set_w(ws, i, w)

    ws.merge_cells("A1:L1")
    c = ws["A1"]
    c.value = "DEPARTMENT-LEVEL SUMMARY — Salary Sacrifice Impact by Business Unit"
    c.fill = fill(NAVY)
    c.font = fnt(bold=True, colour=WHITE, size=13)
    c.alignment = Alignment(horizontal="center", vertical="center")
    set_h(ws, 1, 36)

    # Column headers
    dept_cols = [
        (2, "Department"),
        (3, "Headcount"),
        (4, "Total Salary £"),
        (5, "Sacrificed £"),
        (6, "EE Pension Post £"),
        (7, "ER Pension Post £"),
        (8, "Total Pension £"),
        (9, "ER NI Saving £"),
        (10,"EE Take-Home Chg £"),
        (11,"ER Cost Change £"),
    ]
    for c_idx, label in dept_cols:
        hdr(ws, 3, c_idx, label, bg=MID_BLUE)
    set_h(ws, 3, 36)

    departments = ["Finance", "HR", "Operations", "Sales", "Tech"]

    # CALC_ENGINE column refs
    # Dept=col3, Salary=col4, Sacrificed=col22, EEPenPost=col28
    # ERPenPost=col30, TotPen=col41, ERNISaving=col32, THChg=col36, ERCostChg=col39

    for i, dept in enumerate(departments):
        r = i + 4
        bg = PALE_BLUE if i % 2 == 0 else WHITE

        dept_ref_range = f"{CE}!C{FIRST_ROW}:{CE}!C{FIRST_ROW+N-1}"

        def sumif(ce_col):
            return (f'=SUMIF({dept_ref_range},'
                    f'"{dept}",'
                    f'{CE}!{col(ce_col)}{FIRST_ROW}:{CE}!{col(ce_col)}{FIRST_ROW+N-1})')

        def countif_dept():
            return f'=COUNTIF({dept_ref_range},"{dept}")'

        lbl(ws, r, 2, dept, bg=bg, bold=True)

        cell = ws.cell(row=r, column=3, value=countif_dept())
        cell.fill = fill(bg); cell.font = fnt(bold=False, colour=GREY_DARK, size=10)
        cell.alignment = aln(); cell.border = bdr(); cell.number_format = FMT_NUM

        for c_idx, ce_col in [(4,4),(5,22),(6,28),(7,30),(8,41),(9,32),(10,36),(11,39)]:
            cell = ws.cell(row=r, column=c_idx, value=sumif(ce_col))
            cell.fill = fill(bg)
            cell.font = fnt(bold=False, colour=GREY_DARK, size=10)
            cell.alignment = aln()
            cell.border = bdr()
            cell.number_format = FMT_GBP0
        set_h(ws, r, 18)

    # Totals
    tr = len(departments) + 4
    tc = ws.cell(row=tr, column=2, value="COMPANY TOTAL")
    tc.fill = fill(NAVY); tc.font = fnt(bold=True, colour=WHITE, size=11)
    tc.alignment = aln(h="center"); tc.border = bdr(style="medium")

    for c_idx in range(3, 12):
        cl = col(c_idx)
        cell = ws.cell(row=tr, column=c_idx,
                       value=f"=SUM({cl}4:{cl}{tr-1})")
        cell.fill = fill(NAVY); cell.font = fnt(bold=True, colour=WHITE, size=11)
        cell.alignment = aln(); cell.border = bdr(style="medium")
        cell.number_format = FMT_GBP0 if c_idx > 3 else FMT_NUM
    set_h(ws, tr, 24)

    return ws


# ══════════════════════════════════════════════════════════════════════════════
# SHEET: SCENARIO_COMPARISON
# ══════════════════════════════════════════════════════════════════════════════
def build_scenario_comparison(wb):
    ws = wb.create_sheet("SCENARIO_COMPARISON")
    ws.sheet_view.showGridLines = False
    ws.tab_color = GOLD = "C9A227"

    set_w(ws, 1, 2)
    set_w(ws, 2, 30)
    for c in range(3, 11):
        set_w(ws, c, 16)

    ws.merge_cells("A1:J1")
    c = ws["A1"]
    c.value = "SCENARIO COMPARISON — Side-by-Side Analysis of 4 Contribution Structures"
    c.fill = fill(NAVY)
    c.font = fnt(bold=True, colour=WHITE, size=13)
    c.alignment = Alignment(horizontal="center", vertical="center")
    set_h(ws, 1, 36)

    # Scenario definitions — user edits rates here
    section_hdr(ws, 3, 2, "SCENARIO DEFINITIONS (Edit EE/ER Rates)", span=8, bg=MID_BLUE)

    hdr(ws, 4, 2, "Parameter",          bg=NAVY)
    scenarios = [
        ("Scenario 1\nBase (5%/3%)",    "5%/3%"),
        ("Scenario 2\nEnhanced (6%/4%)", "6%/4%"),
        ("Scenario 3\nMax SS (10%/5%)", "10%/5%"),
        ("Scenario 4\nNo Sacrifice",     "Non-SS 5%/3%"),
    ]
    sc_colors = [MID_BLUE, GREEN, ORANGE, GREY_MID]
    for j, (label, _) in enumerate(scenarios, 3):
        hdr(ws, 4, j, label, bg=sc_colors[j-3])
    set_h(ws, 4, 44)

    params = [
        ("EE Contribution Rate",    [0.05, 0.06, 0.10, 0.05]),
        ("ER Contribution Rate",    [0.03, 0.04, 0.05, 0.03]),
        ("Salary Sacrifice Active", ["Yes","Yes","Yes","No"]),
        ("Pension Basis",           ["QE","QE","Full Salary","Full Salary"]),
        ("ER NI Saving Treatment",  ["Share","Share","Retain","N/A"]),
        ("NI Share % to Employees", [0.50, 0.50, 0.00, 0.00]),
    ]
    for i, (param, vals) in enumerate(params, 5):
        bg = PALE_BLUE if i % 2 == 0 else WHITE
        lbl(ws, i, 2, param, bg=bg, bold=False)
        for j, val in enumerate(vals, 3):
            fmt = FMT_PCT if isinstance(val, float) and val < 1 else FMT_TEXT
            cell = ws.cell(row=i, column=j, value=val)
            cell.fill = fill("FFF2CC")   # yellow = user input
            cell.font = fnt(bold=False, colour=GREY_DARK, size=10)
            cell.alignment = aln()
            cell.border = bdr()
            cell.number_format = fmt
        set_h(ws, i, 18)

    # Results section — uses CALC_ENGINE totals row as Scenario 1 base,
    # then provides formula stubs showing what each scenario would yield.
    # In a live Excel model, users would copy the CALC_ENGINE tab per scenario;
    # here we provide the structural framework and reference scenario 1 actuals.
    section_hdr(ws, 13, 2, "PROJECTED COMPANY-WIDE OUTCOMES", span=8, bg=NAVY)

    hdr(ws, 14, 2, "Metric",         bg=NAVY)
    for j, (label, _) in enumerate(scenarios, 3):
        hdr(ws, 14, j, label.split("\n")[0], bg=sc_colors[j-3])
    set_h(ws, 14, 28)

    CE_TOTAL = 29  # CALC_ENGINE totals row

    # Scenario 1 = live CALC_ENGINE results
    # Scenarios 2-4 = estimated using scaling factors based on rate changes
    sc_metrics = [
        ("Total Employee Take-Home £",  f"={CE}!R{CE_TOTAL}"),
        ("Total PAYE Tax £",            f"={CE}!O{CE_TOTAL}"),
        ("Total Employee NI £",         f"={CE}!P{CE_TOTAL}"),
        ("Total EE Pension £",          f"={CE}!AB{CE_TOTAL}"),
        ("Total ER Pension £",          f"={CE}!AD{CE_TOTAL}"),
        ("Total Pension to Scheme £",   f"={CE}!AB{CE_TOTAL}+{CE}!AD{CE_TOTAL}"),
        ("Total Employer NI £",         f"={CE}!AE{CE_TOTAL}"),
        ("Total Employer Cost £",       f"={CE}!AI{CE_TOTAL}"),
        ("ER NI Saving £",              f"={CE}!AF{CE_TOTAL}"),
        ("EE Take-Home Change vs Pre £",f"={CE}!AJ{CE_TOTAL}"),
        ("ER Cost Change vs Pre £",     f"={CE}!AM{CE_TOTAL}"),
    ]

    for i, (metric, sc1_formula) in enumerate(sc_metrics, 15):
        bg = PALE_BLUE if i % 2 == 0 else WHITE
        lbl(ws, i, 2, metric, bg=bg, bold=("Total Pension" in metric or
                                            "Employer Cost" in metric or
                                            "Take-Home" in metric))

        # Scenario 1 — live data
        cell = ws.cell(row=i, column=3, value=sc1_formula)
        cell.fill = fill(LIGHT_BLUE)
        cell.font = fnt(bold=True, colour=GREY_DARK, size=10)
        cell.alignment = aln(); cell.border = bdr(); cell.number_format = FMT_GBP0

        # Scenarios 2-4 — placeholder notes (live data requires separate engine tabs)
        notes = [
            "See Sc2 tab\n(copy engine)",
            "See Sc3 tab\n(copy engine)",
            "N/A — No SS",
        ]
        note_fmts = [FMT_GBP0, FMT_GBP0, FMT_GBP0]
        for j, note in enumerate(notes, 4):
            cell = ws.cell(row=i, column=j, value=note)
            cell.fill = fill(GREY_LIGHT)
            cell.font = fnt(bold=False, colour=GREY_MID, size=9, italic=True)
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = bdr()
        set_h(ws, i, 24)

    # ── Scenario notes ─────────────────────────────────────────────────────────
    ws.merge_cells("B28:J28")
    note_c = ws["B28"]
    note_c.value = (
        "USAGE NOTE: To fully populate Scenarios 2-4, duplicate the CALC_ENGINE "
        "sheet, rename it CALC_ENGINE_SC2 etc., then update the EE/ER rates in "
        "ASSUMPTIONS (or override per-employee in EMPLOYEE_DATA) and reference "
        "those totals rows here. The ASSUMPTIONS sheet switches Scenario 1 rates."
    )
    note_c.fill = fill(LIGHT_GOLD)
    note_c.font = fnt(bold=False, colour=GREY_DARK, size=10, italic=True)
    note_c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    note_c.border = bdr()
    set_h(ws, 28, 50)

    return ws


# ══════════════════════════════════════════════════════════════════════════════
# SHEET: AUDIT_CHECKS
# ══════════════════════════════════════════════════════════════════════════════
def build_audit_checks(wb):
    ws = wb.create_sheet("AUDIT_CHECKS")
    ws.sheet_view.showGridLines = False
    ws.tab_color = RED

    set_w(ws, 1, 2)
    set_w(ws, 2, 36)
    set_w(ws, 3, 20)
    set_w(ws, 4, 20)
    set_w(ws, 5, 20)
    set_w(ws, 6, 2)

    ws.merge_cells("A1:F1")
    c = ws["A1"]
    c.value = "AUDIT & ERROR CHECKS — Model Integrity Validation"
    c.fill = fill(RED)
    c.font = fnt(bold=True, colour=WHITE, size=13)
    c.alignment = Alignment(horizontal="center", vertical="center")
    set_h(ws, 1, 36)

    section_hdr(ws, 3, 2, "STRUCTURAL CHECKS", span=4, bg=MID_BLUE)
    hdr(ws, 4, 2, "Check", bg=NAVY, w=36)
    hdr(ws, 4, 3, "Result", bg=NAVY, w=20)
    hdr(ws, 4, 4, "Expected", bg=NAVY, w=20)
    hdr(ws, 4, 5, "Status", bg=NAVY, w=20)
    set_h(ws, 4, 24)

    CE_TOTAL = 29

    checks = [
        ("Employee count in CALC_ENGINE",
         f"=COUNTA({CE}!A4:A{FIRST_ROW+N-1})",
         N,
         f'=IF(C5=D5,"✓ PASS","✗ FAIL")'),
        ("Total EE Pension Pre ≥ 0",
         f"={CE}!Q{CE_TOTAL}",
         ">= 0",
         f'=IF(C6>=0,"✓ PASS","✗ FAIL")'),
        ("Total ER NI Saving ≥ 0",
         f"={CE}!AF{CE_TOTAL}",
         ">= 0",
         f'=IF(C7>=0,"✓ PASS","✗ FAIL")'),
        ("Post-sac take-home ≥ pre for all EEs (check count)",
         f"=COUNTIF({CE}!AJ4:AJ{FIRST_ROW+N-1},\">=0\")",
         N,
         f'=IF(C8=D8,"✓ All EEs better off","⚠ Some EEs worse off")'),
        ("Annual Allowance breaches (count)",
         f"=COUNTIF({CE}!AP4:AP{FIRST_ROW+N-1},\"<0\")",
         0,
         f'=IF(C9=0,"✓ No AA breaches","✗ " & C9 & " AA breach(es)")'),
        ("Sacrifice > Salary (count)",
         f"=SUMPRODUCT(({CE}!V4:V{FIRST_ROW+N-1}>{CE}!D4:D{FIRST_ROW+N-1})*1)",
         0,
         f'=IF(C10=0,"✓ PASS","✗ " & C10 & " employee(s) over-sacrificed")'),
        ("Negative take-home (count)",
         f"=COUNTIF({CE}!AC4:AC{FIRST_ROW+N-1},\"<0\")",
         0,
         f'=IF(C11=0,"✓ PASS","✗ " & C11 & " negative take-home(s)")'),
        ("ER Pension ≥ EE Pension legally (informational)",
         f"={CE}!AD{CE_TOTAL}",
         "Info only",
         f'"See note"'),
        ("Post-sac gross = pre gross - sacrifice (total check)",
         f"=ROUND({CE}!W{CE_TOTAL}-({CE}!L{CE_TOTAL}-{CE}!V{CE_TOTAL}),0)",
         0,
         f'=IF(ABS(C13)<1,"✓ PASS","✗ Rounding error: "&C13)'),
        ("EE NI saving is positive (all SS)",
         f"=SUMPRODUCT(({CE}!K4:K{FIRST_ROW+N-1}=\"Yes\")*({CE}!P4:P{FIRST_ROW+N-1}-{CE}!AA4:AA{FIRST_ROW+N-1}>=-1)*1)",
         f"=COUNTIF({CE}!K4:K{FIRST_ROW+N-1},\"Yes\")",
         f'=IF(C14=D14,"✓ PASS","⚠ Check EE NI calcs")'),
    ]

    for i, (check, result, expected, status) in enumerate(checks, 5):
        bg = PALE_BLUE if i % 2 == 0 else WHITE
        lbl(ws, i, 2, check, bg=bg)

        r_cell = ws.cell(row=i, column=3, value=result)
        r_cell.fill = fill(bg)
        r_cell.font = fnt(bold=False, colour=GREY_DARK, size=10)
        r_cell.alignment = aln()
        r_cell.border = bdr()
        if isinstance(result, str) and result.startswith("="):
            r_cell.number_format = FMT_NUM if "COUNT" in result.upper() else FMT_GBP0

        e_cell = ws.cell(row=i, column=4, value=expected)
        e_cell.fill = fill(bg)
        e_cell.font = fnt(bold=False, colour=GREY_DARK, size=10)
        e_cell.alignment = aln()
        e_cell.border = bdr()

        s_cell = ws.cell(row=i, column=5, value=status)
        s_cell.fill = fill(LIGHT_GREEN)
        s_cell.font = fnt(bold=True, colour=GREY_DARK, size=10)
        s_cell.alignment = Alignment(horizontal="center", vertical="center")
        s_cell.border = bdr()
        set_h(ws, i, 18)

    # ── Assumptions Summary ────────────────────────────────────────────────────
    section_hdr(ws, 17, 2, "KEY ASSUMPTIONS AUDIT TRAIL", span=4, bg=MID_BLUE)
    hdr(ws, 18, 2, "Assumption", bg=NAVY)
    hdr(ws, 18, 3, "Current Value", bg=NAVY)
    hdr(ws, 18, 4, "Legal Minimum", bg=NAVY)
    hdr(ws, 18, 5, "Status", bg=NAVY)
    set_h(ws, 18, 24)

    ass_checks = [
        ("Personal Allowance £",   "=ASSUMPTIONS!C15",  12570,
         '=IF(C19>=12570,"✓","⚠ Check")'),
        ("Basic Rate %",           "=ASSUMPTIONS!E15",  0.20,
         '=IF(C20=0.2,"✓","⚠ Verify")'),
        ("ER NI Rate %",           "=ASSUMPTIONS!E32",  0.138,
         '=IF(C21=0.138,"✓","⚠ Verify")'),
        ("QE Lower Limit £",       "=ASSUMPTIONS!C38",  6240,
         '=IF(C22>=6240,"✓","⚠ Below min")'),
        ("QE Upper Limit £",       "=ASSUMPTIONS!C39",  50270,
         '=IF(C23<=50270,"✓","⚠ Above max")'),
        ("Auto-enrol Min EE %",    "=ASSUMPTIONS!C46",  0.05,
         '=IF(C24>=0.05,"✓ Meets AE min","⚠ Below AE minimum")'),
        ("Auto-enrol Min ER %",    "=ASSUMPTIONS!C47",  0.03,
         '=IF(C25>=0.03,"✓ Meets AE min","⚠ Below AE minimum")'),
        ("Annual Allowance £",     "=ASSUMPTIONS!C40",  60000,
         '=IF(C26>=60000,"✓","⚠ Check AA")'),
    ]

    for i, (label, val, minimum, status) in enumerate(ass_checks, 19):
        bg = PALE_BLUE if i % 2 == 0 else WHITE
        lbl(ws, i, 2, label, bg=bg)

        v_cell = ws.cell(row=i, column=3, value=val)
        v_cell.fill = fill(LIGHT_BLUE)
        v_cell.font = fnt(bold=False, colour=GREY_DARK, size=10)
        v_cell.alignment = aln(); v_cell.border = bdr()
        v_cell.number_format = FMT_PCT if isinstance(minimum, float) else FMT_GBP0

        m_cell = ws.cell(row=i, column=4, value=minimum)
        m_cell.fill = fill(bg)
        m_cell.font = fnt(bold=False, colour=GREY_DARK, size=10)
        m_cell.alignment = aln(); m_cell.border = bdr()
        m_cell.number_format = FMT_PCT if isinstance(minimum, float) else FMT_GBP0

        s_cell = ws.cell(row=i, column=5, value=status)
        s_cell.fill = fill(LIGHT_GREEN)
        s_cell.font = fnt(bold=True, colour=GREY_DARK, size=10)
        s_cell.alignment = Alignment(horizontal="center", vertical="center")
        s_cell.border = bdr()
        set_h(ws, i, 18)

    # ── Modelling Risks ────────────────────────────────────────────────────────
    section_hdr(ws, 29, 2, "MODELLING RISKS & LIMITATIONS", span=4, bg=RED)
    risks = [
        "Scottish Income Tax not modelled — add separate tax table for Scottish residents",
        "Welsh rates mirror England/NI — no difference applied in this model",
        "NI Category assumed 'A' for all employees — update for Directors, married women, etc.",
        "Pension taper annual allowance not modelled (>£260k adjusted income threshold)",
        "Bonus sacrifice not split out separately — model treats all earnings uniformly per basis setting",
        "No student loan deductions modelled — add Plan 1/2/4/Postgrad threshold table",
        "Employment Allowance eligibility not verified per employee — confirm with payroll provider",
        "This model uses annual figures; monthly payroll timing differences not captured",
        "Salary sacrifice below National Minimum Wage is prohibited — add NMW check per employee",
        "Benefits in Kind (company cars, BUPA etc.) excluded — these affect NI calculations",
        "TUPE employees may have protected pension rights — verify before applying SS",
        "This is a modelling tool only — always verify outputs with a qualified payroll/pensions adviser",
    ]
    for i, risk in enumerate(risks, 30):
        cell = ws.cell(row=i, column=2, value=f"⚠  {risk}")
        ws.merge_cells(start_row=i, start_column=2, end_row=i, end_column=5)
        cell.fill = fill(LIGHT_RED if i % 2 == 0 else "FFE8E8")
        cell.font = fnt(bold=False, colour=RED, size=10)
        cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        cell.border = bdr()
        set_h(ws, i, 22)

    return ws


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "/home/user/financial-services/models")
    from build_model_part1 import (build_assumptions, build_employee_data,
                                    build_tax_ni_tables)
    from build_model_part2 import build_calc_engine

    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    build_assumptions(wb)
    build_employee_data(wb)
    build_tax_ni_tables(wb)
    build_calc_engine(wb)
    build_employee_impact(wb)
    build_employer_analysis(wb)
    build_dept_summary(wb)
    build_scenario_comparison(wb)
    build_audit_checks(wb)

    out = "/home/user/financial-services/models/pension_salary_sacrifice_PART3_TEST.xlsx"
    wb.save(out)
    print(f"Saved: {out}")
