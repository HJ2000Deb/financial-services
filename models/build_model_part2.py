"""
UK Pension Salary Sacrifice Model - Builder Part 2
Sheet: CALC_ENGINE  (core salary sacrifice calculation per employee)
"""
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ── Palette (duplicated for standalone testing) ────────────────────────────────
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

FMT_GBP0  = '£#,##0'
FMT_GBP   = '£#,##0.00'
FMT_PCT   = '0.00%'
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

def hdr(ws, r, c, val, bg=MID_BLUE, fg=WHITE, size=10, wrap=True, width=None):
    cell = ws.cell(row=r, column=c, value=val)
    cell.fill = fill(bg)
    cell.font = fnt(bold=True, colour=fg, size=size)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=wrap)
    cell.border = bdr()
    if width:
        ws.column_dimensions[get_column_letter(c)].width = width
    return cell

def calc(ws, r, c, formula, fmt=None, bg=WHITE, bold=False, fg=GREY_DARK):
    cell = ws.cell(row=r, column=c, value=formula)
    cell.fill = fill(bg)
    cell.font = fnt(bold=bold, colour=fg, size=10)
    cell.alignment = aln()
    cell.border = bdr()
    if fmt: cell.number_format = fmt
    return cell

def inp(ws, r, c, val, fmt=None, bg=LIGHT_GOLD):
    cell = ws.cell(row=r, column=c, value=val)
    cell.fill = fill(bg)
    cell.font = fnt(bold=False, colour=GREY_DARK, size=10)
    cell.alignment = aln()
    cell.border = bdr()
    if fmt: cell.number_format = fmt
    return cell

def section(ws, r, c, text, span=1, bg=NAVY, size=11):
    cell = ws.cell(row=r, column=c, value=text)
    cell.fill = fill(bg)
    cell.font = fnt(bold=True, colour=WHITE, size=size)
    cell.alignment = aln(h="left")
    cell.border = bdr(style="medium", colour=bg)
    ws.row_dimensions[r].height = 20
    if span > 1:
        ws.merge_cells(start_row=r, start_column=c, end_row=r, end_column=c+span-1)
    return cell

def set_w(ws, c, w):
    ws.column_dimensions[get_column_letter(c)].width = w

def set_h(ws, r, h):
    ws.row_dimensions[r].height = h


# ══════════════════════════════════════════════════════════════════════════════
# CALC_ENGINE columns
# ══════════════════════════════════════════════════════════════════════════════
# The engine pulls from EMPLOYEE_DATA rows 3-27 (25 employees) and
# ASSUMPTIONS for rates. Every formula is fully dynamic.
#
# Column layout (1-indexed):
#  A=1  Emp ID (link)
#  B=2  Name
#  C=3  Department
#  D=4  Annual Basic Salary
#  E=5  Annual Bonus
#  F=6  Total Earnings
#  G=7  Pension Basis (resolved)
#  H=8  Pensionable Pay (pre-sacrifice)
#  I=9  EE Contrib Rate
#  J=10 ER Contrib Rate
#  K=11 Sacrifice On? flag
#  --- PRE-SACRIFICE BASELINE ---
#  L=12 Gross Taxable Pay (pre)
#  M=13 Effective Personal Allowance (PA taper)
#  N=14 Taxable Income (pre)
#  O=15 PAYE Tax (pre)
#  P=16 EE NI (pre)
#  Q=17 EE Pension Contrib (pre, net pay / RAS)
#  R=18 Employee Take-Home (pre)
#  S=19 ER Pension (pre)
#  T=20 ER NI (pre)
#  U=21 Total ER Cost (pre)
#  --- POST-SACRIFICE ---
#  V=22 Sacrificed Amount
#  W=23 Post-Sacrifice Gross
#  X=24 Effective PA (post)
#  Y=25 Taxable Income (post)
#  Z=26 PAYE Tax (post)
# AA=27 EE NI (post)
# AB=28 EE Pension = sacrificed amount (SS = gross)
# AC=29 Employee Take-Home (post)
# AD=30 ER Pension (post) = base ER + optional NI saving share
# AE=31 ER NI (post)
# AF=32 ER NI Saving
# AG=33 ER NI Saving Shared to EE
# AH=34 ER NI Saving Retained/Reinvested
# AI=35 Total ER Cost (post)
# --- IMPACT ---
# AJ=36 EE Take-Home Change
# AK=37 EE Take-Home Change %
# AL=38 EE Pension Change (total pension in - EE cost perspective)
# AM=39 ER Cost Change
# AN=40 ER NI Saving (net)
# AO=41 Total Pension Pot contribution (EE+ER post)
# AP=42 Annual Allowance Check flag
# AQ=43 Taxpayer Band (pre)
# AR=44 Taxpayer Band (post)
# AS=45 NI Saving per £ sacrificed

