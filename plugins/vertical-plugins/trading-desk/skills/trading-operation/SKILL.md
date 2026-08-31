---
name: trading-operation
description: Operating doctrine for running a small self-directed equity account end to end — daily routine, capital-protection rules, dealing-cost arithmetic, and the decision loop from idea to exit. Use when the user wants to run their trading account, asks "what should I do today", opens or closes the trading day, reviews account risk, or asks whether a trade fits the rules. Triggers on "run the desk", "trading day", "open the desk", "close the desk", "my portfolio", "should I buy", "am I within my risk rules".
---

# Trading Operation

The operating doctrine for a small self-directed equity account. Everything here
assumes the user places their own orders through their own broker. **This skill
never places a trade and must never imply that it has.** It records, prices,
checks, and advises.

## The engine

All account state lives in a ledger file driven by
`${CLAUDE_PLUGIN_ROOT}/engine/desk.py`. Never edit the ledger JSON by hand — the
engine maintains the high-water mark and the protection floor, and hand-edits
silently break both.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/engine/desk.py" --file ~/trading/ledger.json status
```

Common calls: `init`, `status`, `size`, `costs`, `buy`, `sell`, `mark`, `stop`,
`journal`, `config`. Run with `--help` for arguments.

## The three constraints that govern everything

Before any idea is discussed, these are the facts of a small account. State them
plainly whenever the user proposes something that ignores them.

### 1. Dealing costs, not stock picking, decide the outcome

Run `desk.py costs --notional <size>` and show the user the number. On a
zero-commission broker a round trip costs roughly 0.9–1.1% of notional once
stamp duty, FX and the spread are counted. On a flat-fee broker charging around
£12 a side, one round trip on £200 costs about 12% of the whole account.

The consequence is arithmetic, not opinion: **trading once a day costs roughly
225–275% of the account per year.** No edge survives that. A small account is
viable only if it trades rarely.

If the user's broker charges per-trade commission, the first and highest-value
action is moving to a zero-commission one. Set it with
`desk.py config --set commission=0`.

### 2. £200 buys one position, so single-name risk is total

Position size is limited by cash, not by the risk rules, until roughly £500.
`desk.py size` reports which constraint binds; below £500 it will almost always
say "available cash". Say so explicitly rather than presenting a fully-invested
single position as a diversified portfolio. One position means one earnings
miss, one profit warning, one fraud can take the account down 30% in a session.

### 3. Stops leak

A stop is an order to sell at market once a price trades, not a guarantee of
that price. Overnight gaps, profit warnings and takeover announcements fill well
through stops. Size on the assumption a stop can slip, and never hold a full
position into a scheduled binary event (see `catalyst-research`).

## The capital rules

Two phases, both enforced by the engine.

**Phase 1 — below the threshold.** Equity has never touched £1,000. A circuit
breaker sits 30% below starting capital (£140 on £200). This is not the user's
stated rule; it is a default so that the account cannot go to zero while it is
unprotected. It is configurable via `phase1_max_drawdown`.

**Phase 2 — armed.** Equity has touched £1,000 at least once. The floor becomes:

```
floor = starting_capital + 0.75 x (high_water_mark - starting_capital)
```

At a £1,000 high-water mark the floor is £800. The floor ratchets up with every
new high and never falls, so 75% of every pound earned is permanently locked in.

**The discontinuity is the trap.** The instant equity touches £1,000 the floor
jumps from £140 to £800. Total permitted open risk collapses from £60 to £200.
A single all-in position with a 20% stop carries roughly £200 of risk and becomes
non-compliant the moment it crosses — forcing a sale at whatever price the market
offers that day.

So plan the approach to £1,000 deliberately:

- From about £850, tighten stops on the way up rather than after the crossing.
- Consider taking the position size down before the crossing, not after it.
- `desk.py status` shows "Equity if all stop" against the floor. Watch that line,
  not the equity line.

## The daily loop

The account should not trade daily. It should be *reviewed* daily and *traded*
when a thesis or a stop says so.

**Open (10 minutes).**
1. `desk.py status` — read the floor headroom first, the P&L second.
2. `desk.py mark` each holding with the current price.
3. Any holding at or through its stop: sell it today. No exceptions, no "let me
   see if it recovers". That is the single rule that keeps the floor intact.
4. Check the catalyst calendar for holdings (see `catalyst-research`). Anything
   reporting in the next 48 hours needs a size decision before it reports.

**During the day.** Do nothing unless a stop triggers or a pre-planned entry
level trades. Reacting to intraday moves on a £200 account converts the spread
into a wealth transfer.

**Close (10 minutes).**
1. Mark everything to the close.
2. If the day produced a trade, journal it while it is fresh (`trade-journal`).
3. If the account made a new high, note the new floor.

**Weekly.** Review the thesis on every holding. Review the journal for repeated
mistakes. This is where decisions get made.

## Deciding to buy

Never propose a buy that has not passed all five:

1. **A written thesis** — what has to be true, by when, and what it is worth if
   it is. One or two sentences. If it cannot be written down it does not exist.
2. **A dated catalyst** — the event that makes the market agree with you. A
   thesis without a catalyst is an opinion with a financing cost.
3. **A stop derived from the thesis** — the price at which the thesis is wrong,
   not a round percentage. Set before entry.
4. **Sizing from `desk.py size`** — with the entry and the thesis-derived stop.
5. **Costs checked** — `desk.py costs` on the notional. If the expected move is
   less than about three times the round-trip cost, the trade is not worth doing.

Then the user places the order themselves and reports the fill, which is recorded
with `desk.py buy`.

## Deciding to sell

Sell for one of exactly three reasons, and say which one:

- **The stop hit.** Mechanical. Same day.
- **The thesis played out.** The catalyst happened and the price reflects it.
- **The thesis broke.** New information invalidates a pillar, regardless of price.

"It has gone up a lot" and "it has gone down a lot" are not reasons. Boredom is
not a reason.

## Rules that are not negotiable

- Every position has a stop, set at entry.
- Stops move up, never down. The engine refuses to widen one without `--force`.
- Never average down. Adding to a loser doubles a position whose thesis is
  already failing.
- No leverage, no CFDs, no spread bets, no options. On £200 these convert a
  volatile account into a terminal one.
- No position held full-size into scheduled earnings while in Phase 2.
- If the desk halts, it stays halted until the journal has been reviewed and the
  user has written down what changed.

## What to tell the user, honestly

- Nobody can see gains or risks before they happen. Research shifts the odds; it
  does not remove the possibility of a total loss on any single name.
- "Grow the money each day" is not an achievable target and pursuing it is the
  most reliable way to lose the £200. Daily-frequency trading guarantees the cost
  drag above. Measure daily; decide weekly.
- Most self-directed accounts of this size lose money. Say so once, clearly, and
  then do the work well rather than repeating the warning.
- Never state a market number without a source and a date. See
  `catalyst-research` for the sourcing discipline.
