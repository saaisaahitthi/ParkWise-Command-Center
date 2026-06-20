"""
tests/integration/test_routing_integration.py
──────────────────────────────────────────────
Integration tests for routing module with real database.

Tests the full workflow: create hotspots, allocations, generate routes, and verify persistence.
Automatically skipped if TEST_DATABASE_URL is not set.
"""

from __future__ import annotations

import os
from datetime import date, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

pytestmark = pytest.mark.skipif(
    os.getenv("TEST_DATABASE_URL") is None,
    reason="TEST_DATABASE_URL not set; skipping routing integration tests",
)


@pytest.fixture(scope="module")
def engine():
    """Create a test database engine."""
    url = os.environ["TEST_DATABASE_URL"]
    engine = create_engine(url, pool_pre_ping=True)
    yield engine
    engine.dispose()


@pytest.fixture()
def db(engine):
    """Create a test database session."""
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = SessionLocal()
    try:
        yield session
        session.rollback()
    finally:
        session.close()


def create_test_hotspot(db, hotspot_id: int, lat: float, lon: float):
    """Create a test hotspot."""
    from app.models.hotspot import Hotspot
    from geoalchemy2.shape import from_shape
    from shapely.geometry import Point

    hotspot = Hotspot(
        cluster_label=8000 + hotspot_id,
        hotspot_name=f"Test Hotspot {hotspot_id}",
        centroid=from_shape(Point(lon, lat), srid=4326),
        centroid_lat=lat,
        centroid_lon=lon,
        radius_m=100.0,
        total_violations=50,
        unique_dates=10,
        dominant_violation_type="Parking",
        avg_fine_amount=500.0,
        violation_density=100.0,
        pipeline_run_id="routing-test",
    )

    db.add(hotspot)
    db.flush()
    return hotspot


def create_test_eis_score(db, hotspot_id: int, eis_score: float = 80.0):
    """Create a test EIS score."""
    from app.models.analytics import EISScore

    score = EISScore(
        hotspot_id=hotspot_id,
        computed_for_date=datetime.utcnow(),
        frequency_score=0.8,
        recurrence_score=0.7,
        density_score=0.9,
        temporal_risk_score=0.8,
        severity_norm=0.7,
        exposure_score=0.75,
        severity_multiplier=1.2,
        eis_score=eis_score,
        risk_category="High" if eis_score < 85.0 else "Critical",
        rank=1,
        pipeline_run_id="routing-test",
    )

    db.add(score)
    db.flush()
    return score


def create_test_allocation(
    db, hotspot_id: int, officers: int = 2, priority: int = 1, risk: str = "High"
):
    """Create a test allocation."""
    from app.models.analytics import Allocation

    allocation = Allocation(
        hotspot_id=hotspot_id,
        officers_allocated=officers,
        allocation_fraction=1.0,
        priority_rank=priority,
        deployment_window=None,
        total_officers_available=officers,
        eis_snapshot=80.0,
        risk_category=risk,
        allocation_date=datetime.utcnow(),
        pipeline_run_id="routing-test",
    )

    db.add(allocation)
    db.flush()
    return allocation


def test_routing_service_generates_route_from_allocations(db):
    """Test that RoutingService generates a route from allocations."""
    from app.services.routing_service import RoutingService

    # Create test data
    hotspot1 = create_test_hotspot(db, 1, lat=12.9716, lon=77.5946)
    hotspot2 = create_test_hotspot(db, 2, lat=12.9700, lon=77.5950)

    create_test_eis_score(db, hotspot1.id, eis_score=85.0)
    create_test_eis_score(db, hotspot2.id, eis_score=75.0)

    create_test_allocation(db, hotspot1.id, officers=3, priority=1, risk="Critical")
    create_test_allocation(db, hotspot2.id, officers=2, priority=2, risk="High")

    db.commit()

    # Generate route
    service = RoutingService(db)
    result = service.generate_route(
        route_date=date.today(),
        shift_name="default",
        commit=True,
    )

    assert "route_id" in result
    assert result["route_id"] is not None
    assert result["total_stops"] == 2
    assert result["total_officers"] == 5
    assert "route_geometry" in result
    assert len(result["route_geometry"]) > 0
    assert "stops" in result
    assert len(result["stops"]) == 2


