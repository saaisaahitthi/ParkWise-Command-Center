"""
app/repositories/routing_repository.py
──────────────────────────────────────
Database persistence layer for patrol route optimization.

Handles reading allocations and hotspots, and writing generated routes
to the PatrolRoute table.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models.analytics import Allocation, PatrolRoute
from app.models.hotspot import Hotspot


class RoutingRepository:
    """Manage routing data persistence and queries."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_latest_allocations(
        self,
        limit: Optional[int] = None,
        allocation_date: Optional[datetime] = None,
        shift_name: Optional[str] = None,
    ) -> List[tuple[Allocation, Hotspot]]:
        """
        Fetch latest allocations joined with hotspot coordinates.

        Returns only allocations with officers_allocated > 0.
        Orders by priority_rank, then by officers_allocated descending.

        Args:
            limit: Max number of allocations to return
            allocation_date: Filter by allocation date (if provided)
            shift_name: Filter by shift name (if provided)

        Returns:
            List of (Allocation, Hotspot) tuples.
        """
        query = (
            self.db.query(Allocation, Hotspot)
            .join(Hotspot, Allocation.hotspot_id == Hotspot.id)
            .filter(Allocation.officers_allocated > 0)
            .order_by(Allocation.priority_rank.asc(), Allocation.officers_allocated.desc())
        )

        if allocation_date is not None:
            query = query.filter(
                func.date(Allocation.allocation_date) == allocation_date.date()
            )

        if limit is not None:
            query = query.limit(limit)

        return list(query.all())

    def create_patrol_route(
        self,
        route_date: datetime,
        shift_name: str,
        stops_json: List[Dict[str, Any]],
        total_distance_km: float,
        estimated_duration_min: int,
        total_stops: int,
        critical_stops: int,
        high_stops: int,
        route_geometry: Optional[Any] = None,
        pipeline_run_id: Optional[str] = None,
        commit: bool = True,
    ) -> PatrolRoute:
        """
        Create and persist a new PatrolRoute.

        Args:
            route_date: Date of the route
            shift_name: Shift name (e.g., "default", "morning", "evening")
            stops_json: Ordered list of stop objects with metadata
            total_distance_km: Total route distance
            estimated_duration_min: Total estimated duration in minutes
            total_stops: Total number of stops
            critical_stops: Count of critical-risk stops
            high_stops: Count of high-risk stops
            route_geometry: Optional WKT geometry (LINESTRING)
            pipeline_run_id: Optional pipeline run ID for traceability
            commit: Whether to commit immediately

        Returns:
            Created PatrolRoute instance.
        """
        route = PatrolRoute(
            route_name=f"{shift_name.title()} Shift - {route_date.date()}",
            shift_label=shift_name,
            officer_count=sum(s.get("officers_allocated", 0) for s in stops_json),
            stops_json=stops_json,
            total_distance_km=total_distance_km,
            estimated_duration_min=estimated_duration_min,
            hotspots_covered=total_stops,
            total_eis_covered=sum(s.get("eis_snapshot", 0.0) for s in stops_json),
            route_geometry=route_geometry,
            pipeline_run_id=pipeline_run_id,
            created_at=datetime.utcnow(),
        )
        self.db.add(route)

        if commit:
            self.db.commit()
            self.db.refresh(route)

        return route

    def list_routes(
        self,
        route_date: Optional[datetime] = None,
        shift_name: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[PatrolRoute]:
        """
        List patrol routes with optional filters.

        Args:
            route_date: Filter by route date
            shift_name: Filter by shift name
            limit: Max results
            offset: Offset for pagination

        Returns:
            List of PatrolRoute instances.
        """
        query = self.db.query(PatrolRoute)

        if route_date is not None:
            # Filter routes created on this date
            query = query.filter(
                func.date(PatrolRoute.created_at) == route_date.date()
            )

        if shift_name is not None:
            query = query.filter(PatrolRoute.shift_label == shift_name)

        query = query.order_by(desc(PatrolRoute.created_at))
        query = query.offset(offset).limit(limit)

        return list(query.all())

    def get_latest_route(self) -> Optional[PatrolRoute]:
        """
        Get the most recently created patrol route.

        Returns:
            PatrolRoute instance or None if none exist.
        """
        return self.db.query(PatrolRoute).order_by(desc(PatrolRoute.created_at)).first()

    def get_route_by_id(self, route_id: int) -> Optional[PatrolRoute]:
        """
        Get a patrol route by ID.

        Args:
            route_id: Route ID

        Returns:
            PatrolRoute instance or None if not found.
        """
        return self.db.query(PatrolRoute).filter(PatrolRoute.id == route_id).first()

    def get_summary(self) -> Dict[str, Any]:
        """
        Get high-level summary statistics for all routes.

        Returns:
            Dict with counts and aggregate metrics.
        """
        total_routes = self.db.query(func.count(PatrolRoute.id)).scalar() or 0
        avg_distance = self.db.query(func.avg(PatrolRoute.total_distance_km)).scalar() or 0.0
        avg_duration = self.db.query(func.avg(PatrolRoute.estimated_duration_min)).scalar() or 0
        avg_stops = self.db.query(func.avg(PatrolRoute.hotspots_covered)).scalar() or 0

        return {
            "total_routes": total_routes,
            "average_distance_km": round(float(avg_distance), 2),
            "average_duration_min": int(avg_duration) if avg_duration else 0,
            "average_stops_per_route": round(float(avg_stops), 1) if avg_stops else 0,
        }
