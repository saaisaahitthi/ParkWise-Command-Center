"""
app/services/temporal_service.py
──────────────────────────────────
Temporal Intelligence Engine — service layer.

Orchestrates the complete pipeline from enriched violations through to
persisted PeakWindow rows and returns a structured run result.

Pipeline steps
──────────────
1. Pre-flight validation (minimum data check).
2. Load EnrichedViolations with IST-adjusted timestamps from the repository.
3. Run the sub-analysers (hour, day, density, risk scoring).
4. Assemble PeakWindow ORM objects from analyser outputs.
5. Optionally truncate stale windows, then bulk-insert fresh ones.
6. Return a TemporalRunResult summary.

Transaction strategy
────────────────────
The service operates within a single transaction owned by the caller.
It never commits directly — only flushes so RETURNING works if needed.
On failure the caller rolls back.

IST convention
──────────────
All timestamps stored in the violations table are UTC.  This service
converts them to IST (UTC+5:30) before dispatching to analysers, so that
hour_of_day / day_of_week dimensions reflect local enforcement reality.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Sequence

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.constants import RiskCategory, TimeWindow
from app.core.exceptions import InsufficientDataForClusteringError, PipelineError
from app.core.logging import get_logger
from app.models.analytics import PeakWindow
from app.models.enriched_violation import EnrichedViolation
from app.models.violation import Violation
from app.repositories.temporal_repository import TemporalRepository

logger = get_logger(__name__)

# ── IST offset ────────────────────────────────────────────────────────────────
_IST_OFFSET = timedelta(hours=5, minutes=30)

# ── Minimum violations needed before running temporal analysis ─────────────────
_MIN_VIOLATIONS_ABSOLUTE: int = 30

# ── Enforcement priority thresholds (pct_of_total) ────────────────────────────
_PRIORITY_CRITICAL_PCT: float = 0.15   # ≥15 % → Critical
_PRIORITY_HIGH_PCT: float = 0.08       # ≥8 %  → High
_PRIORITY_MEDIUM_PCT: float = 0.03     # ≥3 %  → Medium
# below 3 % → Low


# ─────────────────────────────────────────────────────────────────────────────
# Result dataclass
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class TemporalRunResult:
    """Summary returned after a full temporal intelligence run."""

    pipeline_run_id: str
    n_violations_analysed: int
    n_hotspots_analysed: int
    n_windows_written: int
    n_windows_deleted: int
    started_at: datetime
    completed_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def duration_seconds(self) -> float:
        return (self.completed_at - self.started_at).total_seconds()

    def to_dict(self) -> Dict:
        return {
            "pipeline_run_id": self.pipeline_run_id,
            "n_violations_analysed": self.n_violations_analysed,
            "n_hotspots_analysed": self.n_hotspots_analysed,
            "n_windows_written": self.n_windows_written,
            "n_windows_deleted": self.n_windows_deleted,
            "duration_seconds": round(self.duration_seconds, 2),
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Internal data structures
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class _ViolationRecord:
    """Lightweight internal record passed between analysis steps."""
    hotspot_id: Optional[int]
    hour_of_day: int       # IST
    day_of_week: int       # IST (0=Monday … 6=Sunday)
    violation_date: datetime  # IST-adjusted


# ─────────────────────────────────────────────────────────────────────────────
# TemporalService
# ─────────────────────────────────────────────────────────────────────────────

class TemporalService:
    """
    Exposes high-level temporal operations consumed by the API layer and the
    EIS pipeline.

    Parameters
    ----------
    db : sqlalchemy.orm.Session
        Active session — injected via FastAPI Depends or passed directly in
        pipeline scripts.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self._repo = TemporalRepository(db)

    # ── Main pipeline entry point ─────────────────────────────────────────────

    def run_pipeline(
        self,
        *,
        truncate_existing: bool = True,
        hotspot_ids: Optional[Sequence[int]] = None,
        min_window_violations: int = 5,
    ) -> TemporalRunResult:
        """
        Execute the full Temporal Intelligence Engine pipeline.

        Parameters
        ----------
        truncate_existing : bool
            If True, delete all existing peak_windows rows before inserting
            fresh ones (idempotent rerun).  If False, only delete windows for
            the targeted hotspot_ids.
        hotspot_ids : sequence of int, optional
            Limit analysis to specific hotspots.  None means all hotspots.
        min_window_violations : int
            Minimum violation count for a (hotspot, day, hour) cell to be
            persisted as a PeakWindow.

        Returns
        -------
        TemporalRunResult
            Summary of the pipeline execution.

        Raises
        ------
        InsufficientDataForClusteringError
            If the database contains fewer violations than _MIN_VIOLATIONS_ABSOLUTE.
        PipelineError
            On any unexpected error during analysis or persistence.
        """
        pipeline_run_id = str(uuid.uuid4())
        started_at = datetime.utcnow()

        logger.info(
            "temporal_service.run_pipeline.start",
            pipeline_run_id=pipeline_run_id,
            truncate_existing=truncate_existing,
            hotspot_ids=hotspot_ids,
        )

        # ── Step 1: Pre-flight check ──────────────────────────────────────────
        total_evs = self.db.query(func.count(EnrichedViolation.id)).scalar() or 0
        if total_evs < _MIN_VIOLATIONS_ABSOLUTE:
            raise InsufficientDataForClusteringError(
                message=(
                    f"Temporal analysis requires at least "
                    f"{_MIN_VIOLATIONS_ABSOLUTE} enriched violations; "
                    f"found {total_evs}."
                )
            )

        # ── Step 2: Load violation records ────────────────────────────────────
        records = self._load_records(hotspot_ids=hotspot_ids)
        if not records:
            raise PipelineError(
                message="No enriched violations found for the requested hotspots."
            )

        logger.info(
            "temporal_service.run_pipeline.records_loaded",
            n_records=len(records),
            pipeline_run_id=pipeline_run_id,
        )

        # ── Step 3: Clear stale windows ───────────────────────────────────────
        n_deleted = 0
        if truncate_existing:
            n_deleted = self._repo.delete_all_windows()
        elif hotspot_ids:
            for hid in hotspot_ids:
                n_deleted += self._repo.delete_windows_for_hotspot(hid)

        # ── Step 4: Analyse and build PeakWindow objects ──────────────────────
        windows = self._analyse(
            records=records,
            min_window_violations=min_window_violations,
            pipeline_run_id=pipeline_run_id,
        )

        # ── Step 5: Persist ───────────────────────────────────────────────────
        n_written = self._repo.bulk_insert_peak_windows(
            windows, pipeline_run_id=pipeline_run_id
        )

        completed_at = datetime.utcnow()
        n_hotspots = len({r.hotspot_id for r in records if r.hotspot_id is not None})

        result = TemporalRunResult(
            pipeline_run_id=pipeline_run_id,
            n_violations_analysed=len(records),
            n_hotspots_analysed=n_hotspots,
            n_windows_written=n_written,
            n_windows_deleted=n_deleted,
            started_at=started_at,
            completed_at=completed_at,
        )

        logger.info(
            "temporal_service.run_pipeline.complete",
            **result.to_dict(),
        )
        return result

    # ── Read helpers (used by API endpoints) ──────────────────────────────────

    def get_peak_windows(
        self,
        *,
        hotspot_id: Optional[int] = None,
        day_of_week: Optional[int] = None,
        hour_of_day: Optional[int] = None,
        limit: int = 500,
        offset: int = 0,
    ) -> List[PeakWindow]:
        """Paginated read of peak windows with optional filters."""
        return self._repo.list_all(
            hotspot_id=hotspot_id,
            day_of_week=day_of_week,
            hour_of_day=hour_of_day,
            limit=limit,
            offset=offset,
        )

    def get_enforcement_schedule(self, *, top_n: int = 10) -> List[PeakWindow]:
        """Return top-N windows by violation_count (High/Critical priority)."""
        return self._repo.list_top_windows(top_n=top_n, min_priority="High")

    def get_temporal_risk_score(self, hotspot_id: int) -> float:
        """Scalar temporal risk score for a hotspot (0–1), used by EIS."""
        return self._repo.get_hotspot_temporal_risk_score(hotspot_id)

    def get_all_temporal_risk_scores(self) -> dict[int, float]:
        """Batch temporal risk scores for all hotspots — used by EIS pipeline."""
        return self._repo.get_temporal_risk_scores_all()

    def get_heatmap_data(self) -> List[dict]:
        """City-wide (day, hour, count) triples for the dashboard heatmap."""
        return self._repo.get_heatmap_data()

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _load_records(
        self, *, hotspot_ids: Optional[Sequence[int]]
    ) -> List[_ViolationRecord]:
        """
        Join EnrichedViolations → Violations, convert UTC → IST, and
        return lightweight _ViolationRecord objects.
        """
        query = (
            self.db.query(
                EnrichedViolation.hotspot_id,
                Violation.violation_date,
            )
            .join(Violation, EnrichedViolation.violation_id == Violation.id)
            .filter(Violation.violation_date.isnot(None))
        )
        if hotspot_ids:
            query = query.filter(EnrichedViolation.hotspot_id.in_(hotspot_ids))

        rows = query.all()

        records: List[_ViolationRecord] = []
        for row in rows:
            ist_ts: datetime = row.violation_date + _IST_OFFSET
            records.append(
                _ViolationRecord(
                    hotspot_id=row.hotspot_id,
                    hour_of_day=ist_ts.hour,
                    day_of_week=ist_ts.weekday(),   # 0=Monday … 6=Sunday
                    violation_date=ist_ts,
                )
            )
        return records

    def _analyse(
        self,
        *,
        records: List[_ViolationRecord],
        min_window_violations: int,
        pipeline_run_id: str,
    ) -> List[PeakWindow]:
        """
        Build PeakWindow ORM objects from the violation records.

        Strategy
        ────────
        For each unique (hotspot_id, day_of_week, hour_of_day) cell:
          1. Count violations.
          2. Compute avg_violations (count / occurrences of that weekday).
          3. Compute pct_of_total.
          4. Assign enforcement_priority based on pct thresholds.
          5. Derive window_label and recommended enforcement hours.

        Cells below min_window_violations are dropped (noise reduction).
        """
        total_violations = len(records)

        # ── 4-D aggregation: (hotspot_id, day, hour) → count ─────────────────
        cell_counts: Dict[tuple, int] = {}
        for rec in records:
            key = (rec.hotspot_id, rec.day_of_week, rec.hour_of_day)
            cell_counts[key] = cell_counts.get(key, 0) + 1

        # ── Occurrences per weekday (to compute avg_violations) ───────────────
        day_occurrences: Dict[int, int] = {}
        for rec in records:
            if rec.day_of_week not in day_occurrences:
                day_occurrences[rec.day_of_week] = 0
        # Use unique dates per weekday as occurrence denominator
        day_dates: Dict[int, set] = {}
        for rec in records:
            day_dates.setdefault(rec.day_of_week, set()).add(
                rec.violation_date.date()
            )
        for dow, dates in day_dates.items():
            day_occurrences[dow] = len(dates)

        # ── Build PeakWindow objects ──────────────────────────────────────────
        windows: List[PeakWindow] = []
        for (hotspot_id, day, hour), count in cell_counts.items():
            if count < min_window_violations:
                continue

            pct = count / total_violations if total_violations > 0 else 0.0
            occurrences = day_occurrences.get(day, 1)
            avg = count / occurrences if occurrences > 0 else float(count)

            priority = _assign_priority(pct)
            label = _window_label(hour)
            rec_start, rec_end = _enforcement_window(hour)

            windows.append(
                PeakWindow(
                    hotspot_id=hotspot_id,
                    day_of_week=day,
                    hour_of_day=hour,
                    window_label=label,
                    violation_count=count,
                    avg_violations=round(avg, 2),
                    pct_of_total=round(pct * 100, 4),
                    recommended_start_hour=rec_start,
                    recommended_end_hour=rec_end,
                    enforcement_priority=priority,
                    pipeline_run_id=pipeline_run_id,
                    created_at=datetime.utcnow(),
                )
            )

        logger.info(
            "temporal_service._analyse.complete",
            cells_evaluated=len(cell_counts),
            windows_built=len(windows),
            pipeline_run_id=pipeline_run_id,
        )
        return windows


