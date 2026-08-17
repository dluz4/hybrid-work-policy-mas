"""Employee agent used in the hybrid work simulation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EmployeeAgent:
    """
    Represents an individual employee in the hybrid work simulation.

    Each employee has an engagement level and heterogeneous
    sensitivities to workplace flexibility and collaboration.
    """

    employee_id: int
    engagement: float
    flexibility_sensitivity: float
    collaboration_sensitivity: float

    def update_engagement(
        self,
        flexibility: float,
        collaboration: float,
        alpha: float,
        beta: float,
        delta: float,
        noise: float,
    ) -> None:
        """
        Update employee engagement for one simulation step.

        Engagement evolves according to workplace flexibility,
        collaboration, individual sensitivities, diminishing returns,
        and stochastic variation.

        Engagement is bounded between 0 and 1.
        """

        growth_potential = 1.0 - self.engagement

        flexibility_effect = (
            alpha
            * flexibility
            * self.flexibility_sensitivity
            * growth_potential
        )

        collaboration_effect = (
            beta
            * collaboration
            * self.collaboration_sensitivity
            * growth_potential
        )

        low_collaboration_penalty = (
            delta
            * (1.0 - collaboration)
            * self.collaboration_sensitivity
            * self.engagement
        )

        engagement_change = (
            flexibility_effect
            + collaboration_effect
            - low_collaboration_penalty
            + noise
        )

        self.engagement = max(
            0.0,
            min(
                1.0,
                self.engagement + engagement_change,
            ),
        )