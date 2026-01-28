"""
Check if yfinance provides historical income statement data going back to 2019.
This would be an alternative to SimFin for older fundamental data.
"""
import yfinance as yf
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

print('='*60)
print('YFINANCE HISTORICAL FUNDAMENTALS CHECK')
print('='*60)

# Test a sample of S&P 500 stocks
test_tickers = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',  # Big Tech
    'JPM', 'BAC', 'WFC', 'GS', 'MS',           # Financials
    'JNJ', 'PFE', 'UNH', 'MRK', 'ABBV',        # Healthcare
    'XOM', 'CVX', 'COP',                        # Energy
    'WMT', 'PG', 'KO', 'PEP',                   # Consumer
    'NVDA', 'AMD', 'INTC', 'AVGO',              # Semiconductors
]

print(f'\nTesting {len(test_tickers)} stocks for historical EPS data...\n')

results = []

for ticker in test_tickers:
    try:
        stock = yf.Ticker(ticker)
        income = stock.income_stmt

        if income is None or income.empty:
            results.append({'ticker': ticker, 'years': [], 'has_2019': False, 'has_2020': False})
            continue

        # Get available years
        years = sorted([d.year for d in income.columns])

        # Check for EPS or Net Income
        has_eps = 'Basic EPS' in income.index or 'Diluted EPS' in income.index
        has_net_income = 'Net Income' in income.index

        # Get EPS by year if available
        eps_by_year = {}
        if 'Basic EPS' in income.index:
            for date in income.columns:
                eps = income.loc['Basic EPS', date]
                if pd.notna(eps):
                    eps_by_year[date.year] = float(eps)

        results.append({
            'ticker': ticker,
            'years': years,
            'has_2019': 2019 in years,
            'has_2020': 2020 in years,
            'has_eps': has_eps,
            'eps_by_year': eps_by_year
        })

        print(f'{ticker}: Years {years}, EPS: {has_eps}')
        if eps_by_year:
            for year, eps in sorted(eps_by_year.items()):
                print(f'    FY{year}: ${eps:.2f}')

    except Exception as e:
        print(f'{ticker}: Error - {e}')
        results.append({'ticker': ticker, 'years': [], 'has_2019': False, 'has_2020': False, 'error': str(e)})

# Summary
print('\n' + '='*60)
print('SUMMARY')
print('='*60)

has_2019 = sum(1 for r in results if r.get('has_2019', False))
has_2020 = sum(1 for r in results if r.get('has_2020', False))
has_both = sum(1 for r in results if r.get('has_2019', False) and r.get('has_2020', False))

print(f'Stocks with 2019 data: {has_2019}/{len(test_tickers)}')
print(f'Stocks with 2020 data: {has_2020}/{len(test_tickers)}')
print(f'Stocks with BOTH 2019+2020: {has_both}/{len(test_tickers)}')

# Check the typical year range
all_years = set()
for r in results:
    all_years.update(r.get('years', []))
print(f'\nAll years found: {sorted(all_years)}')

# If yfinance has good 2019 coverage, we can use it
if has_both >= len(test_tickers) * 0.8:
    print('\n*** GOOD: yfinance has strong 2019-2020 coverage ***')
    print('Can use yfinance as fallback for SimFin gaps')
else:
    print('\n*** LIMITED: yfinance historical coverage is incomplete ***')
    print('May need to adjust backtest start date')
