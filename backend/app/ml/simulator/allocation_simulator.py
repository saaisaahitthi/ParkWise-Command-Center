"""
app/ml/simulator/allocation_simulator.py
─────────────────────────────────────────
Officer allocation simulator for what-if scenarios.

Simulates how officers would be redistributed based on simulated EIS scores
and other factors, respecting minimum coverage constraints.
"""

from __future__ import annotations

from typing import List, Optional

from app.ml.simulator.eis_simulator import EISSimulator
from app.ml.simulator.types import (
    SimulatedHotspotResult,
    SimulatorOverrides,
)


class AllocationSimulator:
    """
    Pure Python allocation simulation engine.

    Redistributes officers based on simulated risk scores, respecting
    minimum coverage requirements for Critical and High hotspots.
    """

    # Default minimum officer requirements
    DEFAULT_CRITICAL_MIN = 2
    DEFAULT_HIGH_MIN = 1

    @staticmethod
    def simulate_allocations(
        results: List[SimulatedHotspotResult],
        overrides: SimulatorOverrides,
    ) -> List[SimulatedHotspotResult]:
        """
        Simulate officer allocations based on simulated risk scores.

        If total_officers override is specified, redistributes officers.
        Otherwise, returns baseline allocations unchanged.

        Args:
            results: Hotspot results with simulated EIS and risk categories
            overrides: Simulation overrides (includes total_officers)

        Returns:
            Updated results with simulated officer counts
        """
        if overrides.total_officers is None:
            # No redistribution; return baseline allocations
            return results

        # Redistribute officers based on simulated risk
        return AllocationSimulator.redistribute_by_risk(
            results=results,
            total_officers=overrides.total_officers,
            overrides=overrides,
        )

    @staticmethod
    def redistribute_by_risk(
        results: List[SimulatedHotspotResult],
        total_officers: int,
        overrides: SimulatorOverrides,
    ) -> List[SimulatedHotspotResult]:
        """
        Redistribute officers across hotspots based on simulated risk.

        Allocation strategy:
        1. First, allocate minimum officers to Critical hotspots
        2. Then, allocate minimum officers to High hotspots (if available)
        3. Distribute remaining officers proportionally by simulated EIS

        Args:
            results: Hotspot results with simulated EIS and risk categories
            total_officers: Total officers to distribute
            overrides: Simulation overrides (for min officers settings)

        Returns:
            Updated results with simulated officer allocations
        """
        total_officers = max(0, int(total_officers))

        # Get minimum officer requirements
        critical_min = overrides.critical_min_officers or AllocationSimulator.DEFAULT_CRITICAL_MIN
        high_min = overrides.high_min_officers or AllocationSimulator.DEFAULT_HIGH_MIN

        critical_min = max(0, int(critical_min))
        high_min = max(0, int(high_min))

        # Allocate minimum officers to Critical hotspots
        critical_hotspots = [
            r for r in results if r.simulated_risk_category == "Critical"
        ]
        high_hotspots = [
            r for r in results if r.simulated_risk_category == "High"
        ]

        # First pass: minimum allocations
        officers_remaining = total_officers
        allocations = {}

        for result in critical_hotspots:
            allocation = min(critical_min, officers_remaining)
            allocations[result.hotspot_id] = allocation
            officers_remaining -= allocation

        for result in high_hotspots:
            allocation = min(high_min, officers_remaining)
            allocations[result.hotspot_id] = allocation
            officers_remaining -= allocation

        # Second pass: distribute remaining officers by simulated EIS
        if officers_remaining > 0:
            allocations = AllocationSimulator._distribute_proportional(
                results=results,
                allocations=allocations,
                officers_remaining=officers_remaining,
            )

        # Apply allocations to results
        for result in results:
            result.simulated_officers = allocations.get(result.hotspot_id, 0)
            result.officer_delta = result.simulated_officers - result.baseline_officers

        return results

    @staticmethod
    def _distribute_proportional(
        results: List[SimulatedHotspotResult],
        allocations: dict,
        officers_remaining: int,
    ) -> dict:
        """
        Distribute remaining officers proportionally to simulated EIS.

        Args:
            results: Hotspot results
            allocations: Current allocation dict (hotspot_id → officers)
            officers_remaining: Officers left to allocate

        Returns:
            Updated allocations dict
        """
        officers_remaining = max(0, int(officers_remaining))

        if officers_remaining == 0:
            return allocations

        # Calculate total EIS for weighting
        total_eis = sum(r.simulated_eis for r in results)

        if total_eis <= 0:
            # If no EIS, distribute evenly
            per_hotspot = officers_remaining / len(results) if results else 0
            for result in results:
                current = allocations.get(result.hotspot_id, 0)
                additional = int(per_hotspot)
                allocations[result.hotspot_id] = current + additional
        else:
            # Distribute proportionally to EIS
            for result in results:
                eis_proportion = result.simulated_eis / total_eis
                additional = int(officers_remaining * eis_proportion)
                current = allocations.get(result.hotspot_id, 0)
                allocations[result.hotspot_id] = current + additional

        return allocations
