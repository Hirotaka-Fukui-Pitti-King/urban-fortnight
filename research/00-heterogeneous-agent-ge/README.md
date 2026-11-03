# Stage 0: Optimizing Heterogeneous-Agent General Equilibrium

**Status:** Planned — no model solutions or empirical results claimed. **Category:** benchmark.

## Research question

Can a canonical incomplete-markets heterogeneous-agent economy satisfy individual optimization, rational expectations and general equilibrium with sufficiently accurate numerical solutions?

## Feasibility assessment

Baseline: established in standard Aiyagari/Huggett-type economies, subject to the specified asset and aggregate-risk closure.

## Economic mechanisms

- Incomplete-markets household saving and labor decisions
- Competitive firms, wages and asset returns
- Stationary equilibrium and optional aggregate uncertainty with rational forecasting

## Model objects and equations

**State variables:** individual financial assets a; idiosyncratic productivity z; aggregate distribution mu; aggregate shocks and prices, when active.

- Household Bellman and Euler equations
- Household budget and borrowing constraints
- Goods, labor and bond/capital market clearing
- Rational aggregate transition law

## Nested benchmark

Canonical representative-agent or no-idiosyncratic-risk economy under the same primitives

## Mandatory tests

- Household feasibility and Euler/Bellman residuals
- Firm optimization and zero-profit/distributional profit allocation
- Asset supply and goods/labor clearing to documented tolerances
- Distribution normalization, stationary moments and grid convergence
- Krusell-Smith forecasting accuracy if aggregate risk is activated

## Stage completion criterion

Accept a fully converged and economically closed baseline; do not add nominal rigidity yet.

**Literature to consult and verify:** Huggett (1993); Aiyagari (1994); Krusell and Smith (1998).

Reports, code versions, seed files and diagnostics should be stored in `results/`. The machine-readable specification is `plan.json`; model decisions and counterexamples are recorded in `RESEARCH.me`.
