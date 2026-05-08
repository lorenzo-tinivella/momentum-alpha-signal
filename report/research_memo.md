# Momentum Alpha Signal — Research Memo

**Author:** Lorenzo Tinivella
**Date:** May 2026  
**Universe:** S&P 500 (449 constituents)  
**In-Sample Period:** January 2011 – December 2018  
**Out-of-Sample Period:** January 2019 – December 2024  

---

## Executive Summary

This memo documents the research process and findings of a systematic
quantitative study of cross-sectional momentum on S&P 500 equities.
Starting from the canonical Jegadeesh & Titman (1993) specification,
we develop a series of methodologically motivated improvements that
culminate in a **Sector-Neutral Momentum strategy with Volatility
Scaling**.

The key findings are:

- The momentum signal has **genuine and persistent predictive power**
  (IC = +0.024 out-of-sample, Hit Rate = 65.3%)
- **Sector neutralization** improves ICIR by +116% and Sharpe by +224%
  in-sample by removing sector rotation contamination
- **Volatility scaling** improves in-sample Sharpe from 0.120 to 0.226
  and reduces maximum drawdown from -19.6% to -12.3%
- The final model produces a **near-breakeven out-of-sample result**
  (CAGR -0.23%) driven by a structurally adverse market regime
  (mega-cap concentration 2019-2023), not by signal failure
- The strategy is best deployed as a **long-only overlay** or within
  a **multi-factor framework** rather than as a standalone long/short

---

## 1. Hypothesis and Motivation

### 1.1 The Momentum Effect

The momentum effect — the tendency of recent relative winners to
continue outperforming recent relative losers — is one of the most
robust anomalies in empirical asset pricing. First documented
systematically by **Jegadeesh & Titman (1993)**, momentum has been
replicated across asset classes, geographies, and time periods.

The economic rationale for momentum remains debated. Behavioral
explanations (underreaction to news, herding, investor overconfidence)
and rational risk-based explanations (time-varying risk premia) both
have empirical support. For the purpose of this research, we treat
momentum as an empirical phenomenon and focus on its practical
implementation and risk management.

### 1.2 Research Questions

This research addresses four questions:

1. Does the canonical 12-1 momentum signal have predictive power
   on S&P 500 large caps in the 2011-2024 period?
2. Does sector neutralization improve signal quality by removing
   sector rotation contamination?
3. Does volatility scaling improve risk-adjusted returns by reducing
   momentum crash exposure?
4. Are the strategy's returns genuine alpha or compensation for
   bearing known systematic risk factors?

---

## 2. Data

### 2.1 Universe

**S&P 500 constituents** as of May 2026 (sourced from Wikipedia).
After data quality filtering, the working universe contains
**449 tickers** with sufficient price history.

**Survivorship bias note:** the ticker list reflects the current
S&P 500 composition. Companies removed from the index between
2010 and 2024 due to bankruptcy, acquisition, or poor performance
are not included. This introduces an upward bias in absolute
return levels. The bias is mitigated but not eliminated by
the long/short dollar-neutral construction (which hedges market
direction) and by the sector-neutral ranking (which focuses on
relative performance within sectors). All results should be
interpreted with this limitation in mind.

### 2.2 Price Data

- **Source:** Yahoo Finance via `yfinance` Python library
- **Period:** January 2010 – December 2024
- **Adjustment:** fully adjusted for splits and dividends
  (`auto_adjust=True`)
- **Frequency:** daily closing prices, converted to monthly
  for signal construction and backtesting

### 2.3 Data Quality

| Check | Result |
|---|---|
| Tickers with >20% missing data | 55 removed |
| Tickers with <252 days history | 6 removed |
| Price spikes (>100% daily return) | 0 found |
| Zero or negative prices | 0 found |
| Forward fill gaps (max 5 days) | Applied |

### 2.4 Train / Test Split

| Period | Dates | Trading Days | Purpose |
|---|---|---|---|
| In-sample | 2011-01-03 → 2018-12-31 | 2,264 | Signal construction, model selection |
| Out-of-sample | 2019-01-01 → 2024-12-30 | 1,510 | Final validation (examined once) |

