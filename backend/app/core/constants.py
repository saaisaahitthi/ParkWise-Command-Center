"""
app/core/constants.py
─────────────────────
Project-wide constants.  Nothing in this file should change at runtime.

EIS formula (FROZEN — see PARKWISE_PROGRESS_LOG_v2, Phase 3):
    Exposure     = 0.35×Frequency + 0.20×Recurrence + 0.25×Density + 0.20×TemporalRisk
    Multiplier   = 0.6 + (0.8 × Severity_norm)
    EIS          = Exposure × Multiplier   (scaled 0–100)
"""

from __future__ import annotations

from enum import Enum


# ── EIS Formula Weights (FROZEN) ──────────────────────────────────────────────

class EISWeights:
    FREQUENCY:     float = 0.35
    RECURRENCE:    float = 0.20
    DENSITY:       float = 0.25
    TEMPORAL_RISK: float = 0.20

    # Severity multiplier: 0.6 + (0.8 × severity_norm)
    SEVERITY_BASE:  float = 0.6
    SEVERITY_SCALE: float = 0.8

    @classmethod
    def exposure_weights(cls) -> dict[str, float]:
        return {
            "frequency":     cls.FREQUENCY,
            "recurrence":    cls.RECURRENCE,
            "density":       cls.DENSITY,
            "temporal_risk": cls.TEMPORAL_RISK,
        }


# ── EIS Risk Thresholds (0–100 scale) ─────────────────────────────────────────

class EISThreshold:
    LOW_MAX:      float = 25.0
    MEDIUM_MAX:   float = 50.0
    HIGH_MAX:     float = 75.0
    # CRITICAL: > 75.0


class RiskCategory(str, Enum):
    LOW      = "Low"
    MEDIUM   = "Medium"
    HIGH     = "High"
    CRITICAL = "Critical"

    @classmethod
    def from_score(cls, score: float) -> "RiskCategory":
        if score <= EISThreshold.LOW_MAX:
            return cls.LOW
        elif score <= EISThreshold.MEDIUM_MAX:
            return cls.MEDIUM
        elif score <= EISThreshold.HIGH_MAX:
            return cls.HIGH
        return cls.CRITICAL


# ── Violation Severity Mapping ────────────────────────────────────────────────
# Maps violation type strings (as they appear in the dataset) to a
# normalised severity score in [0, 1].
# Adjust values here as enforcement policy evolves.

VIOLATION_SEVERITY: dict[str, float] = {
    # High severity — active obstruction / safety risk
    "no_parking_zone":           1.00,
    "blocking_intersection":     1.00,
    "blocking_fire_hydrant":     0.95,
    "blocking_bus_stop":         0.90,
    "double_parking":            0.85,
    "blocking_driveway":         0.80,
    "footpath_parking":          0.75,

    # Medium severity — capacity reduction
    "wrong_side_parking":        0.65,
    "overtime_parking":          0.55,
    "handicap_zone_violation":   0.90,   # accessibility override
    "loading_zone_violation":    0.50,

    # Lower severity — minor infractions
    "expired_meter":             0.35,
    "improper_display":          0.25,

    # Fallback for unmapped categories
    "_default":                  0.50,
}


# ── Temporal Windows ──────────────────────────────────────────────────────────

class TimeWindow:
    """Hour ranges (24h) used by the Temporal Intelligence Engine."""
    MORNING_RUSH   = (7, 10)
    AFTERNOON_RUSH = (16, 19)
    LUNCH          = (12, 14)
    NIGHT          = (22, 6)    # wraps midnight

    PEAK_WINDOWS = [MORNING_RUSH, AFTERNOON_RUSH]


# ── DBSCAN Defaults ───────────────────────────────────────────────────────────

class DBSCANDefaults:
    EPS         = 0.005     # ~500m in decimal degrees
    MIN_SAMPLES = 10


# ── Officer Allocation ────────────────────────────────────────────────────────

class AllocationDefaults:
    MIN_OFFICERS_PER_HOTSPOT: int = 1
    MAX_OFFICERS_PER_HOTSPOT: int = 5
    # EIS score per officer unit (used for proportional allocation)
    EIS_PER_OFFICER_UNIT: float = 20.0


# ── Pagination ────────────────────────────────────────────────────────────────

class Pagination:
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE:     int = 500


# ── Database Table Names ──────────────────────────────────────────────────────

class TableName:
    VIOLATIONS          = "violations"
    ENRICHED_VIOLATIONS = "enriched_violations"
    HOTSPOTS            = "hotspots"
    PEAK_WINDOWS        = "peak_windows"
    EIS_SCORES          = "eis_scores"
    FORECASTS           = "forecasts"
    ALLOCATIONS         = "allocations"
    PATROL_ROUTES       = "patrol_routes"
