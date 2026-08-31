# Opening Brief — 31 August 2026

Account opened at £200.00. Ledger: `trading/ledger.json`. Phase 1, protected
floor £140.00.

Every figure below carries a source and a date. Anything I could not verify is
labelled. I have no live price feed in this environment — quoted levels are from
published sources on the dates shown, not live quotes. **Check every price
yourself before dealing.**

---

## 1. Where the market is

| Marker | Level | As at | Source |
|---|---|---|---|
| FTSE 100 | 10,824.26 (+0.29%) | 28 Aug 2026 close | Trading Economics |
| UK Bank Rate | 3.75%, held 6–3 | 30 Jul 2026 | CNBC / BoE |
| UK CPI | 2.9%, BoE projects 3.2% peak in Q4 | Jul 2026 print | CNBC / BoE |
| 10-year gilt | ~5.06% | 28 Aug 2026 | ts2.tech (secondary — verify) |
| Next BoE decision | 17 Sep 2026 | — | HomeOwners Alliance |

## 2. The regime

**Sticky, energy-led inflation with a hawkish drift, and a long end that is not
buying the story.**

Three things define it:

1. **The MPC is splitting hawkish.** July's hold was 6–3, with Pill, Greene and
   Mann voting to *raise* to 4% on concern that energy prices make inflation
   persistent. Five consecutive holds is not a cutting cycle on pause; it is a
   cycle that may have turned.

2. **The 10-year gilt at ~5.06% sits well above the 3.75% base rate.** That is a
   steep curve driven by term premium — inflation persistence and fiscal supply —
   not by growth optimism. It is the single most important number on this page,
   because it prices everything long-duration in the UK market.

3. **The index is near highs while the domestic economy is not.** The FTSE 100
   earns most of its revenue abroad and is weighted to energy, miners and
   defence. A record index level tells you nothing good about UK domestic
   equities, and the two are frequently mistaken for each other.

**Note on stale sell-side targets.** Search surfaced a UBS FTSE 100 base case of
10,000 for end-2026 and a Goldman forecast of 4.25% for the 10-year gilt. Both
are inconsistent with where the market actually is (10,824 and ~5.06%), which
means they are almost certainly from an earlier vintage. I am not treating either
as current. Flagging them because they will keep appearing in search results.

## 3. What the regime favours and punishes

This is the framework, not a recommendation list. Names are **research targets**
— I have not verified current prices, valuations, spreads or balance sheets for
any of them.

**Supported by the regime**

- **Energy producers** (Shell, BP). The inflation problem *is* their revenue
  line. The natural hedge if the Middle East situation persists.
- **Gold and precious metals** (Fresnillo, Endeavour Mining). Gold was noted
  firm on 28 Aug. Works on both real-rate and geopolitical stress.
- **Aerospace and defence** (BAE Systems, Melrose, Rolls-Royce). Melrose led
  gains on 28 Aug; BAE was weak, which is worth understanding before assuming
  the sector trades as one.
- **Banks** (Lloyds, NatWest, Barclays). Higher-for-longer supports net interest
  margin. The offset is credit quality if 5% gilts feed into defaults — this
  needs checking, not assuming.

**Punished by the regime**

- **REITs and property** (British Land, Land Securities, Segro). A 5% risk-free
  rate directly compresses property values. Explicitly cited as a drag on 28 Aug.
- **Utilities** (National Grid, SSE). Bond proxies, and the most rate-sensitive
  part of the index. SSE led the FTSE on 28 Aug, which cuts against this — find
  out why before extrapolating.
- **Housebuilders** (Persimmon, Barratt Redrow, Taylor Wimpey). Mortgage rates
  key off the gilt curve, not Bank Rate. At 5% the affordability maths is brutal.
- **Long-duration software** (Sage — noted weak on 28 Aug). Valuations discount
  distant cash flows at a rate that keeps rising.

**The two-sided risk on the consensus trade.** Long energy is the obvious
expression and therefore a crowded one. A Middle East ceasefire reverses it
violently and simultaneously fixes the inflation problem, which would rip the
face off the whole hawkish positioning. Anyone long energy here is short peace.
Size accordingly.

## 4. What this means for a £200 account

Honest arithmetic, ahead of any stock picking.

- **A round trip costs 1.10% of notional** (0.5% stamp duty plus an assumed 0.3%
  half-spread each way, zero commission). Trading once a day is a **275% annual
  cost drag**. There is no selection process that survives that. If your broker
  charges ~£12 a side, one round trip costs **13% of the entire account** and
  the operation is over before it starts.
- **£200 buys exactly one position.** `desk.py size` will report "available cash"
  as the binding constraint on every trade until roughly £500. The real risk is
  not the distance to the stop — it is the whole position. One profit warning is
  a 30% day.
- **The entry point is poor.** Index near highs, hawkish repricing under way, a
  hard macro catalyst on 17 September. Deploying the entire account into a single
  name the day before a rate decision that three MPC members want to be a hike is
  not a trade, it is a coin flip with costs attached.

## 5. Day 1 plan

**No position today.** That is a decision, not a delay, and it is the right one
at index highs with a dated macro event two weeks out.

1. **Confirm the broker charges zero commission.** At this account size this is
   worth more than any stock pick I could give you. If it charges per trade,
   moving is the single highest-value action available. Then:
   `desk.py config --set commission=<actual>` so the engine tells the truth.

2. **Research three names properly** with `/trading-desk:research`, one from the
   supported list and one from the punished list — understanding why something
   should fall is the cheapest way to learn to read the regime. Each needs a
   thesis, a dated catalyst, a checked spread, and a stop derived from the thesis.

3. **Put 17 September in the diary.** The BoE decision is the regime's resolution
   point. Either the hawks get their hike and the punished list gets worse, or the
   hold holds and the rate-sensitive names get their bounce. Trading before it
   without a view on it is gambling on it.

4. **Decide the structural question honestly.** The strongest expected-value
   option for £200 is a diversified low-cost fund until the account reaches
   roughly £500, at which point single-stock position sizing starts to be governed
   by risk rather than by cash. It removes single-name blowup risk and pays no
   stamp duty. It is less interesting than trading and it is very likely to beat
   trading. If you want to trade anyway — which is a legitimate choice, made with
   open eyes — the rules in this repo are built to keep it survivable.

## 6. What I will not do

- Tell you a stock will go up. Nobody knows, and a £200 account cannot absorb
  being wrong with confidence.
- Quote a price, multiple or consensus figure from memory. Every number here has
  a source and a date, or is marked unverified.
- Pretend a 1.10% round-trip cost can be traded through daily.

## Sources

- FTSE 100 close, 28 Aug 2026 — Trading Economics, uk.marketscreener.com
- BoE July decision and vote split — cnbc.com, 30 Jul 2026
- BoE September meeting date and rate forecasts — hoa.org.uk
- Gilt yield and 28 Aug sector moves — ts2.tech (secondary source, verify against
  the FT or LSE before relying on it)
- UBS and Goldman forecasts — ii.co.uk, goldmansachs.com (vintage unclear;
  inconsistent with current levels)
