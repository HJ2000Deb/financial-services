---
name: trade-journal
description: Record and review closed trades to separate process quality from luck, and to find repeated mistakes. Use after closing a position, during a weekly or monthly account review, or when the user asks how their trading is actually going. Triggers on "journal this trade", "review my trades", "how am I doing", "weekly review", "what am I doing wrong", "post-mortem".
---

# Trade Journal

The journal exists to answer one question: **is the process working, or has the
account been lucky?** On a sample of a few dozen trades, P&L alone cannot tell
you. The journal can.

## Recording

The engine already logs every fill, its costs and its realised P&L:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/engine/desk.py" --file <ledger> journal -n 20
```

What the engine cannot capture is the reasoning. Keep a note per closed trade
alongside the ledger:

```
TICKER   opened DATE @ PRICE   closed DATE @ PRICE   net P&L
Thesis:        what I expected
Catalyst:      the event I was trading
Exit reason:   stop hit / thesis played out / thesis broke / undisciplined
Was the process right?   yes / no   — independent of whether it made money
What I would do again:
What I would not:
```

## The distinction that matters

Grade the decision, not the outcome. Four cases:

|  | Made money | Lost money |
|---|---|---|
| **Good process** | Repeat it | Repeat it — this is the cost of doing business |
| **Bad process** | Dangerous. The most damaging trades are the undisciplined ones that worked | Obvious lesson. Cheapest of the four |

The top-right cell is the one that ends accounts. A rule broken profitably gets
broken again, at size, at the worst moment. When the journal shows one, name it
explicitly rather than letting the profit excuse it.

## Metrics worth tracking

Recompute at each review from `desk.py journal`:

- **Hit rate** — fraction of trades closed profitably
- **Average win / average loss** — the ratio that actually determines whether a
  hit rate is good enough. 40% winners at 3:1 beats 70% winners at 0.5:1
- **Total costs paid** — sum of fees and estimated spread. Compare directly to
  net P&L. If costs exceed profits, the problem is trade frequency, not selection
- **Trades taken versus theses written** — the gap is impulse trading
- **Rule breaches** — trades recorded with `--force`. Any breach is a finding
- **Largest loss** — against the per-trade risk limit. If it exceeded the limit,
  a stop slipped or was ignored; find out which

## Weekly review

1. Run `journal` and `status`.
2. Grade every closed trade on process, using the table above.
3. Total the costs. State them as a percentage of the account.
4. Check open theses: is each still intact, and is each catalyst still dated?
5. Note the current floor and the headroom to it.
6. Write one sentence on what changes next week. One, not five.

## Monthly review

Add:

- P&L against a do-nothing benchmark (a broad index tracker over the same
  period). If the account is behind the benchmark, the activity is destroying
  value and should be reduced. This comparison is uncomfortable and is the single
  most useful number in the journal.
- Hit rate and win/loss ratio over all trades to date.
- Whether the observed edge is distinguishable from luck. With fewer than about
  30 trades it generally is not — say so rather than drawing conclusions from a
  small sample.

## Honesty rules

- Report losses in the same tone as gains.
- Never retro-fit a thesis to explain a trade that worked by accident.
- If the account is down, say so directly and quantify it against the floor.
- A run of wins is not evidence of skill at this sample size. Say that too,
  especially when the user is confident.
