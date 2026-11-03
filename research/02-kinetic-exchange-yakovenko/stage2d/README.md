# Stage 2-D: Corrected conditional CM monetary auction

**Status: one-period CM money market cleared; fully stationary monetary general equilibrium not obtained.**

The Stage 2-C implementation used a wealth-grid interpolation of the CM value when updating Bellman values and Nash contracts, but used an exact finite portfolio maximum in its distribution update. We corrected this inconsistency. The prior active private fixed-price state exhibits a Bellman update difference of 356.426 in sup norm and 181 changed bilateral Nash contracts when reoptimized. The old code also incorrectly capped a seller's incoming DM money at the maximum allowed *next-period* savings holdings; the enlarged post-DM intermediate state fixes this.

The Stage 2-D price algorithm verifies optimal indifference and mixes **only** truly tied CM policies, preserving issuer supply without money rescaling. Starting with total nominal money one and a nonoptimal continuation-value guess, conditional clearing prices across 5x5, 7x7 and 9x9 grids are 3.110784, 3.053066 and 2.979536. **These are one-period clearing prices, not steady-state prices.** The fully coupled value, price, bargaining and distribution iteration fails to converge to stationary GE; no new macroeconomic mechanism is established.

Execute from the repository root:

    python -m unittest discover -s research/02-kinetic-exchange-yakovenko/stage2d/tests -v
    python research/02-kinetic-exchange-yakovenko/stage2d/scripts/run_stage2d.py
    python research/02-kinetic-exchange-yakovenko/stage2d/scripts/run_stage2d.py --high-grid

See notes/failure_root_cause.md, plan.json and GitHub Actions stage2d.yml. The original PDF was not visually inspected; source indexing was available. All previous research stages are preserved.
