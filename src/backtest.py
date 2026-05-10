"""
backtest.py
-----------
Functions for portfolio construction, backtesting, and cost modeling.
"""

import pandas as pd
import numpy as np


def compute_quintile_returns(
    prices:    pd.DataFrame,
    quintiles: pd.DataFrame
) -> pd.DataFrame:
    """
    Compute equal-weighted monthly returns for each quintile (1-5).

    Parameters
    ----------
    prices    : adjusted closing prices
    quintiles : quintile assignments 1-5

    Returns
    -------
    quintile_returns : pd.DataFrame with columns Q1..Q5
    """
    monthly_prices    = prices.resample('M').last()
    monthly_returns   = monthly_prices.pct_change()
    monthly_quintiles = quintiles.resample('M').last()
    records = []

    for i in range(1, len(monthly_prices)):
        date_signal = monthly_prices.index[i-1]
        date_return = monthly_prices.index[i]
        if date_signal not in monthly_quintiles.index:
            continue
        q_assign   = monthly_quintiles.loc[date_signal]
        month_rets = monthly_returns.loc[date_return]
        row = {'date': date_return}
        for q in range(1, 6):
            mask   = (q_assign == q) & month_rets.notna()
            stocks = month_rets[mask]
            row[f'Q{q}'] = stocks.mean() if len(stocks) > 0 else np.nan
        records.append(row)

    return pd.DataFrame(records).set_index('date')


def compute_monthly_costs(
    quintiles:    pd.DataFrame,
    cost_bps:     float = 5.0,
    borrow_annual: float = 0.005
) -> pd.DataFrame:
    """
    Compute monthly transaction costs and borrow fees.

    Parameters
    ----------
    quintiles     : quintile assignments 1-5
    cost_bps      : transaction cost per trade in basis points
    borrow_annual : annual borrow fee on short positions

    Returns
    -------
    costs : pd.DataFrame with columns tc, borrow, total
    """
    monthly_q      = quintiles.resample('M').last()
    cost_per_trade = cost_bps / 10000
    borrow_monthly = borrow_annual / 12
    records        = []

    for i in range(1, len(monthly_q)):
        date_curr = monthly_q.index[i]
        date_prev = monthly_q.index[i-1]
        q_curr    = monthly_q.loc[date_curr]
        q_prev    = monthly_q.loc[date_prev]
        total_to  = 0

        for q in [1, 5]:
            s_curr      = set(q_curr[q_curr == q].index)
            s_prev      = set(q_prev[q_prev == q].index)
            new_entries = s_curr - s_prev
            total_to   += (
                len(new_entries) / len(s_curr)
                if len(s_curr) > 0 else 0
            )

        tc = total_to * cost_per_trade
        records.append({
            'date'  : date_curr,
            'tc'    : tc,
            'borrow': borrow_monthly,
            'total' : tc + borrow_monthly
        })

    return pd.DataFrame(records).set_index('date')


def apply_vol_scaling(
    gross_returns: pd.Series,
    prices:        pd.DataFrame,
    target_vol:    float = 0.08,
    max_weight:    float = 2.0,
    vol_window:    int   = 21
) -> tuple[pd.Series, pd.Series]:
    """
    Apply volatility scaling to portfolio gross returns.

    w(t) = min(target_vol / realized_vol(t-1), max_weight)
    r_scaled(t) = w(t-1) * r_gross(t)

    Parameters
    ----------
    gross_returns : monthly gross portfolio returns
    prices        : price DataFrame for market vol estimation
    target_vol    : target annualized volatility
    max_weight    : maximum leverage cap
    vol_window    : rolling window for realized vol (trading days)

    Returns
    -------
    weights        : pd.Series of scaling weights
    scaled_returns : pd.Series of scaled gross returns
    """
    daily_market = prices.pct_change().mean(axis=1)
    realized_vol = (
        daily_market
        .rolling(window=vol_window, min_periods=15)
        .std() * np.sqrt(252)
    )
    vol_monthly = realized_vol.resample('M').last()
    vol_aligned = vol_monthly.reindex(
        gross_returns.index, method='ffill'
    ).shift(1)

    weights = (target_vol / vol_aligned).clip(
        lower=0.0, upper=max_weight
    ).fillna(1.0)

    return weights, weights * gross_returns
