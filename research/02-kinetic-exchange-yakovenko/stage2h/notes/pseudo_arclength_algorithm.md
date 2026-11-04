# Stage 2-H — Bordered pseudo-arclength continuation of 5×5 private fixed point

## Structural reason

The previous solver roots R(z,lambda)=0 for sequential fixed matching rates lambda. It can stall at a fold or at a discontinuous Nash branch change. That failure alone does not imply nonexistence.

Here z is the vector of 24 relative values V_i-V_0 at fixed p=2.5 and exogenous matching distribution concentrated at (k,m)=(1.5,1). Define

    R_i(z,lambda)=T_lambda([0,z])_i-T_lambda([0,z])_0-z_i,

where T_lambda=(1-lambda)T_0+lambda*T_1, T_0 is no matching and T_1 the paper's original matching chance 1/Ntypes. This is a family of *private* problems, not monetary general equilibrium.

Given neighboring valid points (z0,lambda0) and (z1,lambda1), compute a normalized secant direction t in scaled coordinates, then predict (z_pred,lambda_pred). The corrector jointly solves 25 equations:

    R_i(z,lambda)=0 for i=1,...,24;
    t_z'[(z-z_pred)/scale]+t_lambda(lambda-lambda_pred)=0.

This bordered system can traverse an ordinary fold where d(lambda)/ds=0 provided the bordered Jacobian remains full rank. It cannot cure discontinuity of the Nash correspondence, and does not itself prove existence.

Reference: Allgower and Georg (1990), *Numerical Continuation Methods: An Introduction*, Springer. https://doi.org/10.1007/978-3-642-61257-2

## Verification and certification gates

The Python script 'scripts/solve_5x5_pseudo_arclength.py' reoptimizes endogenous continuous Nash contracts on every residual trial, initially through the fast Stage 2-G *candidate* oracle. The separate unit test uses the known fold z²+lambda=1, starting at (.8,.36) and (.6,.64) and crossing the lambda=1 turning point; that is a validation of the arclength corrector, not of the monetary model.

All accepted and rejected corrector points, residuals, matching-rate turning indicator, and the highest reached multiplier are saved in 'results/pseudo_arclength_5x5.json'. If matching multiplier 1 is reached, this is still only a candidate: independent source-rate Bellman evaluation and all-pair convex global Nash reoptimization must pass before the 5×5 private root can be certified. It is not a stationary GE because neither money price nor invariant distribution is solved.

If correctors fail, investigate whether Nash's optimal correspondence has multiple outcomes; a low Nash-product gap need not bound the buyer/seller surplus split. Do not infer nonexistence solely from a failed smooth-root algorithm.

## Executed economic result (Actions run 41744277837)

The 5x5 economic path was actually evaluated in Python on GitHub Actions for 630.96 seconds. The seed points at matching multiplier 0, .05, .15, .30 and .55 all passed relative Bellman residual 1e-7; the last has residual 3.9822e-9. Bordered pseudo-arclength steps advanced to maximum accepted matching multiplier 0.6047853110 with augmented residual 1.3457e-8. Subsequent smaller-step correctors did not pass the convergence threshold; the final rejected candidate had residual 6.9888e-5. No ordinary turning point was observed: the measured matching component of the continuation secant remained positive. Source multiplier 1 was **not** reached, and no original-market equilibrium was found. The failure is consistent with an abrupt Nash/CM policy selection change or solver inaccuracy; it is not evidence of pure-equilibrium nonexistence. Full trace: https://github.com/Hirotaka-Fukui-Pitti-King/urban-fortnight/actions/runs/41744277837 . Persistent compact result: stage2h/results/5x5_pseudo_arclength_reference.json.
