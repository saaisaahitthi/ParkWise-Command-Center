"""
app/ml/routing/optimizer.py
───────────────────────────
Geographic route optimization using nearest neighbor and 2-opt algorithms.

Pure functions for deterministic route ordering. Operates only on geographic
coordinates and distance metrics. No database or external dependencies.
"""

from __future__ import annotations

from typing import List, Optional

from app.ml.routing.distance import haversine_distance_km
from app.ml.routing.types import RouteStop


class PatrolRouteOptimizer:
    """
    Optimizes patrol routes using greedy nearest-neighbor and optional 2-opt improvement.

    Maintains deterministic output for reproducible routes.
    """

    @staticmethod
    def nearest_neighbor_route(
        stops: List[RouteStop],
        start_latitude: Optional[float] = None,
        start_longitude: Optional[float] = None,
    ) -> List[RouteStop]:
        """
        Greedy nearest-neighbor heuristic for route construction.

        Starting from a given point (or the first stop if not provided),
        at each step select the nearest unvisited stop.

        Args:
            stops: List of RouteStop objects to order
            start_latitude: Optional starting latitude
            start_longitude: Optional starting longitude

        Returns:
            Ordered list of RouteStop objects.
        """
        if not stops:
            return []
        if len(stops) == 1:
            return stops

        # Determine starting position
        if start_latitude is not None and start_longitude is not None:
            current_lat, current_lon = start_latitude, start_longitude
        else:
            # Start from first stop (or highest priority)
            current_lat = stops[0].latitude
            current_lon = stops[0].longitude

        visited = set()
        ordered = []

        # Handle first stop if no external start point
        if start_latitude is None or start_longitude is None:
            ordered.append(stops[0])
            visited.add(0)

        # Greedily select nearest unvisited stop
        while len(visited) < len(stops):
            nearest_idx = -1
            nearest_dist = float("inf")

            for i, stop in enumerate(stops):
                if i in visited:
                    continue

                dist = haversine_distance_km(
                    current_lat,
                    current_lon,
                    stop.latitude,
                    stop.longitude,
                )

                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest_idx = i

            if nearest_idx != -1:
                ordered.append(stops[nearest_idx])
                visited.add(nearest_idx)
                current_lat = stops[nearest_idx].latitude
                current_lon = stops[nearest_idx].longitude

        return ordered

    @staticmethod
    def two_opt(
        stops: List[RouteStop],
        start_latitude: Optional[float] = None,
        start_longitude: Optional[float] = None,
        max_iterations: int = 100,
    ) -> List[RouteStop]:
        """
        Apply 2-opt local search improvement to a route.

        Iteratively reverses sub-routes to reduce total distance.

        Args:
            stops: Ordered list of RouteStop objects
            start_latitude: Optional starting latitude
            start_longitude: Optional starting longitude
            max_iterations: Maximum number of improvement attempts

        Returns:
            Improved (or original) list of RouteStop objects.
        """
        if len(stops) <= 2:
            return stops

        route = list(stops)
        improved = True
        iteration = 0

        while improved and iteration < max_iterations:
            improved = False
            iteration += 1

            for i in range(len(route) - 1):
                for j in range(i + 2, len(route)):
                    # Calculate current segment distances
                    i_next = (i + 1) % len(route)
                    j_next = (j + 1) % len(route)

                    # Use start point for edge calculations if needed
                    if i == 0 and start_latitude is not None:
                        dist_a1 = haversine_distance_km(
                            start_latitude,
                            start_longitude,
                            route[i].latitude,
                            route[i].longitude,
                        )
                    else:
                        dist_a1 = haversine_distance_km(
                            route[i].latitude,
                            route[i].longitude,
                            route[i_next].latitude,
                            route[i_next].longitude,
                        )

                    dist_b1 = haversine_distance_km(
                        route[j].latitude,
                        route[j].longitude,
                        route[j_next].latitude if j_next < len(route) else start_latitude or 0,
                        route[j_next].longitude if j_next < len(route) else start_longitude or 0,
                    )

                    # Calculate new segment distances if we reverse
                    if i == 0 and start_latitude is not None:
                        dist_a2 = haversine_distance_km(
                            start_latitude,
                            start_longitude,
                            route[j].latitude,
                            route[j].longitude,
                        )
                    else:
                        dist_a2 = haversine_distance_km(
                            route[i].latitude,
                            route[i].longitude,
                            route[j].latitude,
                            route[j].longitude,
                        )

                    dist_b2 = haversine_distance_km(
                        route[i_next].latitude,
                        route[i_next].longitude,
                        route[j_next].latitude if j_next < len(route) else start_latitude or 0,
                        route[j_next].longitude if j_next < len(route) else start_longitude or 0,
                    )

                    # If 2-opt swap improves, apply it
                    if dist_a1 + dist_b1 > dist_a2 + dist_b2:
                        route[i_next : j + 1] = reversed(route[i_next : j + 1])
                        improved = True

        return route

    @staticmethod
    def optimize(
        stops: List[RouteStop],
        start_latitude: Optional[float] = None,
        start_longitude: Optional[float] = None,
        use_two_opt: bool = True,
    ) -> List[RouteStop]:
        """
        Optimize route order using nearest-neighbor and optional 2-opt.

        Args:
            stops: List of RouteStop objects to order
            start_latitude: Optional starting latitude
            start_longitude: Optional starting longitude
            use_two_opt: Whether to apply 2-opt improvement

        Returns:
            Optimized list of RouteStop objects.
        """
        if not stops:
            return []
        if len(stops) == 1:
            return stops

        # Start with nearest-neighbor greedy construction
        route = PatrolRouteOptimizer.nearest_neighbor_route(
            stops,
            start_latitude,
            start_longitude,
        )

        # Apply 2-opt if requested
        if use_two_opt and len(route) > 2:
            route = PatrolRouteOptimizer.two_opt(
                route,
                start_latitude,
                start_longitude,
            )

        return route
