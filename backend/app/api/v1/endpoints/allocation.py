"""
app/api/v1/endpoints/allocation.py
────────────────────────────────────
Officer Allocation Engine — compute and retrieve deployment plans.
"""

from __future__ import annotations

from datetime import datetime
from math import floor
from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Float, cast, desc, func
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.models.analytics import Allocation, EISScore, Forecast
from app.models.hotspot import Hotspot
from app.schemas.analytics import AllocationPlan, AllocationRead, AllocationRequest

router = APIRouter()


def _distribute_officers_exact(
    total_officers: int,
    priority_weights: Sequence[float],
) -> list[int]:
    """Allocate every officer while guaranteeing one per selected hotspot."""
    hotspot_count = len(priority_weights)
    if hotspot_count == 0:
        return []
    if total_officers < hotspot_count:
        raise ValueError("total_officers must cover every selected hotspot")

    allocations = [1] * hotspot_count
    remaining = total_officers - hotspot_count
    if remaining == 0:
        return allocations

    normalized_weights = [max(0.0, float(weight or 0.0)) for weight in priority_weights]
    total_weight = sum(normalized_weights)
    if total_weight <= 0:
        normalized_weights = [1.0] * hotspot_count
        total_weight = float(hotspot_count)

    exact_extras = [
        remaining * weight / total_weight
        for weight in normalized_weights
    ]
    floor_extras = [floor(extra) for extra in exact_extras]
    for index, extra in enumerate(floor_extras):
        allocations[index] += extra

    leftover = remaining - sum(floor_extras)
    remainder_order = sorted(
        range(hotspot_count),
        key=lambda index: (
            exact_extras[index] - floor_extras[index],
            normalized_weights[index],
            -index,
        ),
        reverse=True,
    )
    for index in remainder_order[:leftover]:
        allocations[index] += 1

    return allocations


def _risk_category_from_score(score: float) -> str:
    if score >= 75:
        return "Critical"
    if score >= 50:
        return "High"
    if score >= 25:
        return "Medium"
    return "Low"


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
      1. Rank hotspots by latest forecast, then latest EIS, then violations.
      2. Select the requested top-N hotspots.
      3. Guarantee one officer per selected hotspot.
      4. Allocate every remaining officer proportionally with exact rounding.
      5. Persist allocations and return the plan.
    """
    latest_eis = (
        db.query(EISScore.hotspot_id, func.max(EISScore.id).label("max_id"))
        .group_by(EISScore.hotspot_id)
        .subquery()
    )
    latest_forecast = (
        db.query(Forecast.hotspot_id, func.max(Forecast.id).label("max_id"))
        .filter(Forecast.horizon_days == 1)
        .group_by(Forecast.hotspot_id)
        .subquery()
    )

    requested_hotspots = request.top_n_hotspots or request.total_officers
    selected_hotspot_count = min(requested_hotspots, request.total_officers)
    priority_score = func.coalesce(
        Forecast.predicted_eis,
        EISScore.eis_score,
        cast(Hotspot.total_violations, Float),
        0.0,
    )
    rows = (
        db.query(Hotspot, EISScore, Forecast)
        .outerjoin(latest_eis, Hotspot.id == latest_eis.c.hotspot_id)
        .outerjoin(EISScore, EISScore.id == latest_eis.c.max_id)
        .outerjoin(latest_forecast, Hotspot.id == latest_forecast.c.hotspot_id)
        .outerjoin(Forecast, Forecast.id == latest_forecast.c.max_id)
        .order_by(
            desc(priority_score),
            desc(Hotspot.total_violations),
            Hotspot.id.asc(),
        )
        .limit(selected_hotspot_count)
        .all()
    )
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No hotspots are available for officer allocation.",
        )

    total_officers = request.total_officers
    priority_weights = [
        float(
            forecast.predicted_eis
            if forecast is not None and forecast.predicted_eis is not None
            else eis.eis_score
            if eis is not None and eis.eis_score is not None
            else hotspot.total_violations or 0
        )
        for hotspot, eis, forecast in rows
    ]
    officer_assignments = _distribute_officers_exact(
        total_officers=total_officers,
        priority_weights=priority_weights,
    )
    computed_at = datetime.utcnow()
    allocations: list[AllocationRead] = []

    for rank, ((hotspot_obj, eis_obj, forecast_obj), officers) in enumerate(
        zip(rows, officer_assignments),
        start=1,
    ):
        priority_value = priority_weights[rank - 1]
        risk_category = (
            forecast_obj.predicted_risk_category
            if forecast_obj is not None and forecast_obj.predicted_risk_category
            else eis_obj.risk_category
            if eis_obj is not None and eis_obj.risk_category
            else _risk_category_from_score(priority_value)
        )
        fraction = officers / total_officers

        alloc = Allocation(
            hotspot_id=hotspot_obj.id,
            eis_score_id=eis_obj.id if eis_obj is not None else None,
            officers_allocated=officers,
            allocation_fraction=round(fraction, 4),
            priority_rank=rank,
            deployment_window=None,  # populated by temporal engine in full pipeline
            total_officers_available=total_officers,
            eis_snapshot=eis_obj.eis_score if eis_obj is not None else None,
            risk_category=risk_category,
            allocation_date=computed_at,
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
                eis_snapshot=eis_obj.eis_score if eis_obj is not None else None,
                risk_category=risk_category,
                allocation_date=computed_at,
            )
        )

    db.commit()

    return AllocationPlan(
        total_officers=total_officers,
        hotspots_covered=len(allocations),
        allocations=allocations,
        unallocated_officers=0,
        computed_at=computed_at,
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
        .filter(Allocation.allocation_date == latest.allocation_date)
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
        unallocated_officers=max(
            0,
            int(latest.total_officers_available or 0)
            - sum(int(item.officers_allocated or 0) for item in items),
        ),
        computed_at=latest.allocation_date,
    )
