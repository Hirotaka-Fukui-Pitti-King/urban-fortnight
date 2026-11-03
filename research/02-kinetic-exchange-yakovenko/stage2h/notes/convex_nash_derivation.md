# Stage 2-H — Convex branch decomposition of source-model Nash (with qualified accuracy)

## Precise approximation and original model

The original Molico–Zhang (2005 manuscript, Section 3, equation 8) maximizes the generalized Nash product with 0 <= nominal payment d <= m_b, 0 <= output y <= A k_s^alpha; effort ell=(y/(A k_s^alpha))^(1/(1-alpha)) and the disutility g(ell)=ell/(1-ell) diverges at unit labor. Positive-output optimum is in 0<y<A k_s^alpha. Outside option is nontrade. The 3x3 and 5x5 experiments fix p=2.5 and an exogenous Dirac matching-partner measure. These are **not** stationary monetary GE calculations.

The **numerical approximation** considered here uses V interpolation affine on triangles D_h in nonnegative (k',m') space. This is not the 100x100 bicubic approximation described in Molico–Zhang Section 4. For each real wealth w, define

  W_h(w) = max_{a=(k',m') in D_h, 0<=k'+m'/p<=w}
             [u(w-k'-m'/p)+beta V_h(a)]
  W(w) = max_h W_h(w).

For a fixed pair of CM triangles (h,j), let a_b in D_h and a_s in D_j, x=d/p, 0<=x<=m_b/p and 0<=y<Ak_s^alpha. Define posttrade consumptions
  c_b= w_b+y-x-k'_b-m'_b/p, c_s=w_s+x-k'_s-m'_s/p.
Holding the outside W(w_b), W(w_s) fixed, define

  B_h=u(c_b)+beta V_h(a_b)-W(w_b),
  S_j=u(c_s)+beta V_j(a_s)-W(w_s)-g(y,k_s).

Enforce c_b,c_s>=0 and B_h,S_j>0. With theta in (0,1), maximize
  theta log(B_h)+(1-theta) log(S_j).

## Proof of concavity and global decomposition

Assume u'(c)>0,u''(c)<0 on c>=0, beta>0, 0<alpha<1, 0<theta<1, and A,k_s>0. Write cap=A k_s^alpha and r=1/(1-alpha)>1. Then

  g(y,k_s) = [ (y/cap)^r ]/[1-(y/cap)^r]
           = inv_pos(1-(y/cap)^r)-1.

The map y -> (y/cap)^r is convex and increasing on y>=0. Hence
y -> 1-(y/cap)^r is concave and positive for y<cap. inv_pos is
convex and decreasing, so its composition is convex. Thus -g is concave.
The posttrade budget variables c_b,c_s are affine in
(y,x,a_b,a_s), V_h and V_j are affine within their respective
triangles, and u of affine consumption is concave. Consequently
B_h and S_j are jointly concave. The superlevel constraints B_h>=0
and S_j>=0 define convex feasible sets. The log is concave increasing,
and theta log(B_h)+(1-theta) log(S_j) is concave on positive B_h,S_j.

For any fixed (y,x), a_b and a_s enter distinct surpluses, and the
Nash objective is increasing in each positive surplus. Therefore
maximizing over a_b and a_s yields W(w_b+y-x), W(w_s+x), respectively.
Taking the maximum over all finite (h,j) gives exactly the Nash
maximum for the continuous (y,d) contract space **conditional on the
piecewise-affine-grid approximation**. This is a finite collection of
convex optimization problems; no global concavity of W itself is
required. KKT conditions are sufficient per branch when appropriate
constraint qualifications hold.

The existence of a well-defined positive objective must be tested.
If none of the branches has strictly positive B_h,S_j, the outcome
is no trade with y=d=0. Multiple globally optimal branches may
produce different bilateral surplus allocations; this possibility
must be handled as an optimal correspondence, not silently assigned
a unique policy.

## Safe pruning

For buyer triangle h, buyer surplus is at most
  W_h(w_b+cap) - W(w_b).
For seller triangle j, seller surplus is at most
  W_j(w_s+m_b/p) - W(w_s),
since the production cost is nonnegative. Both bounds use monotonicity
of W_h in wealth, independent of concavity. For strictly positive
bounds, the weighted log sum gives a valid upper bound on the branch's
Nash objective. A feasible incumbent with a higher objective rules
out the branch from global-maximizer consideration. **Do not add an
arbitrary numeric labor/output upper bound** to make pruning easier.

## Numerical limits and acceptance

The Python `convex_nash.py` implementation constructs DCP problems
using CVXPY and solves with Clarabel. Each reported candidate is
independently evaluated using the Stage 2-E exact-on-affine-grid
CM value. Successful CVXPY DCP/solver status and consistency with a
monotone rectangle upper bound are numerical evidence, not an
outward-rounded interval-arithmetic proof. The code keeps
`global_proof=False` and flags any subproblem failure.

A small maximum log Nash objective gap does not automatically imply
small errors in B and S separately or in the Bellman mapping. The
private root is accepted only after recomputing actual contractual
surpluses for every relevant pair, constructing the full Bellman
operator, and verifying its 1e-8 sup residual. Higher resolution
grid convergence is another independent requirement.

### References

- Molico and Zhang (2005/2006), *Monetary Policy and the Distribution of Money and Capital*, Sections 3–4.
- Boyd and Vandenberghe (2004), *Convex Optimization*, Section 3.2 on composition.
- CVXPY, *Disciplined Convex Programming* documentation: https://www.cvxpy.org/tutorial/dcp/
