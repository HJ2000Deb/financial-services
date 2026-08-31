---
name: catalyst-research
description: Research a listed company before trading it — business model, financial trajectory, dated catalysts, the bear case, and what is already priced in — with strict sourcing discipline. Use when researching a stock, forming or testing an investment thesis, preparing for an earnings date, screening ideas, or asking what could move a share price. Triggers on "research [company]", "what do you think of [ticker]", "should I buy", "what is the bull/bear case", "when do they report", "what is priced in", "find me some ideas".
---

# Catalyst Research

Research for a trading account has one job: work out where the user's view
differs from the market's, and what dated event will resolve the difference.
A summary of a company that everyone already agrees with has no trading value.

## Sourcing discipline — read this first

The single largest failure mode is a confidently stated number that is wrong.
On a real money account that is not a stylistic problem.

- **Never state a price, multiple, growth rate, margin or consensus figure from
  memory.** Search for it, cite it, and date it.
- Label every number as one of: **[FACT, source, date]**, **[CONSENSUS, source,
  date]**, or **[ESTIMATE — mine]**.
- Prefer primary sources: RNS announcements, the company's investor relations
  page, annual and interim reports, regulatory filings. Then reputable financial
  media. Never a content-farm summary, a forecasting site, or an SEO "stocks to
  watch today" page — several rank highly and are unreliable.
- If a figure cannot be sourced, say "I could not verify this" and carry on. An
  acknowledged gap is workable; a fabricated number is not.
- State the price and date any thesis is based on. A thesis without a reference
  price cannot be evaluated later.

## The research sequence

### 1. What does the company actually do

Revenue by segment and geography. Who pays them, how often, and what for.
Recurring versus one-off. If the revenue model cannot be explained in three
sentences, the position cannot be sized with confidence.

### 2. The financial trajectory

The second derivative matters more than the level. Markets price change.

- Revenue growth — and whether it is accelerating or decelerating
- Gross and operating margin direction over the last four to eight periods
- Free cash flow versus reported earnings (a persistent gap is a warning)
- Net debt and maturity profile — the most common cause of a permanent loss in a
  small cap is a refinancing, not a bad quarter
- Share count trend — quiet dilution offsets business progress

### 3. What is already priced in

The core question. Work out the market's implied expectation:

- Current valuation against the company's own history and its closest peers
- Consensus estimates for the next reporting period, with a source
- Recent share price behaviour — a stock up 40% into results has a high bar
- Short interest and any recent director dealings

The thesis is only tradeable where the user's expectation and the market's differ
and there is a reason for the gap.

### 4. Dated catalysts

Every thesis needs an event with a date. Build the calendar:

| Date | Event | Why it resolves the thesis |
|------|-------|---------------------------|
| | Results / trading update | Confirms or breaks the growth or margin pillar |
| | Capital markets day | Guidance reset |
| | Regulatory or clinical decision | Binary |
| | Index review, lock-up expiry, refinancing | Flow and balance sheet |

Get the date from the company's own financial calendar, not from memory.

### 5. The bear case, written properly

Write the strongest argument against the position, as though holding the short.
Then list what specific evidence would confirm it. This produces the stop level.
If the bear case cannot be articulated, the research is not finished.

### 6. Small-account filters

Applied before anything else, because they disqualify most ideas:

- **Liquidity** — average daily value traded should be at least a few hundred
  thousand pounds. Thin stocks cannot be exited on bad news at any sensible price.
- **Spread** — check the live bid and ask. A 3% spread means a 3% loss on entry.
  This alone rules out most of AIM for a £200 account.
- **Binary risk** — pre-revenue miners and single-asset biotechs are coin flips.
  A one-position account cannot survive a losing flip.
- **Reporting quality** — repeated restatements, auditor changes or delayed
  filings: skip, whatever the valuation says.

## Binary events and gap risk

Earnings and regulatory decisions do not respect stops. A 25% overnight gap fills
far below a 10% stop.

- In Phase 1 a full position may be held through results as a deliberate,
  documented decision.
- In Phase 2 it may not — a gap through the stop can breach the floor in one
  session, and the floor is the whole point of the rule.
- Either way, decide *before* the date, not during the announcement.

## Output

A thesis note the user can act on and check later:

```
TICKER — Long / Avoid
Reference price: X on DATE

Thesis (2 sentences): what must be true, and what it is worth if it is.
Pillars (3): each with the evidence behind it and a source.
Catalyst: event and date.
Bear case: the strongest argument against, and what would confirm it.
Stop: price, and the reason that price means the thesis is wrong.
Target: price, and the basis for it.
Reward-to-risk: computed.
Liquidity and spread: checked, with figures.
Unverified: anything that could not be sourced.
```

Hand the sizing to `position-sizing` and record the result with `desk.py buy`
once the user has actually dealt.
