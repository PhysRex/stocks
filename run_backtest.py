import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import warnings
import requests
from io import StringIO
warnings.filterwarnings('ignore')

# Configuration
DATA_START_DATE = '2020-06-01'  # Start earlier to have momentum history
BACKTEST_START_DATE = '2021-01-01'
END_DATE = '2026-01-22'
ANNUAL_INVESTMENT = 1000.0
NUM_STOCKS = 25

REBALANCE_DATES = [
    '2021-01-04',
    '2022-01-03',
    '2023-01-03',
    '2024-01-02',
    '2025-01-02',
]

print('=' * 60)
print('BACKTEST: Value-Only vs Multi-Factor Strategy')
print('=' * 60)

# Get S&P 500 tickers using requests with headers
print('\nLoading S&P 500 constituents...')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
resp = requests.get(url, headers=headers)
sp500_table = pd.read_html(StringIO(resp.text))[0]
sp500_tickers = sp500_table['Symbol'].str.replace('.', '-', regex=False).tolist()
print(f'Loaded {len(sp500_tickers)} tickers')

# Download price data (start earlier for momentum calculation)
print('\nDownloading price data (including 6-month history for momentum)...')
raw_data = yf.download(sp500_tickers, start=DATA_START_DATE, end=END_DATE, progress=False, threads=True)
# Handle different yfinance output formats
if isinstance(raw_data.columns, pd.MultiIndex):
    if 'Adj Close' in raw_data.columns.get_level_values(0):
        all_prices = raw_data['Adj Close']
    else:
        all_prices = raw_data['Close']
else:
    all_prices = raw_data['Close'] if 'Close' in raw_data.columns else raw_data
all_prices = all_prices.ffill().bfill()
print(f'Got data for {len(all_prices.columns)} stocks, {len(all_prices)} trading days')

# Download SPY
print('Downloading SPY benchmark...')
spy_raw = yf.download('SPY', start=DATA_START_DATE, end=END_DATE, progress=False)
if isinstance(spy_raw.columns, pd.MultiIndex):
    spy_data = spy_raw['Close']['SPY'] if 'SPY' in spy_raw['Close'].columns else spy_raw['Close'].iloc[:, 0]
else:
    spy_data = spy_raw['Close'] if 'Close' in spy_raw.columns else spy_raw.iloc[:, 0]
print(f'SPY: {len(spy_data)} trading days')

# Fetch fundamentals for all stocks
print('\nFetching fundamentals (this takes a while)...')
fundamentals = {}
for i, ticker in enumerate(all_prices.columns):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        fundamentals[ticker] = {
            'marketCap': info.get('marketCap', 0),
            'trailingPE': info.get('trailingPE', None),
            'earningsGrowth': info.get('earningsGrowth', None),
        }
    except:
        pass
    if (i + 1) % 100 == 0:
        print(f'  Processed {i+1}/{len(all_prices.columns)}...')

fundamentals_df = pd.DataFrame(fundamentals).T
print(f'Got fundamentals for {len(fundamentals_df)} stocks')

# Helper functions
def calculate_momentum(prices_df, ticker, date, lookback_days=126):
    try:
        prices = prices_df[ticker].loc[:date]
        # Use available data if less than lookback_days (minimum 20 days)
        actual_lookback = min(lookback_days, len(prices) - 1)
        if actual_lookback < 20:
            return None
        current_price = prices.iloc[-1]
        past_price = prices.iloc[-actual_lookback]
        if past_price > 0:
            return (current_price - past_price) / past_price
        return None
    except:
        return None

def estimate_pe_ratio(prices_df, fundamentals_df, ticker, date):
    try:
        current_pe = fundamentals_df.loc[ticker, 'trailingPE']
        if pd.isna(current_pe) or current_pe is None or current_pe <= 0:
            return None
        current_price = prices_df[ticker].iloc[-1]
        hist_price = prices_df[ticker].loc[:date].iloc[-1]
        price_ratio = hist_price / current_price if current_price > 0 else 1
        estimated_pe = current_pe * price_ratio
        return estimated_pe if estimated_pe > 0 else None
    except:
        return None

def estimate_market_cap(prices_df, fundamentals_df, ticker, date):
    try:
        current_cap = fundamentals_df.loc[ticker, 'marketCap']
        if pd.isna(current_cap) or current_cap is None or current_cap <= 0:
            return None
        current_price = prices_df[ticker].iloc[-1]
        hist_price = prices_df[ticker].loc[:date].iloc[-1]
        price_ratio = hist_price / current_price if current_price > 0 else 1
        return current_cap * price_ratio
    except:
        return None

