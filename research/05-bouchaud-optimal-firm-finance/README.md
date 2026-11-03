# Stage 5: Bouchaud-Inspired Firm Fragility with Optimal Firms

**Status:** Planned — no model solutions or empirical results claimed. **Category:** economic mechanism.

## Research question

Can financial fragility, defaults and employment cascades from Bouchaud-inspired macro ABMs be reconstructed with optimizing firms and clearing credit, goods and labor markets?

## Feasibility assessment

Conditional: Mark-0-style heuristic behavioral rules are not automatically optimizing general equilibrium; compare the original heuristic benchmark to a separately microfounded firm model.

## Economic mechanisms

- Heterogeneous firm investment, employment and financing
- Credit supply, collateral and endogenous default
- Entry, exit and propagation of balance-sheet shocks
- Economically closed intermediaries and losses

## Model objects and equations

**State variables:** firm net worth, debt, employment and productivity; bank equity and loan positions; household wealth and aggregate production.

- Firm dynamic optimization and default/limited-liability constraints
- Intermediary budget and loan market clearing
- Household ownership and distribution of profits/losses
- Aggregate resource and labor market clearing

## Nested benchmark

Stage 0/4 equilibrium without frictions; original Bouchaud-style heuristic ABM as a labeled non-equilibrium comparator

## Mandatory tests

- Firm and bank ledger reconciliation after default
- No double count of credit, capital or dividend flows
- Optimization/deviation residuals and credit-market clearing
- Switch-off friction returns baseline equilibrium
- Shock-induced tipping region stable across solvers and grids

## Stage completion criterion

Accept only an explicitly optimized firm/credit mechanism; document which original Bouchaud properties do and do not survive.

**Literature to consult and verify:** Bouchaud and coauthors on Mark-0 macroeconomics; Gualdi et al. (2015); Corporate default and financial accelerator literature.

Reports, code versions, seed files and diagnostics should be stored in `results/`. The machine-readable specification is `plan.json`; model decisions and counterexamples are recorded in `RESEARCH.me`.
