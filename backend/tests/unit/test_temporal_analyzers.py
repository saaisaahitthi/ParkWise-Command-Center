"""
tests/unit/test_temporal_analyzers.py
──────────────────────────────────────
Unit tests for the pure-function temporal ML analysers embedded in
app/services/temporal_service.py.

Covers:
  • _assign_priority  — maps pct-of-total float → priority label
  • _window_label     — maps hour integer → human-readable label
  • _enforcement_window — maps hour → ±1h enforcement bracket (clamped)

All tests are pure / in-memory — no database, no fixtures.
Run with:  pytest tests/unit/test_temporal_analyzers.py -v
"""

from __future__ import annotations

import pytest

# ---------------------------------------------------------------------------
# Import the private helpers under test.
# They are module-level functions in temporal_service, not class methods,
# so we import them directly.  If the names ever change this import will
# fail loudly, which is intentional.
# ---------------------------------------------------------------------------
from app.services.temporal_service import (
    _assign_priority,
    _enforcement_window,
    _window_label,
    _PRIORITY_CRITICAL_PCT,
    _PRIORITY_HIGH_PCT,
    _PRIORITY_MEDIUM_PCT,
)


# ═══════════════════════════════════════════════════════════════════════════
# _assign_priority
# ═══════════════════════════════════════════════════════════════════════════

class TestAssignPriority:
    """Verify priority thresholds match the frozen EIS formula constants."""

    def test_critical_exact_boundary(self):
        """Exactly at the Critical threshold → Critical."""
        assert _assign_priority(_PRIORITY_CRITICAL_PCT) == "Critical"

    def test_critical_above_boundary(self):
        assert _assign_priority(0.5) == "Critical"

    def test_critical_just_above(self):
        assert _assign_priority(_PRIORITY_CRITICAL_PCT + 0.001) == "Critical"

    def test_high_exact_boundary(self):
        """Exactly at the High threshold (below Critical) → High."""
        assert _assign_priority(_PRIORITY_HIGH_PCT) == "High"

    def test_high_just_below_critical(self):
        assert _assign_priority(_PRIORITY_CRITICAL_PCT - 0.001) == "High"

    def test_medium_exact_boundary(self):
        assert _assign_priority(_PRIORITY_MEDIUM_PCT) == "Medium"

    def test_medium_just_below_high(self):
        assert _assign_priority(_PRIORITY_HIGH_PCT - 0.001) == "Medium"

    def test_low_just_below_medium(self):
        assert _assign_priority(_PRIORITY_MEDIUM_PCT - 0.001) == "Low"

    def test_low_zero(self):
        assert _assign_priority(0.0) == "Low"

    def test_low_tiny(self):
        assert _assign_priority(0.0001) == "Low"

    def test_returns_string(self):
        result = _assign_priority(0.1)
        assert isinstance(result, str)

    def test_all_labels_are_valid(self):
        valid_labels = {"Low", "Medium", "High", "Critical"}
        for pct in [0.0, 0.01, 0.03, 0.04, 0.08, 0.09, 0.15, 0.20, 0.50, 1.0]:
            assert _assign_priority(pct) in valid_labels

    @pytest.mark.parametrize("pct,expected", [
        (0.00,  "Low"),
        (0.029, "Low"),
        (0.030, "Medium"),
        (0.079, "Medium"),
        (0.080, "High"),
        (0.149, "High"),
        (0.150, "Critical"),
        (1.000, "Critical"),
    ])
    def test_boundary_table(self, pct, expected):
        assert _assign_priority(pct) == expected


# ═══════════════════════════════════════════════════════════════════════════
# _window_label
# ═══════════════════════════════════════════════════════════════════════════

