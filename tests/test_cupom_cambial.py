"""Tests for the onshore dollar coupon (cupom cambial) and FRC forwards."""

import math

import pytest

from b3_vix.models.cupom_cambial import (
    CupomQuote,
    cupom_continuous,
    fair_dol_futures,
    frc_forward_cupom,
    implied_cupom,
    interpolate_cupom,
)


def test_parity_round_trip():
    spot, di, cc, du = 5.40, 0.10, 0.025, 63
    f = fair_dol_futures(spot, di, cc, du)
    assert implied_cupom(spot, f, di, du) == pytest.approx(cc, rel=1e-12)


def test_implied_cupom_direction():
    # Futures rich vs carry-implied-with-zero-coupon -> negative cupom.
    cc = implied_cupom(spot=5.40, futures=5.60, di_annual=0.10, business_days=63)
    assert cc < 0.03  # sanity bound, sign depends on carry
    cheap = implied_cupom(spot=5.40, futures=5.30, di_annual=0.10, business_days=63)
    assert cheap > cc  # cheaper futures -> higher implied coupon


def test_sujo_below_limpo():
    # Same futures/DI: lagged (lower) PTAX input -> lower implied cupom.
    f = fair_dol_futures(spot=5.40, di_annual=0.10, cupom=0.02, business_days=63)
    limpo = implied_cupom(spot=5.40, futures=f, di_annual=0.10, business_days=63)
    sujo = implied_cupom(spot=5.38, futures=f, di_annual=0.10, business_days=63)
    assert sujo < limpo


def test_frc_forward_consistency():
    cc1, du1, cc2, du2 = 0.02, 63, 0.03, 126
    fwd = frc_forward_cupom(cc1, du1, cc2, du2)
    t1, t2 = du1 / 252.0, du2 / 252.0
    lhs = (1.0 + cc2) ** t2
    rhs = (1.0 + cc1) ** t1 * (1.0 + fwd) ** (t2 - t1)
    assert lhs == pytest.approx(rhs, rel=1e-12)


def test_interpolate_cupom():
    qs = [CupomQuote(21, 0.02), CupomQuote(63, 0.03)]
    assert interpolate_cupom(qs, 42) == pytest.approx(0.025)
    assert interpolate_cupom(qs, 1) == pytest.approx(0.02)  # flat left
    assert interpolate_cupom(qs, 500) == pytest.approx(0.03)  # flat right


def test_cupom_continuous():
    assert cupom_continuous(0.02) == pytest.approx(math.log(1.02))


def test_invalid_inputs():
    with pytest.raises(ValueError):
        implied_cupom(spot=0.0, futures=5.5, di_annual=0.10, business_days=63)
    with pytest.raises(ValueError):
        implied_cupom(spot=5.4, futures=5.5, di_annual=0.10, business_days=0)
    with pytest.raises(ValueError):
        fair_dol_futures(spot=-1.0, di_annual=0.10, cupom=0.02, business_days=63)
    with pytest.raises(ValueError):
        frc_forward_cupom(0.02, 126, 0.03, 63)
    with pytest.raises(ValueError):
        interpolate_cupom([], 42)
