"""
app/api/v1/router.py
─────────────────────
Central v1 API router — registers all feature endpoint sub-routers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    dashboard,
    hotspots,
    eis,
    temporal,
    forecast,
    allocation,
    patrol,
    routing,
    simulator,
    violations,
)

api_router = APIRouter()

api_router.include_router(dashboard.router,   prefix="/dashboard",   tags=["Dashboard"])
api_router.include_router(violations.router,  prefix="/violations",  tags=["Violations"])
api_router.include_router(hotspots.router,    prefix="/hotspots",    tags=["Hotspots"])
api_router.include_router(eis.router,         prefix="/eis",         tags=["EIS"])
api_router.include_router(temporal.router,    prefix="/temporal",    tags=["Temporal"])
api_router.include_router(forecast.router,    prefix="/forecast",    tags=["Forecast"])
api_router.include_router(allocation.router,  prefix="/allocation",  tags=["Allocation"])
api_router.include_router(routing.router,     prefix="/routing",     tags=["Routing"])
api_router.include_router(patrol.router,      prefix="/patrol",      tags=["Patrol"])
api_router.include_router(simulator.router,   prefix="/simulator",   tags=["Simulator"])
