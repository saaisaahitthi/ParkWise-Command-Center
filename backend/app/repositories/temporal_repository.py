"""
app/repositories/temporal_repository.py
─────────────────────────────────────────
Data-access layer for the Temporal Intelligence Engine.

Responsibilities
────────────────
- Bulk-insert PeakWindow rows produced by the temporal pipeline.
- Delete stale windows before a fresh pipeline run.
- Provide read helpers for the API layer and downstream EIS calculations.

Patterns
────────
- Synchronous SQLAlchemy Session (matches existing project convention).
- Single Session per method; the caller (service) owns the transaction.
- No business logic — purely CRUD and queries.
- Logging at INFO level for every bulk write.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Sequence

from sqlalchemy import delete, func
from sqlalchemy.orm import Session

from app.core.constants import TableName
from app.core.logging import get_logger
from app.models.analytics import PeakWindow

logger = get_logger(__name__)


class TemporalRepository:
    """
    All database interactions required by the Temporal Intelligence Engine.

    Parameters
    ----------
    db : sqlalchemy.orm.Session
        Active SQLAlchemy session — injected by the service.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # ── Write ─────────────────────────────────────────────────────────────────

    def bulk_insert_peak_windows(
        self,
        windows: Sequence[PeakWindow],
        *,
        pipeline_run_id: str,
    ) -> int:
        """
        Persist a batch of PeakWindow objects.

        The caller is responsible for deleting stale rows (via
        delete_windows_for_hotspot or delete_all_windows) before calling this,
        ensuring idempotent pipeline reruns.

        Returns
        -------
        int
            Number of rows written.
        """
        if not windows:
            logger.info(
                "temporal_repository.bulk_insert_peak_windows",
                message="Empty window list — nothing to insert.",
                pipeline_run_id=pipeline_run_id,
            )
            return 0

        for win in windows:
            win.pipeline_run_id = pipeline_run_id
            self.db.add(win)

        self.db.flush()

        logger.info(
            "temporal_repository.bulk_insert_peak_windows",
            count=len(windows),
            pipeline_run_id=pipeline_run_id,
        )
        return len(windows)

    def delete_windows_for_hotspot(self, hotspot_id: int) -> int:
        """
        Remove all peak windows associated with a specific hotspot.

        Returns
        -------
        int
            Number of rows deleted.
        """
        stmt = delete(PeakWindow).where(PeakWindow.hotspot_id == hotspot_id)
        result = self.db.execute(stmt)
        self.db.flush()

        logger.info(
            "temporal_repository.delete_windows_for_hotspot",
            hotspot_id=hotspot_id,
            rows_deleted=result.rowcount,
        )
        return result.rowcount

    def delete_all_windows(self) -> int:
        """
        Truncate the peak_windows table.  Use before a full pipeline rerun.

        Returns
        -------
        int
            Number of rows deleted.
        """
        stmt = delete(PeakWindow)
        result = self.db.execute(stmt)
        self.db.flush()

        logger.info(
            "temporal_repository.delete_all_windows",
            rows_deleted=result.rowcount,
        )
        return result.rowcount

    def delete_windows_for_run(self, pipeline_run_id: str) -> int:
        """Delete all windows belonging to a specific pipeline run."""
        stmt = delete(PeakWindow).where(PeakWindow.pipeline_run_id == pipeline_run_id)
        result = self.db.execute(stmt)
        self.db.flush()
        return result.rowcount

    # ── Read ──────────────────────────────────────────────────────────────────

    def get_by_id(self, window_id: int) -> Optional[PeakWindow]:
        """Fetch a single PeakWindow by primary key."""
        return self.db.get(PeakWindow, window_id)

    def list_for_hotspot(
        self,
        hotspot_id: int,
        *,
        day_of_week: Optional[int] = None,
    ) -> List[PeakWindow]:
        """
        Return all peak windows for a given hotspot, optionally filtered by
        day-of-week.  Ordered by violation_count descending.
        """
        query = self.db.query(PeakWindow).filter(
            PeakWindow.hotspot_id == hotspot_id
        )
        if day_of_week is not None:
            query = query.filter(PeakWindow.day_of_week == day_of_week)
        return query.order_by(PeakWindow.violation_count.desc()).all()

    def list_by_priority(
        self,
        priority: str,
        *,
        limit: int = 100,
    ) -> List[PeakWindow]:
        """
        Return windows filtered by enforcement_priority.

        Parameters
        ----------
        priority : str
            One of 'Low', 'Medium', 'High', 'Critical'.
        limit : int
            Maximum rows returned.
        """
        return (
            self.db.query(PeakWindow)
            .filter(PeakWindow.enforcement_priority == priority)
            .order_by(PeakWindow.violation_count.desc())
            .limit(limit)
            .all()
        )

    def list_top_windows(
        self,
        *,
        top_n: int = 20,
        min_priority: Optional[str] = None,
    ) -> List[PeakWindow]:
        """
        Return the top-N peak windows by violation_count, city-wide.

        Parameters
        ----------
        top_n : int
            Maximum rows returned.
        min_priority : str, optional
            If provided, restrict to windows at this priority level and above.
            Accepted values: 'High', 'Critical'.
        """
        query = self.db.query(PeakWindow)
        if min_priority == "Critical":
            query = query.filter(
                PeakWindow.enforcement_priority == "Critical"
            )
        elif min_priority == "High":
            query = query.filter(
                PeakWindow.enforcement_priority.in_(["High", "Critical"])
            )
        return (
            query.order_by(PeakWindow.violation_count.desc())
            .limit(top_n)
            .all()
        )

    def list_all(
        self,
        *,
        hotspot_id: Optional[int] = None,
        day_of_week: Optional[int] = None,
        hour_of_day: Optional[int] = None,
        limit: int = 500,
        offset: int = 0,
    ) -> List[PeakWindow]:
        """
        Paginated listing of peak windows with optional dimension filters.
        """
        query = self.db.query(PeakWindow)
        if hotspot_id is not None:
            query = query.filter(PeakWindow.hotspot_id == hotspot_id)
        if day_of_week is not None:
            query = query.filter(PeakWindow.day_of_week == day_of_week)
        if hour_of_day is not None:
            query = query.filter(PeakWindow.hour_of_day == hour_of_day)
        return (
            query.order_by(PeakWindow.violation_count.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def count_total(self) -> int:
        """Return total row count in the peak_windows table."""
        return self.db.query(func.count(PeakWindow.id)).scalar() or 0

    def count_for_hotspot(self, hotspot_id: int) -> int:
        """Return number of peak windows persisted for a specific hotspot."""
        return (
            self.db.query(func.count(PeakWindow.id))
            .filter(PeakWindow.hotspot_id == hotspot_id)
            .scalar()
            or 0
        )

    def get_hotspot_temporal_risk_score(self, hotspot_id: int) -> float:
        """
        Compute a scalar temporal risk score (0.0–1.0) for a hotspot.

        Used downstream by the EIS Engine as its temporal_risk_score input.

        Formula
        -------
        Score = fraction of total city-wide violations that fall inside the
        hotspot's High/Critical peak windows, clamped to [0, 1].

        Falls back gracefully to 0.0 if no data is available.
        """
        # Numerator: violations in High/Critical windows for this hotspot
        hotspot_window_total: int = (
            self.db.query(func.coalesce(func.sum(PeakWindow.violation_count), 0))
            .filter(
                PeakWindow.hotspot_id == hotspot_id,
                PeakWindow.enforcement_priority.in_(["High", "Critical"]),
            )
            .scalar()
            or 0
        )

        # Denominator: total violations across all windows for this hotspot
        hotspot_total: int = (
            self.db.query(func.coalesce(func.sum(PeakWindow.violation_count), 0))
            .filter(PeakWindow.hotspot_id == hotspot_id)
            .scalar()
            or 0
        )

        if hotspot_total == 0:
            return 0.0

        return min(1.0, hotspot_window_total / hotspot_total)

    def get_temporal_risk_scores_all(self) -> dict[int, float]:
        """
        Return a {hotspot_id: temporal_risk_score} mapping for all hotspots.

        Batch version of get_hotspot_temporal_risk_score; avoids N+1 queries.
        Used by the EIS pipeline when computing scores for all hotspots.
        """
        # Total violations per hotspot (all windows)
        totals_q = (
            self.db.query(
                PeakWindow.hotspot_id,
                func.sum(PeakWindow.violation_count).label("total"),
            )
            .filter(PeakWindow.hotspot_id.isnot(None))
            .group_by(PeakWindow.hotspot_id)
            .all()
        )
        totals: dict[int, int] = {row.hotspot_id: int(row.total) for row in totals_q}

        # High/Critical violations per hotspot
        peak_q = (
            self.db.query(
                PeakWindow.hotspot_id,
                func.sum(PeakWindow.violation_count).label("peak_total"),
            )
            .filter(
                PeakWindow.hotspot_id.isnot(None),
                PeakWindow.enforcement_priority.in_(["High", "Critical"]),
            )
            .group_by(PeakWindow.hotspot_id)
            .all()
        )
        peak_totals: dict[int, int] = {
            row.hotspot_id: int(row.peak_total) for row in peak_q
        }

        scores: dict[int, float] = {}
        for hotspot_id, total in totals.items():
            if total == 0:
                scores[hotspot_id] = 0.0
            else:
                peak = peak_totals.get(hotspot_id, 0)
                scores[hotspot_id] = min(1.0, peak / total)

        return scores

    def get_heatmap_data(self) -> List[dict]:
        """
        Return aggregated (day_of_week, hour_of_day, total_violations) for
        the city-wide temporal heatmap dashboard widget.
        """
        rows = (
            self.db.query(
                PeakWindow.day_of_week,
                PeakWindow.hour_of_day,
                func.sum(PeakWindow.violation_count).label("total_violations"),
            )
            .filter(
                PeakWindow.day_of_week.isnot(None),
                PeakWindow.hour_of_day.isnot(None),
            )
            .group_by(PeakWindow.day_of_week, PeakWindow.hour_of_day)
            .order_by(PeakWindow.day_of_week, PeakWindow.hour_of_day)
            .all()
        )
        return [
            {
                "day_of_week": row.day_of_week,
                "hour_of_day": row.hour_of_day,
                "total_violations": int(row.total_violations),
            }
            for row in rows
        ]
