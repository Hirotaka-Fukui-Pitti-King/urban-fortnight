# Stage 2-H — Convex continuous Nash, source-code audit, and 5x5 private-root attempt

**Scope:** finite triangle-pair convex Nash under the existing piecewise-affine CM interpolation, independently compared to the monotone upper/lower Nash bounds. Stage 2-H does **not** assert stationary monetary GE.

- Real Chiu–Molico (2021) Fortran archive retrieved and examined; **not** Molico–Zhang original source.
- Implemented CVXPY/Clarabel `src/convex_nash.py`: each buyer/seller CM triangle pair is a DCP-verified concave Nash maximization, with conservative upper-bound pruning and independent outside-option evaluation.
- Executed matched-pair 3x3 numerical result (buyer=seller=4, price=2.5): output about 1.06350632, nominal payment 1, Nash log objective about 4.6355727069; 39 subproblems solved after 25 safe prunes. Original 64-branch solver and independent monotone rectangle bound agree.
- Executed 5x5 candidate-root attempt: direct root fails; matching-rate continuation has produced converged **intermediate** private problems but no source-rate 5x5 certified fixed point.
- `scripts/validate_private_5x5.py` globally reoptimizes and independently checks *any* successful 5x5 candidate. If the candidate is absent, it explicitly reports no candidate.
- High-cost 5x5 root and Fortran audit run via manual workflow; pull-request CI runs only convex numerical tests and the one-pair benchmark.

Run the basic checks with scientific Python 3.13, CVXPY and Clarabel:
```bash
python -m unittest discover -s research/02-kinetic-exchange-yakovenko/stage2h/tests -v
python research/02-kinetic-exchange-yakovenko/stage2h/scripts/benchmark_global_nash.py
```

Refer to `notes/convex_nash_derivation.md`, `notes/literature_and_code_audit.md` and `results/*.json`.
