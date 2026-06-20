"""
What-If Simulator API.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.services.simulator_service import SimulatorService

router = APIRouter()


class SimulatorOverridesRequest(BaseModel):
    """Supported in-memory scenario overrides."""

    total_officers: Optional[int] = Field(default=None, ge=0)
    enforcement_intensity: Optional[float] = Field(default=None, gt=0)
    severity_multiplier_delta: Optional[float] = None
    frequency_reduction_pct: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    temporal_risk_reduction_pct: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )
    forecast_horizon_days: Optional[int] = Field(default=None, ge=1)
    target_hotspot_ids: Optional[List[int]] = Field(default=None, min_length=1)
    critical_min_officers: Optional[int] = Field(default=None, ge=0)
    high_min_officers: Optional[int] = Field(default=None, ge=0)


class RunSimulationRequest(BaseModel):
    """Request body for a what-if simulation."""

    scenario_name: str = Field(min_length=1, max_length=200)
    overrides: SimulatorOverridesRequest = Field(
        default_factory=SimulatorOverridesRequest
    )


@router.post(
    "/run",
    summary="Run a what-if simulation",
)
def run_simulation(
    payload: RunSimulationRequest,
    db: Session = Depends(db_session),
) -> Dict[str, Any]:
    """Run the simulator against the latest persisted analytics baseline."""
    try:
        service = SimulatorService(db)
        return service.run_simulation(
            scenario_name=payload.scenario_name,
            overrides=payload.overrides.model_dump(exclude_none=True),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/presets",
    summary="List what-if simulation presets",
)
def get_simulation_presets(
    db: Session = Depends(db_session),
) -> List[Dict[str, Any]]:
    """Return ready-to-use scenario definitions."""
    return SimulatorService(db).get_simulation_presets()


@router.get(
    "/baseline",
    summary="Get current simulator baseline inputs",
)
def get_simulation_baseline(
    target_hotspot_ids: Optional[str] = Query(
        default=None,
        description="Comma-separated hotspot IDs.",
    ),
    forecast_horizon_days: Optional[int] = Query(default=None, ge=1),
    db: Session = Depends(db_session),
) -> List[Dict[str, Any]]:
    """Return current EIS inputs with optional forecast and allocation context."""
    try:
        parsed_ids = _parse_hotspot_ids(target_hotspot_ids)
        inputs = SimulatorService(db).get_baseline_inputs(
            target_hotspot_ids=parsed_ids,
            forecast_horizon_days=forecast_horizon_days,
        )
        return [asdict(item) for item in inputs]
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


def _parse_hotspot_ids(value: Optional[str]) -> Optional[List[int]]:
    if value is None:
        return None

    parts = [part.strip() for part in value.split(",")]
    if not parts or any(not part for part in parts):
        raise ValueError(
            "target_hotspot_ids must be a comma-separated list of positive integers."
        )

    try:
        hotspot_ids = [int(part) for part in parts]
    except ValueError as exc:
        raise ValueError(
            "target_hotspot_ids must be a comma-separated list of positive integers."
        ) from exc

    if any(hotspot_id <= 0 for hotspot_id in hotspot_ids):
        raise ValueError("target_hotspot_ids must contain positive integers only.")
    return list(dict.fromkeys(hotspot_ids))
