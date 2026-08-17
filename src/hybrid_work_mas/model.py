from __future__ import annotations

import random
from statistics import mean

from hybrid_work_mas.employee import EmployeeAgent


class HybridWorkModel:
    """
    Simulates employee engagement under a workplace policy.

    One model instance represents one experimental replication.
    """

    def __init__(
        self,
        flexibility: float,
        collaboration: float,
        n_employees: int = 100,
        initial_engagement: float = 0.21,
        alpha: float = 0.0015,
        beta: float = 0.0015,
        delta: float = 0.0010,
        noise_std: float = 0.002,
        seed: int = 42,
    ):
        self.flexibility = flexibility
        self.collaboration = collaboration

        self.n_employees = n_employees
        self.initial_engagement = initial_engagement

        self.alpha = alpha
        self.beta = beta
        self.delta = delta
        self.noise_std = noise_std

        self.seed = seed
        self.random = random.Random(seed)

        self.day = 0

        self.employees = self._create_population()

        self.engagement_history =         [
            self.average_engagement()
        ]
        self.employee_history = []

        self._record_employee_history()


        

    def _create_population(self) -> list[EmployeeAgent]:
        """
        Create a heterogeneous employee population.

        Individual sensitivities vary around the population while
        remaining bounded between 0 and 1.
        """

        employees = []

        for employee_id in range(self.n_employees):

            flexibility_sensitivity = self.random.uniform(
                0.5,
                1.0,
            )

            collaboration_sensitivity = self.random.uniform(
                0.5,
                1.0,
            )

            employee = EmployeeAgent(
                employee_id=employee_id,
                engagement=self.initial_engagement,
                flexibility_sensitivity=flexibility_sensitivity,
                collaboration_sensitivity=collaboration_sensitivity,
            )

            employees.append(employee)

        return employees

    def average_engagement(self) -> float:
        """
        Calculate organizational average engagement.
        """

        return mean(
            employee.engagement
            for employee in self.employees
        )

    def step(self) -> float:
        """
        Advance the model by one simulation day.
        """

        for employee in self.employees:

            noise = self.random.gauss(
                0.0,
                self.noise_std,
            )

            employee.update_engagement(
                flexibility=self.flexibility,
                collaboration=self.collaboration,
                alpha=self.alpha,
                beta=self.beta,
                delta=self.delta,
                noise=noise,
            )

        self.day += 1

        average = self.average_engagement()

        self.engagement_history.append(average)

        self._record_employee_history()

        return average


    def _record_employee_history(self) -> None:
        """
        Record individual employee engagement for the current simulation day.
        """

        for employee in self.employees:
            self.employee_history.append(
                {
                    "day": self.day,
                    "employee_id": employee.employee_id,
                    "engagement": employee.engagement,
                }
            )


    def run(self, days: int = 180) -> list[float]:
        """
        Run the simulation for the specified number of days.
        """

        for _ in range(days):
            self.step()

        return self.engagement_history

     