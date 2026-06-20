"""
app/api/v1/endpoints/patrol.py
───────────────────────────────
Smart Patrol Route Optimization — query generated patrol routes.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.models.analytics import PatrolRoute
from app.schemas.analytics import PatrolRouteRead, PatrolStop

router = APIRouter()


def _route_to_schema(route: PatrolRoute) -> PatrolRouteRead:
    stops = [
        PatrolStop(
            sequence=stop["sequence"],
            hotspot_id=stop["hotspot_id"],
            hotspot_name=stop.get("hotspot_name"),
            lat=stop.get("lat", stop.get("latitude")),
            lon=stop.get("lon", stop.get("longitude")),
            eis_score=stop.get("eis_score", stop.get("eis_snapshot")),
            estimated_arrival=stop.get("estimated_arrival"),
            recommended_duration_min=stop.get(
                "recommended_duration_min",
                stop.get("dwell_time_minutes"),
            ),
        )
        for stop in (route.stops_json or [])
    ]
    return PatrolRouteRead(
        id=route.id,
        route_name=route.route_name,
        shift_label=route.shift_label,
        officer_count=route.officer_count,
        stops=stops,
        total_distance_km=route.total_distance_km,
        estimated_duration_min=route.estimated_duration_min,
        hotspots_covered=route.hotspots_covered,
        total_eis_covered=route.total_eis_covered,
        created_at=route.created_at,
    )


@router.get(
    "/",
    response_model=list[PatrolRouteRead],
    summary="List all generated patrol routes",
)
def list_patrol_routes(db: Session = Depends(db_session)) -> list[PatrolRouteRead]:
    routes = db.query(PatrolRoute).order_by(PatrolRoute.created_at.desc()).all()
    return [_route_to_schema(r) for r in routes]


@router.get(
    "/{route_id}",
    response_model=PatrolRouteRead,
    summary="Get a specific patrol route",
)
def get_patrol_route(
    route_id: int,
    db: Session = Depends(db_session),
) -> PatrolRouteRead:
    route = db.query(PatrolRoute).filter(PatrolRoute.id == route_id).first()
    if not route:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patrol route not found")
    return _route_to_schema(route)
