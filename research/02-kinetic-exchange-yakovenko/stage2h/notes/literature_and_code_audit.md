# Stage 2-H — Direct source and publicly available Fortran audit

## Primary paper (distinct from Chiu–Molico code)

Molico and Zhang, *Monetary Policy and the Distribution of Money and
Capital*, November 2005 public manuscript, Section 3 equations (1)–(14)
and Section 4 numerical protocol. Manuscript:
https://citeseerx.ist.psu.edu/document?doi=e6826088816be6c1deea19bd1f677f16d190316f&repid=rep1&type=pdf

- Equation (8) has d in [0,m_b], y in [0,A k_s^alpha].
- CM value equation (2) optimizes next-period money and capital under
  the budget constraint; bargaining surpluses use W after DM trades.
- The model's payoff is *not* the Lagos–Wright quasilinear CM.
- Original numerical program: sample of wealth portfolios, nonparametric
  density estimation, 100x100 bicubic value approximations, MPI-style
  Fortran 90 parallelization. Section 4 says the 2005 original program
  could be requested from the authors. It has not been obtained.
- This public manuscript appears dated November 2005; references to the
  2006 conference version must distinguish manuscript dates.

## Chiu and Molico (2021), different economy

*Short-Run Dynamics in a Search-Theoretic Model of Monetary Exchange*,
Review of Economic Dynamics 42:133–155 (2021).
Public code archive: https://red-files-public.s3.amazonaws.com/codes/18/18-446/Chiu_Molico_codes.zip
Code registration: https://ideas.repec.org/c/red/ccodes/18-446.html
Public paper: https://www.econstor.eu/bitstream/10419/241214/1/swp2020-48.pdf
Appendix B discusses quadrature/distribution dynamics, value iteration,
and avoiding policy interpolation *within the Bellman quadrature*.
The source separately constructs bargaining policy grids for moment updates.

## Executed source audit on GitHub Actions

Stage 2-H `.github/workflows/stage2h.yml` downloads, hashes and opens
the ZIP in GitHub Actions, `scripts/audit_related_fortran.py`.
The archive was successfully obtained in the first Stage 2-H run;
SHA-256:
`deae7bbd3f24167367fa4716b15621ffa9e33ec9fc841f9f68e24c655171c014`.
Size: 18,082,836 bytes. 211 decoded Fortran and text files examined.
Unlike past Stage 2-G notes, this is an **actually retrieved and
inspected source archive**, not just a verified existence link.

Key paths inspected from **Steady State/src_code/**:

- `bargprob.f90`: `BP` bargaining objective, `dBP` first derivative,
  `d2BP` second derivative.
- `dq.f90`: one-dimensional bargaining payment `d` is solved by the
  `C2_sc_r_uf` optimizer using those three functions. Production
  quantity `q` is obtained from an inverse cost function; this
  simplification depends on *Chiu–Molico's* bargaining condition.
  Its payment upper bound uses `MIN(x1+mu,MMAX-x2)`; such a
  numerically limited seller money holding must **not** be imported
  as an economic feasibility constraint into Molico–Zhang (2006).
- `mm2020.f90`: iterates value and density parameters with spline
  approximation, MPI broadcasts and moment updates; explicitly
  constructs a DGRID of payment policies to speed up moment
  calculation. The convergence clause requires minimum 3000
  iterations and relative max value difference under 1e-3 percent,
  but that criterion **does not** validate the 5x5 private
  Nash–Bellman residual of the capital model.

This code is useful as numerical design evidence, *not a directly
portable replication* of the original capital-and-money economy.

## Numerical method decision

The strongest applicable method is a finite set of convex Nash
subproblems for the inherited piecewise-affine CM value approximation,
with mathematically admissible branch bounds, plus safeguarded
matching-rate continuation for the fixed-price private root. The
finite-MDP convergence theory for standard semismooth Newton cannot
be applied as a blanket theorem to this endogenous bargaining
operator. No Nash policy from a related model is substituted for
the original economic decision rules.

## Source verification limitations

The original CiteseerX PDF is indexed and available in web extracted
text; direct page-screenshot requests failed because of source fetch
errors. No page-image verification is claimed. The Fortran archive
audit succeeded on GitHub Actions; the container environment had no
external DNS and was not the execution source.
