"""
tests/unit/test_routing_api.py
─────────────────────────────
Unit tests for routing API endpoints.

Uses FastAPI TestClient with mocked RoutingService.
"""

from __future__ import annotations

from datetime import date, datetime
from unittest.mock import MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.deps import db_session
from app.api.v1.endpoints.routing import router


def make_app():
    """Create a FastAPI test app with routing endpoints."""
    app = FastAPI()
    app.include_router(router, prefix="/routing")

    def override_db():
        yield MagicMock()

    app.dependency_overrides[db_session] = override_db
    return app


class TestGenerateRoute:
    """Test POST /routing/generate endpoint."""

    def test_generate_route_success(self):
        """Test successful route generation."""
        app = make_app()
        client = TestClient(app)

        with patch("app.api.v1.endpoints.routing.RoutingService") as MockService:
            mock_service = MagicMock()
            MockService.return_value = mock_service

            mock_service.generate_route.return_value = {
                "route_id": 42,
                "route_date": "2026-06-18",
                "shift_name": "default",
                "total_stops": 5,
                "critical_stops": 1,
                "high_stops": 3,
                "total_officers": 10,
                "total_distance_km": 25.5,
                "estimated_travel_minutes": 60,
                "estimated_total_minutes": 120,
                "route_geometry": [{"lat": 12.97, "lng": 77.59}],
                "stops": [],
                "summary": {},
            }

            response = client.post(
                "/routing/generate",
                json={
                    "route_date": "2026-06-18",
                    "shift_name": "default",
                    "average_speed_kmph": 25.0,
                    "use_two_opt": True,
                },
            )

            assert response.status_code == 201
            data = response.json()
            assert data["route_id"] == 42
            assert data["total_stops"] == 5

    def test_generate_route_validation_error(self):
        """Test route generation with invalid input."""
        app = make_app()
        client = TestClient(app)

        response = client.post(
            "/routing/generate",
            json={
                "route_date": "invalid-date",
                "shift_name": "default",
            },
        )

        assert response.status_code == 422  # Validation error

    def test_generate_route_service_error(self):
        """Test route generation when service raises ValueError."""
        app = make_app()
        client = TestClient(app)

        with patch("app.api.v1.endpoints.routing.RoutingService") as MockService:
            mock_service = MagicMock()
            MockService.return_value = mock_service

            mock_service.generate_route.side_effect = ValueError("No allocations found")

            response = client.post(
                "/routing/generate",
                json={
                    "route_date": "2026-06-18",
                    "shift_name": "default",
                },
            )

            assert response.status_code == 400
            assert "No allocations found" in response.json()["detail"]

    def test_generate_route_with_optional_params(self):
        """Test route generation with optional parameters."""
        app = make_app()
        client = TestClient(app)

        with patch("app.api.v1.endpoints.routing.RoutingService") as MockService:
            mock_service = MagicMock()
            MockService.return_value = mock_service

            mock_service.generate_route.return_value = {
                "route_id": 1,
                "route_date": "2026-06-18",
                "shift_name": "default",
                "total_stops": 3,
                "critical_stops": 0,
                "high_stops": 2,
                "total_officers": 5,
                "total_distance_km": 15.0,
                "estimated_travel_minutes": 30,
                "estimated_total_minutes": 60,
                "route_geometry": [{"lat": 12.97, "lng": 77.59}],
                "stops": [],
                "summary": {},
            }

            response = client.post(
                "/routing/generate",
                json={
                    "route_date": "2026-06-18",
                    "shift_name": "morning",
                    "start_latitude": 12.9680,
                    "start_longitude": 77.5920,
                    "average_speed_kmph": 30.0,
                    "max_stops": 5,
                    "use_two_opt": False,
                },
            )

            assert response.status_code == 201
            mock_service.generate_route.assert_called_once()


class TestListRoutes:
    """Test GET /routing endpoint."""

    def test_list_routes_success(self):
        """Test successful route listing."""
        app = make_app()
        client = TestClient(app)

        with patch("app.api.v1.endpoints.routing.RoutingService") as MockService:
            mock_service = MagicMock()
            MockService.return_value = mock_service

            mock_service.list_routes.return_value = [
                {
                    "route_id": 1,
                    "route_name": "Route 1",
                    "shift_label": "default",
                    "officer_count": 5,
                    "total_distance_km": 25.5,
                    "estimated_duration_min": 90,
                    "hotspots_covered": 5,
                    "total_eis_covered": 425.0,
                    "created_at": datetime.utcnow().isoformat(),
                },
                {
                    "route_id": 2,
                    "route_name": "Route 2",
                    "shift_label": "morning",
                    "officer_count": 5,
                    "total_distance_km": 30.0,
                    "estimated_duration_min": 100,
                    "hotspots_covered": 6,
                    "total_eis_covered": 500.0,
                    "created_at": datetime.utcnow().isoformat(),
                },
            ]

            response = client.get("/routing")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2

    def test_list_routes_with_filters(self):
        """Test route listing with filters."""
        app = make_app()
        client = TestClient(app)

        with patch("app.api.v1.endpoints.routing.RoutingService") as MockService:
            mock_service = MagicMock()
            MockService.return_value = mock_service

            mock_service.list_routes.return_value = []

            response = client.get(
                "/routing",
                params={
                    "route_date": "2026-06-18",
                    "shift_name": "morning",
                    "limit": 50,
                },
            )

            assert response.status_code == 200
            mock_service.list_routes.assert_called_once()

    def test_list_routes_with_trailing_slash(self):
        """Test route listing with trailing slash."""
        app = make_app()
        client = TestClient(app)

        with patch("app.api.v1.endpoints.routing.RoutingService") as MockService:
            mock_service = MagicMock()
            MockService.return_value = mock_service

            mock_service.list_routes.return_value = []

            response = client.get("/routing/")

            assert response.status_code == 200
            mock_service.list_routes.assert_called_once()


