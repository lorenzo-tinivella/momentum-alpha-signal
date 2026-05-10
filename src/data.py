"""
data.py
-------
Functions for downloading and cleaning S&P 500 price data.
"""

import requests
import pandas as pd
import yfinance as yf


def get_sp500_tickers() -> tuple[list[str], pd.DataFrame]:
    """
    Scrape S&P 500 constituents from Wikipedia.

    Returns
    -------
    tickers : list of ticker symbols
    table   : full Wikipedia table with sector info
    """
    url     = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    table    = pd.read_html(response.text)[0]
    tickers  = table['Symbol'].tolist()
    tickers  = [t.replace('.', '-') for t in tickers]
    return tickers, table


def get_sp500_sectors(tickers: list[str]) -> pd.DataFrame:
    """
    Download GICS sector assignments for S&P 500 constituents.

    Parameters
    ----------
    tickers : list of ticker symbols in the working universe

    Returns
    -------
    sector_map : pd.DataFrame with index=Symbol, column=GICS Sector
    """
    url      = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers  = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    table    = pd.read_html(response.text)[0]
    sm       = table[['Symbol', 'GICS Sector']].copy()
    sm['Symbol'] = sm['Symbol'].str.replace('.', '-', regex=False)
    sm = sm.set_index('Symbol')
    return sm.loc[sm.index.isin(tickers)]


def download_prices(
    tickers: list[str],
    start: str = "2010-01-01",
    end: str   = "2024-12-31"
) -> pd.DataFrame:
    """
    Download adjusted closing prices for all tickers via yfinance.

    Parameters
    ----------
    tickers : list of ticker symbols
    start   : start date (YYYY-MM-DD)
    end     : end date   (YYYY-MM-DD)

    Returns
    -------
    prices : pd.DataFrame, shape (trading_days, n_tickers)
    """
    raw    = yf.download(tickers, start=start, end=end,
                         auto_adjust=True, progress=True)
    prices = raw['Close']
    return prices


def clean_prices(
    prices: pd.DataFrame,
    max_missing_pct: float = 0.20,
    min_history_days: int  = 252
) -> pd.DataFrame:
    """
    Remove tickers with excessive missing data or short history.

    Parameters
    ----------
    prices           : raw price DataFrame
    max_missing_pct  : maximum fraction of missing values allowed
    min_history_days : minimum number of non-NaN observations required

    Returns
    -------
    prices_clean : cleaned price DataFrame
    """
    missing_pct    = prices.isnull().mean()
    valid_missing  = missing_pct[missing_pct <= max_missing_pct].index
    history_length = prices.notna().sum()
    valid_history  = history_length[
        history_length >= min_history_days
    ].index
    valid_tickers  = valid_missing.intersection(valid_history)
    return prices[valid_tickers].copy()
