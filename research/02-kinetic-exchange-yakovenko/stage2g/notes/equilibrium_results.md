# Stage 2-G numerical results (conditional 3x3 pilot; not stationary GE)

## Result from the local prototype

Model: Stage 2-C inherited calibration (beta=.96, alpha=.36, delta=.07,
eta=5, b=.2, theta=.5, A=1, Ntypes=3); CM saving grid nk=3,
nm=3, capital in [0,3], nominal cash in [0,2]. Quoted capital-per-fiat
price p=2.5 and partner measure equal to a Dirac mass at (k,m)=(1.5,1).
The distribution is NOT assumed stationary and price is NOT endogenously
cleared. No comparison of welfare or monetary policy is made.

The continuous-Nash solver after smooth-branch FOC polishing and root solve
reported the following during execution in the research environment:

| diagnostic | value |
|:--|--:|
| Max absolute endogenous Bellman residual | 9.094947017729282e-13 |
| Max smooth-branch Nash KKT residual | 8.881784197001252e-16 |
| Relevant oriented pairs | 17 |
| Positive trade contracts | 11 |
| Independent 201x201 rectangular search with higher Nash objective | 0 |
| Contract search grid variants checked | 7x7, 11x11, 17x15, 23x19, 31x27 |
| Largest Bellman residual among those variants | 9.094947017729282e-13 |
| 5x5 extension | not converged |
| Stationary distribution | not computed |
| Endogenous clearing price | not computed |
| Stationary monetary GE | **not established** |

The fixed-contract solved residual is different from the endogenous
Nash–Bellman residual; all above residuals were evaluated after renewed
contract optimization. The deterministic benchmark supplies only a lower
bound for the true global Nash objective. It does NOT establish a rigorous
continuous-domain upper bound or identify all CM policy kinks.

## 5x5 failure and numerical gating

A 5x5 trial using a piecewise-affine interpolation of the 3x3 V as an
initial guess decreased its joint residual from approximately 1457.63
to the order of units, but failed the 1e-8 criterion. Repeated root trials
were not promoted to an equilibrium. For a valid stationary solution,
further work must address (i) a nondifferentiable Nash correspondence,
(ii) grid changes and (iii) coherent policy-driven distribution transitions.
The 3x3 private root alone is insufficient to identify stationary GE.

## Reproduction and CI evidence

The committed Stage 2-G files contain an independent executable
3x3 solve, all-pair dense benchmark, source constraints and CI assertions.
GitHub Actions evidence is authoritative only after the run finishes.
No fabricated 5x5 or equilibrium CSV/JSON is provided.
