from __future__ import annotations

import math
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error
from sqlalchemy.orm import Session

from app.ml.forecast import (
    ForecastModel,
    ForecastPredictor,
    ForecastTrainer,
)
from app.ml.forecast.feature_builder import normalize_eis, risk_category_from_eis
from app.ml.forecast.model import ForecastPrediction, TrainingResult
from app.models.hotspot import Hotspot
from app.repositories.forecast_repository import ForecastRepository


_MODEL_REGISTRY: Dict[int, Any] = {}


class CrossSectionalForecastModel:
    """Adapter that keeps the existing predictor compatible with demo training."""

    feature_names = [
        "hotspot_id",
        "frequency_score",
        "recurrence_score",
        "density_score",
        "temporal_risk_score",
        "severity_norm",
        "exposure_score",
        "severity_multiplier",
        "total_violations",
    ]

    def __init__(
        self,
        model_version: str,
        total_violations: Dict[int, float],
    ) -> None:
        self.model_version = model_version
        self.total_violations = total_violations
        self._delegate = ForecastModel(model_version=model_version)
        self.model: Any = None
        self.model_type = ""
        self.training_metrics: Dict[str, Any] = {}
        self.is_trained = False

    def fit(
        self,
        X: Sequence[Sequence[float]],
        y: Sequence[float],
    ) -> TrainingResult:
        if len(X) >= 8:
            result = self._delegate.fit(
                X=X,
                y=y,
                feature_names=self.feature_names,
            )
            self._sync_delegate()
            return result

        self.model = DummyRegressor(strategy="mean")
        self.model.fit(list(X), list(y))
        predictions = self.model.predict(list(X))
        mae = float(mean_absolute_error(list(y), predictions))
        self.model_type = "sklearn_dummy_regressor"
        self.training_metrics = {
            "mae": mae,
            "r2": None,
            "train_size": len(X),
            "validation_size": 0,
            "model_type": self.model_type,
            "model_version": self.model_version,
        }
        self.is_trained = True
        return TrainingResult(
            model_version=self.model_version,
            model_type=self.model_type,
            train_size=len(X),
            validation_size=0,
            mae=mae,
            r2=None,
            feature_names=list(self.feature_names),
        )

    def predict_one(self, features: Sequence[float]) -> ForecastPrediction:
        cross_sectional = self._prediction_features(features)
        if self._delegate.is_trained:
            return self._delegate.predict_one(cross_sectional)

        predicted = normalize_eis(float(self.model.predict([cross_sectional])[0]))
        mae = float(self.training_metrics.get("mae") or 0.0)
        interval = max(5.0, mae * 1.5)
        return ForecastPrediction(
            predicted_eis=predicted,
            predicted_risk_category=risk_category_from_eis(predicted),
            confidence=max(0.35, min(0.98, 1.0 - mae / 100.0)),
            confidence_lower=max(0.0, predicted - interval),
            confidence_upper=min(100.0, predicted + interval),
        )

    def get_feature_importance(self) -> Dict[str, float]:
        if self._delegate.is_trained:
            return self._delegate.get_feature_importance()
        return {name: 0.0 for name in self.feature_names}

    def _prediction_features(self, features: Sequence[float]) -> List[float]:
        hotspot_id = int(features[0])
        return [
            float(hotspot_id),
            float(features[6]),
            float(features[7]),
            float(features[8]),
            float(features[9]),
            float(features[10]),
            float(features[11]),
            float(features[12]),
            float(self.total_violations.get(hotspot_id, 0.0)),
        ]

    def _sync_delegate(self) -> None:
        self.model = self._delegate.model
        self.model_type = self._delegate.model_type
        self.training_metrics = self._delegate.training_metrics
        self.is_trained = self._delegate.is_trained


