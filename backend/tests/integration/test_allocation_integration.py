from __future__ import annotations

import os
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

pytestmark = pytest.mark.skipif(
    os.getenv("TEST_DATABASE_URL") is None,
    reason="TEST_DATABASE_URL not set; skipping allocation integration tests",
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
        cluster_label=880001,
        hotspot_type="allocation_test_cluster",
        centroid=from_shape(Point(78.4867, 17.3850), srid=4326),
        centroid_lat=17.3850,
        centroid_lng=78.4867,
        radius_meters=100.0,
        violation_count=100,
        density_per_sq_km=250.0,
        confidence_score=0.9,
        is_active=True,
    )

    if hasattr(hotspot, "hotspot_name"):
        hotspot.hotspot_name = "Allocation Test Hotspot"

    db.add(hotspot)
    db.flush()
    return hotspot


def create_eis_score(db, hotspot_id):
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
        eis_score=85.0,
        risk_category="Critical",
        rank=1,
        pipeline_run_id="allocation-test",
    )

    db.add(score)
    db.flush()
    return score


def test_allocation_can_be_created_from_eis(db):
    from app.models.analytics import Allocation

    hotspot = create_hotspot(db)
    eis = create_eis_score(db, hotspot.id)

    allocation = Allocation(
        hotspot_id=hotspot.id,
        eis_score_id=eis.id,
        officers_allocated=5,
        allocation_fraction=1.0,
        priority_rank=1,
        deployment_window=None,
        total_officers_available=5,
        eis_snapshot=eis.eis_score,
        risk_category=eis.risk_category,
    )

    db.add(allocation)
    db.flush()

    saved = (
        db.query(Allocation)
        .filter(Allocation.hotspot_id == hotspot.id)
        .first()
    )

    assert saved is not None
    assert saved.officers_allocated == 5
    assert saved.risk_category == "Critical"
    assert saved.eis_snapshot == 85.0


def test_allocation_latest_query_shape(db):
    from app.models.analytics import Allocation

    hotspot = create_hotspot(db)
    eis = create_eis_score(db, hotspot.id)

    allocation = Allocation(
        hotspot_id=hotspot.id,
        eis_score_id=eis.id,
        officers_allocated=4,
        allocation_fraction=1.0,
        priority_rank=1,
        deployment_window=None,
        total_officers_available=4,
        eis_snapshot=eis.eis_score,
        risk_category=eis.risk_category,
    )

    db.add(allocation)
    db.flush()

    latest = (
        db.query(Allocation)
        .order_by(Allocation.allocation_date.desc())
        .first()
    )

    assert latest is not None
    assert latest.total_officers_available == 4