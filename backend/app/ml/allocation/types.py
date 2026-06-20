from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class AllocationInput:
    hotspot_id: int
    eis_score: float
    risk_category: str
    forecasted_eis: Optional[float] = None
    forecasted_risk_category: Optional[str] = None
    zone_id: Optional[str] = None
    hotspot_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    current_violation_count: Optional[int] = None
    temporal_risk_score: Optional[float] = None


@dataclass(frozen=True)
class AllocationRequest:
    total_officers: int
    allocation_date: date
    shift_name: str = "default"
    min_officers_per_critical: int = 2
    min_officers_per_high: int = 1
    use_forecast: bool = True
    max_hotspots: Optional[int] = None


@dataclass
class AllocationCandidate:
    hotspot_id: int
    priority_score: float
    combined_eis: float
    risk_category: str
    forecasted_eis: Optional[float]
    forecasted_risk_category: Optional[str]
    zone_id: Optional[str]
    hotspot_name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    recommended_officers: int = 0
    reason_codes: List[str] = field(default_factory=list)


@dataclass
class AllocationPlan:
    allocation_date: date
    shift_name: str
    total_officers: int
    allocated_officers: int
    unallocated_officers: int
    hotspots_covered: int
    critical_hotspots_covered: int
    high_hotspots_covered: int
    candidates: List[AllocationCandidate]
    summary: Dict[str, Any]