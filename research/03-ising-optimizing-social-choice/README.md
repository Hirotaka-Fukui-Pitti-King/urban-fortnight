# Stage 3: Ising-Type Social Interactions from Optimal Choices

**Status:** Planned — no model solutions or empirical results claimed. **Category:** economic mechanism.

## Research question

Can optimizing households display mean-field/Ising social complementarities while maintaining rational expectations about aggregate states and equilibrium prices?

## Feasibility assessment

Conditional: binary actions with complementarities and idiosyncratic taste shocks can generate logistic best responses; do not replace rational forecasts with unvalidated heuristic belief switching.

## Economic mechanisms

- Discrete participation, technology adoption, or labor choice
- Peer payoff complementarity J s_i m
- Private taste shocks and conditional optimal policies
- Aggregate-consistent social fixed points and equilibrium selection

## Model objects and equations

**State variables:** binary individual action s_i; mean action m and possibly network structure; household assets/income and equilibrium prices.

- Optimal Bellman value differences across actions
- Logit choice probabilities under stated taste-shock law
- Mean-field self-consistency m=E[s_i]
- Rational forecast of aggregate motion conditional on information
- All-market clearing with endogenous social choices

## Nested benchmark

Same Heterogeneous-Agent GE with peer payoff J=0; separately a non-rational belief-update specification

## Mandatory tests

- Derive rather than assert logit best responses
- Verify household deviation inequalities and social fixed point
- Locate multiple-equilibrium region under exact normalization
- Account for multiplicity and an explicit equilibrium-selection rule
- Peer interaction removal recovers Stage 0/2 counterparts

## Stage completion criterion

Accept optimal Ising-type strategic complementarity only when the equilibrium mapping, not just a behavioral fixed point, exists.

**Literature to consult and verify:** Brock and Durlauf (2001); Ising mean-field theory; Rational expectations heterogeneous-agent equilibrium.

Reports, code versions, seed files and diagnostics should be stored in `results/`. The machine-readable specification is `plan.json`; model decisions and counterexamples are recorded in `RESEARCH.me`.
