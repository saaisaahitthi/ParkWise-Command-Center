"""
app/schemas/analytics.py
────────────────────────
Pydantic v2 schemas for all analytics outputs:
  • HotspotRead / HotspotSummary
  • EISScoreRead / EISScoreDetail
  • ForecastRead
  • AllocationRead / AllocationPlan
  • PatrolRouteRead
  • PeakWindowRead
  • DashboardSummary (executive command centre)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ─── Hotspot ──────────────────────────────────────────────────────────────────

class HotspotSummary(BaseModel):
    """Lightweight representation for map pins and list views."""
    id:                    int
    cluster_label:         int
    hotspot_name:          Optional[str]
    centroid_lat:          float
    centroid_lon:          float
    total_violations:      int
    dominant_violation_type: Optional[str]

    model_config = {"from_attributes": True}


class HotspotRead(HotspotSummary):
    """Full hotspot representation including spatial stats."""
    zone_id:               Optional[str]
    radius_m:              Optional[float]
    unique_dates:          Optional[int]
    dominant_vehicle_category: Optional[str]
    avg_fine_amount:       Optional[float]
    violation_density:     Optional[float]
    created_at:            datetime
    updated_at:            datetime

    model_config = {"from_attributes": True}


class HotspotListResponse(BaseModel):
    total:      int
    page:       int
    page_size:  int
    items:      List[HotspotRead]


# ─── EIS Score ────────────────────────────────────────────────────────────────

class EISComponentBreakdown(BaseModel):
    """Used by dashboards to explain the score to enforcement officers."""
    frequency_score:      float = Field(ge=0, le=1)
    recurrence_score:     float = Field(ge=0, le=1)
    density_score:        float = Field(ge=0, le=1)
    temporal_risk_score:  float = Field(ge=0, le=1)
    severity_norm:        float = Field(ge=0, le=1)
    exposure_score:       float = Field(ge=0, le=1)
    severity_multiplier:  float


class EISScoreRead(BaseModel):
    id:                  int
    hotspot_id:          int
    eis_score:           float  = Field(ge=0, le=100)
    risk_category:       str
    rank:                Optional[int]
    computed_for_date:   datetime
    components:          Optional[EISComponentBreakdown] = None
    created_at:          datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_with_components(cls, obj: Any) -> "EISScoreRead":
        components = EISComponentBreakdown(
            frequency_score=obj.frequency_score,
            recurrence_score=obj.recurrence_score,
            density_score=obj.density_score,
            temporal_risk_score=obj.temporal_risk_score,
            severity_norm=obj.severity_norm,
            exposure_score=obj.exposure_score,
            severity_multiplier=obj.severity_multiplier,
        )
        return cls(
            id=obj.id,
            hotspot_id=obj.hotspot_id,
            eis_score=obj.eis_score,
            risk_category=obj.risk_category,
            rank=obj.rank,
            computed_for_date=obj.computed_for_date,
            components=components,
            created_at=obj.created_at,
        )


class EISScoreListResponse(BaseModel):
    total:      int
    items:      List[EISScoreRead]


# ─── Forecast ─────────────────────────────────────────────────────────────────

class ForecastRead(BaseModel):
    id:                       int
    hotspot_id:               int
    forecast_date:            datetime
    horizon_days:             int
    predicted_eis:            float   = Field(ge=0, le=100)
    predicted_risk_category:  str
    confidence_lower:         Optional[float]
    confidence_upper:         Optional[float]
    top_features:             Optional[Dict[str, Any] | List[Dict[str, Any]]]
    model_version:            Optional[str]
    created_at:               datetime

    model_config = {"from_attributes": True}


class ForecastListResponse(BaseModel):
    forecast_date:  datetime
    total:          int
    items:          List[ForecastRead]


# ─── Allocation ───────────────────────────────────────────────────────────────

class AllocationRead(BaseModel):
    id:                       int
    hotspot_id:               int
    hotspot_name:             Optional[str] = None   # joined from hotspot
    centroid_lat:             Optional[float] = None
    centroid_lon:             Optional[float] = None
    officers_allocated:       int
    allocation_fraction:      float
    priority_rank:            int
    deployment_window:        Optional[str]
    eis_snapshot:             Optional[float]
    risk_category:            Optional[str]
    allocation_date:          datetime

    model_config = {"from_attributes": True}


class AllocationRequest(BaseModel):
    """Input for the Officer Allocation Engine endpoint."""
    total_officers: int = Field(ge=1, le=500,
                                description="Total officers available for deployment")
    top_n_hotspots: Optional[int] = Field(
        None, ge=1, le=100,
        description="Limit allocation to top-N hotspots by EIS. Default: all Critical+High."
    )


class AllocationPlan(BaseModel):
    total_officers:       int
    hotspots_covered:     int
    allocations:          List[AllocationRead]
    unallocated_officers: int
    computed_at:          datetime


# ─── Patrol Route ─────────────────────────────────────────────────────────────

class PatrolStop(BaseModel):
    sequence:                  int
    hotspot_id:                int
    hotspot_name:              Optional[str]
    lat:                       float
    lon:                       float
    eis_score:                 Optional[float]
    estimated_arrival:         Optional[str]
    recommended_duration_min:  Optional[int]


class PatrolRouteRead(BaseModel):
    id:                       int
    route_name:               Optional[str]
    shift_label:              Optional[str]
    officer_count:             int
    stops:                    List[PatrolStop]
    total_distance_km:        Optional[float]
    estimated_duration_min:   Optional[int]
    hotspots_covered:         Optional[int]
    total_eis_covered:        Optional[float]
    created_at:               datetime

    model_config = {"from_attributes": True}


# ─── Peak Window ──────────────────────────────────────────────────────────────

class PeakWindowRead(BaseModel):
    id:                     int
    hotspot_id:             Optional[int]
    day_of_week:            Optional[int]
    hour_of_day:            Optional[int]
    window_label:           Optional[str]
    violation_count:        int
    avg_violations:         Optional[float]
    pct_of_total:           Optional[float]
    recommended_start_hour: Optional[int]
    recommended_end_hour:   Optional[int]
    enforcement_priority:   Optional[str]

    model_config = {"from_attributes": True}


# ─── Dashboard / Executive Command Centre ─────────────────────────────────────

class RiskCategorySummary(BaseModel):
    critical: int
    high:     int
    medium:   int
    low:      int


class DashboardSummary(BaseModel):
    """Top-level metrics for the Executive Command Centre."""
    total_violations:        int
    active_hotspots:         int
    critical_hotspots:       int
    high_risk_hotspots:      int
    risk_distribution:       RiskCategorySummary
    top_hotspots:            List[EISScoreRead]     # top 5 by EIS
    recommended_deployments: Optional[AllocationPlan]
    data_as_of:              datetime