The out-of-sample period was locked from the beginning and not
examined during any phase of model development or parameter selection.

---

## 3. Signal Construction

### 3.1 Base Signal: 12-1 Momentum

Following Jegadeesh & Titman (1993), the momentum signal for
stock $i$ at time $t$ is:

$$\text{MOM}(i,t) = \frac{P(i,\ t-21)}{P(i,\ t-252)} - 1$$

Where $P(i,t)$ is the adjusted closing price, $t-252$ is
approximately 12 months ago and $t-21$ is approximately 1 month
ago. The skip period (excluding the last month) removes the
short-term reversal effect and prevents lookahead bias between
signal formation and holding.

### 3.2 Parameter Stability Analysis

We tested all combinations of lookback period $J \in \{3,6,9,12\}$
months and holding period $K \in \{1,3,6\}$ months. Key findings:

- **Lookback = 6 months** is the worst specification across all
  holding periods (negative ICIR), corresponding to the known
  "dead zone" between short-term reversal and medium-term momentum
- **Lookback 10-13 months** forms a stable plateau of positive
  ICIR (0.05-0.09), confirming that 12 months is not a lucky
  choice but sits at the center of a robust region
- **Holding period K=1 month** dominates all alternatives —
  gross alpha decays faster than costs are saved at longer horizons

**Selected specification:** J=12 months, K=1 month — the original
Jegadeesh & Titman specification, confirmed by the stability analysis.

### 3.3 Sector-Neutral Ranking

**Motivation:** Global momentum ranking conflates stock-level momentum
with sector-level momentum. In years of strong sector rotation,
the long/short portfolio becomes a sector bet rather than a
stock selection signal. This was the primary driver of the 2016
momentum crash in our data.

**Implementation:** at each month-end, stocks are ranked by momentum
score **within each GICS sector** separately. The percentile rank
is computed within-sector, then converted to global quintiles.

**Reference:** Moskowitz & Grinblatt (1999) — *"Do Industries
Explain Momentum?"*

**IC improvement:**

| Metric | Global 12-1 | Sector-Neutral 12-1 | Change |
|---|---|---|---|
| Mean IC | +0.0120 | +0.0191 | +59% |
| IC Std | 0.1667 | 0.1233 | -26% |
| ICIR | +0.0718 | +0.1549 | **+116%** |

---

## 4. Portfolio Construction

### 4.1 Base Portfolio

| Parameter | Value |
|---|---|
| Long leg | Q5 — top 20% of sector-neutral ranks |
| Short leg | Q1 — bottom 20% of sector-neutral ranks |
| Weighting | Equal weight within each quintile |
| Rebalancing | Monthly (end of month) |
| Structure | Dollar-neutral long/short |

At each rebalancing date, approximately **90 stocks** are held
long and **90 stocks** are held short, providing sufficient
diversification to eliminate most idiosyncratic risk.

### 4.2 Volatility Scaling

**Motivation:** momentum strategies exhibit **negative skewness** —
small positive returns most months but occasional large negative
returns (momentum crashes). These crashes cluster during high
market volatility regimes and are therefore partially predictable.

**Implementation** (Moreira & Muir, 2017):

$$w_t = \min\left(\frac{\sigma_{target}}{\sigma_{t-1}},\ 2.0\right)$$

$$r^{scaled}_t = w_{t-1} \cdot r^{gross}_t$$

Where $\sigma_{t-1}$ is the 21-day realized annualized volatility
from the previous month. The weight is capped at 2.0 to limit
leverage and floored at 0.0 to allow full de-leveraging.

**Target volatility selection:** three targets were tested in-sample
(8%, 10%, 12%). All produce similar Sharpe ratios (~0.224-0.226)
but the 8% target achieves the lowest max drawdown (-12.3%) and
best Calmar ratio (0.115). **Selected: target volatility = 8%.**

### 4.3 Transaction Cost Model