def test_routing_persists_to_patrol_route_table(db):
    """Test that generated route is persisted to PatrolRoute table."""
    from app.models.analytics import PatrolRoute
    from app.services.routing_service import RoutingService

    # Create test data
    hotspot = create_test_hotspot(db, 101, lat=12.9716, lon=77.5946)
    create_test_eis_score(db, hotspot.id)
    create_test_allocation(db, hotspot.id, officers=2, priority=1)

    db.commit()

    # Generate route
    service = RoutingService(db)
    result = service.generate_route(
        route_date=date.today(),
        shift_name="integration_test",
        commit=True,
    )

    route_id = result["route_id"]

    # Verify route was persisted
    saved_route = db.query(PatrolRoute).filter(PatrolRoute.id == route_id).first()

    assert saved_route is not None
    assert saved_route.shift_label == "integration_test"
    assert saved_route.hotspots_covered == 1
    assert saved_route.total_distance_km is not None


def test_route_geometry_is_json_compatible(db):
    """Test that route geometry is stored in JSON-compatible format."""
    from app.services.routing_service import RoutingService

    # Create test data
    hotspot1 = create_test_hotspot(db, 201, lat=12.9716, lon=77.5946)
    hotspot2 = create_test_hotspot(db, 202, lat=12.9700, lon=77.5950)

    create_test_eis_score(db, hotspot1.id)
    create_test_eis_score(db, hotspot2.id)

    create_test_allocation(db, hotspot1.id, officers=2, priority=1)
    create_test_allocation(db, hotspot2.id, officers=2, priority=2)

    db.commit()

    # Generate route
    service = RoutingService(db)
    result = service.generate_route(
        route_date=date.today(),
        shift_name="default",
        commit=True,
    )

    # Verify geometry format
    geometry = result["route_geometry"]
    assert isinstance(geometry, list)
    assert len(geometry) > 0
    for point in geometry:
        assert isinstance(point, dict)
        assert "lat" in point
        assert "lng" in point
        assert isinstance(point["lat"], (int, float))
        assert isinstance(point["lng"], (int, float))


def test_stops_json_is_json_compatible(db):
    """Test that stops_json is stored in JSON-compatible format."""
    from app.services.routing_service import RoutingService

    # Create test data
    hotspot = create_test_hotspot(db, 301, lat=12.9716, lon=77.5946)
    create_test_eis_score(db, hotspot.id, eis_score=90.0)
    create_test_allocation(db, hotspot.id, officers=3, priority=1, risk="Critical")

    db.commit()

    # Generate route
    service = RoutingService(db)
    result = service.generate_route(
        route_date=date.today(),
        shift_name="default",
        commit=True,
    )

    # Verify stops format
    stops = result["stops"]
    assert isinstance(stops, list)
    assert len(stops) == 1

    stop = stops[0]
    assert stop["hotspot_id"] == hotspot.id
    assert stop["latitude"] == hotspot.centroid_lat
    assert stop["longitude"] == hotspot.centroid_lon
    assert stop["officers_allocated"] == 3
    assert stop["risk_category"] == "Critical"


def test_route_with_start_point(db):
    """Test route generation with explicit start point."""
    from app.services.routing_service import RoutingService

    # Create test data
    hotspot = create_test_hotspot(db, 401, lat=12.9716, lon=77.5946)
    create_test_eis_score(db, hotspot.id)
    create_test_allocation(db, hotspot.id, officers=2)

    db.commit()

    # Generate route with start point
    service = RoutingService(db)
    result = service.generate_route(
        route_date=date.today(),
        shift_name="default",
        start_latitude=12.9680,
        start_longitude=77.5920,
        commit=True,
    )

    # Verify start point is first in geometry
    geometry = result["route_geometry"]
    assert len(geometry) >= 1
    assert geometry[0]["lat"] == 12.9680
    assert geometry[0]["lng"] == 77.5920


