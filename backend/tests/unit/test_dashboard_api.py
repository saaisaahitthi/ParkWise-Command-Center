from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.deps import db_session
from app.api.v1.endpoints.dashboard import router


def make_client() -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/dashboard")

    def override_db():
        yield MagicMock()

    app.dependency_overrides[db_session] = override_db
    return TestClient(app)


ENDPOINT_CASES = [
    (
        "/dashboard/summary",
        "get_executive_summary",
        {"total_hotspots": 3},
        dict,
    ),
    (
        "/dashboard/risk-distribution",
        "get_risk_distribution",
        {"Low": 1, "Medium": 0, "High": 1, "Critical": 1},
        dict,
    ),
    (
        "/dashboard/map",
        "get_hotspot_map_data",
        [{"hotspot_id": 1, "latitude": 12.9, "longitude": 77.5}],
        list,
    ),
    (
        "/dashboard/temporal",
        "get_temporal_overview",
        {"peak_windows_count": 0, "top_peak_windows": []},
        dict,
    ),
    (
        "/dashboard/forecast",
        "get_forecast_overview",
        {"total_forecasts": 1, "top_forecasted_hotspots": []},
        dict,
    ),
    (
        "/dashboard/allocation",
        "get_allocation_overview",
        {"total_allocations": 1, "total_officers": 4},
        dict,
    ),
    (
        "/dashboard/routing",
        "get_routing_overview",
        {"total_routes": 1, "latest_route": None},
        dict,
    ),
    (
        "/dashboard/full",
        "get_dashboard_payload",
        {
            "executive_summary": {},
            "risk_distribution": {},
            "hotspot_map": [],
            "temporal_overview": {},
            "forecast_overview": {},
            "allocation_overview": {},
            "routing_overview": {},
        },
        dict,
    ),
]


@pytest.mark.parametrize(
    ("path", "method_name", "payload", "expected_type"),
    ENDPOINT_CASES,
)
def test_dashboard_endpoints_return_success(
    path: str,
    method_name: str,
    payload,
    expected_type: type,
) -> None:
    client = make_client()

    with patch(
        "app.api.v1.endpoints.dashboard.DashboardService"
    ) as service_class:
        getattr(service_class.return_value, method_name).return_value = payload
        response = client.get(path)

    assert response.status_code == 200
    assert isinstance(response.json(), expected_type)
    assert response.json() == payload


def test_dashboard_service_error_returns_clean_500_response() -> None:
    client = make_client()

    with patch(
        "app.api.v1.endpoints.dashboard.DashboardService"
    ) as service_class:
        service_class.return_value.get_executive_summary.side_effect = RuntimeError(
            "database unavailable"
        )
        response = client.get("/dashboard/summary")

    assert response.status_code == 500
    assert response.json()["detail"].startswith("Dashboard aggregation failed:")
