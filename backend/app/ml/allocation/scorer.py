from __future__ import annotations

from typing import List

from app.ml.allocation.rules import (
    combine_current_and_forecast_eis,
    normalize_risk_category,
    normalize_score,
    risk_category_from_score,
    risk_weight,
)
from app.ml.allocation.types import AllocationCandidate, AllocationInput


class AllocationScorer:
    def score(
        self,
        item: AllocationInput,
        use_forecast: bool = True,
    ) -> AllocationCandidate:
        current_eis = normalize_score(item.eis_score)
        forecasted_eis = normalize_score(item.forecasted_eis) if item.forecasted_eis is not None else None

        combined_eis = combine_current_and_forecast_eis(
            current_eis=current_eis,
            forecasted_eis=forecasted_eis,
            use_forecast=use_forecast,
        )

        current_category = normalize_risk_category(item.risk_category)
        forecast_category = normalize_risk_category(item.forecasted_risk_category)

        effective_category = self._strongest_category(
            current_category,
            forecast_category if use_forecast and item.forecasted_risk_category else None,
            risk_category_from_score(combined_eis),
        )

        priority_score = self._priority_score(
            current_eis=current_eis,
            forecasted_eis=forecasted_eis,
            combined_eis=combined_eis,
            risk_category=effective_category,
            temporal_risk_score=item.temporal_risk_score,
            violation_count=item.current_violation_count,
        )

        reason_codes = self._reason_codes(
            current_eis=current_eis,
            forecasted_eis=forecasted_eis,
            risk_category=effective_category,
            temporal_risk_score=item.temporal_risk_score,
            violation_count=item.current_violation_count,
        )

        return AllocationCandidate(
            hotspot_id=item.hotspot_id,
            priority_score=priority_score,
            combined_eis=combined_eis,
            risk_category=effective_category,
            forecasted_eis=forecasted_eis,
            forecasted_risk_category=item.forecasted_risk_category,
            zone_id=item.zone_id,
            hotspot_name=item.hotspot_name,
            latitude=item.latitude,
            longitude=item.longitude,
            reason_codes=reason_codes,
        )

    def score_many(
        self,
        items: List[AllocationInput],
        use_forecast: bool = True,
    ) -> List[AllocationCandidate]:
        candidates = [self.score(item, use_forecast=use_forecast) for item in items]
        candidates.sort(key=lambda row: row.priority_score, reverse=True)
        return candidates

    def _priority_score(
        self,
        current_eis: float,
        forecasted_eis: float | None,
        combined_eis: float,
        risk_category: str,
        temporal_risk_score: float | None,
        violation_count: int | None,
    ) -> float:
        score = combined_eis * 0.65
        score += risk_weight(risk_category) * 7.5

        if forecasted_eis is not None and forecasted_eis > current_eis:
            score += min(15.0, (forecasted_eis - current_eis) * 0.5)

        if temporal_risk_score is not None:
            score += normalize_score(temporal_risk_score) * 0.10

        if violation_count is not None:
            score += min(10.0, float(violation_count) / 10.0)

        return round(max(0.0, min(100.0, score)), 4)

    def _strongest_category(self, *categories: str | None) -> str:
        order = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}
        normalized = [normalize_risk_category(category) for category in categories if category]
        if not normalized:
            return "Low"
        return max(normalized, key=lambda category: order[category])

    def _reason_codes(
        self,
        current_eis: float,
        forecasted_eis: float | None,
        risk_category: str,
        temporal_risk_score: float | None,
        violation_count: int | None,
    ) -> List[str]:
        reasons: List[str] = []

        if risk_category == "Critical":
            reasons.append("critical_risk")
        elif risk_category == "High":
            reasons.append("high_risk")

        if forecasted_eis is not None and forecasted_eis > current_eis:
            reasons.append("forecast_risk_increasing")

        if temporal_risk_score is not None and normalize_score(temporal_risk_score) >= 70:
            reasons.append("high_temporal_risk")

        if violation_count is not None and violation_count >= 50:
            reasons.append("high_violation_volume")

        if not reasons:
            reasons.append("baseline_coverage")

        return reasons