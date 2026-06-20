"""
app/api/v1/endpoints/allocation.py
────────────────────────────────────
Officer Allocation Engine — compute and retrieve deployment plans.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.models.analytics import Allocation, EISScore
from app.models.hotspot import Hotspot
from app.schemas.analytics import AllocationPlan, AllocationRead, AllocationRequest
from app.core.constants import AllocationDefaults, RiskCategory

router = APIRouter()


@router.post(
    "/compute",
    response_model=AllocationPlan,
    summary="Compute officer allocation from latest EIS scores",
    status_code=status.HTTP_200_OK,
)
def compute_allocation(
    request: AllocationRequest,
    db: Session = Depends(db_session),
) -> AllocationPlan:
    """
    Proportional allocation algorithm:
      1. Fetch latest EIS scores, filtered to top_n or Critical+High hotspots.
      2. Allocate officers proportionally to EIS score.
      3. Enforce min/max per hotspot bounds.
      4. Persist allocations and return the plan.
    """
    # Latest EIS per hotspot
    subq = (
        db.query(EISScore.hotspot_id, func.max(EISScore.id).label("max_id"))
        .group_by(EISScore.hotspot_id)
        .subquery()
    )
    eis_query = (
        db.query(EISScore, Hotspot)
        .join(subq, EISScore.id == subq.c.max_id)
        .join(Hotspot, EISScore.hotspot_id == Hotspot.id)
        .filter(EISScore.risk_category.in_(["Critical", "High"]))
        .order_by(EISScore.eis_score.desc())
    )
    if request.top_n_hotspots:
        eis_query = eis_query.limit(request.top_n_hotspots)

    rows = eis_query.all()
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No Critical or High EIS hotspots found. Run the EIS pipeline first.",
        )

    total_eis = sum(r.EISScore.eis_score for r in rows)
    total_officers = request.total_officers
    allocations: list[AllocationRead] = []
    officers_used = 0

    for rank, row in enumerate(rows, start=1):
        eis_obj, hotspot_obj = row.EISScore, row.Hotspot
        fraction = eis_obj.eis_score / total_eis if total_eis > 0 else 1 / len(rows)
        raw_officers = fraction * total_officers
        officers = max(
            AllocationDefaults.MIN_OFFICERS_PER_HOTSPOT,
            min(AllocationDefaults.MAX_OFFICERS_PER_HOTSPOT, round(raw_officers)),
        )
        officers_used += officers

        alloc = Allocation(
            hotspot_id=hotspot_obj.id,
            eis_score_id=eis_obj.id,
            officers_allocated=officers,
            allocation_fraction=round(fraction, 4),
            priority_rank=rank,
            deployment_window=None,  # populated by temporal engine in full pipeline
            total_officers_available=total_officers,
            eis_snapshot=eis_obj.eis_score,
            risk_category=eis_obj.risk_category,
        )
        db.add(alloc)

        allocations.append(
            AllocationRead(
                id=0,  # placeholder before flush
                hotspot_id=hotspot_obj.id,
                hotspot_name=hotspot_obj.hotspot_name,
                centroid_lat=hotspot_obj.centroid_lat,
                centroid_lon=hotspot_obj.centroid_lon,
                officers_allocated=officers,
                allocation_fraction=round(fraction, 4),
                priority_rank=rank,
                deployment_window=None,
                eis_snapshot=eis_obj.eis_score,
                risk_category=eis_obj.risk_category,
                allocation_date=datetime.utcnow(),
            )
        )

    db.commit()

    return AllocationPlan(
        total_officers=total_officers,
        hotspots_covered=len(allocations),
        allocations=allocations,
        unallocated_officers=max(0, total_officers - officers_used),
        computed_at=datetime.utcnow(),
    )


@router.get(
    "/latest",
    response_model=AllocationPlan,
    summary="Retrieve the most recent allocation plan",
)
def get_latest_allocation(db: Session = Depends(db_session)) -> AllocationPlan:
    latest = (
        db.query(Allocation)
        .order_by(Allocation.allocation_date.desc())
        .first()
    )
    if not latest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No allocation plan found. POST /allocation/compute first.",
        )
    allocs = (
        db.query(Allocation, Hotspot)
        .join(Hotspot, Allocation.hotspot_id == Hotspot.id)
        .filter(Allocation.allocation_date >= latest.allocation_date.replace(second=0, microsecond=0))
        .order_by(Allocation.priority_rank)
        .all()
    )
    items = [
        AllocationRead(
            id=a.id,
            hotspot_id=a.hotspot_id,
            hotspot_name=h.hotspot_name,
            centroid_lat=h.centroid_lat,
            centroid_lon=h.centroid_lon,
            officers_allocated=a.officers_allocated,
            allocation_fraction=a.allocation_fraction,
            priority_rank=a.priority_rank,
            deployment_window=a.deployment_window,
            eis_snapshot=a.eis_snapshot,
            risk_category=a.risk_category,
            allocation_date=a.allocation_date,
        )
        for a, h in allocs
    ]
    return AllocationPlan(
        total_officers=latest.total_officers_available,
        hotspots_covered=len(items),
        allocations=items,
        unallocated_officers=0,
        computed_at=latest.allocation_date,
    )
