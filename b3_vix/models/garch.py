"""GARCH(1,1) Econometric Volatility Estimation and Forecasting Engine."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence, Union
import numpy as np
from scipy.optimize import minimize


@dataclass(frozen=True)
class GarchFitResult:
    omega: float
    alpha: float
    beta: float
    persistence: float
    unconditional_volatility: float
    log_likelihood: float
    current_volatility: float


class GarchVolatilityModel:
    """Estimates GARCH(1,1) parameters via Maximum Likelihood and projects future volatility."""

    @classmethod
    def fit(cls, returns: Union[Sequence[float], np.ndarray]) -> GarchFitResult:
        r = np.asarray(returns, dtype=float)
        r = r[np.isfinite(r)]
        n = len(r)
        if n < 30:
            raise ValueError(f"At least 30 observations required for GARCH(1,1) estimation, got {n}")

        sample_var = float(np.var(r, ddof=1))
        eps = r - np.mean(r)
        eps2 = eps ** 2

        def negative_log_likelihood(params: np.ndarray) -> float:
            omega, alpha, beta = params
            sigma2 = np.zeros(n)
            sigma2[0] = sample_var

            for t in range(1, n):
                sigma2[t] = omega + alpha * eps2[t - 1] + beta * sigma2[t - 1]
                if sigma2[t] <= 1e-9:
                    sigma2[t] = 1e-9

            ll = -0.5 * np.sum(np.log(2 * np.pi) + np.log(sigma2) + (eps2 / sigma2))
            return -float(ll)

        init_alpha = 0.08
        init_beta = 0.88
        init_omega = sample_var * (1.0 - init_alpha - init_beta)
        initial_params = np.array([init_omega, init_alpha, init_beta])

        bounds = [
            (1e-8, None),
            (1e-5, 0.5),
            (1e-5, 0.99),
        ]
        constraints = [
            {"type": "ineq", "fun": lambda p: 0.999 - (p[1] + p[2])}
        ]

        res = minimize(
            negative_log_likelihood,
            initial_params,
            bounds=bounds,
            constraints=constraints,
            method="SLSQP",
            options={"maxiter": 200, "ftol": 1e-7}
        )

        omega, alpha, beta = res.x
        persistence = alpha + beta
        uncond_var = omega / max(1e-6, (1.0 - persistence))
        uncond_vol = math.sqrt(uncond_var)

        sigma2_last = sample_var
        for t in range(1, n):
            sigma2_last = omega + alpha * eps2[t - 1] + beta * sigma2_last

        return GarchFitResult(
            omega=float(omega),
            alpha=float(alpha),
            beta=float(beta),
            persistence=float(persistence),
            unconditional_volatility=float(uncond_vol),
            log_likelihood=float(-res.fun),
            current_volatility=float(math.sqrt(sigma2_last))
        )

    @classmethod
    def forecast(cls, fit: GarchFitResult, horizon_days: int = 21) -> np.ndarray:
        uncond_var = fit.unconditional_volatility ** 2
        forecasts = np.zeros(horizon_days)
        last_var = fit.current_volatility ** 2

        for k in range(1, horizon_days + 1):
            var_k = uncond_var + (fit.persistence ** (k - 1)) * (last_var - uncond_var)
            forecasts[k - 1] = math.sqrt(max(0.0, var_k))

        return forecasts
