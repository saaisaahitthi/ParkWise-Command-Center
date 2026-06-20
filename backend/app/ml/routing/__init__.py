"""
app/ml/routing/__init__.py
──────────────────────────
Public API for the Patrol Route Optimization Engine.

Exports core types and optimization classes for route building,
distance calculations, and geometric optimization.
"""

from app.ml.routing.distance import (
    estimate_travel_minutes,
    haversine_distance_km,
    route_distance_km,
)
from app.ml.routing.optimizer import PatrolRouteOptimizer
from app.ml.routing.route_builder import PatrolRouteBuilder
from app.ml.routing.types import (
    RouteRequest,
    RouteResult,
    RouteStop,
    RouteSummary,
)

__all__ = [
    # Types
    "RouteStop",
    "RouteRequest",
    "RouteResult",
    "RouteSummary",
    # Distance functions
    "haversine_distance_km",
    "route_distance_km",
    "estimate_travel_minutes",
    # Optimizers and builders
    "PatrolRouteOptimizer",
    "PatrolRouteBuilder",
]
