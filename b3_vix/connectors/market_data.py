"""B3 Options Chain and Historical Data Connectors."""

from __future__ import annotations

import math
from typing import Dict, List
import pandas as pd
from ..models.black_scholes import B3BlackScholesEngine


class B3MarketData:
    """Generates synthetic BOVA11 option chains and pulls market series."""

    @staticmethod
    def generate_bova11_chain(
        spot: float = 112.50,
        strikes_count: int = 15,
        du_to_expiry: int = 21,
        atm_vol: float = 0.28,
        risk_free_rate: float = 0.105,
    ) -> pd.DataFrame:
        """Create realistic BOVA11 option chain with DU-252 time discounting."""
        t_years = du_to_expiry / 252.0
        step = 1.0  # BOVA11 strikes are spaced 1.0 BRL apart
        center_strike = round(spot)
        strikes = [center_strike + (i - strikes_count // 2) * step for i in range(strikes_count)]

        records: List[Dict[str, float]] = []
        for K in strikes:
            moneyness = (K - spot) / spot
            # Volatility skew in equity index: OTM Puts trade at higher IV than OTM Calls
            iv = max(0.12, atm_vol - 0.25 * moneyness + 0.6 * (moneyness ** 2))

            call_p = B3BlackScholesEngine.price("call", spot, K, t_years, risk_free_rate, iv)
            put_p = B3BlackScholesEngine.price("put", spot, K, t_years, risk_free_rate, iv)

            records.append({
                "strike": float(K),
                "time_to_maturity": float(t_years),
                "business_days": float(du_to_expiry),
                "implied_vol": float(iv),
                "call_price": float(call_p),
                "put_price": float(put_p),
            })

        return pd.DataFrame(records)
