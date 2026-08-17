

from hybrid_work_mas.simulation import (
    build_experiment_design,
    run_experiment,
    summarize_trajectories,
)

def test_experiment_has_180_runs():
    runs = build_experiment_design()

    assert len(runs) == 180


def test_each_policy_has_30_replications():
    runs = build_experiment_design()

    policies = {run.policy for run in runs}

    assert policies == {"P1", "P2", "P3", "P4", "P5", "P6"}

    for policy in policies:
        policy_runs = [
            run for run in runs
            if run.policy == policy
        ]

        assert len(policy_runs) == 30


def test_replication_seeds_are_reproducible():
    runs = build_experiment_design()

    expected_seeds = list(range(42, 72))

    for policy in {"P1", "P2", "P3", "P4", "P5", "P6"}:
        policy_seeds = [
            run.seed
            for run in runs
            if run.policy == policy
        ]

        assert policy_seeds == expected_seeds


def test_first_and_last_policy_configuration():
    runs = build_experiment_design()

    first = runs[0]
    last = runs[-1]

    assert first.policy == "P1"
    assert first.office_days == 5
    assert first.remote_days == 0
    assert first.seed == 42

    assert last.policy == "P6"
    assert last.office_days == 0
    assert last.remote_days == 5
    assert last.seed == 71

def test_run_experiment_returns_trajectories():
    """Experiment should optionally return individual employee trajectories."""

    results, trajectories = run_experiment(
        replications=2,
        simulation_days=2,
        n_employees=3,
        return_trajectories=True,
    )

    assert len(results) == 12
    assert len(trajectories) == 108


def test_trajectory_columns():
    """Trajectory dataset should contain the required research variables."""

    _, trajectories = run_experiment(
        replications=1,
        simulation_days=2,
        n_employees=3,
        return_trajectories=True,
    )

    expected_columns = {
        "policy",
        "office_days",
        "remote_days",
        "replication",
        "seed",
        "day",
        "employee_id",
        "engagement",
    }

    assert expected_columns.issubset(trajectories.columns)


def test_trajectory_includes_initial_and_final_day():
    """Employee trajectories should include t=0 and the final simulation day."""

    _, trajectories = run_experiment(
        replications=1,
        simulation_days=2,
        n_employees=3,
        return_trajectories=True,
    )

    assert trajectories["day"].min() == 0
    assert trajectories["day"].max() == 2


def test_trajectory_engagement_is_bounded():
    """Individual engagement must remain within the theoretical [0, 1] range."""

    _, trajectories = run_experiment(
        replications=1,
        simulation_days=10,
        n_employees=10,
        return_trajectories=True,
    )

    assert trajectories["engagement"].between(0.0, 1.0).all()

def test_summarize_trajectories_has_expected_rows():
    """Daily summary should contain one row per policy and simulation day."""

    _, trajectories = run_experiment(
        replications=2,
        simulation_days=2,
        n_employees=3,
        return_trajectories=True,
    )

    summary = summarize_trajectories(trajectories)

    # 6 policies × 3 days (0, 1, 2)
    assert len(summary) == 18


def test_summarize_trajectories_uses_replications():
    """Statistical uncertainty should be calculated across replications."""

    _, trajectories = run_experiment(
        replications=2,
        simulation_days=2,
        n_employees=3,
        return_trajectories=True,
    )

    summary = summarize_trajectories(trajectories)

    assert (summary["replications"] == 2).all()


def test_initial_daily_engagement_is_correct():
    """All policies should start from the configured initial engagement."""

    _, trajectories = run_experiment(
        replications=2,
        simulation_days=2,
        n_employees=3,
        return_trajectories=True,
    )

    summary = summarize_trajectories(trajectories)

    initial = summary[summary["day"] == 0]

    assert (initial["mean_engagement"] == 0.21).all()