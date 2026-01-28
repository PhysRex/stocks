# Investment Strategy Analysis: Value + Momentum + Quality

## Overview

Analysis of a quantitative stock selection strategy: selecting top 25 large-cap US stocks based on value metrics, rebalancing annually, with the claim of ~20% annual returns.

---

## Original Strategy (finviz-finance.ipynb)

**Filters:**
- US-based companies only
- Large cap ($10B+ market cap)
- Stocks only (excludes funds)
- Positive P/E ratio
- P/E < 0.5 × Market Cap (in billions)

**Process:**
1. Screen for undervalued large-cap stocks
2. Select top 25 by market cap
3. Hold for 1 year
4. Rebalance annually

---

## Validation of 20% Return Claims

### The Claim vs Reality

| Source | Claimed Returns | Independent Backtests |
|--------|----------------|----------------------|
| Greenblatt's Magic Formula (1988-2004) | 33% CAGR | 11.4% CAGR (2003-2015) |
| Magic Formula (1988-2009) | 23.8% CAGR | Underperformed S&P 500 since 2014 |

### Why Backtests Overstate Returns

1. **Selection bias** - Only successful backtests get published
2. **Capital inflows** - Popular strategies get arbitraged away over time
3. **Transaction costs** - Real-world trading costs reduce returns
4. **Taxes** - Annual rebalancing triggers short-term capital gains
5. **Slippage** - Backtests assume perfect execution

### What Research Actually Shows

| Strategy | Historical CAGR | Notes |
|----------|-----------------|-------|
| S&P 500 (baseline) | ~10% | Market-cap weighted |
| S&P 500 Equal Weight | 11.5% | Beat cap-weighted by ~1%/year over 20 years |
| Value alone | 11-12% | Periods of significant underperformance |
| Value + Momentum | 15-17% | 783% vs 183% for value alone (12-year European backtest) |
| Qi Value (multi-factor) | ~15% | 1481% total return over 22 years |
| Piotroski F-Score | Market + 13.4%/yr | Quality filter for value stocks |

**Realistic expectation: 12-15% CAGR with disciplined multi-factor approach**

---

## Improved Strategy (finviz-multifactor.ipynb)

### Added Filters

| Filter | Purpose |
|--------|---------|
| **Quality** | EPS growth > 0% (past 5 years) - avoids value traps |
| **Momentum** | 6-month price performance > 0% - captures trending stocks |

### Composite Ranking

Stocks scored equally on three factors:
- **Value**: Inverse P/E (lower P/E = higher score)
- **Growth**: Historical EPS growth rate
- **Momentum**: 6-month price performance

### Why This Works Better

Research shows value and momentum are negatively correlated:
- When value underperforms, momentum often outperforms
- Combining them reduces volatility and drawdowns
- Backtests show 600%+ improvement over value alone

---

## Alternative Strategies (Not S&P 500 Dependent)

### 1. Global Value Investing
Apply value screens to international markets (less arbitraged):
- Hong Kong: +6-15% alpha historically
- France: +5-9% per year
- Benelux: +7.7% per year over 20 years

### 2. Small/Mid Cap Value
Same filters on smaller companies:
- Higher expected returns
- Higher volatility
- Less analyst coverage = more inefficiencies

### 3. Dividend Aristocrats
Companies with 25+ years of dividend growth:
- Lower volatility than market
- 40% of total returns from reinvested dividends
- Better downside protection in bear markets

### 4. Momentum ETF Rotation (Lazy Man's Strategy)
Rotate between asset classes based on momentum:
- 13% CAGR vs 10% for MSCI World (54-year backtest)
- Simple to implement with ETFs
- Monthly or quarterly rebalancing

### 5. Quality Value Momentum (QVM)
Combine all three factors:
- EBIT/Enterprise Value for value
- Piotroski F-Score for quality
- 6-12 month price performance for momentum
- 1142% return over 13 years in backtests

---

## Key Risk Factors

### Value Traps
Stocks that appear cheap but are cheap for a reason:
- Declining business fundamentals
- Disrupted industries
- Poor management

**Mitigation:** Quality filter (positive earnings growth)

### Factor Underperformance
Value underperformed growth for a decade (2010-2020):
- Requires discipline to stick with strategy
- Many investors abandon during drawdowns

**Mitigation:** Multi-factor approach reduces single-factor risk

### Concentration Risk
Top 25 stocks may be concentrated in few sectors:
- Tech-heavy in recent years
- Financials during other periods

**Mitigation:** Consider sector limits or diversification rules

### Rebalancing Costs
Annual rebalancing triggers:
- Transaction costs
- Bid-ask spreads
- Short-term capital gains taxes

**Mitigation:** Use tax-advantaged accounts, consider 13-month hold periods

---

## Implementation Checklist

- [ ] Run multifactor screener quarterly to monitor
- [ ] Rebalance annually (or when positions drift >10%)
- [ ] Track performance vs S&P 500 benchmark
- [ ] Document buy/sell decisions and rationale
- [ ] Review sector concentration before rebalancing
- [ ] Consider tax implications before selling

---

## Tools & Resources

### Screening & Backtesting
- [Portfolio Visualizer](https://www.portfoliovisualizer.com/backtest-portfolio) - Free backtesting
- [Quant Investing](https://www.quant-investing.com/strategies/qi-value-investment-strategy) - European/US screening with backtests
- finvizfinance Python library - Automated screening

### Research & Education
- *The Little Book That Beats the Market* - Joel Greenblatt
- *Quantitative Value* - Wesley Gray & Tobias Carlisle
- *What Works on Wall Street* - James O'Shaughnessy

### Key Academic Papers
- Fama-French factor research
- "Quantitative Value Investing in Europe: What Works for Achieving Alpha"
- Piotroski F-Score research (1976-1996 backtest)

---

## Files in This Project

| File | Description |
|------|-------------|
| `finviz-finance.ipynb` | Original value-only screener |
| `finviz-multifactor.ipynb` | Enhanced value + momentum + quality screener |
| `stock-data.xlsx` | Output from original screener |
| `multifactor-stock-data.xlsx` | Output from enhanced screener |
| `s&p500-constituents.xlsx` | S&P 500 company names and sectors |
| `investment-strategy-analysis.md` | This file |

---

## Future Explorations

- [ ] Backtest the multi-factor strategy with historical data
- [ ] Compare performance across different market cycles
- [ ] Test with small/mid cap universe
- [ ] Add international markets (Europe, Asia)
- [ ] Implement sector rotation overlay
- [ ] Explore machine learning for factor weighting
- [ ] Paper trade for 1 year before committing capital

---

*Last updated: January 2026*
