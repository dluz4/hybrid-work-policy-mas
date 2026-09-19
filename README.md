# Hybrid Work Policy MAS

Agent-based simulation framework for studying hybrid work policies and their effects on employee and organizational outcomes.

## Overview

This repository contains the source code developed for an academic research project investigating hybrid work policies using agent-based modeling and simulation.

The project explores different combinations of office and remote work and provides a computational framework for evaluating their effects over time.

The repository is maintained to support transparency, version control, testing, and reproducibility of the computational research.

### Environment

The experiments and interactive application were developed and tested using:

- Python 3.11.5
- pandas 3.0.3
- matplotlib 3.10.9
- Solara 1.60.3
- pytest 9.1.1

## Repository Structure

```text
hybrid-work-policy-mas/
├── src/
│   └── hybrid_work_mas/
│       ├── __init__.py
│       ├── employee.py
│       ├── model.py
│       ├── policies.py
│       └── simulation.py
├── experiments/
│   ├── run_initial_engagement_sensitivity.py
│   └── run_sensitivity.py
├── results/
│   ├── experiment_results.csv
│   ├── experiment_summary.csv
│   ├── initial_engagement_sensitivity.csv
│   └── sensitivity_analysis.csv
├── tests/
│   ├── test_employee.py
│   ├── test_model.py
│   ├── test_policies.py
│   └── test_simulation.py
├── docs/
│   └── MODEL_FORMULAS.md
├── app_solara.py
├── pyproject.toml
├── .gitignore
└── README.md