# Strategy functions
def select_stocks_value(prices_df, fundamentals_df, date, num_stocks=25):
    candidates = []
    for ticker in prices_df.columns:
        if ticker not in fundamentals_df.index:
            continue
        try:
            price = prices_df[ticker].loc[:date].iloc[-1]
            if pd.isna(price):
                continue
        except:
            continue

        market_cap = estimate_market_cap(prices_df, fundamentals_df, ticker, date)
        pe_ratio = estimate_pe_ratio(prices_df, fundamentals_df, ticker, date)

        if market_cap is None or pe_ratio is None:
            continue

        market_cap_billions = market_cap / 1e9

        if market_cap_billions < 10:
            continue
        if pe_ratio <= 0:
            continue
        if pe_ratio >= 0.5 * market_cap_billions:
            continue

        candidates.append({
            'ticker': ticker,
            'market_cap': market_cap,
            'pe_ratio': pe_ratio,
            'price': price
        })

    if not candidates:
        return []

    candidates_df = pd.DataFrame(candidates)
    candidates_df = candidates_df.sort_values('market_cap', ascending=False)
    return candidates_df.head(num_stocks).to_dict('records')

def select_stocks_multifactor(prices_df, fundamentals_df, date, num_stocks=25):
    candidates = []
    for ticker in prices_df.columns:
        if ticker not in fundamentals_df.index:
            continue
        try:
            price = prices_df[ticker].loc[:date].iloc[-1]
            if pd.isna(price):
                continue
        except:
            continue

        market_cap = estimate_market_cap(prices_df, fundamentals_df, ticker, date)
        pe_ratio = estimate_pe_ratio(prices_df, fundamentals_df, ticker, date)
        momentum = calculate_momentum(prices_df, ticker, date)
        earnings_growth = fundamentals_df.loc[ticker, 'earningsGrowth']

        if market_cap is None or pe_ratio is None or momentum is None:
            continue

        market_cap_billions = market_cap / 1e9

        if market_cap_billions < 10:
            continue
        if pe_ratio <= 0:
            continue
        if pe_ratio >= 0.5 * market_cap_billions:
            continue
        if pd.isna(earnings_growth) or earnings_growth is None or earnings_growth <= 0:
            continue
        if momentum <= 0:
            continue

        candidates.append({
            'ticker': ticker,
            'market_cap': market_cap,
            'pe_ratio': pe_ratio,
            'earnings_growth': earnings_growth,
            'momentum': momentum,
            'price': price
        })

    if not candidates:
        return []

    candidates_df = pd.DataFrame(candidates)
    candidates_df['value_rank'] = candidates_df['pe_ratio'].rank(ascending=True)
    candidates_df['growth_rank'] = candidates_df['earnings_growth'].rank(ascending=False)
    candidates_df['momentum_rank'] = candidates_df['momentum'].rank(ascending=False)
    candidates_df['composite_score'] = candidates_df['value_rank'] + candidates_df['growth_rank'] + candidates_df['momentum_rank']
    candidates_df = candidates_df.sort_values('composite_score', ascending=True)
    return candidates_df.head(num_stocks).to_dict('records')

