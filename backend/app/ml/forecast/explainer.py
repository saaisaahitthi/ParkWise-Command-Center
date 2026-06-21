from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

try:
    import shap
except Exception:
    shap = None


class ForecastExplainer:
    def __init__(self) -> None:
        self._shap_explainer: Any = None
        self._shap_model_id: Optional[int] = None

    def explain(
        self,
        model: Any,
        features: Sequence[float],
        feature_names: Sequence[str],
        top_n: int = 5,
    ) -> Dict[str, Any]:
        if shap is not None:
            try:
                return self._explain_with_shap(model, features, feature_names, top_n)
            except Exception:
                pass

        return self._explain_with_importance(model, features, feature_names, top_n)

    def explain_many(
        self,
        model: Any,
        feature_rows: Sequence[Sequence[float]],
        feature_names: Sequence[str],
        top_n: int = 5,
    ) -> List[Dict[str, Any]]:
        return [
            self.explain(model, row, feature_names, top_n=top_n)
            for row in feature_rows
        ]

    def _explain_with_shap(
        self,
        model: Any,
        features: Sequence[float],
        feature_names: Sequence[str],
        top_n: int,
    ) -> Dict[str, Any]:
        model_id = id(model.model)
        if self._shap_explainer is None or self._shap_model_id != model_id:
            self._shap_explainer = shap.Explainer(model.model)
            self._shap_model_id = model_id
        values = self._shap_explainer([list(features)])
        shap_values = values.values[0]

        factors = []
        for name, value, feature_value in zip(feature_names, shap_values, features):
            factors.append(
                {
                    "feature": str(name),
                    "contribution": float(value),
                    "abs_contribution": abs(float(value)),
                    "feature_value": float(feature_value),
                }
            )

        factors.sort(key=lambda item: item["abs_contribution"], reverse=True)

        return {
            "method": "shap",
            "top_factors": factors[:top_n],
            "raw_values": {
                str(name): float(value)
                for name, value in zip(feature_names, shap_values)
            },
        }

    def _explain_with_importance(
        self,
        model: Any,
        features: Sequence[float],
        feature_names: Sequence[str],
        top_n: int,
    ) -> Dict[str, Any]:
        importance = model.get_feature_importance()

        factors = []
        for name, feature_value in zip(feature_names, features):
            score = float(importance.get(name, 0.0))
            factors.append(
                {
                    "feature": str(name),
                    "contribution": score,
                    "abs_contribution": abs(score),
                    "feature_value": float(feature_value),
                }
            )

        factors.sort(key=lambda item: item["abs_contribution"], reverse=True)

        return {
            "method": "feature_importance",
            "top_factors": factors[:top_n],
            "raw_values": {
                str(name): float(importance.get(name, 0.0))
                for name in feature_names
            },
        }
