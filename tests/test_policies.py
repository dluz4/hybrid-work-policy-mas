import pytest

from hybrid_work_mas.policies import get_policy_parameters


@pytest.mark.parametrize(
    (
        "office_days",
        "expected_flexibility",
        "expected_collaboration",
    ),
    [
        (5, 0.200, 1.000),
        (4, 0.505, 0.916),
        (3, 0.709, 0.820),
        (2, 0.847, 0.706),
        (1, 0.938, 0.558),
        (0, 1.000, 0.200),
    ],
)
def test_model3_policy_values(
    office_days,
    expected_flexibility,
    expected_collaboration,
):
    """Verify the expected Model 3 parameters for policies P1-P6."""

    parameters = get_policy_parameters(office_days)

    assert parameters["flexibility"] == pytest.approx(
        expected_flexibility,
        abs=0.001,
    )

    assert parameters["collaboration"] == pytest.approx(
        expected_collaboration,
        abs=0.001,
    )


def test_parameters_are_between_zero_and_one():
    """Verify that behavioural parameters remain within valid bounds."""

    for office_days in range(6):
        parameters = get_policy_parameters(office_days)

        assert 0.0 <= parameters["flexibility"] <= 1.0
        assert 0.0 <= parameters["collaboration"] <= 1.0


def test_invalid_office_days():
    """Verify that invalid workplace policies are rejected."""

    with pytest.raises(ValueError):
        get_policy_parameters(6)