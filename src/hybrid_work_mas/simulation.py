"""Simulation utilities for hybrid workplace policy experiments.

This module defines the reproducible experimental design used to
evaluate workplace policies P1-P6.

Policy parameters are obtained from policies.py. Each policy can be
evaluated across multiple stochastic replications using explicit
random seeds.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np
import pandas as pd
from scipy.stats import t

from .model import HybridWorkModel
from .policies import POLICIES, FunctionalForm, get_policy_parameters


DEFAULT_REPLICATIONS = 30
DEFAULT_BASE_SEED = 42


@dataclass(frozen=True)
class SimulationRun:
    """Configuration of one simulation replication."""

    policy: str
    office_days: int
    remote_days: int
    replication: int
    seed: int
    flexibility: float
    collaboration: float
    functional_form: str


def build_experiment_design(
    replications: int = DEFAULT_REPLICATIONS,
    base_seed: int = DEFAULT_BASE_SEED,
    functional_form: FunctionalForm | str = FunctionalForm.NONLINEAR,
    *,
    k: float = 2.0,
    gamma: float = 0.5,
) -> list[SimulationRun]:
    """Create the complete reproducible experiment design.

    Each workplace policy P1-P6 is evaluated using the same sequence
    of random seeds, enabling comparable stochastic replications
    across policies.

    Parameters
    ----------
    replications:
        Number of stochastic replications per policy.

    base_seed:
        First random seed used in the experiment.

    functional_form:
        Functional specification used to derive flexibility and
        collaboration.

    k:
        Curvature parameter for flexibility.

    gamma:
        Curvature parameter for collaboration.
    """

    if replications < 1:
        raise ValueError(
            "replications must be greater than or equal to 1."
        )

    if base_seed < 0:
        raise ValueError(
            "base_seed must be greater than or equal to 0."
        )

    experiment_design: list[SimulationRun] = []

    for policy in POLICIES:

        parameters = get_policy_parameters(
            policy.office_days,
            functional_form=functional_form,
            k=k,
            gamma=gamma,
        )

        for replication in range(1, replications + 1):

            seed = base_seed + replication - 1

            experiment_design.append(
                SimulationRun(
                    policy=policy.code,
                    office_days=policy.office_days,
                    remote_days=policy.remote_days,
                    replication=replication,
                    seed=seed,
                    flexibility=float(
                        parameters["flexibility"]
                    ),
                    collaboration=float(
                        parameters["collaboration"]
                    ),
                    functional_form=str(
                        parameters["functional_form"]
                    ),
                )
            )

    return experiment_design

def run_experiment(
    simulation_days: int = 180,
    n_employees: int = 100,
    initial_engagement: float = 0.21,
    replications: int = DEFAULT_REPLICATIONS,
    base_seed: int = DEFAULT_BASE_SEED,
    functional_form: FunctionalForm | str = FunctionalForm.NONLINEAR,
    *,
    k: float = 2.0,
    gamma: float = 0.5,
    alpha: float = 0.0015,
    beta: float = 0.0015,
    delta: float = 0.0010,
    noise_std: float = 0.002,
    return_trajectories: bool = False,
) -> pd.DataFrame:
    """
    Execute the full workplace-policy experiment.

    Each policy is simulated across multiple stochastic replications.
    The returned DataFrame contains one row per policy replication.
    """

    design = build_experiment_design(
        replications=replications,
        base_seed=base_seed,
        functional_form=functional_form,
        k=k,
        gamma=gamma,
    )

    results = []
    trajectories = []

    for run in design:

        model = HybridWorkModel(
            flexibility=run.flexibility,
            collaboration=run.collaboration,
            n_employees=n_employees,
            initial_engagement=initial_engagement,
            alpha=alpha,
            beta=beta,
            delta=delta,
            noise_std=noise_std,
            seed=run.seed,
        )

        history = model.run(
            days=simulation_days
        )

        if return_trajectories:
            for record in model.employee_history:
                trajectories.append(
                    {
                        "policy": run.policy,
                        "office_days": run.office_days,
                        "remote_days": run.remote_days,
                        "replication": run.replication,
                        "seed": run.seed,
                        "day": record["day"],
                        "employee_id": record["employee_id"],
                        "engagement": record["engagement"],
                    }
                )
        




        initial = history[0]
        final = history[-1]

        relative_improvement = (
            ((final - initial) / initial) * 100
            if initial != 0
            else 0.0
        )

        result = {
            **asdict(run),
            "simulation_days": simulation_days,
            "n_employees": n_employees,
            "initial_engagement": initial,
            "final_engagement": final,
            "relative_improvement": relative_improvement,
        }

        results.append(result)

    results_df = pd.DataFrame(results)

    if return_trajectories:
        trajectories_df = pd.DataFrame(trajectories)
        return results_df, trajectories_df

    return results_df


def summarize_experiment(
    results: pd.DataFrame,
    confidence_level: float = 0.95,
) -> pd.DataFrame:
    """
    Summarize experimental results by workplace policy.

    The summary includes mean final engagement, standard deviation,
    standard error, 95% confidence interval, relative improvement,
    number of replications, and policy ranking.
    """

    summary = (
        results
        .groupby(
            [
                "policy",
                "office_days",
                "remote_days",
                "flexibility",
                "collaboration",
            ],
            as_index=False,
        )
        .agg(
            mean_final_engagement=(
                "final_engagement",
                "mean",
            ),
            std_final_engagement=(
                "final_engagement",
                "std",
            ),
            mean_relative_improvement=(
                "relative_improvement",
                "mean",
            ),
            std_relative_improvement=(
                "relative_improvement",
                "std",
            ),
            replications=(
                "replication",
                "count",
            ),
        )
    )

    # Standard error of the mean
    summary["se_final_engagement"] = (
        summary["std_final_engagement"]
        / np.sqrt(summary["replications"])
    )

    # Degrees of freedom
    degrees_freedom = summary["replications"] - 1

    # Two-sided critical t value
    alpha = 1.0 - confidence_level

    summary["t_critical"] = degrees_freedom.apply(
        lambda df: t.ppf(
            1.0 - alpha / 2.0,
            df,
        )
    )

    # Margin of error
    summary["ci_margin"] = (
        summary["t_critical"]
        * summary["se_final_engagement"]
    )

    # Confidence interval
    summary["ci95_lower"] = (
        summary["mean_final_engagement"]
        - summary["ci_margin"]
    )

    summary["ci95_upper"] = (
        summary["mean_final_engagement"]
        + summary["ci_margin"]
    )

    # Rank policies by mean final engagement
    summary["rank"] = (
        summary["mean_final_engagement"]
        .rank(
            ascending=False,
            method="min",
        )
        .astype(int)
    )

    return (
        summary
        .sort_values("rank")
        .reset_index(drop=True)
    )


def summarize_trajectories(
    trajectories: pd.DataFrame,
    confidence_level: float = 0.95,
) -> pd.DataFrame:
    """
    Summarize organizational engagement trajectories by policy and day.

    Employee-level engagement is first averaged within each stochastic
    replication. Summary statistics and confidence intervals are then
    calculated across independent replications.
    """

    # Step 1: organizational mean engagement within each replication
    replication_daily = (
        trajectories
        .groupby(
            [
                "policy",
                "office_days",
                "remote_days",
                "replication",
                "day",
            ],
            as_index=False,
        )
        .agg(
            replication_mean_engagement=(
                "engagement",
                "mean",
            )
        )
    )

    # Step 2: summarize across independent replications
    summary = (
        replication_daily
        .groupby(
            [
                "policy",
                "office_days",
                "remote_days",
                "day",
            ],
            as_index=False,
        )
        .agg(
            mean_engagement=(
                "replication_mean_engagement",
                "mean",
            ),
            std_engagement=(
                "replication_mean_engagement",
                "std",
            ),
            replications=(
                "replication_mean_engagement",
                "count",
            ),
        )
    )

    summary["se_engagement"] = (
        summary["std_engagement"]
        / np.sqrt(summary["replications"])
    )

    degrees_freedom = summary["replications"] - 1
    alpha = 1.0 - confidence_level

    summary["t_critical"] = degrees_freedom.apply(
        lambda df: t.ppf(
            1.0 - alpha / 2.0,
            df,
        )
    )

    summary["ci_margin"] = (
        summary["t_critical"]
        * summary["se_engagement"]
    )

    summary["ci95_lower"] = (
        summary["mean_engagement"]
        - summary["ci_margin"]
    )

    summary["ci95_upper"] = (
        summary["mean_engagement"]
        + summary["ci_margin"]
    )

    return summary





def save_experiment_results(
    results: pd.DataFrame,
    summary: pd.DataFrame,
    results_path: str = "results/experiment_results.csv",
    summary_path: str = "results/experiment_summary.csv",
) -> None:
    """
    Save raw simulation results and summary statistics to CSV files.
    """

    results.to_csv(
        results_path,
        index=False,
    )

    summary.to_csv(
        summary_path,
        index=False,
    )