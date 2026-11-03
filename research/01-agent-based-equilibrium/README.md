# Stage 1: Finite-Agent Simulation of Optimal Policies

Status: **preliminary simulation comparison**, not a proven finite-N general equilibrium.

Agents evolve using the *same* Stage 0 policy functions and idiosyncratic Markov transitions, at fixed stationary general-equilibrium prices. The simulated asset decisions remain continuous; histogram mass-splitting is **not** imposed on individual choices.

Run `python research/01-agent-based-equilibrium/scripts/run_particles.py`, or add `--quick` for the CI smoke experiment.

Local experiment: 1,400 burn-in periods, 150 measurement periods, seeds 101/202/303.

| N | Average simulated K | Stage 0 reference K |
|---:|---:|---:|
| 2,500 | 5.537903 | 5.706221 |
| 10,000 | 5.661995 | 5.706221 |
| 40,000 | 5.669039 | 5.706221 |

The mean N=40,000 difference is about -0.65%. It may combine finite-N sampling noise and histogram-discretization bias. Nine seed/population combinations and one reproducibility unit test have been executed; more seeds and asset-grid refinements are needed to establish a convergence rate. No endogenous price re-clearing is performed for individual finite-N realizations.
