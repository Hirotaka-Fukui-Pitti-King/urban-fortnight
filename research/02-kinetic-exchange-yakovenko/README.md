# Stage 2: Optimal Kinetic Exchange and Boltzmann Dynamics (Yakovenko)

**Status:** Planned — no model solutions or empirical results claimed. **Category:** economic mechanism.

## Research question

Can voluntary optimal bilateral trades generate a kinetic exchange operator consistent with household budgets, rational expectations and market clearing?

## Feasibility assessment

Conditional: exogenous random transfers conserve assets but do not generally arise from optimal trade; require gains from trade, matching frictions or a specified contractual market.

## Economic mechanisms

- State-dependent bilateral matching with voluntary trade
- Bargaining or price-taking mutually feasible exchanges
- Transition kernel for pairwise post-trade holdings
- Boltzmann gain-loss equation coupled with household saving

## Model objects and equations

**State variables:** liquid assets or money and consumption goods; partner state and contract choice; distribution f_t(a,z); aggregate goods, money and asset supply.

- Bilateral post-trade financial asset conservation, accounting for external issuance
- Both partners' budget constraints and participation constraints
- Bellman optimality or bilateral Nash bargaining
- Boltzmann collision operator and other household transition terms
- Goods and financial market clearing

## Nested benchmark

Aiyagari/Huggett GE with kinetic matching shut off; separately exogenous Yakovenko exchange as non-optimal benchmark

## Mandatory tests

- Realized matches satisfy participation and individual budget constraints
- Asset transfers net to zero in a closed pair; goods flows clear
- Particle operator matches nonlinear Boltzmann transition operator
- Density remains normalized and nonnegative
- Zero-matching-rate switch-off recovers baseline prices and distribution
- No exchange theorem/counterexample under frictionless homogeneous preferences

## Stage completion criterion

Accept only if a microfounded, nondegenerate bilateral trading equilibrium exists and aggregate identities hold.

**Literature to consult and verify:** Yakovenko and Rosser (2009); Kinetic exchange and Boltzmann models; Search, matching and bargaining theory.

Reports, code versions, seed files and diagnostics should be stored in `results/`. The machine-readable specification is `plan.json`; model decisions and counterexamples are recorded in `RESEARCH.me`.
