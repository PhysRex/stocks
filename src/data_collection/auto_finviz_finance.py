#!/usr/bin/env python
# coding: utf-8

# # finviz api download


import os
import openpyxl
from datetime import datetime
import pandas as pd
from finvizfinance.screener.valuation import Valuation

foverview = Valuation()
filters_dict = {
    'Exchange': 'Any',
    'Country': 'USA',
    'Market Cap.': '+Large (over $10bln)',
    'Industry': 'Stocks only (ex-Funds)',
}
foverview.set_filter(filters_dict=filters_dict)

df = foverview.ScreenerView()


sorted_stocks = df.sort_values('Market Cap', ascending=False)

positive_stocks = sorted_stocks[sorted_stocks['P/E'] > 0]
positive_stocks.shape

bn = 1000000000
high_earning_stocks = positive_stocks[positive_stocks['P/E']
                                      < (0.5 * positive_stocks['Market Cap'] / bn)]
high_earning_stocks.shape


analysis_stocks = high_earning_stocks[[
    'Ticker', 'Price', 'Market Cap', 'P/E', 'EPS past 5Y', ]].copy()


analysis_stocks.loc[:, [
    'Earnings (in B)']] = analysis_stocks['Market Cap'] / (bn * analysis_stocks['P/E'])


analysis_stocks = analysis_stocks[[
    'Ticker', 'Price', 'Earnings (in B)', 'EPS past 5Y', ]].copy()
analysis_stocks.rename(
    columns={'EPS past 5Y': 'Earnings Growth'}, inplace=True)


# Import ticker names & sectors
sheet = 'constituents'
file_name = 's&p500-constituents.xlsx'
constituents = pd.read_excel(file_name, sheet_name=sheet)

joined_stocks = pd.merge(analysis_stocks, constituents,
                         on='Ticker', how='left').copy()
name_col = joined_stocks.pop('Name')
joined_stocks.insert(0, name_col.name, name_col)  # Is in-place


def save_excel_sheet(df, filepath, sheetname, index=False):
    # Create file if it does not exist
    if not os.path.exists(filepath):
        df.to_excel(filepath, sheet_name=sheetname, index=index)

    # Otherwise, add a sheet. Overwrite if there exists one with the same name.
    else:
        with pd.ExcelWriter(filepath, engine='openpyxl', if_sheet_exists='replace', mode='a') as writer:
            df.to_excel(writer, sheet_name=sheetname, index=index)


sheetname = datetime.now().strftime("%m-%d-%Y--%H-%M")

save_excel_sheet(joined_stocks, 'stock-data.xlsx', sheetname)