class TestWindowLabel:
    """Verify IST hour → window label mapping against TimeWindow constants."""

    # Morning Rush: 7–9 (inclusive start, exclusive end 10)
    @pytest.mark.parametrize("hour", [7, 8, 9])
    def test_morning_rush(self, hour):
        assert _window_label(hour) == "Morning Rush"

    # Lunch: 12–13
    @pytest.mark.parametrize("hour", [12, 13])
    def test_lunch(self, hour):
        assert _window_label(hour) == "Lunch Hour"

    # Evening Rush (Afternoon Rush): 16–18
    @pytest.mark.parametrize("hour", [16, 17, 18])
    def test_evening_rush(self, hour):
        assert _window_label(hour) == "Evening Rush"

    # Night: 22–23 and 0–5
    @pytest.mark.parametrize("hour", [22, 23, 0, 1, 2, 3, 4, 5])
    def test_night(self, hour):
        assert _window_label(hour) == "Night"

    # Off-peak: hours not covered by any named window
    @pytest.mark.parametrize("hour", [6, 10, 11, 14, 15, 19, 20, 21])
    def test_off_peak(self, hour):
        assert _window_label(hour) == "Off-Peak"

    def test_returns_string(self):
        assert isinstance(_window_label(9), str)

    def test_all_hours_return_string(self):
        """Every integer 0–23 must return a non-empty string."""
        for h in range(24):
            label = _window_label(h)
            assert isinstance(label, str) and len(label) > 0, (
                f"Hour {h} returned empty/non-string label: {label!r}"
            )

    def test_valid_label_set(self):
        valid = {"Morning Rush", "Lunch Hour", "Evening Rush", "Night", "Off-Peak"}
        for h in range(24):
            assert _window_label(h) in valid, f"Unexpected label for hour {h}"


# ═══════════════════════════════════════════════════════════════════════════
# _enforcement_window
# ═══════════════════════════════════════════════════════════════════════════

class TestEnforcementWindow:
    """Verify ±1h enforcement bracket with clamping to [0, 23]."""

    def test_mid_day_no_clamp(self):
        start, end = _enforcement_window(12)
        assert start == 11
        assert end == 13

    def test_midnight_lower_clamp(self):
        """Hour 0 → start clamped to 0."""
        start, end = _enforcement_window(0)
        assert start == 0
        assert end == 1

    def test_hour_1_partial_lower_clamp(self):
        start, end = _enforcement_window(1)
        assert start == 0
        assert end == 2

    def test_hour_23_upper_clamp(self):
        """Hour 23 → end clamped to 23."""
        start, end = _enforcement_window(23)
        assert start == 22
        assert end == 23

    def test_hour_22_no_upper_clamp(self):
        start, end = _enforcement_window(22)
        assert start == 21
        assert end == 23

    def test_returns_tuple_of_ints(self):
        result = _enforcement_window(10)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert all(isinstance(v, int) for v in result)

    def test_start_always_lte_end(self):
        for h in range(24):
            start, end = _enforcement_window(h)
            assert start <= end, f"start > end for hour {h}: ({start}, {end})"

    def test_start_always_gte_zero(self):
        for h in range(24):
            start, _ = _enforcement_window(h)
            assert start >= 0

    def test_end_always_lte_23(self):
        for h in range(24):
            _, end = _enforcement_window(h)
            assert end <= 23

    def test_window_width_is_at_most_two(self):
        for h in range(24):
            start, end = _enforcement_window(h)
            assert end - start <= 2, f"Window too wide for hour {h}: {end - start}"

    @pytest.mark.parametrize("hour,expected_start,expected_end", [
        (0,  0,  1),
        (1,  0,  2),
        (7,  6,  8),
        (12, 11, 13),
        (17, 16, 18),
        (22, 21, 23),
        (23, 22, 23),
    ])
    def test_parametrized_clamp_table(self, hour, expected_start, expected_end):
        start, end = _enforcement_window(hour)
        assert start == expected_start
        assert end == expected_end


# ═══════════════════════════════════════════════════════════════════════════
# Integration of the three helpers — consistency checks
# ═══════════════════════════════════════════════════════════════════════════

class TestAnalyzerConsistency:
    """Cross-analyser consistency: priority, label, and bracket agree on peaks."""

    def test_morning_rush_high_priority_produces_correct_bracket(self):
        """
        Morning rush hour 8 with a high % of violations should be Critical,
        labelled 'Morning Rush', and have bracket 7–9.
        """
        priority = _assign_priority(0.20)   # 20% → Critical
        label = _window_label(8)
        start, end = _enforcement_window(8)

        assert priority == "Critical"
        assert label == "Morning Rush"
        assert start == 7
        assert end == 9

    def test_low_volume_night_window(self):
        """
        Night hour 2 with very low % → Low priority, Night label, bracket 1–3.
        """
        priority = _assign_priority(0.01)
        label = _window_label(2)
        start, end = _enforcement_window(2)

        assert priority == "Low"
        assert label == "Night"
        assert start == 1
        assert end == 3

    def test_critical_evening_rush(self):
        priority = _assign_priority(0.18)
        label = _window_label(17)
        start, end = _enforcement_window(17)

        assert priority == "Critical"
        assert label == "Evening Rush"
        assert start == 16
        assert end == 18
