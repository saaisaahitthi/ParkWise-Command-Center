from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.deps import db_session
from app.api.v1.endpoints.forecast import router


def make_app():
    app = FastAPI()
    app.include_router(router, prefix="/forecast")

    def override_db():
        yield MagicMock()

    app.dependency_overrides[db_session] = override_db
    return app


def test_train_forecast_endpoint(monkeypatch):
    app = make_app()
    client = TestClient(app)

    class FakeService:
        def __init__(self, db):
            pass

        def train_model(self, **kwargs):
            return {
                "status": "trained",
                "horizon_days": kwargs["horizon_days"],
                "model_version": "forecast-v1-h1",
                "rows_used": 20,
            }

    monkeypatch.setattr("app.api.v1.endpoints.forecast.ForecastService", FakeService)

    response = client.post(
        "/forecast/train",
        json={"horizon_days": 1, "model_version": "forecast-v1"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "trained"


def test_generate_forecast_endpoint(monkeypatch):
    app = make_app()
    client = TestClient(app)

    class FakeService:
        def __init__(self, db):
            pass

        def generate_forecasts(self, **kwargs):
            return {
                "status": "generated",
                "horizon_days": kwargs["horizon_days"],
                "forecasts_created": 3,
            }

    monkeypatch.setattr("app.api.v1.endpoints.forecast.ForecastService", FakeService)

    response = client.post(
        "/forecast/generate",
        json={"horizon_days": 1, "replace_existing": True},
    )

    assert response.status_code == 200
    assert response.json()["forecasts_created"] == 3


def test_list_forecasts_endpoint(monkeypatch):
    app = make_app()
    client = TestClient(app)

    class FakeService:
        def __init__(self, db):
            pass

        def list_forecasts(self, **kwargs):
            return [
                {
                    "forecast_id": 1,
                    "hotspot_id": 10,
                    "forecast_date": "2026-01-10T00:00:00",
                    "horizon_days": 1,
                    "predicted_eis": 82.5,
                    "predicted_risk_category": "Critical",
                    "confidence": 0.85,
                }
            ]

    monkeypatch.setattr("app.api.v1.endpoints.forecast.ForecastService", FakeService)

    response = client.get("/forecast?limit=10")

    assert response.status_code == 200
    assert response.json()[0]["predicted_risk_category"] == "Critical"


def test_top_forecasts_endpoint(monkeypatch):
    app = make_app()
    client = TestClient(app)

    class FakeService:
        def __init__(self, db):
            pass

        def get_top_forecasts(self, **kwargs):
            return [{"forecast_id": 1, "predicted_eis": 90.0}]

    monkeypatch.setattr("app.api.v1.endpoints.forecast.ForecastService", FakeService)

    response = client.get("/forecast/top?limit=5")

    assert response.status_code == 200
    assert response.json()[0]["predicted_eis"] == 90.0


def test_hotspot_forecasts_endpoint(monkeypatch):
    app = make_app()
    client = TestClient(app)

    class FakeService:
        def __init__(self, db):
            pass

        def get_hotspot_forecasts(self, hotspot_id, **kwargs):
            return [{"forecast_id": 1, "hotspot_id": hotspot_id}]

    monkeypatch.setattr("app.api.v1.endpoints.forecast.ForecastService", FakeService)

    response = client.get("/forecast/hotspots/12")

    assert response.status_code == 200
    assert response.json()[0]["hotspot_id"] == 12


def test_summary_endpoint(monkeypatch):
    app = make_app()
    client = TestClient(app)

    class FakeService:
        def __init__(self, db):
            pass

        def get_summary(self):
            return {
                "total_forecasts": 5,
                "risk_distribution": {"Critical": 2},
                "trained_horizons": [1],
            }

    monkeypatch.setattr("app.api.v1.endpoints.forecast.ForecastService", FakeService)

    response = client.get("/forecast/summary")

    assert response.status_code == 200
    assert response.json()["total_forecasts"] == 5