# Backtest function
def run_backtest(strategy_func, prices_df, fundamentals_df, name):
    holdings = {}
    cash = 0.0
    total_invested = 0.0
    all_dates = prices_df.index.sort_values()
    portfolio_history = []

    for rebal_date_str in REBALANCE_DATES:
        rebal_date = pd.Timestamp(rebal_date_str)
        valid_dates = all_dates[all_dates >= rebal_date]
        if len(valid_dates) == 0:
            continue
        actual_date = valid_dates[0]

        # Sell all
        if holdings:
            for ticker, shares in holdings.items():
                try:
                    price = prices_df.loc[actual_date, ticker]
                    if not pd.isna(price):
                        cash += shares * price
                except:
                    pass
            holdings = {}

        # Add investment
        cash += ANNUAL_INVESTMENT
        total_invested += ANNUAL_INVESTMENT

        # Select stocks
        selected = strategy_func(prices_df, fundamentals_df, actual_date, NUM_STOCKS)

        if not selected:
            print(f'{name}: No stocks selected on {actual_date.date()}')
            continue

        # Buy equally
        allocation = cash / len(selected)
        for stock in selected:
            ticker = stock['ticker']
            price = stock['price']
            if price > 0:
                holdings[ticker] = allocation / price

        cash = 0.0
        print(f'{name} - {actual_date.date()}: {len(selected)} stocks, invested ${total_invested:,.0f}')

    # Calculate daily values
    current_holdings = {}
    current_cash = 0.0
    current_invested = 0.0
    rebal_idx = 0
    start_date = pd.Timestamp(REBALANCE_DATES[0])

    for date in all_dates:
        if date < start_date:
            continue

        if rebal_idx < len(REBALANCE_DATES):
            rebal_date = pd.Timestamp(REBALANCE_DATES[rebal_idx])
            if date >= rebal_date:
                # Sell existing holdings
                if current_holdings:
                    for ticker, shares in current_holdings.items():
                        try:
                            price = prices_df.loc[date, ticker]
                            if not pd.isna(price):
                                current_cash += shares * price
                        except:
                            pass
                    current_holdings = {}

                # Add new investment
                current_cash += ANNUAL_INVESTMENT
                current_invested += ANNUAL_INVESTMENT

                # Select and buy stocks
                selected = strategy_func(prices_df, fundamentals_df, date, NUM_STOCKS)
                if selected:
                    alloc = current_cash / len(selected)
                    for stock in selected:
                        current_holdings[stock['ticker']] = alloc / stock['price']
                    current_cash = 0.0
                # If no stocks selected, cash remains uninvested

                rebal_idx += 1

        # Calculate portfolio value = holdings value + cash
        holdings_value = sum(
            shares * prices_df.loc[date, ticker]
            for ticker, shares in current_holdings.items()
            if ticker in prices_df.columns and not pd.isna(prices_df.loc[date, ticker])
        )
        total_value = holdings_value + current_cash
        portfolio_history.append({'date': date, 'value': total_value, 'invested': current_invested})

    return pd.DataFrame(portfolio_history).set_index('date')

# Run backtests
print('\n' + '=' * 60)
print('Running Value-Only Strategy...')
print('=' * 60)
value_portfolio = run_backtest(select_stocks_value, all_prices, fundamentals_df, 'Value-Only')

print('\n' + '=' * 60)
print('Running Multi-Factor Strategy...')
print('=' * 60)
mf_portfolio = run_backtest(select_stocks_multifactor, all_prices, fundamentals_df, 'Multi-Factor')

# SPY benchmark
print('\n' + '=' * 60)
print('Calculating SPY Benchmark...')
print('=' * 60)
spy_shares = 0.0
spy_invested = 0.0
spy_history = []
start_date = pd.Timestamp(REBALANCE_DATES[0])

rebal_idx = 0
for date in spy_data.index:
    if date < start_date:
        continue
    if rebal_idx < len(REBALANCE_DATES):
        rebal_date = pd.Timestamp(REBALANCE_DATES[rebal_idx])
        if date >= rebal_date:
            price = spy_data.loc[date]
            spy_shares += ANNUAL_INVESTMENT / price
            spy_invested += ANNUAL_INVESTMENT
            print(f'SPY - {date.date()}: Bought {ANNUAL_INVESTMENT/price:.2f} shares @ ${price:.2f}')
            rebal_idx += 1

    spy_history.append({'date': date, 'value': spy_shares * spy_data.loc[date], 'invested': spy_invested})

spy_portfolio = pd.DataFrame(spy_history).set_index('date')

# Calculate metrics
def calc_metrics(df, name):
    # Filter out zero values at start
    df_valid = df[df['value'] > 0].copy()
    if len(df_valid) == 0:
        return {'name': name, 'invested': 0, 'final': 0, 'return': 0, 'cagr': 0, 'vol': 0, 'sharpe': 0, 'max_dd': 0}

    total_invested = df_valid['invested'].iloc[-1]
    final_value = df_valid['value'].iloc[-1]
    total_return = (final_value - total_invested) / total_invested * 100

    years = (df_valid.index[-1] - df_valid.index[0]).days / 365.25
    first_value = df_valid['value'].iloc[0]
    if first_value > 0 and years > 0:
        cagr = ((final_value / first_value) ** (1/years) - 1) * 100
    else:
        cagr = 0

    daily_ret = df_valid['value'].pct_change().dropna()
    daily_ret = daily_ret[daily_ret != 0]  # Remove zero returns
    if len(daily_ret) > 0:
        vol = daily_ret.std() * np.sqrt(252) * 100
        sharpe = (cagr/100 - 0.04) / (vol/100) if vol > 0 else 0
    else:
        vol = 0
        sharpe = 0

    rolling_max = df_valid['value'].cummax()
    drawdown = (df_valid['value'] - rolling_max) / rolling_max
    max_dd = drawdown.min() * 100

    return {
        'name': name,
        'invested': total_invested,
        'final': final_value,
        'return': total_return,
        'cagr': cagr,
        'vol': vol,
        'sharpe': sharpe,
        'max_dd': max_dd
    }

