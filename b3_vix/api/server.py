"""FastAPI Server for B3 Volatility & VIXBOVA Analytics."""

from __future__ import annotations

from typing import Dict, List, Literal, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import pandas as pd

from ..models.black_scholes import B3BlackScholesEngine
from ..models.implied_vol import ImpliedVolatilitySolver
from ..models.vix_bova import VixBovaEngine, business_days_to_time_to_expiry
from ..models.garch import GarchVolatilityModel
from ..models.di_curve import DICurveInterpolator
from ..connectors.rtd_feed import RTDDeskBridge


app = FastAPI(
    title="B3 Volatility & VIXBOVA Analytics API",
    description="Institutional volatility modeling, VIXBOVA index replication, DI1 discounting & GARCH(1,1)",
    version="1.0.0"
)


class B3GreeksRequest(BaseModel):
    flag: Literal["call", "put"]
    spot: float = Field(..., gt=0)
    strike: float = Field(..., gt=0)
    business_days: int = Field(..., gt=0, description="Business days to expiration (DU)")
    annual_rate: float = Field(0.105, description="Annual compound DI rate (e.g. 0.105 for 10.5%)")
    volatility: float = Field(..., gt=0)
    dividend_yield: float = Field(0.0, ge=0)


class VixBovaRequest(BaseModel):
    spot: float = Field(..., gt=0)
    annual_rate: float = Field(0.105)
    # Public API keeps DU names (retrocompatible). Internally they are
    # converted to CBOE calendar year fractions (see calculate_vixbova).
    near_du: int = Field(15, gt=0, description="Near-term expiration in business days (DU); converted to calendar/365 internally")
    next_du: int = Field(35, gt=0, description="Next-term expiration in business days (DU); converted to calendar/365 internally")
    # Retrocompatible aliases: accept calendar-day inputs under alternative names.
    near_days: Optional[int] = Field(None, gt=0, description="Alias for near_du (business days)")
    next_days: Optional[int] = Field(None, gt=0, description="Alias for next_du (business days)")

    def resolved_near_du(self) -> int:
        return self.near_days if self.near_days is not None else self.near_du

    def resolved_next_du(self) -> int:
        return self.next_days if self.next_days is not None else self.next_du


class GarchRequest(BaseModel):
    returns: List[float] = Field(..., min_length=30)
    horizon_du: int = Field(21, ge=1, le=252)


class RTDFormulaRequest(BaseModel):
    platform: Literal["profitchart", "tryd", "fasttrade"]
    ticker: str
    field: Literal["last", "var", "settlement", "time"] = "last"


@app.get("/health")
def health():
    return {"status": "ok", "service": "b3-vix-volatility-engine", "market": "B3 / Brazil"}


@app.post("/api/v1/greeks")
def get_greeks(req: B3GreeksRequest):
    try:
        t_years = req.business_days / 252.0
        r_cont = DICurveInterpolator.from_dict({req.business_days: req.annual_rate}).continuous_rate(req.business_days)
        greeks = B3BlackScholesEngine.greeks(
            flag=req.flag,
            S=req.spot,
            K=req.strike,
            T=t_years,
            r=r_cont,
            sigma=req.volatility,
            q=req.dividend_yield,
            business_days_basis=True
        )
        return {
            "price": greeks.price,
            "delta": greeks.delta,
            "gamma": greeks.gamma,
            "vega": greeks.vega,
            "theta_daily_du": greeks.theta,
            "rho": greeks.rho
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/vixbova")
def calculate_vixbova(req: VixBovaRequest):
    try:
        from ..connectors.market_data import B3MarketData
        near_du = req.resolved_near_du()
        next_du = req.resolved_next_du()
        near_chain = B3MarketData.generate_bova11_chain(req.spot, du_to_expiry=near_du, risk_free_rate=req.annual_rate)
        next_chain = B3MarketData.generate_bova11_chain(req.spot, du_to_expiry=next_du, risk_free_rate=req.annual_rate)

        r_cont = DICurveInterpolator.from_dict({21: req.annual_rate}).continuous_rate(21)
        # CBOE calendar base: T = calendar_days/365, with
        # calendar_days ~= DU * 365/252 (approximation: weekends/holidays).
        # business_days_to_time_to_expiry() does the two-step conversion
        # explicitly (numerically == DU/252, but in calendar units so T1/T2
        # share the base with N30 = 30/365 in calculate_vixbova).
        v1 = VixBovaEngine.compute_single_term_variance(near_chain, time_to_exp=business_days_to_time_to_expiry(near_du), r=r_cont, business_days=near_du)
        v2 = VixBovaEngine.compute_single_term_variance(next_chain, time_to_exp=business_days_to_time_to_expiry(next_du), r=r_cont, business_days=next_du)

        vix_index = VixBovaEngine.calculate_vixbova(v1, v2)
        return {
            "underlying_spot": req.spot,
            "vixbova_index": vix_index,
            "near_term_variance": v1.variance,
            "next_term_variance": v2.variance,
            "near_du": near_du,
            "next_du": next_du
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/garch")
def fit_garch(req: GarchRequest):
    try:
        fit = GarchVolatilityModel.fit(req.returns)
        forecast = GarchVolatilityModel.forecast(fit, horizon_days=req.horizon_du)
        return {
            "omega": fit.omega,
            "alpha": fit.alpha,
            "beta": fit.beta,
            "persistence": fit.persistence,
            "unconditional_volatility": fit.unconditional_volatility,
            "forecast_volatility": forecast.tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/rtd-formula")
def get_rtd_formula(req: RTDFormulaRequest):
    formula = RTDDeskBridge.generate_excel_formula(req.platform, req.ticker, req.field)
    return {"platform": req.platform, "ticker": req.ticker, "field": req.field, "formula": formula}
