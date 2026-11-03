# Stage 2-G: Endogenous continuous Nash--Bellman (conditional private problem)

The central numerical object is V=T(V;f,p) with both continuous bilateral
Nash contracts and continuous CM portfolio optimization *reoptimized*
inside T. This work is based directly on the Stage 2-F head
18d1c494a3271b41751ded85ad74da5d03b7968b and preserves the earlier stages.

At p=2.5 and a 3x3 saving grid, the prototype run reached Bellman sup
residual 9.09e-13, maximum smooth-branch KKT residual 8.88e-16,
with 11 positive contracts among 17 relevant directed pairs. A separate
201x201 deterministic benchmark found no contract with a higher objective
than the candidate. This does *not* establish continuous global optimality;
nor does it establish invariant distribution, money price clearing, or GE.
The GitHub Actions workflow reruns these claims independently, and its
actual outcome must be checked before treating them as CI-verified.

See notes/numerical_algorithm.md and scripts/solve_private.py.
