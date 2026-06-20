"""
app/main.py
───────────
FastAPI application factory for ParkWise Command Center.

Responsibilities:
  • Configure structured logging
  • Register all API routers
  • Add CORS middleware
  • Add global exception handlers
  • Expose lifespan (startup / shutdown hooks)
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import (
    DataNotFoundError,
    DataValidationError,
    ForecastModelNotTrainedError,
    ParkWiseBaseError,
    PipelineError,
)
from app.core.logging import configure_logging, get_logger
from app.db.session import engine

logger = get_logger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Startup: configure logging, verify DB connectivity.
    Shutdown: dispose connection pool cleanly.
    """
    configure_logging()
    logger.info(
        "parkwise_startup",
        app=settings.APP_NAME,
        version=settings.APP_VERSION,
        env=settings.APP_ENV,
    )

    # Verify DB connection
    try:
        with engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("SELECT 1"))
        logger.info("database_connected", url=settings.POSTGRES_SERVER)
    except Exception as exc:
        logger.error("database_connection_failed", error=str(exc))
        # Don't crash on startup — let individual requests fail gracefully
        # so the health endpoint still responds

    yield

    # Shutdown
    engine.dispose()
    logger.info("parkwise_shutdown")


# ── Application factory ───────────────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "AI-Powered Enforcement Intelligence Platform for Parking-Induced Congestion. "
            "Transforms historical parking violation data into actionable traffic enforcement decisions."
        ),
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        lifespan=lifespan,
    )

    # ── Middleware ────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Request timing middleware ─────────────────────────────────────────────
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"
        return response

    # ── Exception handlers ────────────────────────────────────────────────────
    @app.exception_handler(DataNotFoundError)
    async def not_found_handler(request: Request, exc: DataNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": exc.message, "detail": exc.detail},
        )

    @app.exception_handler(DataValidationError)
    async def validation_handler(request: Request, exc: DataValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": exc.message, "detail": exc.detail},
        )

    @app.exception_handler(ForecastModelNotTrainedError)
    async def model_not_trained_handler(request: Request, exc: ForecastModelNotTrainedError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"error": exc.message, "detail": exc.detail},
        )

    @app.exception_handler(PipelineError)
    async def pipeline_error_handler(request: Request, exc: PipelineError):
        logger.error("pipeline_error", error=exc.message, detail=exc.detail)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": exc.message, "detail": exc.detail},
        )

    @app.exception_handler(ParkWiseBaseError)
    async def parkwise_error_handler(request: Request, exc: ParkWiseBaseError):
        return JSONResponse(
            status_code=exc.default_status_code,
            content={"error": exc.message, "detail": exc.detail},
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        logger.error("unhandled_exception", error=str(exc), path=request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "An unexpected server error occurred."},
        )

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # ── Health check ──────────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"], summary="Health check")
    async def health_check():
        return {
            "status": "ok",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "env": settings.APP_ENV,
        }

    return app


app = create_app()
