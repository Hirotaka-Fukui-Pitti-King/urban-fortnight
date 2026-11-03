# Stage 2-B: Joint Capital–Money Bargaining — **GENERAL EQUILIBRIUM OPEN**

This directory contains an **executed fixed-price prototype**, not a completed general equilibrium. It preserves the earlier Stage 2 product construction and tests.

Households simultaneously choose next-period capital and nominal token holdings from a single CM budget. A seller's DM service effort reduces labor available to the same competitive Cobb–Douglas sector. In meetings, both buyer and seller may refuse and choose a utility-surplus-maximizing payment **d** and service quantity **q** via generalized Nash bargaining over a **finite contract grid**. Matching generates a derived gain–loss operator, not an imposed random transfer.

**Fixed-price validation:** at assumed (K,L,real token value)=(4.5,0.97,0.65), Bellman sup residual=9.66e-9 and distribution residual=7.56e-16, with 1296 acceptable bilateral state contracts and exact nominal token conservation in DM. **But GE fails:** capital excess=-3.880104, money demand minus supply=+0.197646, labor mismatch=-0.053913 and goods-resource residual=+0.583097. The outer price solve did not converge to an economically verified solution.

Moreover, numerical Gumbel portfolio preference shocks create **money demand even when all monetary exchange is turned off**. Thus money essentiality is not established; this is not a replication of canonical monetary-search theory or the original deterministic Aiyagari model.

### Execute

From repository root:

\`\`\`bash
python -m pip install -r requirements.txt
python -m unittest discover -s research/02-kinetic-exchange-yakovenko/stage2b/tests -v
python research/02-kinetic-exchange-yakovenko/stage2b/scripts/run_stage2b.py --pop 20000
\`\`\`

Seven Stage 2-B numerical/economic tests pass locally. Particle one-step distribution total variation errors average approximately 0.03227 (N=2500), 0.01723 (N=10000) and 0.00842 (N=40000), with four seeds for each N. They validate the law of motion conditional on assumed prices, **not an equilibrium**.

**Literature priority:** Molico and Zhang (2006), *Monetary Policy and the Distribution of Money and Capital*, is already an optimizing money-and-capital portfolio distribution model. Molico (2006), *The Distribution of Money and Prices in Search Equilibrium*, endogenizes monetary exchange and trade prices. The next step is to reconstruct that canonical environment rather than claim novelty for joint money-capital optimization. Read \`notes/MAIN_FINDINGS.md\`.

Full outputs: \`results/fixed_price_diagnostics.json\`, GitHub CI artifacts and user-facing local reproducibility bundle.
