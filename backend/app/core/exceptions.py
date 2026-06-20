"""
app/core/exceptions.py
──────────────────────
Domain-level exception hierarchy for ParkWise.

FastAPI exception handlers are registered in app/main.py and translate
these into appropriate HTTP responses with structured JSON bodies.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class ParkWiseBaseError(Exception):
    """Root exception for all ParkWise application errors."""

    default_message: str = "An unexpected error occurred."
    default_status_code: int = 500

    def __init__(
        self,
        message: Optional[str] = None,
        detail: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.message = message or self.default_message
        self.detail = detail or {}
        super().__init__(self.message)


# ── Data / Pipeline errors ────────────────────────────────────────────────────

class DataNotFoundError(ParkWiseBaseError):
    """Requested resource does not exist in the database."""
    default_message = "Requested data not found."
    default_status_code = 404


class DataValidationError(ParkWiseBaseError):
    """Input data failed validation before entering the ML pipeline."""
    default_message = "Data validation failed."
    default_status_code = 422


class PipelineError(ParkWiseBaseError):
    """A failure occurred inside an ML/analytics pipeline step."""
    default_message = "Pipeline execution failed."
    default_status_code = 500


# ── Hotspot errors ────────────────────────────────────────────────────────────

class HotspotNotFoundError(DataNotFoundError):
    """A specific hotspot_id does not exist."""
    default_message = "Hotspot not found."


class InsufficientDataForClusteringError(PipelineError):
    """Not enough violation records to run DBSCAN meaningfully."""
    default_message = "Insufficient data to perform hotspot clustering."
    default_status_code = 422


# ── EIS errors ────────────────────────────────────────────────────────────────

class EISComputationError(PipelineError):
    """EIS score computation failed for one or more hotspots."""
    default_message = "EIS computation encountered an error."


# ── Forecast errors ───────────────────────────────────────────────────────────

class ForecastModelNotTrainedError(ParkWiseBaseError):
    """The LightGBM forecast model has not been trained yet."""
    default_message = "Forecast model is not available. Run the training pipeline first."
    default_status_code = 503


class ForecastError(PipelineError):
    """An error occurred during risk forecasting."""
    default_message = "Risk forecasting failed."


# ── Allocation / routing errors ───────────────────────────────────────────────

class AllocationError(PipelineError):
    """Officer allocation computation failed."""
    default_message = "Officer allocation computation failed."


class RouteOptimizationError(PipelineError):
    """Patrol route optimisation failed (OSMnx / NetworkX)."""
    default_message = "Patrol route optimisation failed."


# ── Configuration errors ──────────────────────────────────────────────────────

class ConfigurationError(ParkWiseBaseError):
    """Application is misconfigured at startup."""
    default_message = "Application configuration error."
    default_status_code = 500
