"""
app/api/v1/endpoints/routing.py
───────────────────────────────
Patrol Route Optimization API — generate and retrieve optimized patrol routes.

Endpoints
─────────
POST /routing/generate    Generate a new optimized patrol route
GET  /routing             List patrol routes
GET  /routing/latest      Get the most recent route
GET  /routing/{route_id}  Get a specific route by ID
GET  /routing/summary     Get summary statistics
"""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.services.routing_service import RoutingService

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# Request / Response schemas
# ─────────────────────────────────────────────────────────────────────────────

class GenerateRouteRequest(BaseModel):
    """Input for POST /routing/generate."""

    route_date: date = Field(
        description="Date for which to generate the route"
    )
    shift_name: str = Field(
        default="default",
        description="Shift identifier (e.g., 'default', 'morning', 'evening')",
    )
    start_latitude: Optional[float] = Field(
        default=None,
        description="Optional starting latitude for the route",
    )
    start_longitude: Optional[float] = Field(
        default=None,
        description="Optional starting longitude for the route",
    )
    average_speed_kmph: float = Field(
        default=25.0,
        ge=5.0,
        le=100.0,
        description="Average travel speed in km/h (default 25)",
    )
    max_stops: Optional[int] = Field(
        default=None,
        ge=1,
        le=500,
        description="Maximum number of hotspot stops to include (None = all)",
    )
    use_two_opt: bool = Field(
        default=True,
        description="Whether to apply 2-opt optimization (default True)",
    )


class RouteStopResponse(BaseModel):
    """A single stop in a patrol route."""

    sequence: int
    hotspot_id: int
    hotspot_name: Optional[str]
    latitude: float
    longitude: float
    officers_allocated: int
    priority_rank: int
    risk_category: str
    allocation_id: Optional[int]
    dwell_time_minutes: int
    eis_snapshot: Optional[float]
    zone_id: Optional[str]


class RouteSummaryResponse(BaseModel):
    """Summary statistics for a route."""

    total_stops: int
    critical_stops: int
    high_stops: int
    total_officers: int
    total_distance_km: float
    estimated_travel_minutes: int
    estimated_total_minutes: int


class GenerateRouteResponse(BaseModel):
    """Response from POST /routing/generate."""

    route_id: int
    route_date: str
    shift_name: str
    total_stops: int
    critical_stops: int
    high_stops: int
    total_officers: int
    total_distance_km: float
    estimated_travel_minutes: int
    estimated_total_minutes: int
    route_geometry: List[Dict[str, float]]
    stops: List[Dict[str, Any]]
    summary: Dict[str, Any]


class ListRouteResponse(BaseModel):
    """A single route in a list response."""

    route_id: int
    route_name: Optional[str]
    shift_label: Optional[str]
    officer_count: int
    total_distance_km: Optional[float]
    estimated_duration_min: Optional[int]
    hotspots_covered: Optional[int]
    total_eis_covered: Optional[float]
    created_at: Optional[str]


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/generate",
    response_model=GenerateRouteResponse,
    summary="Generate a new optimized patrol route",
    status_code=status.HTTP_201_CREATED,
)
def generate_route(
    payload: GenerateRouteRequest,
    db: Session = Depends(db_session),
) -> Dict[str, Any]:
    """
    Generate an optimized patrol route from latest allocations.

    Steps:
      1. Fetch latest allocations for the given date and shift.
      2. Convert allocations + hotspots to routing stops.
      3. Optimize route order using nearest-neighbor + optional 2-opt.
      4. Calculate metrics (distance, travel time, dwell time).
      5. Persist route to database.
      6. Return complete route definition with geometry and stops.

    Returns:
        RouteResult with ordered stops, geometry, and metrics.
    """
    try:
        service = RoutingService(db)
        return service.generate_route(
            route_date=payload.route_date,
            shift_name=payload.shift_name,
            start_latitude=payload.start_latitude,
            start_longitude=payload.start_longitude,
            average_speed_kmph=payload.average_speed_kmph,
            max_stops=payload.max_stops,
            use_two_opt=payload.use_two_opt,
            commit=True,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Route generation failed: {exc}",
        ) from exc


@router.get(
    "",
    response_model=List[ListRouteResponse],
    summary="List all patrol routes",
)
def list_routes(
    route_date: Optional[date] = Query(default=None, description="Filter by route date"),
    shift_name: Optional[str] = Query(default=None, description="Filter by shift name"),
    limit: int = Query(default=100, ge=1, le=500, description="Max results"),
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
    db: Session = Depends(db_session),
) -> List[Dict[str, Any]]:
    """
    List patrol routes with optional filters.

    Supports filtering by route_date and shift_name, and pagination.

    Returns:
        List of route summaries.
    """
    service = RoutingService(db)
    return service.list_routes(
        route_date=route_date,
        shift_name=shift_name,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/",
    response_model=List[ListRouteResponse],
    summary="List all patrol routes (with trailing slash)",
)
def list_routes_with_slash(
    route_date: Optional[date] = Query(default=None, description="Filter by route date"),
    shift_name: Optional[str] = Query(default=None, description="Filter by shift name"),
    limit: int = Query(default=100, ge=1, le=500, description="Max results"),
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
    db: Session = Depends(db_session),
) -> List[Dict[str, Any]]:
    """List patrol routes (alternative endpoint with trailing slash)."""
    service = RoutingService(db)
    return service.list_routes(
        route_date=route_date,
        shift_name=shift_name,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/latest",
    response_model=ListRouteResponse,
    summary="Get the most recent patrol route",
)
def get_latest_route(
    db: Session = Depends(db_session),
) -> Dict[str, Any]:
    """
    Get the most recently generated patrol route.

    Returns:
        Latest route summary, or 404 if no routes exist.
    """
    service = RoutingService(db)
    route = service.get_latest_route()
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No routes found",
        )
    return route


@router.get(
    "/summary",
    summary="Get routing summary statistics",
)
def get_route_summary(
    db: Session = Depends(db_session),
) -> Dict[str, Any]:
    """
    Get high-level summary statistics for all patrol routes.

    Returns:
        Summary dict with aggregate metrics.
    """
    service = RoutingService(db)
    return service.get_summary()


@router.get(
    "/{route_id}",
    response_model=ListRouteResponse,
    summary="Get a specific patrol route by ID",
)
def get_route_by_id(
    route_id: int,
    db: Session = Depends(db_session),
) -> Dict[str, Any]:
    """
    Get a patrol route by its ID.

    Args:
        route_id: Route ID

    Returns:
        Route details, or 404 if not found.
    """
    try:
        service = RoutingService(db)
        return service.get_route_by_id(route_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
