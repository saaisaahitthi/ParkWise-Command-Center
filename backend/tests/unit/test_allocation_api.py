from datetime import datetime
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints.allocation import _distribute_officers_exact, router
from app.api.deps import db_session


def make_app(mock_db):
    app = FastAPI()
    app.include_router(router, prefix="/allocation")

    def override_db():
        yield mock_db

    app.dependency_overrides[db_session] = override_db
    return app


class FakeEISScore:
    id = 1
    hotspot_id = 10
    eis_score = 80.0
    risk_category = "Critical"


class FakeHotspot:
    id = 10
    hotspot_name = "Test Hotspot"
    centroid_lat = 17.4
    centroid_lon = 78.4
    centroid_lng = 78.4
    total_violations = 100


class FakeForecast:
    predicted_eis = 90.0
    predicted_risk_category = "Critical"


class FakeAllocation:
    id = 1
    hotspot_id = 10
    officers_allocated = 5
    allocation_fraction = 1.0
    priority_rank = 1
    deployment_window = None
    total_officers_available = 5
    eis_snapshot = 80.0
    risk_category = "Critical"
    allocation_date = datetime.utcnow()


def test_compute_allocation_success():
    mock_db = MagicMock()

    latest_eis_query = MagicMock()
    latest_forecast_query = MagicMock()
    ranked_query = MagicMock()
    mock_db.query.side_effect = [
        latest_eis_query,
        latest_forecast_query,
        ranked_query,
    ]

    latest_eis_query.group_by.return_value.subquery.return_value = MagicMock()
    latest_forecast_query.filter.return_value = latest_forecast_query
    latest_forecast_query.group_by.return_value.subquery.return_value = MagicMock()

    ranked_query.outerjoin.return_value = ranked_query
    ranked_query.order_by.return_value = ranked_query
    ranked_query.limit.return_value = ranked_query
    ranked_query.all.return_value = [
        (FakeHotspot(), FakeEISScore(), FakeForecast())
    ]

    app = make_app(mock_db)
    client = TestClient(app)

    response = client.post(
        "/allocation/compute",
        json={
            "total_officers": 5,
            "top_n_hotspots": 10,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_officers"] == 5
    assert payload["hotspots_covered"] == 1
    assert payload["unallocated_officers"] == 0
    assert payload["allocations"][0]["officers_allocated"] == 5


def test_latest_allocation_not_found():
    mock_db = MagicMock()

    query_mock = MagicMock()
    mock_db.query.return_value = query_mock
    query_mock.order_by.return_value.first.return_value = None

    app = make_app(mock_db)
    client = TestClient(app)

    response = client.get("/allocation/latest")

    assert response.status_code == 404


def test_exact_distribution_uses_all_officers_across_ten_hotspots():
    allocations = _distribute_officers_exact(
        total_officers=45,
        priority_weights=[100, 90, 80, 70, 60, 50, 40, 30, 20, 10],
    )

    assert len(allocations) == 10
    assert sum(allocations) == 45
    assert all(officers >= 1 for officers in allocations)
    assert allocations[0] > allocations[-1]


def test_exact_distribution_limits_rows_when_officers_are_fewer():
    allocations = _distribute_officers_exact(
        total_officers=5,
        priority_weights=[100, 90, 80, 70, 60],
    )

    assert allocations == [1, 1, 1, 1, 1]
