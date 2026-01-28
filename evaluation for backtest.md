Implement the following plan:

  # Backtest Plan: Value-Only vs Multi-Factor Strategy

  ## Overview
  Backtest two investment strategies over 5 years (Jan 2021 - Jan 2026) with $1000/year investment, using a multi-agent architecture.

  ---

  ## Strategies to Compare

  ### Strategy 1: Value-Only (from finviz-finance.ipynb)
  - **Filters**: US Large Cap ($10B+), Positive P/E, P/E < 0.5 × Market Cap (billions)
  - **Selection**: Top 25 stocks by market cap
  - **Rebalance**: Annually

  ### Strategy 2: Multi-Factor (from finviz-multifactor.ipynb)
  - **Filters**: Same base + EPS Growth > 0% (quality) + 6M Performance > 0% (momentum)
  - **Selection**: Top 25 by composite score (Value + Growth + Momentum ranks)
  - **Rebalance**: Annually

  ### Benchmark: S&P 500 (SPY ETF)

  ---

  ## Key Challenge: Historical Stock Selection

  **Problem**: We can't get historical finviz screener results from 2021-2025.

  **Solution**: Proxy-based historical simulation
  1. Get current S&P 500 constituents (504 stocks)
  2. Download 5 years of historical data via yfinance (price, fundamentals)
  3. At each annual rebalancing date, apply filters to historical data:
  - Use trailing P/E from that date
  - Use 6-month momentum from that date
  - Use 5-year EPS growth available at that date
  4. Select top 25 based on each strategy's criteria
  5. Simulate purchases and track portfolio value

  **Limitation**: Survivorship bias (only includes stocks that still exist today). This is acceptable for a comparative backtest since both strategies have the same bias.

  ---

  ## Agent Architecture

  ```
  ┌─────────────────────────────────────────────────────────────┐
  │                    PLANNER AGENT                            │
  │  - Coordinates overall workflow                             │
  │  - Creates shared data infrastructure                       │
  │  - Downloads historical data once                           │
  │  - Triggers execution agents                                │
  └─────────────────────────────────────────────────────────────┘
  │
  ┌───────────────┴───────────────┐
  ▼                               ▼
  ┌─────────────────────────┐     ┌─────────────────────────┐
  │  EXECUTOR 1: Value-Only │     │  EXECUTOR 2: Multi-Factor│
  │  - Apply value filters  │     │  - Apply all 3 filters   │
  │  - Select top 25 by cap │     │  - Rank by composite     │
  │  - Simulate purchases   │     │  - Simulate purchases    │
  │  - Track returns        │     │  - Track returns         │
  └─────────────────────────┘     └─────────────────────────┘
  │                               │
  └───────────────┬───────────────┘
  ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                    EVALUATOR AGENT                          │
  │  - Compare both strategies to benchmark                     │
  │  - Calculate performance metrics (CAGR, Sharpe, Drawdown)   │
  │  - Generate recommendations for future investing            │
  │  - Create final report with visualizations                  │
  └─────────────────────────────────────────────────────────────┘
  ```

  ---

  ## File Structure (Single Notebook Approach)

  ```
  stocks/
  ├── backtest-comparison.ipynb   # Main notebook with all logic
  ├── backtest-results.xlsx       # Output: detailed results
  └── (existing files unchanged)
  ```

  The notebook will be organized into clear sections:
  1. **Setup & Data Loading** - Dependencies, download historical data
  2. **Strategy 1: Value-Only** - Implementation and backtest
  3. **Strategy 2: Multi-Factor** - Implementation and backtest
  4. **Evaluation & Comparison** - Metrics, charts, recommendations

  ---

  ## Implementation Steps

  ### Step 1: Setup & Dependencies
  Add to `pyproject.toml`:
  ```toml
  dependencies = [
  "finvizfinance>=1.3.0",
  "notebook>=7.5.2",
  "openpyxl>=3.1.5",
  "yfinance>=0.2.50",
  "quantstats>=0.0.65",
  "matplotlib>=3.8.0",
  ]
  ```

  ### Step 2: Notebook Section - Data Loading
  ```python
  # Get S&P 500 tickers from existing xlsx or Wikipedia
  # Download 5 years of daily price data via yfinance
  # Cache to avoid re-downloading on reruns
  ```

  ### Step 3: Notebook Section - Strategy Functions

  **Value-Only Selection:**
  ```python
  def select_stocks_value(prices_df, market_caps, pe_ratios, date):
  # 1. Filter P/E > 0
  # 2. Filter P/E < 0.5 * MarketCap(billions)
  # 3. Return top 25 by market cap
  ```

  **Multi-Factor Selection:**
  ```python
  def select_stocks_multifactor(prices_df, fundamentals, date):
  # 1. Apply value filters (same as above)
  # 2. Filter EPS growth > 0 (trailing)
  # 3. Filter 6-month momentum > 0
  # 4. Rank by composite score
  # 5. Return top 25 by composite score
  ```

  ### Step 4: Notebook Section - Backtest Engine
  ```python
  def run_backtest(
  strategy_func: Callable,
  historical_data: pd.DataFrame,
  annual_investment: float = 1000.0,
  start_date: str = "2021-01-04",
  end_date: str = "2026-01-03",
  rebalance_freq: str = "annually"
  ) -> pd.DataFrame:
  """
  For each year:
  1. Call strategy_func to get stock selections
  2. Allocate $1000 equally across selected stocks
  3. Calculate shares purchased: $40 / price per stock (25 stocks)
  4. Track holdings until next rebalance
  5. At rebalance: sell all, apply new selections, reinvest total value + $1000

  Returns: DataFrame with columns:
  - date, portfolio_value, total_invested, holdings, returns
  """
  ```

  ### Step 5: Notebook Section - Evaluation
  ```python
  # Calculate metrics for each strategy:
  # - Total Return, CAGR, Sharpe Ratio, Max Drawdown, Volatility

  # Generate visualizations:
  # - Portfolio value over time (all 3 lines)
  # - Annual returns bar chart
  # - Drawdown chart

  # Use quantstats for detailed tearsheet (optional)

  # Generate investment recommendations based on findings
  ```

  ---

  ## Annual Investment Simulation

  | Year | Date       | Action                                      |
  |------|------------|---------------------------------------------|
  | 2021 | Jan 4      | Screen stocks, invest $1000 in top 25       |
  | 2022 | Jan 3      | Sell all, screen, invest portfolio + $1000  |
  | 2023 | Jan 3      | Sell all, screen, invest portfolio + $1000  |
  | 2024 | Jan 2      | Sell all, screen, invest portfolio + $1000  |
  | 2025 | Jan 2      | Sell all, screen, invest portfolio + $1000  |
  | 2026 | Jan 2      | Final valuation (no new investment)         |

  **Total Invested**: $5,000 over 5 years

  ---

  ## Output Metrics

  ### Per Strategy:
  - Total Invested: $5,000
  - Final Portfolio Value: $X,XXX
  - Total Return: XX.X%
  - CAGR: XX.X%
  - Sharpe Ratio: X.XX
  - Max Drawdown: -XX.X%
  - Best Year / Worst Year

  ### Comparison Table:
  | Metric          | Value-Only | Multi-Factor | S&P 500 |
  |-----------------|------------|--------------|---------|
  | Final Value     | $X,XXX     | $X,XXX       | $X,XXX  |
  | CAGR            | XX.X%      | XX.X%        | XX.X%   |
  | Sharpe Ratio    | X.XX       | X.XX         | X.XX    |
  | Max Drawdown    | -XX.X%     | -XX.X%       | -XX.X%  |

  ---

  ## Verification Plan

  1. **Unit Tests**: Test each filter function with known data
  2. **Sanity Checks**:
  - Verify $1000 is invested each year
  - Confirm 25 stocks selected each time
  - Check portfolio value never goes negative
  3. **Benchmark Comparison**: Results should be in reasonable range (not 1000% or -90%)
  4. **Manual Spot Check**: Verify a few stock selections against historical data

  ---

  ## Execution Order

  1. **Update `pyproject.toml`** with new dependencies (yfinance, quantstats, matplotlib)
  2. **Run `uv sync`** to install dependencies
  3. **Create `backtest-comparison.ipynb`** with sections:
  - Section 1: Setup & download S&P 500 historical data (5 years)
  - Section 2: Value-Only strategy backtest
  - Section 3: Multi-Factor strategy backtest
  - Section 4: Evaluation, comparison charts, and recommendations
  4. **Run notebook end-to-end** and verify results
  5. **Export results** to Excel and generate report

  ---

  ## Recommendations Output Format

  The evaluator will produce guidelines like:
  ```
  ## Investment Recommendations Based on Backtest

  ### Strategy Selection
  - [Winner] performed better with X.X% higher CAGR
  - Multi-factor showed lower drawdowns during [specific periods]
  - Value-only had higher volatility but captured more upside

  ### Implementation Guidelines
  1. Use [recommended strategy] as primary approach
  2. Consider [specific adjustments based on findings]
  3. Rebalance annually in [recommended month]
  4. Expected realistic returns: XX-XX% CAGR

  ### Risk Considerations
  - Past performance doesn't guarantee future results
  - Survivorship bias may inflate historical returns
  - Consider tax implications of annual rebalancing

    If you need specific details from before exiting plan mode (like exact code snippets, error messages, or content you generated), read the full transcript at: C:\Users\campu\.claude\projects\C--Users-campu-Documents-coding-python-stocks\b7757b96-2796-4adb-a596-1a7276db6bed.jsonl