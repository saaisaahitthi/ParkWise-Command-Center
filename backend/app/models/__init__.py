"""
app/models/__init__.py
──────────────────────
Re-exports all ORM models so that Alembic's env.py can import them with:
    from app.models import *
"""

from app.models.violation import Violation
from app.models.enriched_violation import EnrichedViolation
from app.models.hotspot import Hotspot
from app.models.analytics import (
    PeakWindow,
    EISScore,
    Forecast,
    Allocation,
    PatrolRoute,
)

__all__ = [
    "Violation",
    "EnrichedViolation",
    "Hotspot",
    "PeakWindow",
    "EISScore",
    "Forecast",
    "Allocation",
    "PatrolRoute",
]
