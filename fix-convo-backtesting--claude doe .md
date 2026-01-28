● The daily values are now fixed. Here are the corrected results:

  Corrected Backtest Results

  Period: Jan 2021 - Jan 2026 (5 years)
  Investment: $1,000/year = $5,000 total invested
  ┌──────────────┬────────────┬──────────────┬───────────────┐
  │    Metric    │ Value-Only │ Multi-Factor │ S&P 500 (SPY) │
  ├──────────────┼────────────┼──────────────┼───────────────┤
  │ Final Value  │ $8,999     │ $12,166      │ $8,052        │
  ├──────────────┼────────────┼──────────────┼───────────────┤
  │ Total Return │ 80.0%      │ 143.3%       │ 61.0%         │
  ├──────────────┼────────────┼──────────────┼───────────────┤
  │ CAGR         │ 54.6%      │ 64.1%        │ 51.2%         │
  ├──────────────┼────────────┼──────────────┼───────────────┤
  │ Volatility   │ 49.1%      │ 61.2%        │ 47.2%         │
  ├──────────────┼────────────┼──────────────┼───────────────┤
  │ Sharpe Ratio │ 1.03       │ 0.98         │ 1.00          │
  ├──────────────┼────────────┼──────────────┼───────────────┤
  │ Max Drawdown │ -32.2%     │ -24.7%       │ -24.5%        │
  └──────────────┴────────────┴──────────────┴───────────────┘
  ---
  How Daily Values Are Calculated

  The fix addressed tracking uninvested cash:

  1. At each rebalance date:
    - Sell all existing holdings → add proceeds to cash
    - Add $1,000 new investment to cash
    - Run strategy to select stocks
    - If stocks found: buy equally, cash goes to 0
    - If no stocks found: cash remains (e.g., Multi-Factor in 2021)
  2. Daily portfolio value = holdings value + uninvested cash

  For Multi-Factor in 2021, the $1,000 sat as cash (flat line at $1,000) until Jan 2022 when stocks were selected. Then $2,000 ($1,000 carried cash + $1,000 new) was invested.

  ---
  Key Findings (Corrected)

  - Multi-Factor significantly outperformed with $12,166 final value (+143% return) vs Value-Only's $8,999 (+80%)
  - Value-Only has better risk-adjusted returns (Sharpe 1.03 vs 0.98) due to lower volatility
  - Both strategies beat the S&P 500 benchmark ($8,052)

✻ Cooked for 4m 7s

❯ why was this done? "  For Multi-Factor in 2021, the $1,000 sat as cash (flat line at $1,000) until Jan 2022 when stocks were selected. Then $2,000 ($1,000 carried cash + $1,000 new) was invested."

● Good question. This happened because no stocks passed the Multi-Factor filters on 2021-01-04.

  The Multi-Factor strategy requires:
  1. Value filters (P/E > 0, P/E < 0.5 × Market Cap, Market Cap > $10B)
  2. EPS Growth > 0%
  3. 6-month momentum > 0%

  The problem is the momentum calculation. On 2021-01-04, we only had ~3 days of price data (data starts 2021-01-01), but momentum needs at least 20 days of history. So every stock returned None for momentum and got filtered out.

  This is a bug in the backtest setup - I should have downloaded price data starting 6 months earlier (mid-2020) to have enough history for the first rebalance.

  Let me fix this:
# 


#############################################  ############################################# 



what is a sharpe ratio?

● The Sharpe Ratio measures risk-adjusted return - how much excess return you get per unit of risk taken.

  Formula:
  Sharpe Ratio = (Portfolio Return - Risk-Free Rate) / Portfolio Volatility

  Interpretation:
  - > 1.0 = Good (extra return exceeds the risk taken)
  - > 2.0 = Very good
  - < 1.0 = The risk may not be worth the reward

  Example from the backtest:
  ┌──────────────┬───────┬────────────┬────────┐
  │   Strategy   │ CAGR  │ Volatility │ Sharpe │
  ├──────────────┼───────┼────────────┼────────┤
  │ Multi-Factor │ 68.0% │ 42.5%      │ 1.51   │
  ├──────────────┼───────┼────────────┼────────┤
  │ Value-Only   │ 54.6% │ 49.1%      │ 1.03   │
  ├──────────────┼───────┼────────────┼────────┤
  │ S&P 500      │ 51.2% │ 47.2%      │ 1.00   │
  └──────────────┴───────┴────────────┴────────┘
  Multi-Factor has the best Sharpe (1.51) because it achieved higher returns (68%) with lower volatility (42.5%) than the others. Value-Only had higher returns than S&P 500, but also higher volatility, so its Sharpe is only slightly better.

  In plain terms: Sharpe tells you if you're being adequately compensated for the risk. A high-return strategy with wild swings might have a lower Sharpe than a moderate-return strategy with steady gains.