def test_route_distance_calculated(db):
    """Test that route distance is calculated correctly."""
    from app.services.routing_service import RoutingService

    # Create test data
    hotspot = create_test_hotspot(db, 501, lat=12.9716, lon=77.5946)
    create_test_eis_score(db, hotspot.id)
    create_test_allocation(db, hotspot.id, officers=2)

    db.commit()

    # Generate route
    service = RoutingService(db)
    result = service.generate_route(
        route_date=date.today(),
        shift_name="default",
        commit=True,
    )

    # Verify distance is calculated
    assert result["total_distance_km"] >= 0
    assert isinstance(result["total_distance_km"], (int, float))


def test_list_routes_returns_persisted_routes(db):
    """Test that list_routes returns generated routes."""
    from app.services.routing_service import RoutingService

    # Create test data
    hotspot = create_test_hotspot(db, 601, lat=12.9716, lon=77.5946)
    create_test_eis_score(db, hotspot.id)
    create_test_allocation(db, hotspot.id, officers=2)

    db.commit()

    # Generate route
    service = RoutingService(db)
    result = service.generate_route(
        route_date=date.today(),
        shift_name="default",
        commit=True,
    )

    # List routes
    routes = service.list_routes(limit=100)

    assert len(routes) > 0
    route_ids = [r["route_id"] for r in routes]
    assert result["route_id"] in route_ids


def test_get_latest_route_returns_newest(db):
    """Test that get_latest_route returns the most recent route."""
    from app.services.routing_service import RoutingService

    # Create test data
    hotspot = create_test_hotspot(db, 701, lat=12.9716, lon=77.5946)
    create_test_eis_score(db, hotspot.id)
    create_test_allocation(db, hotspot.id, officers=2)

    db.commit()

    # Generate route
    service = RoutingService(db)
    result = service.generate_route(
        route_date=date.today(),
        shift_name="default",
        commit=True,
    )

    # Get latest
    latest = service.get_latest_route()

    assert latest is not None
    assert latest["route_id"] == result["route_id"]


def test_get_route_by_id_retrieves_route(db):
    """Test that get_route_by_id retrieves the correct route."""
    from app.services.routing_service import RoutingService

    # Create test data
    hotspot = create_test_hotspot(db, 801, lat=12.9716, lon=77.5946)
    create_test_eis_score(db, hotspot.id)
    create_test_allocation(db, hotspot.id, officers=2)

    db.commit()

    # Generate route
    service = RoutingService(db)
    result = service.generate_route(
        route_date=date.today(),
        shift_name="default",
        commit=True,
    )

    route_id = result["route_id"]

    # Get by ID
    retrieved = service.get_route_by_id(route_id)

    assert retrieved is not None
    assert retrieved["route_id"] == route_id


def test_get_summary_returns_statistics(db):
    """Test that get_summary returns aggregate statistics."""
    from app.services.routing_service import RoutingService

    # Create test data
    hotspot = create_test_hotspot(db, 901, lat=12.9716, lon=77.5946)
    create_test_eis_score(db, hotspot.id)
    create_test_allocation(db, hotspot.id, officers=2)

    db.commit()

    # Generate route
    service = RoutingService(db)
    service.generate_route(
        route_date=date.today(),
        shift_name="default",
        commit=True,
    )

    # Get summary
    summary = service.get_summary()

    assert summary is not None
    assert "total_routes" in summary
    assert "average_distance_km" in summary
    assert "average_duration_min" in summary
    assert "average_stops_per_route" in summary
    assert summary["total_routes"] >= 1
