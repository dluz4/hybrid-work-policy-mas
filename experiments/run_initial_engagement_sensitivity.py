import pandas as pd

from hybrid_work_mas.simulation import run_experiment


INITIAL_ENGAGEMENT_VALUES = [0.30, 0.50, 0.70]


def main():
    all_results = []

    for initial_engagement in INITIAL_ENGAGEMENT_VALUES:
        print(
            "Running initial-engagement sensitivity: "
            f"E(0)={initial_engagement}"
        )

        results = run_experiment(
            simulation_days=365,
            n_employees=100,
            initial_engagement=initial_engagement,
            replications=30,
            base_seed=42,
            k=2.0,
            gamma=0.5,
            alpha=0.0015,
            beta=0.0015,
            delta=0.0010,
            noise_std=0.002,
        )

        results["initial_engagement_assumption"] = initial_engagement
        all_results.append(results)

    sensitivity_results = pd.concat(
        all_results,
        ignore_index=True,
    )

    sensitivity_results.to_csv(
        "results/initial_engagement_sensitivity.csv",
        index=False,
    )

    print("\nInitial-engagement sensitivity completed.")
    print(f"Total runs: {len(sensitivity_results)}")
    print(
        "Results saved to "
        "results/initial_engagement_sensitivity.csv"
    )


if __name__ == "__main__":
    main()
    