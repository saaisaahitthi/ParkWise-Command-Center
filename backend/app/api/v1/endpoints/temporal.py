"""
app/api/v1/endpoints/temporal.py
─────────────────────────────────
Temporal Intelligence Engine — peak windows and enforcement schedules.

Endpoints
─────────
GET  /temporal/peak-windows          List persisted peak windows (filterable)
GET  /temporal/peak-windows/{id}     Single peak window detail
GET  /temporal/enforcement-schedule  Top High/Critical windows for deployment
GET  /temporal/heatmap               City-wide (day, hour, count) grid
GET  /temporal/hotspots/{id}/windows Peak windows for one hotspot
GET  /temporal/hotspots/{id}/risk    Temporal risk score for EIS input
POST /temporal/run-pipeline          Trigger full temporal analysis pipeline
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import PaginationParams, db_session
from app.core.exceptions import (
    InsufficientDataForClusteringError,
    PipelineError,
)
from app.models.analytics import PeakWindow
from app.schemas.analytics import PeakWindowRead
from app.services.temporal_service import TemporalRunResult, TemporalService

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# Request / Response schemas (temporal-specific — not in analytics.py)
# ─────────────────────────────────────────────────────────────────────────────

class TemporalPipelineRequest(BaseModel):
    """Input for POST /temporal/run-pipeline."""
    truncate_existing: bool = Field(
        default=True,
        description=(
            "If true, all existing peak_windows rows are deleted before "
            "inserting fresh results (idempotent rerun)."
        ),
    )
    hotspot_ids: Optional[List[int]] = Field(
        default=None,
        description="Limit analysis to specific hotspot IDs.  None = all hotspots.",
    )
    min_window_violations: int = Field(
        default=5,
        ge=1,
        le=100,
        description=(
            "Minimum violation count for a (hotspot, day, hour) cell to be "
            "saved as a PeakWindow."
        ),
    )


class TemporalPipelineResponse(BaseModel):
    """Summary returned after a pipeline run."""
    pipeline_run_id: str
    n_violations_analysed: int
    n_hotspots_analysed: int
    n_windows_written: int
    n_windows_deleted: int
    duration_seconds: float
    started_at: str
    completed_at: str


class HeatmapCell(BaseModel):
    """A single cell in the temporal heatmap grid."""
    day_of_week: int = Field(description="0=Monday … 6=Sunday")
    hour_of_day: int = Field(description="0–23")
    total_violations: int


class TemporalRiskScoreResponse(BaseModel):
    """Temporal risk score for a single hotspot."""
    hotspot_id: int
    temporal_risk_score: float = Field(
        ge=0.0, le=1.0,
        description="Fraction of violations in High/Critical windows (0–1).",
    )


class PeakWindowListResponse(BaseModel):
    total: int
    items: List[PeakWindowRead]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _to_schema(window: PeakWindow) -> PeakWindowRead:
    return PeakWindowRead.model_validate(window)


def _run_result_to_response(result: TemporalRunResult) -> TemporalPipelineResponse:
    return TemporalPipelineResponse(
        pipeline_run_id=result.pipeline_run_id,
        n_violations_analysed=result.n_violations_analysed,
        n_hotspots_analysed=result.n_hotspots_analysed,
        n_windows_written=result.n_windows_written,
        n_windows_deleted=result.n_windows_deleted,
        duration_seconds=round(result.duration_seconds, 3),
        started_at=result.started_at.isoformat(),
        completed_at=result.completed_at.isoformat(),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/peak-windows",
    response_model=PeakWindowListResponse,
    summary="List peak violation time windows",
    description=(
        "Returns all persisted peak windows, optionally filtered by hotspot, "
        "day-of-week (0=Monday), or hour-of-day.  Ordered by violation_count desc."
    ),
)
def list_peak_windows(
    db: Session = Depends(db_session),
    pagination: PaginationParams = Depends(),
    hotspot_id: Optional[int] = Query(None, description="Filter to a specific hotspot"),
    day_of_week: Optional[int] = Query(None, ge=0, le=6, description="0=Monday … 6=Sunday"),
    hour_of_day: Optional[int] = Query(None, ge=0, le=23),
) -> PeakWindowListResponse:
    svc = TemporalService(db)
    windows = svc.get_peak_windows(
        hotspot_id=hotspot_id,
        day_of_week=day_of_week,
        hour_of_day=hour_of_day,
        limit=pagination.limit,
        offset=pagination.skip,
    )
    return PeakWindowListResponse(
        total=len(windows),
        items=[_to_schema(w) for w in windows],
    )


@router.get(
    "/peak-windows/{window_id}",
    response_model=PeakWindowRead,
    summary="Retrieve a single peak window by ID",
)
def get_peak_window(
    window_id: int,
    db: Session = Depends(db_session),
) -> PeakWindowRead:
    from app.repositories.temporal_repository import TemporalRepository
    repo = TemporalRepository(db)
    window = repo.get_by_id(window_id)
    if not window:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PeakWindow {window_id} not found.",
        )
    return _to_schema(window)


@router.get(
    "/enforcement-schedule",
    response_model=List[PeakWindowRead],
    summary="Top recommended enforcement windows (city-wide)",
    description=(
        "Returns the top-N High/Critical priority peak windows, ordered by "
        "violation_count descending.  Intended for the daily deployment brief."
    ),
)
def get_enforcement_schedule(
    db: Session = Depends(db_session),
    top_n: int = Query(default=10, ge=1, le=50),
) -> List[PeakWindowRead]:
    svc = TemporalService(db)
    windows = svc.get_enforcement_schedule(top_n=top_n)
    return [_to_schema(w) for w in windows]


@router.get(
    "/heatmap",
    response_model=List[HeatmapCell],
    summary="City-wide temporal heatmap data",
    description=(
        "Returns a list of (day_of_week, hour_of_day, total_violations) cells "
        "aggregated across all hotspots.  Suitable for rendering a 7×24 heatmap "
        "on the command-centre dashboard."
    ),
)
def get_heatmap(
    db: Session = Depends(db_session),
) -> List[HeatmapCell]:
    svc = TemporalService(db)
    rows = svc.get_heatmap_data()
    return [HeatmapCell(**row) for row in rows]


@router.get(
    "/hotspots/{hotspot_id}/windows",
    response_model=List[PeakWindowRead],
    summary="Peak windows for a specific hotspot",
)
def get_hotspot_windows(
    hotspot_id: int,
    db: Session = Depends(db_session),
    day_of_week: Optional[int] = Query(None, ge=0, le=6),
) -> List[PeakWindowRead]:
    svc = TemporalService(db)
    windows = svc.get_peak_windows(
        hotspot_id=hotspot_id,
        day_of_week=day_of_week,
    )
    if not windows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No peak windows found for hotspot {hotspot_id}.",
        )
    return [_to_schema(w) for w in windows]


@router.get(
    "/hotspots/{hotspot_id}/risk-score",
    response_model=TemporalRiskScoreResponse,
    summary="Temporal risk score for a hotspot (EIS input)",
    description=(
        "Returns the scalar temporal_risk_score (0–1) for the given hotspot. "
        "This value feeds directly into the EIS Engine as the temporal_risk "
        "component."
    ),
)
def get_hotspot_temporal_risk(
    hotspot_id: int,
    db: Session = Depends(db_session),
) -> TemporalRiskScoreResponse:
    svc = TemporalService(db)
    score = svc.get_temporal_risk_score(hotspot_id)
    return TemporalRiskScoreResponse(
        hotspot_id=hotspot_id,
        temporal_risk_score=score,
    )


@router.post(
    "/run-pipeline",
    response_model=TemporalPipelineResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger the Temporal Intelligence Engine pipeline",
    description=(
        "Runs the full temporal analysis pipeline: loads enriched violations, "
        "converts timestamps to IST, aggregates by (hotspot, day, hour), "
        "assigns enforcement priorities, and persists PeakWindow rows. "
        "This is an idempotent operation — existing windows are truncated "
        "by default before fresh results are written."
    ),
)
def run_temporal_pipeline(
    db: Session = Depends(db_session),
    body: TemporalPipelineRequest = Body(default=TemporalPipelineRequest()),
) -> TemporalPipelineResponse:
    svc = TemporalService(db)
    try:
        result = svc.run_pipeline(
            truncate_existing=body.truncate_existing,
            hotspot_ids=body.hotspot_ids,
            min_window_violations=body.min_window_violations,
        )
        db.commit()
    except InsufficientDataForClusteringError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except PipelineError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected pipeline error: {exc}",
        ) from exc

    return _run_result_to_response(result)
