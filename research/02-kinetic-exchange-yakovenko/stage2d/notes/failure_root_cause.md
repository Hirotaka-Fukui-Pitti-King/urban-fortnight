# Stage 2-D: Root-cause investigation and price-clearing experiment

**Status (2026-11-03): the conditional centralized-market money auction clears exactly; joint stationary monetary general equilibrium has NOT converged or been certified.**

## Reference and status of primary evidence

The underlying Molico–Zhang model is the November 2005 manuscript, *Monetary Policy and the Distribution of Money and Capital* (SCE 2006, no. 136). Original-mathematics source: https://citeseerx.ist.psu.edu/document?doi=e6826088816be6c1deea19bd1f677f16d190316f&repid=rep1&type=pdf . The text-indexed paper describes centralized money/capital trade (no CM production) and the algorithm's step 3: **solve money-clearing CM price for the current entrant wealth distribution and value function, then update portfolios, bargaining terms and the distribution**. The original-source PDF page images were not accessible for a graphical equation audit, so do not claim full page-by-page visual verification.

Stage 2-C instead evolved the privately optimal distribution repeatedly at a fixed, nonclearing price. The resulting nominal stock changed from issuer supply 1 to, for instance, 1.18318284 in the active private branch at price 3. This is not an equilibrium.

## Three concrete implementation failures found

1. **Inconsistent household optimization.** Stage 2-C's \`calc_W\` takes a discrete maximum over jointly chosen next capital/money only at 501 uniformly spaced wealth grid points and interpolates those values at bargaining wealth and pre-DM states; \`central_forward\` instead chooses the *exact* maximizing portfolio at the actual wealth values. Thus the value update and the distribution's portfolio policy are not the same decision problem at the finite discretization level. Reproducing the old active private branch at price 3 (1,249 iterations, Bellman residual 9.8245e-8, mean capital 0.986579, mean fiat money 1.183183), replacing interpolated W with exact finite-choice W changes the value update by sup 356.425873 (distribution-weighted 16.878814), changes 181 discrete Nash pair contracts and changes the one-period distribution by TV 0.0748668. These are code/model numerical diagnostics, not a general-equilibrium comparative static.

2. **Artificial seller payment ceiling.** Old bargaining excluded positive seller receipts whenever the seller already held \`mmax\`, even though \`mmax\` should bound **next-period CM saving choices**, not a DM intermediate balance. New code allows post-DM money up to \`2*mmax\` and expands the intermediate money grid. At the test continuation value \`V=5*(k+m/3)\`, the corrected model has strictly positive high-balance seller contracts that were mechanically forbidden by the old code. The CM next-period saving choice remains constrained on its original grid.

3. **Discontinuous exact money demand.** Because CM portfolios are discrete, the money-demand correspondence jumps as price moves through an exact tie; conventional scalar Brent/bisection on a continuous excess-demand *function* is not valid across these jumps. We locate an upward switch in the correspondence, verify that the DM bargaining kernel did not jump and that the switching CM portfolios are jointly optimal to a tight tolerance, then choose an equilibrium-consistent **lottery only between genuinely tied CM policies** to clear the issuer's money supply. No monetary balances are rescaled after saving.

## Executed one-period exact CM clearing (all use a feasible M=1 initial distribution)

| Grid (capital x money) | CM clearing price | End-CM money | Maximum reported CM regret | Aggregate budget residual |
|---:|---:|---:|---:|---:|
| 5x5 | 3.1107843541 | 1.0 | <1e-9 | <1e-12 |
| 7x7 | 3.0530664156 | 1.0 | <1e-9 | <1e-12 |
| 9x9 | 2.9795360208 | 1.0 | <1e-9 | <1e-12 |

These are **one-period price clears**, conditioning on an initial mass concentrated at the middle of each grid and a deliberately unoptimized continuation value \`V=5*(k+m/3)\`. The price is *not* demonstrated to converge as the grid becomes finer. The exact CM budget/goods-resource identity is

    C + K_next + M_next/p_k = (1-delta) K_initial + Y_DM + M_initial/p_k .

Both M_initial and M_next equal 1 in these CM experiments. No central firm production, wage, or independent capital-demand equation was introduced.

## Attempted simultaneous stationary equilibrium and resulting failure

Using the source-aligned price step with the corrected exact CM operator, the stationary iteration from the feasible M=1 initial distribution successfully cleared CM money in each of its first 15 updates, but subsequently could not find a verified indifference-compatible price. The Bellman and distribution sup residuals remained far above acceptance thresholds. An alternative warm initialization from the old positive private branch (adjusted to the real fiat stock by economic redistribution of the *starting state*, not after-the-fact normalization) also failed. Thus **a positive stationary monetary equilibrium has not been computed**.

This failure might involve noncontractive joint price-value-distribution iteration, large CRRA value shifts, discontinuous policy maps, small asset/contract grids, and the existence of distinct private regimes. It does not imply monetary equilibrium nonexistence. Original authors used adaptive simulated wealth states, continuous policy optimization and approximately 100x100 interpolated grids with 10,000 agent portfolios; this project does not replicate that algorithm.

## Acceptance conditions not passed

- Stationary Bellman optimality: NOT PASSED.
- Continuous portfolio optimality, Euler/KKT residuals: NOT IMPLEMENTED.
- Continuous Nash bargaining optimality: NOT IMPLEMENTED.
- Independent money-market clearing at every *conditional* CM auction: PASSED.
- Joint stationary distribution with money supply 1: NOT PASSED.
- Stationary aggregate resource clearing: NOT PASSED.
- Numerical grid convergence: NOT PASSED (conditional price changes 5x5 to 9x9).
- Particle/Boltzmann and monetary-policy comparisons at verified stationary GE: NOT EXECUTED.
- Novelty beyond Molico–Zhang (2006): NOT SHOWN.

**Next decision:** keep the exact CM evaluation and intermediate-state financial accounting; implement a robust continuous or carefully tie-aware CM portfolio correspondence, and solve the price/bargaining/distribution fixed point jointly via continuation with verified global resource consistency. Do not present a clearing *single auction* as a full general equilibrium.
