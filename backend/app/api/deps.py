"""
app/api/deps.py
───────────────
FastAPI dependency functions.

All router dependencies should be imported from this module to keep
dependency logic centralised and easy to test/mock.
"""

from __future__ import annotations

from typing import Generator, Optional

from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.constants import Pagination
from app.db.session import get_db


# ── Database session ──────────────────────────────────────────────────────────

def db_session(db: Session = Depends(get_db)) -> Session:
    """
    Thin wrapper so routers can write Depends(db_session)
    rather than Depends(get_db) — keeps import surface clean.
    """
    return db


# ── Configuration ─────────────────────────────────────────────────────────────

def app_settings(settings: Settings = Depends(get_settings)) -> Settings:
    return settings


# ── Pagination ────────────────────────────────────────────────────────────────

class PaginationParams:
    """
    Reusable pagination dependency.

    Usage:
        @router.get("/hotspots")
        def list_hotspots(pagination: PaginationParams = Depends()):
            skip = pagination.skip
            limit = pagination.limit
    """

    def __init__(
        self,
        page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
        page_size: int = Query(
            default=Pagination.DEFAULT_PAGE_SIZE,
            ge=1,
            le=Pagination.MAX_PAGE_SIZE,
            description=f"Items per page (max {Pagination.MAX_PAGE_SIZE})",
        ),
    ) -> None:
        self.page = page
        self.page_size = page_size

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


# ── Risk category filter ──────────────────────────────────────────────────────

def risk_category_filter(
    risk: Optional[str] = Query(
        default=None,
        description="Filter by risk category: Low | Medium | High | Critical",
        pattern="^(Low|Medium|High|Critical)$",
    )
) -> Optional[str]:
    return risk


# ── Hotspot ID validation ─────────────────────────────────────────────────────

def valid_hotspot_id(hotspot_id: int) -> int:
    if hotspot_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="hotspot_id must be a positive integer",
        )
    return hotspot_id
