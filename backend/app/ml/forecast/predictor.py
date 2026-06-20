from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Sequence

from app.ml.forecast.explainer import ForecastExplainer
from app.ml.forecast.feature_builder import ForecastFeatureBuilder, ForecastInput
from app.ml.forecast.model import ForecastModel


@dataclass
class ForecastOutput:
    hotspot_id: int
    forecast_for_date: Any
    horizon_days: int
    predicted_eis: float
    predicted_risk_category: str
    confidence: float
    confidence_lower: float
    confidence_upper: float
    top_features: Dict[str, Any]
    shap_values: Dict[str, Any]
    model_version: str


class ForecastPredictor:
    def __init__(
        self,
        model: ForecastModel,
        feature_builder: ForecastFeatureBuilder | None = None,
        explainer: ForecastExplainer | None = None,
    ) -> None:
        self.model = model
        self.feature_builder = feature_builder or ForecastFeatureBuilder()
        self.explainer = explainer or ForecastExplainer()

    def predict(
        self,
        eis_scores: Sequence[Any],
        horizon_days: int = 1,
    ) -> List[ForecastOutput]:
        if not self.model.is_trained:
            raise RuntimeError("Forecast model is not trained")

        inputs = self.feature_builder.build_prediction_inputs(
            eis_scores=eis_scores,
            horizon_days=horizon_days,
        )

        outputs: List[ForecastOutput] = []

        for item in inputs:
            prediction = self.model.predict_one(item.features)
            explanation = self.explainer.explain(
                model=self.model,
                features=item.features,
                feature_names=item.feature_names,
            )

            outputs.append(
                ForecastOutput(
                    hotspot_id=item.hotspot_id,
                    forecast_for_date=item.forecast_for_date,
                    horizon_days=item.horizon_days,
                    predicted_eis=prediction.predicted_eis,
                    predicted_risk_category=prediction.predicted_risk_category,
                    confidence=prediction.confidence,
                    confidence_lower=prediction.confidence_lower,
                    confidence_upper=prediction.confidence_upper,
                    top_features={
                        "method": explanation.get("method"),
                        "factors": explanation.get("top_factors", []),
                    },
                    shap_values=explanation.get("raw_values", {}),
                    model_version=self.model.model_version,
                )
            )

        return outputs