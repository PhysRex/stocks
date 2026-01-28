"""
Check how far back yfinance historical EPS data goes for multiple stocks.
"""
import yfinance as yf
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

test_tickers = ['AAPL', 'MSFT', 'GOOGL', 'JPM', 'JNJ', 'XOM', 'WMT', 'PG']

print('=== Historical EPS Data Availability ===\n')

for ticker in test_tickers:
    try:
        stock = yf.Ticker(ticker)
        inc = stock.income_stmt  # Annual

        if inc is not None and 'Basic EPS' in inc.index:
            eps_data = inc.loc['Basic EPS']
            eps_data = eps_data.dropna()

            if len(eps_data) > 0:
                oldest = eps_data.index[-1]
                newest = eps_data.index[0]
                print(f'{ticker}: {len(eps_data)} years of EPS data ({oldest.year} to {newest.year})')
                print(f'        EPS values: {eps_data.values}')
            else:
                print(f'{ticker}: No EPS data')
        else:
            print(f'{ticker}: No income statement data')
    except Exception as e:
        print(f'{ticker}: Error - {e}')
    print()

print('\n=== Can We Calculate Historical P/E? ===\n')

# Test: Calculate historical P/E for AAPL
aapl = yf.Ticker('AAPL')
inc = aapl.income_stmt

if inc is not None and 'Basic EPS' in inc.index:
    eps_series = inc.loc['Basic EPS'].dropna()

    # Get historical prices
    prices = aapl.history(start='2020-01-01', end='2026-01-01')['Close']
    # Remove timezone for comparison
    prices.index = prices.index.tz_localize(None)

    print('Historical P/E for AAPL (fiscal year end prices):')
    print('-' * 50)

    for date in eps_series.index:
        eps = eps_series[date]
        if pd.isna(eps) or eps <= 0:
            continue

        # Convert to naive datetime for comparison
        date_naive = pd.Timestamp(date).tz_localize(None) if date.tzinfo else date

        # Get price on or near the fiscal year end date
        try:
            # Find closest price to the fiscal year end
            price_dates = prices.index[prices.index <= date_naive]
            if len(price_dates) > 0:
                closest_date = price_dates[-1]
                price = prices[closest_date]
                pe = price / eps
                print(f'{date_naive.date()}: Price=${price:.2f}, EPS=${eps:.2f}, P/E={pe:.1f}')
        except Exception as e:
            print(f'{date_naive.date()}: Error - {e}')
