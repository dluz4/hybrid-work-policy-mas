import solara
from matplotlib.figure import Figure

from hybrid_work_mas.model import HybridWorkModel
from hybrid_work_mas.policies import get_policy_parameters


# ============================================================
# REACTIVE STATE
# ============================================================

simulation_days = solara.reactive(365)
n_employees = solara.reactive(100)
office_days = solara.reactive(3)
seed = solara.reactive(42)

history = solara.reactive([])
final_engagement = solara.reactive(None)


simulation_status = solara.reactive("Ready")

# ============================================================
# SIMULATION
# ============================================================

def run_simulation():
    """
    Run the hybrid work simulation using the parameters
    selected in the interface.
    """

    params = get_policy_parameters(
        office_days.value
    )

    model = HybridWorkModel(
        flexibility=params["flexibility"],
        collaboration=params["collaboration"],
        n_employees=n_employees.value,
        seed=seed.value,
    )

    result = model.run(
        simulation_days.value
    )

    history.set(result)
    final_engagement.set(result[-1])

    simulation_status.set("Simulation completed")


def reset_simulation():
    """
    Reset the interactive simulation to the default configuration.
    """

    simulation_days.set(365)
    n_employees.set(100)
    office_days.set(3)
    seed.set(42)

    history.set([])
    final_engagement.set(None)

    simulation_status.set("Ready")

# ============================================================
# ENGAGEMENT CHART
# ============================================================

@solara.component
def EngagementChart():

    if not history.value:
        solara.Info(
            "Run the simulation to display the engagement trajectory."
        )
        return

    fig = Figure(
        figsize=(10, 5)
    )

    ax = fig.subplots()

    days = range(
        len(history.value)
    )

    engagement = [
        value * 100
        for value in history.value
    ]

    ax.plot(
        days,
        engagement,
        linewidth=2.3,
        label="Average engagement",
    )

    # --------------------------------------------------------
    # Initial and final engagement
    # --------------------------------------------------------

    initial_day = 0
    initial_value = engagement[0]

    final_day = len(engagement) - 1
    final_value = engagement[-1]

    # Initial point
    ax.scatter(
        initial_day,
        initial_value,
        s=70,
        zorder=5,
    )

    # Final point
    ax.scatter(
        final_day,
        final_value,
        s=70,
        zorder=5,
    )

    # Initial engagement label
    ax.annotate(
        f"Initial: {initial_value:.2f}%",
        xy=(initial_day, initial_value),
        xytext=(15, 15),
        textcoords="offset points",
        fontsize=10,
        fontweight="bold",
        arrowprops={
            "arrowstyle": "->",
            "alpha": 0.7,
        },
    )

    # Final engagement label
    ax.annotate(
        f"Final: {final_value:.2f}%",
        xy=(final_day, final_value),
        xytext=(-100, 20),
        textcoords="offset points",
        fontsize=10,
        fontweight="bold",
        arrowprops={
            "arrowstyle": "->",
            "alpha": 0.7,
        },
    )

    # --------------------------------------------------------
    # Chart formatting
    # --------------------------------------------------------

    ax.set_xlabel(
        "Simulation Day"
    )

    ax.set_ylabel(
        "Average Engagement (%)"
    )

    ax.set_title(
        "Engagement Evolution Over Time"
    )

    ax.set_xlim(
        0,
        simulation_days.value
    )

    ax.set_ylim(
        0,
        100
    )

    if simulation_days.value == 365:
        ax.set_xticks(
            [
                0,
                30,
                60,
                90,
                120,
                150,
                180,
                210,
                240,
                270,
                300,
                330,
                365,
            ]
        )

    ax.grid(
        alpha=0.25
    )

    ax.legend(
        frameon=False
    )

    fig.tight_layout()

    solara.FigureMatplotlib(
        fig
    )


# ============================================================
# SIMULATION CONTROLS
# ============================================================

