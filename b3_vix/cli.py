"""CLI for B3 Volatility Engine & VIXBOVA Suite."""

from __future__ import annotations

import argparse
import uvicorn
from .models.black_scholes import B3BlackScholesEngine
from .models.vix_bova import VixBovaEngine, business_days_to_time_to_expiry
from .models.di_curve import DICurveInterpolator
from .connectors.market_data import B3MarketData
from .connectors.rtd_feed import RTDDeskBridge


def main():
    parser = argparse.ArgumentParser(
        prog="b3-vix",
        description="B3 Volatility Engine & VIXBOVA Analytics CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: greeks
    p_greeks = subparsers.add_parser("greeks", help="Compute Black-Scholes Greeks under B3 DU-252 convention")
    p_greeks.add_argument("--flag", choices=["call", "put"], default="call")
    p_greeks.add_argument("--spot", type=float, required=True, help="Underlying spot price (e.g. BOVA11: 112.50)")
    p_greeks.add_argument("--strike", type=float, required=True, help="Option strike price")
    p_greeks.add_argument("--du", type=int, default=21, help="Business days to expiration (DU)")
    p_greeks.add_argument("--rate", type=float, default=0.105, help="Annual compound DI rate (e.g. 0.105)")
    p_greeks.add_argument("--vol", type=float, required=True, help="Annualized volatility (e.g. 0.28)")

    # Subcommand: vixbova (inputs stay in DU for retrocompat; converted to calendar/365 internally)
    p_vix = subparsers.add_parser("vixbova", help="Compute VIXBOVA index across near-term and next-term options")
    p_vix.add_argument("--spot", type=float, default=112.50, help="BOVA11 spot price")
    p_vix.add_argument("--near-du", dest="near_du", type=int, default=15, help="Near-term expiration in business days (DU; converted to calendar/365 internally)")
    p_vix.add_argument("--next-du", dest="next_du", type=int, default=35, help="Next-term expiration in business days (DU; converted to calendar/365 internally)")
    # Retrocompatible aliases: --near-days / --next-days map to the same DU inputs.
    p_vix.add_argument("--near-days", dest="near_days", type=int, default=None, help="Alias for --near-du (business days)")
    p_vix.add_argument("--next-days", dest="next_days", type=int, default=None, help="Alias for --next-du (business days)")
    p_vix.add_argument("--rate", type=float, default=0.105, help="DI rate")

    # Subcommand: rtd
    p_rtd = subparsers.add_parser("rtd", help="Generate RTD formula for desktop trading platforms")
    p_rtd.add_argument("--platform", choices=["profitchart", "tryd", "fasttrade"], required=True)
    p_rtd.add_argument("--ticker", type=str, required=True, help="Ticker (e.g. BOVA11, WDOM22, DI1F25)")

    # Subcommand: serve
    p_serve = subparsers.add_parser("serve", help="Launch FastAPI REST server")
    p_serve.add_argument("--host", type=str, default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8001)

    args = parser.parse_args()

    if args.command == "greeks":
        t_years = args.du / 252.0
        r_cont = DICurveInterpolator.from_dict({args.du: args.rate}).continuous_rate(args.du)
        res = B3BlackScholesEngine.greeks(args.flag, args.spot, args.strike, t_years, r_cont, args.vol, business_days_basis=True)
        print("=" * 55)
        print(f"B3 OPTIONS GREEKS ({args.flag.upper()}) - DU-252 BASIS")
        print("=" * 55)
        print(f"Spot:                R$ {args.spot:.2f}")
        print(f"Strike:              R$ {args.strike:.2f}")
        print(f"Business Days (DU):  {args.du} DU (T={t_years:.4f})")
        print(f"DI Rate:             {args.rate*100:.2f}% a.a. (Continuous: {r_cont*100:.2f}%)")
        print(f"Theoretical Price:   R$ {res.price:.4f}")
        print(f"Delta:               {res.delta:+.4f}")
        print(f"Gamma:               {res.gamma:.6f}")
        print(f"Vega (1% vol move):  R$ {res.vega:.4f}")
        print(f"Theta (per DU day):  R$ {res.theta:.4f}")
        print("=" * 55)

    elif args.command == "vixbova":
        # Resolve retrocompatible aliases (--near-days overrides --near-du if given).
        near_du = args.near_days if getattr(args, "near_days", None) is not None else args.near_du
        next_du = args.next_days if getattr(args, "next_days", None) is not None else args.next_du
        near_chain = B3MarketData.generate_bova11_chain(args.spot, du_to_expiry=near_du, risk_free_rate=args.rate)
        next_chain = B3MarketData.generate_bova11_chain(args.spot, du_to_expiry=next_du, risk_free_rate=args.rate)
        r_cont = DICurveInterpolator.from_dict({21: args.rate}).continuous_rate(21)

        # CBOE calendar base: T = calendar_days/365, with
        # calendar_days ~= DU * 365/252 (approximation: weekends/holidays).
        # The helper does the two-step conversion explicitly (numerically ==
        # DU/252, but in calendar units so T1/T2 share the base with
        # N30 = 30/365 in calculate_vixbova).
        v1 = VixBovaEngine.compute_single_term_variance(near_chain, time_to_exp=business_days_to_time_to_expiry(near_du), r=r_cont, business_days=near_du)
        v2 = VixBovaEngine.compute_single_term_variance(next_chain, time_to_exp=business_days_to_time_to_expiry(next_du), r=r_cont, business_days=next_du)
        vix = VixBovaEngine.calculate_vixbova(v1, v2)

        print("=" * 55)
        print("VIXBOVA (IBOVESPA 30-DAY VOLATILITY INDEX)")
        print("=" * 55)
        print(f"BOVA11 Spot:         R$ {args.spot:.2f}")
        print(f"Near-Term Variance:  {v1.variance:.6f} ({near_du} DU)")
        print(f"Next-Term Variance:  {v2.variance:.6f} ({next_du} DU)")
        print(f"30-Day VIXBOVA:      {vix:.2f} pts")
        print("=" * 55)

    elif args.command == "rtd":
        formula = RTDDeskBridge.generate_excel_formula(args.platform, args.ticker)
        print(f"Platform: {args.platform}")
        print(f"Formula:  {formula}")

    elif args.command == "serve":
        print(f"Starting B3 Volatility API at http://{args.host}:{args.port}")
        uvicorn.run("b3_vix.api.server:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
