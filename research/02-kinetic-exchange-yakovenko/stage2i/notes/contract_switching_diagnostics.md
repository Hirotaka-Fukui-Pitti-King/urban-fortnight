# Stage 2-I — Identification gate (initial implementation)

The verified Stage 2-H input is the **intermediate** 5×5 private root at matching multiplier 0.609033203125. No source-rate root is established.

## Why an economically distinct second-best must be defined

A unique optimum of a continuous Nash objective has arbitrarily near feasible contracts with objective values arbitrarily near its maximum. Therefore a literal "second-best distinct continuous contract" is ill-defined without a **positive economic separation radius**. The diagnostic uses a normalized L-infinity contract distance of 1e-3. A near tie in that diagnostic is a *candidate* near tie, not a proved second global maximum.

## What is measured

For all 49 directed pairs involving the fixed partner state 12, the script reoptimizes the inherited corrected **candidate** Nash oracle at the reference V and two symmetric value perturbations in the normalized matching-exposure direction. It records quantity, nominal payment, both surpluses, binding payment status, local piecewise KKT residual, CM portfolio changes and distinct-candidate objective gaps. A CM triangle label is not treated as an economic portfolio difference. Optional global convex audit calls the inherited Stage 2-H solve_pair, but unresolved conic branches are never certified.

These probes do **not** lie on a demonstrated equilibrium branch as lambda changes. They cannot by themselves establish that switching is the cause of the failure at lambda 0.609. There is no fold classification from this script and no full-rate equilibrium claim.

## Literature correction

Borkovsky, Doraszelski and Kryukov (2010), Operations Research 58(4), 1116–1132, DOI 10.1287/opre.1100.0843 (the prior handoff DOI 10.1287/opre.1090.0752 was incorrect). Their natural-parameter homotopy traces smooth solution paths and discusses complementarity reformulations, but is not a theorem of convergence for the present discontinuous Nash policy correspondence.

Gargiani et al. (2022) concern semismooth policy iteration for finite-state/action MDPs. The current Nash-Bellman operator includes endogenous, potentially multiple-valued bargaining and cannot simply import their local quadratic-convergence theorem.