value_m = calc_metrics(value_portfolio, 'Value-Only')
mf_m = calc_metrics(mf_portfolio, 'Multi-Factor')
spy_m = calc_metrics(spy_portfolio, 'S&P 500 (SPY)')

# Print results
print('\n' + '=' * 80)
print('BACKTEST RESULTS')
print('=' * 80)
print(f"Period: {REBALANCE_DATES[0]} to {value_portfolio.index[-1].date()}")
print(f'Investment: $1,000/year for 5 years = $5,000 total')
print('=' * 80)

header = f"{'Metric':<20} {'Value-Only':>15} {'Multi-Factor':>15} {'S&P 500':>15}"
print("\n" + header)
print('-' * 65)

row1 = "Final Value".ljust(20) + f"${value_m['final']:,.0f}".rjust(15) + f"${mf_m['final']:,.0f}".rjust(15) + f"${spy_m['final']:,.0f}".rjust(15)
print(row1)

row2 = "Total Return".ljust(20) + f"{value_m['return']:.1f}%".rjust(15) + f"{mf_m['return']:.1f}%".rjust(15) + f"{spy_m['return']:.1f}%".rjust(15)
print(row2)

row3 = "CAGR".ljust(20) + f"{value_m['cagr']:.1f}%".rjust(15) + f"{mf_m['cagr']:.1f}%".rjust(15) + f"{spy_m['cagr']:.1f}%".rjust(15)
print(row3)

row4 = "Volatility".ljust(20) + f"{value_m['vol']:.1f}%".rjust(15) + f"{mf_m['vol']:.1f}%".rjust(15) + f"{spy_m['vol']:.1f}%".rjust(15)
print(row4)

row5 = "Sharpe Ratio".ljust(20) + f"{value_m['sharpe']:.2f}".rjust(15) + f"{mf_m['sharpe']:.2f}".rjust(15) + f"{spy_m['sharpe']:.2f}".rjust(15)
print(row5)

row6 = "Max Drawdown".ljust(20) + f"{value_m['max_dd']:.1f}%".rjust(15) + f"{mf_m['max_dd']:.1f}%".rjust(15) + f"{spy_m['max_dd']:.1f}%".rjust(15)
print(row6)

# Recommendations
print('\n' + '=' * 80)
print('INVESTMENT RECOMMENDATIONS')
print('=' * 80)

strategies = [('Value-Only', value_m), ('Multi-Factor', mf_m), ('S&P 500', spy_m)]
by_cagr = sorted(strategies, key=lambda x: x[1]['cagr'], reverse=True)
by_sharpe = sorted(strategies, key=lambda x: x[1]['sharpe'], reverse=True)

print(f"\nBest CAGR: {by_cagr[0][0]} ({by_cagr[0][1]['cagr']:.1f}%)")
print(f"Best Risk-Adjusted (Sharpe): {by_sharpe[0][0]} ({by_sharpe[0][1]['sharpe']:.2f})")
print(f"\nValue-Only vs S&P 500: {value_m['cagr'] - spy_m['cagr']:+.1f}% alpha")
print(f"Multi-Factor vs S&P 500: {mf_m['cagr'] - spy_m['cagr']:+.1f}% alpha")

# Save results
print('\nSaving results to Excel...')
with pd.ExcelWriter('backtest-results.xlsx', engine='openpyxl') as writer:
    summary = pd.DataFrame([value_m, mf_m, spy_m])
    summary.to_excel(writer, sheet_name='Summary', index=False)

    combined = pd.DataFrame({
        'Value-Only': value_portfolio['value'],
        'Multi-Factor': mf_portfolio['value'],
        'S&P 500': spy_portfolio['value']
    })
    combined.to_excel(writer, sheet_name='Daily Values')

print('Results saved to backtest-results.xlsx')

# Generate charts
print('\nGenerating charts...')

