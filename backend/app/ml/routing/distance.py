"""
app/ml/routing/distance.py
──────────────────────────
Distance and travel time calculations for route optimization.

Pure functions for geographic distance metrics. No database or external
dependencies. All calculations use the Haversine formula for great-circle
distances on Earth.
"""

from __future__ import annotations

import math
from typing import List, Optional

from app.ml.routing.types import RouteStop


def haversine_distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """
    Compute great-circle distance between two points using Haversine formula.

    Args:
        lat1: Latitude of first point (degrees)
        lon1: Longitude of first point (degrees)
        lat2: Latitude of second point (degrees)
        lon2: Longitude of second point (degrees)

    Returns:
        Distance in kilometers, rounded to 3 decimal places.
    """
    if not all(isinstance(x, (int, float)) for x in [lat1, lon1, lat2, lon2]):
        raise ValueError("All coordinates must be numeric")

    if not (-90 <= lat1 <= 90 and -180 <= lon1 <= 180):
        raise ValueError(f"Invalid first point: lat={lat1}, lon={lon1}")
    if not (-90 <= lat2 <= 90 and -180 <= lon2 <= 180):
        raise ValueError(f"Invalid second point: lat={lat2}, lon={lon2}")

    # Earth radius in kilometers
    R = 6371.0

    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    distance = R * c

    return round(distance, 3)


def route_distance_km(
    stops: List[RouteStop],
    start_latitude: Optional[float] = None,
    start_longitude: Optional[float] = None,
) -> float:
    """
    Compute total distance for a sequence of stops.

    If start_latitude and start_longitude are provided, distance is computed
    from start → stop[0] → stop[1] → ... → stop[n-1].

    Otherwise, distance is stop[0] → stop[1] → ... → stop[n-1].

    Args:
        stops: Ordered list of RouteStop objects
        start_latitude: Optional starting latitude
        start_longitude: Optional starting longitude

    Returns:
        Total distance in kilometers, rounded to 3 decimal places.
    """
    if not stops:
        return 0.0

    total_distance = 0.0

    # Include start point if provided
    if start_latitude is not None and start_longitude is not None:
        total_distance += haversine_distance_km(
            start_latitude,
            start_longitude,
            stops[0].latitude,
            stops[0].longitude,
        )
        prev_stop = stops[0]
    else:
        prev_stop = stops[0]

    # Sum distances between consecutive stops
    for i in range(1, len(stops)):
        curr_stop = stops[i]
        total_distance += haversine_distance_km(
            prev_stop.latitude,
            prev_stop.longitude,
            curr_stop.latitude,
            curr_stop.longitude,
        )
        prev_stop = curr_stop

    return round(total_distance, 3)


def estimate_travel_minutes(
    distance_km: float,
    average_speed_kmph: float = 25.0,
) -> int:
    """
    Estimate travel time based on distance and average speed.

    Args:
        distance_km: Distance in kilometers
        average_speed_kmph: Average speed in km/h (default 25)

    Returns:
        Estimated travel time in minutes (rounded down).
    """
    if distance_km < 0:
        raise ValueError("distance_km must be non-negative")
    if average_speed_kmph <= 0:
        raise ValueError("average_speed_kmph must be positive")

    travel_hours = distance_km / average_speed_kmph
    travel_minutes = travel_hours * 60
    return int(travel_minutes)
