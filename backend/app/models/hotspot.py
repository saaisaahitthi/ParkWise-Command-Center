"""
app/models/hotspot.py
─────────────────────
Hotspots table — one row per DBSCAN cluster identified by the
Micro-Hotspot Detection pipeline.

hotspot_id is the universal spatial identifier referenced by:
  • enriched_violations
  • eis_scores
  • forecasts
  • allocations
  • patrol_routes
"""

from __future__ import annotations

from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.constants import TableName
from app.db.base import Base


class Hotspot(Base):
    """
    Represents a spatial cluster of parking violations.

    Centroid geometry allows spatial joins, proximity queries, and map rendering.
    The convex_hull geometry captures the spatial footprint of the cluster.
    """

    __tablename__ = TableName.HOTSPOTS

    # ── Primary key ───────────────────────────────────────────────────────────
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # ── Cluster identity ──────────────────────────────────────────────────────
    cluster_label    = Column(Integer, nullable=False, unique=True,
                               comment="DBSCAN cluster label (≥0; -1 noise rows excluded)")
    hotspot_name     = Column(String(256), nullable=True,
                               comment="Human-readable label, derived from dominant junction name")
    zone_id          = Column(String(64), nullable=True, index=True,
                               comment="Optional administrative zone identifier")

    # ── Geometry ──────────────────────────────────────────────────────────────
    centroid         = Column(
        Geometry(geometry_type="POINT", srid=4326),
        nullable=False,
        comment="Geographic centroid of the cluster (lon, lat)",
    )
    convex_hull      = Column(
        Geometry(geometry_type="POLYGON", srid=4326),
        nullable=True,
        comment="Convex hull bounding the violation points in the cluster",
    )
    centroid_lat     = Column(Float, nullable=False,
                               comment="Redundant lat for non-spatial queries")
    centroid_lon     = Column(Float, nullable=False,
                               comment="Redundant lon for non-spatial queries")
    radius_m         = Column(Float, nullable=True,
                               comment="Approximate cluster radius in metres")

    # ── Aggregate stats (refreshed each pipeline run) ─────────────────────────
    total_violations = Column(Integer, nullable=False, default=0,
                               comment="Total violation count in this cluster")
    unique_dates     = Column(Integer, nullable=True,
                               comment="Number of distinct dates with violations")
    dominant_violation_type = Column(String(128), nullable=True,
                                      comment="Most frequent violation type in this cluster")
    dominant_vehicle_category = Column(String(64), nullable=True)
    avg_fine_amount  = Column(Float, nullable=True)

    # ── Spatial density ───────────────────────────────────────────────────────
    violation_density = Column(Float, nullable=True,
                                comment="Violations per km² within the cluster footprint")

    # ── Pipeline metadata ─────────────────────────────────────────────────────
    pipeline_run_id  = Column(String(64), nullable=True)
    created_at       = Column(DateTime(timezone=False), nullable=False,
                               default=datetime.utcnow)
    updated_at       = Column(DateTime(timezone=False), nullable=False,
                               default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Relationships ─────────────────────────────────────────────────────────
    enriched_violations = relationship(
        "EnrichedViolation", back_populates="hotspot", lazy="dynamic"
    )
    eis_scores   = relationship("EISScore",     back_populates="hotspot", lazy="dynamic")
    forecasts    = relationship("Forecast",      back_populates="hotspot", lazy="dynamic")
    allocations  = relationship("Allocation",    back_populates="hotspot")
    patrol_routes = relationship("PatrolRoute",  back_populates="hotspot")

    # ── Indexes ───────────────────────────────────────────────────────────────
    __table_args__ = (
        Index("ix_hotspots_centroid_gist",   "centroid",    postgresql_using="gist"),
        Index("ix_hotspots_hull_gist",       "convex_hull", postgresql_using="gist"),
        Index("ix_hotspots_zone",            "zone_id"),
        Index("ix_hotspots_total_violations","total_violations"),
    )

    def __repr__(self) -> str:
        return (
            f"<Hotspot id={self.id} label={self.cluster_label} "
            f"name={self.hotspot_name!r} violations={self.total_violations}>"
        )
