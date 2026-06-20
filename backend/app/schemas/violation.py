"""
app/schemas/violation.py
────────────────────────
Pydantic v2 schemas for the Violation and EnrichedViolation models.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ── Base ──────────────────────────────────────────────────────────────────────

class ViolationBase(BaseModel):
    violation_type:     str
    violation_code:     Optional[str]       = None
    vehicle_category:   Optional[str]       = None
    vehicle_type:       Optional[str]       = None
    violation_date:     datetime
    latitude:           Optional[float]     = Field(None, ge=-90,  le=90)
    longitude:          Optional[float]     = Field(None, ge=-180, le=180)
    junction_name:      Optional[str]       = None
    ward:               Optional[str]       = None
    zone:               Optional[str]       = None
    fine_amount:        Optional[float]     = Field(None, ge=0)
    is_paid:            Optional[bool]      = None


# ── Read (API response) ───────────────────────────────────────────────────────

class ViolationRead(ViolationBase):
    id:             int
    hour_of_day:    Optional[int]   = None
    day_of_week:    Optional[int]   = None
    week_number:    Optional[int]   = None
    month:          Optional[int]   = None
    ingested_at:    datetime

    model_config = {"from_attributes": True}


# ── Enriched violation schema ─────────────────────────────────────────────────

class EnrichedViolationRead(BaseModel):
    id:              int
    violation_id:    int
    hotspot_id:      Optional[int]  = None
    severity_score:  float          = Field(ge=0, le=1)
    is_recurrence:   bool
    temporal_flag:   bool
    cluster_label:   Optional[int]  = None
    processed_at:    datetime

    model_config = {"from_attributes": True}


# ── List response wrapper ─────────────────────────────────────────────────────

class ViolationListResponse(BaseModel):
    total:      int
    page:       int
    page_size:  int
    items:      list[ViolationRead]
