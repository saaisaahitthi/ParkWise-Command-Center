"""
Dashboard aggregation API.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.services.dashboard_service import DashboardService

router = APIRouter()


def _execute_dashboard_query(query: Callable[[], Any]) -> Any:
    try:
        return query()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dashboard aggregation failed: {exc}",
        ) from exc


@router.get("/summary", summary="Get executive dashboard summary")
def get_dashboard_summary(
    db: Session = Depends(db_session),
) -> Dict[str, Any]:
    service = DashboardService(db)
    return _execute_dashboard_query(service.get_executive_summary)


@router.get("/risk-distribution", summary="Get current EIS risk distribution")
def get_risk_distribution(
    db: Session = Depends(db_session),
) -> Dict[str, int]:
    service = DashboardService(db)
    return _execute_dashboard_query(service.get_risk_distribution)


@router.get("/map", summary="Get dashboard hotspot map data")
def get_hotspot_map(
    db: Session = Depends(db_session),
) -> List[Dict[str, Any]]:
    service = DashboardService(db)
    return _execute_dashboard_query(service.get_hotspot_map_data)


@router.get("/temporal", summary="Get dashboard temporal overview")
def get_temporal_overview(
    db: Session = Depends(db_session),
) -> Dict[str, Any]:
    service = DashboardService(db)
    return _execute_dashboard_query(service.get_temporal_overview)


@router.get("/forecast", summary="Get dashboard forecast overview")
def get_forecast_overview(
    db: Session = Depends(db_session),
) -> Dict[str, Any]:
    service = DashboardService(db)
    return _execute_dashboard_query(service.get_forecast_overview)


@router.get("/allocation", summary="Get dashboard allocation overview")
def get_allocation_overview(
    db: Session = Depends(db_session),
) -> Dict[str, Any]:
    service = DashboardService(db)
    return _execute_dashboard_query(service.get_allocation_overview)


@router.get("/routing", summary="Get dashboard routing overview")
def get_routing_overview(
    db: Session = Depends(db_session),
) -> Dict[str, Any]:
    service = DashboardService(db)
    return _execute_dashboard_query(service.get_routing_overview)


@router.get("/full", summary="Get complete dashboard payload")
def get_full_dashboard(
    db: Session = Depends(db_session),
) -> Dict[str, Any]:
    service = DashboardService(db)
    return _execute_dashboard_query(service.get_dashboard_payload)
