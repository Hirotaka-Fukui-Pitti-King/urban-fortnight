# Stage 2-B economic audit and theoretical formulas

## Literature and novelty

Lagos and Wright (2005, JPE 113(3):463–484) simplify search/monetary equilibrium by combining decentralized and centralized markets. Under their standard quasilinear CM utility, the money distribution resets by type; this is not suitable for a persistent nondegenerate money-wealth joint distribution without modification. Rocheteau and Wright (2005, Econometrica 73(1):175–202) compare bargaining, competitive and competitive-search price mechanisms.

**Molico and Zhang (2006), *Monetary Policy and the Distribution of Money and Capital*, Society for Computational Economics 136**, already jointly optimize monetary and capital portfolios in a nondegenerate search-money economy. This is the nearest competitor and prevents claiming joint optimization itself as original. Molico (2006, IER 47(3):701–722) endogenizes bargaining quantity/payment and money/price distributions. Aruoba, Waller and Wright (2007), *Money and Capital*, is another direct capital/search connection. Original Foley (1994) entropy is defined over feasible *transaction types*, not over money-holding distributions.

## A joint but incomplete numerical model

Pre-DM state s=(a,m,z). The CM budget is

    c + a' + phi*m' = (1+r)*a + phi*m_after_DM + w*z*(1-q_seller).

The competitive firm sets r=F_K-delta and w=F_L, with Cobb–Douglas output Y=A*K^alpha*L^(1-alpha). A seller's service quantity uses the same time endowment that could have been spent in the centralized labor market; L=E[z*(1-q_seller)].

Centralized decisions (a',m') jointly maximize log(c)+beta E[V(a',m',z')] plus i.i.d. extreme-value portfolio taste shocks, so ex-ante policies are logit. This is NOT the deterministic Aiyagari Euler problem; portfolio taste shocks create positive money demand even if matching is disabled.

The DM generalized Nash contract chooses over feasible discrete (d,q). Buyer surplus is

    Delta_B=xi*log(1+q) + W(a_b,m_b-d,z_b;0)-W(a_b,m_b,z_b;0),

seller surplus is

    Delta_S=W(a_s,m_s+d,z_s;q)-W(a_s,m_s,z_s;0).

Both must be strictly positive; among these the code maximizes Delta_B^eta * Delta_S^(1-eta). No continuous bargaining FOC is computed. Post-DM money is conserved pairwise. For each matched buyer/seller pair the kinetic law has weak form

    <varphi,Q[f]> = (lambda/2)*sum_{b,s} f_b*f_s*chi(b,s) *
                      [varphi(b')+varphi(s')-varphi(b)-varphi(s)].

Population mass, capital and money are conserved in the DM. The subsequent centralized portfolio choice need not clear capital and money markets at the guessed prices.

## Executed economic diagnostics (fixed prices, NOT GE)

Assumed (K,L,phi)=(4.5,0.97,0.65). Bellman residual=9.6598e-9; stationary law=7.56e-16; 1296 mutually acceptable discrete bargaining contracts; minimum buyer surplus=.14992; seller minimum=.07484. DM conserved token and capital changes below 3e-17. Service output=.0887364; market labor diverted=.0839127.

**Market residuals remain enormous**: K_supply-K_demand=-3.8801037, M_demand-M_supply=.197646, L_real-L_assumed=-.0539127, goods Y-C-delta*K=.583097. A nonlinear joint price search attempted many guesses but failed because some inner solves did not converge and the excess demand system remained nonzero. This does not prove non-existence.

Four independent Monte Carlo seeds: average one-step total-variation forecast error, N=2,500: .03227, N=10,000: .01723, N=40,000: .00842. Matching/CM transitions reproduce the conditional stochastic law, not a general-equilibrium allocation.

## Decision rule

Retain these results as a transparent numerical and theoretical failure diagnosis, not a claim of a fully integrated optimizing kinetic GE. Reconstruct Molico–Zhang (2006) with its actual primitives; confirm money essentiality without portfolio taste money utility; clear capital, fiat-money, labor, and goods markets; then derive the Boltzmann weak operator from their optimal trading kernel. Only then compare with Foley's transaction-entropy program on matching-compatible offer sets.
