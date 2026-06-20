from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

import app.services.forecast_service as forecast_service_module
from app.services.forecast_service import ForecastService, _MODEL_REGISTRY


@dataclass
class FakeEISScore:
    hotspot_id: int
    computed_for_date: datetime
    eis_score: float
    risk_category: str = "Medium"
    frequency_score: float = 0.5
    recurrence_score: float = 0.4
    density_score: float = 0.6
    temporal_risk_score: float = 0.7
    severity_norm: float = 0.5
    exposure_score: float = 0.55
    severity_multiplier: float = 1.1


@dataclass
class FakeForecast:
    id: int
    hotspot_id: int
    forecast_date: datetime
    horizon_days: int
    predicted_eis: float
    predicted_risk_category: str
    confidence_lower: float
    confidence_upper: float
    top_features: dict
    shap_values: dict
    model_version: str
    pipeline_run_id: str | None
    created_at: datetime


def make_scores(days: int = 12):
    base = datetime(2026, 1, 1)
    return [
        FakeEISScore(
            hotspot_id=1,
            computed_for_date=base + timedelta(days=i),
            eis_score=30 + i,
            risk_category="High" if i > 6 else "Medium",
        )
        for i in range(days)
    ]


def make_forecast():
    return FakeForecast(
        id=1,
        hotspot_id=1,
        forecast_date=datetime(2026, 1, 15),
        horizon_days=1,
        predicted_eis=78.0,
        predicted_risk_category="Critical",
        confidence_lower=70.0,
        confidence_upper=85.0,
        top_features={"factors": []},
        shap_values={"latest_eis": 0.5},
        model_version="forecast-v1-h1",
        pipeline_run_id=None,
        created_at=datetime(2026, 1, 10),
    )


@pytest.fixture(autouse=True)
def isolated_model_artifacts(tmp_path, monkeypatch):
    """Keep persistence tests isolated from application model artifacts."""
    monkeypatch.setattr(
        forecast_service_module,
        "_ARTIFACT_DIR",
        tmp_path / "artifacts",
    )
    _MODEL_REGISTRY.clear()
    yield
    _MODEL_REGISTRY.clear()


def test_train_model_success():
    _MODEL_REGISTRY.clear()

    db = MagicMock()
    service = ForecastService(db)

    with patch.object(service.repository, "get_historical_eis_scores", return_value=make_scores()):
        result = service.train_model(horizon_days=1, model_version="forecast-v1")

    assert result["status"] == "trained"
    assert result["horizon_days"] == 1
    assert result["rows_used"] > 0
    assert 1 in _MODEL_REGISTRY


def test_generate_forecasts_loads_persisted_model_after_restart():
    db = MagicMock()
    service = ForecastService(db)

    with patch.object(
        service.repository,
        "get_historical_eis_scores",
        return_value=make_scores(),
    ):
        service.train_model(horizon_days=1, model_version="forecast-v1")

    _MODEL_REGISTRY.clear()
    restarted_service = ForecastService(db)
    with patch.object(
        restarted_service.repository,
        "get_historical_eis_scores",
        return_value=make_scores(),
    ), patch.object(
        restarted_service.repository,
        "delete_existing_forecasts",
        return_value=0,
    ), patch.object(
        restarted_service.repository,
        "bulk_create_forecasts",
        return_value=[make_forecast()],
    ):
        result = restarted_service.generate_forecasts(horizon_days=1)

    assert result["status"] == "generated"
    assert result["forecasts_created"] == 1
    assert 1 in _MODEL_REGISTRY


def test_generate_forecasts_success():
    _MODEL_REGISTRY.clear()

    db = MagicMock()
    service = ForecastService(db)

    with patch.object(service.repository, "get_historical_eis_scores", return_value=make_scores()):
        service.train_model(horizon_days=1, model_version="forecast-v1")

    with patch.object(service.repository, "get_historical_eis_scores", return_value=make_scores()), \
        patch.object(service.repository, "delete_existing_forecasts", return_value=0), \
        patch.object(service.repository, "bulk_create_forecasts", return_value=[make_forecast()]):

        result = service.generate_forecasts(horizon_days=1, replace_existing=True)

    assert result["status"] == "generated"
    assert result["forecasts_created"] == 1
    db.commit.assert_called_once()


def test_list_forecasts_serializes_rows():
    db = MagicMock()
    service = ForecastService(db)

    with patch.object(service.repository, "list_forecasts", return_value=[make_forecast()]):
        rows = service.list_forecasts()

    assert len(rows) == 1
    assert rows[0]["forecast_id"] == 1
    assert rows[0]["predicted_risk_category"] == "Critical"
    assert 0.0 <= rows[0]["confidence"] <= 1.0


def test_get_top_forecasts_uses_high_and_critical_by_default():
    db = MagicMock()
    service = ForecastService(db)

    with patch.object(service.repository, "get_top_forecasts", return_value=[make_forecast()]) as mocked:
        rows = service.get_top_forecasts(limit=5)

    assert len(rows) == 1
    mocked.assert_called_once()
    assert mocked.call_args.kwargs["risk_categories"] == ["High", "Critical"]


def test_get_summary_adds_model_registry_info():
    _MODEL_REGISTRY.clear()
    _MODEL_REGISTRY[1] = object()

    db = MagicMock()
    service = ForecastService(db)

    with patch.object(service.repository, "get_summary", return_value={"total_forecasts": 10}):
        summary = service.get_summary()

    assert summary["total_forecasts"] == 10
    assert summary["models_in_memory"] == 1
    assert summary["trained_horizons"] == [1]
