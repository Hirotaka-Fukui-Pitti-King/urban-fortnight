# Stage 2-E — Primary-source algorithm audit

**Scientific status: conditional CM policy/price calculations executed; no verified stationary monetary GE.**

Primary: Molico and Zhang, *Monetary Policy and the Distribution of Money and Capital* (Nov. 2005 draft, SCE 2006 no. 136).
Source indexed PDF: https://citeseerx.ist.psu.edu/document?doi=e6826088816be6c1deea19bd1f677f16d190316f&repid=rep1&type=pdf

The original Section 4, printed pp. 14–16, describes: (1) 10,000 sampled household asset portfolios entering CM; (2) 100x100 money/capital grid with **bicubic spline interpolation** of the before-DM value; (3) endogenous CM fiat-money-clearing price with entrant wealth distribution and prior V held fixed; (4) CM value W evaluated over a wealth interval tied to the maximum entrant wealth; (5) updating portfolio policies and a wealth-distribution representation; (6) adapting money/capital grid bounds to wealth and price; (7) updating the Bellman map and bilateral Nash contracts; (8) sampling decentralized buyer/seller meetings to update the wealth distribution. The paper explicitly cautions that V and W need not be strictly concave and that policy decisions can have discontinuities. Source authors indicate Fortran 90 implementation is available **from the authors by request**. Public repository availability is unverified.

Differences: Stage 2-E uses a **5x5/7x7 triangular piecewise-affine value approximation**, globally optimal CM saving conditional on that interpolant, deterministic mass-preserving joint (k,m) histograms, a fixed portfolio-saving ceiling with an expanded intermediate DM receiving grid, and a finite Nash contract mesh **for the all-households distribution operator**. A continuous multistart SLSQP Nash optimum is computed for one representative active match only, not for the entire aggregate kernel.

The original PDF was accessed via indexed text, but the PDF screenshot interface returned cache errors for the mathematical pages. Page typography/equations are therefore NOT claimed to have been visually checked. Stage 2-E is neither the original 100x100/10,000-agent replication nor a verified full monetary GE.
