"""
metrics.py
----------
Functions for computing portfolio performance and signal quality metrics.
"""

import pandas as pd
import numpy as np
from scipy import stats


def compute_performance(returns: pd.Series) -> dict:
    """
    Compute annualized portfolio performance metrics.

    Parameters
    ----------
    returns : monthly portfolio returns

    Returns
    -------
    metrics : dict with CAGR, Volatility, Sharpe, Max Drawdown,
              Calmar, Skewness
    """
    returns     = returns.dropna()
    n           = len(returns)
    cumulative  = (1 + returns).cumprod()
    total_ret   = cumulative.iloc[-1] - 1
    cagr        = (1 + total_ret) ** (12 / n) - 1
    vol         = returns.std() * np.sqrt(12)
    sharpe      = cagr / vol if vol > 0 else np.nan
    rolling_max = cumulative.cummax()
    drawdown    = (cumulative - rolling_max) / rolling_max
    max_dd      = drawdown.min()
    calmar      = cagr / abs(max_dd) if max_dd != 0 else np.nan
    skewness    = returns.skew()

    return {
        'CAGR'        : cagr,
        'Volatility'  : vol,
        'Sharpe'      : sharpe,
        'Max Drawdown': max_dd,
        'Calmar'      : calmar,
        'Skewness'    : skewness,
        'N'           : n,
    }


def compute_ic_series(
    signal:      pd.DataFrame,
    prices:      pd.DataFrame,
    holding_days: int = 21,
    min_stocks:  int = 50
) -> pd.Series:
    """
    Compute monthly Information Coefficient (IC) time series.

    IC is the Spearman rank correlation between the signal at
    month-end t and forward returns from t to t+holding_days.

    Parameters
    ----------
    signal       : signal DataFrame (e.g. sector-neutral ranks)
    prices       : adjusted closing prices
    holding_days : forward return horizon in trading days
    min_stocks   : minimum stocks required to compute IC

    Returns
    -------
    ic_series : pd.Series of monthly IC values
    """
    fwd_returns = prices.pct_change(holding_days).shift(-holding_days)
    records     = []
    month_ends  = signal.resample('M').last().index

    for date in month_ends:
        if date not in signal.index:
            continue
        sig     = signal.loc[date]
        forward = fwd_returns.loc[date]
        valid   = sig.notna() & forward.notna()
        if valid.sum() < min_stocks:
            continue
        ic, _   = stats.spearmanr(sig[valid], forward[valid])
        records.append({'date': date, 'ic': ic,
                        'n_stocks': valid.sum()})

    return pd.DataFrame(records).set_index('date')


def summarize_ic(ic_df: pd.DataFrame) -> dict:
    """
    Compute IC summary statistics.

    Parameters
    ----------
    ic_df : DataFrame with column 'ic'

    Returns
    -------
    stats : dict with Mean IC, IC Std, ICIR, Hit Rate, p-value
    """
    from scipy import stats as scipy_stats

    ic       = ic_df['ic'].dropna()
    mean_ic  = ic.mean()
    std_ic   = ic.std()
    icir     = mean_ic / std_ic if std_ic > 0 else np.nan
    hit_rate = (ic > 0).mean() * 100
    t_stat, p_value = scipy_stats.ttest_1samp(ic, 0)

    return {
        'Mean IC' : mean_ic,
        'IC Std'  : std_ic,
        'ICIR'    : icir,
        'Hit Rate': hit_rate,
        't-stat'  : t_stat,
        'p-value' : p_value,
        'N'       : len(ic),
    }
