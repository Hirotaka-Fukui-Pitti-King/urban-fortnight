# Stage 6: Minority Game and Strategic Financial Trading (Challet)

**Status:** Planned — no model solutions or empirical results claimed. **Category:** economic mechanism.

## Research question

Can contrarian strategic trading and price impact in Minority Game environments be represented as optimizing Nash or rational-expectations equilibria?

## Feasibility assessment

Conditional: a congestion/strategic trading equilibrium may exist, but original adaptive score-update algorithms need not satisfy rational expectations; do not equate these two objects.

## Economic mechanisms

- Strategic minority payoff from aggregate order flow
- Heterogeneous information and optimal trading decisions
- Endogenous security prices, market maker and inventory
- Comparison with Challet-style boundedly rational adaptation

## Model objects and equations

**State variables:** traders' beliefs, signals and portfolio states; order imbalance, security returns and market-maker wealth; aggregate security supply and holdings.

- Trader dynamic best responses/Nash conditions
- Asset demand, inventory and security market clearing
- Rational expectations for price mappings conditional on signals
- Balance-sheet transfer and price impact identities

## Nested benchmark

Competitive rational portfolio choice with no strategic crowding; original adaptive Minority Game reported separately

## Mandatory tests

- One-agent deviations do not improve payoffs at claimed equilibrium
- Market-clearing order quantities and dealer inventories
- Trader and dealer cash/asset conservation
- Information sets and forecast calibration consistency
- Distinguish genuine strategic minority mechanism from heuristic learning

## Stage completion criterion

Accept a game-theoretic equilibrium variant if it is nondegenerate; retain original adaptive dynamics only as a clearly labeled relaxation.

**Literature to consult and verify:** Challet, Marsili and Zhang (2005); Minority Game literature; Strategic trading and price impact.

Reports, code versions, seed files and diagnostics should be stored in `results/`. The machine-readable specification is `plan.json`; model decisions and counterexamples are recorded in `RESEARCH.me`.
