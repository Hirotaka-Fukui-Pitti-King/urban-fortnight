# Stage 2-G: Source-aligned endogenous private equilibrium

## Scope and status

This stage implements the continuous Nash fixed-point system at **fixed**
capital-per-fiat price and **fixed** partner distribution. It does not certify
stationary monetary GE. The first experiment uses a 3 x 3 saving-state grid,
a degenerate partner distribution at (k,m)=(1.5,1), and p=2.5.

## Original timing and economic constraints

Money is a *nominal quantity*, p is *goods per unit money in the paper's
capital-price convention* (as implemented in the inherited code by m/p).
After DM: real wealth w=(1-delta)k+m/p plus consumption-good gains, conditional
on buyer status; seller receives money and incurs production effort. The
buyer receives y and pays d, the seller produces y and receives d.

The original continuous Nash feasible set is 0<=d<=m_b, 0<=y<=A*k_s^alpha,
with production effort l=(y/(A*k_s^alpha))^(1/(1-alpha)) and
g(l)=l/(1-l), which diverges at l=1. Consequently a positive optimum
must have y<A*k_s^alpha. The Stage 2-E arbitrary factor 0.985 on output
capacity has been **removed in the Stage 2-G solver**.

For w_b=(1-delta)k_b+m_b/p and w_s=(1-delta)k_s+m_s/p:
  B(y,d)=W(w_b+y-d/p)-W(w_b)
  S(y,d)=W(w_s+d/p)-W(w_s)-g(l(y,k_s)).

Outside option y=d=0 gives zero bilateral surplus. Positive trade is
accepted only if both surpluses are strictly positive; otherwise no trade.

Because W is increasing in wealth, B>=0 implies d/p<=y. That condition
reduces the actual search to 0<=x=d/p<=min(m_b/p,y), without changing
economic feasibility for mutually acceptable trades. No finite upper bound
on the seller's *post-DM* nominal money is imposed.

At differentiable interior optima and with x=d/p, write
B_W=W'(w_b+y-x), S_W=W'(w_s+x), and v_y as marginal production disutility.
The Nash first-order conditions in (y,x) are:

  theta*B_W/B -(1-theta)*v_y/S = 0,
  -theta*B_W/B +(1-theta)*S_W/S = 0.

At the binding nominal-payment upper bound d=m_b, the second derivative
with respect to x must be >=0. The output derivative remains zero if output
is interior. Where W has kinks, these are conditional smooth-branch
conditions; the code's derivative is an envelope derivative based on the
selected optimal CM portfolio and must not be represented as a full
Clarke-subgradient certificate at ties.

## Numerical algorithm

1. Stage 2-E's exact-on-affine-triangle CM portfolio problem evaluates W.
2. Profile the real payment x for every candidate y; enumerate discrete
   sample local maxima and refine via bracketed golden search.
3. Profile output y; enumerate local maxima and refine the best candidates.
4. Polish the continuous solution with quantity FOC on d=m_b, or the
   two-dimensional FOCs at an interior contract. Reject objective-decreasing
   polished candidates.
5. Recompute Nash policies inside each evaluation of T(V), *not* once at
   the start of policy iteration.
6. Exploit translation covariance T(V+c)=T(V)+beta*c. Root solve
   T(V)_i-T(V)_0=V_i-V_0 in relative values; recover the level using
   T(V)_0/(1-beta).
7. Independently recompute original unnormalized T at the recovered level
   using a denser contract search. Reject if sup norm exceeds 1e-8.
8. Independently benchmark each relevant Nash pair with a dense rectangular
   search. This **only bounds the candidate from below** and does not
   prove the global optimum over the continuous contract space.

The returned same y,d arrays are suitable for both the DM Bellman expectation
and future DM distribution transition. A fully coupled stationary
distribution and CM money clearing are not implemented in Stage 2-G yet.

## Reproduction

  python -m unittest discover -s research/02-kinetic-exchange-yakovenko/stage2g/tests -v
  python research/02-kinetic-exchange-yakovenko/stage2g/scripts/solve_private.py
  python research/02-kinetic-exchange-yakovenko/stage2g/scripts/validate_nash.py

The hard acceptance gate is 1e-8 independent Bellman residual plus <=1e-6
interior/active-face KKT residual. No fixed-price solution should be called
a stationary GE. A 3x3 solution does not establish grid convergence.
