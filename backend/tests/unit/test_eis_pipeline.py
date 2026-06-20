"""Unit tests for EIS normalization and scoring rules."""

import pytest

from app.services.eis_service import calculate_eis, max_scale, risk_category


def test_max_scale_normalizes_to_100() -> None:
    assert max_scale({1: 10, 2: 20, 3: 0}) == {
        1: 50.0,
        2: 100.0,
        3: 0.0,
    }


def test_max_scale_handles_all_zero_values() -> None:
    assert max_scale({1: 0, 2: 0}) == {1: 0.0, 2: 0.0}


def test_eis_formula() -> None:
    exposure, multiplier, score = calculate_eis(
        frequency_score=100,
        recurrence_score=50,
        density_score=25,
        temporal_risk_score=80,
        severity_norm=0.5,
    )
    assert exposure == pytest.approx(70.0)
    assert multiplier == pytest.approx(1.0)
    assert score == pytest.approx(70.0)


def test_eis_is_capped_at_100() -> None:
    _, _, score = calculate_eis(100, 100, 100, 100, 1.0)
    assert score == 100.0


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (0, "Low"),
        (24.999, "Low"),
        (25, "Medium"),
        (49.999, "Medium"),
        (50, "High"),
        (74.999, "High"),
        (75, "Critical"),
        (100, "Critical"),
    ],
)
def test_risk_category_boundaries(score: float, expected: str) -> None:
    assert risk_category(score) == expected
