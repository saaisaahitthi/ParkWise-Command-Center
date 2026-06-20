"""
app/schemas/simulator.py
────────────────────────
Pydantic schemas for the What-If Simulator (Feature 8).
"""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class SimulationScenario(BaseModel):
    """
    Input parameters for a what-if simulation run.
    All fields are optional — only the ones provided are applied.
    """
    violation_reduction_pct: Optional[float] = Field(
        None, ge=0, le=100,
        description="Simulate a X% reduction in violations (e.g., via enforcement surge)",
    )
    officer_increase: Optional[int] = Field(
        None, ge=0,
        description="Additional officers added to the deployment pool",
    )
    hotspot_coverage_increase_pct: Optional[float] = Field(
        None, ge=0, le=100,
        description="Increase patrol coverage of hotspots by X%",
    )
    target_hotspot_ids: Optional[List[int]] = Field(
        None,
        description="Limit simulation to specific hotspot IDs. Default: all hotspots.",
    )
    total_officers_baseline: int = Field(
        default=20, ge=1,
        description="Baseline officer count before applying officer_increase",
    )


class SimulatedHotspotResult(BaseModel):
    hotspot_id:           int
    hotspot_name:         Optional[str]
    baseline_eis:         float
    simulated_eis:        float
    eis_delta:            float
    baseline_rank:        Optional[int]
    simulated_rank:       Optional[int]
    rank_delta:           Optional[int]
    baseline_risk:        str
    simulated_risk:       str
    risk_changed:         bool


class SimulationResult(BaseModel):
    scenario:                  SimulationScenario
    total_hotspots_affected:   int
    avg_eis_before:            float
    avg_eis_after:             float
    avg_eis_delta:             float
    critical_before:           int
    critical_after:            int
    high_before:               int
    high_after:                int
    hotspot_results:           List[SimulatedHotspotResult]
    simulation_notes:          Optional[str] = None
