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


def test_train_forecast_openapi_defaults():
    app = make_app()
    schema = app.openapi()
    request_schema = schema["components"]["schemas"]["ForecastTrainRequest"]
    request_example = schema["paths"]["/forecast/train"]["post"]["requestBody"][
        "content"
    ]["application/json"]["examples"]["default"]["value"]

    assert request_example == {
        "horizon_days": 1,
        "model_version": "forecast-v1-h1",
        "min_history_per_hotspot": 1,
    }
    assert request_schema["properties"]["horizon_days"]["default"] == 1
    assert "null" in {
        option.get("type")
        for option in request_schema["properties"]["hotspot_id"]["anyOf"]
    }
    assert request_schema["properties"]["model_version"]["default"] == "forecast-v1-h1"
    assert request_schema["properties"]["min_history_per_hotspot"]["default"] == 1


def test_application_openapi_includes_null_hotspot_default():
    from app.main import app as application

    request_example = application.openapi()["paths"]["/api/v1/forecast/train"][
        "post"
    ]["requestBody"]["content"]["application/json"]["examples"]["default"]["value"]

    assert request_example == {
        "horizon_days": 1,
        "hotspot_id": None,
        "model_version": "forecast-v1-h1",
        "min_history_per_hotspot": 1,
    }


def test_train_forecast_endpoint_accepts_zero_as_all_hotspots(monkeypatch):
    app = make_app()
    client = TestClient(app)
    captured = {}

    class FakeService:
        def __init__(self, db):
            pass

        def train_model(self, **kwargs):
            captured.update(kwargs)
            return {
                "status": "trained",
                "model_version": kwargs["model_version"],
                "rows_used": 5872,
                "train_size": 4404,
                "validation_size": 1468,
                "r2": 0.87,
                "mae": 3.30,
                "feature_names": ["frequency_score"],
            }

    monkeypatch.setattr("app.api.v1.endpoints.forecast.ForecastService", FakeService)

    response = client.post(
        "/forecast/train",
        json={
            "horizon_days": 1,
            "hotspot_id": 0,
            "model_version": "forecast-v1-h1",
            "min_history_per_hotspot": 1,
        },
    )

    assert response.status_code == 200
    assert captured["hotspot_id"] is None
    assert response.json()["rows_used"] == 5872


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


def test_generate_forecast_openapi_defaults():
    from app.main import app as application

    openapi = application.openapi()
    request_schema = openapi["components"]["schemas"]["ForecastGenerateRequest"]
    request_example = openapi["paths"]["/api/v1/forecast/generate"]["post"][
        "requestBody"
    ]["content"]["application/json"]["examples"]["default"]["value"]

    assert request_example == {
        "horizon_days": 1,
        "hotspot_id": None,
        "replace_existing": True,
        "pipeline_run_id": "forecast-v1-h1",
    }
    assert request_schema["properties"]["horizon_days"]["default"] == 1
    assert "null" in {
        option.get("type")
        for option in request_schema["properties"]["hotspot_id"]["anyOf"]
    }
    assert request_schema["properties"]["replace_existing"]["default"] is True
    assert (
        request_schema["properties"]["pipeline_run_id"]["default"]
        == "forecast-v1-h1"
    )


def test_generate_forecast_endpoint_normalizes_zero_hotspot(monkeypatch):
    app = make_app()
    client = TestClient(app)
    captured = {}

    class FakeService:
        def __init__(self, db):
            pass

        def generate_forecasts(self, **kwargs):
            captured.update(kwargs)
            return {"status": "generated", "forecasts_created": 5872}

    monkeypatch.setattr("app.api.v1.endpoints.forecast.ForecastService", FakeService)

    response = client.post(
        "/forecast/generate",
        json={
            "horizon_days": 1,
            "hotspot_id": 0,
            "replace_existing": True,
            "pipeline_run_id": "forecast-v1-h1",
        },
    )

    assert response.status_code == 200
    assert captured["hotspot_id"] is None
    assert response.json()["forecasts_created"] == 5872


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
