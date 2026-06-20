from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("TEST_DATABASE_URL") is None,
        reason="TEST_DATABASE_URL not set; skipping simulator integration tests",
    ),
]


@pytest.fixture(scope="module")
def engine():
    engine = create_engine(os.environ["TEST_DATABASE_URL"], pool_pre_ping=True)
    yield engine
    engine.dispose()


@pytest.fixture()
def db(engine):
    connection = engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(
        bind=connection,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


def create_hotspot(db):
    from geoalchemy2.shape import from_shape
    from shapely.geometry import Point

    from app.models.hotspot import Hotspot

    hotspot = Hotspot(
        cluster_label=1_000_000 + (uuid4().int % 1_000_000_000),
        hotspot_name="Simulator Integration Hotspot",
        zone_id="SIM-TEST",
        centroid=from_shape(Point(77.5946, 12.9716), srid=4326),
        centroid_lat=12.9716,
        centroid_lon=77.5946,
        radius_m=100.0,
        total_violations=100,
        unique_dates=20,
        dominant_violation_type="Illegal Parking",
        violation_density=250.0,
        pipeline_run_id="simulator-integration",
    )
    db.add(hotspot)
    db.flush()
    return hotspot


def create_eis_score(db, hotspot_id: int):
    from app.models.analytics import EISScore

    score = EISScore(
        hotspot_id=hotspot_id,
        computed_for_date=datetime.utcnow(),
        frequency_score=0.85,
        recurrence_score=0.70,
        density_score=0.80,
        temporal_risk_score=0.75,
        severity_norm=0.70,
        exposure_score=0.79,
        severity_multiplier=1.16,
        eis_score=82.0,
        risk_category="Critical",
        rank=1,
        pipeline_run_id="simulator-integration",
    )
    db.add(score)
    db.flush()
    return score


def create_forecast(db, hotspot_id: int):
    from app.models.analytics import Forecast

    forecast = Forecast(
        hotspot_id=hotspot_id,
        forecast_date=datetime.utcnow() + timedelta(days=1),
        horizon_days=1,
        predicted_eis=84.0,
        predicted_risk_category="Critical",
        confidence_lower=78.0,
        confidence_upper=89.0,
        model_version="simulator-integration",
        pipeline_run_id="simulator-integration",
    )
    db.add(forecast)
    db.flush()
    return forecast


def create_allocation(db, hotspot_id: int, eis_score_id: int):
    from app.models.analytics import Allocation

    allocation = Allocation(
        hotspot_id=hotspot_id,
        eis_score_id=eis_score_id,
        officers_allocated=3,
        allocation_fraction=1.0,
        priority_rank=1,
        deployment_window="08:00-10:00",
        total_officers_available=3,
        eis_snapshot=82.0,
        risk_category="Critical",
        allocation_date=datetime.utcnow(),
        pipeline_run_id="simulator-integration",
    )
    db.add(allocation)
    db.flush()
    return allocation


def test_simulator_service_runs_read_only_integration(db) -> None:
    from app.models.analytics import Allocation, EISScore, Forecast, PatrolRoute
    from app.services.simulator_service import SimulatorService

    hotspot = create_hotspot(db)
    eis = create_eis_score(db, hotspot.id)
    create_forecast(db, hotspot.id)
    create_allocation(db, hotspot.id, eis.id)

    counts_before = {
        "eis": db.query(EISScore).count(),
        "forecast": db.query(Forecast).count(),
        "allocation": db.query(Allocation).count(),
        "route": db.query(PatrolRoute).count(),
    }

    result = SimulatorService(db).run_simulation(
        scenario_name="Integration frequency reduction",
        overrides={
            "frequency_reduction_pct": 0.15,
            "forecast_horizon_days": 1,
            "target_hotspot_ids": [hotspot.id],
        },
    )

    assert result["total_hotspots"] == 1
    assert result["hotspot_results"][0]["baseline_eis"] == 82.0
    assert 0.0 <= result["hotspot_results"][0]["simulated_eis"] <= 100.0
    assert json.loads(json.dumps(result["hotspot_results"])) == result["hotspot_results"]

    counts_after = {
        "eis": db.query(EISScore).count(),
        "forecast": db.query(Forecast).count(),
        "allocation": db.query(Allocation).count(),
        "route": db.query(PatrolRoute).count(),
    }
    assert counts_after == counts_before
    assert not db.new
    assert not db.dirty
    assert not db.deleted
