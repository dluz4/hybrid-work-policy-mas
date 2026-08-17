import pytest

from hybrid_work_mas.employee import EmployeeAgent


def test_employee_initial_state():
    employee = EmployeeAgent(
        employee_id=1,
        engagement=0.21,
        flexibility_sensitivity=0.8,
        collaboration_sensitivity=0.6,
    )

    assert employee.employee_id == 1
    assert employee.engagement == pytest.approx(0.21)
    assert employee.flexibility_sensitivity == pytest.approx(0.8)
    assert employee.collaboration_sensitivity == pytest.approx(0.6)


def test_engagement_update_without_noise():
    employee = EmployeeAgent(
        employee_id=1,
        engagement=0.21,
        flexibility_sensitivity=0.8,
        collaboration_sensitivity=0.6,
    )

    employee.update_engagement(
        flexibility=0.7,
        collaboration=0.8,
        alpha=0.01,
        beta=0.01,
        delta=0.005,
        noise=0.0,
    )

    expected = (
        0.21
        + (
            (0.01 * 0.7 * 0.8 * (1.0 - 0.21))
            + (0.01 * 0.8 * 0.6 * (1.0 - 0.21))
            - (0.005 * (1.0 - 0.8) * 0.6 * 0.21)
        )
    )

    assert employee.engagement == pytest.approx(expected)


def test_engagement_is_bounded_above():
    employee = EmployeeAgent(
        employee_id=1,
        engagement=0.99,
        flexibility_sensitivity=1.0,
        collaboration_sensitivity=1.0,
    )

    employee.update_engagement(
        flexibility=1.0,
        collaboration=1.0,
        alpha=0.1,
        beta=0.1,
        delta=0.0,
        noise=0.1,
    )

    assert employee.engagement == 1.0


def test_engagement_is_bounded_below():
    employee = EmployeeAgent(
        employee_id=1,
        engagement=0.01,
        flexibility_sensitivity=1.0,
        collaboration_sensitivity=1.0,
    )

    employee.update_engagement(
        flexibility=0.0,
        collaboration=0.0,
        alpha=0.0,
        beta=0.0,
        delta=0.1,
        noise=-0.1,
    )

    assert employee.engagement == 0.0