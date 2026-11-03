# Stage 0: New Keynesian and HANK Baseline

**Status:** Planned. **Dependencies:** None.

## Central research question

What is the benchmark transmission of monetary policy with nominal rigidity and wealth heterogeneity?

## Economic mechanisms

- Calvo pricing and price dispersion
- Household intertemporal optimization and labor supply
- Idiosyncratic income risk and incomplete-market saving
- Taylor rule, rational expectations and all-market clearing

## Economic closure and model caveats

- Begin with representative-agent NK and extend to HANK.
- Enforce asset supply, government budget, household feasibility, and goods/labor clearing.
- Derive aggregate relations from heterogeneous-agent choices.

## Nested comparators

- representative-agent NK
- HANK with nominal rigidity
- flexible-price economy

## Acceptance tests

- Euler and Bellman residuals
- Stationary distribution normalization and asset-market clearing
- Price-setting and resource constraint residuals
- Grid and horizon convergence; RA and flexible-price benchmark recovery

## Deliverables

- Validated equilibria and impulse responses
- Comparison with canonical NK/HANK

**Progression gate:** The numerical equilibrium, accounting identities, convergence checks and nested comparator must be verified before moving to the next stage. Record the code revision, seeds and tolerances in `results/`.

**Literature starting points (verify during implementation):** Calvo (1983); Woodford (2003); HANK sequence-space literature.
