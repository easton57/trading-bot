"""
Script for downloading stock data

Usage:
  download_stock.py <stock-symbol> [--year=<year>]
    [--start_year=<start_year>] [--end_year=<end_year>]
    [--interval=<interval>] [--start_date=<start_date>]
    [--end_date=<end_date>]

Options:
  --year=<year>               Year to download from
  --start_year=<start_year>   Year to start
  --end_year=<end_year>       Year to end
  --interval=<interval>       Interval to download. Will download all data available for the specified interval
                              supported intervals: interval(how much data you get up to today)
                              1m(7 days), 2m(60 days), 5m(60 days), 15m(60 days), 30m(60 days), 60m(730 days), 90m(730 days)
  --start_date=<start_date>   date to start, meant to be used with --interval
  --end_date=<end_date>       date to end, meant to be used with --interval
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
        filename = f"{symbol}_{start_year}_1d.csv"
    else:
        filename = f"{symbol}_{start_year}-{end_year}_1d.csv"

    # writing to csv file
    write_to_csv(data, filename)


def interval_download(symbol, interval, start_date=None, end_date=None):
    """ To download a specific interval. This will download the max amount that it can for the specified interval """
    if start_date is None:
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
    if start_date is None:
        filename = f'{symbol}_{end_date}_{interval}.csv'
    else:
        filename = f'{symbol}_{start_date}-{end_date}_{interval}.csv'

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
    start_date = args['--start_date']
    end_date = args['--end_date']

    if year is not None:
        start_year = year
        end_year = year

    if interval is not None and (start_date is None or end_date is None):
        interval_download(symbol, interval)
    elif start_date is not None and end_date is not None:
        interval_download(symbol, interval, start_date, end_date)
    else:
        year_download(symbol, start_year, end_year)
