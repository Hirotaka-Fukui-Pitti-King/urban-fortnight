# Stage 0: Stationary Aiyagari General Equilibrium

Status: **numerically validated reference**, not an analytical existence/uniqueness theorem. We solve CRRA consumption/saving with idiosyncratic Rouwenhorst labor-productivity states, competitive Cobb–Douglas capital and labor demand, rational stationary expectations, and household/firm/goods/asset clearing. No aggregate risk or nominal rigidity is assumed.

## Run

From the repository root, install `requirements.txt` and execute:

- `python research/00-heterogeneous-agent-ge/scripts/run_stationary_equilibrium.py`
- `python research/00-heterogeneous-agent-ge/scripts/run_accuracy_tests.py`
- `python research/00-heterogeneous-agent-ge/scripts/make_figures.py`
- `python -m unittest discover -s research/00-heterogeneous-agent-ge/tests -v`

Stage 0 uses EGM, a mass-preserving histogram distribution operator, and bracketed Brent root solving. Invalid upper-asset-grid policies fail explicitly rather than being clipped.

## Local reference (Python 3.13.5, November 3, 2026)

Calibration: beta=0.96, sigma=2, alpha=0.36, delta=0.08, rho_z=0.9, unconditional log income SD 0.2, 5 productivity states, 360 asset nodes over [0,600].

| Outcome | Calculated |
|---|---:|
| Capital K | 5.70622063 |
| Net return r | 0.03809715 |
| Wage w | 1.19802383 |
| Output Y | 1.87191223 |
| Consumption C | 1.41541457 |
| Asset Gini | 0.49391408 |
| Relative capital-market residual | 2.31e-8 |
| Goods-resource residual | 5.35e-9 |
| Weighted p99 Euler/KKT error | 7.94e-7 |
| Invariant distribution sup-norm residual | 9.90e-13 |
| Stationary probability at upper asset bound | 0 |

The capital solution changes from 5.71077 (200 asset nodes) to 5.70622 (360) to 5.70507 (520), holding income states and the upper bound fixed. See `results/reference_accuracy.csv`. Economic and numerical accuracy must be kept separate; aggregate stochastic rational expectations have not been implemented.

CI uploads policy-function CSV, invariant-distribution CSV, results JSON, and separately rendered SVGs as workflow artifacts.
