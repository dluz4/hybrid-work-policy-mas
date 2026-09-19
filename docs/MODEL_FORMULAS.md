# Model Parameters and Assumptions

## Purpose

This document describes the main variables, parameters, mathematical
assumptions, and reference values used in the Hybrid Work Policy
Agent-Based Simulation model.

Its purpose is to improve model transparency, reproducibility, and
traceability by documenting:

- what each variable and parameter represents;
- where it is used in the model;
- how it affects the simulation;
- the reference value or range currently used;
- whether the value is empirically calibrated or represents a modelling
  assumption;
- how the parameter is addressed in sensitivity analysis; and
- what should be investigated in future empirical research.

The current model is a proof-of-concept simulation framework.
Unless explicitly stated otherwise, parameter values and functional
relationships documented here should be interpreted as modelling
assumptions rather than empirically calibrated estimates.


# Model Formulas and Parameters

This document provides a concise reference for the main formulas,
symbols, and parameters used in the Hybrid Work Policy Agent-Based
Simulation model.

## 1. Main Symbols

| Symbol | Meaning |
|---|---|
| \(i\) | Employee agent |
| \(t\) | Simulation day |
| \(N\) | Number of employees |
| \(D_r\) | Number of remote workdays per week |
| \(r\) | Proportion of remote workdays |
| \(F\) | Workplace flexibility |
| \(C\) | Collaboration opportunity |
| \(k\) | Curvature parameter of the flexibility function |
| \(\gamma\) | Curvature parameter of the collaboration function |
| \(E_i(t)\) | Engagement of employee \(i\) at day \(t\) |
| \(E_i(0)\) | Initial engagement |
| \(s_i^F\) | Employee sensitivity to flexibility |
| \(s_i^C\) | Employee sensitivity to collaboration |
| \(\alpha\) | Flexibility gain coefficient |
| \(\beta\) | Collaboration gain coefficient |
| \(\delta\) | Low-collaboration penalty coefficient |
| \(\epsilon_i(t)\) | Daily stochastic variation |
| \(\bar{E}(t)\) | Mean organizational engagement |
| \(E_{\mathrm{final}}\) | Final organizational engagement |

## 2. Workplace Policy Formulas

### Remote-work proportion

\[
r = \frac{D_r}{5}
\]

\(D_r\) is the number of remote workdays in a five-day workweek.
Therefore, \(r=0\) represents fully office-based work and \(r=1\)
represents fully remote work.

### Flexibility

\[
F(r)=20+80\frac{1-e^{-kr}}{1-e^{-k}}
\]

Flexibility increases as the proportion of remote work increases.

- \(r\): proportion of remote workdays
- \(k\): controls the curvature and rate of flexibility gains
- Reference value: \(k=2\)

The model uses the equivalent normalized 0--1 value internally.

### Collaboration

\[
C(r)=20+80(1-r)^{\gamma}
\]

Collaboration opportunity decreases as remote work increases.

- \(r\): proportion of remote workdays
- \(\gamma\): controls the curvature of the collaboration decline
- Reference value: \(\gamma=0.5\)

The model uses the equivalent normalized 0--1 value internally.

## 3. Engagement Update

Employee engagement is updated each simulation day as:

\[
E_i(t+1)=
\operatorname{clip}
\left(
E_i(t)
+\alpha F s_i^F[1-E_i(t)]
+\beta C s_i^C[1-E_i(t)]
-\delta(1-C)s_i^C E_i(t)
+\epsilon_i(t),
0,1
\right)
\]

In simple terms:

**Next engagement = Current engagement + Flexibility gain +
Collaboration gain - Low-collaboration penalty + Random daily variation**

Reference parameters:

| Parameter | Reference value | Meaning |
|---|---:|---|
| \(E_i(0)\) | 0.50 | Initial engagement |
| \(s_i^F\) | \(U(0.5,1.0)\) | Flexibility sensitivity |
| \(s_i^C\) | \(U(0.5,1.0)\) | Collaboration sensitivity |
| \(\alpha\) | 0.0015 | Flexibility gain |
| \(\beta\) | 0.0015 | Collaboration gain |
| \(\delta\) | 0.0010 | Low-collaboration penalty |
| \(\epsilon_i(t)\) | \(N(0,0.002^2)\) | Daily stochastic variation |

The `clip(...,0,1)` operation ensures that engagement always remains
between 0 and 1.

## 4. Organizational Engagement

Mean organizational engagement is:

\[
\bar{E}(t)=\frac{1}{N}\sum_{i=1}^{N}E_i(t)
\]

where \(N\) is the number of employees.

Final engagement is:

\[
E_{\mathrm{final}}=\bar{E}(365)
\]

representing mean organizational engagement at the end of the
365-day simulation.

## 5. Sensitivity Analysis

The current model evaluates:

\[
k\in\{1,2,3\}
\]

\[
\gamma\in\{0.3,0.5,0.7\}
\]

and:

\[
E_i(0)\in\{0.30,0.50,0.70\}
\]

These values are used to examine whether policy comparisons change
under different mathematical assumptions and organizational starting
conditions.

## Important Note

The current parameter values and mathematical relationships are
modelling assumptions used for the proof-of-concept simulation.
They should not be interpreted as empirically calibrated estimates.