# ─────────────────────────────────────────────────────────────────────────────
# Pure helper functions (no I/O)
# ─────────────────────────────────────────────────────────────────────────────

def _assign_priority(pct: float) -> str:
    """Map fraction-of-total to enforcement priority label."""
    if pct >= _PRIORITY_CRITICAL_PCT:
        return "Critical"
    if pct >= _PRIORITY_HIGH_PCT:
        return "High"
    if pct >= _PRIORITY_MEDIUM_PCT:
        return "Medium"
    return "Low"


def _window_label(hour: int) -> str:
    """Return a human-readable time-window label for a given hour (0–23)."""
    morning_start, morning_end = TimeWindow.MORNING_RUSH
    lunch_start, lunch_end = TimeWindow.LUNCH
    aft_start, aft_end = TimeWindow.AFTERNOON_RUSH
    night_start, night_end = TimeWindow.NIGHT

    if morning_start <= hour < morning_end:
        return "Morning Rush"
    if lunch_start <= hour < lunch_end:
        return "Lunch Hour"
    if aft_start <= hour < aft_end:
        return "Evening Rush"
    if hour >= night_start or hour < night_end:
        return "Night"
    return "Off-Peak"


def _enforcement_window(hour: int) -> tuple[int, int]:
    """
    Recommend a ±1 h enforcement bracket around the peak hour.

    Clamped so that start ≥ 0 and end ≤ 23.
    """
    start = max(0, hour - 1)
    end = min(23, hour + 1)
    return start, end
