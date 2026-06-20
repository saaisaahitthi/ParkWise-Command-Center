from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.ml.allocation import AllocationInput, AllocationOptimizer, AllocationRequest
from app.repositories.allocation_repository import AllocationRepository


class AllocationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = AllocationRepository(db)
        self.optimizer = AllocationOptimizer()

    def generate_allocation(
        self,
        total_officers: int,
        allocation_date: date,
        shift_name: str = "default",
        horizon_days: int = 1,
        use_forecast: bool = True,
        max_hotspots: Optional[int] = None,
        min_officers_per_critical: int = 2,
        min_officers_per_high: int = 1,
        replace_existing: bool = True,
        pipeline_run_id: Optional[str] = None,
        commit: bool = True,
    ) -> Dict[str, Any]:
        if total_officers < 0:
            raise ValueError("total_officers must be non-negative")

        inputs = self._build_allocation_inputs(
            horizon_days=horizon_days,
            use_forecast=use_forecast,
            max_hotspots=max_hotspots,
        )

        request = AllocationRequest(
            total_officers=total_officers,
            allocation_date=allocation_date,
            shift_name=shift_name,
            min_officers_per_critical=min_officers_per_critical,
            min_officers_per_high=min_officers_per_high,
            use_forecast=use_forecast,
            max_hotspots=max_hotspots,
        )

        plan = self.optimizer.optimize(inputs, request)

        if replace_existing:
            self.repository.delete_existing_allocations(
                allocation_date=allocation_date,
                shift_name=shift_name,
            )

        rows = [
            self._candidate_to_db_row(
                candidate=candidate,
                allocation_date=allocation_date,
                total_officers=plan.total_officers,
                priority_rank=rank,
                pipeline_run_id=pipeline_run_id,
            )
            for rank, candidate in enumerate(plan.candidates, start=1)
        ]

        created = self.repository.bulk_create_allocations(rows, commit=False)

        if commit:
            self.db.commit()

        return {
            "status": "generated",
            "allocation_date": allocation_date,
            "shift_name": shift_name,
            "total_officers": plan.total_officers,
            "allocated_officers": plan.allocated_officers,
            "unallocated_officers": plan.unallocated_officers,
            "hotspots_covered": plan.hotspots_covered,
            "critical_hotspots_covered": plan.critical_hotspots_covered,
            "high_hotspots_covered": plan.high_hotspots_covered,
            "allocations_created": len(created),
            "summary": plan.summary,
            "allocations": [self._serialize_candidate(candidate) for candidate in plan.candidates],
        }

    def list_allocations(
        self,
        allocation_date: Optional[date] = None,
        shift_name: Optional[str] = None,
        hotspot_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        rows = self.repository.list_allocations(
            allocation_date=allocation_date,
            shift_name=shift_name,
            hotspot_id=hotspot_id,
            limit=limit,
            offset=offset,
        )
        return [self._serialize_allocation(row) for row in rows]

    def get_top_allocations(
        self,
        allocation_date: Optional[date] = None,
        shift_name: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        rows = self.repository.get_top_allocations(
            allocation_date=allocation_date,
            shift_name=shift_name,
            limit=limit,
        )
        return [self._serialize_allocation(row) for row in rows]

    def get_hotspot_allocations(
        self,
        hotspot_id: int,
        limit: int = 30,
    ) -> List[Dict[str, Any]]:
        rows = self.repository.get_hotspot_allocations(
            hotspot_id=hotspot_id,
            limit=limit,
        )
        return [self._serialize_allocation(row) for row in rows]

    def get_summary(
        self,
        allocation_date: Optional[date] = None,
        shift_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        return self.repository.get_summary(
            allocation_date=allocation_date,
            shift_name=shift_name,
        )

    def _build_allocation_inputs(
        self,
        horizon_days: int,
        use_forecast: bool,
        max_hotspots: Optional[int],
    ) -> List[AllocationInput]:
        eis_scores = self.repository.get_latest_eis_scores(limit=max_hotspots)
        forecasts = (
            self.repository.get_latest_forecasts(horizon_days=horizon_days)
            if use_forecast
            else []
        )

        forecast_by_hotspot = {int(row.hotspot_id): row for row in forecasts}
        hotspot_ids = [int(row.hotspot_id) for row in eis_scores if row.hotspot_id is not None]
        hotspot_map = self.repository.get_hotspots_by_ids(hotspot_ids)

        inputs: List[AllocationInput] = []

        for eis in eis_scores:
            hotspot_id = int(eis.hotspot_id)
            forecast = forecast_by_hotspot.get(hotspot_id)
            hotspot = hotspot_map.get(hotspot_id)

            inputs.append(
                AllocationInput(
                    hotspot_id=hotspot_id,
                    eis_score=float(eis.eis_score or 0.0),
                    risk_category=eis.risk_category or "Low",
                    forecasted_eis=float(forecast.predicted_eis) if forecast is not None else None,
                    forecasted_risk_category=(
                        forecast.predicted_risk_category if forecast is not None else None
                    ),
                    zone_id=self._get_hotspot_zone(hotspot),
                    hotspot_name=self._get_hotspot_name(hotspot),
                    latitude=self._get_hotspot_lat(hotspot),
                    longitude=self._get_hotspot_lng(hotspot),
                    current_violation_count=self._get_hotspot_violation_count(hotspot),
                    temporal_risk_score=float(eis.temporal_risk_score or 0.0),
                )
            )

        return inputs

    def _candidate_to_db_row(
        self,
        candidate: Any,
        allocation_date: date,
        total_officers: int,
        priority_rank: int,
        pipeline_run_id: Optional[str],
    ) -> Dict[str, Any]:
        return {
            "hotspot_id": candidate.hotspot_id,
            "officers_allocated": candidate.recommended_officers,
            "allocation_fraction": (
                candidate.recommended_officers / total_officers
                if total_officers > 0
                else 0.0
            ),
            "priority_rank": priority_rank,
            "deployment_window": None,
            "total_officers_available": total_officers,
            "eis_snapshot": candidate.combined_eis,
            "risk_category": candidate.risk_category,
            "allocation_date": datetime.combine(
                allocation_date,
                datetime.min.time(),
            ),
            "pipeline_run_id": pipeline_run_id,
        }

    def _serialize_candidate(self, candidate: Any) -> Dict[str, Any]:
        return {
            "hotspot_id": candidate.hotspot_id,
            "priority_score": candidate.priority_score,
            "combined_eis": candidate.combined_eis,
            "risk_category": candidate.risk_category,
            "forecasted_eis": candidate.forecasted_eis,
            "forecasted_risk_category": candidate.forecasted_risk_category,
            "zone_id": candidate.zone_id,
            "hotspot_name": candidate.hotspot_name,
            "latitude": candidate.latitude,
            "longitude": candidate.longitude,
            "recommended_officers": candidate.recommended_officers,
            "reason_codes": candidate.reason_codes,
        }

    def _serialize_allocation(self, row: Any) -> Dict[str, Any]:
        return {
            "allocation_id": getattr(row, "id", None),
            "hotspot_id": getattr(row, "hotspot_id", None),
            "allocation_date": getattr(row, "allocation_date", None),
            "officers_allocated": getattr(row, "officers_allocated", None),
            "allocation_fraction": getattr(row, "allocation_fraction", None),
            "priority_rank": getattr(row, "priority_rank", None),
            "deployment_window": getattr(row, "deployment_window", None),
            "total_officers_available": getattr(
                row,
                "total_officers_available",
                None,
            ),
            "risk_category": getattr(row, "risk_category", None),
            "eis_snapshot": getattr(row, "eis_snapshot", None),
            "pipeline_run_id": getattr(row, "pipeline_run_id", None),
            "created_at": getattr(row, "created_at", None),
        }

    def _get_hotspot_zone(self, hotspot: Any) -> Optional[str]:
        if hotspot is None:
            return None
        return (
            getattr(hotspot, "zone_id", None)
            or getattr(hotspot, "zone", None)
            or getattr(hotspot, "hotspot_type", None)
        )

    def _get_hotspot_name(self, hotspot: Any) -> Optional[str]:
        if hotspot is None:
            return None
        return (
            getattr(hotspot, "name", None)
            or getattr(hotspot, "junction_name", None)
            or getattr(hotspot, "hotspot_name", None)
            or f"Hotspot {getattr(hotspot, 'id', '')}"
        )

    def _get_hotspot_lat(self, hotspot: Any) -> Optional[float]:
        if hotspot is None:
            return None
        value = getattr(hotspot, "centroid_lat", None) or getattr(hotspot, "latitude", None)
        return float(value) if value is not None else None

    def _get_hotspot_lng(self, hotspot: Any) -> Optional[float]:
        if hotspot is None:
            return None
        value = (
            getattr(hotspot, "centroid_lng", None)
            or getattr(hotspot, "centroid_lon", None)
            or getattr(hotspot, "longitude", None)
        )
        return float(value) if value is not None else None

    def _get_hotspot_violation_count(self, hotspot: Any) -> Optional[int]:
        if hotspot is None:
            return None
        value = getattr(hotspot, "total_violations", None)
        return int(value) if value is not None else None
