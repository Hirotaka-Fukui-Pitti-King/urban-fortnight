# Stage 2-F — Original numerical method and independent failure mechanisms

**Status: no certified stationary monetary-search GE; Stage 2-F restores two critical numerical primitives and isolates a second failure beyond grid boundaries.**

## Exact original numerical procedure (Molico and Zhang, November 2005 manuscript, Section 4, pp. 14–16)

Step 3 clears the centralized capital market for the fixed sample of pre-CM entering money/capital portfolios and given prior V. Step 4 uses maximum real wealth after monetary injections, wmax, to compute W on wealth interval [0,4 wmax], with the source's specific treatment of consumption above 2 wmax. Step 5 updates CM optimal portfolios, representing the next decentralized-market sample as real wealth plus a possibly discontinuous portfolio rule; the real wealth distribution is estimated using Gaussian kernel density methods. **Step 6 recreates asset value-grid bounds kmax=2 wmax, mmax=2 wmax*p_k.** Step 7 updates V and re-solves bargaining; Step 8 simulates DM buyer/seller/no-trade meetings and advances the sample.

The paper reports 100x100 bicubic-spline value grids and a 10,000-person simulation. It says its original parallel Fortran 90 program is available from the authors by request, but a publicly accessible code archive was not verified. The paper's indexed PDF text was available; source screenshots failed, so a page-image-level audit is unverified.

## New implementation 1: adaptive asset bounds with exact conservation

The source-aligned bound rule is implemented in src/adaptive_grids.py. Before remeshing positive-mass portfolios the new grid must cover *all occupied old states*. For the transfer, tensor barycentric splitting preserves total population and the first capital and money moments to roundoff, with no negative weights. No clipping, money normalization, or artificial issuance is allowed; when the support is not covered, an exception is raised. Six executed unit tests cover the original formula, old-support coverage, random mass/moment preservation, refusal to clip, affine interpolation and repeated moment preservation.

**Limitation:** this is a standalone transport primitive. It is NOT yet wired into a stationary source solver. Enlarging V's domain requires recomputing the Bellman operator at new nodes, not extrapolating the previous interpolant. Regridding itself does not preserve nonlinear utility, covariance, or fixed-point consistency.

## New implementation 2: policy evaluation separating Nash contracts from the Bellman operator

For fixed partner distribution f, posted money price and fixed bilateral contracts, CM value is W_V(w)=max_(k',m') {u(w-k'-m'/p)+beta V(k',m')} and the post-DM expected utility operator is

T(V)(s)= [(N-2)/N] W_V(w_0(s))
 + (1/N) sum_j f_j [W_V(w_B(s,j)) + W_V(w_S(s,j)) - v(y(j,s),k_s)].

For a fixed contract schedule the weights sum to one, so ||T(V)-T(U)||_infinity <= beta ||V-U||_infinity. This is a contraction under the finite-grid budget/portfolio feasibility used here. **It is NOT a contraction claim for endogenously reoptimized Nash contracts.**

The Stage 2-F Python implementation independently evaluates fixed contracts to residual <1e-8. It then recomputes every original Stage 2-D finite-grid generalized Nash contract and repeats. The discrete Nash policy does not stabilize for tested prices, even though every inner Bellman evaluation converges.

| Quoted price | Converged fixed-contract iterations | Independent fixed-contract Bellman residual | Changed contract array entries after 30 policy improvements |
|---|---:|---:|---:|
| 2.5 | 36 | 2.205e-9 | 96 |
| 3.0 | 37 | 1.100e-9 | 178 |

At p=2.5, 96 entries change in each of the last six Nash improvements, a clear numerical contract-policy cycle under the *finite discrete contract menu*. The initial fixed partner distribution is a Dirac mass at k=1.5 and money=1, not a stationary equilibrium population. These facts neither prove nonexistence of monetary GE nor establish multi-equilibrium.

**Implication:** Stage 2-E's price drift and money upper-bound concentration are consistent with fixed grid error, but a separate discrete Nash policy switching problem exists even with fixed prices/partner distribution. Adaptive grids alone will not remove this obstacle. Continuous all-pairs Nash (and its proper global optimality certification) is a prerequisite to any trustworthy full stationary solver.

## Remaining work and honesty gates

Unsolved: original all-pairs continuous Nash with value-policy consistency; high-accuracy fixed-price endogenous-Nash household value fixed point; adaptive *value* grids and original real-wealth KDE representation; endogenous price + stationary wealth/portfolio distribution; independent KKT/Nash/grid convergence; monetary policy and welfare novelty.

The new tests, code, and diagnostics are designed to reject false GE certification. Do not report the fixed-contract Bellman result as an endogenous privately optimal search equilibrium.


## Additional executed experiments: adapted CM-to-DM transition and continuous Nash pairs

After initial conditional CM price 3.007500, the maximum real wealth is 2.0828649274. The original Step 6 formula sets capital upper bound 4.1657298548 and money upper bound 12.5284325384. Population, money, capital moments are unchanged under remeshing to roundoff. A subsequent conditional CM auction clears at price 3.0050785285 with issuer stock one and CM budget discrepancy −2.22e-16. **The extension of old V is merely an initial guess**; Bellman residual 152.8656 and stationary equilibrium remains open.

The preexisting continuous multistart Nash optimizer was applied for every one of 96 match pairs relevant to the support of the conditional CM distribution. Of these, 76 have positive contracts and zero reported local numerical solver failures. Minimum positive participation surplus 0.43883; trading rate 1/3; DM output 0.189329; K before 0.969525, K after 1.090987 after 7% depreciation, nominal money one before and after. The endogenous Bellman update residual remains 153.050, and continuous Nash global optimality has not been proven. Discrete-contract Nash policy cycling is independently established by converged fixed-contract evaluation tests. Neither observation certifies the full source-model stationary equilibrium.
