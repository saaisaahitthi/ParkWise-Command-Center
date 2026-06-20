"""
tests/unit/test_routing_service.py
────────────────────────────────
Unit tests for RoutingService with mocks.

Tests service orchestration, allocation-to-stop conversion, and persistence.
"""

from __future__ import annotations

from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest

from app.ml.routing.types import RouteStop
from app.models.analytics import Allocation
from app.models.hotspot import Hotspot
from app.services.routing_service import RoutingService


class FakeHotspot:
    """Mock Hotspot for testing."""

    def __init__(self, hotspot_id: int, name: str = "Test Hotspot"):
        self.id = hotspot_id
        self.hotspot_name = name
        self.centroid_lat = 12.9716 + hotspot_id * 0.001
        self.centroid_lon = 77.5946 + hotspot_id * 0.001
        self.zone_id = f"zone_{hotspot_id}"


class FakeAllocation:
    """Mock Allocation for testing."""

    def __init__(
        self,
        allocation_id: int,
        hotspot_id: int,
        officers: int = 2,
        priority: int = 1,
        risk: str = "High",
    ):
        self.id = allocation_id
        self.hotspot_id = hotspot_id
        self.officers_allocated = officers
        self.priority_rank = priority
        self.risk_category = risk
        self.eis_snapshot = 80.0


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def mock_repository():
    """Create a mock repository."""
    return MagicMock()


class TestGenerateRoute:
    """Test route generation workflow."""

    def test_generate_route_success(self, mock_db):
        """Test successful route generation."""
        with patch("app.services.routing_service.RoutingRepository") as MockRepo:
            mock_repo = MagicMock()
            MockRepo.return_value = mock_repo

            # Setup mock allocations
            allocation = FakeAllocation(1, 1, officers=3, priority=1, risk="Critical")
            hotspot = FakeHotspot(1, "KR Market")
            mock_repo.get_latest_allocations.return_value = [(allocation, hotspot)]

            # Setup mock create_patrol_route
            created_route = MagicMock()
            created_route.id = 42
            mock_repo.create_patrol_route.return_value = created_route

            service = RoutingService(mock_db)
            result = service.generate_route(
                route_date=date(2026, 6, 18),
                shift_name="default",
            )

            assert "route_id" in result
            assert result["route_id"] == 42
            assert result["total_stops"] > 0
            assert "route_geometry" in result
            assert "stops" in result
            assert "summary" in result

    def test_generate_route_no_allocations_raises_error(self, mock_db):
        """Test error when no allocations are found."""
        with patch("app.services.routing_service.RoutingRepository") as MockRepo:
            mock_repo = MagicMock()
            MockRepo.return_value = mock_repo

            # Setup mock to return empty allocations
            mock_repo.get_latest_allocations.return_value = []

            service = RoutingService(mock_db)

            with pytest.raises(ValueError, match="No allocations found"):
                service.generate_route(
                    route_date=date(2026, 6, 18),
                    shift_name="default",
                )

    def test_generate_route_with_start_point(self, mock_db):
        """Test route generation with explicit start point."""
        with patch("app.services.routing_service.RoutingRepository") as MockRepo:
            mock_repo = MagicMock()
            MockRepo.return_value = mock_repo

            allocation = FakeAllocation(1, 1, officers=2, priority=1)
            hotspot = FakeHotspot(1)
            mock_repo.get_latest_allocations.return_value = [(allocation, hotspot)]

            created_route = MagicMock()
            created_route.id = 1
            mock_repo.create_patrol_route.return_value = created_route

            service = RoutingService(mock_db)
            result = service.generate_route(
                route_date=date(2026, 6, 18),
                shift_name="default",
                start_latitude=12.9680,
                start_longitude=77.5920,
            )

            assert "route_id" in result
            assert result["route_geometry"][0]["lat"] == 12.9680

    def test_generate_route_calls_persist(self, mock_db):
        """Test that generate_route persists to database."""
        with patch("app.services.routing_service.RoutingRepository") as MockRepo:
            mock_repo = MagicMock()
            MockRepo.return_value = mock_repo

            allocation = FakeAllocation(1, 1, officers=2)
            hotspot = FakeHotspot(1)
            mock_repo.get_latest_allocations.return_value = [(allocation, hotspot)]

            created_route = MagicMock()
            created_route.id = 99
            mock_repo.create_patrol_route.return_value = created_route

            service = RoutingService(mock_db)
            service.generate_route(
                route_date=date(2026, 6, 18),
                shift_name="default",
                commit=True,
            )

            mock_repo.create_patrol_route.assert_called_once()

    def test_generate_route_with_multiple_stops(self, mock_db):
        """Test route generation with multiple allocations."""
        with patch("app.services.routing_service.RoutingRepository") as MockRepo:
            mock_repo = MagicMock()
            MockRepo.return_value = mock_repo

            allocations_and_hotspots = [
                (
                    FakeAllocation(i, i, officers=2, priority=i),
                    FakeHotspot(i, f"Hotspot {i}"),
                )
                for i in range(1, 4)
            ]
            mock_repo.get_latest_allocations.return_value = allocations_and_hotspots

            created_route = MagicMock()
            created_route.id = 50
            mock_repo.create_patrol_route.return_value = created_route

            service = RoutingService(mock_db)
            result = service.generate_route(
                route_date=date(2026, 6, 18),
                shift_name="default",
            )

            assert result["total_stops"] == 3


