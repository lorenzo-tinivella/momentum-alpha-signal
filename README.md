# Momentum Alpha Signal

A systematic quant research project replicating and extending the momentum factor
first documented by Jegadeesh & Titman (1993).

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
