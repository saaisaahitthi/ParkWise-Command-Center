"""
app/services/routing_service.py
───────────────────────────────
Patrol route generation and management service.

Orchestrates route optimization by loading allocations, converting to stops,
building optimized routes, and persisting results.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.ml.routing import (
    PatrolRouteBuilder,
    PatrolRouteOptimizer,
    RouteRequest,
    RouteStop,
)
from app.repositories.routing_repository import RoutingRepository


class RoutingService:
    """Generate and manage patrol routes from allocations."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = RoutingRepository(db)

    def generate_route(
        self,
        route_date: date,
        shift_name: str = "default",
        start_latitude: Optional[float] = None,
        start_longitude: Optional[float] = None,
        average_speed_kmph: float = 25.0,
        max_stops: Optional[int] = None,
        use_two_opt: bool = True,
        commit: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate an optimized patrol route from latest allocations.

        Flow:
          1. Fetch latest allocations for the given date/shift.
          2. Convert to RouteStop objects.
          3. Optimize using nearest-neighbor + optional 2-opt.
          4. Build route result with geometry and metrics.
          5. Persist to database.
          6. Return dashboard-ready output.

        Args:
            route_date: Date for which to generate the route
            shift_name: Shift identifier (default "default")
            start_latitude: Optional starting latitude
            start_longitude: Optional starting longitude
            average_speed_kmph: Average speed for travel time estimation (default 25)
            max_stops: Max hotspots to include (None = all)
            use_two_opt: Whether to apply 2-opt optimization (default True)
            commit: Whether to persist immediately (default True)

        Returns:
            Dict with route_id, coordinates, metrics, and summary.

        Raises:
            ValueError: If no allocations found or invalid parameters.
        """
        # Build RouteRequest
        request = RouteRequest(
            route_date=route_date,
            shift_name=shift_name,
            start_latitude=start_latitude,
            start_longitude=start_longitude,
            average_speed_kmph=average_speed_kmph,
            max_stops=max_stops,
            use_two_opt=use_two_opt,
        )

        # Fetch allocations and hotspots
        allocation_rows = self.repository.get_latest_allocations(
            limit=max_stops,
            allocation_date=datetime.combine(route_date, datetime.min.time()),
            shift_name=shift_name,
        )

        if not allocation_rows:
            raise ValueError(
                f"No allocations found for {route_date} shift '{shift_name}'. "
                "Run allocation engine first."
            )

        # Convert to RouteStop objects
        stops = self._allocations_to_stops(allocation_rows)

        # Optimize route order
        optimizer = PatrolRouteOptimizer()
        optimized_stops = optimizer.optimize(
            stops,
            start_latitude=start_latitude,
            start_longitude=start_longitude,
            use_two_opt=use_two_opt,
        )

        # Build route result with geometry and metrics
        builder = PatrolRouteBuilder()
        route_result = builder.build_route(optimized_stops, request)

        # Convert stops to JSON-serializable format
        stops_json = self._stops_to_json(optimized_stops)

        # Persist route
        db_route = self.repository.create_patrol_route(
            route_date=datetime.combine(route_date, datetime.min.time()),
            shift_name=shift_name,
            stops_json=stops_json,
            total_distance_km=route_result.total_distance_km,
            estimated_duration_min=route_result.estimated_total_minutes,
            total_stops=route_result.summary.total_stops,
            critical_stops=route_result.summary.critical_stops,
            high_stops=route_result.summary.high_stops,
            pipeline_run_id=None,
            commit=commit,
        )

        # Return dashboard-ready output
        return {
            "route_id": db_route.id,
            "route_date": str(route_date),
            "shift_name": shift_name,
            "total_stops": route_result.summary.total_stops,
            "critical_stops": route_result.summary.critical_stops,
            "high_stops": route_result.summary.high_stops,
            "total_officers": route_result.summary.total_officers,
            "total_distance_km": round(route_result.total_distance_km, 2),
            "estimated_travel_minutes": route_result.estimated_travel_minutes,
            "estimated_total_minutes": route_result.estimated_total_minutes,
            "route_geometry": route_result.route_geometry,
            "stops": stops_json,
            "summary": {
                "total_stops": route_result.summary.total_stops,
                "critical_stops": route_result.summary.critical_stops,
                "high_stops": route_result.summary.high_stops,
                "total_officers": route_result.summary.total_officers,
                "total_distance_km": round(route_result.total_distance_km, 2),
                "estimated_travel_minutes": route_result.estimated_travel_minutes,
                "estimated_total_minutes": route_result.estimated_total_minutes,
            },
        }

    def list_routes(
        self,
        route_date: Optional[date] = None,
        shift_name: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        List patrol routes with optional filters.

        Args:
            route_date: Filter by route date
            shift_name: Filter by shift name
            limit: Max results (default 100)
            offset: Pagination offset (default 0)

        Returns:
            List of route dicts.
        """
        route_datetime = (
            datetime.combine(route_date, datetime.min.time())
            if route_date
            else None
        )

        routes = self.repository.list_routes(
            route_date=route_datetime,
            shift_name=shift_name,
            limit=limit,
            offset=offset,
        )

        return [self._route_to_dict(r) for r in routes]

    def get_latest_route(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recently generated route.

        Returns:
            Route dict or None if no routes exist.
        """
        route = self.repository.get_latest_route()
        return self._route_to_dict(route) if route else None

    def get_route_by_id(self, route_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a patrol route by ID.

        Args:
            route_id: Route ID

        Returns:
            Route dict or None if not found.

        Raises:
            ValueError: If route_id not found.
        """
        route = self.repository.get_route_by_id(route_id)
        if not route:
            raise ValueError(f"Route {route_id} not found")
        return self._route_to_dict(route)

    def get_summary(self) -> Dict[str, Any]:
        """
        Get high-level summary statistics.

        Returns:
            Summary dict with aggregate metrics.
        """
        return self.repository.get_summary()

    # ── Private helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _allocations_to_stops(
        allocation_rows: List[tuple],
    ) -> List[RouteStop]:
        """
        Convert (Allocation, Hotspot) tuples to RouteStop objects.

        Args:
            allocation_rows: List of (Allocation, Hotspot) tuples

        Returns:
            List of RouteStop instances.
        """
        stops = []
        for allocation, hotspot in allocation_rows:
            stop = RouteStop(
                hotspot_id=hotspot.id,
                latitude=hotspot.centroid_lat,
                longitude=hotspot.centroid_lon,
                officers_allocated=allocation.officers_allocated,
                priority_rank=allocation.priority_rank,
                risk_category=allocation.risk_category or "Medium",
                hotspot_name=hotspot.hotspot_name,
                allocation_id=allocation.id,
                dwell_time_minutes=10,
                metadata={
                    "eis_snapshot": allocation.eis_snapshot,
                    "zone_id": hotspot.zone_id,
                },
            )
            stops.append(stop)
        return stops

    @staticmethod
    def _stops_to_json(stops: List[RouteStop]) -> List[Dict[str, Any]]:
        """
        Convert RouteStop objects to JSON-serializable dicts.

        Args:
            stops: List of RouteStop instances

        Returns:
            List of dicts suitable for JSONB storage.
        """
        result = []
        for seq, stop in enumerate(stops, start=1):
            result.append({
                "sequence": seq,
                "hotspot_id": stop.hotspot_id,
                "hotspot_name": stop.hotspot_name,
                "latitude": stop.latitude,
                "longitude": stop.longitude,
                "officers_allocated": stop.officers_allocated,
                "priority_rank": stop.priority_rank,
                "risk_category": stop.risk_category,
                "allocation_id": stop.allocation_id,
                "dwell_time_minutes": stop.dwell_time_minutes,
                "eis_snapshot": stop.metadata.get("eis_snapshot"),
                "zone_id": stop.metadata.get("zone_id"),
            })
        return result

    @staticmethod
    def _route_to_dict(route: Any) -> Dict[str, Any]:
        """
        Convert a PatrolRoute model to a dict.

        Args:
            route: PatrolRoute ORM instance

        Returns:
            Dict representation for API response.
        """
        return {
            "route_id": route.id,
            "route_name": route.route_name,
            "shift_label": route.shift_label,
            "officer_count": route.officer_count,
            "total_distance_km": route.total_distance_km,
            "estimated_duration_min": route.estimated_duration_min,
            "hotspots_covered": route.hotspots_covered,
            "total_eis_covered": route.total_eis_covered,
            "stops": route.stops_json or [],
            "created_at": route.created_at.isoformat() if route.created_at else None,
        }
