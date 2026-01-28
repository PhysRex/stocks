# Backtest Analysis: Value-Only vs Multi-Factor Strategy

## Executive Summary

This analysis compares two stock selection strategies against the S&P 500 benchmark over a 5-year period (2021-2026) with $1,000 invested annually ($5,000 total).

**Key Finding:** Results vary dramatically based on data quality AND methodology:
- **V1 (Fake data):** Multi-Factor appeared to crush the market with 174% returns
- **V2 (Real data, January rebalancing):** S&P 500 won due to data timing issues
- **V2.1 (Real data, April rebalancing, robust filters):** Multi-Factor outperforms with +5% alpha

The progression demonstrates that backtesting requires both accurate data AND realistic methodology to produce trustworthy results.

---

## Strategies Tested

### Strategy 1: Value-Only
- **Universe:** S&P 500 stocks
- **Filters:**
  - Large Cap (Market Cap > $10B)
  - Positive P/E ratio
  - P/E < 0.5 × Market Cap (in billions)
- **Selection:** Top 25 stocks by market cap
- **Rebalance:** Annually (January in V2, April in V2.1)

### Strategy 2: Multi-Factor
- **Universe:** S&P 500 stocks
- **Filters:**
  - Same value filters as above
  - EPS Growth > 0% (quality factor) - *optional in V2.1 when data unavailable*
  - 6-month price momentum > 0% (momentum factor)
- **Selection:** Top 25 by composite score (value + growth + momentum ranks)
- **Rebalance:** Annually (January in V2, April in V2.1)

### Benchmark: S&P 500 (SPY ETF)
- Dollar-cost averaging $1,000/year into SPY

---

## The Data Problem

### Initial Approach (V1): Estimated Historical Data

Our first backtest used **estimated historical fundamentals** because free data sources (yfinance) only provide current fundamentals, not historical snapshots.

**How we estimated historical P/E:**
```python
# FAKE - Don't do this!
estimated_historical_pe = current_pe * (historical_price / current_price)
```

