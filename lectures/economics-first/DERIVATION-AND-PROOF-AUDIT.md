# Stage 3 — Derivation and Proof Audit

**Scope:** PR #5, economics-first lectures I–IV. Last updated 2026-11-03. All theorem and equation references below are **specific to the explicit lecture model**, not automatically verbatim propositions in the cited papers.

**Audit definitions:** VERIFIED-DERIVATION = all displayed transformations follow the specified primitives and stated regularity in the lecture; VERIFIED-PROOF = formal statement, assumptions and explicit proof in the lecture; CONDITIONAL = analytic manipulation holds under additional assumptions recorded in the lecture; EXTERNAL = a published theorem is **invoked, not proved**; NUMERICAL = finite approximation verified only by reproducible code; UNRESOLVED = not established. Proof locations refer to the current section headings, which are retained in both Markdown and QMD. This table is a transparency record, **not an automated proof checker**.

## Lecture I — Aiyagari, EGM and Forward Equation

| Lecture | Equation / Proposition | Derived From | Assumptions | Proof Location | Verification |
|---|---|---|---|---|---|
| I | Production factor prices | Competitive firm's profit maximization | CRS Cobb–Douglas, positive factor inputs, price taking | §1, FOCs in K and L | VERIFIED-DERIVATION |
| I | Zero profit | Euler's theorem and factor FOCs | Constant returns | §1, after factor demand | VERIFIED-DERIVATION |
| I | Household Bellman Equation | First-period decomposition of discounted utility | Stationarity, feasible continuation choices, dynamic consistency | §2, dynamic programming principle | VERIFIED-DERIVATION |
| I | Proposition I.1 finite Bellman uniqueness | Sup-norm contraction of Bellman operator | Finite bounded-utility state/action problem, β strictly below one | §2, contraction and Banach proof | VERIFIED-PROOF |
| I | Envelope equation | Differentiate value conditional on a′ and optimality | Differentiability, interior choice, regularity for envelope | §3, two-line derivative | VERIFIED-DERIVATION |
| I | Euler equality | FOC plus next-period envelope | Interior a′, stationary r | §3, FOC/envelope substitution | VERIFIED-DERIVATION |
| I | Proposition I.2 Euler/KKT inequalities | Directional derivatives of constrained concave objective | Upper/lower bounds and feasible positive consumption | §3, proof of sign at each boundary | VERIFIED-PROOF |
| I | Transversality condition | Limiting terminal term in discounted intertemporal perturbations | Nonnegative asset, appropriate integrability and no-Ponzi | §3, explicit sufficient version | CONDITIONAL |
| I | EGM consumption inversion | CRRA marginal utility inverse of Euler | Monotone endo grid, valid interior Euler | §4, EGM derivation | VERIFIED-DERIVATION |
| I | Endogenous asset nodes | Household budget solved for current a | Constant stationary r and w | §4, algebraic formula | VERIFIED-DERIVATION |
| I | Proposition I.3 mass/moment-conserving lottery | Nonnegative adjacent linear weights | Every positive-mass old state and policy target inside new grid | §4, two linear equalities | VERIFIED-PROOF |
| I | Asset grid support inclusion | Reachable a′ and existing distribution support | No clipping or deleting positive mass | §4, numerical conditions | CONDITIONAL |
| I | Distribution pushforward | Law of iterated expectations and policy transition | Exogenous Markov income given current state | §5, test-function derivation | VERIFIED-DERIVATION |
| I | Finite population law of large numbers | Conditional independence | Appropriate LLN, no common shocks | §5 | EXTERNAL |
| I | Continuous HJB | Poisson transition, discount expansion, dynamic programming principle | Smooth interior value or viscosity interpretation | §6, small-time expansions | VERIFIED-DERIVATION |
| I | Generator | Conditional small-time limit | Finite Poisson rates, differentiable test function | §7, limit definition | VERIFIED-DERIVATION |
| I | Kolmogorov Forward / adjoint | Test-function identity and integration by parts | Interior density, correct boundary mass and flux | §7, weak and strong forms | VERIFIED-DERIVATION |
| I | Proposition I.4 probability conservation | Test function φ=1 and generator row sums zero | No unrecorded boundary escape | §7 | VERIFIED-PROOF |
| I | Fokker–Planck diffusion | Ito expansion for log-income OU | Smooth tests, well-defined SDE, boundary flux | §8 | VERIFIED-DERIVATION |
| I | Stationary GE and resource clearing | Firms' FOCs, households' budgets and stationarity | Constant prices, capital and labor market clearing | §9, aggregate budgets | VERIFIED-DERIVATION |
| I | Log–Sum inequality | Normalize a_i,b_i and log x≤x−1 | Nonnegative finite arrays and finite relative entropy | §10, standalone inequality proof | VERIFIED-PROOF |
| I | Proposition I.5 KL contraction | Log–Sum per destination, πP=π | Fixed stochastic kernel, stationary π | §10, summation proof | VERIFIED-PROOF |
| I | Non-reversible counterexample | Directed three-cycle Markov matrix | Stationary uniform π | §10 | VERIFIED-DERIVATION |
| I | Distribution-dependent kernel counterexample | F(p) two-state nonlinear update | F′(1/2)>1, p close to 1/2 | §10 | VERIFIED-DERIVATION |
| I | Wealth Gibbs-law warning | Absence of prior energy or local detailed balance | General Aiyagari equilibria | §11 | VERIFIED-DERIVATION |
| I | Numerical EGM/GE | EGM and invariant distribution from Python | Finite grids and reported calibration | §12 and generate_figures.py | NUMERICAL |

