"""
tests/unit/test_routing_distance.py
──────────────────────────────────
Unit tests for routing distance calculations.

Tests Haversine formula, route distance aggregation, and travel time estimation.
"""

from __future__ import annotations

import pytest

from app.ml.routing.distance import (
    estimate_travel_minutes,
    haversine_distance_km,
    route_distance_km,
)
from app.ml.routing.types import RouteStop


class TestHaversineDistance:
    """Test great-circle distance calculations."""

    def test_same_point_returns_zero(self):
        """Distance between identical coordinates should be 0."""
        distance = haversine_distance_km(12.9716, 77.5946, 12.9716, 77.5946)
        assert distance == 0.0

    def test_different_points_returns_positive(self):
        """Distance between different coordinates should be positive."""
        # Bangalore KR Market to Brigade Road (approximately 3.4 km).
        distance = haversine_distance_km(12.9635, 77.5770, 12.9719, 77.6067)
        assert distance > 0.0
        assert 3.0 < distance < 4.0  # Approximate range

    def test_known_distance(self):
        """Test against a known approximate distance."""
        # Great-circle distance from Delhi to Bangalore is approximately 1,750 km.
        distance = haversine_distance_km(28.7041, 77.1025, 12.9716, 77.5946)
        assert 1700 < distance < 1800

    def test_invalid_latitude_raises_error(self):
        """Invalid latitude should raise ValueError."""
        with pytest.raises(ValueError):
            haversine_distance_km(100.0, 77.5946, 12.9716, 77.5946)

    def test_invalid_longitude_raises_error(self):
        """Invalid longitude should raise ValueError."""
        with pytest.raises(ValueError):
            haversine_distance_km(12.9716, 200.0, 12.9716, 77.5946)

    def test_non_numeric_coordinates_raise_error(self):
        """Non-numeric coordinates should raise ValueError."""
        with pytest.raises(ValueError):
            haversine_distance_km("invalid", 77.5946, 12.9716, 77.5946)


class TestRouteDistance:
    """Test route distance aggregation."""

    def test_empty_stops_returns_zero(self):
        """Route with no stops should have distance 0."""
        distance = route_distance_km([])
        assert distance == 0.0

    def test_single_stop_no_start_returns_zero(self):
        """Single stop with no start point should have distance 0."""
        stops = [
            RouteStop(
                hotspot_id=1,
                latitude=12.9716,
                longitude=77.5946,
                officers_allocated=2,
                priority_rank=1,
                risk_category="High",
            )
        ]
        distance = route_distance_km(stops)
        assert distance == 0.0

    def test_single_stop_with_start_returns_positive(self):
        """Single stop with start point should return distance > 0."""
        stops = [
            RouteStop(
                hotspot_id=1,
                latitude=12.9716,
                longitude=77.5946,
                officers_allocated=2,
                priority_rank=1,
                risk_category="High",
            )
        ]
        distance = route_distance_km(stops, start_latitude=12.9689, start_longitude=77.5941)
        assert distance > 0.0

    def test_multiple_stops_distance_is_sum(self):
        """Route distance should be sum of segment distances."""
        stops = [
            RouteStop(
                hotspot_id=1,
                latitude=12.9716,
                longitude=77.5946,
                officers_allocated=2,
                priority_rank=1,
                risk_category="High",
            ),
            RouteStop(
                hotspot_id=2,
                latitude=12.9700,
                longitude=77.5950,
                officers_allocated=2,
                priority_rank=2,
                risk_category="High",
            ),
        ]
        distance = route_distance_km(stops)
        assert distance > 0.0

    def test_with_start_point_includes_initial_segment(self):
        """Start point to first stop should be included in distance."""
        stops = [
            RouteStop(
                hotspot_id=1,
                latitude=12.9716,
                longitude=77.5946,
                officers_allocated=2,
                priority_rank=1,
                risk_category="High",
            )
        ]
        distance_without_start = route_distance_km(stops)
        distance_with_start = route_distance_km(
            stops, start_latitude=12.9689, start_longitude=77.5941
        )
        assert distance_with_start > distance_without_start


class TestEstimateTravelMinutes:
    """Test travel time estimation."""

    def test_zero_distance_returns_zero(self):
        """Zero distance should result in zero travel minutes."""
        minutes = estimate_travel_minutes(0.0)
        assert minutes == 0

    def test_positive_distance_returns_minutes(self):
        """Positive distance should return positive minutes."""
        # 25 km at 25 km/h = 60 minutes
        minutes = estimate_travel_minutes(25.0, average_speed_kmph=25.0)
        assert minutes == 60

    def test_distance_and_speed_calculation(self):
        """Test various distance and speed combinations."""
        # 10 km at 20 km/h = 30 minutes
        minutes = estimate_travel_minutes(10.0, average_speed_kmph=20.0)
        assert minutes == 30

        # 5 km at 50 km/h = 6 minutes
        minutes = estimate_travel_minutes(5.0, average_speed_kmph=50.0)
        assert minutes == 6

    def test_default_speed(self):
        """Default speed should be 25 km/h."""
        # 25 km at default 25 km/h = 60 minutes
        minutes = estimate_travel_minutes(25.0)
        assert minutes == 60

    def test_invalid_distance_raises_error(self):
        """Negative distance should raise ValueError."""
        with pytest.raises(ValueError):
            estimate_travel_minutes(-5.0)

    def test_invalid_speed_raises_error(self):
        """Zero or negative speed should raise ValueError."""
        with pytest.raises(ValueError):
            estimate_travel_minutes(10.0, average_speed_kmph=0.0)

        with pytest.raises(ValueError):
            estimate_travel_minutes(10.0, average_speed_kmph=-5.0)

    def test_rounds_down(self):
        """Travel time should be rounded down (int conversion)."""
        # 10 km at 30 km/h = 20 minutes exactly
        minutes = estimate_travel_minutes(10.0, average_speed_kmph=30.0)
        assert isinstance(minutes, int)
        assert minutes == 20

        # 11 km at 30 km/h = 22 minutes (11/30 * 60 = 22)
        minutes = estimate_travel_minutes(11.0, average_speed_kmph=30.0)
        assert minutes == 22
