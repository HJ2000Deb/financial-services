"""
UK Pension Salary Sacrifice Model - Builder Part 4
Sheet: DASHBOARD (executive summary with charts)
+ Master assembly function
"""
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, Reference, PieChart, LineChart
from openpyxl.chart.label import DataLabelList
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

CE = "CALC_ENGINE"
EA = "EMPLOYER_ANALYSIS"
DS = "DEPT_SUMMARY"
EI = "EMPLOYEE_IMPACT"
N  = 25
FIRST_ROW = 4
CE_TOTAL  = 29

def col(n): return get_column_letter(n)
def set_w(ws, c, w): ws.column_dimensions[col(c)].width = w
def set_h(ws, r, h): ws.row_dimensions[r].height = h


def kpi_block(ws, r, c, title, value_formula, fmt, title_bg=MID_BLUE,
              value_bg=NAVY, caption=None):
    """Draw a 3-row KPI tile: title / value / caption."""
    ws.merge_cells(start_row=r,   start_column=c, end_row=r,   end_column=c+1)
    ws.merge_cells(start_row=r+1, start_column=c, end_row=r+1, end_column=c+1)
    ws.merge_cells(start_row=r+2, start_column=c, end_row=r+2, end_column=c+1)

    t = ws.cell(row=r, column=c, value=title)
    t.fill = fill(title_bg)
    t.font = fnt(bold=True, colour=WHITE, size=10)
    t.alignment = Alignment(horizontal="center", vertical="center")
    t.border = bdr()
    set_h(ws, r, 18)

    v = ws.cell(row=r+1, column=c, value=value_formula)
    v.fill = fill(value_bg)
    v.font = fnt(bold=True, colour=WHITE, size=18)
    v.alignment = Alignment(horizontal="center", vertical="center")
    v.border = bdr()
    v.number_format = fmt
    set_h(ws, r+1, 36)

    cap = ws.cell(row=r+2, column=c, value=caption or "")
    cap.fill = fill(PALE_BLUE)
    cap.font = fnt(bold=False, colour=GREY_DARK, size=9, italic=True)
    cap.alignment = Alignment(horizontal="center", vertical="center")
    cap.border = bdr()
    set_h(ws, r+2, 16)


