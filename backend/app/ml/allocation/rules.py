from __future__ import annotations

from typing import Optional


RISK_PRIORITY = {
    "low": 1.0,
    "medium": 2.0,
    "high": 3.0,
    "critical": 4.0,
}


def normalize_score(value: Optional[float]) -> float:
    if value is None:
        return 0.0

    value = float(value)

    if value <= 1.5:
        value *= 100.0

    return max(0.0, min(100.0, value))


def normalize_risk_category(category: Optional[str]) -> str:
    if not category:
        return "Low"

    value = category.strip().lower()

    if value == "critical":
        return "Critical"
    if value == "high":
        return "High"
    if value == "medium":
        return "Medium"

    return "Low"


def risk_category_from_score(score: float) -> str:
    score = normalize_score(score)

    if score >= 75:
        return "Critical"
    if score >= 50:
        return "High"
    if score >= 25:
        return "Medium"

    return "Low"


def risk_weight(category: Optional[str]) -> float:
    return RISK_PRIORITY.get(normalize_risk_category(category).lower(), 1.0)


def combine_current_and_forecast_eis(
    current_eis: float,
    forecasted_eis: Optional[float],
    use_forecast: bool = True,
    current_weight: float = 0.6,
    forecast_weight: float = 0.4,
) -> float:
    current = normalize_score(current_eis)

    if not use_forecast or forecasted_eis is None:
        return current

    forecast = normalize_score(forecasted_eis)

    total_weight = current_weight + forecast_weight
    if total_weight <= 0:
        return current

    return ((current * current_weight) + (forecast * forecast_weight)) / total_weight


def minimum_officers_for_risk(
    risk_category: str,
    min_officers_per_critical: int = 2,
    min_officers_per_high: int = 1,
) -> int:
    category = normalize_risk_category(risk_category)

    if category == "Critical":
        return max(1, int(min_officers_per_critical))

    if category == "High":
        return max(0, int(min_officers_per_high))

    return 0


def is_priority_hotspot(risk_category: str) -> bool:
    return normalize_risk_category(risk_category) in {"High", "Critical"}


def officer_need_cap(combined_eis: float, risk_category: str) -> int:
    combined_eis = normalize_score(combined_eis)
    category = normalize_risk_category(risk_category)

    if category == "Critical":
        return 6 if combined_eis >= 90 else 4

    if category == "High":
        return 3 if combined_eis >= 65 else 2

    if category == "Medium":
        return 1

    return 0