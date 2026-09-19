import pandas as pd

from hybrid_work_mas.simulation import run_experiment


# Sensitivity-analysis parameter grid
K_VALUES = [1.0, 2.0, 3.0]
GAMMA_VALUES = [0.3, 0.5, 0.7]


def main():

    all_results = []

    for k in K_VALUES:
        for gamma in GAMMA_VALUES:

            print(f"Running sensitivity analysis: k={k}, gamma={gamma}")

            results = run_experiment(
                simulation_days=365,
                n_employees=100,
                initial_engagement=0.50,
                replications=30,
                base_seed=42,
                k=k,
                gamma=gamma,
                alpha=0.0015,
                beta=0.0015,
                delta=0.0010,
                noise_std=0.002,
            )

            # Record sensitivity parameters
            results["k"] = k
            results["gamma"] = gamma

            all_results.append(results)

    sensitivity_results = pd.concat(
        all_results,
        ignore_index=True,
    )

    sensitivity_results.to_csv(
        "results/sensitivity_analysis.csv",
        index=False,
    )

    print("\nSensitivity analysis completed.")
    print(f"Total runs: {len(sensitivity_results)}")
    print("Results saved to results/sensitivity_analysis.csv")


if __name__ == "__main__":
    main()