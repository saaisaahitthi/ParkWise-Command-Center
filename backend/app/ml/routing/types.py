"""
app/ml/routing/types.py
───────────────────────
Data types for the Patrol Route Optimization Engine.

Defines immutable (frozen) request/input types and mutable result types
for geographic routing computations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class RouteStop:
    """
    A single stop on a patrol route.

    Represents a hotspot with geographic coordinates, officer allocation,
    and metadata for route optimization.
    """

    hotspot_id: int
    latitude: float
    longitude: float
    officers_allocated: int
    priority_rank: int
    risk_category: str
    hotspot_name: Optional[str] = None
    allocation_id: Optional[int] = None
    dwell_time_minutes: int = 10
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RouteRequest:
    """
    Configuration for route optimization.

    Specifies route parameters, optimization preferences, and constraints.
    """

    route_date: date
    shift_name: str = "default"
    start_latitude: Optional[float] = None
    start_longitude: Optional[float] = None
    average_speed_kmph: float = 25.0
    max_stops: Optional[int] = None
    use_two_opt: bool = True


@dataclass
class RouteSummary:
    """
    Summary statistics for an optimized route.

    Aggregates metrics about coverage, distance, and time.
    """

    total_stops: int
    critical_stops: int
    high_stops: int
    total_officers: int
    total_distance_km: float
    estimated_travel_minutes: int
    estimated_total_minutes: int


@dataclass
class RouteResult:
    """
    Output of route optimization.

    Contains the ordered stops, route geometry, and computed metrics.
    """

    ordered_stops: List[RouteStop]
    total_distance_km: float
    estimated_travel_minutes: int
    estimated_total_minutes: int
    route_geometry: List[Dict[str, float]]
    summary: RouteSummary
