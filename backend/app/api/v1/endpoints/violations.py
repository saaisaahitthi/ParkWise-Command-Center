"""
app/api/v1/endpoints/violations.py
────────────────────────────────────
Raw violations query endpoint — used by the Hotspot Explorer detail view.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import PaginationParams, db_session
from app.models.violation import Violation
from app.schemas.violation import ViolationListResponse, ViolationRead

router = APIRouter()


@router.get(
    "/",
    response_model=ViolationListResponse,
    summary="List violations with optional filters",
)
def list_violations(
    db: Session = Depends(db_session),
    pagination: PaginationParams = Depends(),
    junction_name: Optional[str] = Query(None),
    violation_type: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
) -> ViolationListResponse:
    query = db.query(Violation)
    if junction_name:
        query = query.filter(Violation.junction_name.ilike(f"%{junction_name}%"))
    if violation_type:
        query = query.filter(Violation.violation_type == violation_type)
    if date_from:
        query = query.filter(Violation.violation_date >= date_from)
    if date_to:
        query = query.filter(Violation.violation_date <= date_to)

    total = query.count()
    items = (
        query
        .order_by(Violation.violation_date.desc())
        .offset(pagination.skip)
        .limit(pagination.limit)
        .all()
    )
    return ViolationListResponse(
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        items=[ViolationRead.model_validate(v) for v in items],
    )

from pydantic import BaseModel
from typing import List, Any
from geoalchemy2.elements import WKTElement

class ViolationBatchInput(BaseModel):
    batch: List[dict]

@router.post("/batch-upload", summary="Batch upload violations")
def batch_upload(
    payload: ViolationBatchInput,
    db: Session = Depends(db_session)
):
    from sqlalchemy.exc import SQLAlchemyError
    try:
        new_violations = []
        for row in payload.batch:
            lat = row.get("lat")
            lon = row.get("lon")
            if lat is None or lon is None:
                continue
            v = Violation(
                violation_id=row["violation_id"],
                vehicle_type=row.get("vehicle_type", "Unknown"),
                violation_type=row.get("violation_type", "Unknown"),
                violation_date=datetime.fromisoformat(row["violation_date"]) if "violation_date" in row and row["violation_date"] else datetime.now(),
                junction_name=row.get("junction_name", "Unknown"),
                location=WKTElement(f"POINT({lon} {lat})", srid=4326),
            )
            new_violations.append(v)
        if new_violations:
            db.bulk_save_objects(new_violations)
            db.commit()
        return {"status": "ok", "inserted": len(new_violations)}
    except Exception as e:
        db.rollback()
        return {"status": "error", "detail": str(e)}
