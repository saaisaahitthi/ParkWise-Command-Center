"""
app/ml/simulator/__init__.py
─────────────────────────────
Public API for the What-If Simulator module.

Exports all types and simulator classes for scenario-based analysis
of enforcement policy changes and their impact.
"""

from app.ml.simulator.allocation_simulator import AllocationSimulator
from app.ml.simulator.eis_simulator import EISSimulator
from app.ml.simulator.impact_calculator import ImpactCalculator
from app.ml.simulator.types import (
    SimulatedHotspotResult,
    SimulationResult,
    SimulatorInput,
    SimulatorOverrides,
)

__all__ = [
    # Types
    "SimulatorOverrides",
    "SimulatorInput",
    "SimulatedHotspotResult",
    "SimulationResult",
    # Engines
    "EISSimulator",
    "AllocationSimulator",
    "ImpactCalculator",
]
