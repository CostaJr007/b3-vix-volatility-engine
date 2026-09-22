"""RTD & DDE Desk Feed Specification for Nelogica ProfitChart, Tryd, and Cedro Fast Trade."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Literal, Optional


@dataclass(frozen=True)
class RTDServerSpec:
    platform_name: str
    server_prog_id: str
    last_price_topic: str
    variation_topic: str
    settlement_topic: str
    time_topic: str
    formula_template: str


RTD_PLATFORMS: Dict[str, RTDServerSpec] = {
    "profitchart": RTDServerSpec(
        platform_name="Nelogica ProfitChart",
        server_prog_id="rtdtrading.rtdserver",
        last_price_topic="ULT",
        variation_topic="VAR",
        settlement_topic="AJU",
        time_topic="HOR",
        formula_template='=RTD("rtdtrading.rtdserver",, "{TICKER}", "{TOPIC}")'
    ),
    "tryd": RTDServerSpec(
        platform_name="Tryd Desktop",
        server_prog_id="tryd.rtdserver",
        last_price_topic="Ult",
        variation_topic="Var",
        settlement_topic="FechAj",
        time_topic="HORA",
        formula_template='=RTD("tryd.rtdserver",, "COT", "{TICKER}", "{TOPIC}")'
    ),
    "fasttrade": RTDServerSpec(
        platform_name="Cedro Fast Trade",
        server_prog_id="srv.rtd",
        last_price_topic="LAST",
        variation_topic="VAR",
        settlement_topic="AJU",
        time_topic="TIME",
        formula_template='=RTD("srv.rtd",, "SQT", "{TICKER}", "{TOPIC}")'
    ),
}


class RTDDeskBridge:
    """Manages RTD topic mapping and formula generation for live B3 trading desks."""

    @staticmethod
    def get_server_spec(platform: Literal["profitchart", "tryd", "fasttrade"]) -> RTDServerSpec:
        plat = platform.lower()
        if plat not in RTD_PLATFORMS:
            raise ValueError(f"Unknown platform '{platform}'. Supported: {list(RTD_PLATFORMS.keys())}")
        return RTD_PLATFORMS[plat]

    @classmethod
    def generate_excel_formula(
        cls,
        platform: Literal["profitchart", "tryd", "fasttrade"],
        ticker: str,
        field: Literal["last", "var", "settlement", "time"] = "last"
    ) -> str:
        spec = cls.get_server_spec(platform)
        topic_map = {
            "last": spec.last_price_topic,
            "var": spec.variation_topic,
            "settlement": spec.settlement_topic,
            "time": spec.time_topic,
        }
        topic = topic_map[field]
        if platform == "tryd":
            return f'=RTD("{spec.server_prog_id}",, "COT", "{ticker}", "{topic}")'
        elif platform == "fasttrade":
            return f'=RTD("{spec.server_prog_id}",, "SQT", "{ticker}", "{topic}")'
        else:
            return f'=RTD("{spec.server_prog_id}",, "{ticker}", "{topic}")'
