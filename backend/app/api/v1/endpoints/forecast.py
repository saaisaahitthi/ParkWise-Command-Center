from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.services.forecast_service import ForecastService


router = APIRouter()


class ForecastTrainRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "horizon_days": 1,
                "hotspot_id": None,
                "model_version": "forecast-v1-h1",
                "min_history_per_hotspot": 1,
            }
        }
    )

    horizon_days: int = Field(default=1, ge=1, le=7)
    hotspot_id: Optional[int] = Field(
        default=None,
        ge=0,
        description="Positive hotspot ID, or null/0 to train across all hotspots.",
    )
    model_version: str = "forecast-v1-h1"
    min_history_per_hotspot: int = Field(default=1, ge=1, le=30)

    @field_validator("hotspot_id")
    @classmethod
    def normalize_hotspot_id(cls, value: Optional[int]) -> Optional[int]:
        return None if value == 0 else value


class ForecastGenerateRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "horizon_days": 1,
                "hotspot_id": None,
                "replace_existing": True,
                "pipeline_run_id": "forecast-v1-h1",
            }
        }
    )

    horizon_days: int = Field(default=1, ge=1, le=7)
    hotspot_id: Optional[int] = Field(
        default=None,
        ge=0,
        description="Positive hotspot ID, or null/0 to generate for all hotspots.",
    )
    replace_existing: bool = True
    pipeline_run_id: Optional[str] = "forecast-v1-h1"

    @field_validator("hotspot_id")
    @classmethod
    def normalize_hotspot_id(cls, value: Optional[int]) -> Optional[int]:
        return None if value == 0 else value


@router.post("/train")
def train_forecast_model(
    payload: ForecastTrainRequest = Body(
        openapi_examples={
            "default": {
                "summary": "Train across the current hotspot-level EIS dataset",
                "value": {
                    "horizon_days": 1,
                    "hotspot_id": None,
                    "model_version": "forecast-v1-h1",
                    "min_history_per_hotspot": 1,
                },
            }
        }
    ),
    db: Session = Depends(db_session),
) -> Dict[str, Any]:
    try:
        service = ForecastService(db)
        return service.train_model(
            horizon_days=payload.horizon_days,
            hotspot_id=payload.hotspot_id,
            model_version=payload.model_version,
            min_history_per_hotspot=payload.min_history_per_hotspot,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Forecast training failed: {exc}") from exc


@router.post("/generate")
def generate_forecasts(
    payload: ForecastGenerateRequest = Body(
        openapi_examples={
            "default": {
                "summary": "Generate predictions for all available hotspots",
                "value": {
                    "horizon_days": 1,
                    "hotspot_id": None,
                    "replace_existing": True,
                    "pipeline_run_id": "forecast-v1-h1",
                },
            }
        }
    ),
    db: Session = Depends(db_session),
) -> Dict[str, Any]:
    try:
        service = ForecastService(db)
        return service.generate_forecasts(
            horizon_days=payload.horizon_days,
            hotspot_id=payload.hotspot_id,
            replace_existing=payload.replace_existing,
            pipeline_run_id=payload.pipeline_run_id,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Forecast generation failed: {exc}") from exc


@router.get("")
def list_forecasts(
    hotspot_id: Optional[int] = Query(default=None),
    horizon_days: Optional[int] = Query(default=None, ge=1, le=7),
    risk_category: Optional[str] = Query(default=None),
    model_version: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(db_session),
) -> List[Dict[str, Any]]:
    service = ForecastService(db)
    return service.list_forecasts(
        hotspot_id=hotspot_id,
        horizon_days=horizon_days,
        risk_category=risk_category,
        model_version=model_version,
        limit=limit,
        offset=offset,
    )


@router.get("/")
def list_forecasts_with_slash(
    hotspot_id: Optional[int] = Query(default=None),
    horizon_days: Optional[int] = Query(default=None, ge=1, le=7),
    risk_category: Optional[str] = Query(default=None),
    model_version: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(db_session),
) -> List[Dict[str, Any]]:
    service = ForecastService(db)
    return service.list_forecasts(
        hotspot_id=hotspot_id,
        horizon_days=horizon_days,
        risk_category=risk_category,
        model_version=model_version,
        limit=limit,
        offset=offset,
    )


@router.get("/top")
def get_top_forecasts(
    limit: int = Query(default=20, ge=1, le=100),
    horizon_days: Optional[int] = Query(default=None, ge=1, le=7),
    critical_only: bool = Query(default=False),
    db: Session = Depends(db_session),
) -> List[Dict[str, Any]]:
    service = ForecastService(db)
    return service.get_top_forecasts(
        limit=limit,
        horizon_days=horizon_days,
        critical_only=critical_only,
    )


@router.get("/hotspots/{hotspot_id}")
def get_hotspot_forecasts(
    hotspot_id: int,
    horizon_days: Optional[int] = Query(default=None, ge=1, le=7),
    limit: int = Query(default=30, ge=1, le=200),
    db: Session = Depends(db_session),
) -> List[Dict[str, Any]]:
    service = ForecastService(db)
    return service.get_hotspot_forecasts(
        hotspot_id=hotspot_id,
        horizon_days=horizon_days,
        limit=limit,
    )


@router.get("/summary")
def get_forecast_summary(
    db: Session = Depends(db_session),
) -> Dict[str, Any]:
    service = ForecastService(db)
    return service.get_summary()
