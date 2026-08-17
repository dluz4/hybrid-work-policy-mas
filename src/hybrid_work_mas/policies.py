"""Workplace policy definitions for the Hybrid Work MAS.

This module defines the six workplace policies P1-P6 and derives
flexibility and collaboration opportunity from the remote-work ratio.

Main behavioural specification (Model 3):

    F(r) = 0.20 + 0.80 * (1 - exp(-k*r)) / (1 - exp(-k))

    C(r) = 0.20 + 0.80 * (1-r)**gamma

where:

    r = remote_days / 5
    k = 2.0
    gamma = 0.5

The policy itself determines only the office/remote configuration.
Behavioural parameters are derived from the functional specification.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import exp


WORKDAYS_PER_WEEK = 5

DEFAULT_K = 2.0
DEFAULT_GAMMA = 0.5


class FunctionalForm(str, Enum):
    """Functional forms available for robustness analysis."""

    LINEAR = "linear"
    DIMINISHING = "diminishing"
    NONLINEAR = "nonlinear"


@dataclass(frozen=True)
class Policy:
    """Representation of a five-day workplace policy."""

    code: str
    office_days: int
    remote_days: int
    label: str

    @property
    def remote_ratio(self) -> float:
        """Return the proportion of remote workdays."""

        return self.remote_days / WORKDAYS_PER_WEEK


POLICIES: tuple[Policy, ...] = (
    Policy("P1", 5, 0, "Fully office-based"),
    Policy("P2", 4, 1, "Office-dominant hybrid"),
    Policy("P3", 3, 2, "Balanced hybrid"),
    Policy("P4", 2, 3, "Remote-dominant hybrid"),
    Policy("P5", 1, 4, "Highly remote"),
    Policy("P6", 0, 5, "Fully remote"),
)


POLICY_BY_OFFICE_DAYS = {
    policy.office_days: policy
    for policy in POLICIES
}


def _validate_remote_ratio(remote_ratio: float) -> None:
    """Validate that the remote-work ratio is between 0 and 1."""

    if not 0.0 <= remote_ratio <= 1.0:
        raise ValueError(
            "remote_ratio must be between 0 and 1."
        )


def flexibility_linear(remote_ratio: float) -> float:
    """Return flexibility under the linear specification."""

    _validate_remote_ratio(remote_ratio)

    return 0.20 + 0.80 * remote_ratio


def flexibility_diminishing(
    remote_ratio: float,
    k: float = DEFAULT_K,
) -> float:
    """Return flexibility with diminishing marginal returns."""

    _validate_remote_ratio(remote_ratio)

    if k <= 0:
        raise ValueError("k must be greater than zero.")

    numerator = 1.0 - exp(-k * remote_ratio)
    denominator = 1.0 - exp(-k)

    return 0.20 + 0.80 * numerator / denominator


def collaboration_linear(
    remote_ratio: float,
) -> float:
    """Return collaboration opportunity under a linear specification."""

    _validate_remote_ratio(remote_ratio)

    return 1.00 - 0.80 * remote_ratio


def collaboration_nonlinear(
    remote_ratio: float,
    gamma: float = DEFAULT_GAMMA,
) -> float:
    """Return nonlinear collaboration opportunity."""

    _validate_remote_ratio(remote_ratio)

    if gamma <= 0:
        raise ValueError(
            "gamma must be greater than zero."
        )

    return (
        0.20
        + 0.80
        * (1.0 - remote_ratio) ** gamma
    )


def get_policy_parameters(
    office_days: int,
    functional_form: FunctionalForm | str = FunctionalForm.NONLINEAR,
    *,
    k: float = DEFAULT_K,
    gamma: float = DEFAULT_GAMMA,
) -> dict[str, float | int | str]:
    """Return policy and behavioural parameters.

    Parameters
    ----------
    office_days:
        Number of office workdays, from 0 to 5.

    functional_form:
        Behavioural functional specification.

    k:
        Curvature parameter for flexibility.

    gamma:
        Curvature parameter for collaboration opportunity.
    """

    if office_days not in POLICY_BY_OFFICE_DAYS:
        raise ValueError(
            "office_days must be an integer from 0 to 5."
        )

    policy = POLICY_BY_OFFICE_DAYS[office_days]

    remote_ratio = policy.remote_ratio

    form = FunctionalForm(functional_form)

    if form is FunctionalForm.LINEAR:

        flexibility = flexibility_linear(
            remote_ratio
        )

        collaboration = collaboration_linear(
            remote_ratio
        )

    elif form is FunctionalForm.DIMINISHING:

        flexibility = flexibility_diminishing(
            remote_ratio,
            k=k,
        )

        collaboration = collaboration_linear(
            remote_ratio
        )

    else:

        flexibility = flexibility_diminishing(
            remote_ratio,
            k=k,
        )

        collaboration = collaboration_nonlinear(
            remote_ratio,
            gamma=gamma,
        )

    return {
        "policy": policy.code,
        "office_days": policy.office_days,
        "remote_days": policy.remote_days,
        "remote_ratio": remote_ratio,
        "flexibility": float(flexibility),
        "collaboration": float(collaboration),
        "functional_form": form.value,
        "k": float(k),
        "gamma": float(gamma),
    }