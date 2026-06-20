from __future__ import annotations

from datetime import date, datetime, time
from typing import Any, Dict, List, Optional, Sequence

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models.analytics import Allocation, EISScore, Forecast
from app.models.hotspot import Hotspot


class AllocationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_latest_eis_scores(self, limit: Optional[int] = None) -> List[EISScore]:
        latest_dates = (
            self.db.query(
                EISScore.hotspot_id.label("hotspot_id"),
                func.max(EISScore.computed_for_date).label("latest_date"),
            )
            .group_by(EISScore.hotspot_id)
            .subquery()
        )

        query = (
            self.db.query(EISScore)
            .join(
                latest_dates,
                (EISScore.hotspot_id == latest_dates.c.hotspot_id)
                & (EISScore.computed_for_date == latest_dates.c.latest_date),
            )
            .order_by(desc(EISScore.eis_score))
        )

        if limit is not None:
            query = query.limit(limit)

        return list(query.all())

    def get_latest_forecasts(
        self,
        horizon_days: int = 1,
        limit: Optional[int] = None,
    ) -> List[Forecast]:
        latest_dates = (
            self.db.query(
                Forecast.hotspot_id.label("hotspot_id"),
                func.max(Forecast.forecast_date).label("latest_date"),
            )
            .filter(Forecast.horizon_days == horizon_days)
            .group_by(Forecast.hotspot_id)
            .subquery()
        )

        query = (
            self.db.query(Forecast)
            .join(
                latest_dates,
                (Forecast.hotspot_id == latest_dates.c.hotspot_id)
                & (Forecast.forecast_date == latest_dates.c.latest_date),
            )
            .filter(Forecast.horizon_days == horizon_days)
            .order_by(desc(Forecast.predicted_eis))
        )

        if limit is not None:
            query = query.limit(limit)

        return list(query.all())

    def get_hotspots_by_ids(self, hotspot_ids: Sequence[int]) -> Dict[int, Hotspot]:
        if not hotspot_ids:
            return {}

        rows = self.db.query(Hotspot).filter(Hotspot.id.in_(list(set(hotspot_ids)))).all()
        return {int(row.id): row for row in rows}

    def delete_existing_allocations(
        self,
        allocation_date: date,
        shift_name: Optional[str] = None,
        pipeline_run_id: Optional[str] = None,
    ) -> int:
        query = self.db.query(Allocation)

        if hasattr(Allocation, "allocation_date"):
            query = query.filter(
                func.date(Allocation.allocation_date) == allocation_date
            )

        if pipeline_run_id is not None and hasattr(Allocation, "pipeline_run_id"):
            query = query.filter(Allocation.pipeline_run_id == pipeline_run_id)

        deleted = query.delete(synchronize_session=False)
        self.db.flush()
        return int(deleted)

    def bulk_create_allocations(
        self,
        rows: Sequence[Dict[str, Any]],
        commit: bool = False,
    ) -> List[Allocation]:
        created: List[Allocation] = []

        for row in rows:
            allocation = Allocation(**self._filter_allocation_fields(row))
            self.db.add(allocation)
            created.append(allocation)

        self.db.flush()

        if commit:
            self.db.commit()

        return created

    def list_allocations(
        self,
        allocation_date: Optional[date] = None,
        shift_name: Optional[str] = None,
        hotspot_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Allocation]:
        query = self.db.query(Allocation)

        if allocation_date is not None and hasattr(Allocation, "allocation_date"):
            query = query.filter(
                func.date(Allocation.allocation_date) == allocation_date
            )

        if hotspot_id is not None and hasattr(Allocation, "hotspot_id"):
            query = query.filter(Allocation.hotspot_id == hotspot_id)

        order_fields = []
        if hasattr(Allocation, "allocation_date"):
            order_fields.append(desc(Allocation.allocation_date))
        order_fields.append(Allocation.priority_rank.asc())
        order_fields.append(desc(Allocation.officers_allocated))

        if order_fields:
            query = query.order_by(*order_fields)

        return list(query.offset(offset).limit(limit).all())

    def get_top_allocations(
        self,
        allocation_date: Optional[date] = None,
        shift_name: Optional[str] = None,
        limit: int = 20,
    ) -> List[Allocation]:
        query = self.db.query(Allocation)

        if allocation_date is not None and hasattr(Allocation, "allocation_date"):
            query = query.filter(
                func.date(Allocation.allocation_date) == allocation_date
            )

        query = query.filter(Allocation.officers_allocated > 0)
        query = query.order_by(
            desc(Allocation.officers_allocated),
            Allocation.priority_rank.asc(),
        )

        return list(query.limit(limit).all())

    def get_hotspot_allocations(
        self,
        hotspot_id: int,
        limit: int = 30,
    ) -> List[Allocation]:
        return self.list_allocations(hotspot_id=hotspot_id, limit=limit, offset=0)

    def get_summary(
        self,
        allocation_date: Optional[date] = None,
        shift_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        query = self.db.query(Allocation)

        if allocation_date is not None and hasattr(Allocation, "allocation_date"):
            query = query.filter(
                func.date(Allocation.allocation_date) == allocation_date
            )

        rows = list(query.all())

        total_hotspots = len(rows)
        total_officers = sum(
            int(row.officers_allocated or 0)
            for row in rows
        )
        covered_hotspots = sum(
            1 for row in rows if int(row.officers_allocated or 0) > 0
        )

        risk_distribution: Dict[str, int] = {}
        officer_by_risk: Dict[str, int] = {}

        for row in rows:
            risk = str(
                getattr(row, "risk_category", None)
                or getattr(row, "priority_level", None)
                or "Unknown"
            )
            officers = int(row.officers_allocated or 0)

            risk_distribution[risk] = risk_distribution.get(risk, 0) + 1
            officer_by_risk[risk] = officer_by_risk.get(risk, 0) + officers

        return {
            "total_allocations": total_hotspots,
            "covered_hotspots": covered_hotspots,
            "total_allocated_officers": total_officers,
            "risk_distribution": risk_distribution,
            "officer_by_risk": officer_by_risk,
            "allocation_date": allocation_date,
            "shift_name": shift_name,
        }

    def _filter_allocation_fields(self, row: Dict[str, Any]) -> Dict[str, Any]:
        columns = {column.name for column in Allocation.__table__.columns}
        return {key: value for key, value in row.items() if key in columns}
