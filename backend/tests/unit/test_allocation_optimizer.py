from datetime import date

from app.ml.allocation.optimizer import AllocationOptimizer
from app.ml.allocation.types import AllocationInput, AllocationRequest


def test_optimizer_allocates_officers():
    optimizer = AllocationOptimizer()

    inputs = [
        AllocationInput(hotspot_id=1, eis_score=90, risk_category="Critical"),
        AllocationInput(hotspot_id=2, eis_score=70, risk_category="High"),
        AllocationInput(hotspot_id=3, eis_score=40, risk_category="Medium"),
    ]

    request = AllocationRequest(
        total_officers=10,
        allocation_date=date(2026, 1, 1),
        shift_name="morning",
    )

    plan = optimizer.optimize(inputs, request)

    assert plan.total_officers == 10
    assert plan.allocated_officers <= 10
    assert plan.hotspots_covered > 0
    assert plan.critical_hotspots_covered == 1


def test_optimizer_gives_critical_minimum_coverage():
    optimizer = AllocationOptimizer()

    inputs = [
        AllocationInput(hotspot_id=1, eis_score=90, risk_category="Critical"),
        AllocationInput(hotspot_id=2, eis_score=85, risk_category="Critical"),
    ]

    request = AllocationRequest(
        total_officers=4,
        allocation_date=date(2026, 1, 1),
        min_officers_per_critical=2,
    )

    plan = optimizer.optimize(inputs, request)

    critical_candidates = [c for c in plan.candidates if c.risk_category == "Critical"]

    assert len(critical_candidates) == 2
    assert all(c.recommended_officers >= 2 for c in critical_candidates)


def test_optimizer_handles_zero_officers():
    optimizer = AllocationOptimizer()

    inputs = [
        AllocationInput(hotspot_id=1, eis_score=90, risk_category="Critical"),
    ]

    request = AllocationRequest(
        total_officers=0,
        allocation_date=date(2026, 1, 1),
    )

    plan = optimizer.optimize(inputs, request)

    assert plan.allocated_officers == 0
    assert plan.unallocated_officers == 0
    assert plan.hotspots_covered == 0


def test_optimizer_respects_max_hotspots():
    optimizer = AllocationOptimizer()

    inputs = [
        AllocationInput(hotspot_id=i, eis_score=90 - i, risk_category="High")
        for i in range(1, 10)
    ]

    request = AllocationRequest(
        total_officers=10,
        allocation_date=date(2026, 1, 1),
        max_hotspots=3,
    )

    plan = optimizer.optimize(inputs, request)

    assert len(plan.candidates) == 3