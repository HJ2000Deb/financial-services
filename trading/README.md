# The account

Live ledger for the trading operation. `ledger.json` is maintained by
`plugins/vertical-plugins/trading-desk/engine/desk.py` — do not edit it by hand,
or the high-water mark and the protection floor will silently break.

Committing the ledger is deliberate: git history becomes a tamper-evident audit
trail of every fill, mark and stop change, which is the one thing a trading
journal most needs and most often lacks.

```bash
DESK="python3 plugins/vertical-plugins/trading-desk/engine/desk.py --file trading/ledger.json"

$DESK status
$DESK size --entry 4.00 --stop 3.68 --venue uk
$DESK buy --ticker XYZ --qty 49 --price 4.00 --stop 3.68 --venue uk --thesis "..."
$DESK mark --ticker XYZ --price 4.30
$DESK journal
```

Current state: opened 31 Aug 2026 with £200.00, Phase 1, protected floor £140.00.
No positions. See `notes/2026-08-31-opening-brief.md`.

Capital is at risk. Nothing here is financial advice.
