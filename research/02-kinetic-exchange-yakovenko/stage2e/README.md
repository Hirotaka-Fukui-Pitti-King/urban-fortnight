# Stage 2-E — Continuous joint saving and conditional fiat-money clearing

**Result: continuous CM savings optimization and one-period monetary auctions executed. Stationary monetary GE NOT recovered.**

Stage 2-E introduces continuous next-period capital and nominal money choice, globally optimal for a diagonal-triangle *piecewise-affine* continuation-value approximation. Both value evaluation and population transition use the same CM optimizer. All-pair DM Nash contracts remain a finite menu; a separate multistart continuous Nash optimization is tested at one positive-trading pair. The conditional fiat price solver uses the **same-price** optimal money-demand correspondence and does not rescale issuer balances.

Reproduce from repository root with requirements.txt installed:

    python -m unittest discover -s research/02-kinetic-exchange-yakovenko/stage2e/tests -v
    python research/02-kinetic-exchange-yakovenko/stage2e/scripts/run_stage2e.py

Six economic tests succeeded locally. CM one-period prices: 5x5=3.0112500000, 7x7=3.0103125000; each preserves issuer stock one and satisfies its conditional goods/resource budget, but Bellman errors remain around 153 and distribution errors 0.55–0.73. The saved JSON/CSV/SVG and GitHub Actions artifact report **NO stationary monetary GE**.

See notes/original_algorithm_audit.md and notes/stationary_equilibrium_diagnostics.md for original algorithm deviations, incomplete continuous Nash validation and next research gate.
