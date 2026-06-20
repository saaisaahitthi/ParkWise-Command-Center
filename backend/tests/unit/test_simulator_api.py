from __future__ import annotations

from unittest.mock import MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.deps import db_session
from app.api.v1.endpoints.simulator import router
from app.ml.simulator import SimulatorInput


def make_client() -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/simulator")

    def override_db():
        yield MagicMock()

    app.dependency_overrides[db_session] = override_db
    return TestClient(app)


def simulation_response() -> dict:
    return {
        "scenario_name": "Reduce frequency",
        "total_hotspots": 1,
        "improved_hotspots": 1,
        "worsened_hotspots": 0,
        "unchanged_hotspots": 0,
        "baseline_average_eis": 80.0,
        "simulated_average_eis": 70.0,
        "average_eis_delta": -10.0,
        "baseline_total_officers": 2,
        "simulated_total_officers": 2,
        "summary": {"improvement_percentage": 100.0},
        "hotspot_results": [
            {
                "hotspot_id": 1,
                "baseline_eis": 80.0,
                "simulated_eis": 70.0,
            }
        ],
    }


def baseline_input() -> SimulatorInput:
    return SimulatorInput(
        hotspot_id=1,
        current_eis=80.0,
        current_risk_category="Critical",
        frequency_score=0.8,
        recurrence_score=0.7,
        density_score=0.9,
        temporal_risk_score=0.8,
        severity_norm=0.7,
        forecasted_eis=82.0,
        forecasted_risk_category="Critical",
        officers_allocated=2,
        hotspot_name="API Test Hotspot",
        zone_id="Zone A",
    )


def test_post_run_success() -> None:
    client = make_client()

    with patch(
        "app.api.v1.endpoints.simulator.SimulatorService"
    ) as service_class:
        service_class.return_value.run_simulation.return_value = simulation_response()
        response = client.post(
            "/simulator/run",
            json={
                "scenario_name": "Reduce frequency",
                "overrides": {"frequency_reduction_pct": 0.15},
            },
        )

    assert response.status_code == 200
    assert response.json()["scenario_name"] == "Reduce frequency"


def test_post_run_handles_value_error_as_bad_request() -> None:
    client = make_client()

    with patch(
        "app.api.v1.endpoints.simulator.SimulatorService"
    ) as service_class:
        service_class.return_value.run_simulation.side_effect = ValueError(
            "No EIS scores are available."
        )
        response = client.post(
            "/simulator/run",
            json={"scenario_name": "Missing data", "overrides": {}},
        )

    assert response.status_code == 400
    assert "No EIS scores" in response.json()["detail"]


def test_get_presets_success() -> None:
    client = make_client()
    presets = [{"name": "Reduce frequency by 15%", "overrides": {}}]

    with patch(
        "app.api.v1.endpoints.simulator.SimulatorService"
    ) as service_class:
        service_class.return_value.get_simulation_presets.return_value = presets
        response = client.get("/simulator/presets")

    assert response.status_code == 200
    assert response.json() == presets


def test_get_baseline_success() -> None:
    client = make_client()

    with patch(
        "app.api.v1.endpoints.simulator.SimulatorService"
    ) as service_class:
        service_class.return_value.get_baseline_inputs.return_value = [baseline_input()]
        response = client.get("/simulator/baseline")

    assert response.status_code == 200
    assert response.json()[0]["hotspot_id"] == 1


def test_get_baseline_supports_optional_query_params() -> None:
    client = make_client()

    with patch(
        "app.api.v1.endpoints.simulator.SimulatorService"
    ) as service_class:
        service_class.return_value.get_baseline_inputs.return_value = [baseline_input()]
        response = client.get(
            "/simulator/baseline",
            params={
                "target_hotspot_ids": "1,2",
                "forecast_horizon_days": 7,
            },
        )

    assert response.status_code == 200
    service_class.return_value.get_baseline_inputs.assert_called_once_with(
        target_hotspot_ids=[1, 2],
        forecast_horizon_days=7,
    )


def test_get_baseline_handles_missing_data() -> None:
    client = make_client()

    with patch(
        "app.api.v1.endpoints.simulator.SimulatorService"
    ) as service_class:
        service_class.return_value.get_baseline_inputs.side_effect = ValueError(
            "No EIS scores are available."
        )
        response = client.get("/simulator/baseline")

    assert response.status_code == 422
    assert "No EIS scores" in response.json()["detail"]
