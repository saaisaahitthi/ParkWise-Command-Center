from __future__ import annotations

from app.ml.simulator import (
    AllocationSimulator,
    SimulatedHotspotResult,
    SimulatorOverrides,
)


def make_results() -> list[SimulatedHotspotResult]:
    return [
        SimulatedHotspotResult(
            hotspot_id=1,
            simulated_eis=90.0,
            simulated_risk_category="Critical",
            baseline_officers=3,
            simulated_officers=3,
        ),
        SimulatedHotspotResult(
            hotspot_id=2,
            simulated_eis=65.0,
            simulated_risk_category="High",
            baseline_officers=2,
            simulated_officers=2,
        ),
        SimulatedHotspotResult(
            hotspot_id=3,
            simulated_eis=35.0,
            simulated_risk_category="Medium",
            baseline_officers=1,
            simulated_officers=1,
        ),
    ]


def test_missing_total_officers_preserves_baseline_allocations() -> None:
    results = make_results()

    simulated = AllocationSimulator.simulate_allocations(
        results,
        SimulatorOverrides(),
    )

    assert [row.simulated_officers for row in simulated] == [3, 2, 1]


def test_total_officers_override_redistributes_officers() -> None:
    results = make_results()

    simulated = AllocationSimulator.simulate_allocations(
        results,
        SimulatorOverrides(total_officers=12),
    )

    assert any(
        row.simulated_officers != row.baseline_officers for row in simulated
    )


def test_critical_hotspots_receive_minimum_coverage() -> None:
    results = make_results()

    simulated = AllocationSimulator.simulate_allocations(
        results,
        SimulatorOverrides(total_officers=10, critical_min_officers=4),
    )
    critical = next(row for row in simulated if row.hotspot_id == 1)

    assert critical.simulated_officers >= 4


def test_high_hotspots_receive_minimum_when_officers_are_available() -> None:
    results = make_results()

    simulated = AllocationSimulator.simulate_allocations(
        results,
        SimulatorOverrides(
            total_officers=10,
            critical_min_officers=2,
            high_min_officers=3,
        ),
    )
    high = next(row for row in simulated if row.hotspot_id == 2)

    assert high.simulated_officers >= 3


def test_total_simulated_officers_do_not_exceed_requested_total() -> None:
    for requested in (0, 1, 5, 10, 25):
        simulated = AllocationSimulator.simulate_allocations(
            make_results(),
            SimulatorOverrides(total_officers=requested),
        )

        assert sum(row.simulated_officers for row in simulated) <= requested
