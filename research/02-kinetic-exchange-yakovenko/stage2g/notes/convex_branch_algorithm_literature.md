# Stage 2-G: structural replacement for the Nash oracle (literature-audited)

**Status:** Mathematical reduction for the inherited piecewise-affine approximation; **not implemented or executed as a replacement Nash solver yet**. The existing 3x3 root/monotone box certificates do not solve the 5x5 fixed point, nor do they certify stationary GE.

## References and what they do (and do not) justify

- Molico & Zhang (2006), *Monetary Policy and the Distribution of Money and Capital*, Sec. 4 (RePEc https://ideas.repec.org/p/sce/scecfa/136.html): CM value/nonconcavity, bilateral Nash, timing, original wealth-density algorithm. Its earlier version states 100x100 bicubic approximation, 10,000 wealth samples, and Fortran 90 code available from authors by request. Our current triangular approximation is not the original spline.
- Boyd & Vandenberghe (2004), *Convex Optimization*, Sec. 3.2, https://web.stanford.edu/~boyd/cvxbook/: general concavity composition and convex optimization sufficiency. The specific bargaining decomposition below is derived here, not claimed to appear in the book.
- Cai & Judd (2014), *Advances in Numerical Dynamic Programming and New Applications*, Handbook of Computational Economics, https://kenjudd.org/wp-content/uploads/2021/11/2014-Advances-in-Numerical-Dynamic-Programming-and-New-Applications_Handbook-of-Computational-Economics.pdf: approximation and shape/nonconcavity issues.
- Bustamante Amaya (2019), *Essays in Heterogeneous Agent Monetary Economics*, Appendix B.1, https://etd.ohiolink.edu/acprod/odb_etd/ws/send_file/send?accession=osu155447579616523&disposition=inline : deterministic full-distribution transitions as an alternative to match simulation and KDE. Different economic model.
- Chiu & Molico (2021), *Short-Run Dynamics in a Search-Theoretic Model of Monetary Exchange*, Review of Economic Dynamics 42, 133–155, https://doi.org/10.1016/j.red.2020.10.009: numerical methodology in a related money-search economy. **Public Fortran reproducibility package** (2020): https://ideas.repec.org/c/red/ccodes/18-446.html; direct archive https://red-files-public.s3.amazonaws.com/codes/18/18-446/Chiu_Molico_codes.zip. This is NOT the 2006 Molico–Zhang original implementation. Archive source code has not been inspected in this stage.
- Gargiani et al. (2022), *Dynamic Programming Through the Lens of Semismooth Newton-Type Methods*, https://doi.org/10.1109/LCSYS.2022.3181213: convergence theory for finite-state/action MDP Bellman operators, **not** a ready-made convergence theorem for our endogenous bilateral Nash operator.
- CVXPY DCP rules https://www.cvxpy.org/tutorial/dcp/ and solver documentation https://cvxpy.readthedocs.io/en/latest/tutorial/solvers/: a potential implementation route subject to actual DCP and numerical primal-dual checks; no solver result claimed.

## Exact global decomposition relative to the existing interpolant

Let \\mathcal D_h denote one triangular interpolation cell of current post-CM portfolio state (k',m'). On each triangle h, \\widetilde V_h(k',m') is affine. Define
  W_V(w)=max_{h} max_{(k',m') in D_h} {u(w-k'-m'/p)+beta*V_h(k',m')}
over feasible nonnegative consumption.

Fix a buyer b and seller s, and let
  wb=(1-delta)*k_b + m_b/p,
  ws=(1-delta)*k_s + m_s/p,
  cap=A*k_s^alpha.
For buyer triangle h and seller triangle j, introduce (yb, x, a_b, a_s), with
x=d/p, 0<=x<=m_b/p, 0<=y<cap, a_b in D_h, a_s in D_j.
Writing c_b=wb+y-x-k'_b-m'_b/p and c_s=ws+x-k'_s-m'_s/p,
  B_h=u(c_b)+beta*V_h(a_b)-W_V(wb),
  S_j=u(c_s)+beta*V_j(a_s)-W_V(ws)-g(y,k_s).
The source-calibration u(c) is increasing concave for c>=0. With alpha in
(0,1), ell=(y/cap)^(1/(1-alpha)) is convex increasing and
g(y,k_s)=ell/(1-ell) is convex increasing on 0<=y<cap. Therefore B_h and
S_j are jointly concave in all their variables on the affine consumption,
payment, triangle and production-feasibility constraints.

On B_h>0 and S_j>0, theta log(B_h)+(1-theta) log(S_j) is concave by the
nondecreasing concave composition rule. Both participant constraints are
superlevel sets of concave functions and hence convex. Thus, **each fixed
buyer-triangle/seller-triangle pair is a convex optimization problem** (in
the standard equivalent minimization of its negative). First-order/KKT
conditions are *globally sufficient* on that branch when constraint
qualifications hold. Globally maximizing over the finite set of all
triangle pairs recovers the global Nash optimum of the continuous
(y,d) problem with **the inherited piecewise-affine V**, since for
each (y,d) the payoff from each agent's independently optimal CM choice
maximizes their respective surplus, and the Nash product is increasing in
both positive surpluses.

This is NOT a concavity theorem for the original full W globally,
and it does not establish existence, uniqueness, numerical stability or
grid convergence of the coupled Nash--Bellman root.

## Implementable objective without arbitrary capacity cutoffs

For inherited eta>1:
  u(c) = [b^(1-eta) - (c+b)^(1-eta)]/(eta-1)
and with r=1/(1-alpha)>1,
  g(y,k_s) = 1 / [1 - (y/cap)^r] - 1.
The latter is expressible using a convex decreasing reciprocal of a
positive concave denominator. A disciplined convex formulation can use
`power`, `inv_pos` and `log`, subject to each branch passing the library's
actual `is_dcp()` check. A primal feasible solution and primal-dual gap
must be stored. This is a proposed implementation route, not an already
verified package/API result.

At grid nk x nm, there are 2(nk-1)(nm-1) triangles. Brute-force triangle
pair enumeration is O(nk^2 nm^2) *per meeting*, costly at large grids.
Use admissible monotone box/triangle upper bounds to discard inactive
pairs, warm-start from active CM portfolios, and then solve each remaining
convex branch with independent KKT/primal-dual checks. Do not simply claim
that convex decomposition makes the 100x100 original computation cheap.

## Critical missing numerical implication

A <=1e-4 *log generalized-Nash product* gap does NOT in general imply
a <=1e-8 error in individual surplus payoffs or Bellman values.
Different near-optimal Nash contracts can redistribute a substantial
surplus between buyer and seller. Before certifying the endogenous
Bellman fixed point, verify unique outcome (or handle the optimal
correspondence), and recompute the actual Bellman operator using genuinely
globally optimized contracts. Otherwise report the full contract-value
uncertainty, not only the frozen-contract Bellman residual.

## Fixed-price root, then GE

For the private problem at fixed p and partner distribution, matching
opportunity continuation lambda from 0 toward 1/Ntypes is legitimate as a
numerical path, provided each intermediate economy is correctly defined.
At lambda=0 the *private* problem is well-defined, but a positive monetary
*general equilibrium* need not exist there. Preserve this distinction.
Use guarded generalized/semismooth Newton or trust-region solves with
active-set monitoring; no generic convergence theorem applies without
additional regularity.

Only after a 5x5 and subsequent finer-grid independent private root passes
the strict gates: build policy-consistent deterministic probability
transition, solve invariant distribution without clipping or mass loss,
and jointly solve endogenous p and money supply one. Use the same Nash/CM
policies in value and transition operators.