# ══════════════════════════════════════════════════════════════════════════════
# SHEET: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def build_dashboard(wb):
    ws = wb.create_sheet("DASHBOARD", 0)   # insert as first sheet
    ws.sheet_view.showGridLines = False
    ws.tab_color = NAVY

    # Column widths — 26 columns, 2-unit gutters at A, Z
    set_w(ws, 1, 2)
    for c in range(2, 26):
        set_w(ws, c, 14)
    set_w(ws, 26, 2)

    # ── Title ──────────────────────────────────────────────────────────────────
    ws.merge_cells("A1:Z1")
    c = ws["A1"]
    c.value = "UK PENSION SALARY SACRIFICE MODEL  ·  EXECUTIVE DASHBOARD"
    c.fill = fill(NAVY)
    c.font = fnt(bold=True, colour=WHITE, size=18)
    c.alignment = Alignment(horizontal="center", vertical="center")
    set_h(ws, 1, 50)

    ws.merge_cells("A2:Z2")
    c = ws["A2"]
    c.value = (f"Company: =ASSUMPTIONS!C9  |  Tax Year: =ASSUMPTIONS!C5  |  "
               f"Employees: {N}  |  Pension Basis: =ASSUMPTIONS!C48  |  "
               f"NI Treatment: =ASSUMPTIONS!C53")
    c.value = (
        "Example Co Ltd  |  Tax Year 2024/25  |  25 Employees  |  "
        "Salary Sacrifice: Active  |  Data as at 09 May 2026"
    )
    c.fill = fill(MID_BLUE)
    c.font = fnt(bold=False, colour=WHITE, size=11, italic=True)
    c.alignment = Alignment(horizontal="center", vertical="center")
    set_h(ws, 2, 22)

    # ── KPI Row 1 — Employee impact ───────────────────────────────────────────
    ws.merge_cells("B4:Y4")
    s = ws["B4"]
    s.value = "EMPLOYEE OUTCOMES"
    s.fill = fill(MID_BLUE)
    s.font = fnt(bold=True, colour=WHITE, size=12)
    s.alignment = Alignment(horizontal="left", vertical="center")
    set_h(ws, 4, 22)

    kpi_data_row1 = [
        (2,  "Total Take-Home (Post) £", f"={CE}!R{CE_TOTAL}", FMT_GBP0, "Annual, all staff"),
        (6,  "Avg Take-Home Change £",   f"={CE}!AJ{CE_TOTAL}/{N}", FMT_GBP0, "Per employee p.a."),
        (10, "Total EE Pension £",       f"={CE}!AB{CE_TOTAL}", FMT_GBP0, "Salary sacrificed"),
        (14, "Avg EE Tax Saving £",      f"=({CE}!O{CE_TOTAL}-{CE}!Z{CE_TOTAL})/{N}", FMT_GBP0, "PAYE reduction"),
        (18, "Avg EE NI Saving £",       f"=({CE}!P{CE_TOTAL}-{CE}!AA{CE_TOTAL})/{N}", FMT_GBP0, "NI reduction"),
        (22, "Participation Rate",        f"=COUNTIF({CE}!K4:K{FIRST_ROW+N-1},\"Yes\")/{N}", FMT_PCT1, "On salary sacrifice"),
    ]
    for start_col, title, formula, fmt, caption in kpi_data_row1:
        kpi_block(ws, 5, start_col, title, formula, fmt, caption=caption)

    # ── KPI Row 2 — Employer impact ───────────────────────────────────────────
    ws.merge_cells("B9:Y9")
    s = ws["B9"]
    s.value = "EMPLOYER OUTCOMES"
    s.fill = fill(ORANGE)
    s.font = fnt(bold=True, colour=WHITE, size=12)
    s.alignment = Alignment(horizontal="left", vertical="center")
    set_h(ws, 9, 22)

    kpi_data_row2 = [
        (2,  "Total ER Cost (Post) £",   f"={CE}!AI{CE_TOTAL}", FMT_GBP0, "Salary+NI+Pension"),
        (6,  "ER Cost Change £",          f"={CE}!AI{CE_TOTAL}-{CE}!U{CE_TOTAL}", FMT_GBP0, "vs pre-sacrifice"),
        (10, "Gross ER NI Saving £",      f"={CE}!AF{CE_TOTAL}", FMT_GBP0, "Annual saving"),
        (14, "NI Saving per EE £",        f"={CE}!AF{CE_TOTAL}/{N}", FMT_GBP0, "Average per employee"),
        (18, "Total ER Pension £",        f"={CE}!AD{CE_TOTAL}", FMT_GBP0, "Employer contributions"),
        (22, "Total Pension to Scheme £", f"={CE}!AB{CE_TOTAL}+{CE}!AD{CE_TOTAL}", FMT_GBP0, "Combined EE+ER"),
    ]
    for start_col, title, formula, fmt, caption in kpi_data_row2:
        kpi_block(ws, 10, start_col, title, formula, fmt,
                  title_bg=ORANGE, value_bg="7F3206", caption=caption)

    # ── Data tables for charts ────────────────────────────────────────────────
    # Chart data stored in hidden area (rows 14-45, cols B-D for chart data)
    # We'll place chart source data in a dedicated area

    # Chart 1 Source: Department comparison (pull from DEPT_SUMMARY)
    # Rows 14-20 will hold dept chart data
    ws.cell(row=14, column=2, value="Department").font = fnt(bold=True, colour=GREY_DARK, size=9)
    ws.cell(row=14, column=3, value="ER NI Saving £").font = fnt(bold=True, colour=GREY_DARK, size=9)
    ws.cell(row=14, column=4, value="EE Take-Home Chg £").font = fnt(bold=True, colour=GREY_DARK, size=9)
    ws.cell(row=14, column=5, value="Total Pension £").font = fnt(bold=True, colour=GREY_DARK, size=9)

    departments = ["Finance", "HR", "Operations", "Sales", "Tech"]
    # DEPT_SUMMARY rows 4-8
    for i, dept in enumerate(departments):
        ds_row = i + 4
        r = i + 15
        ws.cell(row=r, column=2, value=dept)
        ws.cell(row=r, column=3, value=f"={DS}!I{ds_row}")
        ws.cell(row=r, column=4, value=f"={DS}!J{ds_row}")
        ws.cell(row=r, column=5, value=f"={DS}!H{ds_row}")
        for cc in [3, 4, 5]:
            ws.cell(row=r, column=cc).number_format = FMT_GBP0

    # Chart 2 Source: Pre vs Post breakdown (company totals)
    ws.cell(row=22, column=2, value="Metric")
    ws.cell(row=22, column=3, value="Pre-Sacrifice £")
    ws.cell(row=22, column=4, value="Post-Sacrifice £")

    breakdown_metrics = [
        ("PAYE Tax",    f"={CE}!O{CE_TOTAL}", f"={CE}!Z{CE_TOTAL}"),
        ("Employee NI", f"={CE}!P{CE_TOTAL}", f"={CE}!AA{CE_TOTAL}"),
        ("EE Pension",  f"={CE}!Q{CE_TOTAL}", f"={CE}!AB{CE_TOTAL}"),
        ("ER Pension",  f"={CE}!S{CE_TOTAL}", f"={CE}!AD{CE_TOTAL}"),
        ("ER NI",       f"={CE}!T{CE_TOTAL}", f"={CE}!AE{CE_TOTAL}"),
    ]
    for i, (metric, pre, post) in enumerate(breakdown_metrics):
        r = i + 23
        ws.cell(row=r, column=2, value=metric)
        ws.cell(row=r, column=3, value=pre).number_format = FMT_GBP0
        ws.cell(row=r, column=4, value=post).number_format = FMT_GBP0

    # ── Chart 1: Department ER NI Saving (Bar) ────────────────────────────────
    chart1 = BarChart()
    chart1.type = "col"
    chart1.title = "ER NI Saving by Department"
    chart1.style = 10
    chart1.y_axis.title = "£"
    chart1.x_axis.title = "Department"
    chart1.height = 12
    chart1.width = 18

    cats1 = Reference(ws, min_col=2, min_row=15, max_row=19)
    data1 = Reference(ws, min_col=3, min_row=14, max_row=19)
    chart1.add_data(data1, titles_from_data=True)
    chart1.set_categories(cats1)
    chart1.series[0].graphicalProperties.solidFill = MID_BLUE
    ws.add_chart(chart1, "B14")

    # ── Chart 2: Pre vs Post Payroll Breakdown (Clustered Bar) ────────────────
    chart2 = BarChart()
    chart2.type = "col"
    chart2.grouping = "clustered"
    chart2.title = "Pre vs Post Sacrifice — Company Payroll Components"
    chart2.style = 10
    chart2.y_axis.title = "£"
    chart2.height = 12
    chart2.width = 18

    cats2 = Reference(ws, min_col=2, min_row=23, max_row=27)
    data2 = Reference(ws, min_col=3, min_row=22, max_row=27)
    chart2.add_data(data2, titles_from_data=True)
    chart2.set_categories(cats2)
    if len(chart2.series) > 0:
        chart2.series[0].graphicalProperties.solidFill = GREEN
    if len(chart2.series) > 1:
        chart2.series[1].graphicalProperties.solidFill = ORANGE
    ws.add_chart(chart2, "L14")

    # ── Chart 3: Total Pension Split (Pie) ────────────────────────────────────
    # Source data rows 30-31
    ws.cell(row=30, column=2, value="Component")
    ws.cell(row=30, column=3, value="Amount £")
    ws.cell(row=31, column=2, value="EE Pension")
    ws.cell(row=31, column=3, value=f"={CE}!AB{CE_TOTAL}")
    ws.cell(row=32, column=2, value="ER Pension")
    ws.cell(row=32, column=3, value=f"={CE}!AD{CE_TOTAL}")
    ws.cell(row=33, column=2, value="NI Shared to EEs")
    ws.cell(row=33, column=3, value=f"={CE}!AG{CE_TOTAL}")

    chart3 = PieChart()
    chart3.title = "Total Value — EE Pension vs ER Pension vs NI Share"
    chart3.style = 10
    chart3.height = 12
    chart3.width = 14

    cats3 = Reference(ws, min_col=2, min_row=31, max_row=33)
    data3 = Reference(ws, min_col=3, min_row=30, max_row=33)
    chart3.add_data(data3, titles_from_data=True)
    chart3.set_categories(cats3)
    ws.add_chart(chart3, "B29")

    # ── Chart 4: Employee Take-Home Change (Bar — individual employees) ────────
    # Source: first 15 employees from EMPLOYEE_IMPACT for readability
    ws.cell(row=35, column=2, value="Employee")
    ws.cell(row=35, column=3, value="Take-Home Change £")
    for i in range(15):
        ei_row = i + 4  # EMPLOYEE_IMPACT data starts row 4
        r = i + 36
        ws.cell(row=r, column=2, value=f"={EI}!B{ei_row}")
        ws.cell(row=r, column=3, value=f"={EI}!I{ei_row}").number_format = FMT_GBP0

    chart4 = BarChart()
    chart4.type = "bar"   # horizontal
    chart4.title = "Individual Take-Home Change (Top 15 Employees)"
    chart4.style = 10
    chart4.y_axis.title = "Employee"
    chart4.x_axis.title = "£ Change"
    chart4.height = 14
    chart4.width = 18

    cats4 = Reference(ws, min_col=2, min_row=36, max_row=50)
    data4 = Reference(ws, min_col=3, min_row=35, max_row=50)
    chart4.add_data(data4, titles_from_data=True)
    chart4.set_categories(cats4)
    chart4.series[0].graphicalProperties.solidFill = MID_BLUE
    ws.add_chart(chart4, "L29")

    # ── Key Insights text block ────────────────────────────────────────────────
    ws.merge_cells("B45:Y45")
    ins = ws["B45"]
    ins.value = (
        "KEY INSIGHTS  |  "
        "Salary sacrifice reduces the employee's gross for PAYE and NI, creating tax efficiency for both parties.  "
        "The employer saves ER NI at 13.8% on all sacrificed amounts — this saving can be retained, shared or reinvested.  "
        "Higher-rate taxpayers see the greatest take-home improvement per £ sacrificed.  "
        "Ensure no employee's post-sacrifice salary falls below National Minimum Wage.  "
        "Verify Annual Allowance for high earners (see AUDIT_CHECKS tab)."
    )
    ins.fill = fill(LIGHT_GOLD)
    ins.font = fnt(bold=False, colour=GREY_DARK, size=10, italic=True)
    ins.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    ins.border = bdr(style="medium")
    set_h(ws, 45, 50)

    return ws