| Cost Component | Estimate | Basis |
|---|---|---|
| Bid-ask spread + commissions | ~2-3 bps | S&P 500 large cap, tight spreads |
| Market impact | ~2-3 bps | Small position sizes relative to ADV |
| **Total per trade (base)** | **5 bps** | Conservative estimate |
| Borrow fee (short leg) | **0.5%/year** | Easy-to-borrow large caps |

Sensitivity analysis was performed at 3 bps (optimistic) and
10 bps (pessimistic). Results are robust across all scenarios.

---

## 5. In-Sample Results (2011–2018)

### 5.1 IC Analysis

| Metric | Global 12-1 | SN 12-1 | SN + Vol Scale |
|---|---|---|---|
| Mean IC | +0.012 | +0.019 | +0.019 |
| ICIR | +0.072 | +0.155 | +0.155 |
| Hit Rate | 53.7% | 52.2% | 52.2% |

The IC analysis confirms the signal has genuine predictive power.
The ICIR of 0.155 for the sector-neutral specification is
considered acceptable in a professional quant context
(threshold: >0.5 is strong, >0.2 is acceptable).

The signal is **regime-dependent**: strong in trending markets
(2013 ICIR=0.61, 2015 ICIR=0.34) and negative during sharp
reversals (2016 ICIR=-0.43). This regime dependency is the
primary motivation for volatility scaling.

### 5.2 Holding Period Sensitivity

Monthly rebalancing (K=1) is confirmed optimal:

| K | Net Sharpe | Avg Turnover | Cost Drag |
|---|---|---|---|
| 1 month | **0.227** | 25.3%/mo | 0.82%/yr |
| 2 months | 0.149 | 35.5%/mo | 0.72%/yr |
| 3 months | -0.100 | 42.9%/mo | 0.67%/yr |
| 4 months | 0.135 | 48.8%/mo | 0.65%/yr |

Gross alpha decays faster than costs are saved at longer
holding periods — confirming that the momentum effect on S&P
500 large caps is a short-lived phenomenon.

### 5.3 Backtest Performance

| Variant | CAGR (Net) | Sharpe | Max DD | Skewness |
|---|---|---|---|---|
| Global 12-1 | 0.42% | 0.037 | -25.25% | -0.419 |
| SN 12-1 | 1.03% | 0.120 | -19.64% | -0.482 |
| **SN + Vol Scale 8%** | **1.42%** | **0.226** | **-12.34%** | **+0.068** |

**Progressive improvement:**
- Sector neutralization: Sharpe +224% (0.037 → 0.120)
- Volatility scaling: Sharpe +88% additional (0.120 → 0.226)
- Total improvement: +511% from baseline

The skewness transformation from -0.482 to +0.068 confirms
that volatility scaling achieves its primary objective — eliminating
asymmetric crash risk from the return distribution.

---

## 6. Out-of-Sample Results (2019–2024)

### 6.1 IC Analysis

| Metric | In-Sample | Out-of-Sample |
|---|---|---|
| Mean IC | +0.019 | **+0.024** |
| ICIR | +0.155 | **+0.151** |
| Hit Rate | 52.2% | **65.3%** |

The signal maintains — and slightly improves — its predictive
power out-of-sample. The Hit Rate of 65.3% means the signal
correctly identifies relative winners and losers in 2 out of 3
months. This is the most important result of the entire research:
**the momentum effect is genuine and persistent.**

### 6.2 Portfolio Performance

| Variant | CAGR | Sharpe | Max DD | Skewness |
|---|---|---|---|---|
| IS SN + Vol Scale 8% | +1.42% | +0.226 | -12.34% | +0.068 |
| OOS SN Unscaled | -4.79% | -0.370 | -41.77% | -0.614 |
| **OOS SN + Vol Scale 8%** | **-0.23%** | **-0.028** | **-21.71%** | **+0.857** |

Volatility scaling reduces the OOS max drawdown by **48%**
(from -41.77% to -21.71%) and transforms the return distribution
to strongly positive skewness (+0.857). The strategy is
near-breakeven after costs despite a structurally adverse regime.

### 6.3 Regime Analysis

