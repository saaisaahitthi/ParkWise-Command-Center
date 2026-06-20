"""
Lightweight mock API for frontend demos — no pandas/ML/Postgres required.

Serves the same JSON shapes the real FastAPI backend returns (post schema-alignment).
Use when Python 3.13 dependency install fails or Postgres is unavailable.

Usage (from backend/):
    pip install fastapi uvicorn
    python scripts/mock_api_server.py

Then in the frontend header, disable Mock mode to hit http://127.0.0.1:8000/api/v1
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

API_PREFIX = "/api/v1"
NOW = datetime.now(timezone.utc).isoformat()

MOCK_DASHBOARD_FULL: dict[str, Any] = {
    "executive_summary": {
        "total_hotspots": 4,
        "active_hotspots": 4,
        "critical_hotspots": 1,
        "high_risk_hotspots": 2,
        "total_forecasts": 4,
        "total_allocated_officers": 20,
        "latest_route_distance_km": 8.4,
        "latest_route_duration_min": 45,
        "last_updated_at": NOW,
    },
    "risk_distribution": {"Critical": 1, "High": 2, "Medium": 1, "Low": 0},
    "hotspot_map": [
        {
            "hotspot_id": 1,
            "name": "Civic Center Junction",
            "latitude": 23.1678,
            "longitude": 79.9322,
            "hotspot_type": "Commercial Hub",
            "violation_count": 482,
            "latest_eis": 78.4,
            "risk_category": "High",
            "forecasted_eis": 85.2,
            "officers_allocated": 6,
        },
        {
            "hotspot_id": 2,
            "name": "Jabalpur Railway Station",
            "latitude": 23.1667,
            "longitude": 79.95,
            "hotspot_type": "Transit Node",
            "violation_count": 703,
            "latest_eis": 92.1,
            "risk_category": "Critical",
            "forecasted_eis": 94.5,
            "officers_allocated": 8,
        },
        {
            "hotspot_id": 3,
            "name": "Gorakhpur Market Area",
            "latitude": 23.1539,
            "longitude": 79.9247,
            "hotspot_type": "Shopping District",
            "violation_count": 558,
            "latest_eis": 81.5,
            "risk_category": "High",
            "forecasted_eis": 88.0,
            "officers_allocated": 4,
        },
        {
            "hotspot_id": 4,
            "name": "Sadar Cantt Road",
            "latitude": 23.1492,
            "longitude": 79.9489,
            "hotspot_type": "Main Thoroughfare",
            "violation_count": 329,
            "latest_eis": 58.2,
            "risk_category": "Medium",
            "forecasted_eis": 68.0,
            "officers_allocated": 2,
        },
    ],
    "temporal_overview": {},
    "forecast_overview": {},
    "allocation_overview": {},
    "routing_overview": {},
}

MOCK_EIS_SCORES = {
    "total": 4,
    "items": [
        {
            "id": 1,
            "rank": 1,
            "hotspot_id": 2,
            "eis_score": 92.1,
            "risk_category": "Critical",
            "computed_for_date": NOW,
            "created_at": NOW,
            "components": {
                "frequency_score": 0.95,
                "recurrence_score": 0.92,
                "density_score": 0.88,
                "temporal_risk_score": 0.91,
                "severity_norm": 0.85,
                "exposure_score": 0.9,
                "severity_multiplier": 1.2,
            },
        },
        {
            "id": 2,
            "rank": 2,
            "hotspot_id": 3,
            "eis_score": 81.5,
            "risk_category": "High",
            "computed_for_date": NOW,
            "created_at": NOW,
            "components": {
                "frequency_score": 0.84,
                "recurrence_score": 0.81,
                "density_score": 0.78,
                "temporal_risk_score": 0.82,
                "severity_norm": 0.75,
                "exposure_score": 0.8,
                "severity_multiplier": 1.15,
            },
        },
        {
            "id": 3,
            "rank": 3,
            "hotspot_id": 1,
            "eis_score": 78.4,
            "risk_category": "High",
            "computed_for_date": NOW,
            "created_at": NOW,
            "components": {
                "frequency_score": 0.82,
                "recurrence_score": 0.79,
                "density_score": 0.75,
                "temporal_risk_score": 0.8,
                "severity_norm": 0.72,
                "exposure_score": 0.78,
                "severity_multiplier": 1.1,
            },
        },
        {
            "id": 4,
            "rank": 4,
            "hotspot_id": 4,
            "eis_score": 58.2,
            "risk_category": "Medium",
            "computed_for_date": NOW,
            "created_at": NOW,
            "components": {
                "frequency_score": 0.6,
                "recurrence_score": 0.58,
                "density_score": 0.55,
                "temporal_risk_score": 0.62,
                "severity_norm": 0.5,
                "exposure_score": 0.56,
                "severity_multiplier": 1.0,
            },
        },
    ],
}

MOCK_FORECAST_SUMMARY = {
    "total_forecasts": 4,
    "average_predicted_eis": 75.3,
    "max_predicted_eis": 94.5,
    "risk_distribution": {"Critical": 1, "High": 2, "Medium": 1},
    "horizon_distribution": {"7": 4},
    "latest_generated_at": NOW,
    "trained_horizons": [1, 7],
    "models_in_memory": 2,
}

MOCK_FORECAST_TOP = [
    {
        "forecast_id": 1,
        "hotspot_id": 2,
        "forecast_date": NOW,
        "horizon_days": 7,
        "predicted_eis": 94.5,
        "predicted_risk_category": "Critical",
        "confidence_lower": 88.0,
        "confidence_upper": 98.0,
        "top_features": {"temporal_risk_score": 0.91},
    },
    {
        "forecast_id": 2,
        "hotspot_id": 3,
        "forecast_date": NOW,
        "horizon_days": 7,
        "predicted_eis": 88.0,
        "predicted_risk_category": "High",
        "confidence_lower": 82.0,
        "confidence_upper": 92.0,
        "top_features": {"frequency_score": 0.84},
    },
    {
        "forecast_id": 3,
        "hotspot_id": 1,
        "forecast_date": NOW,
        "horizon_days": 7,
        "predicted_eis": 85.2,
        "predicted_risk_category": "High",
        "confidence_lower": 78.0,
        "confidence_upper": 90.0,
        "top_features": {"density_score": 0.75},
    },
]

MOCK_ALLOCATION = {
    "total_officers": 20,
    "hotspots_covered": 4,
    "unallocated_officers": 0,
    "computed_at": NOW,
    "allocations": [
        {
            "id": 1,
            "hotspot_id": 2,
            "hotspot_name": "Jabalpur Railway Station",
            "officers_allocated": 8,
            "allocation_fraction": 0.4,
            "priority_rank": 1,
            "deployment_window": "Shift 2 (14:00 - 22:00)",
            "eis_snapshot": 92.1,
            "risk_category": "Critical",
            "allocation_date": NOW,
        },
        {
            "id": 2,
            "hotspot_id": 1,
            "hotspot_name": "Civic Center Junction",
            "officers_allocated": 6,
            "allocation_fraction": 0.3,
            "priority_rank": 2,
            "deployment_window": None,
            "eis_snapshot": 78.4,
            "risk_category": "High",
            "allocation_date": NOW,
        },
        {
            "id": 3,
            "hotspot_id": 3,
            "hotspot_name": "Gorakhpur Market Area",
            "officers_allocated": 4,
            "allocation_fraction": 0.2,
            "priority_rank": 3,
            "deployment_window": None,
            "eis_snapshot": 81.5,
            "risk_category": "High",
            "allocation_date": NOW,
        },
        {
            "id": 4,
            "hotspot_id": 4,
            "hotspot_name": "Sadar Cantt Road",
            "officers_allocated": 2,
            "allocation_fraction": 0.1,
            "priority_rank": 4,
            "deployment_window": None,
            "eis_snapshot": 58.2,
            "risk_category": "Medium",
            "allocation_date": NOW,
        },
    ],
}

MOCK_ROUTE_STOPS = [
    {
        "sequence": 1,
        "hotspot_id": 1,
        "hotspot_name": "Civic Center Junction",
        "latitude": 23.1678,
        "longitude": 79.9322,
        "risk_category": "High",
    },
    {
        "sequence": 2,
        "hotspot_id": 2,
        "hotspot_name": "Jabalpur Railway Station",
        "latitude": 23.1667,
        "longitude": 79.95,
        "risk_category": "Critical",
    },
    {
        "sequence": 3,
        "hotspot_id": 4,
        "hotspot_name": "Sadar Cantt Road",
        "latitude": 23.1492,
        "longitude": 79.9489,
        "risk_category": "Medium",
    },
    {
        "sequence": 4,
        "hotspot_id": 3,
        "hotspot_name": "Gorakhpur Market Area",
        "latitude": 23.1539,
        "longitude": 79.9247,
        "risk_category": "High",
    },
]

MOCK_ROUTING_LATEST = {
    "route_id": 1,
    "route_name": "Default Patrol",
    "shift_label": "default",
    "officer_count": 20,
    "total_distance_km": 8.4,
    "estimated_duration_min": 45,
    "hotspots_covered": 4,
    "total_eis_covered": 310.2,
    "stops": MOCK_ROUTE_STOPS,
    "created_at": NOW,
}

MOCK_SIMULATOR_BASELINE = [
    {
        "hotspot_id": 2,
        "hotspot_name": "Jabalpur Railway Station",
        "current_eis": 92.1,
        "current_risk_category": "Critical",
        "officers_allocated": 8,
        "frequency_score": 0.95,
        "recurrence_score": 0.92,
        "density_score": 0.88,
        "temporal_risk_score": 0.91,
        "severity_norm": 0.85,
        "exposure_score": 0.9,
        "severity_multiplier": 1.2,
    },
    {
        "hotspot_id": 1,
        "hotspot_name": "Civic Center Junction",
        "current_eis": 78.4,
        "current_risk_category": "High",
        "officers_allocated": 6,
        "frequency_score": 0.82,
        "recurrence_score": 0.79,
        "density_score": 0.75,
        "temporal_risk_score": 0.8,
        "severity_norm": 0.72,
        "exposure_score": 0.78,
        "severity_multiplier": 1.1,
    },
]

MOCK_SIMULATOR_PRESETS = [
    {
        "name": "Increase officers by 20%",
        "description": "Redistribute a 20% larger officer pool by simulated risk.",
        "overrides": {"total_officers": 24},
    },
    {
        "name": "Reduce frequency by 15%",
        "description": "Model a 15% reduction in violation frequency.",
        "overrides": {"frequency_reduction_pct": 0.15},
    },
]

app = FastAPI(title="ParkWise Mock API", version="demo")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "mock"}


@app.get(f"{API_PREFIX}/dashboard/full")
def dashboard_full() -> dict[str, Any]:
    return MOCK_DASHBOARD_FULL


@app.get(f"{API_PREFIX}/eis/scores")
def eis_scores() -> dict[str, Any]:
    return MOCK_EIS_SCORES


@app.get(f"{API_PREFIX}/forecast/summary")
def forecast_summary() -> dict[str, Any]:
    return MOCK_FORECAST_SUMMARY


@app.get(f"{API_PREFIX}/forecast/top")
def forecast_top() -> list[dict[str, Any]]:
    return MOCK_FORECAST_TOP


@app.post(f"{API_PREFIX}/forecast/generate")
def forecast_generate(_: dict[str, Any] | None = None) -> dict[str, str]:
    return {"status": "generated"}


@app.get(f"{API_PREFIX}/allocation/latest")
def allocation_latest() -> dict[str, Any]:
    return MOCK_ALLOCATION


@app.post(f"{API_PREFIX}/allocation/compute")
def allocation_compute(_: dict[str, Any] | None = None) -> dict[str, Any]:
    return MOCK_ALLOCATION


@app.get(f"{API_PREFIX}/routing/latest")
def routing_latest() -> dict[str, Any]:
    return MOCK_ROUTING_LATEST


@app.post(f"{API_PREFIX}/routing/generate")
def routing_generate(_: dict[str, Any] | None = None) -> dict[str, Any]:
    geometry = [
        {"lat": stop["latitude"], "lng": stop["longitude"]} for stop in MOCK_ROUTE_STOPS
    ]
    return {
        "route_id": 2,
        "total_stops": 4,
        "critical_stops": 1,
        "high_stops": 2,
        "total_distance_km": 8.4,
        "estimated_travel_minutes": 25,
        "estimated_total_minutes": 45,
        "route_geometry": geometry,
        "stops": MOCK_ROUTE_STOPS,
    }


@app.get(f"{API_PREFIX}/simulator/baseline")
def simulator_baseline() -> list[dict[str, Any]]:
    return MOCK_SIMULATOR_BASELINE


@app.get(f"{API_PREFIX}/simulator/presets")
def simulator_presets() -> list[dict[str, Any]]:
    return MOCK_SIMULATOR_PRESETS


@app.post(f"{API_PREFIX}/simulator/run")
def simulator_run(body: dict[str, Any]) -> dict[str, Any]:
    overrides = body.get("overrides") or {}
    officers = overrides.get("total_officers", 20)
    return {
        "scenario_name": body.get("scenario_name", "Mock scenario"),
        "total_hotspots": 4,
        "improved_hotspots": 2,
        "worsened_hotspots": 0,
        "unchanged_hotspots": 2,
        "baseline_average_eis": 77.5,
        "simulated_average_eis": max(45.0, 95.0 - officers * 1.2),
        "average_eis_delta": -5.0,
        "baseline_total_officers": 20,
        "simulated_total_officers": officers,
        "hotspot_results": [{"impact_notes": ["Mock simulation applied."]}],
        "summary": {"officers_added": max(0, officers - 20)},
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
