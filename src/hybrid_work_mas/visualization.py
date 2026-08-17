"""Visualization utilities for hybrid work policy simulation results."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import pandas as pd


def plot_policy_engagement_trajectories(
    daily_summary: pd.DataFrame,
    output_path: str = "results/policy_engagement_trajectories.png",
    show_confidence_interval: bool = True,
) -> None:
    """
    Plot average organizational engagement over time for workplace
    policies P1-P6.

    Solid lines represent the mean organizational engagement across
    stochastic replications. Optional shaded areas represent the
    corresponding 95% confidence intervals.
    """

    required_columns = {
        "policy",
        "office_days",
        "remote_days",
        "day",
        "mean_engagement",
        "ci95_lower",
        "ci95_upper",
    }

    missing_columns = required_columns.difference(daily_summary.columns)

    if missing_columns:
        raise ValueError(
            "daily_summary is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    data = daily_summary.sort_values(
        ["policy", "day"]
    ).copy()

    fig, ax = plt.subplots(
        figsize=(10, 6)
    )

    for policy in sorted(data["policy"].unique()):

        policy_data = data[
            data["policy"] == policy
        ]

        office_days = int(
            policy_data["office_days"].iloc[0]
        )

        remote_days = int(
            policy_data["remote_days"].iloc[0]
        )

        label = (
            f"{policy} "
            f"({office_days} office / "
            f"{remote_days} remote)"
        )

        line = ax.plot(
            policy_data["day"],
            policy_data["mean_engagement"] * 100,
            linewidth=2.0,
            label=label,
        )[0]

        if show_confidence_interval:

            ax.fill_between(
                policy_data["day"],
                policy_data["ci95_lower"] * 100,
                policy_data["ci95_upper"] * 100,
                alpha=0.05,
                color=line.get_color(),
            )

    ax.set_xlabel(
        "Simulation Day"
    )

    ax.set_ylabel(
        "Average Engagement (%)"
    )

    ax.set_title(
       "Employee-Level and Mean Engagement "
        "Trajectories by Workplace Policy"
    )

    ax.set_xlim(
        data["day"].min(),
        data["day"].max(),
    )

    ax.set_ylim(
        0,
        100,
    )

    ax.grid(
        alpha=0.25
    )


    ax.set_xticks(
        [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 365]
    )

    fig.tight_layout()

    output = Path(output_path)

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)

def plot_individual_employee_trajectories(
    trajectories: pd.DataFrame,
    daily_summary: pd.DataFrame,
    output_path: str = "results/individual_employee_trajectories.png",
    replication: int = 1,
    employees_per_policy: int = 20,
    sample_seed: int = 42,
) -> None:
    """
    Plot individual employee engagement observations together with
    the mean organizational trajectory for workplace policies P1-P6.

    Individual observations are sampled from one representative
    replication to preserve readability. Solid lines represent the
    mean organizational engagement across all stochastic replications.
    """

    required_trajectory_columns = {
        "policy",
        "replication",
        "day",
        "employee_id",
        "engagement",
    }

    required_summary_columns = {
        "policy",
        "office_days",
        "remote_days",
        "day",
        "mean_engagement",
    }

    missing_trajectory_columns = (
        required_trajectory_columns.difference(trajectories.columns)
    )

    missing_summary_columns = (
        required_summary_columns.difference(daily_summary.columns)
    )

    if missing_trajectory_columns:
        raise ValueError(
            "trajectories is missing required columns: "
            f"{sorted(missing_trajectory_columns)}"
        )

    if missing_summary_columns:
        raise ValueError(
            "daily_summary is missing required columns: "
            f"{sorted(missing_summary_columns)}"
        )

    fig, ax = plt.subplots(
        figsize=(11, 6.5)
    )

    policies = sorted(
        daily_summary["policy"].unique()
    )

    for policy_index, policy in enumerate(policies):

        policy_summary = daily_summary[
            daily_summary["policy"] == policy
        ].sort_values("day")

        office_days = int(
            policy_summary["office_days"].iloc[0]
        )

        remote_days = int(
            policy_summary["remote_days"].iloc[0]
        )

        label = (
            f"{policy} "
            f"({office_days} office / "
            f"{remote_days} remote)"
        )

        # Mean organizational trajectory across all replications
        line = ax.plot(
            policy_summary["day"],
            policy_summary["mean_engagement"] * 100,
            linewidth=2.2,
            label=label,
            zorder=3,
        )[0]

        # Individual observations from one selected replication
        policy_individual = trajectories[
            (trajectories["policy"] == policy)
            & (trajectories["replication"] == replication)
        ].copy()

        employee_ids = (
            policy_individual["employee_id"]
            .drop_duplicates()
            .sample(
                n=min(
                    employees_per_policy,
                    policy_individual["employee_id"].nunique(),
                ),
                random_state=sample_seed + policy_index,
            )
            .tolist()
        )

        sample = policy_individual[
            policy_individual["employee_id"].isin(employee_ids)
        ]

        ax.scatter(
            sample["day"],
            sample["engagement"] * 100,
            s=5,
            alpha=0.06,
            color=line.get_color(),
            edgecolors="none",
            zorder=1,
        )

    ax.set_xlabel(
        "Simulation Day"
    )

    ax.set_ylabel(
        "Employee Engagement (%)"
    )

    ax.set_title(
        "Employee-Level and Mean Engagement Trajectories by Workplace Policy"
    )

    ax.set_xlim(
        daily_summary["day"].min(),
        daily_summary["day"].max(),
    )

    ax.set_ylim(
        0,
        100,
    )

    if daily_summary["day"].max() == 365:
        ax.set_xticks(
            [
                0, 30, 60, 90, 120, 150, 180,
                210, 240, 270, 300, 330, 365,
            ]
        )

    ax.grid(
        alpha=0.20
    )

    ax.legend(
        title="Workplace Policy",
        frameon=False,
        loc="upper left",
    )

    fig.tight_layout()

    # Legend 1: workplace policies
    policy_legend = ax.legend(
        title="Workplace Policy",
        frameon=False,
        loc="upper left",
    )

    # Keep the policy legend when adding the second legend
    ax.add_artist(policy_legend)

    # Legend 2: interpretation of line types
    representation_handles = [
        Line2D(
            [0],
            [0],
            linewidth=2.5,
            linestyle="-",
            label="Policy mean",
        ),
        Line2D(
            [0],
            [0],
            linewidth=1.5,
            linestyle="-",
            alpha=0.20,
            label="Sampled individual employees",
        ),
    ]

    ax.legend(
        handles=representation_handles,
        title="Representation",
        frameon=False,
        loc="lower right",
    )


    output = Path(output_path)

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)




if __name__ == "__main__":
    from .simulation import run_experiment, summarize_trajectories

    print("Running simulation...")

    results, trajectories = run_experiment(
        replications=30,
        simulation_days=365,
        n_employees=100,
        return_trajectories=True,
    )

    daily_summary = summarize_trajectories(trajectories)

    print("Simulation completed.")
    print(f"Simulation results: {len(results)}")
    print(f"Trajectory records: {len(trajectories)}")

    # Figure 1 - Organizational engagement
    plot_policy_engagement_trajectories(
        daily_summary
    )

    # Figure 2 - Individual employee engagement
    plot_individual_employee_trajectories(
        trajectories=trajectories,
        daily_summary=daily_summary,
        replication=1,
        employees_per_policy=20,
    )

    print(
        "Figures saved to:\n"
        "  results/policy_engagement_trajectories.png\n"
        "  results/individual_employee_trajectories.png"
    )
 