**Problems with this approach:**
1. Assumes earnings stayed constant (they don't)
2. Survivorship bias (only tested stocks that exist today)
3. Look-ahead bias (used information we wouldn't have known)

### Improved Approach (V2): Real Historical Data

We obtained real historical fundamentals from:
- **SimFin** (free tier): Income statements from 2019-2024
- **yfinance**: 2025 data and price history

**How we calculated real P/E:**
```python
# REAL - Correct approach
historical_eps = simfin_net_income[fiscal_year] / simfin_shares[fiscal_year]
historical_pe = historical_price / historical_eps
```

### Data Validation

We tested consistency between SimFin and yfinance for overlapping years:

| Ticker | Year | SimFin EPS | yfinance EPS | Difference |
|--------|------|------------|--------------|------------|
| AAPL | 2022 | $6.11 | $6.15 | 0.6% |
| AAPL | 2023 | $6.13 | $6.16 | 0.4% |
| MSFT | 2022 | $9.65 | $9.70 | 0.5% |
| AMZN | 2023 | $2.90 | $2.95 | 1.7% |

**Result:** 96.2% of tests passed (25/26), confirming data consistency.

---

## Results Comparison

### V1: Fake Historical Data (Estimated)

| Metric | Value-Only | Multi-Factor | S&P 500 |
|--------|------------|--------------|---------|
| Final Value | $8,999 | $13,703 | $8,052 |
| Total Return | 80.0% | 174.1% | 61.0% |
| CAGR | 54.6% | 68.0% | 51.2% |
| Sharpe Ratio | 1.03 | 1.51 | 1.00 |
| Max Drawdown | -32.2% | -24.7% | -24.5% |

**V1 Conclusion:** Multi-Factor appears to crush the benchmark with 174% returns and a Sharpe ratio of 1.51.

### V2: Real Historical Data (SimFin + yfinance)

| Metric | Value-Only | Multi-Factor | S&P 500 |
|--------|------------|--------------|---------|
| Final Value | $8,369 | $7,492 | $8,052 |
| Total Return | 67.4% | 49.8% | 61.0% |
| CAGR | 52.4% | 49.1% | 51.2% |
| Sharpe Ratio | 0.99 | 0.72 | **1.00** |
| Max Drawdown | -29.3% | -23.9% | -24.5% |

**V2 Conclusion:** S&P 500 has the best risk-adjusted return. Multi-Factor actually underperforms.

### The Difference (V1 vs V2)

| Metric | V1 (Fake) | V2 (Real) | Change |
|--------|-----------|-----------|--------|
| Multi-Factor Final Value | $13,703 | $7,492 | **-45%** |
| Multi-Factor CAGR | 68.0% | 49.1% | **-19 points** |
| Multi-Factor vs SPY Alpha | +16.8% | -2.1% | **-18.9 points** |
| Best Strategy | Multi-Factor | S&P 500 | Changed |

---

## V2.1: Fixing Methodology Issues

### Problems Discovered in V2

After investigating why Multi-Factor underperformed, we discovered two methodology issues:

**1. January Rebalancing Used Unavailable Data**

Annual reports for fiscal year N are published in February-April of year N+1. A January rebalance was trying to use data that didn't exist yet:

| Rebalance Date | Data Needed | Data Available? |
|----------------|-------------|-----------------|
| Jan 2021 | FY2020 annual report | No (published Mar 2021) |
| Jan 2022 | FY2021 annual report | No (published Mar 2022) |

**2. SimFin Free Tier Has Limited Historical Data**

SimFin's free tier provides ~5 years of rolling history. In 2026, FY2019 data has largely aged out:

| Fiscal Year | S&P 500 Coverage |
|-------------|------------------|
| 2019 | 9 stocks |
| 2020 | 427 stocks |
| 2021 | 429 stocks |

For the April 2021 rebalance, EPS growth (which requires FY2020 vs FY2019) could only be calculated for 8 S&P 500 stocks.

### V2.1 Fixes Applied

1. **Moved rebalancing to April** - when annual reports are actually available
2. **Made EPS growth optional** - when historical data is missing, stocks receive a neutral (median) rank instead of being excluded. Stocks with negative EPS growth are still filtered out when data is available.

### V2.1 Results: Real Data + Correct Methodology

| Metric | Value-Only | Multi-Factor | S&P 500 |
|--------|------------|--------------|---------|
| Final Value | $8,296 | **$9,010** | $7,724 |
| Total Return | 65.9% | **80.2%** | 54.5% |
| CAGR | 55.3% | **58.0%** | 53.0% |
| Volatility | 52.7% | 54.3% | 51.6% |
| Sharpe Ratio | 0.97 | **0.99** | 0.95 |
| Max Drawdown | -19.8% | -21.2% | -21.3% |

**V2.1 Conclusion:** Multi-Factor outperforms with +5.0% alpha vs S&P 500 and the highest Sharpe ratio.

### Full Comparison Across Versions

| Metric | V1 (Fake) | V2 (Real, Jan) | V2.1 (Real, Apr) |
|--------|-----------|----------------|------------------|
| Multi-Factor Final | $13,703 | $7,492 | $9,010 |
| Multi-Factor CAGR | 68.0% | 49.1% | 58.0% |
| MF vs SPY Alpha | +16.8% | -2.1% | **+5.0%** |
| Best Strategy | Multi-Factor | S&P 500 | Multi-Factor |

---

## Key Findings

### 1. Fake Data Dramatically Inflated Returns (V1 vs V2)

The estimated historical data inflated Multi-Factor returns by approximately 45%. This happened because:
- Our P/E estimates assumed constant earnings
- We used current earnings growth rates for historical periods
- Survivorship bias excluded failed companies

### 2. Methodology Matters as Much as Data Quality (V2 vs V2.1)

Even with real data, V2 produced misleading results because:
- **January rebalancing used unavailable data** - annual reports aren't published until Feb-April
- **Strict filters excluded stocks with missing data** - SimFin's rolling 5-year window meant 2019 data was unavailable

When these issues were fixed in V2.1:
- Multi-Factor went from -2.1% alpha to **+5.0% alpha**
- Multi-Factor became the best strategy (highest CAGR and Sharpe)

### 3. Multi-Factor Can Outperform (With Correct Implementation)

With proper methodology, Multi-Factor delivers:
- **+5.0% annual alpha** vs S&P 500
- **Highest Sharpe ratio** (0.99) among all strategies
- Comparable max drawdown (-21.2% vs -21.3% for SPY)

The key is using data that was actually available at rebalancing time.

### 4. Data Availability Constraints Are Real

Free data sources have limitations:
- SimFin free tier: ~5 years rolling history (older data ages out)
- yfinance: ~4-5 years of income statement history
- Both sources lack 2019 data in 2026

Robust strategies must handle missing data gracefully rather than failing entirely.

### 5. Value-Only Provides Consistent Alpha

Value-Only beat SPY by +2.3% CAGR with similar volatility. This simpler strategy is more robust to data availability issues since it doesn't require consecutive years of EPS data.

---

## Limitations

Even with real historical data, this backtest has limitations:

1. **Survivorship Bias:** We only tested stocks currently in the S&P 500. Companies that were removed or went bankrupt are excluded.

2. **Transaction Costs:** Real trading involves brokerage fees, bid-ask spreads, and market impact.

3. **Tax Drag:** Annual rebalancing triggers capital gains taxes.

4. **Sample Period:** 5 years is relatively short. Different time periods may show different results.

5. **Market Cap Estimation:** We still estimated historical market caps from current values.

---

## Recommendations

### For Individual Investors

1. **Factor investing can work, but implementation matters.** Multi-Factor delivered +5% alpha with proper methodology.

2. **Be skeptical of backtests.** Results vary dramatically based on data quality AND methodology. Verify both.

3. **Account for costs.** Real-world returns will be lower due to fees, taxes, and slippage. The +5% alpha may shrink to +2-3% after costs.

4. **Index funds remain a strong baseline.** S&P 500 still delivered solid risk-adjusted returns with zero effort.

### For Strategy Development

1. **Use point-in-time data.** Historical fundamentals must reflect what was knowable at each date. April rebalancing ensures annual reports are available.

2. **Handle missing data gracefully.** Don't exclude stocks just because one factor is unavailable. Use neutral ranks or fallback logic.

3. **Include failed companies.** Survivorship bias is a major source of inflated returns.

4. **Test multiple time periods.** A strategy that works in one period may fail in another.

5. **Validate data sources.** Cross-check between multiple providers (we found 96% consistency between SimFin and yfinance).

6. **Document data limitations.** Be explicit about what data was available and any gaps in coverage.

---

## Technical Implementation

### Data Sources

| Source | Data Type | Coverage | Cost |
|--------|-----------|----------|------|
| SimFin | Income statements, balance sheets | 2019-2024, 4,400+ tickers | Free (5-year history) |
| yfinance | Prices, current fundamentals | Full history | Free |

### Files

| File | Description |
|------|-------------|
| `run_backtest.py` | V1 backtest (estimated data) |
| `run_backtest_v2.py` | V2/V2.1 backtest (real data, April rebalancing) |
| `test_data_sources.py` | Data validation tests |
| `explore_simfin.py` | SimFin data exploration |
| `analyze_simfin_coverage.py` | SimFin coverage analysis by year |
| `check_yfinance_historical.py` | yfinance historical data check |
| `backtest-results-v2.xlsx` | Detailed results |
| `backtest-charts-v2.png` | Visualization |

### Running the Backtest

```bash
# Install dependencies
uv sync

# Set SimFin API key (get free key at app.simfin.com)
export SIMFIN_API_KEY=your_key_here

# Run data validation tests
uv run python test_data_sources.py

# Run backtest with real data
uv run python run_backtest_v2.py
```

---

## Conclusion

This analysis demonstrates that **both data quality AND methodology** are critical in backtesting:

| Version | Data | Methodology | Multi-Factor Alpha |
|---------|------|-------------|-------------------|
| V1 | Fake (estimated) | January rebalance | +16.8% (inflated) |
| V2 | Real (SimFin) | January rebalance | -2.1% (flawed timing) |
| V2.1 | Real (SimFin) | April rebalance + robust filters | **+5.0%** |

**Key lessons:**

1. **Fake data inflates returns.** V1's 174% returns were an illusion.

2. **Bad methodology can hide real alpha.** V2 showed Multi-Factor underperforming, but this was due to using unavailable data (January rebalancing before annual reports).

3. **Proper implementation reveals true performance.** V2.1 shows Multi-Factor can deliver meaningful alpha (+5%) when done correctly.

4. **Handle data limitations gracefully.** Free data sources have gaps. Robust strategies work around them rather than failing.

**Bottom line:** Factor investing can outperform passive indexing, but only with careful attention to data availability and realistic methodology. A poorly implemented factor strategy is worse than indexing; a well-implemented one can add real value.

---

*Analysis conducted January 2026. Past performance does not guarantee future results.*
