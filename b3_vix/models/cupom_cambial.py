"""Onshore Dollar Coupon (Cupom Cambial) and FRC Forward Curve.

Covered interest parity for B3 USD/BRL futures (DOL/WDO), discrete DU-252 basis:

    F = S * (1 + DI)^(DU/252) / (1 + cc)^(DU/252)

so the implied onshore dollar coupon is::

    cc = ((S / F) * (1 + DI)^(DU/252))^(252/DU) - 1

Conventions:
- Cupom *limpo* uses same-day spot; cupom *sujo* uses lagged PTAX (D-1).
  Both are the same formula — they differ only in the spot input.
- FRC (FRA de cupom) is the forward coupon between two expiries::

    (1 + cc2)^T2 = (1 + cc1)^T1 * (1 + fwd)^(T2 - T1),  T = DU/252
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class CupomQuote:
    business_days: int
    cupom: float  # Annualized onshore dollar coupon (e.g. 0.02 for 2.00% a.a.)


def implied_cupom(spot: float, futures: float, di_annual: float, business_days: int) -> float:
    """Implied onshore dollar coupon from covered interest parity.

    Args:
        spot: USD/BRL spot (same-day for limpo, lagged PTAX for sujo).
        futures: DOL/WDO futures price for the expiry.
        di_annual: DI annual compound rate (decimal).
        business_days: DU to expiry (must be > 0).
    """
    if spot <= 0 or futures <= 0:
        raise ValueError("spot and futures must be positive.")
    if business_days <= 0:
        raise ValueError("business_days must be positive.")
    if di_annual <= -1.0:
        raise ValueError("di_annual must exceed -1.")
    t = business_days / 252.0
    return ((spot / futures) * (1.0 + di_annual) ** t) ** (1.0 / t) - 1.0


def fair_dol_futures(spot: float, di_annual: float, cupom: float, business_days: int) -> float:
    """Fair DOL/WDO futures price from spot, DI and cupom (parity inverse)."""
    if spot <= 0:
        raise ValueError("spot must be positive.")
    if business_days <= 0:
        raise ValueError("business_days must be positive.")
    t = business_days / 252.0
    return spot * (1.0 + di_annual) ** t / (1.0 + cupom) ** t


def frc_forward_cupom(cc_near: float, du_near: int, cc_far: float, du_far: int) -> float:
    """Forward cupom (FRC) between two expiries.

    Args:
        cc_near: Implied cupom at the near expiry (annualized, decimal).
        du_near: DU to the near expiry.
        cc_far: Implied cupom at the far expiry.
        du_far: DU to the far expiry (must exceed du_near).
    """
    if du_far <= du_near:
        raise ValueError("du_far must exceed du_near.")
    if du_near < 0:
        raise ValueError("du_near must be non-negative.")
    t1 = du_near / 252.0
    t2 = du_far / 252.0
    accumulation = (1.0 + cc_far) ** t2 / (1.0 + cc_near) ** t1
    return accumulation ** (1.0 / (t2 - t1)) - 1.0


def interpolate_cupom(quotes: list[CupomQuote], business_days: int) -> float:
    """Linear interpolation of the cupom term structure (flat outside the grid)."""
    if not quotes:
        raise ValueError("At least one cupom quote is required.")
    qs = sorted(quotes, key=lambda q: q.business_days)
    if business_days <= qs[0].business_days:
        return qs[0].cupom
    if business_days >= qs[-1].business_days:
        return qs[-1].cupom
    for q1, q2 in zip(qs, qs[1:]):
        if q1.business_days <= business_days <= q2.business_days:
            w = (business_days - q1.business_days) / (q2.business_days - q1.business_days)
            return q1.cupom + w * (q2.cupom - q1.cupom)
    return qs[-1].cupom


def cupom_continuous(cupom: float) -> float:
    """Annualized cupom in continuous compounding: ln(1 + cc)."""
    return math.log(1.0 + cupom)
