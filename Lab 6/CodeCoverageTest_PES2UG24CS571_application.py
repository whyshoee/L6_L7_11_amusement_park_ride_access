"""Line-coverage tests for Lab 6 amusement park ride access.

Student: Vaishnavi Goyal
SRN: PES2UG24CS571
"""
import pytest
from amusement_park_ride_access import (
    process_ride_admissions,
    inspect_safety_restraints,
)


def patron(height=150, health_warning=False, is_child=False):
    return {
        "height_cm": height,
        "health_warning": health_warning,
        "is_child": is_child,
    }


def group(ride_type="family", patrons=None, **kwargs):
    data = {
        "is_open": True,
        "ride_type": ride_type,
        "has_fast_lane": False,
        "patrons": [] if patrons is None else patrons,
    }
    data.update(kwargs)
    return data


def test_invalid_groups_argument():
    with pytest.raises(ValueError):
        process_ride_admissions("not a list", 5.0)


def test_negative_express_fee():
    with pytest.raises(ValueError):
        process_ride_admissions([], -1.0)


def test_closed_ride_is_skipped():
    result = process_ride_admissions(
        [group(is_open=False, patrons=[patron()])], 5.0
    )
    assert result == {"total_revenue": 0.0, "status": "ZERO_ADMISSIONS"}


def test_all_ride_types_and_default_ride_type():
    groups = [
        group("roller_coaster", [patron()]),
        group("water_ride", [patron()]),
        group("family", [patron()]),
        {"is_open": True, "patrons": [patron()]},  # default family ride
    ]
    result = process_ride_admissions(groups, 5.0)
    assert result == {"total_revenue": 63.0, "status": "COMPLETED"}


def test_unknown_ride_type_is_rejected():
    result = process_ride_admissions(
        [group("unknown", [patron()])], 5.0
    )
    assert result == {"total_revenue": 0.0, "status": "ZERO_ADMISSIONS"}


def test_nonpositive_height_is_rejected():
    result = process_ride_admissions(
        [group(patrons=[patron(height=0)])], 5.0
    )
    assert result == {"total_revenue": 0.0, "status": "ZERO_ADMISSIONS"}


def test_health_warning_on_non_coaster_and_short_height():
    result = process_ride_admissions(
        [group("family", [patron(health_warning=True), patron(height=100)])],
        5.0,
    )
    assert result == {"total_revenue": 0.0, "status": "ZERO_ADMISSIONS"}


def test_health_warning_on_roller_coaster_cancels_group_total():
    result = process_ride_admissions(
        [group("roller_coaster", [patron(), patron(health_warning=True), patron()])],
        5.0,
    )
    assert result == {"total_revenue": 0.0, "status": "ZERO_ADMISSIONS"}


def test_child_discount_adult_ticket_and_fast_lane():
    result = process_ride_admissions(
        [group("family", [patron(is_child=True), patron()], has_fast_lane=True)],
        5.0,
    )
    assert result == {"total_revenue": 21.0, "status": "COMPLETED"}


def test_safety_audit_after_more_than_four_rejections():
    result = process_ride_admissions(
        [group("unknown") for _ in range(5)], 5.0
    )
    assert result == {"total_revenue": 0.0, "status": "SAFETY_AUDIT"}


def test_empty_restraint_data():
    assert inspect_safety_restraints([]) == "NO_DATA"


def test_restraints_safe_with_no_two_consecutive_zeroes():
    assert inspect_safety_restraints([[0, 1, 0, 1], [1, 1]]) == "SAFE"


def test_restraints_emergency_after_two_consecutive_zeroes():
    assert inspect_safety_restraints([[1, 0, 0, 1]]) == "EMERGENCY_LOCK"
