"""
Read-only aggregation service for dashboard-facing API payloads.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.analytics import (
    Allocation,
    EISScore,
    Forecast,
    PatrolRoute,
    PeakWindow,
)
from app.models.hotspot import Hotspot


RISK_CATEGORIES = ("Low", "Medium", "High", "Critical")


class DashboardService:
    """Aggregate current analytics data without modifying persistent state."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_executive_summary(self) -> Dict[str, Any]:
        """Return headline metrics for the executive dashboard."""
        total_hotspots = self.db.query(func.count(Hotspot.id)).scalar() or 0
        risk_distribution = self.get_risk_distribution()
        latest_eis_count = sum(risk_distribution.values())
        total_forecasts = self.db.query(func.count(Forecast.id)).scalar() or 0
        total_allocated_officers = sum(
            int(row.officers_allocated or 0)
            for row in self._latest_allocations()
        )
        latest_route = self._latest_route()

        timestamps = [
            self.db.query(func.max(Hotspot.updated_at)).scalar(),
            self.db.query(func.max(EISScore.created_at)).scalar(),
            self.db.query(func.max(PeakWindow.created_at)).scalar(),
            self.db.query(func.max(Forecast.created_at)).scalar(),
            self.db.query(func.max(Allocation.allocation_date)).scalar(),
            self.db.query(func.max(PatrolRoute.created_at)).scalar(),
        ]
        last_updated = max(
            (value for value in timestamps if value is not None),
            default=None,
        )

        return {
            "total_hotspots": int(total_hotspots),
            "active_hotspots": latest_eis_count,
            "critical_hotspots": risk_distribution["Critical"],
            "high_risk_hotspots": risk_distribution["High"],
            "total_forecasts": int(total_forecasts),
            "total_allocated_officers": total_allocated_officers,
            "latest_route_distance_km": (
                self._optional_float(latest_route.total_distance_km)
                if latest_route
                else None
            ),
            "latest_route_duration_min": (
                int(latest_route.estimated_duration_min)
                if latest_route and latest_route.estimated_duration_min is not None
                else None
            ),
            "last_updated_at": self._isoformat(last_updated),
        }

    def get_risk_distribution(self) -> Dict[str, int]:
        """Return risk-category counts from the latest EIS per hotspot."""
        counts = {category: 0 for category in RISK_CATEGORIES}
        latest_eis = self._latest_id_subquery(EISScore)
        rows = (
            self.db.query(EISScore.risk_category, func.count(EISScore.id))
            .join(latest_eis, EISScore.id == latest_eis.c.latest_id)
            .group_by(EISScore.risk_category)
            .all()
        )
        for category, count in rows:
            if category in counts:
                counts[category] = int(count)
        return counts

    def get_hotspot_map_data(self) -> List[Dict[str, Any]]:
        """Return map-ready hotspot records enriched with current analytics."""
        hotspots = (
            self.db.query(Hotspot)
            .order_by(Hotspot.total_violations.desc(), Hotspot.id.asc())
            .all()
        )
        if not hotspots:
            return []

        hotspot_ids = [int(hotspot.id) for hotspot in hotspots]
        eis_by_hotspot = {
            int(row.hotspot_id): row
            for row in self._latest_rows(EISScore, hotspot_ids)
        }
        forecast_by_hotspot = {
            int(row.hotspot_id): row
            for row in self._latest_rows(Forecast, hotspot_ids)
        }
        allocation_by_hotspot = {
            int(row.hotspot_id): row
            for row in self._latest_rows(Allocation, hotspot_ids)
        }

        return [
            {
                "hotspot_id": int(hotspot.id),
                "name": hotspot.hotspot_name,
                "latitude": float(hotspot.centroid_lat),
                "longitude": float(hotspot.centroid_lon),
                "hotspot_type": hotspot.dominant_violation_type,
                "violation_count": int(hotspot.total_violations or 0),
                "latest_eis": (
                    float(eis_by_hotspot[hotspot.id].eis_score)
                    if hotspot.id in eis_by_hotspot
                    else None
                ),
                "risk_category": (
                    eis_by_hotspot[hotspot.id].risk_category
                    if hotspot.id in eis_by_hotspot
                    else None
                ),
                "forecasted_eis": (
                    float(forecast_by_hotspot[hotspot.id].predicted_eis)
                    if hotspot.id in forecast_by_hotspot
                    else None
                ),
                "officers_allocated": (
                    int(allocation_by_hotspot[hotspot.id].officers_allocated)
                    if hotspot.id in allocation_by_hotspot
                    else None
                ),
            }
            for hotspot in hotspots
        ]

    def get_temporal_overview(self) -> Dict[str, Any]:
        """Return peak-window, heatmap, and temporal-risk dashboard data."""
        peak_windows_count = self.db.query(func.count(PeakWindow.id)).scalar() or 0
        top_rows = (
            self.db.query(PeakWindow, Hotspot)
            .outerjoin(Hotspot, Hotspot.id == PeakWindow.hotspot_id)
            .order_by(PeakWindow.violation_count.desc(), PeakWindow.id.desc())
            .limit(10)
            .all()
        )
        heatmap_rows = (
            self.db.query(
                PeakWindow.day_of_week,
                PeakWindow.hour_of_day,
                func.sum(PeakWindow.violation_count).label("total_violations"),
            )
            .filter(
                PeakWindow.day_of_week.isnot(None),
                PeakWindow.hour_of_day.isnot(None),
            )
            .group_by(PeakWindow.day_of_week, PeakWindow.hour_of_day)
            .order_by(PeakWindow.day_of_week, PeakWindow.hour_of_day)
            .all()
        )

        latest_eis = self._latest_id_subquery(EISScore)
        temporal_risk_rows = (
            self.db.query(EISScore, Hotspot)
            .join(latest_eis, EISScore.id == latest_eis.c.latest_id)
            .join(Hotspot, Hotspot.id == EISScore.hotspot_id)
            .order_by(EISScore.temporal_risk_score.desc())
            .limit(10)
            .all()
        )

        return {
            "peak_windows_count": int(peak_windows_count),
            "top_peak_windows": [
                {
                    "peak_window_id": int(window.id),
                    "hotspot_id": (
                        int(window.hotspot_id)
                        if window.hotspot_id is not None
                        else None
                    ),
                    "hotspot_name": hotspot.hotspot_name if hotspot else None,
                    "day_of_week": window.day_of_week,
                    "hour_of_day": window.hour_of_day,
                    "window_label": window.window_label,
                    "violation_count": int(window.violation_count),
                    "enforcement_priority": window.enforcement_priority,
                    "recommended_start_hour": window.recommended_start_hour,
                    "recommended_end_hour": window.recommended_end_hour,
                }
                for window, hotspot in top_rows
            ],
            "day_hour_heatmap": [
                {
                    "day_of_week": int(day),
                    "hour_of_day": int(hour),
                    "total_violations": int(total or 0),
                }
                for day, hour, total in heatmap_rows
            ],
            "highest_temporal_risk_hotspots": [
                {
                    "hotspot_id": int(score.hotspot_id),
                    "hotspot_name": hotspot.hotspot_name,
                    "temporal_risk_score": float(score.temporal_risk_score),
                    "latest_eis": float(score.eis_score),
                    "risk_category": score.risk_category,
                }
                for score, hotspot in temporal_risk_rows
            ],
        }

    def get_forecast_overview(self) -> Dict[str, Any]:
        """Return latest forecast rankings and aggregate statistics."""
        total_forecasts = self.db.query(func.count(Forecast.id)).scalar() or 0
        latest_forecasts = self._latest_rows(Forecast)
        latest_forecasts.sort(key=lambda row: row.predicted_eis, reverse=True)
        hotspot_names = self._hotspot_name_map(
            [int(row.hotspot_id) for row in latest_forecasts]
        )

        distribution = {category: 0 for category in RISK_CATEGORIES}
        for row in latest_forecasts:
            if row.predicted_risk_category in distribution:
                distribution[row.predicted_risk_category] += 1

        average_predicted_eis = (
            sum(float(row.predicted_eis) for row in latest_forecasts)
            / len(latest_forecasts)
            if latest_forecasts
            else 0.0
        )
        return {
            "total_forecasts": int(total_forecasts),
            "top_forecasted_hotspots": [
                {
                    "forecast_id": int(row.id),
                    "hotspot_id": int(row.hotspot_id),
                    "hotspot_name": hotspot_names.get(int(row.hotspot_id)),
                    "forecast_date": self._isoformat(row.forecast_date),
                    "horizon_days": int(row.horizon_days),
                    "predicted_eis": float(row.predicted_eis),
                    "predicted_risk_category": row.predicted_risk_category,
                    "confidence_lower": self._optional_float(row.confidence_lower),
                    "confidence_upper": self._optional_float(row.confidence_upper),
                }
                for row in latest_forecasts[:10]
            ],
            "risk_distribution": distribution,
            "average_predicted_eis": round(average_predicted_eis, 2),
        }

    def get_allocation_overview(self) -> Dict[str, Any]:
        """Return current officer deployment aggregates."""
        allocations = self._latest_allocations()
        allocations.sort(
            key=lambda row: (row.officers_allocated, -(row.priority_rank or 0)),
            reverse=True,
        )
        hotspot_names = self._hotspot_name_map(
            [int(row.hotspot_id) for row in allocations]
        )
        officer_by_risk = {category: 0 for category in RISK_CATEGORIES}
        for row in allocations:
            if row.risk_category in officer_by_risk:
                officer_by_risk[row.risk_category] += int(
                    row.officers_allocated or 0
                )

        return {
            "total_allocations": len(allocations),
            "total_officers": sum(
                int(row.officers_allocated or 0) for row in allocations
            ),
            "top_allocated_hotspots": [
                {
                    "allocation_id": int(row.id),
                    "hotspot_id": int(row.hotspot_id),
                    "hotspot_name": hotspot_names.get(int(row.hotspot_id)),
                    "officers_allocated": int(row.officers_allocated),
                    "priority_rank": int(row.priority_rank),
                    "deployment_window": row.deployment_window,
                    "eis_snapshot": self._optional_float(row.eis_snapshot),
                    "risk_category": row.risk_category,
                    "allocation_date": self._isoformat(row.allocation_date),
                }
                for row in allocations[:10]
            ],
            "officer_by_risk": officer_by_risk,
        }

    def get_routing_overview(self) -> Dict[str, Any]:
        """Return latest patrol-route information and route count."""
        total_routes = self.db.query(func.count(PatrolRoute.id)).scalar() or 0
        latest_route = self._latest_route()

        return {
            "total_routes": int(total_routes),
            "latest_route": self._serialize_route(latest_route),
            "latest_distance_km": (
                self._optional_float(latest_route.total_distance_km)
                if latest_route
                else None
            ),
            "latest_duration_min": (
                int(latest_route.estimated_duration_min)
                if latest_route and latest_route.estimated_duration_min is not None
                else None
            ),
            "latest_stops_count": (
                int(latest_route.hotspots_covered)
                if latest_route and latest_route.hotspots_covered is not None
                else 0
            ),
        }

    def get_dashboard_payload(self) -> Dict[str, Any]:
        """Return the complete dashboard payload in one request."""
        return {
            "executive_summary": self.get_executive_summary(),
            "risk_distribution": self.get_risk_distribution(),
            "hotspot_map": self.get_hotspot_map_data(),
            "temporal_overview": self.get_temporal_overview(),
            "forecast_overview": self.get_forecast_overview(),
            "allocation_overview": self.get_allocation_overview(),
            "routing_overview": self.get_routing_overview(),
        }

    def _latest_id_subquery(self, model):
        return (
            self.db.query(
                model.hotspot_id,
                func.max(model.id).label("latest_id"),
            )
            .group_by(model.hotspot_id)
            .subquery()
        )

    def _latest_rows(
        self,
        model,
        hotspot_ids: Optional[List[int]] = None,
    ) -> List[Any]:
        latest = self._latest_id_subquery(model)
        query = self.db.query(model).join(latest, model.id == latest.c.latest_id)
        if hotspot_ids is not None:
            query = query.filter(model.hotspot_id.in_(hotspot_ids))
        return query.all()

    def _latest_allocations(self) -> List[Allocation]:
        return self._latest_rows(Allocation)

    def _latest_route(self) -> Optional[PatrolRoute]:
        return (
            self.db.query(PatrolRoute)
            .order_by(PatrolRoute.created_at.desc(), PatrolRoute.id.desc())
            .first()
        )

    def _hotspot_name_map(self, hotspot_ids: List[int]) -> Dict[int, Optional[str]]:
        if not hotspot_ids:
            return {}
        rows = (
            self.db.query(Hotspot.id, Hotspot.hotspot_name)
            .filter(Hotspot.id.in_(hotspot_ids))
            .all()
        )
        return {int(hotspot_id): name for hotspot_id, name in rows}

    @staticmethod
    def _serialize_route(route: Optional[PatrolRoute]) -> Optional[Dict[str, Any]]:
        if route is None:
            return None
        return {
            "route_id": int(route.id),
            "route_name": route.route_name,
            "shift_label": route.shift_label,
            "officer_count": int(route.officer_count),
            "stops": route.stops_json or [],
            "total_distance_km": DashboardService._optional_float(
                route.total_distance_km
            ),
            "estimated_duration_min": (
                int(route.estimated_duration_min)
                if route.estimated_duration_min is not None
                else None
            ),
            "hotspots_covered": int(route.hotspots_covered or 0),
            "total_eis_covered": DashboardService._optional_float(
                route.total_eis_covered
            ),
            "created_at": DashboardService._isoformat(route.created_at),
        }

    @staticmethod
    def _optional_float(value: Any) -> Optional[float]:
        return float(value) if value is not None else None

    @staticmethod
    def _isoformat(value: Optional[datetime]) -> Optional[str]:
        return value.isoformat() if value is not None else None
