from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from statistics import mean, pstdev
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import math


RISK_CATEGORIES = ("Low", "Medium", "High", "Critical")


@dataclass(frozen=True)
class ForecastDataset:
    X: List[List[float]]
    y: List[float]
    feature_names: List[str]
    metadata: List[Dict[str, Any]]


@dataclass(frozen=True)
class ForecastInput:
    hotspot_id: int
    forecast_for_date: datetime
    horizon_days: int
    features: List[float]
    feature_names: List[str]
    latest_eis: float
    latest_risk_category: str


def normalize_eis(value: Optional[float]) -> float:
    if value is None or math.isnan(float(value)):
        return 0.0
    value = float(value)
    if value <= 1.5:
        value *= 100.0
    return max(0.0, min(100.0, value))


def risk_category_from_eis(score: float) -> str:
    score = normalize_eis(score)
    if score < 25:
        return "Low"
    if score < 50:
        return "Medium"
    if score < 75:
        return "High"
    return "Critical"


def risk_category_to_numeric(category: Optional[str]) -> float:
    if not category:
        return 0.0
    category = category.strip().lower()
    mapping = {
        "low": 0.0,
        "medium": 1.0,
        "high": 2.0,
        "critical": 3.0,
    }
    return mapping.get(category, 0.0)


class ForecastFeatureBuilder:
    feature_names = [
        "hotspot_id",
        "day_of_week",
        "day_of_month",
        "month",
        "is_weekend",
        "latest_eis",
        "frequency_score",
        "recurrence_score",
        "density_score",
        "temporal_risk_score",
        "severity_norm",
        "exposure_score",
        "severity_multiplier",
        "risk_category_numeric",
        "rolling_mean_3",
        "rolling_mean_7",
        "rolling_std_7",
        "trend_3",
        "trend_7",
        "days_since_last_score",
        "horizon_days",
    ]

    def build_training_dataset(
        self,
        eis_scores: Sequence[Any],
        horizon_days: int = 1,
        min_history_per_hotspot: int = 4,
    ) -> ForecastDataset:
        grouped = self._group_scores(eis_scores)

        X: List[List[float]] = []
        y: List[float] = []
        metadata: List[Dict[str, Any]] = []

        for hotspot_id, rows in grouped.items():
            if len(rows) < min_history_per_hotspot:
                continue

            for idx in range(len(rows)):
                target_idx = self._find_target_index(rows, idx, horizon_days)
                if target_idx is None:
                    continue

                features = self._build_features_from_history(
                    hotspot_id=hotspot_id,
                    rows=rows,
                    idx=idx,
                    forecast_for_date=self._get_date(rows[idx]) + timedelta(days=horizon_days),
                    horizon_days=horizon_days,
                )

                X.append(features)
                y.append(normalize_eis(self._get_eis(rows[target_idx])))
                metadata.append(
                    {
                        "hotspot_id": hotspot_id,
                        "source_date": self._get_date(rows[idx]),
                        "target_date": self._get_date(rows[target_idx]),
                        "horizon_days": horizon_days,
                    }
                )

        return ForecastDataset(
            X=X,
            y=y,
            feature_names=list(self.feature_names),
            metadata=metadata,
        )

    def build_prediction_inputs(
        self,
        eis_scores: Sequence[Any],
        horizon_days: int = 1,
    ) -> List[ForecastInput]:
        grouped = self._group_scores(eis_scores)
        inputs: List[ForecastInput] = []

        for hotspot_id, rows in grouped.items():
            if not rows:
                continue

            idx = len(rows) - 1
            latest_date = self._get_date(rows[idx])
            forecast_for_date = latest_date + timedelta(days=horizon_days)

            features = self._build_features_from_history(
                hotspot_id=hotspot_id,
                rows=rows,
                idx=idx,
                forecast_for_date=forecast_for_date,
                horizon_days=horizon_days,
            )

            inputs.append(
                ForecastInput(
                    hotspot_id=hotspot_id,
                    forecast_for_date=forecast_for_date,
                    horizon_days=horizon_days,
                    features=features,
                    feature_names=list(self.feature_names),
                    latest_eis=normalize_eis(self._get_eis(rows[idx])),
                    latest_risk_category=getattr(rows[idx], "risk_category", "Low") or "Low",
                )
            )

        return inputs

    def _group_scores(self, eis_scores: Sequence[Any]) -> Dict[int, List[Any]]:
        grouped: Dict[int, List[Any]] = {}

        for row in eis_scores:
            hotspot_id = getattr(row, "hotspot_id", None)
            score_date = self._get_date(row)
            if hotspot_id is None or score_date is None:
                continue
            grouped.setdefault(int(hotspot_id), []).append(row)

        for hotspot_id in grouped:
            grouped[hotspot_id].sort(key=self._get_date)

        return grouped

    def _find_target_index(self, rows: Sequence[Any], idx: int, horizon_days: int) -> Optional[int]:
        source_date = self._get_date(rows[idx])
        target_date = source_date + timedelta(days=horizon_days)

        for j in range(idx + 1, len(rows)):
            if self._get_date(rows[j]).date() >= target_date.date():
                return j

        return None

    def _build_features_from_history(
        self,
        hotspot_id: int,
        rows: Sequence[Any],
        idx: int,
        forecast_for_date: datetime,
        horizon_days: int,
    ) -> List[float]:
        current = rows[idx]
        history = rows[max(0, idx - 6) : idx + 1]
        eis_values = [normalize_eis(self._get_eis(row)) for row in history]

        latest_eis = normalize_eis(self._get_eis(current))
        rolling_mean_3 = self._safe_mean(eis_values[-3:])
        rolling_mean_7 = self._safe_mean(eis_values[-7:])
        rolling_std_7 = self._safe_std(eis_values[-7:])
        trend_3 = self._trend(eis_values[-3:])
        trend_7 = self._trend(eis_values[-7:])

        current_date = self._get_date(current)
        previous_date = self._get_date(rows[idx - 1]) if idx > 0 else current_date
        days_since_last_score = max(0, (current_date.date() - previous_date.date()).days)

        return [
            float(hotspot_id),
            float(forecast_for_date.weekday()),
            float(forecast_for_date.day),
            float(forecast_for_date.month),
            1.0 if forecast_for_date.weekday() >= 5 else 0.0,
            latest_eis,
            self._score(current, "frequency_score"),
            self._score(current, "recurrence_score"),
            self._score(current, "density_score"),
            self._score(current, "temporal_risk_score"),
            self._score(current, "severity_norm"),
            self._score(current, "exposure_score"),
            self._score(current, "severity_multiplier"),
            risk_category_to_numeric(getattr(current, "risk_category", None)),
            rolling_mean_3,
            rolling_mean_7,
            rolling_std_7,
            trend_3,
            trend_7,
            float(days_since_last_score),
            float(horizon_days),
        ]

    def _score(self, row: Any, field: str) -> float:
        value = getattr(row, field, 0.0)
        if value is None:
            return 0.0
        value = float(value)
        if field.endswith("_score") or field in {"severity_norm", "exposure_score"}:
            if value <= 1.5:
                value *= 100.0
        return max(0.0, min(100.0, value))

    def _get_date(self, row: Any) -> datetime:
        value = getattr(row, "computed_for_date", None)
        if value is None:
            value = getattr(row, "computation_date", None)
        if value is None:
            value = getattr(row, "created_at", None)
        if value is None:
            raise ValueError("EIS score row is missing computed_for_date/computation_date/created_at")
        return value

    def _get_eis(self, row: Any) -> float:
        value = getattr(row, "eis_score", None)
        if value is None:
            value = getattr(row, "eis_final", None)
        return normalize_eis(value)

    def _safe_mean(self, values: Sequence[float]) -> float:
        return float(mean(values)) if values else 0.0

    def _safe_std(self, values: Sequence[float]) -> float:
        return float(pstdev(values)) if len(values) > 1 else 0.0

    def _trend(self, values: Sequence[float]) -> float:
        if len(values) < 2:
            return 0.0
        return float(values[-1] - values[0])