"""
tests/unit/test_temporal_service.py
─────────────────────────────────────
Unit tests for app/services/temporal_service.py — TemporalService class.

Strategy
────────
- SQLite in-memory DB (same pattern as test_temporal_repository.py).
- _load_violation_records is patched to inject synthetic _ViolationRecord
  stubs without needing a real Violation/EnrichedViolation join.
- We verify pipeline outputs: TemporalRunResult fields, PeakWindow rows
  written to the DB, and edge-case behaviour.

Run with:  pytest tests/unit/test_temporal_service.py -v
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.models.analytics import PeakWindow
from app.services.temporal_service import (
    TemporalRunResult,
    TemporalService,
    _ViolationRecord,
)
from tests.sqlite_helpers import (
    create_temporal_test_tables,
    drop_temporal_test_tables,
)


# ═══════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="function")
def db():
    """In-memory SQLite session — fresh per test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine, "connect")
    def _fk_pragma(dbapi_conn, _record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=OFF")
        cursor.close()

    create_temporal_test_tables(engine)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        drop_temporal_test_tables(engine)


@pytest.fixture(autouse=True)
def allow_synthetic_temporal_data(monkeypatch):
    """Bypass the production minimum-row guard only for synthetic unit data."""
    monkeypatch.setattr("app.services.temporal_service._MIN_VIOLATIONS_ABSOLUTE", 0)


def _make_records(hotspot_id: int, hour: int, day: int, count: int) -> List[_ViolationRecord]:
    base = datetime(2024, 1, 15, hour, 0, 0)
    return [
        _ViolationRecord(
            hotspot_id=hotspot_id,
            hour_of_day=hour,
            day_of_week=day,
            violation_date=base + timedelta(days=i),
        )
        for i in range(count)
    ]


def _synthetic_records(hotspot_id: int = 1) -> List[_ViolationRecord]:
    """60 violations at peak + 20 at off-peak for contrast."""
    return (
        _make_records(hotspot_id, hour=8, day=0, count=60)
        + _make_records(hotspot_id, hour=14, day=2, count=20)
    )


# ═══════════════════════════════════════════════════════════════════════════
# TemporalRunResult dataclass
# ═══════════════════════════════════════════════════════════════════════════

class TestTemporalRunResult:
    def test_duration_seconds_positive(self):
        r = TemporalRunResult(
            pipeline_run_id="run-1",
            n_violations_analysed=100,
            n_hotspots_analysed=5,
            n_windows_written=20,
            n_windows_deleted=0,
            started_at=datetime(2024, 1, 1, 10, 0, 0),
            completed_at=datetime(2024, 1, 1, 10, 0, 5),
        )
        assert r.duration_seconds == pytest.approx(5.0)

    def test_to_dict_keys(self):
        r = TemporalRunResult(
            pipeline_run_id="abc",
            n_violations_analysed=50,
            n_hotspots_analysed=3,
            n_windows_written=10,
            n_windows_deleted=5,
            started_at=datetime(2024, 1, 1, 9, 0, 0),
            completed_at=datetime(2024, 1, 1, 9, 0, 2),
        )
        assert set(r.to_dict().keys()) == {
            "pipeline_run_id", "n_violations_analysed", "n_hotspots_analysed",
            "n_windows_written", "n_windows_deleted", "duration_seconds",
            "started_at", "completed_at",
        }

    def test_to_dict_values(self):
        r = TemporalRunResult(
            pipeline_run_id="xyz",
            n_violations_analysed=200,
            n_hotspots_analysed=8,
            n_windows_written=40,
            n_windows_deleted=15,
            started_at=datetime(2024, 3, 1, 12, 0, 0),
            completed_at=datetime(2024, 3, 1, 12, 0, 3),
        )
        d = r.to_dict()
        assert d["pipeline_run_id"] == "xyz"
        assert d["n_violations_analysed"] == 200
        assert d["duration_seconds"] == pytest.approx(3.0)


# ═══════════════════════════════════════════════════════════════════════════
# TemporalService.run_pipeline
# ═══════════════════════════════════════════════════════════════════════════

class TestRunPipeline:
    TARGET = "app.services.temporal_service.TemporalService._load_records"

    @patch(TARGET)
    def test_returns_temporal_run_result(self, mock_load, db):
        mock_load.return_value = _synthetic_records()
        result = TemporalService(db).run_pipeline(truncate_existing=True, min_window_violations=5)
        assert isinstance(result, TemporalRunResult)
        assert result.pipeline_run_id

    @patch(TARGET)
    def test_writes_peak_windows(self, mock_load, db):
        mock_load.return_value = _synthetic_records()
        result = TemporalService(db).run_pipeline(truncate_existing=True, min_window_violations=5)
        windows = db.query(PeakWindow).all()
        assert result.n_windows_written == len(windows)
        assert len(windows) >= 1

    @patch(TARGET)
    def test_truncate_replaces_existing_windows(self, mock_load, db):
        mock_load.return_value = _synthetic_records()
        svc = TemporalService(db)
        svc.run_pipeline(truncate_existing=True, min_window_violations=5)

        mock_load.return_value = _synthetic_records()
        r2 = svc.run_pipeline(truncate_existing=True, min_window_violations=5)
        assert db.query(PeakWindow).count() == r2.n_windows_written

    @patch(TARGET)
    def test_high_min_violations_writes_zero(self, mock_load, db):
        mock_load.return_value = _synthetic_records()
        result = TemporalService(db).run_pipeline(truncate_existing=True, min_window_violations=9999)
        assert result.n_windows_written == 0

    @patch(TARGET)
    def test_pipeline_run_ids_are_unique(self, mock_load, db):
        mock_load.return_value = _synthetic_records()
        svc = TemporalService(db)
        r1 = svc.run_pipeline(truncate_existing=True, min_window_violations=5)
        mock_load.return_value = _synthetic_records()
        r2 = svc.run_pipeline(truncate_existing=True, min_window_violations=5)
        assert r1.pipeline_run_id != r2.pipeline_run_id

    @patch(TARGET)
    def test_empty_data_raises_or_zero(self, mock_load, db):
        """Empty input → InsufficientDataForClusteringError OR zero windows."""
        mock_load.return_value = []
        from app.core.exceptions import PipelineError

        with pytest.raises(PipelineError):
            TemporalService(db).run_pipeline(
                truncate_existing=True,
                min_window_violations=5,
            )


# ═══════════════════════════════════════════════════════════════════════════
# TemporalService.get_temporal_risk_score
# ═══════════════════════════════════════════════════════════════════════════

class TestGetTemporalRiskScore:
    def test_returns_zero_when_no_windows(self, db):
        assert TemporalService(db).get_temporal_risk_score(hotspot_id=999) == pytest.approx(0.0)

    def test_returns_float_in_range(self, db):
        db.add(PeakWindow(
            hotspot_id=None,
            violation_count=10,
            enforcement_priority="High",
            pipeline_run_id="test-run",
        ))
        db.flush()
        score = TemporalService(db).get_temporal_risk_score(hotspot_id=999)
        assert 0.0 <= score <= 1.0


# ═══════════════════════════════════════════════════════════════════════════
# TemporalService.get_heatmap_data / get_peak_windows / get_enforcement_schedule
# ═══════════════════════════════════════════════════════════════════════════

class TestHelperMethods:
    def test_get_heatmap_data_returns_list(self, db):
        assert isinstance(TemporalService(db).get_heatmap_data(), list)

    def test_get_peak_windows_returns_list(self, db):
        assert isinstance(TemporalService(db).get_peak_windows(), list)

    def test_get_enforcement_schedule_returns_list(self, db):
        assert isinstance(TemporalService(db).get_enforcement_schedule(top_n=5), list)

    def test_get_all_temporal_risk_scores_returns_dict(self, db):
        assert isinstance(TemporalService(db).get_all_temporal_risk_scores(), dict)