## Lecture II — Random Utility, Gibbs and Phase Transition

| Lecture | Equation / Proposition | Derived From | Assumptions | Proof Location | Verification |
|---|---|---|---|---|---|
| II | Binary social-utility difference | Compare s=+1 and −1 | Symmetric complete-graph influence | §1 | VERIFIED-DERIVATION |
| II | Logit formula | Integral of two independent Gumbel variables | Identical scale τ>0, independent shocks | §2, change of variables | VERIFIED-DERIVATION |
| II | Proposition II.1 conditional tanh mean | 2P(+)-1 | Binary actions, Logit probabilities | §2 | VERIFIED-PROOF |
| II | Asynchronous update Markov chain | One uniform reviser per period | Positive conditional choice probabilities | §3, transition definition | VERIFIED-DERIVATION |
| II | Proposition II.2 Exact Potential | Compute unilateral change of quadratic potential | Symmetric J on complete graph | §3, explicit difference | VERIFIED-PROOF |
| II | Non-symmetric counterexample | Four-cycle cross difference | Two players with J12≠J21 | §3 | VERIFIED-PROOF |
| II | Proposition II.3 Gibbs/detailed balance | Odds ratio + potential differences | Asynchronous Logit, finite irreducible chain | §4, pairwise flow equality | VERIFIED-PROOF |
| II | Microstate count and combinatorial entropy | Binomial counts and Stirling | N large with interior choice fractions | §5 | VERIFIED-DERIVATION |
| II | Partition function for aggregate choices | Sum 2^N microstates by equal S | Homogeneous symmetric utility | §5 | VERIFIED-DERIVATION |
| II | Large-deviation rate function | Max-term bound for partition function | Symmetric complete graph, N→∞ | §6, upper/lower bound | VERIFIED-DERIVATION |
| II | Mean-field self-consistency | First derivative of macro exponent | Interior typical mode | §6, derivative of H_B | VERIFIED-DERIVATION |
| II | Proposition II.4 solution multiplicity | Concavity of tanh(km)-m | h=0, k positive | §7, IVT and derivative proof | VERIFIED-PROOF |
| II | Critical exponent near k=1 | Third-order tanh expansion | k→1+ | §7 | CONDITIONAL |
| II | Spinodal thresholds | Inversion h(m) and turning points | J>τ, local stationary solutions | §8 | VERIFIED-DERIVATION |
| II | Social multiplier | Implicit Function Theorem | Denominator nonzero | §8 | VERIFIED-DERIVATION |
| II | Finite-N susceptibility | First/second derivatives of log Z_N | Finite N, τ>0 | §9 | VERIFIED-DERIVATION |
| II | Metastable transition-time scaling | Reversible-chain large deviations | Additional mixing/hitting-time assumptions | §9 | EXTERNAL |
| II | Welfare vs potential | Sum individual bilateral social utilities | Deterministic direct spillovers | §10, compare factor of 2 | VERIFIED-DERIVATION |
| II | Reflection problem | Average structural equation within group | Linear social effects with common group shock | §11 | VERIFIED-DERIVATION |
| II | Finite-N Gibbs plot | Exact binomial weighted normalization | N=100 educational case | §12 and generate_figures.py | NUMERICAL |

## Lecture III — Monetary Search and Kinetic Theory

