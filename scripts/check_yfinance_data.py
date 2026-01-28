"""
Script to check what historical fundamental data yfinance provides.
"""
import yfinance as yf

# Check what historical data yfinance actually has
aapl = yf.Ticker('AAPL')

print('=== Earnings History ===')
try:
    eh = aapl.earnings_history
    if eh is not None:
        print(eh)
    else:
        print('None returned')
except Exception as e:
    print(f'Error: {e}')

print('\n=== Quarterly Earnings ===')
try:
    qe = aapl.quarterly_earnings
    if qe is not None:
        print(qe)
    else:
        print('None returned')
except Exception as e:
    print(f'Error: {e}')

print('\n=== Income Statement (Quarterly - last 4) ===')
try:
    inc = aapl.quarterly_income_stmt
    if inc is not None and len(inc) > 0:
        # Show Net Income and EPS rows
        rows_to_show = ['Net Income', 'Basic EPS', 'Diluted EPS']
        available_rows = [r for r in rows_to_show if r in inc.index]
        print(inc.loc[available_rows].T)
except Exception as e:
    print(f'Error: {e}')

print('\n=== Income Statement (Annual) ===')
try:
    inc_annual = aapl.income_stmt
    if inc_annual is not None and len(inc_annual) > 0:
        rows_to_show = ['Net Income', 'Basic EPS', 'Diluted EPS']
        available_rows = [r for r in rows_to_show if r in inc_annual.index]
        print(inc_annual.loc[available_rows].T)
except Exception as e:
    print(f'Error: {e}')

print('\n=== Financials History Available ===')
try:
    # Check date range of income statements
    inc = aapl.quarterly_income_stmt
    if inc is not None:
        print(f'Quarterly data from {inc.columns[-1]} to {inc.columns[0]}')
        print(f'Number of quarters: {len(inc.columns)}')
except Exception as e:
    print(f'Error: {e}')
