"""Enforcement Intelligence Score generation pipeline."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.analytics import EISScore, PeakWindow
from app.models.enriched_violation import EnrichedViolation
from app.models.hotspot import Hotspot


BATCH_SIZE = 1000


def max_scale(values: dict[int, float]) -> dict[int, float]:
    """Scale non-negative values to 0-100 using the dataset maximum."""
    maximum = max(values.values(), default=0.0)
    if maximum <= 0:
        return {key: 0.0 for key in values}
    return {
        key: max(0.0, min(100.0, (value / maximum) * 100.0))
        for key, value in values.items()
    }


def calculate_eis(
    frequency_score: float,
    recurrence_score: float,
    density_score: float,
    temporal_risk_score: float,
    severity_norm: float,
) -> tuple[float, float, float]:
    exposure_score = (
        0.35 * frequency_score
        + 0.20 * recurrence_score
        + 0.20 * density_score
        + 0.25 * temporal_risk_score
    )
    severity_multiplier = 0.6 + 0.8 * severity_norm
    eis_score = min(100.0, exposure_score * severity_multiplier)
    return exposure_score, severity_multiplier, eis_score


def risk_category(eis_score: float) -> str:
    if eis_score >= 75:
        return "Critical"
    if eis_score >= 50:
        return "High"
    if eis_score >= 25:
        return "Medium"
    return "Low"


class EISService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def run_pipeline(self) -> dict[str, Any]:
        pipeline_run_id = str(uuid.uuid4())
        computed_at = datetime.utcnow()

        hotspots = (
            self.db.query(
                Hotspot.id,
                Hotspot.total_violations,
                Hotspot.violation_density,
            )
            .order_by(Hotspot.id)
            .all()
        )
        hotspot_ids = [row.id for row in hotspots]

        enriched = self._enriched_aggregates()
        temporal = self._temporal_aggregates()

        frequency_raw = {
            hotspot_id: float(enriched.get(hotspot_id, {}).get("count", 0))
            for hotspot_id in hotspot_ids
        }
        recurrence_raw = {
            hotspot_id: float(enriched.get(hotspot_id, {}).get("recurrence", 0))
            for hotspot_id in hotspot_ids
        }
        density_raw = {
            row.id: float(
                row.violation_density
                if row.violation_density is not None
                and row.violation_density > 0
                else row.total_violations or 0
            )
            for row in hotspots
        }
        temporal_raw = {
            hotspot_id: float(temporal.get(hotspot_id, 0))
            for hotspot_id in hotspot_ids
        }

        frequency_scores = max_scale(frequency_raw)
        recurrence_scores = max_scale(recurrence_raw)
        density_scores = max_scale(density_raw)
        temporal_scores = max_scale(temporal_raw)

        score_rows: list[dict[str, Any]] = []
        for hotspot_id in hotspot_ids:
            severity_norm = max(
                0.0,
                min(
                    1.0,
                    float(enriched.get(hotspot_id, {}).get("severity", 0.0)),
                ),
            )
            exposure, multiplier, score = calculate_eis(
                frequency_score=frequency_scores[hotspot_id],
                recurrence_score=recurrence_scores[hotspot_id],
                density_score=density_scores[hotspot_id],
                temporal_risk_score=temporal_scores[hotspot_id],
                severity_norm=severity_norm,
            )
            score_rows.append(
                {
                    "hotspot_id": hotspot_id,
                    "computed_for_date": computed_at,
                    "frequency_score": frequency_scores[hotspot_id],
                    "recurrence_score": recurrence_scores[hotspot_id],
                    "density_score": density_scores[hotspot_id],
                    "temporal_risk_score": temporal_scores[hotspot_id],
                    "severity_norm": severity_norm,
                    "exposure_score": exposure,
                    "severity_multiplier": multiplier,
                    "eis_score": score,
                    "risk_category": risk_category(score),
                    "rank": None,
                    "pipeline_run_id": pipeline_run_id,
                    "created_at": computed_at,
                }
            )

        score_rows.sort(key=lambda row: (-row["eis_score"], row["hotspot_id"]))
        for rank, row in enumerate(score_rows, start=1):
            row["rank"] = rank

        try:
            self.db.query(EISScore).delete(synchronize_session=False)
            self.db.flush()
            for start in range(0, len(score_rows), BATCH_SIZE):
                self.db.bulk_insert_mappings(
                    EISScore,
                    score_rows[start : start + BATCH_SIZE],
                )
                self.db.flush()
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        return {
            "pipeline_run_id": pipeline_run_id,
            "hotspots_processed": len(hotspot_ids),
            "eis_scores_created": len(score_rows),
            "status": "completed",
        }

    def _enriched_aggregates(self) -> dict[int, dict[str, float]]:
        rows = (
            self.db.query(
                EnrichedViolation.hotspot_id,
                func.count(EnrichedViolation.id).label("violation_count"),
                func.sum(
                    case((EnrichedViolation.is_recurrence.is_(True), 1), else_=0)
                ).label("recurrence_count"),
                func.avg(EnrichedViolation.severity_score).label("avg_severity"),
            )
            .filter(EnrichedViolation.hotspot_id.isnot(None))
            .group_by(EnrichedViolation.hotspot_id)
            .all()
        )
        return {
            row.hotspot_id: {
                "count": float(row.violation_count or 0),
                "recurrence": float(row.recurrence_count or 0),
                "severity": float(row.avg_severity or 0.0),
            }
            for row in rows
        }

    def _temporal_aggregates(self) -> dict[int, float]:
        rows = (
            self.db.query(
                PeakWindow.hotspot_id,
                func.sum(PeakWindow.violation_count).label("violation_count"),
            )
            .filter(PeakWindow.hotspot_id.isnot(None))
            .group_by(PeakWindow.hotspot_id)
            .all()
        )
        return {
            row.hotspot_id: float(row.violation_count or 0)
            for row in rows
        }
