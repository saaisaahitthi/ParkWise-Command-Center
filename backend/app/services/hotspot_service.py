"""Hotspot grouping and violation enrichment pipeline."""

from __future__ import annotations

import math
import uuid
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from geoalchemy2.elements import WKTElement
from sqlalchemy.orm import Session

from app.models.enriched_violation import EnrichedViolation
from app.models.hotspot import Hotspot
from app.models.violation import Violation


BATCH_SIZE = 1000
NO_JUNCTION = "no junction"


@dataclass
class GroupStats:
    count: int = 0
    latitude_sum: float = 0.0
    longitude_sum: float = 0.0
    dates: set[Any] = field(default_factory=set)
    violation_types: Counter[str] = field(default_factory=Counter)
    vehicle_categories: Counter[str] = field(default_factory=Counter)
    zones: Counter[str] = field(default_factory=Counter)
    fine_sum: float = 0.0
    fine_count: int = 0


def valid_coordinates(latitude: float | None, longitude: float | None) -> bool:
    return (
        latitude is not None
        and longitude is not None
        and math.isfinite(latitude)
        and math.isfinite(longitude)
        and -90 <= latitude <= 90
        and -180 <= longitude <= 180
    )


def hotspot_group_key(
    junction_name: str | None,
    latitude: float,
    longitude: float,
) -> tuple[str, str] | tuple[str, float, float]:
    junction = (junction_name or "").strip()
    if junction and junction.casefold() != NO_JUNCTION:
        return ("junction", junction)
    return ("coordinates", round(latitude, 3), round(longitude, 3))


def severity_score(violation_type: str | None) -> float:
    value = (violation_type or "").upper()
    for marker, score in (
        ("DOUBLE PARKING", 1.0),
        ("MAIN ROAD", 0.9),
        ("FOOTPATH", 0.8),
        ("NO PARKING", 0.6),
        ("WRONG PARKING", 0.4),
    ):
        if marker in value:
            return score
    return 0.5


def is_rush_hour(hour: int | None) -> bool:
    return hour is not None and (7 <= hour <= 10 or 17 <= hour <= 21)


def _most_common(counter: Counter[str], max_len: int) -> str | None:
    if not counter:
        return None
    return counter.most_common(1)[0][0][:max_len]


