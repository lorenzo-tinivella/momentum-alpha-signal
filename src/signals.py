"""
signals.py
----------
Functions for constructing the sector-neutral momentum signal.
"""

import pandas as pd
import numpy as np


def compute_momentum(
    prices: pd.DataFrame,
    formation_long:  int = 252,
    formation_short: int = 21,
    min_obs:         int = 200
) -> pd.DataFrame:
    """
    Compute the 12-1 cross-sectional momentum signal.

    MOM(i,t) = P(i, t-formation_short) / P(i, t-formation_long) - 1

    Parameters
    ----------
    prices          : adjusted closing prices
    formation_long  : lookback start in trading days (default: 252 = 12m)
    formation_short : skip period in trading days   (default: 21  =  1m)
    min_obs         : minimum non-NaN observations required

    Returns
    -------
    momentum : pd.DataFrame, same shape as prices
    """
    price_long   = prices.shift(formation_long)
    price_short  = prices.shift(formation_short)
    momentum_raw = (price_short / price_long) - 1
    valid_obs    = (
        prices.pct_change()
        .rolling(window=formation_long, min_periods=min_obs)
        .count()
    )
    return momentum_raw.where(valid_obs >= min_obs)


def compute_sector_neutral_ranks(
    momentum:   pd.DataFrame,
    sector_map: pd.DataFrame,
    min_stocks: int = 5
) -> pd.DataFrame:
    """
    Compute sector-neutral percentile ranks.

    For each date and GICS sector, rank stocks by momentum score
    within the sector and compute the percentile rank in [0,1].

    Parameters
    ----------
    momentum   : momentum signal DataFrame
    sector_map : DataFrame with index=ticker, column='GICS Sector'
    min_stocks : minimum stocks per sector to compute valid rank

    Returns
    -------
    sn_ranks : pd.DataFrame, sector-neutral percentile ranks
    """
    sn_ranks = pd.DataFrame(
        np.nan,
        index=momentum.index,
        columns=momentum.columns
    )
    sectors = sector_map['GICS Sector'].unique()

    for date in momentum.index:
        row = momentum.loc[date]
        for sector in sectors:
            tickers_s = sector_map[
                sector_map['GICS Sector'] == sector
            ].index
            valid = tickers_s[
                tickers_s.isin(row.index) & row[tickers_s].notna()
            ]
            if len(valid) < min_stocks:
                continue
            sn_ranks.loc[date, valid] = row[valid].rank(pct=True)

    return sn_ranks


def ranks_to_quintiles(
    sn_ranks: pd.DataFrame,
    min_stocks: int = 10
) -> pd.DataFrame:
    """
    Convert sector-neutral percentile ranks to quintile labels 1-5.

    Parameters
    ----------
    sn_ranks   : sector-neutral percentile ranks in [0,1]
    min_stocks : minimum valid stocks required to assign quintiles

    Returns
    -------
    quintiles : pd.DataFrame, integer quintile labels 1-5
    """
    quintiles = pd.DataFrame(
        np.nan,
        index=sn_ranks.index,
        columns=sn_ranks.columns
    )
    bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]

    for date in sn_ranks.index:
        row   = sn_ranks.loc[date]
        valid = row.notna()
        if valid.sum() < min_stocks:
            continue
        quintiles.loc[date, valid] = pd.cut(
            row[valid], bins=bins,
            labels=[1, 2, 3, 4, 5],
            include_lowest=True
        ).astype(float)

    return quintiles
