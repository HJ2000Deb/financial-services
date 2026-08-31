#!/usr/bin/env python3
"""
desk.py - ledger and risk engine for a small self-directed equity account.

This does not connect to a broker and cannot place orders. It records trades you
have executed yourself, prices them, and refuses trades that would breach the
capital-protection rules configured for the account.

Rules enforced (see `config` in the ledger file to change them):

  Phase 1  - equity has never reached the protection threshold (default GBP 1,000).
             A circuit breaker sits at `phase1_max_drawdown` below starting capital.

  Phase 2  - equity has touched the threshold at least once. The floor becomes
             starting_capital + (1 - giveback) * (high_water_mark - starting_capital),
             i.e. you may give back at most `giveback` (default 25%) of peak
             earnings. The floor ratchets up with the high-water mark and never
             falls.

Every buy is checked against the floor on the assumption that every open
position gaps to its stop simultaneously. Stops are mandatory. Note that a stop
is not a guarantee: an overnight gap can fill you well below it.

Usage:
  desk.py init [--capital 200] [--file ledger.json]
  desk.py status
  desk.py size --entry 12.40 --stop 11.40 [--venue uk|us]
  desk.py costs --notional 200 [--venue uk|us]
  desk.py buy  --ticker LLOY --qty 300 --price 0.62 --stop 0.57 --venue uk [--thesis "..."] [--force]
  desk.py sell --ticker LLOY --qty 300 --price 0.68
  desk.py mark --ticker LLOY --price 0.65
  desk.py stop --ticker LLOY --price 0.60
  desk.py journal [-n 20]
  desk.py config [--set key=value]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP, getcontext
from pathlib import Path

getcontext().prec = 28

ZERO = Decimal("0")
DEFAULT_FILE = "ledger.json"

# Money fields stored as strings in JSON so no float rounding creeps into the ledger.
MONEY_KEYS = {
    "starting_capital", "cash", "high_water_mark", "realised_pnl",
    "qty", "avg_price", "fees_paid", "stop", "mark", "price",
    "equity", "proceeds", "cost", "fees", "pnl", "floor",
}


def D(x) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(str(x))


def money(x) -> Decimal:
    return D(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def gbp(x) -> str:
    v = money(x)
    return f"-£{abs(v):,.2f}" if v < 0 else f"£{v:,.2f}"


def pct(x) -> str:
    return f"{D(x) * 100:.2f}%"


def today() -> str:
    return date.today().isoformat()


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


DEFAULT_CONFIG = {
    # Capital protection
    "protect_threshold": "1000",      # equity level that arms the earnings floor
    "protect_giveback": "0.25",       # max fraction of peak earnings you may give back
    "phase1_max_drawdown": "0.30",    # pre-threshold circuit breaker, fraction of starting capital
    # Trade risk
    "max_risk_per_trade": "0.08",     # max fraction of equity risked between entry and stop
    "max_positions": "3",
    "min_notional": "50",             # below this, costs dominate; refuse the trade
    # Dealing costs
    "commission": "0",                # per side, GBP. Zero-commission broker assumed.
    "stamp_duty_uk": "0.005",         # 0.5% SDRT on UK share purchases only
    "fx_fee": "0.0015",               # per side on non-GBP shares
    "assumed_spread": "0.003",        # half-spread used in estimates, not in recorded fills
}


# --------------------------------------------------------------------------- IO

def load(path: Path) -> dict:
    if not path.exists():
        sys.exit(f"No ledger at {path}. Run: desk.py init --file {path}")
    return json.loads(path.read_text())


def save(path: Path, state: dict) -> None:
    path.write_text(json.dumps(state, indent=2, sort_keys=False) + "\n")


# ----------------------------------------------------------------- computations

def equity(state: dict) -> Decimal:
    mv = sum((D(p["qty"]) * D(p["mark"]) for p in state["positions"].values()), ZERO)
    return D(state["cash"]) + mv


def cfg(state: dict, key: str) -> Decimal:
    return D(state["config"][key])


def armed(state: dict) -> bool:
    """The earnings floor arms the first time equity touches the threshold."""
    return D(state["high_water_mark"]) >= cfg(state, "protect_threshold")


def floor(state: dict) -> Decimal:
    """The equity level the account must not close below."""
    start = D(state["starting_capital"])
    if not armed(state):
        return start * (Decimal("1") - cfg(state, "phase1_max_drawdown"))
    peak_earnings = D(state["high_water_mark"]) - start
    return start + peak_earnings * (Decimal("1") - cfg(state, "protect_giveback"))


def position_risk(pos: dict) -> Decimal:
    """Cash lost if this position gaps straight to its stop. Never negative:
    a position already above its stop-in-profit contributes no downside."""
    risk = D(pos["qty"]) * (D(pos["mark"]) - D(pos["stop"]))
    return risk if risk > ZERO else ZERO


def open_risk(state: dict) -> Decimal:
    return sum((position_risk(p) for p in state["positions"].values()), ZERO)


def equity_at_risk(state: dict) -> Decimal:
    """Equity if every open position stopped out at once."""
    return equity(state) - open_risk(state)


def buy_cost(state: dict, notional: Decimal, venue: str) -> Decimal:
    """Dealing costs on a purchase, excluding the spread (which is in the fill)."""
    fees = cfg(state, "commission")
    if venue == "uk":
        fees += notional * cfg(state, "stamp_duty_uk")
    else:
        fees += notional * cfg(state, "fx_fee")
    return money(fees)


def sell_cost(state: dict, notional: Decimal, venue: str) -> Decimal:
    fees = cfg(state, "commission")
    if venue != "uk":
        fees += notional * cfg(state, "fx_fee")
    return money(fees)


def breakeven(state: dict, pos: dict) -> Decimal:
    """Price at which selling the whole position returns the cash it consumed."""
    qty, venue = D(pos["qty"]), pos["venue"]
    cash_out = qty * D(pos["avg_price"]) + D(pos["fees_paid"])
    f = ZERO if venue == "uk" else cfg(state, "fx_fee")
    denom = qty * (Decimal("1") - f)
    if denom <= ZERO:
        return ZERO
    return (cash_out + cfg(state, "commission")) / denom


def update_hwm(state: dict) -> None:
    eq = equity(state)
    if eq > D(state["high_water_mark"]):
        state["high_water_mark"] = str(money(eq))


def check_halt(state: dict) -> None:
    """Trip the breaker if equity has closed at or below the protected floor."""
    eq, fl = equity(state), floor(state)
    if eq <= fl and not state["halted"]:
        state["halted"] = True
        state["halt_reason"] = (
            f"Equity {gbp(eq)} at or below protected floor {gbp(fl)} on {today()}. "
            "Close all positions and stop trading until you have reviewed the journal."
        )


# ---------------------------------------------------------------------- actions

def cmd_init(args) -> None:
    path = Path(args.file)
    if path.exists() and not args.force:
        sys.exit(f"{path} already exists. Use --force to overwrite (this destroys the journal).")
    cap = money(args.capital)
    state = {
        "currency": "GBP",
        "opened": today(),
        "starting_capital": str(cap),
        "cash": str(cap),
        "high_water_mark": str(cap),
        "realised_pnl": "0",
        "halted": False,
        "halt_reason": None,
        "positions": {},
        "trades": [],
        "config": dict(DEFAULT_CONFIG),
    }
    save(path, state)
    print(f"Opened account at {path} with {gbp(cap)}.")
    render_status(state)


def render_status(state: dict) -> None:
    eq, fl = equity(state), floor(state)
    start = D(state["starting_capital"])
    pnl = eq - start
    ret = (pnl / start) if start else ZERO
    ear = equity_at_risk(state)
    phase = "2 — earnings floor ARMED" if armed(state) else "1 — building to threshold"

    print()
    print("  ACCOUNT")
    print(f"    Equity              {gbp(eq)}")
    print(f"    Cash                {gbp(state['cash'])}")
    print(f"    Started with        {gbp(start)}")
    print(f"    P&L                 {gbp(pnl)}  ({pct(ret)})")
    print(f"    High-water mark     {gbp(state['high_water_mark'])}")
    print()
    print("  RISK")
    print(f"    Phase               {phase}")
    print(f"    Protected floor     {gbp(fl)}")
    print(f"    Headroom to floor   {gbp(eq - fl)}")
    print(f"    Open risk to stops  {gbp(open_risk(state))}")
    print(f"    Equity if all stop  {gbp(ear)}"
          + ("   *** BREACHES FLOOR ***" if ear < fl else ""))
    if not armed(state):
        gap = cfg(state, "protect_threshold") - eq
        if gap > ZERO:
            print(f"    To arm the floor    {gbp(gap)} more")

    if state["halted"]:
        print()
        print("  ** TRADING HALTED **")
        print(f"    {state['halt_reason']}")

    if state["positions"]:
        print()
        print("  POSITIONS")
        hdr = f"    {'Ticker':<8}{'Qty':>10}{'Avg':>10}{'Mark':>10}{'Stop':>10}{'Value':>11}{'P&L':>11}{'Risk':>10}  Breakeven"
        print(hdr)
        for t, p in sorted(state["positions"].items()):
            qty, avg, mk = D(p["qty"]), D(p["avg_price"]), D(p["mark"])
            val, ppl = qty * mk, qty * (mk - avg)
            print(f"    {t:<8}{qty:>10}{avg:>10}{mk:>10}{D(p['stop']):>10}"
                  f"{gbp(val):>11}{gbp(ppl):>11}{gbp(position_risk(p)):>10}"
                  f"  {money(breakeven(state, p))}")
    print()


def cmd_status(args) -> None:
    state = load(Path(args.file))
    check_halt(state)
    render_status(state)
    save(Path(args.file), state)


def cmd_size(args) -> None:
    """Largest position the rules allow, given an entry and a stop."""
    state = load(Path(args.file))
    entry, stop = D(args.entry), D(args.stop)
    if stop >= entry:
        sys.exit("Stop must be below entry for a long position.")

    eq, fl = equity(state), floor(state)
    per_share_risk = entry - stop
    stop_pct = per_share_risk / entry

    # Two independent caps: the per-trade limit and the floor itself.
    cap_trade = eq * cfg(state, "max_risk_per_trade")
    cap_floor = eq - open_risk(state) - fl
    budget = min(cap_trade, cap_floor)
    binding = "per-trade limit" if cap_trade <= cap_floor else "protected floor"

    if budget <= ZERO:
        print(f"\n  No risk budget available. Floor {gbp(fl)}, equity {gbp(eq)}, "
              f"open risk {gbp(open_risk(state))}.\n")
        return

    shares = budget / per_share_risk
    notional = shares * entry
    cash_needed = notional + buy_cost(state, notional, args.venue)
    affordable = D(state["cash"])
    if cash_needed > affordable:
        # Re-solve so notional + costs exactly consumes available cash.
        load_factor = cfg(state, "stamp_duty_uk") if args.venue == "uk" else cfg(state, "fx_fee")
        notional = (affordable - cfg(state, "commission")) / (Decimal("1") + load_factor)
        shares = notional / entry if entry else ZERO
        binding = "available cash"

    rt = buy_cost(state, notional, args.venue) + sell_cost(state, notional, args.venue)
    spread = notional * cfg(state, "assumed_spread") * 2

    print()
    print(f"  SIZING  entry {entry}  stop {stop}  ({pct(stop_pct)} away)  venue {args.venue}")
    print(f"    Risk budget         {gbp(budget)}   (binding constraint: {binding})")
    print(f"    Max shares          {shares.quantize(Decimal('0.0001'))}")
    print(f"    Notional            {gbp(notional)}")
    print(f"    Entry costs         {gbp(buy_cost(state, notional, args.venue))}")
    print(f"    Round-trip costs    {gbp(rt)} fees + {gbp(spread)} spread "
          f"= {pct((rt + spread) / notional if notional else 0)} of notional")
    print(f"    Breakeven move      {pct((rt + spread) / notional if notional else 0)} "
          "before you make a penny")
    print()


def cmd_costs(args) -> None:
    state = load(Path(args.file))
    n = D(args.notional)
    b, s = buy_cost(state, n, args.venue), sell_cost(state, n, args.venue)
    spread = n * cfg(state, "assumed_spread") * 2
    total = b + s + spread
    print()
    print(f"  ROUND-TRIP COST on {gbp(n)} ({args.venue.upper()})")
    print(f"    Buy-side fees       {gbp(b)}")
    print(f"    Sell-side fees      {gbp(s)}")
    print(f"    Spread (2 x half)   {gbp(spread)}")
    print(f"    Total               {gbp(total)}   = {pct(total / n if n else 0)} of notional")
    print(f"    You must gain       {pct(total / n if n else 0)} to break even.")
    print(f"    One trade a day     {pct(total / n if n else 0)} x 250 sessions = "
          f"{(total / n * 250 * 100):,.0f}% of notional per year in costs.")
    print()


def _record(state: dict, entry: dict) -> None:
    state["trades"].append(entry)


def cmd_buy(args) -> None:
    path = Path(args.file)
    state = load(path)
    check_halt(state)
    tkr, venue = args.ticker.upper(), args.venue
    qty, price, stop = D(args.qty), D(args.price), D(args.stop)
    breaches: list[str] = []

    if qty <= ZERO or price <= ZERO:
        sys.exit("Quantity and price must be positive.")
    if stop >= price:
        sys.exit("Stop must be below the entry price for a long position.")

    notional = qty * price
    fees = buy_cost(state, notional, venue)
    cash_needed = notional + fees

    if state["halted"]:
        breaches.append(f"account is halted: {state['halt_reason']}")
    if cash_needed > D(state["cash"]):
        breaches.append(f"needs {gbp(cash_needed)} but cash is {gbp(state['cash'])}")
    if notional < cfg(state, "min_notional"):
        breaches.append(f"notional {gbp(notional)} is below the {gbp(cfg(state, 'min_notional'))} "
                        "minimum — dealing costs would dominate")
    if tkr not in state["positions"] and len(state["positions"]) >= int(cfg(state, "max_positions")):
        breaches.append(f"already holding {len(state['positions'])} positions "
                        f"(max {int(cfg(state, 'max_positions'))})")

    trade_risk = qty * (price - stop)
    eq = equity(state)
    if trade_risk > eq * cfg(state, "max_risk_per_trade"):
        breaches.append(f"risks {gbp(trade_risk)}, over the per-trade limit of "
                        f"{gbp(eq * cfg(state, 'max_risk_per_trade'))} "
                        f"({pct(cfg(state, 'max_risk_per_trade'))} of equity)")

    # Floor test: assume this position and every existing one gaps to its stop.
    fl = floor(state)
    projected = eq - fees - open_risk(state) - trade_risk
    if projected < fl:
        breaches.append(f"if every position stopped out, equity would be {gbp(projected)}, "
                        f"below the protected floor of {gbp(fl)}")

    if breaches and not args.force:
        print("\n  TRADE REJECTED")
        for b in breaches:
            print(f"    - {b}")
        print("\n  Use --force only to record a trade you have already executed.\n")
        sys.exit(1)

    # Apply
    state["cash"] = str(money(D(state["cash"]) - cash_needed))
    if tkr in state["positions"]:
        p = state["positions"][tkr]
        old_qty, old_avg = D(p["qty"]), D(p["avg_price"])
        new_qty = old_qty + qty
        p["avg_price"] = str(((old_qty * old_avg) + notional) / new_qty)
        p["qty"] = str(new_qty)
        p["fees_paid"] = str(money(D(p["fees_paid"]) + fees))
        p["stop"] = str(stop)
        p["mark"] = str(price)
    else:
        state["positions"][tkr] = {
            "qty": str(qty), "avg_price": str(price), "venue": venue,
            "stop": str(stop), "mark": str(price), "fees_paid": str(fees),
            "opened": today(), "thesis": args.thesis or "",
        }

    _record(state, {
        "ts": now(), "action": "BUY", "ticker": tkr, "qty": str(qty), "price": str(price),
        "venue": venue, "fees": str(fees), "cost": str(money(cash_needed)),
        "stop": str(stop), "thesis": args.thesis or "",
        "forced": bool(breaches), "breaches": breaches,
    })
    update_hwm(state)
    check_halt(state)
    save(path, state)

    print(f"\n  BOUGHT {qty} {tkr} @ {price} — notional {gbp(notional)}, "
          f"fees {gbp(fees)}, total {gbp(cash_needed)}")
    if breaches:
        print("  RECORDED AS A RULE BREACH:")
        for b in breaches:
            print(f"    - {b}")
    render_status(state)


def cmd_sell(args) -> None:
    path = Path(args.file)
    state = load(path)
    tkr, price = args.ticker.upper(), D(args.price)
    if tkr not in state["positions"]:
        sys.exit(f"No position in {tkr}.")
    p = state["positions"][tkr]
    held = D(p["qty"])
    qty = held if args.qty in (None, "all") else D(args.qty)
    if qty > held:
        sys.exit(f"Holding {held} {tkr}, cannot sell {qty}.")

    notional = qty * price
    fees = sell_cost(state, notional, p["venue"])
    proceeds = notional - fees
    entry_fees_share = D(p["fees_paid"]) * (qty / held)
    pnl = notional - (qty * D(p["avg_price"])) - fees - entry_fees_share

    state["cash"] = str(money(D(state["cash"]) + proceeds))
    state["realised_pnl"] = str(money(D(state["realised_pnl"]) + pnl))
    if qty == held:
        del state["positions"][tkr]
    else:
        p["qty"] = str(held - qty)
        p["fees_paid"] = str(money(D(p["fees_paid"]) - entry_fees_share))
        p["mark"] = str(price)

    _record(state, {
        "ts": now(), "action": "SELL", "ticker": tkr, "qty": str(qty), "price": str(price),
        "venue": p["venue"], "fees": str(fees), "proceeds": str(money(proceeds)),
        "pnl": str(money(pnl)), "forced": False, "breaches": [],
    })
    update_hwm(state)
    check_halt(state)
    save(path, state)

    print(f"\n  SOLD {qty} {tkr} @ {price} — proceeds {gbp(proceeds)}, "
          f"realised {gbp(pnl)} net of all costs")
    render_status(state)


def cmd_mark(args) -> None:
    path = Path(args.file)
    state = load(path)
    tkr = args.ticker.upper()
    if tkr not in state["positions"]:
        sys.exit(f"No position in {tkr}.")
    p = state["positions"][tkr]
    p["mark"] = str(D(args.price))
    if D(args.price) <= D(p["stop"]):
        print(f"\n  ** {tkr} is at or through its stop of {p['stop']}. "
              "Sell it. The stop is the thesis being wrong. **")
    update_hwm(state)
    check_halt(state)
    save(path, state)
    render_status(state)


def cmd_stop(args) -> None:
    path = Path(args.file)
    state = load(path)
    tkr = args.ticker.upper()
    if tkr not in state["positions"]:
        sys.exit(f"No position in {tkr}.")
    p = state["positions"][tkr]
    old, new = D(p["stop"]), D(args.price)
    if new < old and not args.force:
        sys.exit(f"Refusing to widen the stop on {tkr} from {old} to {new}. "
                 "Widening a stop to avoid a loss is how small losses become large ones. "
                 "Use --force if you have a documented reason.")
    p["stop"] = str(new)
    _record(state, {"ts": now(), "action": "STOP", "ticker": tkr,
                    "price": str(new), "forced": bool(new < old), "breaches": []})
    save(path, state)
    print(f"\n  Stop on {tkr} moved {old} -> {new}")
    render_status(state)


def cmd_journal(args) -> None:
    state = load(Path(args.file))
    trades = state["trades"][-args.n:]
    if not trades:
        print("\n  No trades recorded.\n")
        return
    print()
    print(f"  {'When':<21}{'Action':<7}{'Ticker':<8}{'Qty':>10}{'Price':>10}{'P&L':>11}  Note")
    for t in trades:
        p = t.get("pnl", "")
        p = gbp(p) if p else ""
        note = t.get("thesis", "") or ("BREACH: " + "; ".join(t["breaches"]) if t.get("breaches") else "")
        print(f"  {t['ts'][:19]:<21}{t['action']:<7}{t['ticker']:<8}"
              f"{t.get('qty', ''):>10}{t.get('price', ''):>10}{p:>11}  {note[:60]}")
    print(f"\n  Realised P&L to date: {gbp(state['realised_pnl'])}\n")


def cmd_config(args) -> None:
    path = Path(args.file)
    state = load(path)
    if args.set:
        for pair in args.set:
            k, _, v = pair.partition("=")
            if k not in state["config"]:
                sys.exit(f"Unknown config key '{k}'. Known: {', '.join(sorted(state['config']))}")
            state["config"][k] = v
            print(f"  {k} = {v}")
        save(path, state)
    else:
        print()
        for k, v in state["config"].items():
            print(f"  {k:<22}{v}")
        print()


# ------------------------------------------------------------------------- main

def main(argv=None) -> None:
    ap = argparse.ArgumentParser(prog="desk.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default=DEFAULT_FILE, help="ledger file (default: ledger.json)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="open a new account")
    p.add_argument("--capital", default="200")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_init)

    sub.add_parser("status", help="equity, risk and positions").set_defaults(func=cmd_status)

    p = sub.add_parser("size", help="largest position the rules allow")
    p.add_argument("--entry", required=True)
    p.add_argument("--stop", required=True)
    p.add_argument("--venue", default="uk", choices=["uk", "us"])
    p.set_defaults(func=cmd_size)

    p = sub.add_parser("costs", help="round-trip dealing costs")
    p.add_argument("--notional", required=True)
    p.add_argument("--venue", default="uk", choices=["uk", "us"])
    p.set_defaults(func=cmd_costs)

    p = sub.add_parser("buy", help="record a purchase")
    p.add_argument("--ticker", required=True)
    p.add_argument("--qty", required=True)
    p.add_argument("--price", required=True)
    p.add_argument("--stop", required=True)
    p.add_argument("--venue", default="uk", choices=["uk", "us"])
    p.add_argument("--thesis", default="")
    p.add_argument("--force", action="store_true", help="record a trade that breaks the rules")
    p.set_defaults(func=cmd_buy)

    p = sub.add_parser("sell", help="record a sale")
    p.add_argument("--ticker", required=True)
    p.add_argument("--qty", default=None, help="quantity, or omit to sell all")
    p.add_argument("--price", required=True)
    p.set_defaults(func=cmd_sell)

    p = sub.add_parser("mark", help="update the price of a holding")
    p.add_argument("--ticker", required=True)
    p.add_argument("--price", required=True)
    p.set_defaults(func=cmd_mark)

    p = sub.add_parser("stop", help="move a stop (tightening only, unless forced)")
    p.add_argument("--ticker", required=True)
    p.add_argument("--price", required=True)
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_stop)

    p = sub.add_parser("journal", help="trade history")
    p.add_argument("-n", type=int, default=20)
    p.set_defaults(func=cmd_journal)

    p = sub.add_parser("config", help="show or change the rules")
    p.add_argument("--set", action="append", metavar="KEY=VALUE")
    p.set_defaults(func=cmd_config)

    args = ap.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