class TestGetLatestRoute:
    """Test GET /routing/latest endpoint."""

    def test_get_latest_route_success(self):
        """Test successful latest route retrieval."""
        app = make_app()
        client = TestClient(app)

        with patch("app.api.v1.endpoints.routing.RoutingService") as MockService:
            mock_service = MagicMock()
            MockService.return_value = mock_service

            mock_service.get_latest_route.return_value = {
                "route_id": 99,
                "route_name": "Latest Route",
                "shift_label": "default",
                "officer_count": 5,
                "total_distance_km": 25.5,
                "estimated_duration_min": 90,
                "hotspots_covered": 5,
                "total_eis_covered": 425.0,
                "created_at": datetime.utcnow().isoformat(),
            }

            response = client.get("/routing/latest")

            assert response.status_code == 200
            data = response.json()
            assert data["route_id"] == 99

    def test_get_latest_route_not_found(self):
        """Test latest route not found (404)."""
        app = make_app()
        client = TestClient(app)

        with patch("app.api.v1.endpoints.routing.RoutingService") as MockService:
            mock_service = MagicMock()
            MockService.return_value = mock_service

            mock_service.get_latest_route.return_value = None

            response = client.get("/routing/latest")

            assert response.status_code == 404


class TestGetRouteSummary:
    """Test GET /routing/summary endpoint."""

    def test_get_summary_success(self):
        """Test successful summary retrieval."""
        app = make_app()
        client = TestClient(app)

        with patch("app.api.v1.endpoints.routing.RoutingService") as MockService:
            mock_service = MagicMock()
            MockService.return_value = mock_service

            mock_service.get_summary.return_value = {
                "total_routes": 5,
                "average_distance_km": 25.5,
                "average_duration_min": 90,
                "average_stops_per_route": 5.0,
            }

            response = client.get("/routing/summary")

            assert response.status_code == 200
            data = response.json()
            assert data["total_routes"] == 5
            assert data["average_distance_km"] == 25.5


class TestGetRouteById:
    """Test GET /routing/{route_id} endpoint."""

    def test_get_route_by_id_success(self):
        """Test successful route retrieval by ID."""
        app = make_app()
        client = TestClient(app)

        with patch("app.api.v1.endpoints.routing.RoutingService") as MockService:
            mock_service = MagicMock()
            MockService.return_value = mock_service

            mock_service.get_route_by_id.return_value = {
                "route_id": 42,
                "route_name": "Route 42",
                "shift_label": "morning",
                "officer_count": 5,
                "total_distance_km": 25.5,
                "estimated_duration_min": 90,
                "hotspots_covered": 5,
                "total_eis_covered": 425.0,
                "created_at": datetime.utcnow().isoformat(),
            }

            response = client.get("/routing/42")

            assert response.status_code == 200
            data = response.json()
            assert data["route_id"] == 42

    def test_get_route_by_id_not_found(self):
        """Test route not found (404)."""
        app = make_app()
        client = TestClient(app)

        with patch("app.api.v1.endpoints.routing.RoutingService") as MockService:
            mock_service = MagicMock()
            MockService.return_value = mock_service

            mock_service.get_route_by_id.side_effect = ValueError("Route 999 not found")

            response = client.get("/routing/999")

            assert response.status_code == 404

    def test_summary_not_matched_as_route_id(self):
        """Test that /summary is not matched as /{route_id}."""
        app = make_app()
        client = TestClient(app)

        with patch("app.api.v1.endpoints.routing.RoutingService") as MockService:
            mock_service = MagicMock()
            MockService.return_value = mock_service

            mock_service.get_summary.return_value = {
                "total_routes": 10,
                "average_distance_km": 20.0,
                "average_duration_min": 80,
                "average_stops_per_route": 4.5,
            }

            response = client.get("/routing/summary")

            assert response.status_code == 200
            # Verify get_summary was called, not get_route_by_id
            mock_service.get_summary.assert_called_once()
            mock_service.get_route_by_id.assert_not_called()
