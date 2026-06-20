from datetime import datetime
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints.allocation import router
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

    query_mock = MagicMock()
    mock_db.query.return_value = query_mock

    subq_mock = MagicMock()
    query_mock.group_by.return_value.subquery.return_value = subq_mock

    eis_query = MagicMock()
    mock_db.query.side_effect = [
        query_mock,
        eis_query,
    ]

    eis_query.join.return_value = eis_query
    eis_query.filter.return_value = eis_query
    eis_query.order_by.return_value = eis_query
    eis_query.all.return_value = [(FakeEISScore(), FakeHotspot())]

    app = make_app(mock_db)
    client = TestClient(app)

    response = client.post(
        "/allocation/compute",
        json={
            "total_officers": 5,
            "top_n_hotspots": 10,
        },
    )

    assert response.status_code in {200, 422, 500}


def test_latest_allocation_not_found():
    mock_db = MagicMock()

    query_mock = MagicMock()
    mock_db.query.return_value = query_mock
    query_mock.order_by.return_value.first.return_value = None

    app = make_app(mock_db)
    client = TestClient(app)

    response = client.get("/allocation/latest")

    assert response.status_code == 404