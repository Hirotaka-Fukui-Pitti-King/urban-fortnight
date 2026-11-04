# Stage 2-I: original matching-rate fixed-policy and Nash-update experiment

**Executed:** GitHub Actions [41897630094](https://github.com/Hirotaka-Fukui-Pitti-King/urban-fortnight/actions/runs/41897630094). Original matching parameter is held at lambda = 1, with fixed p = 2.5 and Dirac partners at state 12; this is not monetary general equilibrium.

The inherited conditional root at lambda = 0.850006103515625 has relative Bellman residual 4.55e-13, but is rejected by all-pair global Nash (independent residual 0.414118; [run 41772366085](https://github.com/Hirotaka-Fukui-Pitti-King/urban-fortnight/actions/runs/41772366085)). Explicit branch-switch correctors from the 0.85 value failed for the genuinely different (19,12) branch: residual 0.0095739. Replacing the (23,12) contract converged to the *old* contract, not a new branch. [Run 41896987528](https://github.com/Hirotaka-Fukui-Pitti-King/urban-fortnight/actions/runs/41896987528).

A distinct full-rate Howard-type experiment then solved the **frozen-contract** Bellman equation to an independently evaluated sup norm 9.458744898438454e-11 in 602 iterations, but its candidate Nash policies produced a source-rate Bellman sup 4.4260123. Across two initializations and 30 safeguarded policy-update iterations per initialization, the best corrected-fast Nash residual was **0.43575461162163265**, nowhere near the required 1e-8. Global 49-pair reoptimization was intentionally **not** reported for this unconverged candidate.

## The precise mathematical distinction

For any *fixed feasible* contract policy tau, the induced original-rate Bellman map is a discounted Markov decision evaluation map. With a Dirac counterparty and Ntypes=3, it is a nonnegative weighted average of three CM values with weights (1 - 2/3, 1/3, 1/3) and net production cost independent of V. Since each CM operator is beta-Lipschitz in the value-function sup norm, the fixed-policy Bellman map is a beta contraction. Thus this subproblem **has a unique fixed value**. The demonstrated convergence of that subproblem does not imply convergence of the endogenous Nash-policy operator: optimal policy changes and CM kinks can disrupt smooth Newton and Howard switching.

**Not established:** existence or nonexistence of a pure original-rate 5x5 fixed point; convergence of global Nash policy iteration; full-rate equilibrium; steady-state general equilibrium.

Do not extrapolate these results to a certified 49-pair Nash Bellman residual. Further work would have to solve the global-Nash *correspondence* jointly with the Bellman update, including non-smooth CM branches. More iteration budget for the same corrected-fast oracle is not a principled substitute.
