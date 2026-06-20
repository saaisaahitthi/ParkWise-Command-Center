"""
app/ml/simulator/eis_simulator.py
──────────────────────────────────
EIS simulation engine for what-if scenarios.

Applies hypothetical overrides to EIS components in-memory to simulate
the impact of enforcement changes, severity adjustments, and other factors.

EIS formula (FROZEN from Phase 3):
    Exposure     = 0.35×frequency + 0.20×recurrence + 0.25×density + 0.20×temporal_risk
    Multiplier   = 0.6 + (0.8 × severity_norm)
    EIS          = Exposure × Multiplier   (scaled 0–100)
"""

from __future__ import annotations

from typing import Optional

from app.ml.simulator.types import SimulatorInput, SimulatorOverrides


class EISSimulator:
    """
    Pure Python EIS simulation engine.

    Applies overrides to component scores and recalculates EIS and risk category
    without modifying the database or any persistent state.
    """

    # EIS formula weights (frozen from constants)
    FREQUENCY_WEIGHT = 0.35
    RECURRENCE_WEIGHT = 0.20
    DENSITY_WEIGHT = 0.25
    TEMPORAL_RISK_WEIGHT = 0.20

    # Severity multiplier: 0.6 + (0.8 × severity_norm)
    SEVERITY_BASE = 0.6
    SEVERITY_SCALE = 0.8

    @staticmethod
    def simulate_hotspot(
        input_data: SimulatorInput,
        overrides: SimulatorOverrides,
    ) -> tuple[float, str]:
        """
        Simulate EIS and risk category for a hotspot with given overrides.

        Args:
            input_data: Current hotspot data with baseline components
            overrides: Simulation parameter changes

        Returns:
            (simulated_eis, simulated_risk_category)
            EIS is 0–100, risk_category is "Low" | "Medium" | "High" | "Critical"
        """
        # Apply overrides to component scores (all normalized to 0–1)
        frequency = EISSimulator._apply_reduction(
            input_data.frequency_score,
            overrides.frequency_reduction_pct,
        )
        recurrence = input_data.recurrence_score
        density = input_data.density_score
        temporal_risk = EISSimulator._apply_reduction(
            input_data.temporal_risk_score,
            overrides.temporal_risk_reduction_pct,
        )
        severity_norm = input_data.severity_norm

        # Recalculate exposure (all components are 0–1)
        exposure = (
            EISSimulator.FREQUENCY_WEIGHT * frequency
            + EISSimulator.RECURRENCE_WEIGHT * recurrence
            + EISSimulator.DENSITY_WEIGHT * density
            + EISSimulator.TEMPORAL_RISK_WEIGHT * temporal_risk
        )

        # Calculate severity multiplier
        severity_multiplier = EISSimulator.SEVERITY_BASE + (
            EISSimulator.SEVERITY_SCALE * severity_norm
        )

        # Apply severity_multiplier_delta if provided
        if overrides.severity_multiplier_delta is not None:
            severity_multiplier += overrides.severity_multiplier_delta

        # Apply enforcement_intensity if provided (affects multiplier)
        if overrides.enforcement_intensity is not None:
            severity_multiplier *= overrides.enforcement_intensity

        # Calculate EIS (0–1 scale)
        eis_normalized = exposure * severity_multiplier

        # Scale to 0–100
        eis_score = EISSimulator.normalize_score(eis_normalized * 100.0)

        # Determine risk category
        risk_category = EISSimulator.risk_category_from_score(eis_score)

        return eis_score, risk_category

    @staticmethod
    def _apply_reduction(
        base_value: float,
        reduction_pct: Optional[float],
    ) -> float:
        """
        Apply a percentage reduction to a normalized score.

        Args:
            base_value: Score between 0–1
            reduction_pct: Reduction percentage (0.0–1.0; 0.2 = 20% reduction)

        Returns:
            Reduced value, clamped to 0–1
        """
        if reduction_pct is None or reduction_pct <= 0.0:
            return base_value

        reduction_pct = EISSimulator.clamp(reduction_pct, 0.0, 1.0)
        return base_value * (1.0 - reduction_pct)

    @staticmethod
    def risk_category_from_score(score: float) -> str:
        """
        Determine risk category based on EIS score.

        Args:
            score: EIS score (0–100)

        Returns:
            "Critical" | "High" | "Medium" | "Low"
        """
        score = EISSimulator.normalize_score(score)

        if score >= 75.0:
            return "Critical"
        if score >= 50.0:
            return "High"
        if score >= 25.0:
            return "Medium"

        return "Low"

    @staticmethod
    def normalize_score(value: Optional[float]) -> float:
        """
        Normalize a score to 0–100 range.

        Handles both 0–1 (percentile) and 0–100 (percentage) formats.

        Args:
            value: Score to normalize

        Returns:
            Normalized score (0–100)
        """
        if value is None:
            return 0.0

        value = float(value)

        # If value is 0–1.5 range, scale to 0–100
        if value <= 1.5:
            value *= 100.0

        return EISSimulator.clamp(value, 0.0, 100.0)

    @staticmethod
    def clamp(value: float, min_value: float, max_value: float) -> float:
        """
        Clamp a value between min and max.

        Args:
            value: Value to clamp
            min_value: Minimum bound
            max_value: Maximum bound

        Returns:
            Clamped value
        """
        return max(min_value, min(max_value, float(value)))
