# Momentum Alpha Signal

A systematic quant research project replicating and extending the momentum factor
first documented by Jegadeesh & Titman (1993).

## Viewing Notebooks

GitHub's notebook renderer may have display issues with long notebooks.
For best rendering, view the notebooks on nbviewer:

👉 [View notebooks on nbviewer](https://nbviewer.org/github/TUO-USERNAME/momentum-alpha-signal/tree/main/notebooks/)

## Objective
Build, test, and analyze a cross-sectional momentum signal on S&P 500 equities,
following a rigorous quant research process: signal construction, IC analysis,
backtesting, and risk decomposition.

## Project Structure
- `notebooks/` — step-by-step analysis notebooks
- `src/` — reusable Python modules
- `report/` — final research memo

## Signal
12-1 month cross-sectional momentum: buy top quintile, sell bottom quintile.

## Stack
Python · pandas · numpy · yfinance · matplotlib · scipy
