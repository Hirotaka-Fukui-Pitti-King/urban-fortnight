# Stage 4: Statistical Equilibrium and Maximum Entropy

**Status:** Planned — no model solutions or empirical results claimed. **Category:** analytical method.

## Research question

Under what constraints, invariant measures and equilibrium policies does the heterogeneous-agent distribution admit a rigorous entropy-based characterization?

## Feasibility assessment

Conditional: household optimality and competitive clearing alone do not imply Boltzmann-Gibbs or maximum entropy; require derivable invariant or optimization conditions.

## Economic mechanisms

- Master equations for joint asset and action distributions
- Stationary measures, probability currents and detailed balance
- Constrained maximum entropy as a candidate representation
- Phase diagrams and metastability if justified

## Model objects and equations

**State variables:** invariant distribution and transition kernel; conserved resources and explicit constraints; aggregate prices and any order parameters.

- Stationary distribution operator or master equation
- Resource/moment constraints and probability normalization
- Conditional entropy optimization and Lagrange multipliers
- Detailed balance or stationary probability-current identities

## Nested benchmark

Direct invariant distribution of verified GE policy functions, with and without reversible dynamics

## Mandatory tests

- Prove/verify existence of stationary distribution under assumptions
- Check whether proposed entropy density is invariant under the actual kernel
- Compare moments and tail behavior to direct microsimulation
- Provide explicit counterexample if maximum-entropy property fails
- Show when detailed balance is not required or not satisfied

## Stage completion criterion

Prove a conditional characterization or report an informative failure; do not impose entropy as an equilibrium axiom.

**Literature to consult and verify:** Jaynes (1957); Markov chains and invariant measures; Statistical equilibrium in economic models.

Reports, code versions, seed files and diagnostics should be stored in `results/`. The machine-readable specification is `plan.json`; model decisions and counterexamples are recorded in `RESEARCH.me`.
