# Stage 2-B: Updated novelty and code audit (2026-11-03)

## Source and GitHub provenance

The literature review, branch comparison and BibTeX were copied *verbatim* from main to lectures/literature on this research branch, without merging unrelated main history. The comparison note's observation that Stage 2-B was identical to Stage 2 at commit 9716f377 is **historical, now outdated**. Stage 2-B has an independent joint-portfolio and discrete-bargaining implementation and Draft PR #4. This note supersedes only that dated implementation-status claim.

## Critical papers and exact overlap

- Chakrabarti and Chakrabarti (2009), Physica A 388:4151-4158, DOI 10.1016/j.physa.2009.06.038: consumer optimization yields gas-like asset-exchange equations and the paper discusses global goods price formation. Optimization-to-kinetic exchange is not new.
- Toscani, Brugna and Demichelis (2013), Journal of Statistical Physics 151:549-566, DOI 10.1007/s10955-012-0653-0: Cobb-Douglas/Edgeworth-box voluntary two-good trade yields a nonlinear Boltzmann equation. The result is not the same as a joint intertemporal Bellman monetary-production GE, but voluntary trade plus a kinetic equation alone is not novel.
- Green and Zhou (2002), Econometrica 70:929-969, DOI 10.1111/1468-0262.00315: divisible money, double auction, infinite-horizon anonymous matching, endogenous money distributions and a continuum of single-price equilibria. Random matching, prices, and money distributions already coexist.
- Aruoba and Wright (2003), JMCB 35(6):1085-1105: introduces neoclassical production, labor and capital in monetary search and proves a conditional money/nonmoney dichotomy. Factor production plus search is not new.
- Aruoba, Waller and Wright (2011), JME 58:98-116, DOI 10.1016/j.jmoneco.2011.03.003: capital, monetary trade, bargaining, and quantitatively important inflation-investment results. Even nonzero money-capital interaction alone is not novel.
- Molico (2006), IER 47:701-722, DOI 10.1111/j.1468-2354.2006.00393.x: endogenous bargained goods and money amounts, money and price distributions, and nonlinear inflation/welfare effects.
- **Molico and Zhang (2006)**, SCE paper 136, November 2005 draft: specialized producers and storers, anonymous decentralized goods trade, optimal joint money-capital holdings, uninsured trading and production risk, nondegenerate wealth distributions, and monetary policy effects on capital, consumption and welfare. This is the most direct economic competitor. Primary draft: https://citeseerx.ist.psu.edu/document?doi=e6826088816be6c1deea19bd1f677f16d190316f&repid=rep1&type=pdf
- Farmer (2024), NBER w32836, DOI 10.3386/w32836: monetary/nonmonetary equilibria and stability in an incomplete-markets heterogeneous-agent model.

These claims are supported by source reading and publication abstracts. We do not claim a theorem-by-theorem full audit of every original article.

## Correct scientific contribution claim

The revised research question is whether the **endogenous joint liquidity distribution and bilateral trade kernel** generate an economic prediction beyond canonical monetary-search GE, not whether that kernel can be written as Q[f,f]. The same distribution operator can generally be written in Markov or gain-loss form; rewriting it is not a new economic mechanism. A distinctive result must identify new comparative statics or theorem relative to Molico-Zhang and Aruoba-Waller-Wright, with the same preferences, production technology, bargaining institution and equilibrium pricing.

## Actual model status: partial dynamic optimization, NOT general equilibrium

At assumed prices Kd=4.5, Ld=.97 and phi=.65, the finite-state joint portfolio and discrete Nash bargaining model reaches Bellman sup residual 9.66e-9 and invariant-distribution residual 7.56e-16. However:
- Ks-Kd = -3.880104;
- Md-Ms = +0.197646;
- Ls-Ld = -0.053913;
- Goods residual = +0.583097, implied by capital/labor excesses to 1.67e-15 (not a fourth independent condition).

The zero-meeting counterfactual still holds positive fiat money because random portfolio-choice shocks make money itself desirable. Therefore this model does **not** establish essentiality of money arising solely from search. The discrete contract menu does not establish continuous Nash first-order optimality.

## Newly executed kinetic-feedback ablation (conditional only)

At the above fixed-price stationary reference f*, keep bargaining contracts and portfolio policies fixed. Let B(f,g) be the ordered-pair collision operator with pair mass lambda*f_b*g_s/2 and exact matched-pair asset/token conservation. Then Q(f)=B(f,f), DQ(f*)h=B(h,f*)+B(f*,h). Compare it to Qref(f)=[B(f,f*)+B(f*,f)]/2, which conserves the same quantities and equals Q(f*) at the reference, but suppresses part of partner-distribution feedback off the reference.

Perturb a-money covariance across four states by mass 0.01 without altering a or m marginal means. Derivative finite-difference sup error 8.78e-13; one-step full-versus-reference distribution TV distance 0.00236518; next capital difference 0.000110128. Neither prices nor future optimizing policies are recalculated, so this is **not** a GE capital effect or monetary transmission estimate. The code tests invariance and exact collision identities.

## Why not report a market-clearing root?

Additional executed price scan at L=.94, phi=.8:
- K_guess=1.0: inner converged, Ks=9.99970 and asset-grid top mass=0.999915.
- K_guess=2.0: inner failed, Bellman residual=.04124 and top mass=0.999673.
- K_guess=2.8: inner failed, Bellman residual=.000959 and top mass=.72459.
- K_guess=3.3: inner not converged at tolerance 1e-8.
- K_guess=4.0: inner converged, Ks=.58766, far below the guessed K.

Asset-grid upper-bound artifacts and failed inner fixed points make an outer price root unreliable. Do not infer nonexistence from numerical failure; nor truncate the grid or let the outer solver accept unconverged inner residuals.

## Necessary next model and novelty gate

First reconstruct Molico and Zhang's actual household, matching, capital-production, money-essentiality, price and issuer accounts; verify a stationary equilibrium on a converged joint (a,m,z) grid with all independent markets clearing. Then implement a well-defined distribution-feedback ablation **at the same primitives and equilibrium prices**, solve both equilibria including rational policy adjustment, compare capital, consumption and welfare, and seek an economically distinct theorem or comparative static absent from the original monetary-search literature. If only an equivalent forward operator is obtained, claim a numerical method rather than a new economic channel. New Keynesian rigidities remain out of scope.
