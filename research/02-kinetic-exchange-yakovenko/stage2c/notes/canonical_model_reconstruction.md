# Stage 2-C: primary source, exact modeling differences, and executed numerical audit

**Status 2026-11-03: original-equation finite-grid pilot executed. NO monetary stationary general equilibrium found or claimed.**

## Original manuscript source

Molico and Zhang, *Monetary Policy and the Distribution of Money and Capital*, November 2005 draft, SCE (2006) No. 136.
Source: https://citeseerx.ist.psu.edu/document?doi=e6826088816be6c1deea19bd1f677f16d190316f&repid=rep1&type=pdf

- pp. 6–8, environment: N>=3 household types. Type i stores/consumes own good and produces type i+1 from labor and type-i capital. Output y=A*k^alpha*l^(1-alpha), depreciation delta. Fiat money is not directly consumed. DM has random matches; centralized capital market has **no production**. This is substantively different from the Stage 2-B representative Cobb–Douglas firm plus centralized labor sector.
- pp. 9–11, eqs. (1)–(7): V before DM, W before CM, joint k',m' saving choice subject to normalized real wealth c+k'+m'/p_k=kbar+mbar/p_k (mu=0).
- pp. 11–12, eq. (8): generalized Nash chooses output y and money payment d, with buyer gain W(m_b-d,(1-delta)k_b+y)-W(m_b,(1-delta)k_b) and seller gain W(m_s+d,(1-delta)k_s)-W(m_s,(1-delta)k_s)-v(y,k_s).
- pp. 12–14, eqs. (9)–(14): matching-induced distribution transition then CM portfolio mapping. Recursive equilibrium needs all value/optimality conditions and end-of-CM normalized fiat money **market clearing E[m']=1**.
- pp. 15–16, original algorithm: 100x100 money/capital interpolating grid, sample of 10,000 households, nonparametric wealth densities, iterative price and asset-portfolio clearing, parallel Fortran solver. Our 5x5/7x7 pilot is not a replication.
- p. 17, Table 1: N=3, beta=0.96, eta=5, b=0.2, alpha=0.36, A=1, delta=0.07, theta=0.5. The small numerical grids and solver tolerances in this project are NOT in that table.

## Implemented Python equation subset

The new source file src/molico_grid.py defines U(c)=[(c+b)^(1-eta)-b^(1-eta)]/(1-eta); seller g(l)=l/(1-l); the DM Cobb–Douglas production and labor cost; and CM joint choice of capital, fiat money and consumption under a single wealth budget. There is no Gumbel portfolio shock and money has no direct utility. A finite contract menu approximates original *continuous* Nash bargaining. Buyers receive output as a storable own-type consumption/capital good; seller productivity depends on seller's own capital. We use 1/N buyer and 1/N seller contact probabilities.

The DM measure is propagated by mass splitting on a post-trade goods grid that is enlarged above the next-period savings grid: newly produced goods are **not cut off** at the savings-grid boundary. The maximum money grid, however, restricts admissible transfers. The CM then maps wealth back into next-period portfolio choices and consumption. At nonclearing quoted prices, the repeated CM mapping can change the aggregate nominal money balances, and thus is NOT itself a feasible monetary general-equilibrium transition.

Exact tested one-period accounting (at zero inflation/transfers):
C + K_next + M_next/p_k = (1-delta)*K_initial + Y_DM + M_initial/p_k.
Only after normalized money clearing and K stationarity does this simplify to Y_DM=C+delta*K. There is no competitive representative firm's K demand or market-wage condition in Molico-Zhang, so imposing those equations from the old Aiyagari model would be an economic error.

## Executed tests and result

Seven local Python/Numba unit and economic checks pass: type specialization, labor/c utility, discrete Nash voluntary participation, matching money/mass/DM-goods conservation, CM asset/consumption budget identity, explicit failure of monetary clearing, and no direct money preference shocks.

| Grid (capital x money) | p_k | Private fixed point | End-CM money demand | Excess relative to supply=1 |
|---|---:|---|---:|---:|
| 5x5 | 0.5 | converged | approximately 0 | -1.0000 |
| 5x5 | 1.4 | converged | approximately 0 | -1.0000 |
| 5x5 | 2.0 | converged | 0.333804 | -0.666196 |
| 7x7 | 1.4 | **not converged** | 0.526249 (invalid) | -0.473751 (invalid) |

All four cases conserve computational distribution mass; the last case is not a valid stationary individual solution. The *first three private problems* are not positive-stock monetary equilibria either: nominal fiat supply cannot clear.

The original model admits monetary and potentially nonmonetary regimes; the coarse iteration is vulnerable to a nontrading/low-wealth attractor. These failures are not an impossibility theorem. Money essentials must also be distinguished from its store-of-value role in the assumed-price partial problem; the lambda=0 test alone is not a complete general-equilibrium result.

## Next necessary implementation and gate

A legitimate next solver must clear the normalized CM money supply **jointly** with stationary V, bargaining rules, and population measure. Continuous choice/contract interpolation, exact feasible policy matching and numerical continuation in price and trade intensity are prior to any large-scale grid experiment. Because the original source uses a specialized no-CM-production economy, it does NOT mechanically nest the standard Aiyagari economy when meetings vanish. Do not introduce Aiyagari production in CM and call the resulting solution the original Molico-Zhang model.

No new Boltzmann-type monetary GE, particle-level validated positive stationary equilibrium, policy comparative static, or additional novelty claim is supported by this pilot.


## Multistart test of monetary branch selection (executed)

Using the **same** original-equation finite 5x5 portfolio grid, capital price p_k=3, and exactly the same household fundamentals and contract menu, we varied only initial continuation values and initial household portfolios. From V0=0 and uniform f0, the privately consistent distribution converged after 327 iterations to capital ≈0, fiat holdings 0.343056, and essentially no trade. From V0=5*(k+m/3) and f0 concentrated at k=1.5, m=1, the same conditional private Bellman–population equations converged after 1,249 iterations to mean capital 0.986579, mean fiat holdings 1.183183 and successful trade rate 0.241363. Bellman residuals are <1e-7 in both cases. **Neither clears normalized money supply one**, so this establishes distinct fixed-price privately stationary regimes under an incomplete price closure, **not multiple monetary general equilibria**. Reproduce using scripts/run_monetary_multistart.py, results/reference_multistart.json, and the executed CI artifact monetary_multistart.json. This finding demonstrates why a single V=0 initialization and naive monotone money-demand Brent root are not sufficient.
