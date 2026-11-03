# Stage 2-F — Adaptive grids and the separate Nash policy-stability problem

**Result:** implemented and executed mass/moment preserving adaptive portfolio-grid transport and a convergent fixed-contract Bellman evaluator. However endogenous discrete Nash policy improvement still cycles. Stationary monetary general equilibrium is NOT recovered.

Economically relevant source corrections:
- Molico–Zhang Section 4 Step 4 evaluates W on [0,4 wmax]; Step 5 retains real-wealth distribution and portfolio rules; Step 6 changes kmax=2 wmax and mmax=2 wmax*p_k. Our source-aligned grid bounds and mass/moment conserving transport are implemented and tested, but not integrated into the full equilibrium solver.
- Fixing bilateral contracts and partner distribution gives a beta-contraction household value operator. In a 5x5 *discrete bargaining* benchmark, conditional Bellman evaluation converges in 36 and 37 iterations at prices 2.5 and 3.0, whereas reoptimized Nash contracts fail to stabilize after 30 policy improvements. Discrete Nash cycling is distinct from the fixed money-savings grid error.

Run from repository root:

    PYTHONPATH=research/02-kinetic-exchange-yakovenko/stage2f/src:research/02-kinetic-exchange-yakovenko/stage2d/src:research/02-kinetic-exchange-yakovenko/stage2c/src python -m unittest discover -s research/02-kinetic-exchange-yakovenko/stage2f/tests -v
    python research/02-kinetic-exchange-yakovenko/stage2f/scripts/run_fixed_price_diagnostic.py

See notes/numerical_root_cause.md and results/reference_fixed_price_diagnostic.json; .github/workflows/stage2f.yml runs tests and produces a JSON/CSV artifact. None of this proves a stationary monetary GE or a new kinetic economic mechanism.
