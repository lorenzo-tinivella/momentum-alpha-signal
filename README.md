# Momentum Alpha Signal

A systematic quant research project replicating and extending the momentum factor
first documented by Jegadeesh & Titman (1993).

## Viewing Notebooks

## Viewing Notebooks

| Notebook | Colab |
|---|---|
| 01 - Data Collection | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/lorenzo-tinivella/momentum-alpha-signal/blob/main/notebooks/01_data_collection.ipynb) |
| 02 - Signal Construction | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/lorenzo-tinivella/momentum-alpha-signal/blob/main/notebooks/02_signal_construction.ipynb) |
| 03 - IC Analysis | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/lorenzo-tinivella/momentum-alpha-signal/blob/main/notebooks/03_ic_analysis.ipynb) |
| 04 - Backtesting | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/lorenzo-tinivella/momentum-alpha-signal/blob/main/notebooks/04_backtesting.ipynb) |
| 05 - Risk Analysis | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/lorenzo-tinivella/momentum-alpha-signal/blob/main/notebooks/05_risk_analysis.ipynb) |

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
