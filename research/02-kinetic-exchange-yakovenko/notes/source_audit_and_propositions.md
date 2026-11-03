Historical Foley/Gallegati primary-source page claims are NOT independently reverified in the current audit; no original PDF hashes or page-image evidence are available.

# Foley, Gallegati, and our Stage 2 propositions

## Source-audited literature

**Foley (1994), Journal of Economic Theory 62:321–345.** Pages 324–326 define acceptable market-transaction offer sets and feasibility. Page 327, Definition 1, defines weighted entropy H(h)=-sum_k w_k sum_x h_k(x)log(h_k(x)), with per-type normalization (N) and aggregate feasibility (F), generating conditional Gibbs-form transaction probabilities. Pages 328–329 establish strict concavity and finite-offer existence/uniqueness of the entropy-maximizing distribution, with an additional interiority condition for finite supporting entropy-price representations (Proposition 2). Pages 330–331 treat statistical excess demand and possible multilateral interactions. Pages 331–334, 342–343 discuss why statistical equilibrium does not automatically attain Walrasian Pareto efficiency. Pages 339–340 explain the entropy price/market temperature analogy. Foley does NOT derive an optimal dynamic Bellman strategy or a Boltzmann equation from individual utility maximization.

**Gallegati, Keen, Lux, Ormerod (2006), Physica A 370:1–6.** Page 3 warns about apparent universal income power laws and misleading graphical distribution fitting. Pages 4–5 emphasize that pure exchange conserves transferred assets but does not produce real income; a productive capitalist economy cannot be explained by exchange-only dynamics. Our model explicitly separates a capital/numeraire production block from matched home-service production and token conservation.

**Canonical alternative:** Lagos and Wright (2005), JPE 113:463–484, provides a decentralized/centralized market search framework. This Stage 2 posted-price model is neither a replication nor a claim of novelty over Lagos–Wright.

## Proposition 1: No voluntary pure transfer

If the only feasible arrangement is (a_i,a_j) to (a_i+d,a_j-d), both continuation values are strictly increasing in own assets, and no other good, contingent promise, service or externality exists, then participation by i requires d>=0, while participation by j requires d<=0. Hence d=0. This does not rule out risk-sharing contracts or trade with additional real goods and services.

## Proposition 2: Restrained stationary optimal monetary search

Households hold m=0,...,M indivisible tokens. Random buyer/seller pairs may meet with probability lambda*w(b,s), bounded above by one. The buyer pays one token for a seller-produced perishable service worth utility b to the buyer and effort cost c to the seller. Both can refuse, and the protocol fixes the token price at one. Stationary token shadow value V(m) implies the buyer gain G_B=b+beta[V(m-1)-V(m)] and seller gain G_S=-c+beta[V(m+1)-V(m)]. Acceptance is optimal if and only if both gains are nonnegative. Conditional on population money shares f, the Bellman equation is V=u_flow(f,chi)+beta*(I+L(f,chi))*V. Rational stationary expectations require f*(I+L)=f and a conserved mean token supply.

For M=5, mean tokens=2, beta=.96, b=5, c=.15, lambda=.45, all eligible trades are accepted: every participation inequality, Bellman equation and token/service market identity passes numerical validation. A **no-trade equilibrium** also coexists: V=0 makes seller acceptance unprofitable for every seller, so no trade occurs and any feasible token distribution is stationary. We do not establish equilibrium uniqueness or selection.

## Proposition 3: Optimal Boltzmann-type gain–loss operator

For a fixed optimal acceptance policy chi(b,s), the expected number of matches per capita is q_(b,s) = lambda*w(b,s)*chi(b,s)*f_b*f_s/2. For every test function phi, the exact weak gain–loss equation is

sum_m phi(m) Q_m(f)
= sum_{b>=1,s<M} q_(b,s) [phi(b-1)-phi(b)+phi(s+1)-phi(s)].

Set phi=1 to prove population mass conservation; set phi=m for exact total-token conservation. The distribution evolves as f_next=f+Q(f). It remains nonnegative if meeting probability is at most one because f_next=f*(I+L) with a stochastic transition matrix. Buyer service consumption equals seller service production and the matched trade count. Capital-sector income and physical production are not subject to this money-conservation rule. The operator is quadratic in f conditional on chi; endogenous policy changes can make the reduced policy-dependent operator more nonlinear. Numerical tests verify Q(f)=L(f)^T f off stationarity.

## Proposition 4: Conditional entropy coincidence and a genuine noncoincidence

Under uniform matching and all-trade acceptance, upward token transitions have rate lambda*(1-f_0)/2, downward transitions lambda*(1-f_M)/2. Detailed balance gives f_(m+1)/f_m=(1-f_0)/(1-f_M), a truncated geometric distribution. This is ALSO the Shannon maximum-entropy distribution over money holdings conditional on fixed mean and mass. It follows from the special matching rates; it is NOT Foley's theorem, whose object is a transaction distribution.

For assortative matching w(b,s)=1+3(b/M)(s/M), lambda=.2, the optimal active stationary token distribution differs from the mean-constrained Gibbs family: D_KL(f||f_ME)=0.0060626683. We also compute an explicitly different **Foley-style comparison** in which money-state types can choose feasible {-1,0,+1} changes subject to token clearing, ignoring matching and role constraints. Actual action probabilities differ: KL=0.19240049 for uniform matching, KL=0.35979716 for assortative matching. Since this comparison changes the offer sets, it does not refute Foley's theorems.

## Explicit boundary of general-equilibrium claims

The Aiyagari capital/numeraire sector was previously solved with optimizing households, production, and competitive asset/labor/goods clearing. A segmented *product* embedding of the present token/service sector is possible only under additively separable preferences, common discount beta, independent idiosyncratic and matching shocks, nonconvertible tokens with no collateral role, and an independent time endowment for home-service production. Under those assumptions, Bellman value functions and stationary distributions factor, with clearing in both sectors. This is a narrow theoretical construction, NOT a numerically solved nonseparable money-capital HANK equilibrium.

Unsolved: optimal bargaining over money prices, token-to-numeraire conversion, portfolio savings interactions, a single labor resource across sectors, partial-trade regimes, and selection among active/no-trade equilibria. Changes in matching intensity or storage capacity can invalidate the full-trade candidate; such cases must be rejected, not reported as valid equilibria.

The full analytical derivation and verification code is included in the Stage 2 reproducibility ZIP, and the source files in this repository contain exact production and token-accounting checks.

## Numerical product-embedding validation

The restricted additive product construction was explicitly executed. With 200 Aiyagari asset nodes, the joint policy-value Bellman residual was 9.22e-12, stationary product distribution sup residual 2.45e-13, relative capital-market error 1.79e-9, goods resource error 7.11e-10, and service output=consumption=0.15200709. The underlying nonconvertible tokens and separate home-service effort guarantee segmentation; these calculations do not establish a general nonseparable HANK plus kinetic exchange model.