TOTAL_COLS = 45
FIRST_DATA_ROW = 4   # row 2 = main header, row 3 = sub-headers
LAST_DATA_ROW  = 28  # 25 employees
N_EMPLOYEES    = 25
ED = "EMPLOYEE_DATA"   # sheet reference prefix
AS_SHT = "ASSUMPTIONS" # assumptions sheet

def col(n):
    """Convert 1-based column index to Excel letter."""
    return get_column_letter(n)


def build_calc_engine(wb):
    ws = wb.create_sheet("CALC_ENGINE")
    ws.sheet_view.showGridLines = False
    ws.tab_color = GREEN

    # Freeze first 3 columns + header rows
    ws.freeze_panes = "D4"

    # Banner
    last_col_letter = col(TOTAL_COLS)
    ws.merge_cells(f"A1:{last_col_letter}1")
    c = ws["A1"]
    c.value = ("SALARY SACRIFICE CALCULATION ENGINE  |  "
               "All formulas link to ASSUMPTIONS & EMPLOYEE_DATA  |  "
               "Do not edit formula cells")
    c.fill = fill(NAVY)
    c.font = fnt(bold=True, colour=WHITE, size=12)
    c.alignment = Alignment(horizontal="center", vertical="center")
    set_h(ws, 1, 36)

    # ── Group headers row 2 ────────────────────────────────────────────────────
    groups = [
        (1,  3,  "EMPLOYEE",          MID_BLUE),
        (4,  6,  "EARNINGS",          MID_BLUE),
        (7,  11, "PENSION SETUP",     "4472C4"),
        (12, 21, "PRE-SACRIFICE BASELINE", "375623"),
        (22, 35, "POST-SACRIFICE",    "C55A11"),
        (36, 44, "IMPACT ANALYSIS",   NAVY),
        (45, 45, "CHECKS",            RED),
    ]
    for start, end, label, bg in groups:
        if start == end:
            hdr(ws, 2, start, label, bg=bg, size=9)
        else:
            hdr(ws, 2, start, label, bg=bg, size=9)
            ws.merge_cells(start_row=2, start_column=start,
                           end_row=2, end_column=end)
    set_h(ws, 2, 28)

    # ── Column sub-headers row 3 ───────────────────────────────────────────────
    col_headers = [
        # Employee
        (1,  "Emp ID",            8),
        (2,  "Name",              16),
        (3,  "Department",        14),
        # Earnings
        (4,  "Basic Salary £",    14),
        (5,  "Bonus £",           12),
        (6,  "Total Earnings £",  14),
        # Pension setup
        (7,  "Pension Basis",     16),
        (8,  "Pensionable Pay £", 14),
        (9,  "EE Rate %",         9),
        (10, "ER Rate %",         9),
        (11, "Sacrifice On?",     10),
        # Pre-sacrifice
        (12, "Gross Pay £",       13),
        (13, "Eff. PA £",         12),
        (14, "Taxable Inc £",     13),
        (15, "PAYE Tax £",        12),
        (16, "EE NI £",           12),
        (17, "EE Pension £\n(Net Pay/RAS)", 14),
        (18, "Take-Home £\n(Pre)", 13),
        (19, "ER Pension £",      13),
        (20, "ER NI £",           12),
        (21, "Total ER Cost £",   13),
        # Post-sacrifice
        (22, "Sacrificed £",      13),
        (23, "Post-Sac Gross £",  13),
        (24, "Eff. PA (Post) £",  13),
        (25, "Taxable Inc\n(Post) £", 13),
        (26, "PAYE Tax\n(Post) £", 13),
        (27, "EE NI\n(Post) £",   12),
        (28, "EE Pension £\n(SS)", 13),
        (29, "Take-Home £\n(Post)", 13),
        (30, "ER Pension £\n(Post)", 14),
        (31, "ER NI\n(Post) £",   12),
        (32, "ER NI Saving £",    13),
        (33, "NI Share→EE £",     13),
        (34, "NI Retain/\nReinvest £", 13),
        (35, "Total ER Cost\n(Post) £", 14),
        # Impact
        (36, "Take-Home\nChange £", 14),
        (37, "Take-Home\nChange %",  13),
        (38, "EE Pension\nChange £", 14),
        (39, "ER Cost\nChange £",   13),
        (40, "ER NI\nSaving £",     13),
        (41, "Total Pension\n(EE+ER) £", 14),
        (42, "Ann Allowance\nRemaining £", 15),
        (43, "Tax Band\n(Pre)",      12),
        (44, "Tax Band\n(Post)",     12),
        # Check
        (45, "Flags",               10),
    ]
    for c_idx, label, width in col_headers:
        set_w(ws, c_idx, width)
        bg = MID_BLUE
        if   c_idx <= 3:  bg = MID_BLUE
        elif c_idx <= 6:  bg = MID_BLUE
        elif c_idx <= 11: bg = "4472C4"
        elif c_idx <= 21: bg = "375623"
        elif c_idx <= 35: bg = "C55A11"
        elif c_idx <= 44: bg = NAVY
        else:             bg = RED
        hdr(ws, 3, c_idx, label, bg=bg, size=9, width=width)
    set_h(ws, 3, 40)

    # ── Data rows ──────────────────────────────────────────────────────────────
    # Shorthand references
    PA       = f"ASSUMPTIONS!$C$15"
    BR_RATE  = f"ASSUMPTIONS!$E$15"
    HR_THR   = f"ASSUMPTIONS!$C$16"
    HR_RATE  = f"ASSUMPTIONS!$E$16"
    AR_THR   = f"ASSUMPTIONS!$C$17"
    AR_RATE  = f"ASSUMPTIONS!$E$17"
    PA_TAPER = f"ASSUMPTIONS!$C$18"
    NI_PT    = f"TAX_NI_TABLES!$D$6"   # annual PT
    NI_UEL   = f"TAX_NI_TABLES!$D$7"   # annual UEL
    NI_ST    = f"TAX_NI_TABLES!$D$8"   # annual ST
    EE_MAIN  = f"ASSUMPTIONS!$E$25"    # 8%
    EE_UP    = f"ASSUMPTIONS!$E$26"    # 2%
    ER_RATE  = f"ASSUMPTIONS!$E$32"    # 13.8%
    QE_LO    = f"ASSUMPTIONS!$C$38"
    QE_HI    = f"ASSUMPTIONS!$C$39"
    DEF_EE   = f"ASSUMPTIONS!$C$46"
    DEF_ER   = f"ASSUMPTIONS!$C$47"
    PEN_BAS  = f"ASSUMPTIONS!$C$48"
    NI_TREAT = f"ASSUMPTIONS!$C$53"
    NI_SHARE = f"ASSUMPTIONS!$C$55"
    SS_GLOBAL= f"ASSUMPTIONS!$C$62"    # "On"/"Off"
    AA_LIMIT = f"ASSUMPTIONS!$C$40"

    for i in range(N_EMPLOYEES):
        r   = FIRST_DATA_ROW + i
        ed_r = i + 3   # EMPLOYEE_DATA row for this employee (starts row 3)
        bg_row = PALE_BLUE if i % 2 == 0 else WHITE

        def f(col_i, formula, fmt=None, bold=False, bg=None):
            _bg = bg if bg is not None else bg_row
            calc(ws, r, col_i, formula, fmt=fmt, bg=_bg, bold=bold)

        def lbl(col_i, formula, fmt=None, bg=None):
            _bg = bg if bg is not None else bg_row
            cell = ws.cell(row=r, column=col_i, value=formula)
            cell.fill = fill(_bg)
            cell.font = fnt(bold=False, colour=GREY_DARK, size=10)
            cell.alignment = aln(h="left")
            cell.border = bdr()
            if fmt: cell.number_format = fmt

        # ── A: Emp ID ─────────────────────────────────────────────────────────
        lbl(1,  f"={ED}!A{ed_r}", fmt=FMT_TEXT)
        # ── B: Name ───────────────────────────────────────────────────────────
        lbl(2,  f'={ED}!B{ed_r}&" "&{ED}!C{ed_r}', fmt=FMT_TEXT)
        # ── C: Department ─────────────────────────────────────────────────────
        lbl(3,  f"={ED}!D{ed_r}", fmt=FMT_TEXT)

        # ── D: Basic Salary ───────────────────────────────────────────────────
        f(4,  f"={ED}!H{ed_r}", fmt=FMT_GBP0)
        # ── E: Bonus ──────────────────────────────────────────────────────────
        f(5,  f"={ED}!I{ed_r}", fmt=FMT_GBP0)
        # ── F: Total Earnings ─────────────────────────────────────────────────
        f(6,  f"={ED}!J{ed_r}", fmt=FMT_GBP0, bold=True)

        # ── G: Pension Basis (resolved) ───────────────────────────────────────
        # Override per employee OR global assumption
        lbl(7, (f'=IF({ED}!O{ed_r}<>"",{ED}!O{ed_r},{PEN_BAS})'),
            fmt=FMT_TEXT, bg=LIGHT_BLUE if i % 2 == 0 else LIGHT_BLUE)

        # ── H: Pensionable Pay (pre-sacrifice) ────────────────────────────────
        # Qualifying Earnings: BETWEEN QE_LO and QE_HI
        # Full Salary: basic only
        # Full incl. Bonus: total earnings
        f(8, (
            f'=IF(G{r}="Qualifying Earnings",'
            f'MAX(0,MIN({col(6)}{r},{QE_HI})-{QE_LO}),'
            f'IF(G{r}="Full Salary",{col(4)}{r},{col(6)}{r}))'
        ), fmt=FMT_GBP0, bg=LIGHT_BLUE if i % 2 == 0 else LIGHT_BLUE)

        # ── I: EE Contrib Rate ────────────────────────────────────────────────
        f(9, f'=IF({ED}!M{ed_r}="Y",{ED}!K{ed_r},{DEF_EE})', fmt=FMT_PCT)
        # ── J: ER Contrib Rate ────────────────────────────────────────────────
        f(10, f'=IF({ED}!M{ed_r}="Y",{ED}!L{ed_r},{DEF_ER})', fmt=FMT_PCT)
        # ── K: Sacrifice On flag ──────────────────────────────────────────────
        lbl(11, f'=IF(AND({ED}!N{ed_r}="Y",{SS_GLOBAL}="On"),"Yes","No")',
            fmt=FMT_TEXT, bg=LIGHT_BLUE if i % 2 == 0 else LIGHT_BLUE)

        # ── PRE-SACRIFICE BASELINE ────────────────────────────────────────────
        # L=12: Gross taxable pay (pre) = total earnings (no sacrifice yet)
        f(12, f"={col(6)}{r}", fmt=FMT_GBP0, bg=LIGHT_GREEN if i%2==0 else "D9EFD3")

        # M=13: Effective Personal Allowance (PA taper for >£100k)
        # Taper: PA reduced by £1 for every £2 over £100k; zero at £125,140
        f(13, (
            f'=MAX(0,'
            f'IF({col(12)}{r}<={PA_TAPER},{PA},'
            f'{PA}-INT(({col(12)}{r}-{PA_TAPER})/2)))'
        ), fmt=FMT_GBP0, bg=LIGHT_GREEN if i%2==0 else "D9EFD3")

        # N=14: Taxable Income (pre)
        f(14, f'=MAX(0,{col(12)}{r}-{col(13)}{r})', fmt=FMT_GBP0,
          bg=LIGHT_GREEN if i%2==0 else "D9EFD3")

        # O=15: PAYE Tax (pre)
        # Multi-band: BR on (HR_THR-PA), HR on (AR_THR-HR_THR), AR on rest
        f(15, (
            f'=MAX(0,'
            f'MIN({col(14)}{r},MAX(0,{HR_THR}-{col(13)}{r}))*{BR_RATE}'
            f'+MAX(0,MIN({col(14)}{r},{AR_THR}-{col(13)}{r})-MAX(0,{HR_THR}-{col(13)}{r}))*{HR_RATE}'
            f'+MAX(0,{col(14)}{r}-MAX(0,{AR_THR}-{col(13)}{r}))*{AR_RATE}'
            f')'
        ), fmt=FMT_GBP0, bg=LIGHT_GREEN if i%2==0 else "D9EFD3")

        # P=16: EE NI (pre)  annual, Cat A: 8% PT→UEL, 2% above UEL
        f(16, (
            f'=MAX(0,MIN({col(12)}{r},{NI_UEL})-{NI_PT})*{EE_MAIN}'
            f'+MAX(0,{col(12)}{r}-{NI_UEL})*{EE_UP}'
        ), fmt=FMT_GBP0, bg=LIGHT_GREEN if i%2==0 else "D9EFD3")

        # Q=17: EE Pension (pre) — relief at source / net pay arrangement
        # Under non-sacrifice, employee pays from net; cost = gross pension contrib
        f(17, f'={col(8)}{r}*{col(9)}{r}', fmt=FMT_GBP0,
          bg=LIGHT_GREEN if i%2==0 else "D9EFD3")

        # R=18: Take-Home (pre) = gross - tax - EE NI - EE pension
        f(18, (
            f'={col(12)}{r}-{col(15)}{r}-{col(16)}{r}-{col(17)}{r}'
        ), fmt=FMT_GBP0, bold=True, bg=LIGHT_GREEN if i%2==0 else "D9EFD3")

        # S=19: ER Pension (pre)
        f(19, f'={col(8)}{r}*{col(10)}{r}', fmt=FMT_GBP0,
          bg=LIGHT_GREEN if i%2==0 else "D9EFD3")

        # T=20: ER NI (pre)  13.8% on earnings above ST
        f(20, f'=MAX(0,{col(12)}{r}-{NI_ST})*{ER_RATE}', fmt=FMT_GBP0,
          bg=LIGHT_GREEN if i%2==0 else "D9EFD3")

        # U=21: Total ER Cost (pre)
        f(21, f'={col(12)}{r}+{col(19)}{r}+{col(20)}{r}', fmt=FMT_GBP0, bold=True,
          bg=LIGHT_GREEN if i%2==0 else "D9EFD3")

        # ── POST-SACRIFICE ─────────────────────────────────────────────────────
        orange_bg = "FCE4D6" if i%2==0 else "FDEBD0"

        # V=22: Sacrificed Amount (if sacrifice On)
        f(22, (
            f'=IF({col(11)}{r}="Yes",'
            f'{col(8)}{r}*{col(9)}{r},'
            f'0)'
        ), fmt=FMT_GBP0, bg=orange_bg)

        # W=23: Post-Sacrifice Gross (reduced salary)
        f(23, f'={col(12)}{r}-{col(22)}{r}', fmt=FMT_GBP0, bold=True, bg=orange_bg)

        # X=24: Effective PA (post) — taper on post-sacrifice gross
        f(24, (
            f'=MAX(0,'
            f'IF({col(23)}{r}<={PA_TAPER},{PA},'
            f'{PA}-INT(({col(23)}{r}-{PA_TAPER})/2)))'
        ), fmt=FMT_GBP0, bg=orange_bg)

        # Y=25: Taxable income (post)
        f(25, f'=MAX(0,{col(23)}{r}-{col(24)}{r})', fmt=FMT_GBP0, bg=orange_bg)

        # Z=26: PAYE Tax (post)
        f(26, (
            f'=MAX(0,'
            f'MIN({col(25)}{r},MAX(0,{HR_THR}-{col(24)}{r}))*{BR_RATE}'
            f'+MAX(0,MIN({col(25)}{r},{AR_THR}-{col(24)}{r})-MAX(0,{HR_THR}-{col(24)}{r}))*{HR_RATE}'
            f'+MAX(0,{col(25)}{r}-MAX(0,{AR_THR}-{col(24)}{r}))*{AR_RATE}'
            f')'
        ), fmt=FMT_GBP0, bg=orange_bg)

        # AA=27: EE NI (post) on reduced gross
        f(27, (
            f'=MAX(0,MIN({col(23)}{r},{NI_UEL})-{NI_PT})*{EE_MAIN}'
            f'+MAX(0,{col(23)}{r}-{NI_UEL})*{EE_UP}'
        ), fmt=FMT_GBP0, bg=orange_bg)

        # AB=28: EE Pension under SS = sacrificed amount (gross contribution)
        f(28, f'={col(22)}{r}', fmt=FMT_GBP0, bg=orange_bg)

        # AC=29: Take-Home (post)
        # Under SS, EE doesn't pay pension from net — sacrifice already deducted
        # Also add employer NI sharing if applicable
        f(29, (
            f'={col(23)}{r}-{col(26)}{r}-{col(27)}{r}+{col(33)}{r}'
        ), fmt=FMT_GBP0, bold=True, bg=orange_bg)

        # AD=30: ER Pension (post) = base ER pension
        # If NI_TREAT = "Reinvest in Pension", add ER NI saving × share %
        f(30, (
            f'={col(8)}{r}*{col(10)}{r}'
            f'+IF({NI_TREAT}="Reinvest in Pension",{col(32)}{r}*{NI_SHARE},0)'
        ), fmt=FMT_GBP0, bg=orange_bg)

        # AE=31: ER NI (post) on post-sacrifice gross
        f(31, f'=MAX(0,{col(23)}{r}-{NI_ST})*{ER_RATE}', fmt=FMT_GBP0, bg=orange_bg)

        # AF=32: ER NI Saving = pre NI - post NI
        f(32, f'=MAX(0,{col(20)}{r}-{col(31)}{r})', fmt=FMT_GBP0, bold=True,
          bg="FFFF99" if i%2==0 else "FFFACC")

        # AG=33: ER NI Saving Shared to Employee (added to take-home)
        f(33, (
            f'=IF({NI_TREAT}="Share with Employees",'
            f'{col(32)}{r}*{NI_SHARE},'
            f'0)'
        ), fmt=FMT_GBP0, bg=orange_bg)

        # AH=34: Retained / Reinvested amount
        f(34, f'={col(32)}{r}-{col(33)}{r}', fmt=FMT_GBP0, bg=orange_bg)

        # AI=35: Total ER Cost (post)
        f(35, (
            f'={col(23)}{r}+{col(30)}{r}+{col(31)}{r}+{col(33)}{r}'
        ), fmt=FMT_GBP0, bold=True, bg=orange_bg)

        # ── IMPACT ANALYSIS ────────────────────────────────────────────────────
        navy_bg = LIGHT_BLUE if i%2==0 else "D6E4F0"

        # AJ=36: Take-Home Change £
        f(36, f'={col(29)}{r}-{col(18)}{r}', fmt=FMT_GBP0, bold=True, bg=navy_bg)

        # AK=37: Take-Home Change %
        f(37, (
            f'=IF({col(18)}{r}<>0,'
            f'({col(29)}{r}-{col(18)}{r})/{col(18)}{r},'
            f'0)'
        ), fmt=FMT_PCT, bg=navy_bg)

        # AL=38: EE Pension Change (post pension - pre pension cost)
        f(38, f'={col(28)}{r}-{col(17)}{r}', fmt=FMT_GBP0, bg=navy_bg)

        # AM=39: ER Cost Change
        f(39, f'={col(35)}{r}-{col(21)}{r}', fmt=FMT_GBP0, bg=navy_bg)

        # AN=40: ER NI Saving (net — after sharing)
        f(40, f'={col(34)}{r}', fmt=FMT_GBP0, bold=True, bg=navy_bg)

        # AO=41: Total Pension (EE+ER post)
        f(41, f'={col(28)}{r}+{col(30)}{r}', fmt=FMT_GBP0, bold=True, bg=navy_bg)

        # AP=42: Annual Allowance Remaining
        f(42, f'={AA_LIMIT}-{col(41)}{r}', fmt=FMT_GBP0, bg=navy_bg)

        # AQ=43: Tax Band Pre
        lbl(43, (
            f'=IF({col(6)}{r}<={PA},"Personal Allowance",'
            f'IF({col(6)}{r}<={HR_THR},"Basic Rate",'
            f'IF({col(6)}{r}<={AR_THR},"Higher Rate","Additional Rate")))'
        ), fmt=FMT_TEXT, bg=navy_bg)

        # AR=44: Tax Band Post
        lbl(44, (
            f'=IF({col(23)}{r}<={PA},"Personal Allowance",'
            f'IF({col(23)}{r}<={HR_THR},"Basic Rate",'
            f'IF({col(23)}{r}<={AR_THR},"Higher Rate","Additional Rate")))'
        ), fmt=FMT_TEXT, bg=navy_bg)

        # AS=45: Flags / Checks
        lbl(45, (
            f'=IF({col(42)}{r}<0,"⚠ AA Breach!","")'
            f'&IF({col(22)}{r}>{col(6)}{r},"⚠ Sacrifice>Salary","")'
            f'&IF({col(29)}{r}<0,"⚠ Neg Take-Home","")'
        ), fmt=FMT_TEXT, bg="FFCCCC" if i%2==0 else "FFE0E0")

        set_h(ws, r, 18)

    # ── TOTALS ROW ─────────────────────────────────────────────────────────────
    tr = LAST_DATA_ROW + 1
    ws.merge_cells(f"A{tr}:C{tr}")
    c = ws[f"A{tr}"]
    c.value = "COMPANY TOTALS"
    c.fill = fill(NAVY)
    c.font = fnt(bold=True, colour=WHITE, size=11)
    c.alignment = aln(h="center")
    c.border = bdr(style="medium")
    set_h(ws, tr, 24)

    sum_cols = [4,5,6,8,12,15,16,17,18,19,20,21,
                22,23,26,27,28,29,30,31,32,33,34,35,
                36,38,39,40,41]
    for ci in sum_cols:
        cl = col(ci)
        cell = ws.cell(row=tr, column=ci,
                       value=f"=SUM({cl}{FIRST_DATA_ROW}:{cl}{LAST_DATA_ROW})")
        cell.fill = fill(NAVY)
        cell.font = fnt(bold=True, colour=WHITE, size=11)
        cell.alignment = aln()
        cell.border = bdr(style="medium")
        cell.number_format = FMT_GBP0

    # Weighted average for % columns
    for ci in [37]:
        cl = col(ci)
        ref_cl = col(18)
        cell = ws.cell(row=tr, column=ci,
                       value=f"=IFERROR(SUM({col(36)}{FIRST_DATA_ROW}:{col(36)}{LAST_DATA_ROW})/SUM({ref_cl}{FIRST_DATA_ROW}:{ref_cl}{LAST_DATA_ROW}),0)")
        cell.fill = fill(NAVY)
        cell.font = fnt(bold=True, colour=WHITE, size=11)
        cell.alignment = aln()
        cell.border = bdr(style="medium")
        cell.number_format = FMT_PCT

    return ws


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "/home/user/financial-services/models")
    from build_model_part1 import build_assumptions, build_employee_data, build_tax_ni_tables

    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    build_assumptions(wb)
    build_employee_data(wb)
    build_tax_ni_tables(wb)
    build_calc_engine(wb)

    out = "/home/user/financial-services/models/pension_salary_sacrifice_PART2_TEST.xlsx"
    wb.save(out)
    print(f"Saved: {out}")
