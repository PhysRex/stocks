"""
Analyze SimFin data coverage to understand why Multi-Factor strategy
failed to select stocks in April 2021.

The Multi-Factor strategy requires EPS growth, which needs two consecutive
years of data (e.g., FY2019 and FY2020 for April 2021 rebalancing).
"""
import pandas as pd
from pathlib import Path
import requests
from io import StringIO

# Load SimFin data
SIMFIN_DATA_DIR = Path.home() / 'simfin_data'
simfin_file = SIMFIN_DATA_DIR / 'us-income-annual.csv'

print('='*60)
print('SIMFIN DATA COVERAGE ANALYSIS')
print('='*60)

df = pd.read_csv(simfin_file, sep=';')
print(f'\nLoaded {len(df)} records for {df["Ticker"].nunique()} tickers')

# Count records per fiscal year
print('\n--- Records per Fiscal Year ---')
year_counts = df.groupby('Fiscal Year')['Ticker'].count()
print(year_counts.to_string())

# Count unique tickers per year
print('\n--- Unique Tickers per Fiscal Year ---')
year_tickers = df.groupby('Fiscal Year')['Ticker'].nunique()
print(year_tickers.to_string())

# Find tickers with data in each year
tickers_by_year = {}
for year in range(2019, 2025):
    tickers_by_year[year] = set(df[df['Fiscal Year'] == year]['Ticker'].unique())

# Check consecutive year coverage (needed for EPS growth)
print('\n--- Consecutive Year Coverage (for EPS Growth) ---')
for year in range(2020, 2025):
    prev_year = year - 1
    both = tickers_by_year[prev_year] & tickers_by_year[year]
    print(f'FY{prev_year} + FY{year}: {len(both)} tickers have both years')

# Load S&P 500 constituents
print('\n--- S&P 500 Coverage ---')
headers = {'User-Agent': 'Mozilla/5.0'}
url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
resp = requests.get(url, headers=headers)
sp500_table = pd.read_html(StringIO(resp.text))[0]
sp500_tickers = set(sp500_table['Symbol'].str.replace('.', '-', regex=False).tolist())

print(f'Total S&P 500 tickers: {len(sp500_tickers)}')

for year in range(2019, 2025):
    overlap = sp500_tickers & tickers_by_year[year]
    print(f'S&P 500 with FY{year} data: {len(overlap)}')

# Critical check: S&P 500 stocks with both 2019 AND 2020 data
both_2019_2020 = tickers_by_year[2019] & tickers_by_year[2020]
sp500_with_both = sp500_tickers & both_2019_2020
print(f'\nS&P 500 with BOTH FY2019 + FY2020 data: {len(sp500_with_both)}')

# Which S&P 500 stocks are missing?
missing_2019 = sp500_tickers - tickers_by_year[2019]
missing_2020 = sp500_tickers - tickers_by_year[2020]
missing_either = sp500_tickers - both_2019_2020

print(f'\nS&P 500 stocks missing FY2019 data: {len(missing_2019)}')
print(f'S&P 500 stocks missing FY2020 data: {len(missing_2020)}')
print(f'S&P 500 stocks missing FY2019 OR FY2020: {len(missing_either)}')

# Show some examples of missing stocks
print('\n--- Sample Missing Stocks (first 30) ---')
print(sorted(missing_either)[:30])

# Now check: for April 2021, how many S&P 500 stocks have valid EPS growth?
print('\n' + '='*60)
print('APRIL 2021 REBALANCE SIMULATION')
print('='*60)

# Build EPS lookup
simfin_eps = {}
for _, row in df.iterrows():
    ticker = row['Ticker']
    year = int(row['Fiscal Year'])
    net_income = row['Net Income']
    shares = row['Shares (Diluted)']

    if pd.notna(net_income) and pd.notna(shares) and shares > 0:
        if ticker not in simfin_eps:
            simfin_eps[ticker] = {}
        simfin_eps[ticker][year] = net_income / shares

# Count S&P 500 stocks that can calculate EPS growth for April 2021
# (needs FY2020 and FY2019 data, with positive EPS in prior year)
valid_for_growth = []
for ticker in sp500_tickers:
    if ticker not in simfin_eps:
        continue
    if 2020 not in simfin_eps[ticker] or 2019 not in simfin_eps[ticker]:
        continue
    eps_2020 = simfin_eps[ticker][2020]
    eps_2019 = simfin_eps[ticker][2019]
    if eps_2019 > 0:  # Need positive prior year for growth calc
        growth = (eps_2020 - eps_2019) / eps_2019
        valid_for_growth.append({
            'ticker': ticker,
            'eps_2019': eps_2019,
            'eps_2020': eps_2020,
            'growth': growth
        })

print(f'S&P 500 stocks with valid EPS growth data: {len(valid_for_growth)}')

# How many have POSITIVE growth (required by Multi-Factor)?
positive_growth = [v for v in valid_for_growth if v['growth'] > 0]
print(f'S&P 500 stocks with POSITIVE EPS growth: {len(positive_growth)}')

# Show distribution
import numpy as np
growths = [v['growth'] for v in valid_for_growth]
print(f'\nEPS Growth distribution (FY2019 to FY2020):')
print(f'  Min:    {min(growths)*100:.1f}%')
print(f'  25th:   {np.percentile(growths, 25)*100:.1f}%')
print(f'  Median: {np.median(growths)*100:.1f}%')
print(f'  75th:   {np.percentile(growths, 75)*100:.1f}%')
print(f'  Max:    {max(growths)*100:.1f}%')

print('\n--- Stocks with Positive EPS Growth (sample) ---')
positive_growth_sorted = sorted(positive_growth, key=lambda x: x['growth'], reverse=True)
for stock in positive_growth_sorted[:15]:
    print(f"  {stock['ticker']}: {stock['growth']*100:.1f}% (${stock['eps_2019']:.2f} -> ${stock['eps_2020']:.2f})")
