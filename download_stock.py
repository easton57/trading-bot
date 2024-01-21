"""
Script for downloading stock data

Usage:
  download_stock.py <stock-symbol> [--year=<year>] [--start_year=<start_year>] [--end_year=<end_year>] [--interval=<interval>]

Options:
  --year=<year>               Year to download from
  --start_year=<start_year>   Year to start
  --end_year=<end_year>       Year to end
  --interval=<interval>       Interval to download, supported intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m
"""

import logging

import yfinance as yf
from docopt import docopt
from datetime import datetime, timedelta


def year_download(symbol, start_year, end_year):
    start_date = f'{start_year}-01-01'
    end_date = f'{end_year}-12-31'

    data = yf.download(symbol, start=start_date, end=end_date)

    # name of csv file
    if start_year == end_year:
        filename = f"{symbol}_{start_year}.csv"
    else:
        filename = f"{symbol}_{start_year}-{end_year}.csv"

    # writing to csv file
    write_to_csv(data, filename)


def interval_download(symbol, interval):
    """ To download a specific interval. This will download the max amount that it can for the specified interval """
    end_date = datetime.today().strftime('%Y-%m-%d')

    if interval == '1m':
        # Has to be the last 7 days
        start_date = datetime.today() - timedelta(days=6)
    elif interval in ['2m', '5m', '15m', '30m', '90m']:
        # These are the last 60 days
        start_date = datetime.today() - timedelta(days=59)
    elif interval in ['60m', '1h']:
        # These have a phat delta of 730 days
        start_date = datetime.today() - timedelta(days=729)
    else:
        logging.error("Interval invalid! Please refer to help for appropriate interval times")
        return

    # Download Data
    data = yf.download(symbol, start=start_date, end=end_date, interval=interval)

    # Create our filename
    filename = f'{symbol}_{end_date}_{interval}.csv'

    # Write the file out
    write_to_csv(data, filename)


def write_to_csv(data, filename):
    data.to_csv(f'data/{filename}')


if __name__ == '__main__':
    args = docopt(__doc__)

    symbol = args['<stock-symbol>']
    year = args['--year']
    start_year = args['--start_year']
    end_year = args['--end_year']
    interval = args['--interval']

    if year is not None:
        start_year = year
        end_year = year

    if interval is not None:
        interval_download(symbol, interval)
    else:
        year_download(symbol, start_year, end_year)
