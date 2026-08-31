---
name: position-sizing
description: Size an equity position from an entry price and a thesis-derived stop, under a hard capital-protection floor and a realistic dealing-cost model. Use when deciding how many shares to buy, where to place a stop, whether a trade is worth its costs, or how much risk an account can carry. Triggers on "how many shares", "position size", "where should my stop go", "how much should I put in", "can I afford this trade", "what is my risk budget".
---

# Position Sizing

Sizing is the only part of trading fully under the user's control. Entry timing
and outcomes are not.

## The calculation

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/engine/desk.py" --file <ledger> \
  size --entry 4.00 --stop 3.68 --venue uk
```

The engine takes the smaller of three caps and reports which one binds:

| Cap | Meaning |
|-----|---------|
| Per-trade limit | `max_risk_per_trade` x equity — the most that may be lost on one idea |
| Protected floor | equity − existing open risk − floor — what the account can still afford to lose in total |
| Available cash | notional plus entry costs cannot exceed cash |

Shares = risk budget ÷ (entry − stop).

## Read the binding constraint out loud

It tells the user what kind of account they are running.

- **"available cash"** — the account is too small for the risk rules to bite. The
  user is fully invested in one name and the real risk is the whole position, not
  the distance to the stop. This is the normal state below about £500. Say it
  plainly every time rather than letting the risk-budget number imply safety.
- **"per-trade limit"** — the account is behaving normally.
- **"protected floor"** — the account is close to its floor. Size is being
  squeezed deliberately. Do not work around it.

## Placing the stop

The stop comes from the thesis, then sizing follows. Never the reverse — choosing
a stop to justify a size is how accounts die.

Reasonable anchors, in order of preference:

1. **Structural** — below the low that would mean the setup failed, or below the
   level that invalidates a thesis pillar.
2. **Volatility-scaled** — a multiple (2–3x) of the stock's average daily range,
   so ordinary noise does not stop the position out.
3. **Percentage** — a last resort. A round 10% has no relationship to the stock.

A stop closer than about 2x the round-trip cost is noise: the spread alone will
trigger it.

## The cost gate

Before recommending any trade, run:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/engine/desk.py" --file <ledger> costs --notional 200 --venue uk
```

Compare the expected move to the round-trip cost. **Require at least 3x.** If the
thesis targets a 2% move and the round trip costs 1.1%, the trade needs to be
right more than 70% of the time simply to break even after costs. It will not be.

## Reward-to-risk

Compute it explicitly and refuse trades below 2:1.

```
reward-to-risk = (target − entry) / (entry − stop)
```

The target must come from the thesis — a valuation level, a prior high, an
analyst consensus figure with a source. A target reverse-engineered to make the
ratio work is not a target.

At 2:1 with costs, roughly a 40% hit rate breaks even. Below 2:1 the required hit
rate climbs past what any retail process achieves.

## Venue matters on a small account

- **UK shares**: 0.5% stamp duty on purchases, none on sales. No FX.
- **UK AIM shares**: no stamp duty, but spreads are frequently 2–5%, which is far
  worse than the duty saved. Check the actual quoted spread before assuming AIM
  is cheaper.
- **US shares**: no stamp duty, but FX conversion each way (0.15% on a good
  broker, up to 1.5% on a bad one). Adds currency risk to single-stock risk.
- **Investment trusts and ETFs**: no stamp duty. Instant diversification, which
  is the one genuine structural advantage available to a £200 account.

## Scaling

- **Adding to winners** is allowed. Re-run `size` on the incremental amount and
  move the stop up so total open risk does not rise.
- **Adding to losers is prohibited.** The thesis is failing; doubling the
  position increases exposure to a thesis with fresh evidence against it.
- **Trimming** into strength is how Phase 2 compliance is maintained without
  giving up the position entirely.

## Approaching the £1,000 threshold

Total permitted open risk drops from £60 to £200 — but on an account that has
grown to £1,000 in a single position, actual open risk is typically £200–300.
The crossing therefore forces action.

From about £850, size the account so that the crossing is a non-event: tighten
stops progressively, or trim so that "Equity if all stop" in `desk.py status`
already sits above £800 before the threshold is reached.
