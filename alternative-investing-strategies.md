I'm backtesting multiple investing strategies but would like to explore other potential avenues of investing. You've summarized previous approaches to invseting, what
  other ways exist to maximize an investment strategy? this will be benchmarked against a simple S&P500 invested or similar mix into those kinds of funds

● Let me review the existing strategies and analysis in your project to understand what's been explored.

● Read(investment-strategy-analysis.md)
  ⎿  Read 208 lines

● Read(backtest-analysis.md)
  ⎿  Read 331 lines

● Based on your existing work, you've tested Value, Momentum, Quality (EPS growth), and a Multi-Factor composite against the S&P 500 benchmark. Your V2.1 approach delivered +5%
  alpha with proper methodology.

  Here are additional strategies worth exploring, organized by category:

  ---
  Factor-Based (Beyond Your Current Factors)
  ┌─────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────┬───────────────────────────┬───────────────────────────────┐
  │              Strategy               │                                 Core Idea                                 │     Historical Alpha      │          Data Needed          │
  ├─────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────┼───────────────────────────┼───────────────────────────────┤
  │ Low Volatility                      │ Stocks with lower price volatility outperform on risk-adjusted basis      │ 2-4% with lower drawdowns │ Daily price history           │
  ├─────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────┼───────────────────────────┼───────────────────────────────┤
  │ Shareholder Yield                   │ Dividends + net buybacks outperform dividend-only                         │ 2-5%                      │ Dividend + shares outstanding │
  ├─────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────┼───────────────────────────┼───────────────────────────────┤
  │ Profitability (Gross Profit/Assets) │ Novy-Marx factor: gross profit margin is more predictive than net margins │ 3-5%                      │ Income statement data         │
  ├─────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────┼───────────────────────────┼───────────────────────────────┤
  │ Accruals Anomaly                    │ Companies with low accruals (high cash-to-earnings ratio) outperform      │ 2-4%                      │ Cash flow statement           │
  ├─────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────┼───────────────────────────┼───────────────────────────────┤
  │ Net Payout Yield                    │ Combines dividends + buybacks - dilution                                  │ 3-5%                      │ Share count changes           │
  └─────────────────────────────────────┴───────────────────────────────────────────────────────────────────────────┴───────────────────────────┴───────────────────────────────┘
  ---
  Timing & Rotation Strategies
  ┌───────────────────────────┬──────────────────────────────────────────────────────────────────────────────────────────┬───────────────────────────────┬─────────────────┐
  │         Strategy          │                                        Core Idea                                         │        Historical CAGR        │   Complexity    │
  ├───────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────┼─────────────────┤
  │ Dual Momentum (Antonacci) │ Hold assets only when both absolute & relative momentum are positive; else cash          │ 15-17%                        │ Low - uses ETFs │
  ├───────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────┼─────────────────┤
  │ Trend Following (SMA)     │ Hold SPY when above 200-day SMA, else bonds/cash                                         │ 10-11% with 50% less drawdown │ Very low        │
  ├───────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────┼─────────────────┤
  │ Risk Parity               │ Allocate based on volatility, not capital (60/40 but volatility-balanced)                │ 8-10% with lower vol          │ Medium          │
  ├───────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────┼─────────────────┤
  │ Sector Rotation           │ Overweight sectors based on economic cycle (early cycle = industrials, late = utilities) │ 2-3% alpha                    │ Medium          │
  ├───────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────┼─────────────────┤
  │ Seasonal Strategies       │ "Sell in May" or tax-loss harvesting effects                                             │ 1-2%                          │ Low             │
  └───────────────────────────┴──────────────────────────────────────────────────────────────────────────────────────────┴───────────────────────────────┴─────────────────┘
  ---
  Alternative Portfolio Construction
  ┌──────────────────────┬─────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────┐
  │       Strategy       │                  Core Idea                  │                               Best For                               │
  ├──────────────────────┼─────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────┤
  │ Equal Weight S&P 500 │ Equal allocation vs market-cap weight       │ Captures small-cap premium within large caps (+1%/year historically) │
  ├──────────────────────┼─────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────┤
  │ Permanent Portfolio  │ 25% each: stocks, bonds, gold, cash         │ Capital preservation with modest growth                              │
  ├──────────────────────┼─────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────┤
  │ All-Weather (Dalio)  │ Risk parity across growth/inflation regimes │ Smooth returns across economic environments                          │
  ├──────────────────────┼─────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────┤
  │ Barbell Strategy     │ 90% safe assets + 10% highly speculative    │ Asymmetric risk/reward                                               │
  └──────────────────────┴─────────────────────────────────────────────┴──────────────────────────────────────────────────────────────────────┘
  ---
  Quantitative/Event-Driven
  ┌─────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────┬─────────────────────┐
  │                Strategy                 │                                 Core Idea                                 │  Historical Alpha   │
  ├─────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────┼─────────────────────┤
  │ Post-Earnings Announcement Drift (PEAD) │ Buy stocks with positive earnings surprises, ride momentum for 60-90 days │ 3-5%                │
  ├─────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────┼─────────────────────┤
  │ Spinoffs                                │ Companies that spin off divisions tend to outperform                      │ 10-15% over 3 years │
  ├─────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────┼─────────────────────┤
  │ Insider Buying                          │ Follow cluster insider purchases (3+ insiders)                            │ 5-10%               │
  ├─────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────┼─────────────────────┤
  │ Buyback Announcements                   │ Companies announcing buybacks outperform                                  │ 2-4%                │
  ├─────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────┼─────────────────────┤
  │ Short Interest Squeeze                  │ Low float + high short interest = squeeze potential                       │ High variance       │
  └─────────────────────────────────────────┴───────────────────────────────────────────────────────────────────────────┴─────────────────────┘
  ---
  Income/Yield Strategies
  ┌───────────────────────────┬─────────────────────────────────────────────────────────┬───────────────────────────────────────┐
  │         Strategy          │                        Core Idea                        │            Yield + Growth             │
  ├───────────────────────────┼─────────────────────────────────────────────────────────┼───────────────────────────────────────┤
  │ Dividend Aristocrats      │ 25+ years of consecutive dividend growth                │ 10-12% total return, lower volatility │
  ├───────────────────────────┼─────────────────────────────────────────────────────────┼───────────────────────────────────────┤
  │ Dividend Growth           │ Focus on dividend growth rate rather than current yield │ Better tax efficiency                 │
  ├───────────────────────────┼─────────────────────────────────────────────────────────┼───────────────────────────────────────┤
  │ Covered Calls (Buy-Write) │ Sell calls on holdings to generate premium              │ Enhanced yield in sideways markets    │
  └───────────────────────────┴─────────────────────────────────────────────────────────┴───────────────────────────────────────┘
  ---
  Recommended Next Steps

  Given your existing infrastructure, the easiest to implement with your current data sources:

  1. Low Volatility - Only needs price history (you have this via yfinance)
  2. Dual Momentum - Can implement with ETFs (SPY, EFA, BND, SHY)
  3. Equal Weight - Simple modification of your existing approach
  4. Post-Earnings Drift - yfinance has earnings dates

  Highest academic support for long-term alpha:
  1. Profitability (Gross Profit/Assets) - Novy-Marx 2013 paper
  2. Shareholder Yield - Mebane Faber research
  3. Dual Momentum - Gary Antonacci research with 40+ year backtests

  ---
  Hybrid Approach Worth Testing

  Combine your Multi-Factor with timing:

  IF SPY > 200-day SMA:
      Run Multi-Factor stock selection (your V2.1)
  ELSE:
      Move to bonds/cash

  This overlay historically reduces max drawdown by 30-50% while preserving most upside. It would have kept you out of the 2022 bear market.