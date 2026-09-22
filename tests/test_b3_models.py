"""Unit tests for B3 Volatility Engine models and formulas."""

import pytest
import math
import numpy as np
from b3_vix.models.black_scholes import B3BlackScholesEngine
from b3_vix.models.implied_vol import ImpliedVolatilitySolver
from b3_vix.models.vix_bova import VixBovaEngine, business_days_to_time_to_expiry
from b3_vix.models.di_curve import DICurveInterpolator
from b3_vix.models.garch import GarchVolatilityModel
from b3_vix.connectors.market_data import B3MarketData
from b3_vix.connectors.rtd_feed import RTDDeskBridge


def test_di_curve_interpolation():
    curve = DICurveInterpolator.from_dict({21: 0.105, 42: 0.110})
    rate_31 = curve.zero_rate(31.5)
    assert 0.105 < rate_31 < 0.110
    r_cont = curve.continuous_rate(21)
    assert math.isclose(r_cont, math.log(1.105), abs_tol=1e-6)
    df = curve.discount_factor(21)
    assert math.isclose(df, (1.105) ** (-21.0 / 252.0), abs_tol=1e-6)


def test_b3_black_scholes_parity():
    S, K, du = 112.50, 110.00, 21
    t_years = du / 252.0
    r = math.log(1.105)
    vol = 0.28

    call_p = B3BlackScholesEngine.price("call", S, K, t_years, r, vol)
    put_p = B3BlackScholesEngine.price("put", S, K, t_years, r, vol)

    # Parity: C - P = S - K * exp(-r*T)
    left = call_p - put_p
    right = S - K * math.exp(-r * t_years)
    assert math.isclose(left, right, abs_tol=1e-5)


def test_b3_implied_vol_convergence():
    true_vol = 0.31
    S, K, t_years, r = 112.50, 115.00, 21 / 252.0, 0.10
    market_price = B3BlackScholesEngine.price("call", S, K, t_years, r, true_vol)

    solved = ImpliedVolatilitySolver.solve(market_price, "call", S, K, t_years, r)
    assert math.isclose(solved, true_vol, abs_tol=1e-5)


def test_vixbova_index_calculation():
    near_chain = B3MarketData.generate_bova11_chain(112.50, du_to_expiry=15)
    next_chain = B3MarketData.generate_bova11_chain(112.50, du_to_expiry=35)
    r = math.log(1.105)

    # CBOE calendar base (unified): T = calendar_days/365, N30 = 30/365.
    # Inputs are in DU, so convert explicitly:
    # calendar_days ~= DU * 365/252, then T = calendar_days/365
    # (numerically == DU/252, but expressed in calendar units).
    # NOTE: the synthetic chain itself is priced with DU/252 Black-Scholes
    # discounting (correct for B3); only the VIX variance/interpolation leg
    # uses the calendar base.
    v1 = VixBovaEngine.compute_single_term_variance(near_chain, time_to_exp=business_days_to_time_to_expiry(15), r=r)
    v2 = VixBovaEngine.compute_single_term_variance(next_chain, time_to_exp=business_days_to_time_to_expiry(35), r=r)
    vix = VixBovaEngine.calculate_vixbova(v1, v2)

    assert 10.0 < vix < 100.0


def test_rtd_formula_generator():
    f_profit = RTDDeskBridge.generate_excel_formula("profitchart", "BOVA11", "last")
    assert 'rtdtrading.rtdserver' in f_profit
    assert 'BOVA11' in f_profit

    f_tryd = RTDDeskBridge.generate_excel_formula("tryd", "WDOM22", "last")
    assert 'tryd.rtdserver' in f_tryd
