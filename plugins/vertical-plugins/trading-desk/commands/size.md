---
description: Size a trade and check it against the risk rules
argument-hint: "[ticker] [entry] [stop]"
---

Load the `position-sizing` skill.

Run `desk.py size` with the entry and stop, and `desk.py costs` on the resulting
notional. Report the binding constraint in plain words, the reward-to-risk against
the thesis target, and whether the expected move clears the 3x cost hurdle.

If the trade fails a gate, say which one and what would have to change. Do not
propose working around it.
