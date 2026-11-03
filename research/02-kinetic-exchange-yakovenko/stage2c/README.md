Source verification status for Molico--Zhang: web-indexed text only; PDF pages and equations have NOT been visually verified.

# Stage 2-C — Provisional reconstruction from indexed manuscript text

**Executed original-equation pilot; monetary general equilibrium not obtained.**

Molico and Zhang (2005/2006) uses N>=3 specialized consumption/production types, jointly chosen money and capital, and Nash bargaining over goods and fiat money in a decentralized market (DM). The centralized capital/portfolio market (CM) produces no goods. Unlike the older Stage 2-B, this module does not impose a representative Cobb–Douglas firm producing goods in CM or random portfolio tastes that make fiat money directly desirable.

Run from repository root after installing requirements:

    PYTHONPATH=research/02-kinetic-exchange-yakovenko/stage2c/src python -m unittest discover -s research/02-kinetic-exchange-yakovenko/stage2c/tests -v
    python research/02-kinetic-exchange-yakovenko/stage2c/scripts/run_canonical_benchmark.py

Seven tests passed locally. Among three converged quoted-price private solutions none cleared the exogenous normalized money supply of one. A fourth finer-grid case did not converge. Therefore **no monetary steady-state equilibrium or policy effect is reported**. The small 5x5/7x7 grids are smoke tests only, not the original 100x100 numerical exercise. Candidate equations and their unverified source correspondence, deviations, outcomes and next acceptance gate are documented in notes/canonical_model_reconstruction.md.

An independent GitHub Actions workflow runs the tests, price/grid scan, and uploads CSV/JSON. The main research paper remains academic-typst Quarto; it must explicitly preserve the non-GE caveat.


**New multistart experiment:** With the same 5x5 grid at capital price 3, zero-value/uniform initial conditions converge to near-zero capital/trade and mean money 0.343056; positive-value/concentrated initial conditions converge to an active private stationary state with capital 0.986579, mean money 1.183183 and trade rate 0.241363. Both have Bellman residual below 1e-7, but **both violate the required mean money supply 1**, and neither qualifies as general equilibrium. Run scripts/run_monetary_multistart.py. This is a concrete equilibrium-selection and root-identification obstacle, not a nonexistence theorem.
