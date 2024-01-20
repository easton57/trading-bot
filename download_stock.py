"""
Script for downloading stock data

Usage:
  download_stock.py <stock-symbol> [--year=<year>] [--start_year=<start_year>] [--end_year=<end_year>]

Options:
  --year=<year>               Year to download from
  --start_year=<start_year>   Year to start
  --end_year=<end_year>       Year to end
"""

import csv
import yfinance as yf
from docopt import docopt


def main(symbol, start_year, end_year):
    start_date = f'{start_year}-01-01'
    end_date = f'{end_year}-12-31'

    data = yf.download(symbol, start=start_date, end=end_date)

    # name of csv file
    if start_year == end_year:
        filename = f"{symbol}_{start_year}.csv"
    else:
        filename = f"{symbol}_{start_year}-{end_year}.csv"

    # writing to csv file
    data.to_csv(f'data/{filename}')


if __name__ == '__main__':
    args = docopt(__doc__)

    symbol = args['<stock-symbol>']
    year = args['--year']
    start_year = args['--start_year']
    end_year = args['--end_year']

    if year is not None:
        start_year = year
        end_year = year

    main(symbol, start_year, end_year)
