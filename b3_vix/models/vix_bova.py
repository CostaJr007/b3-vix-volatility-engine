"""CBOE VIX Volatility Index Replication Engine tailored for B3 BOVA11 Options.

Time convention (CBOE, unified):
    All VIX inputs use CALENDAR time in years: T = calendar_days / 365.
    The 30-day target is N30 = 30 / 365.
    When only business days (DU) are known, estimate
    calendar_days ~= DU * 365/252 and then T = calendar_days / 365
    (numerically equal to DU/252, but expressed in calendar units so that
    T1/T2 and N30 share the same base). B3 option *pricing* (Black-Scholes)
    and DI discounting still use DU/252 internally — only the VIX variance
    and interpolation use the calendar base.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
import numpy as np
import pandas as pd


# CBOE calendar convention constants (unified base for the VIX engine).
CALENDAR_DAYS_PER_YEAR: float = 365.0
BUSINESS_DAYS_PER_YEAR: float = 252.0
# Approximation: one DU ~= 365/252 calendar days (weekends/holidays).
DU_TO_CALENDAR_FACTOR: float = CALENDAR_DAYS_PER_YEAR / BUSINESS_DAYS_PER_YEAR


def business_days_to_calendar_days(business_days: float) -> float:
    """Estimate calendar days from business days (DU).

    Approximation: calendar_days ~= DU * 365/252.
    """
    return float(business_days) * DU_TO_CALENDAR_FACTOR


def calendar_days_to_time_to_expiry(calendar_days: float) -> float:
    """Convert calendar days to CBOE year fraction: T = calendar_days / 365."""
    return float(calendar_days) / CALENDAR_DAYS_PER_YEAR


def business_days_to_time_to_expiry(business_days: float) -> float:
    """Convert DU to CBOE year fraction via explicit calendar step.

    calendar_days ~= DU * 365/252, then T = calendar_days / 365.
    NOTE: numerically identical to DU/252, but written in two steps so the
    calendar (CBOE) base shared with N30 = 30/365 is explicit.
    """
    calendar_days = business_days_to_calendar_days(business_days)
    return calendar_days_to_time_to_expiry(calendar_days)


@dataclass(frozen=True)
class TermVariance:
    maturity_du: float
    time_to_maturity: float  # CBOE calendar year fraction (calendar_days / 365)
    forward_price: float
    atm_strike: float
    variance: float
    maturity_calendar_days: float = 0.0  # informative estimate (DU * 365/252)


class VixBovaEngine:
    """Computes the 30-day model-free implied volatility index (VIXBOVA) using CBOE methodology."""

    @classmethod
    def compute_single_term_variance(
        cls,
        df_options: pd.DataFrame,
        time_to_exp: float,
        r: float,
        business_days: float = 21.0,
        calendar_days: float | None = None,
    ) -> TermVariance:
        """Compute variance for a single expiration term according to CBOE VIX formula.

        Expected DataFrame columns: 'strike', 'call_price', 'put_price'

        Time convention (CBOE calendar base):
            ``time_to_exp`` MUST be a calendar year fraction
            ``T = calendar_days / 365`` (NOT ``DU/252`` directly).
            If you only know business days (DU), convert explicitly::

                calendar_days ~= DU * 365/252
                T = calendar_days / 365   # == DU/252 numerically

            Use :func:`business_days_to_time_to_expiry` for that conversion.
            ``business_days`` (DU) is kept only as informative metadata;
            ``calendar_days`` optionally records the calendar estimate.
        """
        if time_to_exp <= 0:
            raise ValueError("Time to expiration must be positive.")

        # 1. Determine Forward Price F = Strike + exp(r*T) * (Call - Put) for strike with min |Call - Put|
        df = df_options.copy()
        df["call_put_diff"] = np.abs(df["call_price"] - df["put_price"])
        min_row = df.loc[df["call_put_diff"].idxmin()]

        atm_k = float(min_row["strike"])
        forward = atm_k + math.exp(r * time_to_exp) * (float(min_row["call_price"]) - float(min_row["put_price"]))

        # 2. Select K0: First strike immediately below or equal to forward price
        strikes = sorted(df["strike"].unique())
        strikes_below = [k for k in strikes if k <= forward]
        k0 = max(strikes_below) if strikes_below else strikes[0]

        # 3. Select out-of-the-money options: Puts below K0, Calls above K0, average at K0
        df = df.sort_values("strike").reset_index(drop=True)
        q_prices = []
        valid_strikes = []

        for _, row in df.iterrows():
            k = float(row["strike"])
            cp, pp = float(row["call_price"]), float(row["put_price"])
            if k < k0:
                price = pp
            elif k > k0:
                price = cp
            else:
                price = (cp + pp) / 2.0

            if price > 0:
                q_prices.append(price)
                valid_strikes.append(k)

        if len(valid_strikes) < 3:
            raise ValueError("Insufficient active out-of-the-money options to calculate variance.")

        # 4. Compute Delta K intervals
        delta_k = []
        n = len(valid_strikes)
        for i in range(n):
            if i == 0:
                dk = valid_strikes[1] - valid_strikes[0]
            elif i == n - 1:
                dk = valid_strikes[-1] - valid_strikes[-2]
            else:
                dk = (valid_strikes[i + 1] - valid_strikes[i - 1]) / 2.0
            delta_k.append(dk)

        # 5. Sum: (Delta_K / K^2) * exp(R*T) * Q(K)
        exp_rt = math.exp(r * time_to_exp)
        weighted_sum = sum(
            (dk / (k ** 2)) * exp_rt * q
            for dk, k, q in zip(delta_k, valid_strikes, q_prices)
        )

        term_variance = (2.0 / time_to_exp) * weighted_sum - (1.0 / time_to_exp) * ((forward / k0 - 1.0) ** 2)

        cal_days = float(calendar_days) if calendar_days is not None else business_days_to_calendar_days(business_days)
        return TermVariance(
            maturity_du=business_days,
            time_to_maturity=time_to_exp,
            forward_price=forward,
            atm_strike=k0,
            variance=max(0.0, term_variance),
            maturity_calendar_days=cal_days,
        )

    @classmethod
    def calculate_vixbova(
        cls,
        near_term: TermVariance,
        next_term: TermVariance,
        target_days: float = 30.0,
    ) -> float:
        """Interpolate near-term and next-term variances to target constant 30-day index.

        CBOE calendar convention: T1, T2 and N30 share the same base —
        T1 = cal_days_1/365, T2 = cal_days_2/365, N30 = target_days/365
        (default target_days=30 -> N30 = 30/365). Do NOT pass DU/252 here;
        convert DU via ``business_days_to_time_to_expiry`` first.
        """
        t1 = near_term.time_to_maturity
        t2 = next_term.time_to_maturity
        v1 = near_term.variance
        v2 = next_term.variance

        n30 = target_days / 365.0
        if t1 == t2:
            return 100.0 * math.sqrt(v1)

        var_30 = (t1 * v1 * (t2 - n30) / (t2 - t1) + t2 * v2 * (n30 - t1) / (t2 - t1)) * (1.0 / n30)
        return float(100.0 * math.sqrt(max(0.0, var_30)))
