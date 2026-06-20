from __future__ import annotations

import pytest

from app.ml.simulator import EISSimulator, SimulatorInput, SimulatorOverrides


@pytest.fixture()
def simulator_input() -> SimulatorInput:
    return SimulatorInput(
        hotspot_id=1,
        current_eis=70.0,
        current_risk_category="High",
        frequency_score=0.8,
        recurrence_score=0.7,
        density_score=0.6,
        temporal_risk_score=0.9,
        severity_norm=0.7,
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0.0, 0.0),
        (0.5, 50.0),
        (1.0, 100.0),
        (25.0, 25.0),
        (80.0, 80.0),
        (150.0, 100.0),
    ],
)
def test_normalize_score_handles_normalized_and_percentage_values(
    value: float,
    expected: float,
) -> None:
    assert EISSimulator.normalize_score(value) == expected


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (10.0, "Low"),
        (25.0, "Medium"),
        (50.0, "High"),
        (75.0, "Critical"),
    ],
)
def test_risk_category_from_score(score: float, expected: str) -> None:
    assert EISSimulator.risk_category_from_score(score) == expected


def test_frequency_reduction_reduces_simulated_eis(
    simulator_input: SimulatorInput,
) -> None:
    baseline, _ = EISSimulator.simulate_hotspot(
        simulator_input,
        SimulatorOverrides(),
    )
    reduced, _ = EISSimulator.simulate_hotspot(
        simulator_input,
        SimulatorOverrides(frequency_reduction_pct=0.25),
    )

    assert reduced < baseline


def test_temporal_risk_reduction_reduces_simulated_eis(
    simulator_input: SimulatorInput,
) -> None:
    baseline, _ = EISSimulator.simulate_hotspot(
        simulator_input,
        SimulatorOverrides(),
    )
    reduced, _ = EISSimulator.simulate_hotspot(
        simulator_input,
        SimulatorOverrides(temporal_risk_reduction_pct=0.25),
    )

    assert reduced < baseline


def test_severity_multiplier_delta_changes_simulated_eis(
    simulator_input: SimulatorInput,
) -> None:
    baseline, _ = EISSimulator.simulate_hotspot(
        simulator_input,
        SimulatorOverrides(),
    )
    increased, _ = EISSimulator.simulate_hotspot(
        simulator_input,
        SimulatorOverrides(severity_multiplier_delta=0.2),
    )

    assert increased > baseline


def test_enforcement_intensity_changes_eis_in_expected_direction(
    simulator_input: SimulatorInput,
) -> None:
    lower, _ = EISSimulator.simulate_hotspot(
        simulator_input,
        SimulatorOverrides(enforcement_intensity=0.75),
    )
    higher, _ = EISSimulator.simulate_hotspot(
        simulator_input,
        SimulatorOverrides(enforcement_intensity=1.25),
    )

    assert lower < higher


@pytest.mark.parametrize(
    "overrides",
    [
        SimulatorOverrides(severity_multiplier_delta=-10.0),
        SimulatorOverrides(severity_multiplier_delta=10.0),
        SimulatorOverrides(enforcement_intensity=10.0),
        SimulatorOverrides(
            frequency_reduction_pct=1.0,
            temporal_risk_reduction_pct=1.0,
        ),
    ],
)
def test_simulated_eis_stays_in_valid_range(
    simulator_input: SimulatorInput,
    overrides: SimulatorOverrides,
) -> None:
    score, category = EISSimulator.simulate_hotspot(simulator_input, overrides)

    assert 0.0 <= score <= 100.0
    assert category in {"Low", "Medium", "High", "Critical"}
