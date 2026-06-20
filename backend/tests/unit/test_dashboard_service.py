from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.models.analytics import Allocation, EISScore, Forecast
from app.services.dashboard_service import DashboardService


def test_get_executive_summary_returns_required_keys() -> None:
    db = MagicMock()
    query = MagicMock()
    db.query.return_value = query
    now = datetime(2026, 6, 18, 12, 0, 0)
    query.scalar.side_effect = [4, 7, now, now, now, now, now, now]
    service = DashboardService(db)
    route = SimpleNamespace(
        total_distance_km=12.5,
        estimated_duration_min=45,
    )

    with patch.object(
        service,
        "get_risk_distribution",
        return_value={"Low": 1, "Medium": 1, "High": 1, "Critical": 1},
    ), patch.object(
        service,
        "_latest_allocations",
        return_value=[
            SimpleNamespace(officers_allocated=3),
            SimpleNamespace(officers_allocated=2),
        ],
    ), patch.object(service, "_latest_route", return_value=route):
        result = service.get_executive_summary()

    required = {
        "total_hotspots",
        "active_hotspots",
        "critical_hotspots",
        "high_risk_hotspots",
        "total_forecasts",
        "total_allocated_officers",
        "latest_route_distance_km",
        "latest_route_duration_min",
        "last_updated_at",
    }
    assert required <= result.keys()
    assert result["total_hotspots"] == 4
    assert result["total_allocated_officers"] == 5


def test_get_risk_distribution_returns_category_counts() -> None:
    db = MagicMock()
    query = MagicMock()
    db.query.return_value = query
    query.join.return_value = query
    query.group_by.return_value = query
    query.all.return_value = [
        ("Low", 2),
        ("High", 3),
        ("Critical", 1),
    ]
    service = DashboardService(db)

    with patch.object(service, "_latest_id_subquery", return_value=MagicMock()):
        result = service.get_risk_distribution()

    assert result == {
        "Low": 2,
        "Medium": 0,
        "High": 3,
        "Critical": 1,
    }


def test_get_hotspot_map_data_returns_map_ready_objects() -> None:
    db = MagicMock()
    query = MagicMock()
    db.query.return_value = query
    query.order_by.return_value = query
    hotspot = SimpleNamespace(
        id=1,
        hotspot_name="Central Market",
        centroid_lat=12.9716,
        centroid_lon=77.5946,
        dominant_violation_type="No Parking",
        total_violations=120,
    )
    query.all.return_value = [hotspot]
    service = DashboardService(db)
    latest_eis = SimpleNamespace(
        hotspot_id=1,
        eis_score=82.0,
        risk_category="Critical",
    )
    forecast = SimpleNamespace(hotspot_id=1, predicted_eis=85.0)
    allocation = SimpleNamespace(hotspot_id=1, officers_allocated=4)

    def latest_rows(model, hotspot_ids=None):
        if model is EISScore:
            return [latest_eis]
        if model is Forecast:
            return [forecast]
        if model is Allocation:
            return [allocation]
        return []

    with patch.object(service, "_latest_rows", side_effect=latest_rows):
        result = service.get_hotspot_map_data()

    assert result == [
        {
            "hotspot_id": 1,
            "name": "Central Market",
            "latitude": 12.9716,
            "longitude": 77.5946,
            "hotspot_type": "No Parking",
            "violation_count": 120,
            "latest_eis": 82.0,
            "risk_category": "Critical",
            "forecasted_eis": 85.0,
            "officers_allocated": 4,
        }
    ]


def test_get_temporal_overview_handles_missing_peak_windows() -> None:
    db = MagicMock()
    count_query = MagicMock()
    top_query = MagicMock()
    heatmap_query = MagicMock()
    temporal_query = MagicMock()
    db.query.side_effect = [
        count_query,
        top_query,
        heatmap_query,
        temporal_query,
    ]
    count_query.scalar.return_value = 0
    top_query.outerjoin.return_value = top_query
    top_query.order_by.return_value = top_query
    top_query.limit.return_value = top_query
    top_query.all.return_value = []
    heatmap_query.filter.return_value = heatmap_query
    heatmap_query.group_by.return_value = heatmap_query
    heatmap_query.order_by.return_value = heatmap_query
    heatmap_query.all.return_value = []
    temporal_query.join.return_value = temporal_query
    temporal_query.order_by.return_value = temporal_query
    temporal_query.limit.return_value = temporal_query
    temporal_query.all.return_value = []
    service = DashboardService(db)

    with patch.object(service, "_latest_id_subquery", return_value=MagicMock()):
        result = service.get_temporal_overview()

    assert result["peak_windows_count"] == 0
    assert result["top_peak_windows"] == []
    assert result["day_hour_heatmap"] == []
    assert result["highest_temporal_risk_hotspots"] == []


