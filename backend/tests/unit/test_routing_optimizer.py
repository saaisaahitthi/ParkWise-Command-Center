"""
tests/unit/test_routing_optimizer.py
───────────────────────────────────
Unit tests for route optimization algorithms.

Tests nearest-neighbor, 2-opt, and combined optimization behavior.
"""

from __future__ import annotations

import pytest

from app.ml.routing.distance import route_distance_km
from app.ml.routing.optimizer import PatrolRouteOptimizer
from app.ml.routing.types import RouteStop


class TestNearestNeighbor:
    """Test nearest-neighbor greedy heuristic."""

    def test_empty_stops_returns_empty(self):
        """Empty stop list should return empty."""
        result = PatrolRouteOptimizer.nearest_neighbor_route([])
        assert result == []

    def test_single_stop_returns_same(self):
        """Single stop should return unchanged."""
        stop = RouteStop(
            hotspot_id=1,
            latitude=12.9716,
            longitude=77.5946,
            officers_allocated=2,
            priority_rank=1,
            risk_category="High",
        )
        result = PatrolRouteOptimizer.nearest_neighbor_route([stop])
        assert len(result) == 1
        assert result[0].hotspot_id == 1

    def test_two_stops_returns_both(self):
        """Two stops should both be returned."""
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
                risk_category="Medium",
            ),
        ]
        result = PatrolRouteOptimizer.nearest_neighbor_route(stops)
        assert len(result) == 2
        ids = {s.hotspot_id for s in result}
        assert ids == {1, 2}

    def test_result_contains_all_stops_exactly_once(self):
        """Result should contain all input stops exactly once."""
        stops = [
            RouteStop(
                hotspot_id=i,
                latitude=12.9716 + i * 0.001,
                longitude=77.5946 + i * 0.001,
                officers_allocated=2,
                priority_rank=i,
                risk_category="High",
            )
            for i in range(5)
        ]
        result = PatrolRouteOptimizer.nearest_neighbor_route(stops)
        assert len(result) == len(stops)
        ids = [s.hotspot_id for s in result]
        assert sorted(ids) == sorted([s.hotspot_id for s in stops])

    def test_deterministic_output(self):
        """Same input should produce same output."""
        stops = [
            RouteStop(
                hotspot_id=i,
                latitude=12.9716 + i * 0.001,
                longitude=77.5946 + i * 0.001,
                officers_allocated=2,
                priority_rank=i,
                risk_category="High",
            )
            for i in range(5)
        ]
        result1 = PatrolRouteOptimizer.nearest_neighbor_route(stops)
        result2 = PatrolRouteOptimizer.nearest_neighbor_route(stops)
        ids1 = [s.hotspot_id for s in result1]
        ids2 = [s.hotspot_id for s in result2]
        assert ids1 == ids2


class TestTwoOpt:
    """Test 2-opt local search improvement."""

    def test_empty_stops_returns_empty(self):
        """Empty stop list should return empty."""
        result = PatrolRouteOptimizer.two_opt([])
        assert result == []

    def test_single_stop_returns_same(self):
        """Single stop should return unchanged."""
        stop = RouteStop(
            hotspot_id=1,
            latitude=12.9716,
            longitude=77.5946,
            officers_allocated=2,
            priority_rank=1,
            risk_category="High",
        )
        result = PatrolRouteOptimizer.two_opt([stop])
        assert len(result) == 1

    def test_two_stops_returns_both(self):
        """Two stops should return both unchanged."""
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
                risk_category="Medium",
            ),
        ]
        result = PatrolRouteOptimizer.two_opt(stops)
        assert len(result) == 2

    def test_result_never_increases_distance(self):
        """2-opt should never increase total route distance."""
        stops = [
            RouteStop(
                hotspot_id=i,
                latitude=12.9716 + i * 0.001,
                longitude=77.5946 + i * 0.001,
                officers_allocated=2,
                priority_rank=i,
                risk_category="High",
            )
            for i in range(5)
        ]
        original_distance = route_distance_km(stops)
        improved = PatrolRouteOptimizer.two_opt(stops)
        improved_distance = route_distance_km(improved)
        assert improved_distance <= original_distance + 0.01  # Allow small rounding error


class TestOptimize:
    """Test combined optimization workflow."""

    def test_empty_stops_returns_empty(self):
        """Empty stop list should return empty."""
        result = PatrolRouteOptimizer.optimize([])
        assert result == []

    def test_single_stop_returns_same(self):
        """Single stop should return unchanged."""
        stop = RouteStop(
            hotspot_id=1,
            latitude=12.9716,
            longitude=77.5946,
            officers_allocated=2,
            priority_rank=1,
            risk_category="High",
        )
        result = PatrolRouteOptimizer.optimize([stop])
        assert len(result) == 1
        assert result[0].hotspot_id == 1

    def test_result_contains_all_stops(self):
        """Result should contain all input stops."""
        stops = [
            RouteStop(
                hotspot_id=i,
                latitude=12.9716 + i * 0.001,
                longitude=77.5946 + i * 0.001,
                officers_allocated=2,
                priority_rank=i,
                risk_category="High",
            )
            for i in range(5)
        ]
        result = PatrolRouteOptimizer.optimize(stops)
        assert len(result) == len(stops)
        ids = {s.hotspot_id for s in result}
        assert ids == {s.hotspot_id for s in stops}

    def test_deterministic_output(self):
        """Same input should produce same output."""
        stops = [
            RouteStop(
                hotspot_id=i,
                latitude=12.9716 + i * 0.001,
                longitude=77.5946 + i * 0.001,
                officers_allocated=2,
                priority_rank=i,
                risk_category="High",
            )
            for i in range(5)
        ]
        result1 = PatrolRouteOptimizer.optimize(stops)
        result2 = PatrolRouteOptimizer.optimize(stops)
        ids1 = [s.hotspot_id for s in result1]
        ids2 = [s.hotspot_id for s in result2]
        assert ids1 == ids2

    def test_with_start_point(self):
        """Optimization with start point should work."""
        stops = [
            RouteStop(
                hotspot_id=i,
                latitude=12.9716 + i * 0.001,
                longitude=77.5946 + i * 0.001,
                officers_allocated=2,
                priority_rank=i,
                risk_category="High",
            )
            for i in range(3)
        ]
        result = PatrolRouteOptimizer.optimize(
            stops,
            start_latitude=12.9680,
            start_longitude=77.5920,
            use_two_opt=True,
        )
        assert len(result) == len(stops)

    def test_two_opt_disabled(self):
        """Optimization with use_two_opt=False should only use nearest-neighbor."""
        stops = [
            RouteStop(
                hotspot_id=i,
                latitude=12.9716 + i * 0.001,
                longitude=77.5946 + i * 0.001,
                officers_allocated=2,
                priority_rank=i,
                risk_category="High",
            )
            for i in range(5)
        ]
        result = PatrolRouteOptimizer.optimize(stops, use_two_opt=False)
        assert len(result) == len(stops)
        ids = {s.hotspot_id for s in result}
        assert ids == {s.hotspot_id for s in stops}
