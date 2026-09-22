"""Brazilian DI1 Futures Curve Interpolation and Zero-Rate Discounting."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np


@dataclass(frozen=True)
class DIVertex:
    business_days: int
    annual_rate: float  # Annual compound rate (e.g. 0.105 for 10.50% a.a.)


class DICurveInterpolator:
    """Interpolates Brazilian DI1 futures rates (DU-252 convention) to continuous discount rates."""

    def __init__(self, vertices: List[DIVertex]):
        if not vertices:
            raise ValueError("At least one DI vertex is required.")
        self.vertices = sorted(vertices, key=lambda x: x.business_days)

    @classmethod
    def from_dict(cls, rates_by_du: Dict[int, float]) -> DICurveInterpolator:
        """Construct curve from dictionary mapping business days (DU) to annualized rates."""
        vertices = [DIVertex(business_days=du, annual_rate=rate) for du, rate in rates_by_du.items()]
        return cls(vertices)

    def zero_rate(self, business_days: int) -> float:
        """Compute annualized compound DI rate for given business days via linear interpolation."""
        if business_days <= self.vertices[0].business_days:
            return self.vertices[0].annual_rate
        if business_days >= self.vertices[-1].business_days:
            return self.vertices[-1].annual_rate

        for i in range(len(self.vertices) - 1):
            v1 = self.vertices[i]
            v2 = self.vertices[i + 1]
            if v1.business_days <= business_days <= v2.business_days:
                weight = (business_days - v1.business_days) / (v2.business_days - v1.business_days)
                return v1.annual_rate + weight * (v2.annual_rate - v1.annual_rate)

        return self.vertices[-1].annual_rate

    def continuous_rate(self, business_days: int) -> float:
        """Convert DU-252 annual compound rate into continuous compounding rate r_cont = ln(1 + R)."""
        r_annual = self.zero_rate(business_days)
        return math.log(1.0 + r_annual)

    def discount_factor(self, business_days: int) -> float:
        """Compute B3 discount factor: DF = (1 + R)^(-DU/252)."""
        r_annual = self.zero_rate(business_days)
        t_du = business_days / 252.0
        return (1.0 + r_annual) ** (-t_du)
