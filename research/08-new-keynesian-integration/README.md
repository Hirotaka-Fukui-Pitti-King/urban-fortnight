# Stage 8: New Keynesian Integration after General-Equilibrium Compatibility

**Status:** Planned — no model solutions or empirical results claimed. **Category:** extension.

## Research question

Which equilibrium-compatible statistical-mechanical mechanisms add distinct predictions for inflation, monetary transmission, wealth inequality and welfare once nominal rigidity is introduced?

## Feasibility assessment

Proceed only after mechanisms in Stages 2–7 have individually passed feasibility, rational-expectations and market-clearing checks.

## Economic mechanisms

- Calvo staggered prices and optimal reset pricing
- Monetary policy and goods-price inflation
- Embedding of validated exchange, social, credit and trading mechanisms
- Nonlinear inflation, output, inequality and welfare effects

## Model objects and equations

**State variables:** goods-price dispersion and monetary policy states; endogenous wealth-belief distribution; firm credit and security markets, where validated.

- Firm dynamic optimal pricing and Calvo price index
- Household Euler/Bellman equations with rational equilibrium forecasts
- Goods, labor, money/bonds and security-market clearing
- Central bank policy rule and equilibrium transition

## Nested benchmark

Standard NK and HANK benchmark without statistical-mechanical components

## Mandatory tests

- Recover flexible-price and conventional HANK limits
- Exact Calvo price aggregation and pricing FOC
- Monetary-policy impulse response with full asset and resource accounting
- One-at-a-time and joint mechanism ablations
- Welfare evaluated on optimized households and stable equilibrium

## Stage completion criterion

Do not implement before Stages 0–4 pass their core gates; optional firm/finance modules enter only if Stages 5–7 pass.

**Literature to consult and verify:** Calvo (1983); Woodford (2003); Heterogeneous-agent New Keynesian literature.

Reports, code versions, seed files and diagnostics should be stored in `results/`. The machine-readable specification is `plan.json`; model decisions and counterexamples are recorded in `RESEARCH.me`.
