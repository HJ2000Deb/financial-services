# Trading Desk

A self-directed equity trading operation for a small account: a ledger with a
realistic dealing-cost model, a capital-protection floor that ratchets, position
sizing, and the research discipline that has to sit in front of both.

## What this is not

It does not connect to a broker and it cannot place an order. The user deals
through their own broker and reports the fill. Nothing here predicts prices.

## Quick start

```bash
DESK=plugins/vertical-plugins/trading-desk/engine/desk.py
mkdir -p ~/trading

python3 $DESK --file ~/trading/ledger.json init --capital 200
python3 $DESK --file ~/trading/ledger.json costs --notional 200 --venue uk
python3 $DESK --file ~/trading/ledger.json size --entry 4.00 --stop 3.68 --venue uk

# after dealing through your broker:
python3 $DESK --file ~/trading/ledger.json buy \
  --ticker XYZ --qty 49 --price 4.00 --stop 3.68 --venue uk --thesis "margin inflection at H1"

python3 $DESK --file ~/trading/ledger.json mark --ticker XYZ --price 4.30
python3 $DESK --file ~/trading/ledger.json status
```

## The capital rules

**Phase 1** — equity has never touched £1,000. A circuit breaker sits 30% below
starting capital. This is a default, not a stated requirement; change it with
`config --set phase1_max_drawdown=...`.

**Phase 2** — equity has touched £1,000 at least once, permanently. The floor is

```
floor = starting_capital + 0.75 x (high_water_mark - starting_capital)
```

so at most 25% of peak earnings can be given back. The floor ratchets up with each
new high and never falls. At a £1,000 high-water mark it sits at £800.

Every buy is tested on the assumption that all open positions gap to their stops
simultaneously. If that would put equity below the floor, the trade is rejected.
Breaching the floor halts the desk.

**The crossing is discontinuous.** Touching £1,000 moves the floor from £140 to
£800 in one step and cuts permitted open risk from £60 to £200. A single all-in
position with a wide stop becomes non-compliant the moment it crosses. Derisk
before £1,000, not after.

## Why the cost model is the important part

| Broker | Round trip on £200 (UK share) | Cost of trading daily, per year |
|---|---|---|
| Zero commission | ~£2.20 (1.1%) | ~275% of the account |
| £11.95 per side | ~£25.90 (13.0%) | not survivable |

`desk.py costs` prints this for the configured broker. It is the reason the desk
reviews daily but trades rarely. A £200 account cannot outrun 1.1% per round trip
at daily frequency; no stock selection process closes that gap.

## Commands

| Command | Does |
|---|---|
| `/trading-desk:open` | Mark positions, check the floor, act on stops |
| `/trading-desk:close` | Mark to close, journal trades, note the new floor |
| `/trading-desk:research` | Research a company with sourcing discipline |
| `/trading-desk:size` | Size a trade and check it against the rules |
| `/trading-desk:risk` | Floor, headroom, and open risk to stops |
| `/trading-desk:journal` | Grade closed trades on process, not outcome |

## Skills

- `trading-operation` — operating doctrine, daily loop, buy and sell gates
- `position-sizing` — sizing, stop placement, the cost and reward-to-risk gates
- `catalyst-research` — pre-trade research and the sourcing rules
- `trade-journal` — post-trade review, process grading, honest metrics

## Configuration

```bash
python3 $DESK --file ~/trading/ledger.json config
python3 $DESK --file ~/trading/ledger.json config --set commission=0 --set fx_fee=0.0015
```

| Key | Default | Meaning |
|---|---|---|
| `protect_threshold` | 1000 | Equity level that arms the earnings floor |
| `protect_giveback` | 0.25 | Max fraction of peak earnings that may be given back |
| `phase1_max_drawdown` | 0.30 | Pre-threshold circuit breaker |
| `max_risk_per_trade` | 0.08 | Max fraction of equity risked on one idea |
| `max_positions` | 3 | Concurrent holdings |
| `min_notional` | 50 | Below this, costs dominate |
| `commission` | 0 | Per side, GBP |
| `stamp_duty_uk` | 0.005 | SDRT on UK share purchases |
| `fx_fee` | 0.0015 | Per side on non-GBP shares |
| `assumed_spread` | 0.003 | Half-spread, used in estimates only |

## Tests

```bash
cd plugins/vertical-plugins/trading-desk/engine && python3 -m unittest test_desk -v
```

## Risk warning

Capital is at risk. A single-position account can lose 30% in one session on a
profit warning, and stops do not protect against overnight gaps. Most
self-directed accounts of this size lose money. Nothing in this plugin is
financial advice or a recommendation to buy or sell any security.
