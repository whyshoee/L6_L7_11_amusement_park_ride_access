"""Branch-coverage tests for Lab 6 amusement park ride access.

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


@pytest.mark.parametrize("groups,fee", [
    ("invalid", 2.0),
    ([], -0.01),
])
def test_each_invalid_input_branch(groups, fee):
    with pytest.raises(ValueError):
        process_ride_admissions(groups, fee)


def test_open_and_closed_group_branches():
    result = process_ride_admissions(
        [
            group("family", [patron()]),
            group("roller_coaster", [patron()], is_open=False),
        ],
        0,
    )
    assert result == {"total_revenue": 10.0, "status": "COMPLETED"}


def test_every_ride_type_branch_and_unknown_type():
    result = process_ride_admissions(
        [
            group("roller_coaster", [patron()]),
            group("water_ride", [patron()]),
            group("family", [patron()]),
            group("invalid_ride", [patron()]),
        ],
        0,
    )
    assert result == {"total_revenue": 53.0, "status": "COMPLETED"}


def test_default_ride_type_and_missing_patron_list():
    result = process_ride_admissions([{"is_open": True}], 0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_ADMISSIONS"}


def test_missing_height_defaults_to_zero():
    result = process_ride_admissions(
        [group(patrons=[{"health_warning": False, "is_child": False}])], 0
    )
    assert result == {"total_revenue": 0.0, "status": "ZERO_ADMISSIONS"}


def test_nonpositive_and_below_minimum_height_branches():
    result = process_ride_admissions(
        [group(patrons=[patron(0), patron(119)])], 0
    )
    assert result == {"total_revenue": 0.0, "status": "ZERO_ADMISSIONS"}


def test_height_boundary_120_is_admitted():
    result = process_ride_admissions(
        [group(patrons=[patron(120)])], 0
    )
    assert result == {"total_revenue": 10.0, "status": "COMPLETED"}


def test_health_warning_branch_for_family_ride():
    result = process_ride_admissions(
        [group(patrons=[patron(health_warning=True), patron()])], 0
    )
    assert result == {"total_revenue": 10.0, "status": "COMPLETED"}


def test_health_warning_breaks_roller_coaster_group():
    result = process_ride_admissions(
        [group("roller_coaster", [patron(), patron(health_warning=True), patron()])],
        0,
    )
    assert result == {"total_revenue": 0.0, "status": "ZERO_ADMISSIONS"}


def test_missing_health_warning_and_is_child_defaults():
    result = process_ride_admissions(
        [group(patrons=[{"height_cm": 150}])], 0
    )
    assert result == {"total_revenue": 10.0, "status": "COMPLETED"}


def test_child_and_adult_pricing_branches():
    result = process_ride_admissions(
        [group(patrons=[patron(is_child=True), patron(is_child=False)])], 0
    )
    assert result == {"total_revenue": 16.0, "status": "COMPLETED"}


def test_fast_lane_true_and_false_branches():
    result = process_ride_admissions(
        [
            group(patrons=[patron()], has_fast_lane=True),
            group(patrons=[patron()], has_fast_lane=False),
        ],
        5.0,
    )
    assert result == {"total_revenue": 25.0, "status": "COMPLETED"}


def test_safety_audit_threshold_above_four():
    result = process_ride_admissions(
        [group("not_a_ride") for _ in range(5)], 0
    )
    assert result["status"] == "SAFETY_AUDIT"


def test_four_rejections_do_not_trigger_safety_audit():
    result = process_ride_admissions(
        [group("not_a_ride") for _ in range(4)],
        0,
    )
    assert result == {"total_revenue": 0.0, "status": "ZERO_ADMISSIONS"}


def test_zero_revenue_and_completed_status_branches():
    zero = process_ride_admissions([group()], 0)
    positive = process_ride_admissions(
        [group(patrons=[patron()])], 0
    )
    assert zero["status"] == "ZERO_ADMISSIONS"
    assert positive["status"] == "COMPLETED"


def test_empty_and_nonempty_restraint_streams():
    assert inspect_safety_restraints([]) == "NO_DATA"
    assert inspect_safety_restraints([[1, 1], [1]]) == "SAFE"


def test_unlatched_streak_resets_after_latched_reading():
    assert inspect_safety_restraints([[0, 1, 0]]) == "SAFE"


def test_emergency_lock_on_two_consecutive_unlatched_readings():
    assert inspect_safety_restraints([[0, 0, 1]]) == "EMERGENCY_LOCK"


def test_emergency_lock_found_in_later_sensor_stream():
    assert inspect_safety_restraints([[0, 1], [1, 0, 0]]) == "EMERGENCY_LOCK"
