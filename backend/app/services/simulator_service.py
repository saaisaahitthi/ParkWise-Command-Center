"""
Read-only service layer for the What-If Simulator.
"""

from __future__ import annotations

from dataclasses import asdict
from math import ceil, isfinite
from typing import Any, Dict, List, Mapping, Optional, Sequence

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.ml.simulator import (
    ImpactCalculator,
    SimulatorInput,
    SimulatorOverrides,
)
from app.models.analytics import Allocation, EISScore, Forecast
from app.models.hotspot import Hotspot


class SimulatorService:
    """Build simulator inputs from current analytics data without DB writes."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def run_simulation(
        self,
        scenario_name: str,
        overrides: SimulatorOverrides | Mapping[str, Any],
    ) -> Dict[str, Any]:
        """Run an in-memory scenario and return dashboard-ready data."""
        scenario_name = scenario_name.strip()
        if not scenario_name:
            raise ValueError("scenario_name must not be empty.")

        validated_overrides = self.validate_overrides(overrides)
        inputs = self.get_baseline_inputs(
            target_hotspot_ids=validated_overrides.target_hotspot_ids,
            forecast_horizon_days=validated_overrides.forecast_horizon_days,
        )
        result = ImpactCalculator.calculate(
            scenario_name=scenario_name,
            inputs=inputs,
            overrides=validated_overrides,
        )
        return asdict(result)

    def get_baseline_inputs(
        self,
        target_hotspot_ids: Optional[Sequence[int]] = None,
        forecast_horizon_days: Optional[int] = None,
    ) -> List[SimulatorInput]:
        """Return the latest EIS baseline enriched with forecast/allocation data."""
        hotspot_ids = self._validate_hotspot_ids(target_hotspot_ids)
        if forecast_horizon_days is not None and forecast_horizon_days < 1:
            raise ValueError("forecast_horizon_days must be at least 1.")

        latest_eis = (
            self.db.query(
                EISScore.hotspot_id,
                func.max(EISScore.id).label("latest_id"),
            )
            .group_by(EISScore.hotspot_id)
        )
        if hotspot_ids is not None:
            latest_eis = latest_eis.filter(EISScore.hotspot_id.in_(hotspot_ids))
        latest_eis = latest_eis.subquery()

        rows = (
            self.db.query(EISScore, Hotspot)
            .join(latest_eis, EISScore.id == latest_eis.c.latest_id)
            .join(Hotspot, Hotspot.id == EISScore.hotspot_id)
            .order_by(EISScore.eis_score.desc(), EISScore.hotspot_id.asc())
            .all()
        )
        if not rows:
            raise ValueError(
                "No EIS scores are available for the requested hotspots. "
                "Run the EIS pipeline first."
            )

        selected_ids = [int(eis.hotspot_id) for eis, _ in rows]
        forecasts = self._get_latest_forecasts(
            hotspot_ids=selected_ids,
            forecast_horizon_days=forecast_horizon_days,
        )
        allocations = self._get_latest_allocations(selected_ids)

        return [
            SimulatorInput(
                hotspot_id=int(eis.hotspot_id),
                hotspot_name=hotspot.hotspot_name,
                zone_id=hotspot.zone_id,
                current_eis=float(eis.eis_score),
                current_risk_category=eis.risk_category,
                frequency_score=float(eis.frequency_score),
                recurrence_score=float(eis.recurrence_score),
                density_score=float(eis.density_score),
                temporal_risk_score=float(eis.temporal_risk_score),
                severity_norm=float(eis.severity_norm),
                exposure_score=float(eis.exposure_score),
                severity_multiplier=float(eis.severity_multiplier),
                forecasted_eis=(
                    float(forecasts[eis.hotspot_id].predicted_eis)
                    if eis.hotspot_id in forecasts
                    else None
                ),
                forecasted_risk_category=(
                    forecasts[eis.hotspot_id].predicted_risk_category
                    if eis.hotspot_id in forecasts
                    else None
                ),
                officers_allocated=(
                    int(allocations[eis.hotspot_id].officers_allocated)
                    if eis.hotspot_id in allocations
                    else None
                ),
            )
            for eis, hotspot in rows
        ]

    def get_simulation_presets(self) -> List[Dict[str, Any]]:
        """Return ready-to-use scenarios based on the current officer baseline."""
        baseline_officers = self._get_baseline_officer_total()
        effective_baseline = baseline_officers or 20

        return [
            {
                "name": "Increase officers by 20%",
                "description": "Redistribute a 20% larger officer pool by simulated risk.",
                "overrides": {
                    "total_officers": ceil(effective_baseline * 1.20),
                },
            },
            {
                "name": "Reduce frequency by 15%",
                "description": "Model a 15% reduction in violation frequency.",
                "overrides": {
                    "frequency_reduction_pct": 0.15,
                },
            },
            {
                "name": "Reduce temporal risk by 20%",
                "description": "Model a 20% reduction in peak-window temporal risk.",
                "overrides": {
                    "temporal_risk_reduction_pct": 0.20,
                },
            },
            {
                "name": "Critical hotspot surge deployment",
                "description": "Expand the pool and guarantee stronger Critical/High coverage.",
                "overrides": {
                    "total_officers": ceil(effective_baseline * 1.25),
                    "critical_min_officers": 4,
                    "high_min_officers": 2,
                    "enforcement_intensity": 1.10,
                },
            },
            {
                "name": "Low enforcement scenario",
                "description": "Model reduced enforcement intensity and officer availability.",
                "overrides": {
                    "total_officers": max(0, int(effective_baseline * 0.80)),
                    "enforcement_intensity": 0.75,
                },
            },
        ]

    def validate_overrides(
        self,
        overrides: SimulatorOverrides | Mapping[str, Any],
    ) -> SimulatorOverrides:
        """Validate and normalize API/service override values."""
        if isinstance(overrides, SimulatorOverrides):
            validated = overrides
        elif isinstance(overrides, Mapping):
            try:
                validated = SimulatorOverrides(**dict(overrides))
            except TypeError as exc:
                raise ValueError(f"Invalid simulator overrides: {exc}") from exc
        else:
            raise ValueError("overrides must be a SimulatorOverrides object or mapping.")

        self._validate_non_negative_int("total_officers", validated.total_officers)
        self._validate_non_negative_int(
            "critical_min_officers", validated.critical_min_officers
        )
        self._validate_non_negative_int(
            "high_min_officers", validated.high_min_officers
        )

        if (
            validated.enforcement_intensity is not None
            and (
                not isfinite(validated.enforcement_intensity)
                or validated.enforcement_intensity <= 0
            )
        ):
            raise ValueError("enforcement_intensity must be a finite value greater than 0.")

        if (
            validated.severity_multiplier_delta is not None
            and not isfinite(validated.severity_multiplier_delta)
        ):
            raise ValueError("severity_multiplier_delta must be finite.")

        self._validate_reduction(
            "frequency_reduction_pct", validated.frequency_reduction_pct
        )
        self._validate_reduction(
            "temporal_risk_reduction_pct",
            validated.temporal_risk_reduction_pct,
        )

        if (
            validated.forecast_horizon_days is not None
            and validated.forecast_horizon_days < 1
        ):
            raise ValueError("forecast_horizon_days must be at least 1.")

        self._validate_hotspot_ids(validated.target_hotspot_ids)
        return validated

    def _get_latest_forecasts(
        self,
        hotspot_ids: Sequence[int],
        forecast_horizon_days: Optional[int],
    ) -> Dict[int, Forecast]:
        forecasts: Dict[int, Forecast] = {}

        if forecast_horizon_days is not None:
            matching_forecasts = self._latest_forecasts_for_ids(
                hotspot_ids=hotspot_ids,
                forecast_horizon_days=forecast_horizon_days,
            )
            forecasts = {**forecasts, **matching_forecasts}

        missing_ids = [
            hotspot_id for hotspot_id in hotspot_ids if hotspot_id not in forecasts
        ]
        if missing_ids:
            fallback_forecasts = self._latest_forecasts_for_ids(
                hotspot_ids=missing_ids,
                forecast_horizon_days=None,
            )
            forecasts = {**forecasts, **fallback_forecasts}
        return forecasts

    def _latest_forecasts_for_ids(
        self,
        hotspot_ids: Sequence[int],
        forecast_horizon_days: Optional[int],
    ) -> Dict[int, Forecast]:
        latest = (
            self.db.query(
                Forecast.hotspot_id,
                func.max(Forecast.id).label("latest_id"),
            )
            .filter(Forecast.hotspot_id.in_(hotspot_ids))
        )
        if forecast_horizon_days is not None:
            latest = latest.filter(Forecast.horizon_days == forecast_horizon_days)
        latest = latest.group_by(Forecast.hotspot_id).subquery()

        rows = (
            self.db.query(Forecast)
            .join(latest, Forecast.id == latest.c.latest_id)
            .all()
        )
        return {int(row.hotspot_id): row for row in rows}

    def _get_latest_allocations(
        self,
        hotspot_ids: Sequence[int],
    ) -> Dict[int, Allocation]:
        if not hotspot_ids:
            return {}

        latest = (
            self.db.query(
                Allocation.hotspot_id,
                func.max(Allocation.id).label("latest_id"),
            )
            .filter(Allocation.hotspot_id.in_(hotspot_ids))
            .group_by(Allocation.hotspot_id)
            .subquery()
        )
        rows = (
            self.db.query(Allocation)
            .join(latest, Allocation.id == latest.c.latest_id)
            .all()
        )
        return {int(row.hotspot_id): row for row in rows}

    def _get_baseline_officer_total(self) -> int:
        hotspot_ids = [
            row[0]
            for row in self.db.query(Allocation.hotspot_id).distinct().all()
        ]
        allocations = self._get_latest_allocations(hotspot_ids)
        return sum(int(row.officers_allocated) for row in allocations.values())

    @staticmethod
    def _validate_hotspot_ids(
        target_hotspot_ids: Optional[Sequence[int]],
    ) -> Optional[List[int]]:
        if target_hotspot_ids is None:
            return None

        hotspot_ids = list(dict.fromkeys(target_hotspot_ids))
        if not hotspot_ids:
            raise ValueError("target_hotspot_ids must contain at least one hotspot ID.")
        if any(not isinstance(value, int) or isinstance(value, bool) or value <= 0
               for value in hotspot_ids):
            raise ValueError("target_hotspot_ids must contain positive integers only.")
        return hotspot_ids

    @staticmethod
    def _validate_non_negative_int(name: str, value: Optional[int]) -> None:
        if value is not None and (
            not isinstance(value, int) or isinstance(value, bool) or value < 0
        ):
            raise ValueError(f"{name} must be a non-negative integer.")

    @staticmethod
    def _validate_reduction(name: str, value: Optional[float]) -> None:
        if value is not None and (not isfinite(value) or not 0.0 <= value <= 1.0):
            raise ValueError(f"{name} must be between 0.0 and 1.0.")
