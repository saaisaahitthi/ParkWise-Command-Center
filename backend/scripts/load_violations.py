"""Load parking violations from a CSV file into the violations table."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from geoalchemy2.elements import WKTElement

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db.session import SessionLocal  # noqa: E402
from app.models.violation import Violation  # noqa: E402


BATCH_SIZE = 1000
NULL_VALUES = {"", "null", "none", "nan", "nat"}
FIELD_ALIASES = {
    "violation_id": ("violation_id", "id", "challan_id"),
    "violation_type": ("violation_type", "offence", "violation"),
    "violation_code": ("violation_code", "offence_code", "code"),
    "vehicle_category": ("vehicle_category", "vehicle_type"),
    "vehicle_type": ("vehicle_type", "vehicle_category"),
    "violation_date": (
        "violation_date",
        "date",
        "datetime",
        "timestamp",
        "created_datetime",
    ),
    "latitude": ("latitude", "lat"),
    "longitude": ("longitude", "lon", "lng"),
    "junction_name": ("junction_name", "junction", "location_name"),
    "ward": ("ward",),
    "zone": ("zone",),
    "fine_amount": ("fine_amount", "fine", "amount"),
}


def normalize_column_name(name: str) -> str:
    return name.strip().lstrip("\ufeff").lower().replace(" ", "_").replace("-", "_")


def build_column_map(fieldnames: Iterable[str]) -> dict[str, str]:
    available = {normalize_column_name(name): name for name in fieldnames}
    column_map: dict[str, str] = {}
    for field, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            if alias in available:
                column_map[field] = available[alias]
                break
    return column_map


def clean_str(value, max_len=None):
    """Normalize nullable, structured, and length-limited string values."""
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None

    if isinstance(value, dict):
        cleaned = json.dumps(value, ensure_ascii=False, sort_keys=True)
    elif isinstance(value, (list, tuple, set)):
        parts = [clean_str(item) for item in value]
        cleaned = ", ".join(part for part in parts if part is not None)
    else:
        cleaned = str(value).strip()
        if cleaned.lower() in NULL_VALUES:
            return None

        if (
            len(cleaned) >= 2
            and cleaned[0] in "[{"
            and cleaned[-1] in "]}"
        ):
            try:
                parsed = json.loads(cleaned)
            except (TypeError, ValueError, json.JSONDecodeError):
                pass
            else:
                return clean_str(parsed, max_len=max_len)

    cleaned = cleaned.strip()
    if not cleaned:
        return None
    return cleaned[:max_len] if max_len is not None else cleaned


def get_value(
    row: dict[str, str | None], column_map: dict[str, str], field: str
) -> str | None:
    column = column_map.get(field)
    return clean_str(row.get(column)) if column else None


def parse_datetime(value: str) -> datetime:
    normalized = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        parsed = None
        for date_format in (
            "%Y-%m-%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y/%m/%d",
        ):
            try:
                parsed = datetime.strptime(normalized, date_format)
                break
            except ValueError:
                continue
        if parsed is None:
            raise ValueError(f"Unsupported date value: {value!r}")

    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


def parse_float(value: str | None) -> float | None:
    return float(value.replace(",", "")) if value is not None else None


def row_to_violation(
    row: dict[str, str | None], column_map: dict[str, str]
) -> Violation | None:
    violation_type = clean_str(
        get_value(row, column_map, "violation_type"), max_len=128
    )
    violation_date_raw = get_value(row, column_map, "violation_date")
    if not violation_type or not violation_date_raw:
        return None

    try:
        violation_date = parse_datetime(violation_date_raw)
        latitude = parse_float(get_value(row, column_map, "latitude"))
        longitude = parse_float(get_value(row, column_map, "longitude"))
        fine_amount = parse_float(get_value(row, column_map, "fine_amount"))
    except (TypeError, ValueError):
        return None

    location = None
    if latitude is not None and longitude is not None:
        location = WKTElement(f"POINT({longitude} {latitude})", srid=4326)

    return Violation(
        violation_id=clean_str(
            get_value(row, column_map, "violation_id"), max_len=64
        ),
        violation_type=violation_type,
        violation_code=clean_str(
            get_value(row, column_map, "violation_code"), max_len=32
        ),
        vehicle_category=clean_str(
            get_value(row, column_map, "vehicle_category"), max_len=64
        ),
        vehicle_type=clean_str(
            get_value(row, column_map, "vehicle_type"), max_len=64
        ),
        violation_date=violation_date,
        hour_of_day=violation_date.hour,
        day_of_week=violation_date.weekday(),
        week_number=violation_date.isocalendar().week,
        month=violation_date.month,
        latitude=latitude,
        longitude=longitude,
        location=location,
        junction_name=clean_str(
            get_value(row, column_map, "junction_name"), max_len=256
        ),
        ward=clean_str(get_value(row, column_map, "ward"), max_len=128),
        zone=clean_str(get_value(row, column_map, "zone"), max_len=128),
        fine_amount=fine_amount,
        data_source=clean_str("police_csv", max_len=64),
    )


def commit_batch(db, batch: list[tuple[int, Violation]]) -> tuple[int, int]:
    """Commit a batch, falling back to individual rows if the batch fails."""
    violations = [violation for _, violation in batch]
    try:
        db.add_all(violations)
        db.commit()
        return len(violations), 0
    except Exception as exc:
        db.rollback()
        reason = " ".join(str(exc).splitlines())
        print(f"Batch commit failed; retrying row-by-row. Reason: {reason}")

    inserted = 0
    skipped = 0
    for csv_row_number, violation in batch:
        try:
            violation.id = None
            db.add(violation)
            db.commit()
            inserted += 1
        except Exception as exc:
            db.rollback()
            skipped += 1
            reason = " ".join(str(exc).splitlines())
            print(f"Skipped CSV row {csv_row_number}. Reason: {reason}")

    return inserted, skipped


def load_csv(csv_path: Path) -> tuple[int, int, int]:
    total_rows = 0
    inserted = 0
    skipped = 0
    pending: list[tuple[int, Violation]] = []
    db = SessionLocal()

    try:
        with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            if not reader.fieldnames:
                raise ValueError("CSV file has no header row")

            column_map = build_column_map(reader.fieldnames)
            missing = {
                field
                for field in ("violation_type", "violation_date")
                if field not in column_map
            }
            if missing:
                raise ValueError(
                    "CSV is missing required column(s): " + ", ".join(sorted(missing))
                )

            for row in reader:
                total_rows += 1
                violation = row_to_violation(row, column_map)
                if violation is None:
                    skipped += 1
                    continue

                pending.append((reader.line_num, violation))
                if len(pending) == BATCH_SIZE:
                    batch_inserted, batch_skipped = commit_batch(db, pending)
                    inserted += batch_inserted
                    skipped += batch_skipped
                    pending.clear()

            if pending:
                batch_inserted, batch_skipped = commit_batch(db, pending)
                inserted += batch_inserted
                skipped += batch_skipped
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    return total_rows, inserted, skipped


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load a CSV file into the ParkWise violations table."
    )
    parser.add_argument("csv_path", type=Path, help="Path to the violations CSV file")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    csv_path = args.csv_path.expanduser().resolve()
    if not csv_path.is_file():
        raise SystemExit(f"CSV file not found: {csv_path}")

    total_rows, inserted, skipped = load_csv(csv_path)
    print(f"Total rows read: {total_rows}")
    print(f"Inserted count: {inserted}")
    print(f"Skipped count: {skipped}")


if __name__ == "__main__":
    main()
