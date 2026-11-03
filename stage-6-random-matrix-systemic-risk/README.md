# Stage 6: Random Matrix Methods and Systemic Risk

**Status:** Planned. **Dependencies:** Stage 0, Stage 1, Stage 2, Stage 3, Stage 4, Stage 5.

## Central research question

Can spectral correlation measures identify model-generated systemic risk beyond conventional factors and sampling noise?

## Economic mechanisms

- Cross-asset covariance and correlation spectra
- Random-matrix sampling-noise benchmarks
- Macro-financial stress diagnostics
- Out-of-sample correlation risk tests

## Economic closure and model caveats

- Treat random matrix theory first as a diagnostic, not an optimizing agent.
- Apply Marchenko-Pastur benchmarks only under defensible null assumptions.
- Separate predictive content from mechanical in-sample fitting.

## Nested comparators

- independent returns null
- conventional factor model
- endogenous market interactions

## Acceptance tests

- Null simulation across dimensions and samples
- Eigenvalue and eigenvector stability
- Out-of-sample stress predictability
- Full model component ablation

## Deliverables

- Spectral diagnostic toolkit
- Validated macro-financial risk exhibits

**Progression gate:** The numerical equilibrium, accounting identities, convergence checks and nested comparator must be verified before moving to the next stage. Record the code revision, seeds and tolerances in `results/`.

**Literature starting points (verify during implementation):** Marchenko and Pastur (1967); Laloux et al. (1999).
