"""
app/models/enriched_violation.py
─────────────────────────────────
Enriched violations table — 1:1 with the violations table.

Added by the analytics pipeline:
  • hotspot_id       — assigned after DBSCAN clustering
  • severity_score   — normalised [0,1] from VIOLATION_SEVERITY map
  • is_recurrence    — True if the same junction saw ≥1 violation in prior 7 days
  • temporal_flag    — True if violation occurred in a defined peak window
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.core.constants import TableName
from app.db.base import Base


class EnrichedViolation(Base):
    """
    Derived attributes for each raw violation, computed by the pipeline.
    Never populated during CSV ingestion — updated by run_pipeline.py.
    """

    __tablename__ = TableName.ENRICHED_VIOLATIONS

    # ── Primary key ───────────────────────────────────────────────────────────
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # ── Foreign keys ──────────────────────────────────────────────────────────
    violation_id = Column(
        BigInteger,
        ForeignKey(f"{TableName.VIOLATIONS}.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        comment="1:1 link back to the raw violation",
    )
    hotspot_id = Column(
        BigInteger,
        ForeignKey(f"{TableName.HOTSPOTS}.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Assigned DBSCAN cluster; NULL if noise point",
    )

    # ── Derived EIS component scores ──────────────────────────────────────────
    severity_score  = Column(Float, nullable=False, default=0.5,
                              comment="Normalised [0,1] violation severity")
    is_recurrence   = Column(Boolean, nullable=False, default=False,
                              comment="True if location had violations in prior 7 days")
    temporal_flag   = Column(Boolean, nullable=False, default=False,
                              comment="True if violation falls within a peak time window")

    # ── Cluster membership ────────────────────────────────────────────────────
    cluster_label   = Column(Integer, nullable=True,
                              comment="Raw DBSCAN label (-1 = noise)")
    distance_to_core = Column(Float, nullable=True,
                               comment="Distance to cluster core point (degrees)")

    # ── Processing metadata ───────────────────────────────────────────────────
    pipeline_run_id = Column(String(64), nullable=True,
                              comment="Identifier for the pipeline run that produced this row")
    processed_at    = Column(DateTime(timezone=False), nullable=False,
                              default=datetime.utcnow)

    # ── Relationships ─────────────────────────────────────────────────────────
    violation = relationship("Violation", back_populates="enriched")
    hotspot   = relationship("Hotspot",   back_populates="enriched_violations")

    # ── Indexes ───────────────────────────────────────────────────────────────
    __table_args__ = (
        Index("ix_enriched_hotspot_severity", "hotspot_id", "severity_score"),
    )

    def __repr__(self) -> str:
        return (
            f"<EnrichedViolation id={self.id} violation_id={self.violation_id} "
            f"hotspot_id={self.hotspot_id} severity={self.severity_score:.2f}>"
        )