# ══════════════════════════════════════════════════════════════════════════════
# MASTER ASSEMBLY
# ══════════════════════════════════════════════════════════════════════════════
def build_full_workbook(output_path):
    import sys
    sys.path.insert(0, "/home/user/financial-services/models")
    from build_model_part1 import (build_assumptions, build_employee_data,
                                    build_tax_ni_tables)
    from build_model_part2 import build_calc_engine
    from build_model_part3 import (build_employee_impact, build_employer_analysis,
                                    build_dept_summary, build_scenario_comparison,
                                    build_audit_checks)

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    # Build in logical order — DASHBOARD inserted as first sheet inside its function
    build_assumptions(wb)
    build_employee_data(wb)
    build_tax_ni_tables(wb)
    build_calc_engine(wb)
    build_employee_impact(wb)
    build_employer_analysis(wb)
    build_dept_summary(wb)
    build_scenario_comparison(wb)
    build_audit_checks(wb)
    build_dashboard(wb)   # inserts as first sheet (index 0)

    # ── Workbook-level properties ──────────────────────────────────────────────
    wb.properties.title = "UK Pension Salary Sacrifice Model"
    wb.properties.subject = "Pension / Payroll Financial Modelling"
    wb.properties.creator = "Financial Services Model Builder"
    wb.properties.description = (
        "Professional UK salary sacrifice pension model covering employee "
        "take-home, employer NI optimisation, qualifying earnings vs full "
        "salary basis, and NI saving disposition analysis."
    )
    wb.properties.keywords = "salary sacrifice, pension, NI, PAYE, payroll, UK"

    # ── Sheet order: DASHBOARD first ──────────────────────────────────────────
    sheet_order = [
        "DASHBOARD",
        "ASSUMPTIONS",
        "EMPLOYEE_DATA",
        "TAX_NI_TABLES",
        "CALC_ENGINE",
        "EMPLOYEE_IMPACT",
        "EMPLOYER_ANALYSIS",
        "DEPT_SUMMARY",
        "SCENARIO_COMPARISON",
        "AUDIT_CHECKS",
    ]
    # Reorder sheets
    for i, name in enumerate(sheet_order):
        if name in wb.sheetnames:
            idx = wb.sheetnames.index(name)
            wb.move_sheet(name, offset=i - idx)

    wb.active = wb["DASHBOARD"]

    wb.save(output_path)
    print(f"✓ Workbook saved: {output_path}")
    print(f"  Sheets: {', '.join(wb.sheetnames)}")

    return wb


if __name__ == "__main__":
    out = "/home/user/financial-services/models/UK_Pension_Salary_Sacrifice_Model.xlsx"
    build_full_workbook(out)