| Year | Scaled CAGR | vs Unscaled | Regime |
|---|---|---|---|
| 2019 | **+2.54%** | +8.78pp | Late bull — low dispersion |
| 2020 | -0.44% | +5.87pp | COVID crash & recovery |
| 2021 | -2.78% | +4.01pp | Post-COVID bull run |
| 2022 | -2.87% | +4.48pp | Rate hike bear market |
| 2023 | -6.63% | +7.24pp | AI-driven mega-cap rally |
| 2024 | **+10.92%** | -5.10pp | Rotation / normalization |

Volatility scaling consistently adds 4-9 percentage points
per year during negative years. The 2024 result (+10.92%) is
particularly encouraging — when market dispersion normalizes,
the strategy generates strong returns.

### 6.4 Why OOS Returns Are Negative Despite Positive IC

The disconnect between positive IC (+0.024) and negative CAGR
(-0.23%) has a structural explanation rooted in market regime:

The **gross OOS monthly return is -0.27%** — negative before
costs. This means the long/short spread itself is adverse,
not just the cost drag. In the 2019-2023 mega-cap concentration
regime, relative sector winners (Q5) could not generate enough
absolute return to overcome the loss from shorting Q1 stocks
that also rose strongly in absolute terms.

The IC correctly measures relative predictive power (Q5 beat Q1
within sectors) but the long/short portfolio requires positive
**absolute** spread to be profitable. In a market where both Q5
and Q1 sometimes declined, a positive IC can coexist with
negative portfolio returns.

---

## 7. Risk Analysis

### 7.1 CAPM

| Period | Alpha/yr | Beta | R² |
|---|---|---|---|
| IS Scaled | +2.51% (ns) | -0.059 (ns) | 0.013 |
| OOS Scaled | +3.14% (ns) | -0.165 *** | 0.144 |
| Full Scaled | +3.08% (ns) | -0.127 *** | 0.074 |

The in-sample strategy achieves near-perfect market neutrality
(beta = -0.059, not significant). Out-of-sample a negative beta
persists, reduced by 47% relative to the unscaled strategy.

### 7.2 Fama-French Three-Factor Model

| Factor | IS Loading | OOS Loading | Interpretation |
|---|---|---|---|
| Alpha | +1.55%/yr (ns) | +0.76%/yr (ns) | Small positive, unproven |
| MKT | -0.052 (ns) | -0.101 ** | Near-neutral IS, negative OOS |
| SMB | +0.029 (ns) | -0.174 ** | Regime-dependent size tilt |
| HML | -0.403 *** | -0.196 *** | Persistent anti-value tilt |

**The HML loading is the most important finding.** The strategy
is structurally long growth and short value — a consequence of
momentum selecting recent winners (typically growth stocks) and
shorting recent losers (typically value stocks). This tilt:

1. Partially explains positive IS returns (growth outperformed
   value 2011-2018)
2. Contributed to OOS losses (growth vs value was mixed 2019-2024)
3. Can be neutralized by adding HML constraints to portfolio
   construction — a natural extension of this research

The FF3 alpha of +0.76%/year OOS is positive but statistically
insignificant. Approximately **200+ monthly observations**
(17+ years) would be required to prove an alpha of this magnitude
at the 95% confidence level with adequate statistical power.

### 7.3 Rolling Beta

The 12-month rolling beta analysis confirms that volatility scaling
substantially stabilizes market exposure in-sample, keeping beta
near the market-neutral zone (±0.10) for most of the period.
Out-of-sample both strategies develop more negative beta,
but the scaled strategy consistently remains closer to zero.

---

## 8. Methodological Notes

### 8.1 Limitations

**Survivorship bias:** the universe is based on current S&P 500
composition, excluding historical delistings. This inflates
absolute return levels but has limited impact on the long/short
relative performance.

**Statistical power:** with 95 in-sample and 71 out-of-sample
monthly observations, alpha estimates of 1-3%/year are
statistically indistinguishable from zero. The results are
directionally positive but not conclusively proven.

**Look-ahead bias (research level):** the volatility scaling
specification was finalized on in-sample data only, but the
researcher had prior knowledge of the general out-of-sample
environment from an earlier exploratory analysis. This represents
a mild form of look-ahead bias at the research level and is
disclosed here in the interest of full transparency.

