from app.ml.allocation.rules import (
    normalize_score,
    normalize_risk_category,
    risk_category_from_score,
    risk_weight,
    combine_current_and_forecast_eis,
    minimum_officers_for_risk,
    is_priority_hotspot,
    officer_need_cap,
)


def test_normalize_score_fraction_to_percent():
    assert normalize_score(0.8) == 80.0


def test_normalize_score_clamps():
    assert normalize_score(-10) == 0.0
    assert normalize_score(150) == 100.0


def test_normalize_risk_category():
    assert normalize_risk_category("critical") == "Critical"
    assert normalize_risk_category("HIGH") == "High"
    assert normalize_risk_category("medium") == "Medium"
    assert normalize_risk_category(None) == "Low"


def test_risk_category_from_score():
    assert risk_category_from_score(10) == "Low"
    assert risk_category_from_score(35) == "Medium"
    assert risk_category_from_score(60) == "High"
    assert risk_category_from_score(90) == "Critical"


def test_risk_weight():
    assert risk_weight("Low") == 1.0
    assert risk_weight("Medium") == 2.0
    assert risk_weight("High") == 3.0
    assert risk_weight("Critical") == 4.0


def test_combine_current_and_forecast():
    result = combine_current_and_forecast_eis(
        current_eis=60,
        forecasted_eis=80,
        use_forecast=True,
    )
    assert result == 68.0


def test_combine_without_forecast():
    result = combine_current_and_forecast_eis(
        current_eis=60,
        forecasted_eis=90,
        use_forecast=False,
    )
    assert result == 60.0


def test_minimum_officers_for_risk():
    assert minimum_officers_for_risk("Critical") == 2
    assert minimum_officers_for_risk("High") == 1
    assert minimum_officers_for_risk("Medium") == 0
    assert minimum_officers_for_risk("Low") == 0


def test_is_priority_hotspot():
    assert is_priority_hotspot("Critical") is True
    assert is_priority_hotspot("High") is True
    assert is_priority_hotspot("Medium") is False


def test_officer_need_cap():
    assert officer_need_cap(90, "Critical") == 6
    assert officer_need_cap(80, "Critical") == 4
    assert officer_need_cap(70, "High") == 3
    assert officer_need_cap(55, "High") == 2
    assert officer_need_cap(40, "Medium") == 1
    assert officer_need_cap(10, "Low") == 0