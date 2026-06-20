from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from app.ml.forecast.feature_builder import (
    ForecastFeatureBuilder,
    normalize_eis,
    risk_category_from_eis,
    risk_category_to_numeric,
)


@dataclass
class FakeEISScore:
    hotspot_id: int
    computed_for_date: datetime
    eis_score: float
    risk_category: str = "Medium"
    frequency_score: float = 0.5
    recurrence_score: float = 0.4
    density_score: float = 0.6
    temporal_risk_score: float = 0.7
    severity_norm: float = 0.5
    exposure_score: float = 0.55
    severity_multiplier: float = 1.1


def make_scores(hotspot_id: int = 1, days: int = 10):
    base = datetime(2026, 1, 1)
    return [
        FakeEISScore(
            hotspot_id=hotspot_id,
            computed_for_date=base + timedelta(days=i),
            eis_score=30 + i,
            risk_category="High" if i >= 6 else "Medium",
        )
        for i in range(days)
    ]


def test_normalize_eis_converts_fraction_to_percent():
    assert normalize_eis(0.75) == 75.0


def test_normalize_eis_clamps_range():
    assert normalize_eis(-5) == 0.0
    assert normalize_eis(150) == 100.0


def test_risk_category_from_eis():
    assert risk_category_from_eis(10) == "Low"
    assert risk_category_from_eis(35) == "Medium"
    assert risk_category_from_eis(60) == "High"
    assert risk_category_from_eis(90) == "Critical"


def test_risk_category_to_numeric():
    assert risk_category_to_numeric("Low") == 0.0
    assert risk_category_to_numeric("Medium") == 1.0
    assert risk_category_to_numeric("High") == 2.0
    assert risk_category_to_numeric("Critical") == 3.0


def test_build_training_dataset_has_rows_and_features():
    builder = ForecastFeatureBuilder()
    scores = make_scores(days=10)

    dataset = builder.build_training_dataset(scores, horizon_days=1)

    assert len(dataset.X) > 0
    assert len(dataset.y) > 0
    assert len(dataset.X) == len(dataset.y)
    assert len(dataset.feature_names) == len(dataset.X[0])
    assert "latest_eis" in dataset.feature_names
    assert "temporal_risk_score" in dataset.feature_names


def test_build_training_dataset_respects_horizon():
    builder = ForecastFeatureBuilder()
    scores = make_scores(days=10)

    dataset = builder.build_training_dataset(scores, horizon_days=7)

    assert len(dataset.X) > 0
    assert all(meta["horizon_days"] == 7 for meta in dataset.metadata)


def test_build_prediction_inputs_returns_latest_per_hotspot():
    builder = ForecastFeatureBuilder()
    scores = make_scores(hotspot_id=1, days=8) + make_scores(hotspot_id=2, days=8)

    inputs = builder.build_prediction_inputs(scores, horizon_days=1)

    assert len(inputs) == 2
    assert {item.hotspot_id for item in inputs} == {1, 2}
    assert all(item.horizon_days == 1 for item in inputs)
    assert all(len(item.features) == len(item.feature_names) for item in inputs)


def test_prediction_input_forecast_date_is_future():
    builder = ForecastFeatureBuilder()
    scores = make_scores(days=8)

    inputs = builder.build_prediction_inputs(scores, horizon_days=7)

    latest_date = max(row.computed_for_date for row in scores)
    assert inputs[0].forecast_for_date.date() == (latest_date + timedelta(days=7)).date()