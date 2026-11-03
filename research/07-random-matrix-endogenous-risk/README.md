# Stage 7: Random Matrix Diagnostics of Endogenous Correlations

**Status:** Planned — no model solutions or empirical results claimed. **Category:** analytical method.

## Research question

Do spectral patterns of model-generated financial returns identify economically meaningful common risk beyond sampling noise?

## Feasibility assessment

Direct as a statistical diagnostic of equilibrium outcomes, but random matrix theory by itself is not an optimal-choice or market-clearing mechanism.

## Economic mechanisms

- Cross-asset covariance and spectral eigenvalue distributions
- Marchenko-Pastur null when its assumptions hold
- Common risk-factor and correlation-network diagnostics
- Out-of-sample systemic-risk prediction

## Model objects and equations

**State variables:** T-by-N equilibrium return panel; empirical correlation and covariance matrices; eigenvalues, eigenvectors and factor estimates.

- Finite-sample spectral measures
- Null distribution under documented independence assumptions
- Model-generated covariance and risk network functions

## Nested benchmark

Independent asset returns and conventional factor models at the same sample size

## Mandatory tests

- Recover reference null with controlled Monte Carlo
- Stability under heavy tails and time dependence
- Out-of-sample predictive content
- Link risk eigenvectors back to holdings and balance sheets
- Do not mistake statistical significance for a new equilibrium mechanism

## Stage completion criterion

Retain only diagnostically or predictively informative spectral statistics; no artificial structural claim.

**Literature to consult and verify:** Marchenko and Pastur (1967); Laloux et al. (1999); Financial random matrix theory.

Reports, code versions, seed files and diagnostics should be stored in `results/`. The machine-readable specification is `plan.json`; model decisions and counterexamples are recorded in `RESEARCH.me`.