# Filter daily data to backtest period
daily = pd.DataFrame({
    'Value-Only': value_portfolio['value'],
    'Multi-Factor': mf_portfolio['value'],
    'S&P 500': spy_portfolio['value']
})
daily = daily[daily.index >= BACKTEST_START_DATE]

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Chart 1: Portfolio Value Over Time
ax1 = axes[0, 0]
ax1.plot(daily.index, daily['Value-Only'], label='Value-Only', linewidth=2)
ax1.plot(daily.index, daily['Multi-Factor'], label='Multi-Factor', linewidth=2)
ax1.plot(daily.index, daily['S&P 500'], label='S&P 500 (SPY)', linewidth=2, linestyle='--')
ax1.axhline(y=5000, color='gray', linestyle=':', alpha=0.7, label='Total Invested ($5,000)')
ax1.set_title('Portfolio Value Over Time', fontsize=12, fontweight='bold')
ax1.set_xlabel('Date')
ax1.set_ylabel('Portfolio Value ($)')
ax1.legend(loc='upper left')
ax1.grid(True, alpha=0.3)
ax1.set_ylim(bottom=0)

# Chart 2: Annual Returns
ax2 = axes[0, 1]
annual_returns = {'Year': [], 'Value-Only': [], 'Multi-Factor': [], 'S&P 500': []}
for year in range(2021, 2026):
    year_start = f'{year}-01-01'
    year_end = f'{year}-12-31'
    year_data = daily[(daily.index >= year_start) & (daily.index <= year_end)]
    if len(year_data) > 1:
        annual_returns['Year'].append(year)
        for col in ['Value-Only', 'Multi-Factor', 'S&P 500']:
            ret = (year_data[col].iloc[-1] / year_data[col].iloc[0] - 1) * 100
            annual_returns[col].append(ret)

years = annual_returns['Year']
x = np.arange(len(years))
width = 0.25

ax2.bar(x - width, annual_returns['Value-Only'], width, label='Value-Only', color='#1f77b4')
ax2.bar(x, annual_returns['Multi-Factor'], width, label='Multi-Factor', color='#ff7f0e')
ax2.bar(x + width, annual_returns['S&P 500'], width, label='S&P 500', color='#2ca02c')
ax2.set_title('Annual Returns by Year', fontsize=12, fontweight='bold')
ax2.set_xlabel('Year')
ax2.set_ylabel('Return (%)')
ax2.set_xticks(x)
ax2.set_xticklabels(years)
ax2.legend()
ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax2.grid(True, alpha=0.3, axis='y')

# Chart 3: Drawdown
ax3 = axes[1, 0]
for col, color in [('Value-Only', '#1f77b4'), ('Multi-Factor', '#ff7f0e'), ('S&P 500', '#2ca02c')]:
    rolling_max = daily[col].cummax()
    drawdown = (daily[col] - rolling_max) / rolling_max * 100
    ax3.fill_between(daily.index, drawdown, 0, alpha=0.3, label=col, color=color)
    ax3.plot(daily.index, drawdown, color=color, linewidth=0.5)
ax3.set_title('Drawdown Over Time', fontsize=12, fontweight='bold')
ax3.set_xlabel('Date')
ax3.set_ylabel('Drawdown (%)')
ax3.legend(loc='lower left')
ax3.grid(True, alpha=0.3)

# Chart 4: Summary Metrics Comparison
ax4 = axes[1, 1]
metrics = ['CAGR (%)', 'Sharpe Ratio', 'Max DD (%)']
value_vals = [value_m['cagr'], value_m['sharpe'], abs(value_m['max_dd'])]
mf_vals = [mf_m['cagr'], mf_m['sharpe'], abs(mf_m['max_dd'])]
spy_vals = [spy_m['cagr'], spy_m['sharpe'], abs(spy_m['max_dd'])]

x = np.arange(len(metrics))
ax4.bar(x - width, value_vals, width, label='Value-Only', color='#1f77b4')
ax4.bar(x, mf_vals, width, label='Multi-Factor', color='#ff7f0e')
ax4.bar(x + width, spy_vals, width, label='S&P 500', color='#2ca02c')
ax4.set_title('Key Performance Metrics', fontsize=12, fontweight='bold')
ax4.set_xticks(x)
ax4.set_xticklabels(metrics)
ax4.legend()
ax4.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('backtest-charts.png', dpi=150, bbox_inches='tight')
print('Charts saved to backtest-charts.png')

print('\nBacktest complete!')
