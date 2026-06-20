from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import pytest

from app.ml.simulator import (
    SimulationResult,
    SimulatorInput,
    SimulatorOverrides,
)
from app.services.simulator_service import SimulatorService


@dataclass
class FakeEISScore:
    hotspot_id: int = 1
    eis_score: float = 72.0
    risk_category: str = "High"
    frequency_score: float = 0.7
    recurrence_score: float = 0.6
    density_score: float = 0.8
    temporal_risk_score: float = 0.75
    severity_norm: float = 0.6
    exposure_score: float = 0.7
    severity_multiplier: float = 1.08


@dataclass
class FakeHotspot:
    hotspot_name: str = "Test Hotspot"
    zone_id: str = "Zone A"


def make_input() -> SimulatorInput:
    return SimulatorInput(
        hotspot_id=1,
        current_eis=72.0,
        current_risk_category="High",
        frequency_score=0.7,
        recurrence_score=0.6,
        density_score=0.8,
        temporal_risk_score=0.75,
        severity_norm=0.6,
        officers_allocated=2,
        hotspot_name="Test Hotspot",
        zone_id="Zone A",
    )


def make_service_with_baseline_row() -> SimulatorService:
    db = MagicMock()
    latest_query = MagicMock()
    baseline_query = MagicMock()
    db.query.side_effect = [latest_query, baseline_query]

    latest_query.group_by.return_value = latest_query
    latest_query.filter.return_value = latest_query
    latest_query.subquery.return_value = MagicMock()

    baseline_query.join.return_value = baseline_query
    baseline_query.order_by.return_value = baseline_query
    baseline_query.all.return_value = [(FakeEISScore(), FakeHotspot())]
    return SimulatorService(db)


def test_run_simulation_loads_inputs_and_calls_impact_calculator() -> None:
    service = SimulatorService(MagicMock())
    baseline = [make_input()]
    calculated = SimulationResult(
        scenario_name="Frequency reduction",
        total_hotspots=1,
        baseline_average_eis=72.0,
        simulated_average_eis=65.0,
        average_eis_delta=-7.0,
    )

    with patch.object(
        service,
        "get_baseline_inputs",
        return_value=baseline,
    ) as baseline_mock, patch(
        "app.services.simulator_service.ImpactCalculator.calculate",
        return_value=calculated,
    ) as calculator_mock:
        result = service.run_simulation(
            "Frequency reduction",
            SimulatorOverrides(
                frequency_reduction_pct=0.15,
                target_hotspot_ids=[1],
                forecast_horizon_days=7,
            ),
        )

    baseline_mock.assert_called_once_with(
        target_hotspot_ids=[1],
        forecast_horizon_days=7,
    )
    calculator_mock.assert_called_once()
    assert result["scenario_name"] == "Frequency reduction"


def test_run_simulation_returns_dashboard_ready_dict() -> None:
    service = SimulatorService(MagicMock())

    with patch.object(service, "get_baseline_inputs", return_value=[make_input()]):
        result = service.run_simulation(
            "Baseline",
            SimulatorOverrides(),
        )

    expected_keys = {
        "scenario_name",
        "total_hotspots",
        "improved_hotspots",
        "worsened_hotspots",
        "unchanged_hotspots",
        "baseline_average_eis",
        "simulated_average_eis",
        "average_eis_delta",
        "baseline_total_officers",
        "simulated_total_officers",
        "summary",
        "hotspot_results",
    }
    assert expected_keys <= result.keys()
    assert isinstance(result["hotspot_results"], list)


def test_get_baseline_inputs_handles_missing_forecast_rows() -> None:
    service = make_service_with_baseline_row()

    with patch.object(service, "_get_latest_forecasts", return_value={}), patch.object(
        service,
        "_get_latest_allocations",
        return_value={1: MagicMock(officers_allocated=2)},
    ):
        inputs = service.get_baseline_inputs()

    assert inputs[0].forecasted_eis is None
    assert inputs[0].forecasted_risk_category is None
    assert inputs[0].officers_allocated == 2


def test_get_baseline_inputs_handles_missing_allocation_rows() -> None:
    service = make_service_with_baseline_row()
    forecast = MagicMock(
        predicted_eis=78.0,
        predicted_risk_category="Critical",
    )

    with patch.object(
        service,
        "_get_latest_forecasts",
        return_value={1: forecast},
    ), patch.object(service, "_get_latest_allocations", return_value={}):
        inputs = service.get_baseline_inputs()

    assert inputs[0].forecasted_eis == 78.0
    assert inputs[0].officers_allocated is None


def test_get_simulation_presets_returns_non_empty_list() -> None:
    service = SimulatorService(MagicMock())

    with patch.object(service, "_get_baseline_officer_total", return_value=20):
        presets = service.get_simulation_presets()

    assert len(presets) == 5
    assert all("name" in preset and "overrides" in preset for preset in presets)


def test_validate_overrides_accepts_valid_values() -> None:
    service = SimulatorService(MagicMock())

    overrides = service.validate_overrides(
        {
            "total_officers": 25,
            "enforcement_intensity": 1.1,
            "frequency_reduction_pct": 0.15,
            "temporal_risk_reduction_pct": 0.2,
            "target_hotspot_ids": [1, 2],
        }
    )

    assert overrides.total_officers == 25
    assert overrides.frequency_reduction_pct == 0.15


@pytest.mark.parametrize(
    "overrides",
    [
        {"total_officers": -1},
        {"critical_min_officers": -1},
        {"high_min_officers": -1},
        {"enforcement_intensity": -0.5},
        {"frequency_reduction_pct": -0.1},
        {"temporal_risk_reduction_pct": 1.1},
        {"forecast_horizon_days": -1},
        {"target_hotspot_ids": [-1]},
    ],
)
def test_validate_overrides_rejects_invalid_values(overrides: dict) -> None:
    service = SimulatorService(MagicMock())

    with pytest.raises(ValueError):
        service.validate_overrides(overrides)


def test_service_performs_no_database_writes() -> None:
    db = MagicMock()
    service = SimulatorService(db)

    with patch.object(service, "get_baseline_inputs", return_value=[make_input()]):
        service.run_simulation("Read only", SimulatorOverrides())

    db.add.assert_not_called()
    db.commit.assert_not_called()
    db.delete.assert_not_called()
    db.merge.assert_not_called()
    db.update.assert_not_called()
