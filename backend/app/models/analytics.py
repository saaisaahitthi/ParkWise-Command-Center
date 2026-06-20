"""
app/models/analytics.py
────────────────────────
Remaining 5 analytics tables:
  • PeakWindow    — temporal intelligence outputs
  • EISScore      — per-hotspot EIS computation results
  • Forecast      — LightGBM risk predictions
  • Allocation    — officer deployment recommendations
  • PatrolRoute   — optimised patrol route definitions
"""

from __future__ import annotations

from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.constants import RiskCategory, TableName
from app.db.base import Base


# ── PeakWindow ────────────────────────────────────────────────────────────────

class PeakWindow(Base):
    """
    Peak violation time windows identified by the Temporal Intelligence Engine.

    One row per (hotspot_id, day_of_week, hour_of_day) combination that
    exceeds the significance threshold.
    """

    __tablename__ = TableName.PEAK_WINDOWS

    id              = Column(BigInteger, primary_key=True, autoincrement=True)
    hotspot_id      = Column(
        BigInteger,
        ForeignKey(f"{TableName.HOTSPOTS}.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="NULL means the window is city-wide (not hotspot-specific)",
    )

    # Window dimensions
    day_of_week     = Column(Integer, nullable=True,
                              comment="0=Monday … 6=Sunday; NULL means all days")
    hour_of_day     = Column(Integer, nullable=True,
                              comment="0–23; NULL means all hours")
    window_label    = Column(String(64), nullable=True,
                              comment="E.g. 'Morning Rush', 'Lunch', 'Evening Rush'")

    # Observed statistics
    violation_count = Column(Integer, nullable=False)
    avg_violations  = Column(Float, nullable=True,
                              comment="Average violations per occurrence of this window")
    pct_of_total    = Column(Float, nullable=True,
                              comment="Percentage of total violations in this window")

    # Enforcement recommendation
    recommended_start_hour = Column(Integer, nullable=True)
    recommended_end_hour   = Column(Integer, nullable=True)
    enforcement_priority   = Column(String(16), nullable=True,
                                    comment="Low | Medium | High | Critical")

    pipeline_run_id = Column(String(64), nullable=True)
    created_at      = Column(DateTime(timezone=False), nullable=False,
                              default=datetime.utcnow)

    __table_args__ = (
        Index("ix_peak_windows_hotspot_day_hour", "hotspot_id", "day_of_week", "hour_of_day"),
    )

    def __repr__(self) -> str:
        return (
            f"<PeakWindow id={self.id} hotspot_id={self.hotspot_id} "
            f"day={self.day_of_week} hour={self.hour_of_day} "
            f"count={self.violation_count}>"
        )


# ── EISScore ──────────────────────────────────────────────────────────────────

class EISScore(Base):
    """
    Enforcement Intelligence Score for a hotspot at a point in time.

    Stores the full component breakdown so dashboards can explain
    WHY a hotspot is ranked the way it is.

    EIS formula (FROZEN):
        Exposure   = 0.35×frequency + 0.20×recurrence + 0.25×density + 0.20×temporal_risk
        Multiplier = 0.6 + (0.8 × severity_norm)
        EIS        = Exposure × Multiplier   →  scaled to 0–100
    """

    __tablename__ = TableName.EIS_SCORES

    id              = Column(BigInteger, primary_key=True, autoincrement=True)
    hotspot_id      = Column(
        BigInteger,
        ForeignKey(f"{TableName.HOTSPOTS}.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    computed_for_date = Column(DateTime(timezone=False), nullable=False,
                                comment="The date range this EIS was computed over")

    # ── Raw component scores (percentile-normalised, 0–1) ──────────────────
    frequency_score    = Column(Float, nullable=False,
                                 comment="Percentile rank of violation frequency")
    recurrence_score   = Column(Float, nullable=False,
                                 comment="Percentile rank of recurrence within dataset")
    density_score      = Column(Float, nullable=False,
                                 comment="Percentile rank of spatial density")
    temporal_risk_score = Column(Float, nullable=False,
                                  comment="Percentile rank of peak-window overlap")
    severity_norm      = Column(Float, nullable=False,
                                 comment="Average normalised severity of violations [0,1]")

    # ── Intermediate computations ────────────────────────────────────────────
    exposure_score     = Column(Float, nullable=False,
                                 comment="Weighted sum of frequency/recurrence/density/temporal")
    severity_multiplier = Column(Float, nullable=False,
                                  comment="0.6 + (0.8 × severity_norm)")

    # ── Final score ──────────────────────────────────────────────────────────
    eis_score          = Column(Float, nullable=False,
                                 comment="Final EIS score, 0–100")
    risk_category      = Column(String(16), nullable=False,
                                 comment="Low | Medium | High | Critical")

    # ── Ranking ──────────────────────────────────────────────────────────────
    rank               = Column(Integer, nullable=True,
                                 comment="Rank among all hotspots (1 = most urgent)")

    # ── Pipeline metadata ────────────────────────────────────────────────────
    pipeline_run_id    = Column(String(64), nullable=True)
    created_at         = Column(DateTime(timezone=False), nullable=False,
                                 default=datetime.utcnow)

    # ── Relationships ────────────────────────────────────────────────────────
    hotspot = relationship("Hotspot", back_populates="eis_scores")

    __table_args__ = (
        Index("ix_eis_hotspot_date", "hotspot_id", "computed_for_date"),
        Index("ix_eis_score_desc",   "eis_score"),
        Index("ix_eis_risk_cat",     "risk_category"),
    )

    def __repr__(self) -> str:
        return (
            f"<EISScore id={self.id} hotspot_id={self.hotspot_id} "
            f"eis={self.eis_score:.1f} category={self.risk_category}>"
        )


# ── Forecast ──────────────────────────────────────────────────────────────────

class Forecast(Base):
    """
    LightGBM risk forecast for a hotspot for a future date.

    SHAP values are stored as JSONB for interpretability (feature importance
    per prediction), enabling the dashboard to show WHY a forecast was made.
    """

    __tablename__ = TableName.FORECASTS

    id              = Column(BigInteger, primary_key=True, autoincrement=True)
    hotspot_id      = Column(
        BigInteger,
        ForeignKey(f"{TableName.HOTSPOTS}.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    forecast_date   = Column(DateTime(timezone=False), nullable=False, index=True,
                              comment="The future date being predicted")
    horizon_days    = Column(Integer, nullable=False, default=1,
                              comment="How many days ahead this forecast is for")

    # ── Prediction outputs ───────────────────────────────────────────────────
    predicted_eis       = Column(Float, nullable=False,
                                  comment="Predicted EIS score for the forecast date")
    predicted_risk_category = Column(String(16), nullable=False,
                                      comment="Low | Medium | High | Critical")
    confidence_lower    = Column(Float, nullable=True,
                                  comment="Lower bound of prediction interval")
    confidence_upper    = Column(Float, nullable=True,
                                  comment="Upper bound of prediction interval")

    # ── Interpretability ─────────────────────────────────────────────────────
    shap_values         = Column(JSONB, nullable=True,
                                  comment="SHAP feature contributions as {feature: value} dict")
    top_features        = Column(JSONB, nullable=True,
                                  comment="Top 5 contributing features [{'feature':..,'value':..}]")

    # ── Pipeline metadata ────────────────────────────────────────────────────
    model_version       = Column(String(32), nullable=True)
    pipeline_run_id     = Column(String(64), nullable=True)
    created_at          = Column(DateTime(timezone=False), nullable=False,
                                  default=datetime.utcnow)

    # ── Relationships ────────────────────────────────────────────────────────
    hotspot = relationship("Hotspot", back_populates="forecasts")

    __table_args__ = (
        UniqueConstraint("hotspot_id", "forecast_date", "horizon_days",
                         name="uq_forecast_hotspot_date_horizon"),
        Index("ix_forecast_date_risk", "forecast_date", "predicted_risk_category"),
    )

    def __repr__(self) -> str:
        return (
            f"<Forecast id={self.id} hotspot_id={self.hotspot_id} "
            f"date={self.forecast_date.date()} eis={self.predicted_eis:.1f} "
            f"risk={self.predicted_risk_category}>"
        )


# ── Allocation ────────────────────────────────────────────────────────────────

class Allocation(Base):
    """
    Officer deployment recommendation produced by the Allocation Engine.

    One row per (hotspot, pipeline_run) combination.
    Allocations are re-computed whenever the pipeline runs.
    """

    __tablename__ = TableName.ALLOCATIONS

    id              = Column(BigInteger, primary_key=True, autoincrement=True)
    hotspot_id      = Column(
        BigInteger,
        ForeignKey(f"{TableName.HOTSPOTS}.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    eis_score_id    = Column(
        BigInteger,
        ForeignKey(f"{TableName.EIS_SCORES}.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── Allocation decision ──────────────────────────────────────────────────
    officers_allocated  = Column(Integer, nullable=False,
                                  comment="Number of officers recommended for this hotspot")
    allocation_fraction = Column(Float, nullable=False,
                                  comment="Fraction of total available officers assigned here")
    priority_rank       = Column(Integer, nullable=False,
                                  comment="Rank in the deployment priority order")
    deployment_window   = Column(String(64), nullable=True,
                                  comment="Recommended time window, e.g. '07:00–10:00'")

    # ── Context ──────────────────────────────────────────────────────────────
    total_officers_available = Column(Integer, nullable=False,
                                       comment="Total officer count used for this calculation")
    eis_snapshot         = Column(Float, nullable=True,
                                   comment="EIS value at time of allocation")
    risk_category        = Column(String(16), nullable=True)

    # ── Pipeline metadata ────────────────────────────────────────────────────
    allocation_date  = Column(DateTime(timezone=False), nullable=False,
                               default=datetime.utcnow)
    pipeline_run_id  = Column(String(64), nullable=True)

    # ── Relationships ────────────────────────────────────────────────────────
    hotspot = relationship("Hotspot", back_populates="allocations")

    __table_args__ = (
        Index("ix_alloc_hotspot_date", "hotspot_id", "allocation_date"),
        Index("ix_alloc_priority",     "priority_rank"),
    )

    def __repr__(self) -> str:
        return (
            f"<Allocation id={self.id} hotspot_id={self.hotspot_id} "
            f"officers={self.officers_allocated} rank={self.priority_rank}>"
        )


# ── PatrolRoute ───────────────────────────────────────────────────────────────

class PatrolRoute(Base):
    """
    Optimised patrol route generated by OSMnx + NetworkX.

    stops_json stores the ordered list of hotspot stops with metadata,
    allowing the frontend to render the full route without additional queries.

    JSONB structure for stops_json:
    [
      {
        "sequence": 1,
        "hotspot_id": 7,
        "hotspot_name": "KR Market",
        "lat": 12.971,
        "lon": 77.594,
        "eis_score": 91.2,
        "estimated_arrival": "07:15",
        "recommended_duration_min": 30
      }, ...
    ]
    """

    __tablename__ = TableName.PATROL_ROUTES

    id              = Column(BigInteger, primary_key=True, autoincrement=True)
    hotspot_id      = Column(
        BigInteger,
        ForeignKey(f"{TableName.HOTSPOTS}.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Primary (first) hotspot in this route; NULL for a multi-zone route",
    )

    # ── Route identity ───────────────────────────────────────────────────────
    route_name       = Column(String(128), nullable=True,
                               comment="E.g. 'Zone A – Morning Shift'")
    shift_label      = Column(String(32), nullable=True,
                               comment="Morning | Afternoon | Evening | Night")
    officer_count    = Column(Integer, nullable=False, default=1)

    # ── Route geometry ───────────────────────────────────────────────────────
    route_geometry   = Column(
        Geometry(geometry_type="LINESTRING", srid=4326),
        nullable=True,
        comment="Full road-network path as a LINESTRING",
    )
    stops_json       = Column(JSONB, nullable=False, default=list,
                               comment="Ordered list of stop objects (see docstring)")

    # ── Route metrics ────────────────────────────────────────────────────────
    total_distance_km   = Column(Float, nullable=True)
    estimated_duration_min = Column(Integer, nullable=True)
    hotspots_covered    = Column(Integer, nullable=True,
                                  comment="Number of distinct hotspots in this route")
    total_eis_covered   = Column(Float, nullable=True,
                                  comment="Sum of EIS scores for all covered hotspots")

    # ── Pipeline metadata ────────────────────────────────────────────────────
    pipeline_run_id  = Column(String(64), nullable=True)
    created_at       = Column(DateTime(timezone=False), nullable=False,
                               default=datetime.utcnow)

    # ── Relationships ────────────────────────────────────────────────────────
    hotspot = relationship("Hotspot", back_populates="patrol_routes")

    __table_args__ = (
        Index("ix_patrol_routes_geometry_gist", "route_geometry", postgresql_using="gist"),
        Index("ix_patrol_routes_shift",         "shift_label"),
    )

    def __repr__(self) -> str:
        return (
            f"<PatrolRoute id={self.id} name={self.route_name!r} "
            f"stops={self.hotspots_covered} dist_km={self.total_distance_km}>"
        )
