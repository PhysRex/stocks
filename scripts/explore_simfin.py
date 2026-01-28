"""
Explore what historical fundamental data SimFin provides.
"""
import simfin as sf
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

# Get API key from environment
API_KEY = os.environ.get('SIMFIN_API_KEY', 'YOUR_API_KEY')

if API_KEY == 'YOUR_API_KEY':
    print('SETUP REQUIRED: Set SIMFIN_API_KEY environment variable')
    exit(0)

# Set up SimFin
sf.set_api_key(API_KEY)
sf.set_data_dir('~/simfin_data/')

print('=== SimFin Data Exploration ===\n')

# The simfin package has compatibility issues with newer pandas
# Let's read the downloaded CSV files directly
import glob
from pathlib import Path

data_dir = Path.home() / 'simfin_data'
print(f'Data directory: {data_dir}')
print(f'Files found: {list(data_dir.glob("*.csv")) if data_dir.exists() else "None"}')

# Try to load the income data directly
income_file = data_dir / 'us-income-annual.csv'
if income_file.exists():
    print(f'\nLoading income data from: {income_file}')
    df_income = pd.read_csv(income_file, sep=';')
    print(f'Shape: {df_income.shape}')
    print(f'Columns: {list(df_income.columns)}')

    # Check date range
    if 'Fiscal Year' in df_income.columns:
        print(f"Fiscal Year range: {df_income['Fiscal Year'].min()} to {df_income['Fiscal Year'].max()}")
    if 'Report Date' in df_income.columns:
        print(f"Report Date range: {df_income['Report Date'].min()} to {df_income['Report Date'].max()}")

    print(f"Unique tickers: {df_income['Ticker'].nunique()}")

    # Show AAPL data
    print('\n' + '='*60)
    print('AAPL Historical Income Data')
    print('='*60)

    aapl = df_income[df_income['Ticker'] == 'AAPL'].copy()
    aapl = aapl.sort_values('Fiscal Year')

    cols = ['Fiscal Year', 'Revenue', 'Net Income', 'Shares (Diluted)']
    cols_available = [c for c in cols if c in aapl.columns]
    print(aapl[cols_available].tail(10).to_string(index=False))

    # Calculate EPS
    if 'Net Income' in aapl.columns and 'Shares (Diluted)' in aapl.columns:
        aapl['EPS'] = aapl['Net Income'] / aapl['Shares (Diluted)']
        print('\n\nCalculated EPS:')
        print(aapl[['Fiscal Year', 'Net Income', 'Shares (Diluted)', 'EPS']].tail(10).to_string(index=False))

else:
    print(f'Income file not found at {income_file}')
    print('Attempting to download via simfin API...')

    try:
        # Try the simfin load function
        df_income = sf.load_income(variant='annual', market='us')
        print(f'Loaded: {df_income.shape}')
    except Exception as e:
        print(f'Error: {e}')

# Check for share prices
print('\n' + '='*60)
print('Checking for share prices data...')
print('='*60)

prices_file = data_dir / 'us-shareprices-daily.csv'
if prices_file.exists():
    print(f'Share prices file exists: {prices_file}')
    # Don't load it all - it's huge
    df_prices_sample = pd.read_csv(prices_file, sep=';', nrows=1000)
    print(f'Sample columns: {list(df_prices_sample.columns)}')
    print(f'Sample tickers: {df_prices_sample["Ticker"].unique()[:10]}')
else:
    print('Share prices not downloaded yet. Would need to call sf.load_shareprices()')

print('\n' + '='*60)
print('SUMMARY: What SimFin Provides')
print('='*60)
print('''
- Income statements with Net Income, Revenue, Shares Outstanding
- Balance sheets with Total Assets, Equity, Debt
- Cash flow statements
- Share prices (daily)

We can calculate REAL historical:
- P/E Ratio = Price / (Net Income / Shares)
- Market Cap = Price * Shares Outstanding
- EPS Growth = Year-over-year change in EPS
- Revenue Growth = Year-over-year change in Revenue
''')
