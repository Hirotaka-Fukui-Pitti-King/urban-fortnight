# Stage 2: Kinetic Exchange and Wealth Distribution

**Status:** Planned. **Dependencies:** Stage 0, Stage 1.

## Central research question

Does pairwise asset exchange change wealth concentration and monetary transmission in a HANK economy?

## Economic mechanisms

- Feasible pairwise asset transfer kernel
- Boltzmann-type distribution evolution
- Joint asset, income and belief distribution
- Wealth-dependent interactions

## Economic closure and model caveats

- Conserve the combined financial assets of each closed pairwise exchange.
- Account separately for income, asset issuance, taxes, and transfers.
- Impose individual borrowing and budget constraints; exchange is not production.

## Nested comparators

- no pairwise exchange
- exchange with independent beliefs
- exchange with Ising beliefs

## Acceptance tests

- Exact two-agent and aggregate ledger identities
- Mass conservation, nonnegative density and feasibility
- Particle simulation versus distribution solver
- Switch-off recovery and mesh/agent-count convergence

## Deliverables

- Validated asset-exchange simulation
- Wealth distribution and monetary MPC heterogeneity

**Progression gate:** The numerical equilibrium, accounting identities, convergence checks and nested comparator must be verified before moving to the next stage. Record the code revision, seeds and tolerances in `results/`.

**Literature starting points (verify during implementation):** Yakovenko and Rosser (2009); Kinetic exchange literature.
