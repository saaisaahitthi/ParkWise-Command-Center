"""
tests/unit/test_temporal_repository.py
────────────────────────────────────────
Unit tests for app/repositories/temporal_repository.py.

Strategy
────────
All tests use an in-memory SQLite database via SQLAlchemy so they run
without a real PostgreSQL instance.  PeakWindow rows are created directly
— no service layer is involved.

Run with:  pytest tests/unit/test_temporal_repository.py -v
"""

from __future__ import annotations

from datetime import datetime
from typing import List

import pytest
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from app.models.analytics import PeakWindow
from app.repositories.temporal_repository import TemporalRepository
from tests.sqlite_helpers import (
    create_temporal_test_tables,
    drop_temporal_test_tables,
)


# ═══════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="function")
def db() -> Session:
    """
    In-memory SQLite session.  Tables are created fresh for each test and
    dropped after.  SQLite does not enforce FK constraints by default;
    enable them so the tests remain realistic.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    # Only PeakWindow is needed here; referenced PostGIS tables are omitted.
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


@pytest.fixture
def repo(db: Session) -> TemporalRepository:
    return TemporalRepository(db)


def _make_window(
    *,
    hotspot_id: int = 1,
    day_of_week: int = 0,
    hour_of_day: int = 8,
    violation_count: int = 20,
    enforcement_priority: str = "High",
    pipeline_run_id: str = "run-001",
) -> PeakWindow:
    """Factory helper — creates an *unsaved* PeakWindow ORM object."""
    return PeakWindow(
        hotspot_id=hotspot_id,
        day_of_week=day_of_week,
        hour_of_day=hour_of_day,
        window_label="Morning Rush",
        violation_count=violation_count,
        avg_violations=5.0,
        pct_of_total=round(violation_count / 200 * 100, 4),
        recommended_start_hour=max(0, hour_of_day - 1),
        recommended_end_hour=min(23, hour_of_day + 1),
        enforcement_priority=enforcement_priority,
        pipeline_run_id=pipeline_run_id,
        created_at=datetime.utcnow(),
    )


# ═══════════════════════════════════════════════════════════════════════════
# bulk_insert_peak_windows
# ═══════════════════════════════════════════════════════════════════════════

class TestBulkInsertPeakWindows:

    def test_inserts_returns_correct_count(self, repo, db):
        windows = [_make_window(hour_of_day=h) for h in range(5)]
        n = repo.bulk_insert_peak_windows(windows, pipeline_run_id="run-abc")
        db.commit()
        assert n == 5

    def test_rows_appear_in_db_after_flush(self, repo, db):
        windows = [_make_window(), _make_window(hour_of_day=9)]
        repo.bulk_insert_peak_windows(windows, pipeline_run_id="run-x")
        db.commit()
        assert db.query(PeakWindow).count() == 2

    def test_empty_list_returns_zero(self, repo, db):
        n = repo.bulk_insert_peak_windows([], pipeline_run_id="run-empty")
        assert n == 0
        assert db.query(PeakWindow).count() == 0

    def test_pipeline_run_id_stamped_on_rows(self, repo, db):
        w = _make_window()
        repo.bulk_insert_peak_windows([w], pipeline_run_id="run-stamp-test")
        db.commit()
        row = db.query(PeakWindow).first()
        assert row.pipeline_run_id == "run-stamp-test"

    def test_multiple_hotspots_inserted(self, repo, db):
        windows = [_make_window(hotspot_id=i) for i in range(1, 6)]
        n = repo.bulk_insert_peak_windows(windows, pipeline_run_id="multi")
        db.commit()
        assert n == 5
        hotspot_ids = {r.hotspot_id for r in db.query(PeakWindow).all()}
        assert hotspot_ids == {1, 2, 3, 4, 5}


# ═══════════════════════════════════════════════════════════════════════════
# delete_windows_for_hotspot
# ═══════════════════════════════════════════════════════════════════════════

class TestDeleteWindowsForHotspot:

    def _seed(self, repo, db):
        windows = [
            _make_window(hotspot_id=1, hour_of_day=7),
            _make_window(hotspot_id=1, hour_of_day=8),
            _make_window(hotspot_id=2, hour_of_day=7),
        ]
        repo.bulk_insert_peak_windows(windows, pipeline_run_id="seed")
        db.commit()

    def test_deletes_only_target_hotspot(self, repo, db):
        self._seed(repo, db)
        deleted = repo.delete_windows_for_hotspot(1)
        db.commit()
        assert deleted == 2
        remaining = db.query(PeakWindow).all()
        assert all(r.hotspot_id == 2 for r in remaining)

    def test_returns_zero_when_none_exist(self, repo, db):
        deleted = repo.delete_windows_for_hotspot(99)
        assert deleted == 0

    def test_other_hotspot_untouched(self, repo, db):
        self._seed(repo, db)
        repo.delete_windows_for_hotspot(1)
        db.commit()
        count_hs2 = db.query(PeakWindow).filter(PeakWindow.hotspot_id == 2).count()
        assert count_hs2 == 1


# ═══════════════════════════════════════════════════════════════════════════
# delete_all_windows
# ═══════════════════════════════════════════════════════════════════════════

class TestDeleteAllWindows:

    def test_truncates_table(self, repo, db):
        windows = [_make_window(hour_of_day=h) for h in range(3)]
        repo.bulk_insert_peak_windows(windows, pipeline_run_id="pre")
        db.commit()
        deleted = repo.delete_all_windows()
        db.commit()
        assert deleted == 3
        assert db.query(PeakWindow).count() == 0

    def test_delete_on_empty_table_returns_zero(self, repo, db):
        assert repo.delete_all_windows() == 0


# ═══════════════════════════════════════════════════════════════════════════
# delete_windows_for_run
# ═══════════════════════════════════════════════════════════════════════════

class TestDeleteWindowsForRun:

    def test_deletes_only_matching_run(self, repo, db):
        repo.bulk_insert_peak_windows(
            [_make_window(hour_of_day=7)], pipeline_run_id="run-A"
        )
        repo.bulk_insert_peak_windows(
            [_make_window(hour_of_day=8)], pipeline_run_id="run-B"
        )
        db.commit()
        deleted = repo.delete_windows_for_run("run-A")
        db.commit()
        assert deleted == 1
        remaining = db.query(PeakWindow).all()
        assert all(r.pipeline_run_id == "run-B" for r in remaining)


# ═══════════════════════════════════════════════════════════════════════════
# get_by_id
# ═══════════════════════════════════════════════════════════════════════════

class TestGetById:

    def test_returns_correct_row(self, repo, db):
        w = _make_window(violation_count=42)
        repo.bulk_insert_peak_windows([w], pipeline_run_id="r1")
        db.commit()
        row = db.query(PeakWindow).first()
        fetched = repo.get_by_id(row.id)
        assert fetched is not None
        assert fetched.violation_count == 42

    def test_returns_none_for_missing_id(self, repo):
        assert repo.get_by_id(999_999) is None


# ═══════════════════════════════════════════════════════════════════════════
# list_for_hotspot
# ═══════════════════════════════════════════════════════════════════════════

class TestListForHotspot:

    def _seed(self, repo, db):
        windows = [
            _make_window(hotspot_id=1, day_of_week=0, hour_of_day=7, violation_count=30),
            _make_window(hotspot_id=1, day_of_week=0, hour_of_day=8, violation_count=50),
            _make_window(hotspot_id=1, day_of_week=1, hour_of_day=9, violation_count=10),
            _make_window(hotspot_id=2, day_of_week=0, hour_of_day=7, violation_count=20),
        ]
        repo.bulk_insert_peak_windows(windows, pipeline_run_id="seed")
        db.commit()

    def test_returns_only_target_hotspot(self, repo, db):
        self._seed(repo, db)
        rows = repo.list_for_hotspot(1)
        assert len(rows) == 3
        assert all(r.hotspot_id == 1 for r in rows)

    def test_ordered_by_violation_count_desc(self, repo, db):
        self._seed(repo, db)
        rows = repo.list_for_hotspot(1)
        counts = [r.violation_count for r in rows]
        assert counts == sorted(counts, reverse=True)

    def test_day_of_week_filter(self, repo, db):
        self._seed(repo, db)
        rows = repo.list_for_hotspot(1, day_of_week=1)
        assert len(rows) == 1
        assert rows[0].hour_of_day == 9

    def test_empty_for_unknown_hotspot(self, repo, db):
        self._seed(repo, db)
        assert repo.list_for_hotspot(99) == []


# ═══════════════════════════════════════════════════════════════════════════
# list_by_priority
# ═══════════════════════════════════════════════════════════════════════════

class TestListByPriority:

    def _seed(self, repo, db):
        windows = [
            _make_window(hour_of_day=7, enforcement_priority="Critical"),
            _make_window(hour_of_day=8, enforcement_priority="High"),
            _make_window(hour_of_day=9, enforcement_priority="High"),
            _make_window(hour_of_day=10, enforcement_priority="Low"),
        ]
        repo.bulk_insert_peak_windows(windows, pipeline_run_id="seed")
        db.commit()

    def test_filters_by_priority(self, repo, db):
        self._seed(repo, db)
        rows = repo.list_by_priority("High")
        assert len(rows) == 2
        assert all(r.enforcement_priority == "High" for r in rows)

    def test_critical_returns_one(self, repo, db):
        self._seed(repo, db)
        rows = repo.list_by_priority("Critical")
        assert len(rows) == 1

    def test_low_priority(self, repo, db):
        self._seed(repo, db)
        rows = repo.list_by_priority("Low")
        assert len(rows) == 1

    def test_limit_respected(self, repo, db):
        windows = [
            _make_window(hour_of_day=h, enforcement_priority="High")
            for h in range(10)
        ]
        repo.bulk_insert_peak_windows(windows, pipeline_run_id="r")
        db.commit()
        rows = repo.list_by_priority("High", limit=3)
        assert len(rows) == 3


# ═══════════════════════════════════════════════════════════════════════════
# list_top_windows
# ═══════════════════════════════════════════════════════════════════════════

class TestListTopWindows:

    def _seed(self, repo, db):
        windows = [
            _make_window(hour_of_day=7,  violation_count=100, enforcement_priority="Critical"),
            _make_window(hour_of_day=8,  violation_count=80,  enforcement_priority="High"),
            _make_window(hour_of_day=9,  violation_count=60,  enforcement_priority="High"),
            _make_window(hour_of_day=10, violation_count=30,  enforcement_priority="Medium"),
            _make_window(hour_of_day=11, violation_count=10,  enforcement_priority="Low"),
        ]
        repo.bulk_insert_peak_windows(windows, pipeline_run_id="seed")
        db.commit()

    def test_top_n_respected(self, repo, db):
        self._seed(repo, db)
        rows = repo.list_top_windows(top_n=3)
        assert len(rows) == 3

    def test_ordered_by_violation_count_desc(self, repo, db):
        self._seed(repo, db)
        rows = repo.list_top_windows(top_n=5)
        counts = [r.violation_count for r in rows]
        assert counts == sorted(counts, reverse=True)

    def test_min_priority_critical_filters_correctly(self, repo, db):
        self._seed(repo, db)
        rows = repo.list_top_windows(top_n=10, min_priority="Critical")
        assert all(r.enforcement_priority == "Critical" for r in rows)
        assert len(rows) == 1

    def test_min_priority_high_includes_critical(self, repo, db):
        self._seed(repo, db)
        rows = repo.list_top_windows(top_n=10, min_priority="High")
        priorities = {r.enforcement_priority for r in rows}
        assert priorities == {"High", "Critical"}


# ═══════════════════════════════════════════════════════════════════════════
# count_total / count_for_hotspot
# ═══════════════════════════════════════════════════════════════════════════

class TestCounts:

    def test_count_total_empty(self, repo, db):
        assert repo.count_total() == 0

    def test_count_total_after_insert(self, repo, db):
        repo.bulk_insert_peak_windows(
            [_make_window(hour_of_day=h) for h in range(4)],
            pipeline_run_id="r",
        )
        db.commit()
        assert repo.count_total() == 4

    def test_count_for_hotspot(self, repo, db):
        repo.bulk_insert_peak_windows(
            [_make_window(hotspot_id=1, hour_of_day=h) for h in range(3)],
            pipeline_run_id="r",
        )
        repo.bulk_insert_peak_windows(
            [_make_window(hotspot_id=2, hour_of_day=7)],
            pipeline_run_id="r",
        )
        db.commit()
        assert repo.count_for_hotspot(1) == 3
        assert repo.count_for_hotspot(2) == 1
        assert repo.count_for_hotspot(99) == 0


# ═══════════════════════════════════════════════════════════════════════════
# get_hotspot_temporal_risk_score
# ═══════════════════════════════════════════════════════════════════════════

class TestGetHotspotTemporalRiskScore:

    def test_no_data_returns_zero(self, repo, db):
        score = repo.get_hotspot_temporal_risk_score(42)
        assert score == 0.0

    def test_all_high_critical_returns_one(self, repo, db):
        windows = [
            _make_window(hotspot_id=1, hour_of_day=7,  enforcement_priority="High",     violation_count=40),
            _make_window(hotspot_id=1, hour_of_day=8,  enforcement_priority="Critical",  violation_count=60),
        ]
        repo.bulk_insert_peak_windows(windows, pipeline_run_id="r")
        db.commit()
        score = repo.get_hotspot_temporal_risk_score(1)
        assert score == 1.0

    def test_no_high_critical_returns_zero(self, repo, db):
        windows = [
            _make_window(hotspot_id=1, hour_of_day=7,  enforcement_priority="Low",    violation_count=20),
            _make_window(hotspot_id=1, hour_of_day=8,  enforcement_priority="Medium", violation_count=30),
        ]
        repo.bulk_insert_peak_windows(windows, pipeline_run_id="r")
        db.commit()
        score = repo.get_hotspot_temporal_risk_score(1)
        assert score == 0.0

    def test_partial_score(self, repo, db):
        """50 High/Critical out of 100 total → score = 0.5."""
        windows = [
            _make_window(hotspot_id=1, hour_of_day=7, enforcement_priority="High",   violation_count=50),
            _make_window(hotspot_id=1, hour_of_day=9, enforcement_priority="Low",    violation_count=50),
        ]
        repo.bulk_insert_peak_windows(windows, pipeline_run_id="r")
        db.commit()
        score = repo.get_hotspot_temporal_risk_score(1)
        assert score == pytest.approx(0.5)

    def test_score_clamped_to_one(self, repo, db):
        windows = [
            _make_window(hotspot_id=1, hour_of_day=h, enforcement_priority="Critical", violation_count=100)
            for h in range(5)
        ]
        repo.bulk_insert_peak_windows(windows, pipeline_run_id="r")
        db.commit()
        score = repo.get_hotspot_temporal_risk_score(1)
        assert score <= 1.0

    def test_score_between_zero_and_one(self, repo, db):
        windows = [
            _make_window(hotspot_id=1, hour_of_day=7, enforcement_priority="High",   violation_count=30),
            _make_window(hotspot_id=1, hour_of_day=8, enforcement_priority="Medium", violation_count=70),
        ]
        repo.bulk_insert_peak_windows(windows, pipeline_run_id="r")
        db.commit()
        score = repo.get_hotspot_temporal_risk_score(1)
        assert 0.0 <= score <= 1.0


# ═══════════════════════════════════════════════════════════════════════════
# get_temporal_risk_scores_all
# ═══════════════════════════════════════════════════════════════════════════

class TestGetTemporalRiskScoresAll:

    def test_returns_empty_dict_when_no_data(self, repo, db):
        result = repo.get_temporal_risk_scores_all()
        assert isinstance(result, dict)
        assert result == {}

    def test_contains_all_hotspot_ids(self, repo, db):
        for hid in [1, 2, 3]:
            repo.bulk_insert_peak_windows(
                [_make_window(hotspot_id=hid, enforcement_priority="High")],
                pipeline_run_id="r",
            )
        db.commit()
        result = repo.get_temporal_risk_scores_all()
        assert set(result.keys()) == {1, 2, 3}

    def test_scores_between_zero_and_one(self, repo, db):
        for hid in [1, 2]:
            repo.bulk_insert_peak_windows(
                [_make_window(hotspot_id=hid, enforcement_priority="High")],
                pipeline_run_id="r",
            )
        db.commit()
        for score in repo.get_temporal_risk_scores_all().values():
            assert 0.0 <= score <= 1.0

    def test_matches_per_hotspot_method(self, repo, db):
        """Batch result must agree with individual hotspot calls."""
        for hid, prio in [(1, "High"), (2, "Low"), (3, "Critical")]:
            repo.bulk_insert_peak_windows(
                [_make_window(hotspot_id=hid, enforcement_priority=prio, violation_count=50)],
                pipeline_run_id="r",
            )
        db.commit()
        batch = repo.get_temporal_risk_scores_all()
        for hid in [1, 2, 3]:
            individual = repo.get_hotspot_temporal_risk_score(hid)
            assert batch[hid] == pytest.approx(individual)


# ═══════════════════════════════════════════════════════════════════════════
# get_heatmap_data
# ═══════════════════════════════════════════════════════════════════════════

class TestGetHeatmapData:

    def test_returns_list_of_dicts(self, repo, db):
        repo.bulk_insert_peak_windows(
            [_make_window()], pipeline_run_id="r"
        )
        db.commit()
        result = repo.get_heatmap_data()
        assert isinstance(result, list)
        assert all(isinstance(row, dict) for row in result)

    def test_dict_has_required_keys(self, repo, db):
        repo.bulk_insert_peak_windows([_make_window()], pipeline_run_id="r")
        db.commit()
        row = repo.get_heatmap_data()[0]
        assert "day_of_week" in row
        assert "hour_of_day" in row
        assert "total_violations" in row

    def test_aggregates_across_hotspots(self, repo, db):
        """Same (day, hour) across two hotspots → summed in heatmap."""
        windows = [
            _make_window(hotspot_id=1, day_of_week=0, hour_of_day=8, violation_count=20),
            _make_window(hotspot_id=2, day_of_week=0, hour_of_day=8, violation_count=30),
        ]
        repo.bulk_insert_peak_windows(windows, pipeline_run_id="r")
        db.commit()
        result = repo.get_heatmap_data()
        cell = next(r for r in result if r["day_of_week"] == 0 and r["hour_of_day"] == 8)
        assert cell["total_violations"] == 50

    def test_empty_table_returns_empty_list(self, repo, db):
        assert repo.get_heatmap_data() == []

    def test_ordered_by_day_and_hour(self, repo, db):
        windows = [
            _make_window(day_of_week=2, hour_of_day=14, violation_count=5),
            _make_window(day_of_week=0, hour_of_day=7,  violation_count=5),
            _make_window(day_of_week=1, hour_of_day=9,  violation_count=5),
        ]
        repo.bulk_insert_peak_windows(windows, pipeline_run_id="r")
        db.commit()
        result = repo.get_heatmap_data()
        days = [r["day_of_week"] for r in result]
        # Should be sorted by day ascending
        assert days == sorted(days)


# ═══════════════════════════════════════════════════════════════════════════
# list_all (pagination + multi-filter)
# ═══════════════════════════════════════════════════════════════════════════

class TestListAll:

    def _seed(self, repo, db):
        windows = [
            _make_window(hotspot_id=1, day_of_week=0, hour_of_day=7),
            _make_window(hotspot_id=1, day_of_week=0, hour_of_day=8),
            _make_window(hotspot_id=1, day_of_week=1, hour_of_day=8),
            _make_window(hotspot_id=2, day_of_week=0, hour_of_day=8),
        ]
        repo.bulk_insert_peak_windows(windows, pipeline_run_id="r")
        db.commit()

    def test_no_filters_returns_all(self, repo, db):
        self._seed(repo, db)
        assert len(repo.list_all()) == 4

    def test_hotspot_id_filter(self, repo, db):
        self._seed(repo, db)
        rows = repo.list_all(hotspot_id=1)
        assert len(rows) == 3

    def test_day_of_week_filter(self, repo, db):
        self._seed(repo, db)
        rows = repo.list_all(day_of_week=1)
        assert len(rows) == 1

    def test_hour_of_day_filter(self, repo, db):
        self._seed(repo, db)
        rows = repo.list_all(hour_of_day=8)
        assert len(rows) == 3

    def test_combined_filters(self, repo, db):
        self._seed(repo, db)
        rows = repo.list_all(hotspot_id=1, day_of_week=0, hour_of_day=8)
        assert len(rows) == 1

    def test_limit(self, repo, db):
        self._seed(repo, db)
        rows = repo.list_all(limit=2)
        assert len(rows) == 2

    def test_offset(self, repo, db):
        self._seed(repo, db)
        all_rows = repo.list_all()
        offset_rows = repo.list_all(offset=2)
        assert len(offset_rows) == len(all_rows) - 2
