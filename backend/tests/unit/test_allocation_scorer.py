from app.ml.allocation.scorer import AllocationScorer
from app.ml.allocation.types import AllocationInput


def test_scorer_generates_candidate():
    scorer = AllocationScorer()

    item = AllocationInput(
        hotspot_id=1,
        eis_score=80,
        risk_category="Critical",
        forecasted_eis=90,
        forecasted_risk_category="Critical",
        zone_id="zone-a",
        hotspot_name="Hotspot 1",
        latitude=17.4,
        longitude=78.4,
        current_violation_count=100,
        temporal_risk_score=80,
    )

    candidate = scorer.score(item)

    assert candidate.hotspot_id == 1
    assert candidate.risk_category == "Critical"
    assert candidate.priority_score > 0
    assert candidate.combined_eis >= 80
    assert "critical_risk" in candidate.reason_codes


def test_scorer_detects_forecast_increase():
    scorer = AllocationScorer()

    item = AllocationInput(
        hotspot_id=2,
        eis_score=50,
        risk_category="High",
        forecasted_eis=80,
        forecasted_risk_category="Critical",
    )

    candidate = scorer.score(item, use_forecast=True)

    assert candidate.risk_category == "Critical"
    assert "forecast_risk_increasing" in candidate.reason_codes


def test_score_many_sorts_by_priority():
    scorer = AllocationScorer()

    items = [
        AllocationInput(hotspot_id=1, eis_score=30, risk_category="Medium"),
        AllocationInput(hotspot_id=2, eis_score=90, risk_category="Critical"),
        AllocationInput(hotspot_id=3, eis_score=60, risk_category="High"),
    ]

    candidates = scorer.score_many(items)

    assert candidates[0].hotspot_id == 2
    assert candidates[0].priority_score >= candidates[1].priority_score