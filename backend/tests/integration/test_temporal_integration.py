"""
tests/integration/test_temporal_integration.py
─────────────────────────────────────────────────
Integration tests for the Temporal Intelligence Engine.

Unlike the unit test suite (which uses an in-memory SQLite database), these
tests run against a real PostgreSQL/PostGIS instance, exercising the full
synchronous SQLAlchemy stack used in production:

    Violation → EnrichedViolation → TemporalService.run_pipeline()
        → TemporalRepository → PeakWindow (persisted)

Requirements covered
─────────────────────
1. Reads TEST_DATABASE_URL from the environment.
2. Automatically skips the entire module if TEST_DATABASE_URL is not set.
3. Uses PostgreSQL/PostGIS only — no SQLite fallback.
4. Verifies TemporalService.run_pipeline() populates peak_windows.
5. Verifies persisted peak_windows can be queried back (via repository
   read helpers and a direct query).
6. Verifies temporal risk scores fall within [0, 1].
7. Verifies the temporal risk output shape is suitable as downstream EIS
   input (a {hotspot_id: float} mapping with valid values for every
   analysed hotspot).
8. Follows the existing synchronous SQLAlchemy project style (plain
   Session, explicit commit/rollback, no async).
9. Uses existing models from the uploaded zip (Hotspot, Violation,
   EnrichedViolation, PeakWindow) rather than ad-hoc tables.

Run with:  pytest tests/integration/test_temporal_integration.py -v -m integration
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta
from typing import Generator, List

import pytest

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")

pytestmark = pytest.mark.integration

if not TEST_DATABASE_URL:
    pytest.skip(
        "TEST_DATABASE_URL is not set — skipping PostgreSQL/PostGIS "
        "integration tests for the Temporal Intelligence Engine.",
        allow_module_level=True,
    )

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.models.analytics import PeakWindow
from app.models.enriched_violation import EnrichedViolation
from app.models.hotspot import Hotspot
from app.models.violation import Violation
from app.repositories.temporal_repository import TemporalRepository
from app.services.temporal_service import TemporalService, TemporalRunResult

try:
    from geoalchemy2.elements import WKTElement
except ImportError:  # pragma: no cover - geoalchemy2 is a hard project dependency
    WKTElement = None


# ═══════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def engine():
    """
    Real PostgreSQL/PostGIS engine, built from TEST_DATABASE_URL.

    Ensures the PostGIS extension is available and (re)creates all tables
    for the duration of the test module.
    """
    eng = create_engine(TEST_DATABASE_URL, future=True)

    with eng.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.commit()

    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture
def db(engine) -> Generator[Session, None, None]:
    """
    Function-scoped synchronous SQLAlchemy session.

    Each test runs inside its own transaction; tables are truncated
    afterwards so tests remain independent and idempotent.
    """
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.query(PeakWindow).delete()
        session.query(EnrichedViolation).delete()
        session.query(Violation).delete()
        session.query(Hotspot).delete()
        session.commit()
        session.close()


@pytest.fixture
def service(db: Session) -> TemporalService:
    return TemporalService(db)


@pytest.fixture
def repo(db: Session) -> TemporalRepository:
    return TemporalRepository(db)


# ═══════════════════════════════════════════════════════════════════════════
# Helpers — seed realistic data via existing models
# ═══════════════════════════════════════════════════════════════════════════

def _make_hotspot(db: Session, *, cluster_label: int, lon: float = 80.6480, lat: float = 16.5062) -> Hotspot:
    """Persist a minimal but valid Hotspot row (PostGIS centroid required)."""
    centroid = WKTElement(f"POINT({lon} {lat})", srid=4326)
    hotspot = Hotspot(
        cluster_label=cluster_label,
        hotspot_name=f"Test Hotspot {cluster_label}",
        centroid=centroid,
        centroid_lat=lat,
        centroid_lon=lon,
        total_violations=0,
    )
    db.add(hotspot)
    db.flush()
    return hotspot


def _seed_violations_for_hotspot(
    db: Session,
    *,
    hotspot: Hotspot,
    n_violations: int,
    hour_utc: int,
    weekday: int,
    n_days: int = 6,
) -> None:
    """
    Insert n_violations Violation + EnrichedViolation rows, spread across
    n_days occurrences of the given UTC hour/weekday so the temporal
    pipeline's IST-converted aggregation has enough density to build a
    PeakWindow (min_window_violations default is 5).

    UTC hour is chosen so that hour_utc + 5:30 (IST offset) stays sane;
    the service converts UTC -> IST internally.
    """
    base_date = datetime(2026, 1, 5)  # a Monday, for deterministic weekday math
    target_date = base_date + timedelta(days=(weekday - base_date.weekday()) % 7)

    per_day = max(1, n_violations // n_days)
    created = 0
    day_offset = 0
    while created < n_violations:
        violation_date = target_date + timedelta(weeks=day_offset, hours=hour_utc)
        batch = min(per_day, n_violations - created)
        for i in range(batch):
            violation = Violation(
                violation_id=f"V-{hotspot.cluster_label}-{day_offset}-{i}-{uuid.uuid4().hex[:6]}",
                violation_type="No Parking Zone",
                violation_date=violation_date,
                hour_of_day=violation_date.hour,
                day_of_week=violation_date.weekday(),
                latitude=hotspot.centroid_lat,
                longitude=hotspot.centroid_lon,
                data_source="integration_test",
            )
            db.add(violation)
            db.flush()

            enriched = EnrichedViolation(
                violation_id=violation.id,
                hotspot_id=hotspot.id,
                severity_score=0.5,
                is_recurrence=False,
                temporal_flag=False,
            )
            db.add(enriched)
            created += 1
        day_offset += 1

    db.flush()


def _seed_min_pipeline_dataset(db: Session, hotspot: Hotspot) -> None:
    """
    Seed enough violations to clear TemporalService._MIN_VIOLATIONS_ABSOLUTE
    (30), concentrated in one clear peak window so a High/Critical
    PeakWindow is guaranteed to be built and persisted.
    """
    _seed_violations_for_hotspot(
        db,
        hotspot=hotspot,
        n_violations=40,
        hour_utc=3,       # 3:00 UTC -> 08:30 IST, a plausible morning-rush hour
        weekday=1,        # Tuesday
        n_days=8,
    )


# ═══════════════════════════════════════════════════════════════════════════
# Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestTemporalPipelinePopulatesPeakWindows:
    """Requirement: the TemporalService pipeline can populate peak_windows."""

    def test_run_pipeline_persists_peak_windows(self, db: Session, service: TemporalService) -> None:
        hotspot = _make_hotspot(db, cluster_label=1)
        _seed_min_pipeline_dataset(db, hotspot)
        db.commit()

        result = service.run_pipeline(truncate_existing=True)

        assert isinstance(result, TemporalRunResult)
        assert result.n_windows_written > 0
        assert result.n_violations_analysed >= 30
        assert result.n_hotspots_analysed >= 1

        db.commit()

        persisted_count = db.query(PeakWindow).count()
        assert persisted_count == result.n_windows_written
        assert persisted_count > 0

    def test_run_pipeline_raises_below_minimum_data_threshold(
        self, db: Session, service: TemporalService
    ) -> None:
        from app.core.exceptions import InsufficientDataForClusteringError

        hotspot = _make_hotspot(db, cluster_label=2)
        _seed_violations_for_hotspot(
            db, hotspot=hotspot, n_violations=5, hour_utc=3, weekday=1, n_days=1
        )
        db.commit()

        with pytest.raises(InsufficientDataForClusteringError):
            service.run_pipeline(truncate_existing=True)


class TestPersistedPeakWindowsAreQueryable:
    """Requirement: persisted peak_windows can be queried."""

    def test_peak_windows_queryable_via_repository(
        self, db: Session, service: TemporalService, repo: TemporalRepository
    ) -> None:
        hotspot = _make_hotspot(db, cluster_label=3)
        _seed_min_pipeline_dataset(db, hotspot)
        db.commit()

        service.run_pipeline(truncate_existing=True)
        db.commit()

        windows_for_hotspot = repo.list_for_hotspot(hotspot.id)
        assert len(windows_for_hotspot) > 0
        assert all(w.hotspot_id == hotspot.id for w in windows_for_hotspot)

        all_windows = repo.list_all(limit=500)
        assert len(all_windows) >= len(windows_for_hotspot)

        total = repo.count_total()
        assert total == len(all_windows) or total >= len(windows_for_hotspot)

    def test_peak_windows_queryable_via_service_read_api(
        self, db: Session, service: TemporalService
    ) -> None:
        hotspot = _make_hotspot(db, cluster_label=4)
        _seed_min_pipeline_dataset(db, hotspot)
        db.commit()

        service.run_pipeline(truncate_existing=True)
        db.commit()

        windows = service.get_peak_windows(hotspot_id=hotspot.id)
        assert len(windows) > 0
        for window in windows:
            assert window.id is not None
            assert window.violation_count > 0


class TestTemporalRiskScoresInValidRange:
    """Requirement: temporal risk scores are produced in range 0 to 1."""

    def test_hotspot_temporal_risk_score_in_unit_interval(
        self, db: Session, service: TemporalService
    ) -> None:
        hotspot = _make_hotspot(db, cluster_label=5)
        _seed_min_pipeline_dataset(db, hotspot)
        db.commit()

        service.run_pipeline(truncate_existing=True)
        db.commit()

        score = service.get_temporal_risk_score(hotspot.id)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_temporal_risk_score_zero_for_hotspot_with_no_windows(
        self, db: Session, service: TemporalService
    ) -> None:
        hotspot = _make_hotspot(db, cluster_label=6)
        db.commit()

        score = service.get_temporal_risk_score(hotspot.id)
        assert score == 0.0

    def test_all_temporal_risk_scores_in_unit_interval(
        self, db: Session, service: TemporalService
    ) -> None:
        hotspot_a = _make_hotspot(db, cluster_label=7, lon=80.64, lat=16.50)
        hotspot_b = _make_hotspot(db, cluster_label=8, lon=80.65, lat=16.51)
        _seed_min_pipeline_dataset(db, hotspot_a)
        _seed_min_pipeline_dataset(db, hotspot_b)
        db.commit()

        service.run_pipeline(truncate_existing=True)
        db.commit()

        scores = service.get_all_temporal_risk_scores()
        assert len(scores) >= 2
        for hotspot_id, score in scores.items():
            assert isinstance(hotspot_id, int)
            assert 0.0 <= score <= 1.0


class TestTemporalOutputSuitableForDownstreamEIS:
    """
    Requirement: temporal risk output is suitable for downstream EIS input.

    The EIS Engine's frozen formula consumes a per-hotspot temporal_risk
    component as a float in [0, 1]. These tests assert the shape and
    completeness of that contract rather than re-testing the EIS Engine
    itself (Forecast/EIS engines are explicitly out of scope here).
    """

    def test_risk_scores_cover_every_analysed_hotspot(
        self, db: Session, service: TemporalService
    ) -> None:
        hotspot_a = _make_hotspot(db, cluster_label=9, lon=80.64, lat=16.50)
        hotspot_b = _make_hotspot(db, cluster_label=10, lon=80.66, lat=16.52)
        _seed_min_pipeline_dataset(db, hotspot_a)
        _seed_min_pipeline_dataset(db, hotspot_b)
        db.commit()

        result = service.run_pipeline(truncate_existing=True)
        db.commit()

        scores = service.get_all_temporal_risk_scores()

        # Every hotspot the pipeline analysed must have a usable EIS input.
        assert hotspot_a.id in scores
        assert hotspot_b.id in scores
        assert len(scores) == result.n_hotspots_analysed

        for score in scores.values():
            assert isinstance(score, float)
            assert 0.0 <= score <= 1.0

    def test_single_hotspot_score_matches_batch_score(
        self, db: Session, service: TemporalService
    ) -> None:
        """
        EIS may call either the scalar per-hotspot accessor or the batch
        accessor depending on call site; both must agree so downstream
        consumers get a consistent temporal_risk_score regardless of path.
        """
        hotspot = _make_hotspot(db, cluster_label=11)
        _seed_min_pipeline_dataset(db, hotspot)
        db.commit()

        service.run_pipeline(truncate_existing=True)
        db.commit()

        scalar_score = service.get_temporal_risk_score(hotspot.id)
        batch_scores = service.get_all_temporal_risk_scores()

        assert hotspot.id in batch_scores
        assert scalar_score == pytest.approx(batch_scores[hotspot.id])