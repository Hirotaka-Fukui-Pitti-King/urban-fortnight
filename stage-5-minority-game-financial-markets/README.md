# Stage 5: Minority Game and Financial Markets

**Status:** Planned. **Dependencies:** Stage 0, Stage 1, Stage 2, Stage 3, Stage 4.

## Central research question

How do adaptive trading and price impact affect financial volatility and monetary transmission?

## Economic mechanisms

- Challet-style adaptive minority-game strategies
- Order imbalance and market-maker price impact
- Inventory and liquidity dynamics
- Portfolio feedback to household and firm decisions

## Economic closure and model caveats

- Asset prices are distinct from Calvo-set goods prices.
- Trade financing, dealer inventory and asset supply must clear.
- Include matched fundamental and non-strategic trading benchmarks.

## Nested comparators

- no adaptive trading
- fundamental trader benchmark
- minority-game strategies

## Acceptance tests

- Order and inventory reconciliation
- Trader wealth and dealer P&L identities
- Asset market clearing
- Random seed robustness and switch-off recovery

## Deliverables

- Verified adaptive trading market
- Financial stress and monetary transmission comparisons

**Progression gate:** The numerical equilibrium, accounting identities, convergence checks and nested comparator must be verified before moving to the next stage. Record the code revision, seeds and tolerances in `results/`.

**Literature starting points (verify during implementation):** Challet, Marsili and Zhang (2005); Bouchaud price-impact literature.