def test_get_forecast_overview_returns_totals_and_top_hotspots() -> None:
    db = MagicMock()
    db.query.return_value.scalar.return_value = 2
    service = DashboardService(db)
    rows = [
        SimpleNamespace(
            id=2,
            hotspot_id=2,
            forecast_date=datetime(2026, 6, 20),
            horizon_days=1,
            predicted_eis=91.0,
            predicted_risk_category="Critical",
            confidence_lower=84.0,
            confidence_upper=96.0,
        ),
        SimpleNamespace(
            id=1,
            hotspot_id=1,
            forecast_date=datetime(2026, 6, 20),
            horizon_days=1,
            predicted_eis=65.0,
            predicted_risk_category="High",
            confidence_lower=None,
            confidence_upper=None,
        ),
    ]

    with patch.object(service, "_latest_rows", return_value=rows), patch.object(
        service,
        "_hotspot_name_map",
        return_value={1: "Market", 2: "Station"},
    ):
        result = service.get_forecast_overview()

    assert result["total_forecasts"] == 2
    assert result["top_forecasted_hotspots"][0]["hotspot_name"] == "Station"
    assert result["risk_distribution"]["Critical"] == 1
    assert result["average_predicted_eis"] == 78.0


def test_get_allocation_overview_returns_officer_totals() -> None:
    service = DashboardService(MagicMock())
    allocations = [
        SimpleNamespace(
            id=1,
            hotspot_id=1,
            officers_allocated=4,
            priority_rank=1,
            deployment_window="08:00-10:00",
            eis_snapshot=85.0,
            risk_category="Critical",
            allocation_date=datetime(2026, 6, 18),
        ),
        SimpleNamespace(
            id=2,
            hotspot_id=2,
            officers_allocated=2,
            priority_rank=2,
            deployment_window=None,
            eis_snapshot=62.0,
            risk_category="High",
            allocation_date=datetime(2026, 6, 18),
        ),
    ]

    with patch.object(
        service,
        "_latest_allocations",
        return_value=allocations,
    ), patch.object(
        service,
        "_hotspot_name_map",
        return_value={1: "Market", 2: "Station"},
    ):
        result = service.get_allocation_overview()

    assert result["total_allocations"] == 2
    assert result["total_officers"] == 6
    assert result["officer_by_risk"]["Critical"] == 4
    assert result["officer_by_risk"]["High"] == 2


def test_get_routing_overview_returns_latest_route_data() -> None:
    db = MagicMock()
    db.query.return_value.scalar.return_value = 3
    service = DashboardService(db)
    route = SimpleNamespace(
        id=7,
        route_name="Morning Route",
        shift_label="Morning",
        officer_count=5,
        stops_json=[{"hotspot_id": 1}],
        total_distance_km=14.2,
        estimated_duration_min=55,
        hotspots_covered=1,
        total_eis_covered=82.0,
        created_at=datetime(2026, 6, 18, 8, 0, 0),
    )

    with patch.object(service, "_latest_route", return_value=route):
        result = service.get_routing_overview()

    assert result["total_routes"] == 3
    assert result["latest_route"]["route_id"] == 7
    assert result["latest_distance_km"] == 14.2
    assert result["latest_duration_min"] == 55
    assert result["latest_stops_count"] == 1


def test_get_dashboard_payload_combines_all_sections() -> None:
    service = DashboardService(MagicMock())
    method_results = {
        "get_executive_summary": {"total_hotspots": 1},
        "get_risk_distribution": {"Low": 1},
        "get_hotspot_map_data": [{"hotspot_id": 1}],
        "get_temporal_overview": {"peak_windows_count": 0},
        "get_forecast_overview": {"total_forecasts": 0},
        "get_allocation_overview": {"total_allocations": 0},
        "get_routing_overview": {"total_routes": 0},
    }

    patches = [
        patch.object(service, method, return_value=value)
        for method, value in method_results.items()
    ]
    for active_patch in patches:
        active_patch.start()
    try:
        result = service.get_dashboard_payload()
    finally:
        for active_patch in reversed(patches):
            active_patch.stop()

    assert set(result) == {
        "executive_summary",
        "risk_distribution",
        "hotspot_map",
        "temporal_overview",
        "forecast_overview",
        "allocation_overview",
        "routing_overview",
    }


def test_dashboard_service_is_read_only() -> None:
    db = MagicMock()
    service = DashboardService(db)

    with patch.object(service, "get_executive_summary", return_value={}), patch.object(
        service, "get_risk_distribution", return_value={}
    ), patch.object(service, "get_hotspot_map_data", return_value=[]), patch.object(
        service, "get_temporal_overview", return_value={}
    ), patch.object(service, "get_forecast_overview", return_value={}), patch.object(
        service, "get_allocation_overview", return_value={}
    ), patch.object(service, "get_routing_overview", return_value={}):
        service.get_dashboard_payload()

    db.add.assert_not_called()
    db.commit.assert_not_called()
    db.delete.assert_not_called()
    db.merge.assert_not_called()
    db.flush.assert_not_called()
