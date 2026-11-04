# Stage 2-H — Executed numerical results and remaining economic blocker

## Purpose and exact status

The first acceptance gate is a fixed-price, fixed-partner **endogenous Nash–Bellman** root on a 5x5 capital–money grid with the *original* matching opportunity rate. This gate has **not** passed. No invariant joint distribution, money-market-clearing price, or stationary GE is claimed.

## Direct literature and source-code audit

The November 2005 Molico–Zhang manuscript was checked for the Nash production/payment constraints and timing. The separate Chiu–Molico (2021) replication archive was fetched and hashed on GitHub Actions: 18,082,836 bytes, SHA256 `deae7bbd3f24167367fa4716b15621ffa9e33ec9fc841f9f68e24c655171c014`. Examined bargaining and steady-state Fortran files: `bargprob.f90`, `dq.f90`, `mm2020.f90`. This is **not the original 2006 capital-and-money model code**. See `notes/literature_and_code_audit.md`.

## Convex-decomposition Nash oracle

For the inherited triangular piecewise-affine V approximation, each buyer/seller CM triangle pair gives a concave log-Nash objective and convex joint participation/feasibility domain. Every relevant pair can be globally compared by solving convex branches, using admissible upper-bound pruning. The Python `src/convex_nash.py` implementation now:
- Attempts strict and relaxed Clarabel plus SCS fallback on ambiguous solver branches.
- Preserves all returned primal candidates across solver attempts and evaluates every candidate with the independent global CM value function.
- Tracks any unresolved branch by its admissible upper log-Nash bound; no silent global certification on failure.
- Never imposes arbitrary 0.95/0.985 production ceilings.

All 17 relevant 3x3 Nash pairs were reoptimized on the solved private V: 11 positive contracts, no unresolved conic branches, maximum log-Nash change 1.5987e-14, Bellman sup 4.54747e-13. CI success **41749186786**.

## Source-rate 5x5 root: failed, but root cause clarified

Model grid: nk=nm=5, k in [0,3], m in [0,2], fixed price 2.5, partners Dirac at (k,m)=(1.5,1). At matching multiplier lambda=0.55, the old fast Nash oracle gave an apparent Bellman root with residual 3.9822e-9. Independent all-49 convex Nash reoptimization changed Bellman residual to **0.655415**, and log Nash objective improved by up to 0.003689 (not a valid private root).

Correcting an incorrectly binding *upper payment* Nash active set yielded a new private continuation sequence. At lambda=.55, .60, .6078125 and .609033203125, the fast private Bellman residuals were approximately 1.87e-10, 4.40e-10, 1.27e-11 and 6.37e-12. The next attempt at .6097961 failed tolerance (residual 1.14e-4); lambda=1 has **not** been reached. Source run **41747487351**.

A new independent all-49 convex reoptimization at *the exact last accepted* lambda=.609033203125 and same 5x5 V reported:
- Relevant directed pairs: 49; positive trades: 39.
- Fast-policy Bellman sup: **6.3664629124e-12**.
- Bellman sup with the **convex-reoptimized policies**: **5.9117155615e-12**.
- Maximum finite log Nash improvement: **5.3290705182e-15**.
- **One** conic branch remains unresolved, buyer 3 / seller 12; rigorous exact-rounded continuous optimum cannot be claimed.
- CI run **41748837033** succeeded and uploaded complete NPZ/CSV/JSON. Persistent numerical reference: `results/5x5_corrected_global_reference.json`.

This is strong evidence for a **conditional intermediate matching-rate private root**, not for the original rate or the actual stationary monetary economy.

## Alternative full-matching price homotopy

To avoid relying on the unsuccessful lambda continuation, `scripts/solve_5x5_price_continuation.py` was implemented and run at the paper's original matching multiplier 1 throughout. The initial high-price root at p=100 failed with private residual approximately 200.519. Increasing starting price to 100,000 reduced but did not eliminate the initial root failure; residual approximately 19.460. Neither path reached target p=2.5. Runs **41749939289** and **41750151841**. These failures are not nonexistence proofs.

## Required next algorithmic test, not a generic recommendation

The last valid 5x5 intermediate root is now saved as an executable Actions artifact. `scripts/diagnose_5x5_jacobian.py` uses that exact state to compute two finite-difference Jacobians (and their grid-step sensitivity), the smallest singular value of the *corrected* 24-dimensional relative Bellman residual, a matching-rate tangent, and targeted trust-region root attempts at lambda .61 and .62. A small singular value would support ordinary fold/near-singular root dynamics; a stable Jacobian but discontinuous contract selection would instead favor generalized/complementarity root formulations. **Only actual output can decide which.**

No 5x5 lambda=1 private equilibrium, adaptive-grid Bellman fixed point, endogenous clearing price, invariant distribution, welfare or price transmission results are certified.
