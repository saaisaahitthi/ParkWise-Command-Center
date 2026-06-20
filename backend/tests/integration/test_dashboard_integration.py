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
        reason="TEST_DATABASE_URL not set; skipping dashboard integration tests",
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
        hotspot_name="Dashboard Integration Hotspot",
        zone_id="DASHBOARD-TEST",
        centroid=from_shape(Point(77.5946, 12.9716), srid=4326),
        centroid_lat=12.9716,
        centroid_lon=77.5946,
        radius_m=120.0,
        total_violations=150,
        unique_dates=25,
        dominant_violation_type="No Parking",
        violation_density=300.0,
        pipeline_run_id="dashboard-integration",
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
        recurrence_score=0.75,
        density_score=0.80,
        temporal_risk_score=0.90,
        severity_norm=0.70,
        exposure_score=0.82,
        severity_multiplier=1.16,
        eis_score=86.0,
        risk_category="Critical",
        rank=1,
        pipeline_run_id="dashboard-integration",
    )
    db.add(score)
    db.flush()
    return score


def create_peak_window(db, hotspot_id: int):
    from app.models.analytics import PeakWindow

    window = PeakWindow(
        hotspot_id=hotspot_id,
        day_of_week=0,
        hour_of_day=9,
        window_label="Morning Rush",
        violation_count=35,
        avg_violations=7.0,
        pct_of_total=23.3,
        recommended_start_hour=8,
        recommended_end_hour=10,
        enforcement_priority="Critical",
        pipeline_run_id="dashboard-integration",
    )
    db.add(window)
    db.flush()
    return window


def create_forecast(db, hotspot_id: int):
    from app.models.analytics import Forecast

    forecast = Forecast(
        hotspot_id=hotspot_id,
        forecast_date=datetime.utcnow() + timedelta(days=1),
        horizon_days=1,
        predicted_eis=88.0,
        predicted_risk_category="Critical",
        confidence_lower=82.0,
        confidence_upper=93.0,
        model_version="dashboard-integration",
        pipeline_run_id="dashboard-integration",
    )
    db.add(forecast)
    db.flush()
    return forecast


def create_allocation(db, hotspot_id: int, eis_score_id: int):
    from app.models.analytics import Allocation

    allocation = Allocation(
        hotspot_id=hotspot_id,
        eis_score_id=eis_score_id,
        officers_allocated=4,
        allocation_fraction=1.0,
        priority_rank=1,
        deployment_window="08:00-10:00",
        total_officers_available=4,
        eis_snapshot=86.0,
        risk_category="Critical",
        allocation_date=datetime.utcnow(),
        pipeline_run_id="dashboard-integration",
    )
    db.add(allocation)
    db.flush()
    return allocation


def create_route(db, hotspot_id: int):
    from app.models.analytics import PatrolRoute

    route = PatrolRoute(
        hotspot_id=hotspot_id,
        route_name="Dashboard Morning Route",
        shift_label="Morning",
        officer_count=4,
        stops_json=[
            {
                "sequence": 1,
                "hotspot_id": hotspot_id,
                "hotspot_name": "Dashboard Integration Hotspot",
            }
        ],
        total_distance_km=8.5,
        estimated_duration_min=35,
        hotspots_covered=1,
        total_eis_covered=86.0,
        pipeline_run_id="dashboard-integration",
    )
    db.add(route)
    db.flush()
    return route


def test_dashboard_payload_integration(db) -> None:
    from app.services.dashboard_service import DashboardService

    hotspot = create_hotspot(db)
    eis = create_eis_score(db, hotspot.id)
    create_peak_window(db, hotspot.id)
    create_forecast(db, hotspot.id)
    create_allocation(db, hotspot.id, eis.id)
    create_route(db, hotspot.id)

    result = DashboardService(db).get_dashboard_payload()

    expected_sections = {
        "executive_summary",
        "risk_distribution",
        "hotspot_map",
        "temporal_overview",
        "forecast_overview",
        "allocation_overview",
        "routing_overview",
    }
    assert set(result) == expected_sections
    assert result["executive_summary"]["total_hotspots"] >= 1
    assert result["risk_distribution"]["Critical"] >= 1
    assert any(
        row["hotspot_id"] == hotspot.id for row in result["hotspot_map"]
    )
    assert result["temporal_overview"]["peak_windows_count"] >= 1
    assert result["forecast_overview"]["total_forecasts"] >= 1
    assert result["allocation_overview"]["total_officers"] >= 4
    assert result["routing_overview"]["total_routes"] >= 1
    assert json.loads(json.dumps(result)) == result
