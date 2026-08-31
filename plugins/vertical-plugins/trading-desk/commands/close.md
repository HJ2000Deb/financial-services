---
description: Close the trading day - mark to close, journal any trades, note the floor
---

Load the `trading-operation` skill and run the close routine.

1. Mark every holding to the closing price via `desk.py mark`.
2. Run `desk.py status`. If the account made a new high-water mark, state the new
   protected floor.
3. If any trade was executed today, load `trade-journal` and record the reasoning
   while it is fresh.
4. Report the day in three lines: equity, change, and headroom to the floor.
