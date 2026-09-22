"""B3 Volatility Engine & VIXBOVA Suite.

Quantitative volatility modeling, CBOE VIX replication for BOVA11 options,
DI1 yield curve discounting, GARCH(1,1) estimation, and RTD desk bridge.
"""

__version__ = "1.0.0"
__author__ = "Costa Junior (CostaJr007)"

from .models.black_scholes import B3BlackScholesEngine, OptionGreeks
from .models.implied_vol import ImpliedVolatilitySolver
from .models.vix_bova import VixBovaEngine, TermVariance
from .models.garch import GarchVolatilityModel
from .models.di_curve import DICurveInterpolator

__all__ = [
    "B3BlackScholesEngine",
    "OptionGreeks",
    "ImpliedVolatilitySolver",
    "VixBovaEngine",
    "TermVariance",
    "GarchVolatilityModel",
    "DICurveInterpolator",
]
