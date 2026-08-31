---
description: Open the trading day - mark positions, check the floor, act on stops
---

Load the `trading-operation` skill and run the market open routine for the user's
ledger (default `~/trading/ledger.json`; ask if it does not exist).

1. Run `desk.py status` and report the floor headroom before the P&L.
2. Ask the user for current prices on each holding, then `desk.py mark` each one.
3. Flag any holding at or through its stop — these are sells today, not decisions.
4. Note any holding with a catalyst inside 48 hours.
5. Give one short paragraph: what, if anything, needs doing today. "Nothing" is a
   complete and common answer.
