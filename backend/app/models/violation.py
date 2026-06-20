"""
app/models/violation.py
───────────────────────
Raw violations table — direct representation of the ingested CSV dataset
(jan_to_may_police_violation_anonymized.csv).

Column names mirror the dataset schema discovered during Phase 1 analysis.
UTC timestamps are preserved as-is; timezone conversion happens in the
Temporal Intelligence Engine.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from geoalchemy2 import Geometry
from sqlalchemy import (
    BigInteger,
    Boolean,
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


class Violation(Base):
    """
    Stores one row per parking violation record from the source dataset.
    This table is append-only; it is never updated after initial ingestion.
    """

    __tablename__ = TableName.VIOLATIONS

    # ── Primary key ───────────────────────────────────────────────────────────
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # ── Raw violation identifiers ─────────────────────────────────────────────
    violation_id      = Column(String(64), nullable=True, index=True,
                               comment="Original violation ID from dataset, if present")
    violation_type    = Column(String(128), nullable=False,
                               comment="Category of parking violation")
    violation_code    = Column(String(32), nullable=True,
                               comment="Enforcement code, if available")

    # ── Vehicle information ───────────────────────────────────────────────────
    vehicle_category  = Column(String(64), nullable=True,
                               comment="Two-wheeler, car, truck, etc.")
    vehicle_type      = Column(String(64), nullable=True)

    # ── Timestamps (stored in UTC) ────────────────────────────────────────────
    violation_date    = Column(DateTime(timezone=False), nullable=False, index=True,
                               comment="UTC datetime of the violation")
    hour_of_day       = Column(Integer, nullable=True,
                               comment="Derived: 0–23, stored for query performance")
    day_of_week       = Column(Integer, nullable=True,
                               comment="Derived: 0=Monday … 6=Sunday")
    week_number       = Column(Integer, nullable=True,
                               comment="ISO week number")
    month             = Column(Integer, nullable=True,
                               comment="1–12")

    # ── Location ──────────────────────────────────────────────────────────────
    latitude          = Column(Float, nullable=True)
    longitude         = Column(Float, nullable=True)
    location          = Column(
        Geometry(geometry_type="POINT", srid=4326),
        nullable=True,
        comment="PostGIS POINT geometry (lon, lat) — populated during ingestion",
    )
    junction_name     = Column(String(256), nullable=True, index=True,
                               comment="Named junction from dataset; 49.5% may be NULL")
    ward              = Column(String(128), nullable=True)
    zone              = Column(String(128), nullable=True)
    address_raw       = Column(Text, nullable=True)

    # ── Fine / penalty ────────────────────────────────────────────────────────
    fine_amount       = Column(Float, nullable=True)
    is_paid           = Column(Boolean, nullable=True)

    # ── Metadata ──────────────────────────────────────────────────────────────
    data_source       = Column(String(64), nullable=False, default="csv_import")
    ingested_at       = Column(DateTime(timezone=False), nullable=False,
                               default=datetime.utcnow)

    # ── Relationships ─────────────────────────────────────────────────────────
    enriched = relationship(
        "EnrichedViolation",
        back_populates="violation",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # ── Indexes ───────────────────────────────────────────────────────────────
    __table_args__ = (
        Index("ix_violations_location_gist", "location", postgresql_using="gist"),
        Index("ix_violations_date_type", "violation_date", "violation_type"),
        Index("ix_violations_junction_date", "junction_name", "violation_date"),
    )

    def __repr__(self) -> str:
        return (
            f"<Violation id={self.id} type={self.violation_type!r} "
            f"date={self.violation_date} junction={self.junction_name!r}>"
        )
