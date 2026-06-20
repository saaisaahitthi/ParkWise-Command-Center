from __future__ import annotations

import os
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

pytestmark = pytest.mark.skipif(
    os.getenv("TEST_DATABASE_URL") is None,
    reason="TEST_DATABASE_URL not set; skipping forecast integration tests",
)


@pytest.fixture(scope="module")
def engine():
    url = os.environ["TEST_DATABASE_URL"]
    engine = create_engine(url, pool_pre_ping=True)
    yield engine
    engine.dispose()


@pytest.fixture()
def db(engine):
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = SessionLocal()
    try:
        yield session
        session.rollback()
    finally:
        session.close()


def create_hotspot(db):
    from geoalchemy2.shape import from_shape
    from shapely.geometry import Point

    from app.models.hotspot import Hotspot

    hotspot = Hotspot(
        cluster_label=990001,
        hotspot_type="test_forecast_cluster",
        centroid=from_shape(Point(78.4867, 17.3850), srid=4326),
        centroid_lat=17.3850,
        centroid_lng=78.4867,
        radius_meters=100.0,
        violation_count=50,
        density_per_sq_km=200.0,
        confidence_score=0.9,
        is_active=True,
    )

    db.add(hotspot)
    db.flush()
    return hotspot


def seed_eis_scores(db, hotspot_id: int, days: int = 14):
    from app.models.analytics import EISScore

    base = datetime(2026, 1, 1)

    rows = []
    for i in range(days):
        score = EISScore(
            hotspot_id=hotspot_id,
            computed_for_date=base + timedelta(days=i),
            frequency_score=0.4 + (i * 0.01),
            recurrence_score=0.3 + (i * 0.01),
            density_score=0.5 + (i * 0.01),
            temporal_risk_score=0.6,
            severity_norm=0.5,
            exposure_score=0.55,
            severity_multiplier=1.1,
            eis_score=45 + i,
            risk_category="High" if i >= 8 else "Medium",
            rank=i + 1,
            pipeline_run_id="test-forecast",
        )
        db.add(score)
        rows.append(score)

    db.flush()
    return rows


def test_forecast_training_and_generation_integration(db):
    from app.services.forecast_service import ForecastService, _MODEL_REGISTRY
    from app.models.analytics import Forecast

    _MODEL_REGISTRY.clear()

    hotspot = create_hotspot(db)
    seed_eis_scores(db, hotspot.id, days=16)

    service = ForecastService(db)

    train_result = service.train_model(
        horizon_days=1,
        hotspot_id=hotspot.id,
        model_version="forecast-test",
        min_history_per_hotspot=4,
    )

    assert train_result["status"] == "trained"
    assert train_result["rows_used"] > 0

    generate_result = service.generate_forecasts(
        horizon_days=1,
        hotspot_id=hotspot.id,
        replace_existing=True,
        pipeline_run_id="test-run",
        commit=False,
    )

    assert generate_result["status"] == "generated"
    assert generate_result["forecasts_created"] >= 1

    persisted = (
        db.query(Forecast)
        .filter(Forecast.hotspot_id == hotspot.id)
        .filter(Forecast.horizon_days == 1)
        .all()
    )

    assert len(persisted) >= 1
    assert persisted[0].predicted_risk_category in {"Low", "Medium", "High", "Critical"}
    assert persisted[0].top_features is not None
    assert persisted[0].shap_values is not None


def test_forecast_query_methods_integration(db):
    from app.services.forecast_service import ForecastService, _MODEL_REGISTRY

    _MODEL_REGISTRY.clear()

    hotspot = create_hotspot(db)
    seed_eis_scores(db, hotspot.id, days=16)

    service = ForecastService(db)

    service.train_model(
        horizon_days=7,
        hotspot_id=hotspot.id,
        model_version="forecast-test",
        min_history_per_hotspot=4,
    )

    service.generate_forecasts(
        horizon_days=7,
        hotspot_id=hotspot.id,
        replace_existing=True,
        pipeline_run_id="test-run",
        commit=False,
    )

    listed = service.list_forecasts(hotspot_id=hotspot.id, horizon_days=7)
    top = service.get_top_forecasts(horizon_days=7)
    hotspot_rows = service.get_hotspot_forecasts(hotspot_id=hotspot.id, horizon_days=7)
    summary = service.get_summary()

    assert len(listed) >= 1
    assert len(top) >= 1
    assert len(hotspot_rows) >= 1
    assert summary["total_forecasts"] >= 1