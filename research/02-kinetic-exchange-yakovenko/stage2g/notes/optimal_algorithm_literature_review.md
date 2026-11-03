# Stage 2-G: Literature-based numerical replacement (November 2026)

## Primary references

1. Molico and Zhang (2006), *Monetary Policy and the Distribution of
Money and Capital*, source manuscript sections 3--4:
https://citeseerx.ist.psu.edu/document?doi=e6826088816be6c1deea19bd1f677f16d190316f&repid=rep1&type=pdf
The authors expressly warn that V and W need not be strictly concave,
and that the CM portfolio policy can be discontinuous; their full
algorithm uses 100x100 bicubic splines and simulated wealth portfolios.

2. Hoang Tuy (2000), *Monotonic Optimization: Problems and Solution
Approaches*, SIAM J. Optim. 11(2), 464--494,
https://doi.org/10.1137/S1052623499359828 .
Provides general deterministic global methods for monotonic structures.
Our explicit rectangle bounds below are derived specifically for
Molico--Zhang; they are NOT claimed to be a result of Tuy's paper.

3. Gargiani et al. (2022), *Dynamic Programming Through the Lens of
Semismooth Newton-Type Methods*, IEEE Control Systems Letters 6,
2996--3001, https://doi.org/10.1109/LCSYS.2022.3181213 .
Their policy-iteration results concern finite-state/action MDPs. The
endogenous bilateral bargaining operator here is NOT automatically a
finite MDP Bellman maximum. Thus no direct convergence theorem transfers.

4. Bustamante Amaya (2019), *Essays in Heterogeneous Agent Monetary
Economics*, Ohio State dissertation, Appendices B.1/C.1:
https://etd.ohiolink.edu/acprod/odb_etd/ws/send_file/send?accession=osu155447579616523&disposition=inline
Uses explicit deterministic distribution transitions in search monetary
models, replacing simulation and kernel-density estimation. This is an
algorithmic analogue, not a replication of Molico--Zhang's exact economy.

## Exact source-model change of variables (zero money growth baseline)

Write x=d/p and w_b=(1-delta)k_b+m_b/p,
w_s=(1-delta)k_s+m_s/p. Then
B(y,x)=W(w_b+y-x)-W(w_b)
S(y,x)=W(w_s+x)-W(w_s)-v(y,k_s).
The source capacity is 0<=y<Ak_s^alpha for strictly positive trade,
0<=x<=m_b/p, and the zero-surplus outside choice (0,0).
W is strictly increasing in w since u is strictly increasing; hence
B>=0 requires x<=y. v is increasing in y.

### Exact nested one-dimensional profile

Set z=y-x (buyer's net real wealth increment), with z>=0 for a
participating buyer. For each fixed z, B(z) is constant and monotone.
The seller's maximizing production quantity solves
  S_star(z)=max over y in [z,min(Ak_s^alpha,z+m_b/p)]
            {W(w_s+y-z)-W(w_s)-v(y,k_s)}.
The payment is reconstructed as x=y-z and d=p*x. Then
  max_{z>=0} [W(w_b+z)-W(w_b)]^theta
            [max(0,S_star(z))]^(1-theta).
This is EXACT algebraic dimension reduction and remains valid
for nonconcave W. BOTH one-dimensional maximizations must be global;
blind bounded scalar minimization is insufficient if nonunimodal.

### Independent monotone branch-and-bound

For a rectangle y in [yl,yu], x in [xl,xu], the exact upper bounds are
  B_up=W(w_b+yu-xl)-W(w_b),
  S_up=W(w_s+min(xu,yu))-W(w_s)-v(max(yl,xl),k_s).
The tightened S_up exploits x<=y. If either <=0 the entire rectangle
contains no strictly positive contract. Otherwise the log Nash
objective is upper bounded by theta*log(B_up)+(1-theta)*log(S_up).
Any evaluated participating contract provides a global lower bound.
Partition boxes in decreasing order of their upper bound. Stop when
global_upper-best_lower<=epsilon, NOT just when KKT residual is small.

Stage 2-G src/nash_global_bounds.py implements a *floating-point*
version of this rectangle certificate, and tests it on an analytic
linear W case and a nonconcave increasing W case. It reports UNRESOLVED
if the box budget runs out. Its guarantee is conditional on correct
monotone W and exact arithmetic; strict mathematical certification
requires outward-rounded interval bounds that also enclose W evaluation
error, and grid convergence for the source continuous economic model.

## Nonlinear fixed-point solver after Nash certification

The root residual must call the global Nash oracle for every relevant
pair, reusing policies in the DM distribution transition. A low KKT
residual alone is unacceptable. Start from the existing 3x3 private root,
certify every positive pair (and rule out missed positive matches), then
run the source-exact private Bellman residual. Resolve active-set changes
using safeguarded Broyden/semismooth Newton and locally damped
continuation. Only after this has passed on 5x5 and richer grids should
price and invariant distributions be joined.

The earlier 3x3 root is NOT yet a certified source-model private
equilibrium; it passed FOC and dense-grid checks only. Do not identify
absence of a higher-scoring 201x201 grid point as a global proof.