class ForecastService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = ForecastRepository(db)

    def train_model(
        self,
        horizon_days: int = 1,
        hotspot_id: Optional[int] = None,
        model_version: str = "forecast-v1",
        min_history_per_hotspot: int = 4,
    ) -> Dict[str, Any]:
        eis_scores = self.repository.get_historical_eis_scores(hotspot_id=hotspot_id)

        if not eis_scores:
            raise ValueError("No EIS rows are available for forecast training.")

        histories: Dict[int, int] = {}
        for row in eis_scores:
            histories[row.hotspot_id] = histories.get(row.hotspot_id, 0) + 1

        demo_mode = (
            min_history_per_hotspot == 1
            and max(histories.values(), default=0) == 1
        )

        if demo_mode:
            model, result, rows_used = self._train_cross_sectional(
                eis_scores=eis_scores,
                model_version=f"{model_version}-h{horizon_days}",
            )
            training_mode = "cross_sectional"
        else:
            trainer = ForecastTrainer(model_version=model_version)
            output = trainer.train(
                eis_scores=eis_scores,
                horizon_days=horizon_days,
                min_history_per_hotspot=min_history_per_hotspot,
            )
            model = output.model
            result = output.training_result
            rows_used = output.rows_used
            training_mode = "historical"

        _MODEL_REGISTRY[horizon_days] = model

        return {
            "status": "trained",
            "horizon_days": horizon_days,
            "model_version": model.model_version,
            "model_type": result.model_type,
            "training_mode": training_mode,
            "rows_used": rows_used,
            "train_size": result.train_size,
            "validation_size": result.validation_size,
            "mae": self._json_metric(result.mae),
            "r2": self._json_metric(result.r2),
            "feature_names": result.feature_names,
        }

    def _train_cross_sectional(
        self,
        eis_scores: Sequence[Any],
        model_version: str,
    ) -> tuple[CrossSectionalForecastModel, TrainingResult, int]:
        hotspot_ids = [int(row.hotspot_id) for row in eis_scores]
        hotspot_rows = (
            self.db.query(Hotspot.id, Hotspot.total_violations)
            .filter(Hotspot.id.in_(hotspot_ids))
            .all()
        )
        total_violations = {
            int(row.id): float(row.total_violations or 0)
            for row in hotspot_rows
        }

        model = CrossSectionalForecastModel(
            model_version=model_version,
            total_violations=total_violations,
        )
        X = [
            [
                float(row.hotspot_id),
                self._score(row, "frequency_score"),
                self._score(row, "recurrence_score"),
                self._score(row, "density_score"),
                self._score(row, "temporal_risk_score"),
                self._score(row, "severity_norm"),
                self._score(row, "exposure_score"),
                float(row.severity_multiplier or 0.0),
                total_violations.get(int(row.hotspot_id), 0.0),
            ]
            for row in eis_scores
        ]
        y = [normalize_eis(row.eis_score) for row in eis_scores]
        result = model.fit(X, y)
        return model, result, len(X)

    @staticmethod
    def _score(row: Any, field: str) -> float:
        value = float(getattr(row, field, 0.0) or 0.0)
        if value <= 1.5:
            value *= 100.0
        return max(0.0, min(100.0, value))

    @staticmethod
    def _json_metric(value: Any) -> Optional[float]:
        if value is None:
            return None
        number = float(value)
        return number if math.isfinite(number) else None

    def generate_forecasts(
        self,
        horizon_days: int = 1,
        hotspot_id: Optional[int] = None,
        replace_existing: bool = True,
        pipeline_run_id: Optional[str] = None,
        commit: bool = True,
    ) -> Dict[str, Any]:
        model = _MODEL_REGISTRY.get(horizon_days)

        if model is None:
            raise RuntimeError(
                f"Forecast model for horizon_days={horizon_days} is not trained. "
                "Call POST /forecast/train first."
            )

        eis_scores = self.repository.get_historical_eis_scores(hotspot_id=hotspot_id)

        predictor = ForecastPredictor(model=model)
        outputs = predictor.predict(
            eis_scores=eis_scores,
            horizon_days=horizon_days,
        )

        if replace_existing:
            self.repository.delete_existing_forecasts(
                horizon_days=horizon_days,
                model_version=model.model_version,
            )

        rows: List[Dict[str, Any]] = []
        for item in outputs:
            rows.append(
                {
                    "hotspot_id": item.hotspot_id,
                    "forecast_date": item.forecast_for_date,
                    "horizon_days": item.horizon_days,
                    "predicted_eis": item.predicted_eis,
                    "predicted_risk_category": item.predicted_risk_category,
                    "confidence_lower": item.confidence_lower,
                    "confidence_upper": item.confidence_upper,
                    "shap_values": item.shap_values,
                    "top_features": item.top_features,
                    "model_version": item.model_version,
                    "pipeline_run_id": pipeline_run_id,
                }
            )

        created = self.repository.bulk_create_forecasts(rows, commit=False)

        if commit:
            self.db.commit()

        return {
            "status": "generated",
            "horizon_days": horizon_days,
            "model_version": model.model_version,
            "forecasts_created": len(created),
            "replace_existing": replace_existing,
            "pipeline_run_id": pipeline_run_id,
        }

    def list_forecasts(
        self,
        hotspot_id: Optional[int] = None,
        horizon_days: Optional[int] = None,
        risk_category: Optional[str] = None,
        model_version: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        rows = self.repository.list_forecasts(
            hotspot_id=hotspot_id,
            horizon_days=horizon_days,
            risk_category=risk_category,
            model_version=model_version,
            limit=limit,
            offset=offset,
        )
        return [self._serialize_forecast(row) for row in rows]

    def get_top_forecasts(
        self,
        limit: int = 20,
        horizon_days: Optional[int] = None,
        critical_only: bool = False,
    ) -> List[Dict[str, Any]]:
        risk_categories = ["Critical"] if critical_only else ["High", "Critical"]

        rows = self.repository.get_top_forecasts(
            limit=limit,
            horizon_days=horizon_days,
            risk_categories=risk_categories,
        )

        return [self._serialize_forecast(row) for row in rows]

    def get_hotspot_forecasts(
        self,
        hotspot_id: int,
        horizon_days: Optional[int] = None,
        limit: int = 30,
    ) -> List[Dict[str, Any]]:
        rows = self.repository.get_hotspot_forecasts(
            hotspot_id=hotspot_id,
            horizon_days=horizon_days,
            limit=limit,
        )
        return [self._serialize_forecast(row) for row in rows]

    def get_summary(self) -> Dict[str, Any]:
        summary = self.repository.get_summary()
        trained_horizons = sorted(_MODEL_REGISTRY.keys())

        summary["trained_horizons"] = trained_horizons
        summary["models_in_memory"] = len(trained_horizons)

        return summary

    def _serialize_forecast(self, row: Any) -> Dict[str, Any]:
        confidence = self._confidence_from_bounds(
            row.confidence_lower,
            row.confidence_upper,
            row.predicted_eis,
        )

        return {
            "forecast_id": row.id,
            "hotspot_id": row.hotspot_id,
            "forecast_date": row.forecast_date,
            "horizon_days": row.horizon_days,
            "predicted_eis": row.predicted_eis,
            "predicted_risk_category": row.predicted_risk_category,
            "confidence": confidence,
            "confidence_lower": row.confidence_lower,
            "confidence_upper": row.confidence_upper,
            "top_features": row.top_features,
            "shap_values": row.shap_values,
            "model_version": row.model_version,
            "pipeline_run_id": row.pipeline_run_id,
            "created_at": row.created_at,
        }

    def _confidence_from_bounds(
        self,
        lower: Optional[float],
        upper: Optional[float],
        predicted: Optional[float],
    ) -> float:
        if lower is None or upper is None:
            return 0.5

        width = max(0.0, float(upper) - float(lower))
        confidence = 1.0 - min(1.0, width / 100.0)
        return max(0.0, min(1.0, confidence))
