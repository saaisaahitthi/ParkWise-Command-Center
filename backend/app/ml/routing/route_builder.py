"""
app/ml/routing/route_builder.py
───────────────────────────────
Constructs RouteResult from optimized stops.

Converts a sequence of ordered stops into a complete route representation
with geometry, metrics, and summary statistics.
"""

from __future__ import annotations

from typing import Dict, List

from app.ml.routing.distance import estimate_travel_minutes, route_distance_km
from app.ml.routing.types import RouteRequest, RouteResult, RouteSummary, RouteStop


class PatrolRouteBuilder:
    """
    Builds a complete RouteResult from optimized stops and a route request.

    Computes geometry, metrics, and summary statistics for visualization
    and analysis.
    """

    @staticmethod
    def build_route(
        stops: List[RouteStop],
        request: RouteRequest,
    ) -> RouteResult:
        """
        Build a complete RouteResult from ordered stops.

        Computes total distance, travel time, dwell time at each stop,
        creates route geometry as a list of coordinates, and builds summary.

        Args:
            stops: Ordered list of RouteStop objects
            request: RouteRequest with optimization parameters

        Returns:
            RouteResult with complete route definition and metrics.
        """
        if not stops:
            return PatrolRouteBuilder._empty_route()

        # Compute total distance
        total_distance_km = route_distance_km(
            stops,
            request.start_latitude,
            request.start_longitude,
        )

        # Compute travel time
        estimated_travel_minutes = estimate_travel_minutes(
            total_distance_km,
            request.average_speed_kmph,
        )

        # Compute total dwell time (sum of dwell_time_minutes for each stop)
        total_dwell_minutes = sum(stop.dwell_time_minutes for stop in stops)

        # Total time is travel + dwell
        estimated_total_minutes = estimated_travel_minutes + total_dwell_minutes

        # Build route geometry as list of coordinates
        route_geometry = PatrolRouteBuilder._build_geometry(
            stops,
            request.start_latitude,
            request.start_longitude,
        )

        # Build summary
        summary = PatrolRouteBuilder._build_summary(stops, total_distance_km, estimated_travel_minutes, estimated_total_minutes)

        return RouteResult(
            ordered_stops=stops,
            total_distance_km=total_distance_km,
            estimated_travel_minutes=estimated_travel_minutes,
            estimated_total_minutes=estimated_total_minutes,
            route_geometry=route_geometry,
            summary=summary,
        )

    @staticmethod
    def _build_geometry(
        stops: List[RouteStop],
        start_latitude: float | None,
        start_longitude: float | None,
    ) -> List[Dict[str, float]]:
        """
        Create route geometry as a JSON-compatible list of coordinates.

        Args:
            stops: Ordered list of RouteStop objects
            start_latitude: Optional starting latitude
            start_longitude: Optional starting longitude

        Returns:
            List of {"lat": ..., "lng": ...} dicts, starting with start point if provided.
        """
        geometry = []

        # Add start point if provided
        if start_latitude is not None and start_longitude is not None:
            geometry.append({"lat": start_latitude, "lng": start_longitude})

        # Add all stops
        for stop in stops:
            geometry.append({"lat": stop.latitude, "lng": stop.longitude})

        return geometry

    @staticmethod
    def _build_summary(
        stops: List[RouteStop],
        total_distance_km: float,
        estimated_travel_minutes: int,
        estimated_total_minutes: int,
    ) -> RouteSummary:
        """
        Build a RouteSummary from stops and metrics.

        Args:
            stops: Ordered list of RouteStop objects
            total_distance_km: Total route distance in km
            estimated_travel_minutes: Travel time in minutes
            estimated_total_minutes: Total time (travel + dwell) in minutes

        Returns:
            RouteSummary with aggregated statistics.
        """
        critical_stops = sum(
            1 for stop in stops if stop.risk_category == "Critical"
        )
        high_stops = sum(
            1 for stop in stops if stop.risk_category == "High"
        )
        total_officers = sum(stop.officers_allocated for stop in stops)

        return RouteSummary(
            total_stops=len(stops),
            critical_stops=critical_stops,
            high_stops=high_stops,
            total_officers=total_officers,
            total_distance_km=total_distance_km,
            estimated_travel_minutes=estimated_travel_minutes,
            estimated_total_minutes=estimated_total_minutes,
        )

    @staticmethod
    def _empty_route() -> RouteResult:
        """
        Return an empty RouteResult.

        Used when no stops are provided.
        """
        empty_summary = RouteSummary(
            total_stops=0,
            critical_stops=0,
            high_stops=0,
            total_officers=0,
            total_distance_km=0.0,
            estimated_travel_minutes=0,
            estimated_total_minutes=0,
        )

        return RouteResult(
            ordered_stops=[],
            total_distance_km=0.0,
            estimated_travel_minutes=0,
            estimated_total_minutes=0,
            route_geometry=[],
            summary=empty_summary,
        )