| Lecture | Equation / Proposition | Derived From | Assumptions | Proof Location | Verification |
|---|---|---|---|---|---|
| III | Matching rate λN/2 | N(N−1)/2 Poisson pair clocks | Independent clocks, each rate λ/(N−1) | §2 | VERIFIED-DERIVATION |
| III | Buyer/seller surplus | Value if trade minus value if decline | Continuous-time payoff at trade time | §3 | VERIFIED-DERIVATION |
| III | Proposition III.1 no-trade transfer | Strict monotonic value and no service | Pure zero-sum money transfer | §3 | VERIFIED-PROOF |
| III | Policy evaluation Bellman | Small-time Poisson DPP | Fixed one-token contract, stationary f | §4 | VERIFIED-DERIVATION |
| III | Nash objective and participation | Bilateral Nash solution | Feasible positive surplus or no trade | §5 | VERIFIED-DERIVATION |
| III | Proposition III.2 Nash FOCs | Differentiate log Nash product in q and d | Positive surpluses, differentiable V, interior | §5 | VERIFIED-PROOF |
| III | Trading kernel | Bargaining and acceptance map, including no-trade | Tie-breaking and admissible contracts | §6 | CONDITIONAL |
| III | Boltzmann weak form | Finite-N empirical-measure jump and random matching | Conditional chaos, regular limit kernel | §6 | CONDITIONAL |
| III | Strong gain–loss operator | Sum indicators of post and pre states | Finite tokens and fixed one-token policy | §7 | VERIFIED-DERIVATION |
| III | Proposition III.3 conservation | Tests φ=1 and φ=m | Trade conserves pairwise money | §7 | VERIFIED-PROOF |
| III | Birth/death rates | Probability opposite role is feasible | All-trade acceptance, uniform matching | §8 | VERIFIED-DERIVATION |
| III | Proposition III.4 truncated geometric | Zero boundary flux, geometric recursion, monotone mean | 0<mean<M, irreducible active chain | §8 | VERIFIED-PROOF |
| III | Entropy maximizing exponential | Lagrange FOCs, entropy Hessian | Finite set, interior feasible mean | §9 | VERIFIED-DERIVATION |
| III | Fokker–Planck limit | Taylor expansion with drift/variance scaling | Small trades, high frequency, negligible third moments | §10 | CONDITIONAL |
| III | Proposed money–capital general equilibrium | Sequential DM and CM budget and markets | Must complete household choice and aggregate RE | §11 | UNRESOLVED |
| III | Fixed-price token calibration | Bilateral gains, stationarity, Bellman and money | Limited discrete contract | §12 and generate_figures.py | NUMERICAL |

## Lecture IV — Learning, Networks, Entropy, Random Matrices and HANK

| Lecture | Equation / Proposition | Derived From | Assumptions | Proof Location | Verification |
|---|---|---|---|---|---|
| IV | Minority aggregate loss | Sum u_i=−a_i A/N over i | Specified minority proxy payoff | §1.1 | VERIFIED-DERIVATION |
| IV | Two-strategy representation | Algebraic identity with ω and ξ | Binary strategy choices | §1.2 | VERIFIED-DERIVATION |
| IV | Predictability/volatility split | Conditional variance decomposition | Uniform public states | §1.2 | VERIFIED-DERIVATION |
| IV | Spin-style coupling J_ij | Expand squared conditional A | Fixed strategy table and mean-choice approximation | §1.3 | CONDITIONAL |
| IV | Generating functional derivatives | Differentiate finite-path generating function | Bounded paths, finite observation horizon | §1.4 | VERIFIED-DERIVATION |
| IV | Heterogeneous optimal demand | Differentiate mean-variance objective | Quadratic risk penalty, interior choice | §2.1 | VERIFIED-DERIVATION |
| IV | Asset price clearing | Sum heterogeneous demand | Exogenous stock supply | §2.1 | VERIFIED-DERIVATION |
| IV | Logit strategy switching | Gumbel-derived discrete choice | Heterogeneous forecast-score utilities | §2.2; Lecture II §2 | VERIFIED-DERIVATION |
| IV | Cobb–Douglas input demand | Firm unit-cost minimization and FOCs | CRS and positive inputs | §3.1 | VERIFIED-DERIVATION |
| IV | Proposition IV.1 Leontief inverse | Geometric matrix series and spectral radius | ρ(A)<1 | §3.2 | VERIFIED-PROOF |
| IV | Aggregate shock variance | v^TΣv linear algebra | Given linear network reduced form | §3.3 | VERIFIED-DERIVATION |
| IV | Foley type-specific Gibbs trade shares | Entropy Lagrange FOC | Feasible interior solution, finite offer sets | §4.1 | VERIFIED-DERIVATION |
| IV | Proposition IV.2 entropy uniqueness | Strict concavity on convex feasible set | Positive type masses and feasible optimum | §4.1 | VERIFIED-PROOF |
| IV | Marchenko–Pastur limiting law | Established random matrix concentration theorem | High-dimensional i.i.d. noise and moment assumptions | §5.1 | EXTERNAL |
| IV | MP spectral support endpoints | Discriminant of limiting resolvent equation | Given MP fixed-point, positive variance | §5.2 | VERIFIED-DERIVATION |
| IV | Calvo CES price index | Final-good cost minimization | ε>1, competitive final-good producers | §6.1 | VERIFIED-DERIVATION |
| IV | Reset-price FOC | Infinite discounted profit maximization | Price rigidity with independent Calvo hazard | §6.2 | VERIFIED-DERIVATION |
| IV | Price dispersion law | Partition price cohorts and CES demand | Identical resetters, constant ε | §6.3 | VERIFIED-DERIVATION |
| IV | NKPC linearization | Zero-inflation Taylor approximation, price index and FOC | No indexation, stationary discount β | §6.4 | CONDITIONAL |
| IV | HANK distribution linearization | Product rule μ_{t+1}=μ_t P_t | Differentiable Markov kernel | §6.5 | VERIFIED-DERIVATION |
| IV | Sequence-space aggregate response | Implicit linearization of F(X,Z)=0 | D_XF invertible | §6.5 | CONDITIONAL |

