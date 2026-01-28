"""
Test script to validate that SimFin and yfinance data are consistent
for overlapping years.
"""
import pandas as pd
import numpy as np
import yfinance as yf
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Load SimFin data
SIMFIN_DATA_DIR = Path.home() / 'simfin_data'
SIMFIN_INCOME_FILE = SIMFIN_DATA_DIR / 'us-income-annual.csv'

def load_simfin_data():
    """Load SimFin income statement data."""
    if not SIMFIN_INCOME_FILE.exists():
        raise FileNotFoundError(f"SimFin data not found at {SIMFIN_INCOME_FILE}")
    return pd.read_csv(SIMFIN_INCOME_FILE, sep=';')

def get_simfin_eps(df, ticker):
    """Get EPS by year from SimFin data."""
    ticker_data = df[df['Ticker'] == ticker].copy()
    if len(ticker_data) == 0:
        return {}

    ticker_data = ticker_data.sort_values('Fiscal Year')
    eps_dict = {}

    for _, row in ticker_data.iterrows():
        year = int(row['Fiscal Year'])
        net_income = row['Net Income']
        shares = row['Shares (Diluted)']

        if pd.notna(net_income) and pd.notna(shares) and shares > 0:
            eps = net_income / shares
            eps_dict[year] = eps

    return eps_dict

def get_yfinance_eps(ticker):
    """Get EPS by year from yfinance."""
    stock = yf.Ticker(ticker)

    try:
        income_stmt = stock.income_stmt
        if income_stmt is None or 'Basic EPS' not in income_stmt.index:
            return {}

        eps_series = income_stmt.loc['Basic EPS']
        eps_dict = {}

        for date, eps in eps_series.items():
            if pd.notna(eps):
                # yfinance dates are fiscal year end dates
                year = date.year
                eps_dict[year] = float(eps)

        return eps_dict
    except Exception as e:
        print(f"Error getting yfinance data for {ticker}: {e}")
        return {}

def compare_eps(ticker, simfin_eps, yfinance_eps, tolerance=0.15):
    """
    Compare EPS between SimFin and yfinance.
    Returns (passed, details) tuple.

    tolerance: allowed relative difference (default 15% to account for
               different calculation methods)
    """
    results = []
    overlapping_years = set(simfin_eps.keys()) & set(yfinance_eps.keys())

    if not overlapping_years:
        return None, f"No overlapping years for {ticker}"

    all_passed = True
    details = []

    for year in sorted(overlapping_years):
        sf_eps = simfin_eps[year]
        yf_eps = yfinance_eps[year]

        if sf_eps == 0 and yf_eps == 0:
            diff_pct = 0
        elif sf_eps == 0 or yf_eps == 0:
            diff_pct = 100  # One is zero, other isn't
        else:
            diff_pct = abs(sf_eps - yf_eps) / abs(yf_eps) * 100

        passed = diff_pct <= tolerance * 100
        all_passed = all_passed and passed

        status = "PASS" if passed else "FAIL"
        details.append({
            'year': year,
            'simfin_eps': sf_eps,
            'yfinance_eps': yf_eps,
            'diff_pct': diff_pct,
            'status': status
        })

    return all_passed, details

def run_tests():
    """Run data consistency tests."""
    print("="*70)
    print("DATA CONSISTENCY TESTS: SimFin vs yfinance")
    print("="*70)
    print()

    # Load SimFin data
    print("Loading SimFin data...")
    simfin_df = load_simfin_data()
    print(f"  Loaded {len(simfin_df)} records for {simfin_df['Ticker'].nunique()} tickers")
    print(f"  Years: {simfin_df['Fiscal Year'].min()} - {simfin_df['Fiscal Year'].max()}")
    print()

    # Test tickers (mix of sectors)
    test_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'JPM', 'JNJ', 'XOM', 'PG', 'WMT', 'V']

    print("Testing EPS consistency across data sources...")
    print("-"*70)

    total_tests = 0
    passed_tests = 0
    failed_tests = 0

    for ticker in test_tickers:
        print(f"\n{ticker}:")

        # Get EPS from both sources
        simfin_eps = get_simfin_eps(simfin_df, ticker)
        yfinance_eps = get_yfinance_eps(ticker)

        if not simfin_eps:
            print(f"  [SKIP] No SimFin data")
            continue
        if not yfinance_eps:
            print(f"  [SKIP] No yfinance data")
            continue

        # Compare
        all_passed, details = compare_eps(ticker, simfin_eps, yfinance_eps)

        if details is None:
            print(f"  [SKIP] {details}")
            continue

        for d in details:
            total_tests += 1
            if d['status'] == 'PASS':
                passed_tests += 1
            else:
                failed_tests += 1

            print(f"  {d['year']}: SimFin=${d['simfin_eps']:.2f}, yfinance=${d['yfinance_eps']:.2f}, "
                  f"diff={d['diff_pct']:.1f}% [{d['status']}]")

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Total tests:  {total_tests}")
    print(f"Passed:       {passed_tests} ({passed_tests/total_tests*100:.1f}%)" if total_tests > 0 else "Passed: 0")
    print(f"Failed:       {failed_tests} ({failed_tests/total_tests*100:.1f}%)" if total_tests > 0 else "Failed: 0")

    if failed_tests > 0:
        print("\nNote: Some differences are expected due to:")
        print("  - Different EPS calculation methods (Basic vs Diluted)")
        print("  - Timing of data updates")
        print("  - Restatements")

    print("\n" + "="*70)
    print("DATA COVERAGE CHECK")
    print("="*70)

    # Check what years each source covers
    print("\nSimFin coverage:")
    print(f"  Years: {simfin_df['Fiscal Year'].min()} - {simfin_df['Fiscal Year'].max()}")

    print("\nyfinance coverage (sample - AAPL):")
    yf_eps = get_yfinance_eps('AAPL')
    if yf_eps:
        print(f"  Years: {min(yf_eps.keys())} - {max(yf_eps.keys())}")

    print("\nRecommendation:")
    print("  - Use SimFin for 2019-2024 (more complete history)")
    print("  - Use yfinance for 2025 (more recent data)")

    return passed_tests, failed_tests

if __name__ == "__main__":
    run_tests()
