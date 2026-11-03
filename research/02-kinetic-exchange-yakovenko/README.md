# Stage 2: Optimal kinetic monetary exchange

**Status: restricted posted-price search equilibrium implemented and tested; full integrated capital–money general equilibrium NOT completed.**

A buyer voluntarily pays one indivisible token to a seller who supplies one freshly produced perishable service. Both decide optimally whether to participate, considering stationary rational continuation values. Optimal matching produces an explicit quadratic Boltzmann-type gain–loss operator for the endogenous token distribution, preserving household mass and aggregate token holdings. The sold service is produced at an effort cost, so token transfers must not be mistaken for income generation.

Run from the repository root after installing requirements.txt:

1. python -m unittest discover -s research/02-kinetic-exchange-yakovenko/tests -v
2. python research/02-kinetic-exchange-yakovenko/scripts/run_stage2.py --quick
3. python research/02-kinetic-exchange-yakovenko/scripts/run_stage2.py
4. python research/02-kinetic-exchange-yakovenko/scripts/make_figures.py

Full simulation: N=1500,6000,20000; seeds 11,22,33,44; 1800 burn-in periods, 700 measurement periods. The CI workflow stage2.yml reruns tests and a quick independent simulation; generated CSV, JSON and SVG files are uploaded as workflow artifacts.

| Numerical quantity | Uniform matching | Assortative matching |
|---|---:|---:|
| Trades/services per household period | 0.15200709 | 0.09684967 |
| Bellman residual (sup) | 3.55e-15 | 1.78e-15 |
| Stationarity residual (sup) | 6.79e-18 | 6.94e-18 |
| Participation violations | 0 | 0 |
| Token conservation error | below 1e-16 | below 1e-16 |
| KL money holdings versus fixed-mean max entropy | about 0 | 0.00606267 |
| KL transactions versus *different-offer-set* entropy comparator | 0.19240049 | 0.35979716 |

At N=20000 with four seeds, average Wasserstein distance to the stationary money distribution is approximately 0.000903 under uniform meeting and 0.000877 under assortativity.

**Caution:** Foley (1994) characterizes transaction entropy conditional on specified offer sets; none of these comparisons refutes Foley. An active monetary equilibrium coexists with a no-trade equilibrium. Seller/buyer bargaining, fully coupled Aiyagari money-and-capital household optimization, and endogenous conversion price remain open.

See notes/source_audit_and_propositions.md and results/reference_stage2_summary.json.

## Executed segmented product-equilibrium check

A further Python experiment now combines the Aiyagari capital-income stationary measure and optimal-policy value evaluation with the monetary service-search measure under strong separability and nonconvertibility. Stationary joint-distribution sup residual: 2.45e-13. Joint additive Bellman policy-evaluation sup residual: 9.22e-12. Capital-market relative residual: 1.79e-9. Goods-resource residual: 7.11e-10. Token, service and labor resources are accounted separately. Run the additional product_embedding.py tests or scripts/run_product_embedding.py. **Do not interpret this construction as fully integrated capital-money portfolio choice or endogenous service-price bargaining.**