class HotspotService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def run_pipeline(self) -> dict[str, Any]:
        pipeline_run_id = str(uuid.uuid4())
        processed_at = datetime.utcnow()

        try:
            self._delete_existing()
            groups, violations_read = self._aggregate_groups()
            hotspot_ids = self._create_hotspots(
                groups=groups,
                pipeline_run_id=pipeline_run_id,
                timestamp=processed_at,
            )
            enriched_created = self._create_enriched_violations(
                groups=groups,
                hotspot_ids=hotspot_ids,
                pipeline_run_id=pipeline_run_id,
                processed_at=processed_at,
            )
        except Exception:
            self.db.rollback()
            raise

        return {
            "pipeline_run_id": pipeline_run_id,
            "violations_read": violations_read,
            "hotspots_created": len(hotspot_ids),
            "enriched_violations_created": enriched_created,
            "status": "completed",
        }

    def _delete_existing(self) -> None:
        self.db.query(EnrichedViolation).delete(synchronize_session=False)
        self.db.flush()
        self.db.query(Hotspot).delete(synchronize_session=False)
        self.db.commit()

    def _violation_batches(self):
        last_id = 0
        while True:
            rows = (
                self.db.query(
                    Violation.id,
                    Violation.violation_type,
                    Violation.vehicle_category,
                    Violation.vehicle_type,
                    Violation.violation_date,
                    Violation.hour_of_day,
                    Violation.latitude,
                    Violation.longitude,
                    Violation.junction_name,
                    Violation.zone,
                    Violation.fine_amount,
                )
                .filter(
                    Violation.id > last_id,
                    Violation.latitude.isnot(None),
                    Violation.longitude.isnot(None),
                )
                .order_by(Violation.id)
                .limit(BATCH_SIZE)
                .all()
            )
            if not rows:
                break
            yield rows
            last_id = rows[-1].id

    def _aggregate_groups(
        self,
    ) -> tuple[dict[tuple[Any, ...], GroupStats], int]:
        groups: dict[tuple[Any, ...], GroupStats] = {}
        violations_read = 0

        for rows in self._violation_batches():
            for row in rows:
                if not valid_coordinates(row.latitude, row.longitude):
                    continue

                violations_read += 1
                key = hotspot_group_key(
                    row.junction_name,
                    row.latitude,
                    row.longitude,
                )
                stats = groups.setdefault(key, GroupStats())
                stats.count += 1
                stats.latitude_sum += row.latitude
                stats.longitude_sum += row.longitude

                if row.violation_date is not None:
                    stats.dates.add(row.violation_date.date())
                if row.violation_type:
                    stats.violation_types[row.violation_type.strip()] += 1

                vehicle_category = row.vehicle_category or row.vehicle_type
                if vehicle_category:
                    stats.vehicle_categories[vehicle_category.strip()] += 1
                if row.zone and row.zone.strip():
                    stats.zones[row.zone.strip()] += 1
                if (
                    row.fine_amount is not None
                    and math.isfinite(row.fine_amount)
                ):
                    stats.fine_sum += row.fine_amount
                    stats.fine_count += 1

        return groups, violations_read

    def _create_hotspots(
        self,
        groups: dict[tuple[Any, ...], GroupStats],
        pipeline_run_id: str,
        timestamp: datetime,
    ) -> dict[tuple[Any, ...], int]:
        hotspot_ids: dict[tuple[Any, ...], int] = {}
        pending: list[tuple[tuple[Any, ...], Hotspot]] = []

        for cluster_label, key in enumerate(sorted(groups, key=repr)):
            stats = groups[key]
            centroid_lat = stats.latitude_sum / stats.count
            centroid_lon = stats.longitude_sum / stats.count
            hotspot_name = (
                str(key[1])
                if key[0] == "junction"
                else f"{key[1]:.3f}, {key[2]:.3f}"
            )

            hotspot = Hotspot(
                cluster_label=cluster_label,
                hotspot_name=hotspot_name[:256],
                zone_id=_most_common(stats.zones, 64),
                centroid_lat=centroid_lat,
                centroid_lon=centroid_lon,
                centroid=WKTElement(
                    f"POINT({centroid_lon} {centroid_lat})",
                    srid=4326,
                ),
                total_violations=stats.count,
                unique_dates=len(stats.dates),
                dominant_violation_type=_most_common(
                    stats.violation_types, 128
                ),
                dominant_vehicle_category=_most_common(
                    stats.vehicle_categories, 64
                ),
                avg_fine_amount=(
                    stats.fine_sum / stats.fine_count
                    if stats.fine_count
                    else None
                ),
                violation_density=0.0,
                radius_m=0.0,
                pipeline_run_id=pipeline_run_id,
                created_at=timestamp,
                updated_at=timestamp,
            )
            pending.append((key, hotspot))

            if len(pending) >= BATCH_SIZE:
                self._commit_hotspot_batch(pending, hotspot_ids)
                pending.clear()

        if pending:
            self._commit_hotspot_batch(pending, hotspot_ids)

        return hotspot_ids

    def _commit_hotspot_batch(
        self,
        batch: list[tuple[tuple[Any, ...], Hotspot]],
        hotspot_ids: dict[tuple[Any, ...], int],
    ) -> None:
        self.db.add_all([hotspot for _, hotspot in batch])
        self.db.flush()
        for key, hotspot in batch:
            hotspot_ids[key] = hotspot.id
        self.db.commit()

    def _create_enriched_violations(
        self,
        groups: dict[tuple[Any, ...], GroupStats],
        hotspot_ids: dict[tuple[Any, ...], int],
        pipeline_run_id: str,
        processed_at: datetime,
    ) -> int:
        mappings: list[dict[str, Any]] = []
        created = 0

        cluster_labels = {
            key: cluster_label
            for cluster_label, key in enumerate(sorted(groups, key=repr))
        }

        for rows in self._violation_batches():
            for row in rows:
                if not valid_coordinates(row.latitude, row.longitude):
                    continue

                key = hotspot_group_key(
                    row.junction_name,
                    row.latitude,
                    row.longitude,
                )
                stats = groups[key]
                mappings.append(
                    {
                        "violation_id": row.id,
                        "hotspot_id": hotspot_ids[key],
                        "severity_score": severity_score(row.violation_type),
                        "is_recurrence": stats.count > 1,
                        "temporal_flag": is_rush_hour(
                            row.hour_of_day
                            if row.hour_of_day is not None
                            else (
                                row.violation_date.hour
                                if row.violation_date is not None
                                else None
                            )
                        ),
                        "cluster_label": cluster_labels[key],
                        "distance_to_core": None,
                        "pipeline_run_id": pipeline_run_id,
                        "processed_at": processed_at,
                    }
                )

            if mappings:
                self._commit_enrichment_batch(mappings)
                created += len(mappings)
                mappings.clear()

        return created

    def _commit_enrichment_batch(
        self,
        mappings: list[dict[str, Any]],
    ) -> None:
        self.db.bulk_insert_mappings(EnrichedViolation, mappings)
        self.db.commit()
