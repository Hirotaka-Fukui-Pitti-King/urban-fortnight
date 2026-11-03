# Stage 1: Agent-Based Econophysics as an Equilibrium Computation Method

**Status:** Planned — no model solutions or empirical results claimed. **Category:** method.

## Research question

Can many-agent simulations of policy-optimal decisions replicate the stationary and transition distributions of the same heterogeneous-agent general equilibrium model?

## Feasibility assessment

Yes as a numerical representation, provided the simulated decision rules solve the same equilibrium and common/aggregate risk is consistently forecast.

## Economic mechanisms

- Individual agents use verified Bellman policies
- Finite-N Markov evolution and seed-controlled Monte Carlo
- Distribution operator and particle-method comparison

## Model objects and equations

**State variables:** individual asset and income state arrays; cross-sectional distribution and moments; prices and aggregate state.

- Discrete Kolmogorov or histogram distribution evolution
- Law of motion of aggregate states
- Market-clearing identities in agent simulation

## Nested benchmark

Distributional operator solution of Stage 0 at the same prices and shocks

## Mandatory tests

- Particle distribution converges to stationary measure as N and time increase
- Policies agree with Stage 0 over the state grid
- Aggregate resource and financial asset accounting
- Common-shock versus idiosyncratic-shock simulation distinction
- Multiple-seed confidence intervals and reproducible run manifests

## Stage completion criterion

Treat ABM as an implementation method, not as a free-standing economic microfoundation.

**Literature to consult and verify:** Aiyagari (1994); Krusell and Smith (1998); Numerical distribution simulation methods.

Reports, code versions, seed files and diagnostics should be stored in `results/`. The machine-readable specification is `plan.json`; model decisions and counterexamples are recorded in `RESEARCH.me`.
