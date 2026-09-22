"""Unit tests for B3 API."""

from fastapi.testclient import TestClient
from b3_vix.api.server import app

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["service"] == "b3-vix-volatility-engine"


def test_greeks_endpoint():
    payload = {
        "flag": "call",
        "spot": 112.50,
        "strike": 110.00,
        "business_days": 21,
        "annual_rate": 0.105,
        "volatility": 0.28,
        "dividend_yield": 0.0
    }
    res = client.post("/api/v1/greeks", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "price" in data
    assert 0 < data["delta"] < 1


def test_vixbova_endpoint():
    payload = {
        "spot": 112.50,
        "annual_rate": 0.105,
        "near_du": 15,
        "next_du": 35
    }
    res = client.post("/api/v1/vixbova", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "vixbova_index" in data
    assert data["vixbova_index"] > 0
