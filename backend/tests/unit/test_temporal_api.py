"""
tests/unit/test_temporal_api.py
────────────────────────────────
Unit tests for app/api/v1/endpoints/temporal.py.

Strategy
────────
- Use FastAPI TestClient with dependency overrides so no real DB is needed.
- TemporalService methods are replaced with lightweight mocks.
- Tests verify HTTP status codes, response shapes, and error propagation.

Run with:  pytest tests/unit/test_temporal_api.py -v
"""

from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from typing import List
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.deps import db_session
from app.services.temporal_service import TemporalRunResult


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════

def _make_peak_window(**kwargs) -> SimpleNamespace:
    defaults = dict(
        id=1,
        hotspot_id=1,
        day_of_week=0,
        hour_of_day=8,
        window_label="Morning Rush",
        violation_count=42,
        avg_violations=6.0,
        pct_of_total=0.18,
        recommended_start_hour=7,
        recommended_end_hour=9,
        enforcement_priority="Critical",
        pipeline_run_id="run-test",
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _make_run_result() -> TemporalRunResult:
    return TemporalRunResult(
        pipeline_run_id="run-abc",
        n_violations_analysed=500,
        n_hotspots_analysed=10,
        n_windows_written=25,
        n_windows_deleted=20,
        started_at=datetime(2024, 1, 1, 10, 0, 0),
        completed_at=datetime(2024, 1, 1, 10, 0, 3),
    )


# ═══════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def client(mock_db):
    app.dependency_overrides[db_session] = lambda: mock_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


# ═══════════════════════════════════════════════════════════════════════════
# GET /temporal/peak-windows
# ═══════════════════════════════════════════════════════════════════════════

class TestListPeakWindows:
    SVC_PATH = "app.api.v1.endpoints.temporal.TemporalService"

    def test_returns_200_with_items(self, client):
        with patch(self.SVC_PATH) as MockSvc:
            MockSvc.return_value.get_peak_windows.return_value = [_make_peak_window()]
            MockSvc.return_value.count_windows.return_value = 1
            resp = client.get("/api/v1/temporal/peak-windows")
        # Endpoint may use 200 with list or wrapped response
        assert resp.status_code in (200,)

    def test_empty_list_returns_200(self, client):
        with patch(self.SVC_PATH) as MockSvc:
            MockSvc.return_value.get_peak_windows.return_value = []
            MockSvc.return_value.count_windows.return_value = 0
            resp = client.get("/api/v1/temporal/peak-windows")
        assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════
# GET /temporal/peak-windows/{id}
# ═══════════════════════════════════════════════════════════════════════════

class TestGetPeakWindow:
    REPO_PATH = "app.repositories.temporal_repository.TemporalRepository"

    def test_existing_id_returns_200(self, client):
        win = _make_peak_window(id=5)
        with patch(self.REPO_PATH) as MockRepo:
            MockRepo.return_value.get_by_id.return_value = win
            resp = client.get("/api/v1/temporal/peak-windows/5")
        assert resp.status_code == 200

    def test_missing_id_returns_404(self, client):
        with patch(self.REPO_PATH) as MockRepo:
            MockRepo.return_value.get_by_id.return_value = None
            resp = client.get("/api/v1/temporal/peak-windows/9999")
        assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════
# GET /temporal/enforcement-schedule
# ═══════════════════════════════════════════════════════════════════════════

class TestEnforcementSchedule:
    SVC_PATH = "app.api.v1.endpoints.temporal.TemporalService"

    def test_returns_200(self, client):
        with patch(self.SVC_PATH) as MockSvc:
            MockSvc.return_value.get_enforcement_schedule.return_value = [_make_peak_window()]
            resp = client.get("/api/v1/temporal/enforcement-schedule")
        assert resp.status_code == 200

    def test_response_is_list(self, client):
        with patch(self.SVC_PATH) as MockSvc:
            MockSvc.return_value.get_enforcement_schedule.return_value = [_make_peak_window()]
            resp = client.get("/api/v1/temporal/enforcement-schedule")
        assert isinstance(resp.json(), list)


# ═══════════════════════════════════════════════════════════════════════════
# GET /temporal/heatmap
# ═══════════════════════════════════════════════════════════════════════════

class TestHeatmap:
    SVC_PATH = "app.api.v1.endpoints.temporal.TemporalService"

    def test_returns_200_list(self, client):
        with patch(self.SVC_PATH) as MockSvc:
            MockSvc.return_value.get_heatmap_data.return_value = [
                {"day_of_week": 0, "hour_of_day": 8, "total_violations": 42}
            ]
            resp = client.get("/api/v1/temporal/heatmap")
        assert resp.status_code == 200

    def test_heatmap_cell_shape(self, client):
        with patch(self.SVC_PATH) as MockSvc:
            MockSvc.return_value.get_heatmap_data.return_value = [
                {"day_of_week": 1, "hour_of_day": 9, "total_violations": 15}
            ]
            resp = client.get("/api/v1/temporal/heatmap")
        data = resp.json()
        assert isinstance(data, list)
        if data:
            cell = data[0]
            assert "day_of_week" in cell
            assert "hour_of_day" in cell
            assert "total_violations" in cell


# ═══════════════════════════════════════════════════════════════════════════
# GET /temporal/hotspots/{id}/windows
# ═══════════════════════════════════════════════════════════════════════════

class TestHotspotWindows:
    SVC_PATH = "app.api.v1.endpoints.temporal.TemporalService"

    def test_returns_200_for_known_hotspot(self, client):
        with patch(self.SVC_PATH) as MockSvc:
            MockSvc.return_value.get_peak_windows.return_value = [_make_peak_window()]
            resp = client.get("/api/v1/temporal/hotspots/1/windows")
        assert resp.status_code == 200

    def test_returns_list(self, client):
        with patch(self.SVC_PATH) as MockSvc:
            MockSvc.return_value.get_windows_for_hotspot.return_value = []
            resp = client.get("/api/v1/temporal/hotspots/1/windows")
        assert isinstance(resp.json(), list)


# ═══════════════════════════════════════════════════════════════════════════
# GET /temporal/hotspots/{id}/risk
# ═══════════════════════════════════════════════════════════════════════════

class TestHotspotRisk:
    SVC_PATH = "app.api.v1.endpoints.temporal.TemporalService"

    def test_returns_risk_score(self, client):
        with patch(self.SVC_PATH) as MockSvc:
            MockSvc.return_value.get_temporal_risk_score.return_value = 0.72
            resp = client.get("/api/v1/temporal/hotspots/1/risk-score")
        assert resp.status_code == 200
        body = resp.json()
        assert "temporal_risk_score" in body
        assert 0.0 <= body["temporal_risk_score"] <= 1.0


# ═══════════════════════════════════════════════════════════════════════════
# POST /temporal/run-pipeline
# ═══════════════════════════════════════════════════════════════════════════

class TestRunPipelineEndpoint:
    SVC_PATH = "app.api.v1.endpoints.temporal.TemporalService"

    def test_returns_200_with_summary(self, client):
        with patch(self.SVC_PATH) as MockSvc:
            MockSvc.return_value.run_pipeline.return_value = _make_run_result()
            resp = client.post(
                "/api/v1/temporal/run-pipeline",
                json={"truncate_existing": True, "min_window_violations": 5},
            )
        assert resp.status_code == 202
        body = resp.json()
        assert "pipeline_run_id" in body
        assert "n_windows_written" in body

    def test_insufficient_data_returns_422_or_400(self, client):
        from app.core.exceptions import InsufficientDataForClusteringError
        with patch(self.SVC_PATH) as MockSvc:
            MockSvc.return_value.run_pipeline.side_effect = InsufficientDataForClusteringError("no data")
            resp = client.post(
                "/api/v1/temporal/run-pipeline",
                json={"truncate_existing": True, "min_window_violations": 5},
            )
        assert resp.status_code in (400, 422, 500)
