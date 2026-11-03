# Stage 4: Bouchaud-Inspired Firm Fragility

**Status:** Planned. **Dependencies:** Stage 0, Stage 1, Stage 2, Stage 3.

## Central research question

Can endogenous balance-sheet fragility amplify unemployment, inflation and monetary-policy shocks?

## Economic mechanisms

- Heterogeneous firm balance sheets, borrowing and default
- Hiring, vacancy and output adjustment
- Entry and exit with asset/liability reconciliation
- Calvo pricing coupled to firm financial states

## Economic closure and model caveats

- Keep Calvo as the baseline nominal rigidity; compare any alternative pricing model separately.
- No double-counting firm-price adjustment or bank losses.
- Explicit loan market, firm cash-flow and accounting closure.

## Nested comparators

- baseline with no firm credit friction
- Calvo with credit fragility
- flexible prices with credit fragility

## Acceptance tests

- Loan/default loss identities
- Goods, labor and loan-market clearing
- Firm-price optimality and default accounting
- Switch-off recovery and nonlinear response robustness

## Deliverables

- Heterogeneous-firm transition engine
- Employment, default and inflation responses

**Progression gate:** The numerical equilibrium, accounting identities, convergence checks and nested comparator must be verified before moving to the next stage. Record the code revision, seeds and tolerances in `results/`.

**Literature starting points (verify during implementation):** Gualdi et al. (2015); Bouchaud Mark-0 macro models.