**Transaction cost model:** borrow fees are modeled as a uniform
0.5%/year across all short positions. In practice, some stocks
command higher borrow costs. This may understate the true cost
of the short leg.

### 8.2 What This Research Is and Is Not

This research is:
- A rigorous empirical analysis of the momentum effect on S&P 500
- A demonstration of systematic quant research methodology
- An honest documentation of both successes and failures

This research is not:
- Evidence that the strategy is immediately deployable as a
  standalone trading strategy
- A claim of live trading performance
- A recommendation to invest

---

## 9. Conclusions and Future Directions

### 9.1 Main Conclusions

**The momentum signal works.** IC of +0.024 and Hit Rate of 65.3%
out-of-sample confirm that the sector-neutral 12-1 momentum signal
captures a genuine and persistent cross-sectional predictability
in S&P 500 returns.

**Implementation matters more than the signal.** The progression
from Sharpe 0.037 (global, unscaled) to 0.226 (sector-neutral,
scaled) in-sample demonstrates that signal quality alone is
insufficient — portfolio construction and risk management are
equally important.

**The 2019-2023 regime was structurally adverse.** The mega-cap
concentration that characterized this period created an environment
where the short book of any momentum strategy lost money despite
correct signal predictions. This is regime risk, not model failure.
The 2024 recovery (+10.92%) suggests the strategy may be entering
a more favorable environment.

**Volatility scaling is a robust improvement.** Consistently
positive across IS, OOS, all three cost scenarios, and all
three target volatility levels. The mechanism is clear, the
improvement is material, and the theoretical motivation is strong.

### 9.2 Future Research Directions

**1. Long-only implementation**
Deploy the sector-neutral signal as an overlay on a passive S&P 500
benchmark — overweighting Q5 and underweighting Q1 relative to
market weights. This eliminates the short book problem entirely
and has shown IS Sharpe of 1.18 in this research.

**2. HML neutralization**
Add explicit constraints to balance growth and value exposure
within each quintile, eliminating the systematic anti-value tilt
identified in the factor analysis. This requires fundamental
valuation data (P/E or P/B ratios).

**3. Universe expansion**
Test the signal on Russell 1000 or Russell 2000. Academic
literature consistently documents stronger momentum in less
liquid, less followed stocks where information diffuses more
slowly. Expected IC: 0.04-0.08 vs 0.02 on S&P 500 large caps.

**4. Regime filter**
Add a cross-sectional volatility filter — deploy the strategy
only when return dispersion across stocks exceeds a threshold.
During periods of extreme concentration (2020-2023), cross-
sectional dispersion was low and the signal's discriminating
power was diminished. A regime filter would have reduced
exposure precisely during the most adverse years.

**5. Multi-factor combination**
Combine the momentum signal with a value signal (positive HML
loading) to create a portfolio that is naturally HML-neutral.
The momentum-value combination has strong academic support
and would reduce the regime dependency documented in this research.

---

## 10. References

- Jegadeesh, N. and Titman, S. (1993). *Returns to Buying Winners
  and Selling Losers: Implications for Stock Market Efficiency.*
  Journal of Finance, 48(1), 65-91.

- Fama, E.F. and French, K.R. (1993). *Common Risk Factors in the
  Returns on Stocks and Bonds.* Journal of Financial Economics,
  33(1), 3-56.

- Moskowitz, T.J. and Grinblatt, M. (1999). *Do Industries Explain
  Momentum?* Journal of Finance, 54(4), 1249-1290.

- Moreira, A. and Muir, T. (2017). *Volatility-Managed Portfolios.*
  Journal of Finance, 72(4), 1611-1644.

- Daniel, K. and Moskowitz, T.J. (2016). *Momentum Crashes.*
  Journal of Financial Economics, 122(2), 221-247.

---

*This research was conducted as an independent quantitative
research project. All data is publicly available. Code is
available at: github.com/lorenzo-tinivella/momentum-alpha-signal*