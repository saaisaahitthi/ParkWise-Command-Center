"""Unit tests for hotspot grouping and enrichment rules."""

from app.services.hotspot_service import (
    hotspot_group_key,
    is_rush_hour,
    severity_score,
    valid_coordinates,
)


def test_junction_grouping_takes_precedence() -> None:
    assert hotspot_group_key("MG Road", 12.97161, 77.59461) == (
        "junction",
        "MG Road",
    )


def test_no_junction_groups_by_rounded_coordinates() -> None:
    assert hotspot_group_key("No Junction", 12.97161, 77.59461) == (
        "coordinates",
        12.972,
        77.595,
    )
    assert hotspot_group_key("", 12.97161, 77.59461) == (
        "coordinates",
        12.972,
        77.595,
    )


def test_severity_rules() -> None:
    assert severity_score("DOUBLE PARKING") == 1.0
    assert severity_score("PARKING IN A MAIN ROAD") == 0.9
    assert severity_score("PARKING ON FOOTPATH") == 0.8
    assert severity_score("NO PARKING") == 0.6
    assert severity_score("WRONG PARKING") == 0.4
    assert severity_score("OTHER") == 0.5


def test_rush_hour_boundaries() -> None:
    for hour in (7, 8, 9, 10, 17, 18, 19, 20, 21):
        assert is_rush_hour(hour)
    for hour in (0, 6, 11, 16, 22, 23, None):
        assert not is_rush_hour(hour)


def test_coordinate_validation() -> None:
    assert valid_coordinates(12.9, 77.6)
    assert not valid_coordinates(None, 77.6)
    assert not valid_coordinates(91.0, 77.6)