@solara.component
def SimulationControls():

    solara.Markdown(
        "## Simulation Controls"
    )

    # --------------------------------------------------------
    # Simulation days
    # --------------------------------------------------------

    solara.Markdown(
        f"**Simulation days:** {simulation_days.value}"
    )

    solara.SliderInt(
        "Simulation days",
        value=simulation_days,
        min=30,
        max=1000,
        step=5,
        thumb_label="always",
    )

    # --------------------------------------------------------
    # Employees
    # --------------------------------------------------------

    solara.Markdown(
        f"**Number of employees:** {n_employees.value}"
    )

    solara.SliderInt(
        "Number of employees",
        value=n_employees,
        min=10,
        max=500,
        step=10,
        thumb_label="always",
    )

    # --------------------------------------------------------
    # Office days
    # --------------------------------------------------------

    solara.Markdown(
        f"**Office days per week:** {office_days.value}"
    )

    solara.SliderInt(
        "Office days per week",
        value=office_days,
        min=0,
        max=5,
        step=1,
        thumb_label="always",
        tick_labels=True,
    )

    # --------------------------------------------------------
    # Seed
    # --------------------------------------------------------

    solara.Markdown(
        f"**Seed:** {seed.value}"
    )

    solara.SliderInt(
        "Seed",
        value=seed,
        min=1,
        max=100,
        step=1,
        thumb_label="always",
    )

    with solara.Row(
        gap="12px"
    ):

        solara.Button(
            "RUN SIMULATION",
            on_click=run_simulation,
            color="primary",
        )

        solara.Button(
            "RESET SIMULATION",
            on_click=reset_simulation,
        )


# ============================================================
# CURRENT RESULTS
# ============================================================

@solara.component
def CurrentResults():

    params = get_policy_parameters(
        office_days.value
    )

    initial_engagement = 0.21

    if final_engagement.value is not None:

        final_value = (
            final_engagement.value * 100
        )

        relative_improvement = (
            (
                final_engagement.value
                - initial_engagement
            )
            / initial_engagement
            * 100
        )

    else:

        final_value = None
        relative_improvement = None

    solara.Markdown(
        "## Current Results"
    )

    solara.Markdown(
        f"""
**Policy:** {params["policy"]}

**Work arrangement:**  
{params["office_days"]} office / {params["remote_days"]} remote days

**Flexibility:** {params["flexibility"]:.3f}

**Collaboration:** {params["collaboration"]:.3f}

**Number of employees:** {n_employees.value}

**Simulation period:** {simulation_days.value} days

**Initial engagement:** {initial_engagement * 100:.2f}%

**Final engagement:** {
    f"{final_value:.2f}%"
    if final_value is not None
    else "Run simulation"
}

**Relative improvement:** {
    f"{relative_improvement:.2f}%"
    if relative_improvement is not None
    else "Run simulation"
}
"""
    )


# ============================================================
# MAIN PAGE
# ============================================================

@solara.component
def Page():

    with solara.Column(
        gap="25px",
        style={
            "width": "100%",
            "max-width": "1200px",
            "margin": "0 auto",
            "padding": "20px 30px",
        },
    ):

        # ----------------------------------------------------
        # Title
        # ----------------------------------------------------

        solara.Markdown(
            "# Hybrid Work Policy Simulation"
        )

        solara.Markdown(
            """
Interactive multi-agent simulation for exploring how alternative
hybrid workplace policies may influence employee engagement over time.
"""
        )

        # ====================================================
        # TOP SECTION
        # Controls + Results
        # ====================================================

        with solara.Columns(
            [3, 2],
            gutters="30px",
        ):

            # LEFT SIDE
            with solara.Column(
                gap="8px"
            ):

                SimulationControls()

            # RIGHT SIDE
            with solara.Column(
                gap="8px"
            ):

                CurrentResults()

        # ====================================================
        # GRAPH
        # ====================================================

        solara.Markdown(
            "---"
        )

        EngagementChart()

        solara.Markdown(
            """
            ---

            ### Academic Project August.2026

            Developed as part of doctoral research at the  
            **Faculty of Engineering of the University of Porto (FEUP), Porto, Portugal**

            **Danielle Luz**  
            Doctoral Program in Informatics Engineering - (FEUP)  
            
            ORCID: 0009-0006-7235-5953  

            **PhD Supervisor: Rosaldo Rossetti**  
            Department of Informatics Engineering -  (FEUP)   
            ORCID: 0000-0002-1566-7006
            """
                    )
        