class TestListRoutes:
    """Test list_routes delegation."""

    def test_list_routes_delegates_to_repository(self, mock_db):
        """Test that list_routes calls repository."""
        with patch("app.services.routing_service.RoutingRepository") as MockRepo:
            mock_repo = MagicMock()
            MockRepo.return_value = mock_repo

            route_mock = MagicMock()
            route_mock.id = 1
            route_mock.route_name = "Test Route"
            route_mock.shift_label = "default"
            route_mock.officer_count = 5
            route_mock.total_distance_km = 25.5
            route_mock.estimated_duration_min = 90
            route_mock.hotspots_covered = 5
            route_mock.total_eis_covered = 425.0
            route_mock.stops_json = []
            route_mock.created_at = datetime.utcnow()

            mock_repo.list_routes.return_value = [route_mock]

            service = RoutingService(mock_db)
            result = service.list_routes(limit=10)

            assert len(result) == 1
            mock_repo.list_routes.assert_called_once()


class TestGetLatestRoute:
    """Test get_latest_route delegation."""

    def test_get_latest_route_delegates(self, mock_db):
        """Test that get_latest_route calls repository."""
        with patch("app.services.routing_service.RoutingRepository") as MockRepo:
            mock_repo = MagicMock()
            MockRepo.return_value = mock_repo

            route_mock = MagicMock()
            route_mock.id = 1
            route_mock.route_name = "Latest Route"
            route_mock.shift_label = "default"
            route_mock.officer_count = 5
            route_mock.total_distance_km = 25.5
            route_mock.estimated_duration_min = 90
            route_mock.hotspots_covered = 5
            route_mock.total_eis_covered = 425.0
            route_mock.stops_json = []
            route_mock.created_at = datetime.utcnow()

            mock_repo.get_latest_route.return_value = route_mock

            service = RoutingService(mock_db)
            result = service.get_latest_route()

            assert result["route_id"] == 1
            mock_repo.get_latest_route.assert_called_once()


class TestGetRouteById:
    """Test get_route_by_id delegation."""

    def test_get_route_by_id_success(self, mock_db):
        """Test successful route retrieval by ID."""
        with patch("app.services.routing_service.RoutingRepository") as MockRepo:
            mock_repo = MagicMock()
            MockRepo.return_value = mock_repo

            route_mock = MagicMock()
            route_mock.id = 42
            route_mock.route_name = "Route 42"
            route_mock.shift_label = "morning"
            route_mock.officer_count = 5
            route_mock.total_distance_km = 25.5
            route_mock.estimated_duration_min = 90
            route_mock.hotspots_covered = 5
            route_mock.total_eis_covered = 425.0
            route_mock.stops_json = []
            route_mock.created_at = datetime.utcnow()

            mock_repo.get_route_by_id.return_value = route_mock

            service = RoutingService(mock_db)
            result = service.get_route_by_id(42)

            assert result["route_id"] == 42
            mock_repo.get_route_by_id.assert_called_once_with(42)

    def test_get_route_by_id_not_found_raises_error(self, mock_db):
        """Test error when route not found."""
        with patch("app.services.routing_service.RoutingRepository") as MockRepo:
            mock_repo = MagicMock()
            MockRepo.return_value = mock_repo

            mock_repo.get_route_by_id.return_value = None

            service = RoutingService(mock_db)

            with pytest.raises(ValueError, match="Route .* not found"):
                service.get_route_by_id(999)


class TestGetSummary:
    """Test get_summary delegation."""

    def test_get_summary_delegates(self, mock_db):
        """Test that get_summary calls repository."""
        with patch("app.services.routing_service.RoutingRepository") as MockRepo:
            mock_repo = MagicMock()
            MockRepo.return_value = mock_repo

            mock_repo.get_summary.return_value = {
                "total_routes": 5,
                "average_distance_km": 25.5,
                "average_duration_min": 90,
                "average_stops_per_route": 5.0,
            }

            service = RoutingService(mock_db)
            result = service.get_summary()

            assert result["total_routes"] == 5
            mock_repo.get_summary.assert_called_once()


class TestAllocationToStop:
    """Test conversion of allocations to RouteStop objects."""

    def test_allocation_to_stop_conversion(self, mock_db):
        """Test conversion maintains all required fields."""
        with patch("app.services.routing_service.RoutingRepository") as MockRepo:
            mock_repo = MagicMock()
            MockRepo.return_value = mock_repo

            allocation = FakeAllocation(1, 10, officers=3, priority=1, risk="Critical")
            hotspot = FakeHotspot(10, "Test Hotspot")
            mock_repo.get_latest_allocations.return_value = [(allocation, hotspot)]

            created_route = MagicMock()
            created_route.id = 1
            mock_repo.create_patrol_route.return_value = created_route

            service = RoutingService(mock_db)
            result = service.generate_route(
                route_date=date(2026, 6, 18),
                shift_name="default",
            )

            stops = result["stops"]
            assert len(stops) > 0
            assert stops[0]["hotspot_id"] == 10
            assert stops[0]["officers_allocated"] == 3
            assert stops[0]["risk_category"] == "Critical"
