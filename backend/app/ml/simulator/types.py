"""
app/ml/simulator/types.py
──────────────────────────
Data types for the What-If Simulator.

Defines immutable request types and result types for scenario-based EIS
and allocation simulations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class SimulatorOverrides:
    """
    Configuration overrides for a simulation scenario.

    Allows users to test hypothetical changes to enforcement parameters,
    officer availability, and other factors to see simulated impact.
    """

    total_officers: Optional[int] = None
    """Total officers available to reallocate (if None, uses current allocation)."""

    enforcement_intensity: Optional[float] = None
    """Multiplier for enforcement effectiveness (0.5 = 50% intensity, 1.5 = 150%)."""

    severity_multiplier_delta: Optional[float] = None
    """Adjustment to severity multiplier (e.g., +0.1 to increase penalties by 10%)."""

    frequency_reduction_pct: Optional[float] = None
    """Simulated reduction in violation frequency (0.0–1.0, 0.2 = 20% reduction)."""

    temporal_risk_reduction_pct: Optional[float] = None
    """Simulated reduction in temporal risk (0.0–1.0)."""

    forecast_horizon_days: Optional[int] = None
    """Forecast horizon for prediction (overrides default)."""

    target_hotspot_ids: Optional[List[int]] = None
    """If specified, only simulate these hotspots; others use baseline."""

    critical_min_officers: Optional[int] = None
    """Minimum officers for Critical hotspots (overrides default 2)."""

    high_min_officers: Optional[int] = None
    """Minimum officers for High hotspots (overrides default 1)."""


@dataclass(frozen=True)
class SimulatorInput:
    """
    Input data for simulating a single hotspot.

    Combines current EIS components, current allocations, and optional
    forecast data for scenario analysis.
    """

    hotspot_id: int
    """Unique hotspot identifier."""

    current_eis: float
    """Current EIS score (0–100 or 0–1, will be normalized)."""

    current_risk_category: str
    """Current risk category (Low | Medium | High | Critical)."""

    frequency_score: float
    """Normalized frequency score (0–1)."""

    recurrence_score: float
    """Normalized recurrence score (0–1)."""

    density_score: float
    """Normalized density score (0–1)."""

    temporal_risk_score: float
    """Normalized temporal risk score (0–1)."""

    severity_norm: float
    """Normalized severity (0–1)."""

    exposure_score: Optional[float] = None
    """Cached exposure score (0–1), recalculated if None."""

    severity_multiplier: Optional[float] = None
    """Cached severity multiplier (0.6–1.4), recalculated if None."""

    forecasted_eis: Optional[float] = None
    """Predicted future EIS score (0–100 or 0–1), if available."""

    forecasted_risk_category: Optional[str] = None
    """Predicted future risk category, if available."""

    officers_allocated: Optional[int] = None
    """Currently allocated officers."""

    hotspot_name: Optional[str] = None
    """Human-readable hotspot name."""

    zone_id: Optional[str] = None
    """Zone identifier for grouping."""


@dataclass
class SimulatedHotspotResult:
    """
    Result of simulating a single hotspot.

    Compares baseline (current) vs simulated (after overrides) metrics
    to show impact of proposed changes.
    """

    hotspot_id: int
    """Unique hotspot identifier."""

    hotspot_name: Optional[str] = None
    """Human-readable hotspot name."""

    zone_id: Optional[str] = None
    """Zone identifier."""

    baseline_eis: float = 0.0
    """Baseline (current) EIS score (0–100)."""

    simulated_eis: float = 0.0
    """Simulated EIS score after overrides (0–100)."""

    baseline_risk_category: str = "Low"
    """Baseline risk category."""

    simulated_risk_category: str = "Low"
    """Simulated risk category."""

    eis_delta: float = 0.0
    """Change in EIS (simulated - baseline); negative = improvement."""

    risk_delta_label: str = "unchanged"
    """Change in risk category: improved | worsened | unchanged."""

    baseline_officers: int = 0
    """Baseline officer allocation."""

    simulated_officers: int = 0
    """Simulated officer allocation."""

    officer_delta: int = 0
    """Change in officer count (simulated - baseline)."""

    impact_notes: List[str] = field(default_factory=list)
    """Human-readable notes explaining the simulation results."""


@dataclass
class SimulationResult:
    """
    Result of a complete what-if simulation across all hotspots.

    Provides high-level summary and detailed breakdown for dashboard display.
    """

    scenario_name: str
    """Name of the simulation scenario (e.g., 'Increase Officers to 100')."""

    total_hotspots: int = 0
    """Total hotspots simulated."""

    improved_hotspots: int = 0
    """Number of hotspots with improved EIS."""

    worsened_hotspots: int = 0
    """Number of hotspots with worse EIS."""

    unchanged_hotspots: int = 0
    """Number of hotspots with no EIS change."""

    baseline_average_eis: float = 0.0
    """Average baseline EIS across all hotspots."""

    simulated_average_eis: float = 0.0
    """Average simulated EIS after overrides."""

    average_eis_delta: float = 0.0
    """Change in average EIS (simulated - baseline); negative = improvement."""

    baseline_total_officers: int = 0
    """Total baseline officers across all hotspots."""

    simulated_total_officers: int = 0
    """Total simulated officers after redistribution."""

    hotspot_results: List[SimulatedHotspotResult] = field(default_factory=list)
    """Detailed results for each hotspot."""

    summary: Dict[str, Any] = field(default_factory=dict)
    """Additional aggregate statistics and metadata."""
