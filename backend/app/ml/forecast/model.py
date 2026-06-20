from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

import math
import pickle

try:
    import lightgbm as lgb
except Exception:
    lgb = None

from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

from app.ml.forecast.feature_builder import normalize_eis, risk_category_from_eis


@dataclass
class ForecastPrediction:
    predicted_eis: float
    predicted_risk_category: str
    confidence: float
    confidence_lower: float
    confidence_upper: float


@dataclass
class TrainingResult:
    model_version: str
    model_type: str
    train_size: int
    validation_size: int
    mae: float
    r2: float
    feature_names: List[str]


class ForecastModel:
    def __init__(
        self,
        model_version: str = "forecast-v1",
        random_state: int = 42,
        prefer_lightgbm: bool = True,
    ) -> None:
        self.model_version = model_version
        self.random_state = random_state
        self.prefer_lightgbm = prefer_lightgbm
        self.model: Any = None
        self.model_type: str = ""
        self.feature_names: List[str] = []
        self.training_metrics: Dict[str, Any] = {}
        self.is_trained: bool = False

    def fit(
        self,
        X: Sequence[Sequence[float]],
        y: Sequence[float],
        feature_names: Sequence[str],
    ) -> TrainingResult:
        if len(X) < 8:
            raise ValueError("At least 8 training rows are required for forecast training")

        self.feature_names = list(feature_names)
        X_train, X_val, y_train, y_val = train_test_split(
            list(X),
            list(y),
            test_size=0.25,
            random_state=self.random_state,
        )

        self.model = self._build_model()
        self.model.fit(X_train, y_train)

        predictions = [normalize_eis(v) for v in self.model.predict(X_val)]
        y_val_norm = [normalize_eis(v) for v in y_val]

        mae = float(mean_absolute_error(y_val_norm, predictions))
        try:
            r2 = float(r2_score(y_val_norm, predictions))
        except Exception:
            r2 = 0.0

        self.training_metrics = {
            "mae": mae,
            "r2": r2,
            "train_size": len(X_train),
            "validation_size": len(X_val),
            "model_type": self.model_type,
            "model_version": self.model_version,
        }
        self.is_trained = True

        return TrainingResult(
            model_version=self.model_version,
            model_type=self.model_type,
            train_size=len(X_train),
            validation_size=len(X_val),
            mae=mae,
            r2=r2,
            feature_names=list(self.feature_names),
        )

    def predict_one(self, features: Sequence[float]) -> ForecastPrediction:
        if not self.is_trained or self.model is None:
            raise RuntimeError("Forecast model is not trained")

        predicted = normalize_eis(float(self.model.predict([list(features)])[0]))
        category = risk_category_from_eis(predicted)

        mae = float(self.training_metrics.get("mae", 15.0))
        confidence = self._confidence_from_error(mae)
        interval = max(5.0, mae * 1.5)

        return ForecastPrediction(
            predicted_eis=predicted,
            predicted_risk_category=category,
            confidence=confidence,
            confidence_lower=max(0.0, predicted - interval),
            confidence_upper=min(100.0, predicted + interval),
        )

    def predict_many(self, X: Sequence[Sequence[float]]) -> List[ForecastPrediction]:
        return [self.predict_one(features) for features in X]

    def get_feature_importance(self) -> Dict[str, float]:
        if self.model is None or not self.feature_names:
            return {}

        raw_importances = None

        if hasattr(self.model, "feature_importances_"):
            raw_importances = list(self.model.feature_importances_)
        elif hasattr(self.model, "coef_"):
            raw_importances = [abs(float(v)) for v in self.model.coef_]

        if raw_importances is None:
            return {name: 1.0 / len(self.feature_names) for name in self.feature_names}

        total = float(sum(abs(float(v)) for v in raw_importances))
        if total <= 0:
            return {name: 0.0 for name in self.feature_names}

        return {
            name: abs(float(value)) / total
            for name, value in zip(self.feature_names, raw_importances)
        }

    def dumps(self) -> bytes:
        return pickle.dumps(
            {
                "model": self.model,
                "model_type": self.model_type,
                "model_version": self.model_version,
                "feature_names": self.feature_names,
                "training_metrics": self.training_metrics,
                "is_trained": self.is_trained,
            }
        )

    @classmethod
    def loads(cls, payload: bytes) -> "ForecastModel":
        state = pickle.loads(payload)
        obj = cls(model_version=state["model_version"])
        obj.model = state["model"]
        obj.model_type = state["model_type"]
        obj.feature_names = state["feature_names"]
        obj.training_metrics = state["training_metrics"]
        obj.is_trained = state["is_trained"]
        return obj

    def _build_model(self) -> Any:
        if self.prefer_lightgbm and lgb is not None:
            self.model_type = "lightgbm"
            return lgb.LGBMRegressor(
                n_estimators=250,
                learning_rate=0.05,
                max_depth=5,
                random_state=self.random_state,
                objective="regression",
            )

        self.model_type = "sklearn_hist_gradient_boosting"
        return HistGradientBoostingRegressor(
            max_iter=250,
            learning_rate=0.05,
            max_leaf_nodes=31,
            random_state=self.random_state,
        )

    def _confidence_from_error(self, mae: float) -> float:
        mae = max(0.0, min(100.0, float(mae)))
        return max(0.35, min(0.98, 1.0 - mae / 100.0))