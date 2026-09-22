"""CBOE VIX Volatility Index Replication Engine tailored for B3 BOVA11 Options."""

from __future__ import annotations

import math
from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class TermVariance:
    maturity_du: float
    time_to_maturity: float
    forward_price: float
    atm_strike: float
    variance: float


class VixBovaEngine:
    """Computes the 30-day model-free implied volatility index (VIXBOVA) using CBOE methodology."""

    @classmethod
    def compute_single_term_variance(
        cls,
        df_options: pd.DataFrame,
        time_to_exp: float,
        r: float,
        business_days: float = 21.0,
    ) -> TermVariance:
        """Compute variance for a single expiration term according to CBOE VIX formula.

        Expected DataFrame columns: 'strike', 'call_price', 'put_price'
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

        return TermVariance(
            maturity_du=business_days,
            time_to_maturity=time_to_exp,
            forward_price=forward,
            atm_strike=k0,
            variance=max(0.0, term_variance)
        )

    @classmethod
    def calculate_vixbova(
        cls,
        near_term: TermVariance,
        next_term: TermVariance,
        target_days: float = 30.0,
    ) -> float:
        """Interpolate near-term and next-term variances to target constant 30-day index."""
        t1 = near_term.time_to_maturity
        t2 = next_term.time_to_maturity
        v1 = near_term.variance
        v2 = next_term.variance

        n30 = target_days / 365.0
        if t1 == t2:
            return 100.0 * math.sqrt(v1)

        var_30 = (t1 * v1 * (t2 - n30) / (t2 - t1) + t2 * v2 * (n30 - t1) / (t2 - t1)) * (1.0 / n30)
        return float(100.0 * math.sqrt(max(0.0, var_30)))
