"""
app/ml/simulator/impact_calculator.py
──────────────────────────────────────
Impact calculation engine for what-if scenarios.

Compares baseline vs simulated metrics and generates comprehensive
impact analysis including improvement/degradation counts and notes.
"""

from __future__ import annotations

from typing import List

from app.ml.simulator.allocation_simulator import AllocationSimulator
from app.ml.simulator.eis_simulator import EISSimulator
from app.ml.simulator.types import (
    SimulatedHotspotResult,
    SimulationResult,
    SimulatorInput,
    SimulatorOverrides,
)


class ImpactCalculator:
    """
    Pure Python impact calculation engine.

    Orchestrates EIS and allocation simulation, then computes aggregate
    metrics and generates impact notes for dashboard display.
    """

    @staticmethod
    def calculate(
        scenario_name: str,
        inputs: List[SimulatorInput],
        overrides: SimulatorOverrides,
    ) -> SimulationResult:
        """
        Execute full simulation and calculate impact across all hotspots.

        Args:
            scenario_name: Name of the simulation scenario
            inputs: List of hotspot simulation inputs
            overrides: Simulation parameter overrides

        Returns:
            Comprehensive SimulationResult with aggregates and details
        """
        # Step 1: Simulate EIS for each hotspot
        results = []
        for input_data in inputs:
            simulated_eis, simulated_category = EISSimulator.simulate_hotspot(
                input_data=input_data,
                overrides=overrides,
            )

            baseline_eis = EISSimulator.normalize_score(input_data.current_eis)

            result = SimulatedHotspotResult(
                hotspot_id=input_data.hotspot_id,
                hotspot_name=input_data.hotspot_name,
                zone_id=input_data.zone_id,
                baseline_eis=baseline_eis,
                simulated_eis=simulated_eis,
                baseline_risk_category=input_data.current_risk_category,
                simulated_risk_category=simulated_category,
                eis_delta=simulated_eis - baseline_eis,
                baseline_officers=input_data.officers_allocated or 0,
                simulated_officers=input_data.officers_allocated or 0,
            )

            # Determine risk delta label
            result.risk_delta_label = ImpactCalculator._risk_delta_label(
                baseline=input_data.current_risk_category,
                simulated=simulated_category,
            )

            results.append(result)

        # Step 2: Simulate allocations (if overrides.total_officers is set)
        results = AllocationSimulator.simulate_allocations(
            results=results,
            overrides=overrides,
        )

        # Step 3: Calculate impact metrics
        return ImpactCalculator._build_simulation_result(
            scenario_name=scenario_name,
            results=results,
        )

    @staticmethod
    def _risk_delta_label(baseline: str, simulated: str) -> str:
        """
        Determine risk category change label.

        Args:
            baseline: Baseline risk category
            simulated: Simulated risk category

        Returns:
            "improved" | "worsened" | "unchanged"
        """
        risk_hierarchy = {
            "Low": 0,
            "Medium": 1,
            "High": 2,
            "Critical": 3,
        }

        baseline_level = risk_hierarchy.get(baseline, 0)
        simulated_level = risk_hierarchy.get(simulated, 0)

        if simulated_level < baseline_level:
            return "improved"
        if simulated_level > baseline_level:
            return "worsened"

        return "unchanged"

    @staticmethod
    def _build_simulation_result(
        scenario_name: str,
        results: List[SimulatedHotspotResult],
    ) -> SimulationResult:
        """
        Build aggregated SimulationResult from detailed results.

        Args:
            scenario_name: Scenario name
            results: Hotspot-level results

        Returns:
            Aggregated simulation result
        """
        total_hotspots = len(results)

        improved = sum(1 for r in results if r.risk_delta_label == "improved")
        worsened = sum(1 for r in results if r.risk_delta_label == "worsened")
        unchanged = sum(1 for r in results if r.risk_delta_label == "unchanged")

        baseline_average_eis = (
            sum(r.baseline_eis for r in results) / total_hotspots
            if total_hotspots > 0
            else 0.0
        )
        simulated_average_eis = (
            sum(r.simulated_eis for r in results) / total_hotspots
            if total_hotspots > 0
            else 0.0
        )

        average_eis_delta = simulated_average_eis - baseline_average_eis

        baseline_total_officers = sum(r.baseline_officers for r in results)
        simulated_total_officers = sum(r.simulated_officers for r in results)

        # Generate impact notes for each hotspot
        for result in results:
            notes = ImpactCalculator._generate_impact_notes(result)
            result.impact_notes = notes

        # Build summary dict
        summary = {
            "improvement_percentage": (
                (improved / total_hotspots * 100) if total_hotspots > 0 else 0.0
            ),
            "degradation_percentage": (
                (worsened / total_hotspots * 100) if total_hotspots > 0 else 0.0
            ),
            "total_eis_reduction": -average_eis_delta,  # Negative delta = improvement
            "critical_hotspots_improved": sum(
                1 for r in results
                if r.baseline_risk_category == "Critical"
                and r.risk_delta_label == "improved"
            ),
            "high_hotspots_improved": sum(
                1 for r in results
                if r.baseline_risk_category == "High"
                and r.risk_delta_label == "improved"
            ),
            "officers_added": max(0, simulated_total_officers - baseline_total_officers),
            "officers_removed": max(0, baseline_total_officers - simulated_total_officers),
        }

        return SimulationResult(
            scenario_name=scenario_name,
            total_hotspots=total_hotspots,
            improved_hotspots=improved,
            worsened_hotspots=worsened,
            unchanged_hotspots=unchanged,
            baseline_average_eis=round(baseline_average_eis, 2),
            simulated_average_eis=round(simulated_average_eis, 2),
            average_eis_delta=round(average_eis_delta, 2),
            baseline_total_officers=baseline_total_officers,
            simulated_total_officers=simulated_total_officers,
            hotspot_results=results,
            summary=summary,
        )

    @staticmethod
    def _generate_impact_notes(result: SimulatedHotspotResult) -> List[str]:
        """
        Generate human-readable impact notes for a hotspot result.

        Args:
            result: Hotspot simulation result

        Returns:
            List of note strings
        """
        notes = []

        # EIS change
        eis_abs = abs(result.eis_delta)
        if result.eis_delta < -5:
            notes.append(
                f"EIS improved by {eis_abs:.1f} points ({result.eis_delta:.1f})"
            )
        elif result.eis_delta > 5:
            notes.append(
                f"EIS worsened by {eis_abs:.1f} points ({result.eis_delta:.1f})"
            )

        # Risk category change
        if result.risk_delta_label == "improved":
            notes.append(
                f"Risk improved from {result.baseline_risk_category} to {result.simulated_risk_category}"
            )
        elif result.risk_delta_label == "worsened":
            notes.append(
                f"Risk worsened from {result.baseline_risk_category} to {result.simulated_risk_category}"
            )

        # Officer change
        if result.officer_delta > 0:
            notes.append(f"+{result.officer_delta} officer(s) allocated")
        elif result.officer_delta < 0:
            notes.append(f"{result.officer_delta} officer(s) removed")

        # Edge cases
        if result.simulated_officers > 5:
            notes.append(f"High officer concentration: {result.simulated_officers} officers")

        if result.simulated_eis >= 85 and result.simulated_risk_category == "Critical":
            notes.append("Critical hotspot; requires immediate attention")

        return notes