## 5. Primary-literature provenance — original claims versus lecture constructions

| Original paper | Verified original research question and source | Lecture construction and non-equivalence |
|---|---|---|
| [Aiyagari 1994](https://doi.org/10.2307/2118417) | Precautionary aggregate saving, income and wealth inequality with incomplete markets | Lecture I additionally demonstrates fixed-kernel KL contraction: **not** an original Aiyagari proposition |
| [Huggett 1993](https://doi.org/10.1016/0165-1889(93)90024-M) | Equilibrium safe interest rate with incomplete insurance and riskless asset | Does not use production capital clearing of Aiyagari |
| [Achdou et al. 2022](https://doi.org/10.1093/restud/rdab002) | Continuous-time HJB–KF, poverty policy, analytic special case, uniqueness conditional on EIS | Lecture derives smooth interior HJB–KF; does **not** reprove paper's existence/uniqueness theorems |
| [Carroll 2006](https://doi.org/10.1016/j.econlet.2005.09.013) | Endogenous gridpoint solution method | Lecture shows CRRA inversion and lottery numerical approximation, not original-paper quantitative replication |
| [Blume 1993](https://doi.org/10.1006/game.1993.1023) | Stochastic strategy revision, equilibrium selection on a lattice | Lecture II complete-graph symmetric potential is a specified pedagogical case |
| [Brock–Durlauf 2001](https://doi.org/10.1111/1467-937X.00168) | Social-interaction Logit, multiple self-consistent mean choices, identification | Lecture II combines that choice structure with a separate asynchronous reversible process |
| [Green–Zhou 2002](https://doi.org/10.1111/1468-0262.00315) | Divisible money, double auction, evolving distribution, continuum of single-price equilibria | Fixed one-token service matching is **less general**, not a new general money-price theory |
| [Aruoba–Waller–Wright 2011](https://doi.org/10.1016/j.jmoneco.2011.03.003) | Money and capital with stochastic trading, bargaining and centralized/decentralized market structure | Lecture III money-capital GE is schematic and not a completed benchmark |
| [Toscani–Brugna–Demichelis 2013](https://doi.org/10.1007/s10955-012-0653-0) | Boltzmann-type goods exchange from Cobb–Douglas and Pareto-improving trades, quasi-invariant limit | Boltzmann derivation from voluntary trade is **not novel** |
| [Foley 1994](https://doi.org/10.1006/jeth.1994.1018) | Entropy of distributions over admissible transactions in large economies | It is **not** maximizing the entropy of stationary token holdings |
| [Calvo 1983](https://doi.org/10.1016/0304-3932(83)90060-0) | Staggered nominal price setting | Lecture derives a standard simplified reset-price and NKPC special case |
| [Auclert et al. 2021](https://doi.org/10.3982/ECTA17434) | Sequence-space solution and estimation for heterogeneous agent GE | Lecture presents only generic Jacobian linearization, not full efficient implementation |

## 6. Numerical and PDF evidence, limitations and remaining work

- The Python figures represent **pedagogical finite-model calibrations**. EGM upper-grid feasibility is enforced within policy iteration and a separate Bellman-value optimization verification would strengthen the results. Grid-sensitivity checks and the no-clipping distribution-lottery moment condition are central.
- The GitHub Actions workflow checks markdown/QMD parity, residual tests, Quarto HTML/Typst builds, raw TeX and orphan PDF pages; all pages should be inspected as images after rendering. These are **artifact QA**, not formal proof of mathematics.
- No automated parser can decide whether arbitrary unlabelled equations have a correct mathematical proof. The structural audit script can ensure all *declared propositions* are found in lecture sources with nearby proof markers, as well as flag undecided audit statuses; a human mathematical audit remains indispensable.
- The lectures presently derive full key results but the publisher-equivalent 30–60 page target per section is an **editorial target, not a verified completion status**. The four separate model classes in Lecture IV especially contain externally invoked theorems and merit independent multi-session volumes if every advanced result must be proved from first principles.
- No modifications are authorized to research/stage2b-integrated-monetary-ge. No PR merge was performed solely on the basis of this audit.
