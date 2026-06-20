"""
app/api/v1/endpoints/eis.py
────────────────────────────
Enforcement Intelligence Score — query and rank hotspots by EIS.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import PaginationParams, db_session
from app.models.analytics import EISScore
from app.models.hotspot import Hotspot
from app.services.eis_service import EISService

router = APIRouter()


class EISComponentBreakdown(BaseModel):
    frequency_score: float = Field(ge=0, le=100)
    recurrence_score: float = Field(ge=0, le=100)
    density_score: float = Field(ge=0, le=100)
    temporal_risk_score: float = Field(ge=0, le=100)
    severity_norm: float = Field(ge=0, le=1)
    exposure_score: float = Field(ge=0, le=100)
    severity_multiplier: float


class EISScoreRead(BaseModel):
    id: int
    hotspot_id: int
    eis_score: float = Field(ge=0, le=100)
    risk_category: str
    rank: Optional[int]
    computed_for_date: datetime
    components: Optional[EISComponentBreakdown] = None
    created_at: datetime

    @classmethod
    def from_orm_with_components(cls, obj) -> "EISScoreRead":
        return cls(
            id=obj.id,
            hotspot_id=obj.hotspot_id,
            eis_score=obj.eis_score,
            risk_category=obj.risk_category,
            rank=obj.rank,
            computed_for_date=obj.computed_for_date,
            components=EISComponentBreakdown(
                frequency_score=obj.frequency_score,
                recurrence_score=obj.recurrence_score,
                density_score=obj.density_score,
                temporal_risk_score=obj.temporal_risk_score,
                severity_norm=obj.severity_norm,
                exposure_score=obj.exposure_score,
                severity_multiplier=obj.severity_multiplier,
            ),
            created_at=obj.created_at,
        )


class EISScoreListResponse(BaseModel):
    total: int
    items: list[EISScoreRead]


class EISPipelineResponse(BaseModel):
    pipeline_run_id: str
    hotspots_processed: int
    eis_scores_created: int
    status: str


@router.post(
    "/run-pipeline",
    response_model=EISPipelineResponse,
    summary="Generate EIS scores for all hotspots",
)
def run_eis_pipeline(
    db: Session = Depends(db_session),
) -> EISPipelineResponse:
    try:
        result = EISService(db).run_pipeline()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"EIS pipeline failed: {exc}",
        ) from exc
    return EISPipelineResponse(**result)


def _latest_eis_query(db: Session):
    """Returns a query for the most recent EIS score per hotspot."""
    subq = (
        db.query(EISScore.hotspot_id, func.max(EISScore.id).label("max_id"))
        .group_by(EISScore.hotspot_id)
        .subquery()
    )
    return db.query(EISScore).join(subq, EISScore.id == subq.c.max_id)


@router.get(
    "/scores",
    response_model=EISScoreListResponse,
    summary="Latest EIS scores for all hotspots",
)
def list_eis_scores(
    db: Session = Depends(db_session),
    risk_category: Optional[str] = Query(
        None, pattern="^(Low|Medium|High|Critical)$"
    ),
) -> EISScoreListResponse:
    query = _latest_eis_query(db)
    if risk_category:
        query = query.filter(EISScore.risk_category == risk_category)
    items = query.order_by(EISScore.eis_score.desc()).all()
    return EISScoreListResponse(
        total=len(items),
        items=[EISScoreRead.from_orm_with_components(r) for r in items],
    )


@router.get(
    "/scores/{hotspot_id}",
    response_model=EISScoreRead,
    summary="Latest EIS score for a specific hotspot",
)
def get_hotspot_eis(
    hotspot_id: int,
    db: Session = Depends(db_session),
) -> EISScoreRead:
    score = (
        db.query(EISScore)
        .filter(EISScore.hotspot_id == hotspot_id)
        .order_by(EISScore.id.desc())
        .first()
    )
    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No EIS score found for hotspot {hotspot_id}",
        )
    return EISScoreRead.from_orm_with_components(score)


@router.get(
    "/priority-queue",
    response_model=list[EISScoreRead],
    summary="Enforcement Priority Queue — all hotspots ranked by EIS descending",
)
def get_priority_queue(
    db: Session = Depends(db_session),
    top_n: int = Query(default=20, ge=1, le=200),
) -> list[EISScoreRead]:
    items = (
        _latest_eis_query(db)
        .order_by(EISScore.eis_score.desc())
        .limit(top_n)
        .all()
    )
    return [EISScoreRead.from_orm_with_components(r) for r in items]
