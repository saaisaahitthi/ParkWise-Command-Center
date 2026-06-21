from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Sequence

from app.ml.forecast.feature_builder import ForecastFeatureBuilder
from app.ml.forecast.model import ForecastModel, TrainingResult


@dataclass
class ForecastTrainingOutput:
    model: ForecastModel
    training_result: TrainingResult
    rows_used: int
    horizon_days: int


class ForecastTrainer:
    def __init__(
        self,
        feature_builder: ForecastFeatureBuilder | None = None,
        model_version: str = "forecast-v1",
    ) -> None:
        self.feature_builder = feature_builder or ForecastFeatureBuilder()
        self.model_version = model_version

    def train(
        self,
        eis_scores: Sequence[Any],
        horizon_days: int = 1,
        min_history_per_hotspot: int = 4,
    ) -> ForecastTrainingOutput:
        dataset = self.feature_builder.build_training_dataset(
            eis_scores=eis_scores,
            horizon_days=horizon_days,
            min_history_per_hotspot=min_history_per_hotspot,
        )

        if len(dataset.X) < 8:
            raise ValueError(
                f"Not enough historical EIS rows for training. Need at least 8 usable rows, got {len(dataset.X)}"
            )

        model = ForecastModel(
            model_version=(
                self.model_version
                if self.model_version.endswith(f"-h{horizon_days}")
                else f"{self.model_version}-h{horizon_days}"
            ),
        )

        result = model.fit(
            X=dataset.X,
            y=dataset.y,
            feature_names=dataset.feature_names,
        )

        return ForecastTrainingOutput(
            model=model,
            training_result=result,
            rows_used=len(dataset.X),
            horizon_days=horizon_days,
        )
