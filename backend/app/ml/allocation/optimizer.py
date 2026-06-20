from __future__ import annotations

from collections import Counter
from typing import List

from app.ml.allocation.rules import (
    minimum_officers_for_risk,
    officer_need_cap,
)
from app.ml.allocation.scorer import AllocationScorer
from app.ml.allocation.types import (
    AllocationCandidate,
    AllocationInput,
    AllocationPlan,
    AllocationRequest,
)


class AllocationOptimizer:
    def __init__(self, scorer: AllocationScorer | None = None) -> None:
        self.scorer = scorer or AllocationScorer()

    def optimize(
        self,
        inputs: List[AllocationInput],
        request: AllocationRequest,
    ) -> AllocationPlan:
        if request.total_officers < 0:
            raise ValueError("total_officers must be non-negative")

        if not inputs or request.total_officers == 0:
            return AllocationPlan(
                allocation_date=request.allocation_date,
                shift_name=request.shift_name,
                total_officers=request.total_officers,
                allocated_officers=0,
                unallocated_officers=request.total_officers,
                hotspots_covered=0,
                critical_hotspots_covered=0,
                high_hotspots_covered=0,
                candidates=[],
                summary={
                    "message": "No allocation generated",
                    "risk_distribution": {},
                    "zone_distribution": {},
                },
            )

        candidates = self.scorer.score_many(
            inputs,
            use_forecast=request.use_forecast,
        )

        if request.max_hotspots is not None:
            candidates = candidates[: max(1, request.max_hotspots)]

        remaining = request.total_officers

        remaining = self._apply_minimum_coverage(candidates, request, remaining)
        remaining = self._apply_proportional_distribution(candidates, remaining)
        remaining = self._apply_leftover_distribution(candidates, remaining)

        allocated = sum(candidate.recommended_officers for candidate in candidates)

        return AllocationPlan(
            allocation_date=request.allocation_date,
            shift_name=request.shift_name,
            total_officers=request.total_officers,
            allocated_officers=allocated,
            unallocated_officers=max(0, request.total_officers - allocated),
            hotspots_covered=sum(1 for c in candidates if c.recommended_officers > 0),
            critical_hotspots_covered=sum(
                1 for c in candidates if c.risk_category == "Critical" and c.recommended_officers > 0
            ),
            high_hotspots_covered=sum(
                1 for c in candidates if c.risk_category == "High" and c.recommended_officers > 0
            ),
            candidates=candidates,
            summary=self._summary(candidates, request.total_officers),
        )

    def _apply_minimum_coverage(
        self,
        candidates: List[AllocationCandidate],
        request: AllocationRequest,
        remaining: int,
    ) -> int:
        for candidate in candidates:
            if remaining <= 0:
                break

            minimum = minimum_officers_for_risk(
                candidate.risk_category,
                min_officers_per_critical=request.min_officers_per_critical,
                min_officers_per_high=request.min_officers_per_high,
            )

            if minimum <= 0:
                continue

            assigned = min(minimum, remaining)
            candidate.recommended_officers += assigned
            remaining -= assigned

            if assigned > 0 and "minimum_risk_coverage" not in candidate.reason_codes:
                candidate.reason_codes.append("minimum_risk_coverage")

        return remaining

    def _apply_proportional_distribution(
        self,
        candidates: List[AllocationCandidate],
        remaining: int,
    ) -> int:
        if remaining <= 0:
            return 0

        eligible = [
            candidate
            for candidate in candidates
            if officer_need_cap(candidate.combined_eis, candidate.risk_category) > candidate.recommended_officers
        ]

        if not eligible:
            return remaining

        total_priority = sum(candidate.priority_score for candidate in eligible)

        if total_priority <= 0:
            return remaining

        for candidate in eligible:
            if remaining <= 0:
                break

            cap = officer_need_cap(candidate.combined_eis, candidate.risk_category)
            room = max(0, cap - candidate.recommended_officers)
            if room <= 0:
                continue

            share = candidate.priority_score / total_priority
            assigned = int(share * remaining)

            if assigned <= 0 and candidate.risk_category in {"High", "Critical"}:
                assigned = 1

            assigned = min(assigned, room, remaining)

            candidate.recommended_officers += assigned
            remaining -= assigned

            if assigned > 0 and "proportional_risk_allocation" not in candidate.reason_codes:
                candidate.reason_codes.append("proportional_risk_allocation")

        return remaining

    def _apply_leftover_distribution(
        self,
        candidates: List[AllocationCandidate],
        remaining: int,
    ) -> int:
        if remaining <= 0:
            return 0

        candidates = sorted(candidates, key=lambda row: row.priority_score, reverse=True)

        while remaining > 0:
            assigned_any = False

            for candidate in candidates:
                if remaining <= 0:
                    break

                cap = officer_need_cap(candidate.combined_eis, candidate.risk_category)
                if candidate.recommended_officers >= cap:
                    continue

                candidate.recommended_officers += 1
                remaining -= 1
                assigned_any = True

                if "leftover_priority_allocation" not in candidate.reason_codes:
                    candidate.reason_codes.append("leftover_priority_allocation")

            if not assigned_any:
                break

        return remaining

    def _summary(
        self,
        candidates: List[AllocationCandidate],
        total_officers: int,
    ) -> dict:
        risk_distribution = Counter(candidate.risk_category for candidate in candidates)
        zone_distribution = Counter(candidate.zone_id or "Unknown" for candidate in candidates)
        allocated_by_risk = Counter()

        for candidate in candidates:
            allocated_by_risk[candidate.risk_category] += candidate.recommended_officers

        return {
            "total_candidates": len(candidates),
            "total_officers": total_officers,
            "risk_distribution": dict(risk_distribution),
            "zone_distribution": dict(zone_distribution),
            "allocated_by_risk": dict(allocated_by_risk),
            "average_priority_score": (
                round(sum(c.priority_score for c in candidates) / len(candidates), 4)
                if candidates
                else 0.0
            ),
        }