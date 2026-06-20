"""
app/db/session.py
─────────────────
Database engine and session factory.

Uses SQLAlchemy 2.x synchronous API with psycopg2 (the dataset is processed
in batch — no streaming/async DB calls required per the frozen architecture).

Connection pool is configured for a Render.com free-tier backend
(limited concurrent connections) while remaining tunable via env vars.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


# ── Engine ────────────────────────────────────────────────────────────────────

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,          # Detect stale connections before use
    echo=settings.DEBUG,         # Log SQL in development only
    future=True,                 # SQLAlchemy 2.x style
)


# ── PostGIS / pg extension health check ──────────────────────────────────────

@event.listens_for(engine, "connect")
def _verify_postgis(dbapi_connection, connection_record):  # noqa: ANN001
    """Emit a warning if PostGIS extension is unavailable."""
    cursor = dbapi_connection.cursor()
    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'postgis');"
    )
    (postgis_available,) = cursor.fetchone()
    cursor.close()
    if not postgis_available:
        logger.warning(
            "postgis_extension_missing",
            message="PostGIS extension is not installed. "
                    "Run: CREATE EXTENSION postgis; in your database.",
        )


# ── Session Factory ───────────────────────────────────────────────────────────

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,   # Avoids lazy-load issues after commit
)


# ── Context manager for scripts / pipeline code ───────────────────────────────

@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Use in non-request contexts (e.g., ML pipeline scripts, Alembic hooks).

    Example:
        with get_db_context() as db:
            hotspots = db.query(Hotspot).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ── FastAPI dependency ────────────────────────────────────────────────────────

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency — yields a DB session per request.

    Usage in a router:
        @router.get("/hotspots")
        def list_hotspots(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
