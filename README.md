# B3 Volatility Engine & VIXBOVA Suite

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com)
[![Tests](https://img.shields.io/badge/tests-8%20passed-brightgreen.svg)]()
[![Market: B3](https://img.shields.io/badge/market-B3%20%7C%20Brazil-green.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Volatility Modeling, VIXBOVA Index Replication, and DI1 Yield Curve Engine for Brazilian Equities (B3).**

This repository modernizes legacy options and volatility tracking workbooks (`excel_legacy/b3_vixbova_volatility_engine_legacy.xlsm`) into a modular Python engine tailored to the Brazilian market's unique conventions:
- **DU-252 Business Day Calendar Basis** (vs 365 calendar days).
- **DI1 Yield Curve Discounting** ($DF = (1 + R_{\text{DI}})^{-DU/252}$).
- **CBOE VIX Replication on BOVA11 Options** (Discrete variance swap strip).
- **GARCH(1,1) Volatility Forecasting** via Maximum Likelihood Estimation.
- **RTD Bridge Specifications** for Brazilian desktop trading terminals (**Nelogica ProfitChart**, **Tryd**, and **Cedro Fast Trade**).

---

## 📐 Mathematical Foundations

### 1. CBOE VIX Index Replication (VIXBOVA)
Computes model-free 30-day implied volatility for the Brazilian market using out-of-the-money `BOVA11` calls and puts:

$$\sigma^2 = \frac{2}{T}\sum_i \frac{\Delta K_i}{K_i^2} e^{RT} Q(K_i) - \frac{1}{T}\left(\frac{F}{K_0} - 1\right)^2$$

$$\text{VIXBOVA} = 100 \times \sqrt{\sigma_{30\text{d}}^2}$$

Where:
- $F = K_{\text{min}} + e^{RT}(C_{\text{atm}} - P_{\text{atm}})$ is the forward index level.
- $K_0$ is the strike immediately below $F$.
- $\Delta K_i = \frac{K_{i+1} - K_{i-1}}{2}$ is the discrete strike interval.
- Linear interpolation across near-term ($T_1$) and next-term ($T_2$) expirations produces the constant 30-day metric.

### 2. Brazilian Fixed Income Discounting (DI1 Curve)
In B3, interest rates are quoted as annual compound rates based on 252 business days ($R_{\text{DI}}$). The continuous risk-free rate used in Black-Scholes is:

$$r_{\text{cont}} = \ln(1 + R_{\text{DI}})$$

Discount Factor:

$$DF(t) = \frac{1}{(1 + R_{\text{DI}})^{DU/252}}$$

### 3. GARCH(1,1) Econometric Model
Estimates time-varying volatility clustering on Brazilian indices:

$$\sigma_t^2 = \omega + \alpha \epsilon_{t-1}^2 + \beta \sigma_{t-1}^2, \quad \text{with } \alpha + \beta < 1$$

---

## ⚡ Quick Start

### Installation

```bash
git clone https://github.com/CostaJr007/b3-vix-volatility-engine.git
cd b3-vix-volatility-engine
pip install -e .
```

### Running Tests

```bash
pytest tests -v
```

### CLI Commands

```bash
# Compute Black-Scholes Greeks under DU-252 convention
b3-vix greeks --flag call --spot 112.50 --strike 110.00 --du 21 --rate 0.105 --vol 0.28

# Compute 30-day VIXBOVA Index
b3-vix vixbova --spot 112.50 --near-du 15 --next-du 35 --rate 0.105

# Generate RTD formula for ProfitChart or Tryd
b3-vix rtd --platform profitchart --ticker BOVA11
b3-vix rtd --platform tryd --ticker WDOM22

# Launch FastAPI REST service
b3-vix serve --port 8000
```

---

## 🌐 FastAPI Endpoints

- `GET /health`: Health status.
- `POST /api/v1/greeks`: Calculates Black-Scholes price and analytical Greeks with DU-252 time basis.
- `POST /api/v1/vixbova`: Computes VIXBOVA index across near-term and next-term options strips.
- `POST /api/v1/garch`: Fits GARCH(1,1) model and outputs volatility forecasts.
- `POST /api/v1/rtd-formula`: Returns exact Excel RTD formulas for ProfitChart, Tryd, and Fast Trade.

---

## 🗄️ Legacy VBA Archive (`vba_legacy/`)
Audited source code extracted from `OBT_VIX_MOVE.25.05.xlsm`:
- `BlackScholes_NewtonRaphson.bas`: European option pricing & Newton-Raphson IV solver.
- `RTD_Formula_Manager.bas`: Dynamic formula rewriting for Nelogica, Tryd, and Fast Trade.
- `Market_Recorder_AxesScaler.bas`: Dynamic chart axis scaling for `VIXBOVA` and `GFMOVE`.
- `Data_Scheduler_Cron.bas`: Real-time market tick recorder.
- `ExportarGrafico_HD.bas`: HD chart image exporter for automated Telegram reports.
- `Servidor1_RTD_Selector.frm`: UserForm for platform selection (Password: `12345`).

---

## 📄 License
MIT License. Author: [Adeilson da Costa (Costa Junior)](https://github.com/CostaJr007) — Ottawa, Canada.
