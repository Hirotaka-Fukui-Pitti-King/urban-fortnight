# Stage 2-E — Numerical findings and failure of stationary GE gate

Executed 2026-11-03, Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, Numba 0.65.1. Six local economics tests passed.

## Conditional continuous joint CM optimization

The continuation value is **piecewise affine on triangles** in next capital and fiat-money savings. Given real budget wealth w, within a triangle the objective is utility of unspent wealth plus an affine function of savings. At fixed portfolio cost, the linear continuation value achieves its maximum on the triangle boundary; all candidates therefore lie on triangle edges. Along each edge with cost slope Dcost and continuation slope DV, the derivative is

    F'(t) = -Dcost*(c(t)+b)^(-eta) + beta*DV.

The algorithm checks all feasible edge end points and the analytic stationary coordinate. This is a **global optimum for that particular interpolated V**, not a proof of global optimality for the original smooth continuous-value problem. Tests independently inspect 200x40 feasible two-dimensional deviations at four wealths and verify budget feasibility.

Initial population has total fiat money exactly 1 and mass concentrated at the middle savings state. Continuation V=5*(k+m/3)+0.02*sin(k)+0.003*sin(2m) is deliberately **not a Bellman fixed point**.

| Grid | Conditional CM p | End money | End K | Resource error | Bellman sup | Distribution sup |
|---|---:|---:|---:|---:|---:|---:|
| 5x5 | 3.0112500000 | 0.9999999999999999 | 1.0843862137 | 0 | 153.1684046 | 0.5526071 |
| 7x7 | 3.0103125000 | 1.0000000000000000 | 1.0843874600 | 0 | 153.2431128 | 0.7309184 |

CM near-optimal correspondence threshold 5e-8; no ex-post nominal-stock renormalization. These two coarse grid results do NOT establish grid convergence. A 9x9 pilot exceeded the computational budget and has not been validated. A joint price/value/distribution iteration was explored but did not reach the required small Bellman and distribution residuals. The scripted reproducible gate performs one iteration and explicitly reports nonstationarity; no positive stationary monetary GE has been found.

## Conditional continuous bilateral Nash

One supported match at 5x5, conditional p=3.01125: output y=0.6535636809538037; fiat payment d=1 (cash budget binds). Buyer gain 1.545682679056597, seller net gain 0.9030054361157394, seller effort 0.40957743919351713. Multistart SLSQP log Nash value 0.1667194853511511 versus best coarse candidate 0.11582103108020697. Buyer/seller participation, seller labor and buyer cash feasibility pass. **This does not prove a global Nash optimum over a nonconcave domain**, and the full law still uses discrete contracts.

## Research decision

DM preserves fiat money and population mass and produces output from seller labor/capital. CM's continuous joint portfolio policy conserves the aggregate goods/financial budget at quoted price. Yet the current experiment does NOT simultaneously satisfy stationarity, optimized continuous bargaining in all meetings, or high-grid numerical accuracy. Thus there is no claim about monetary policy, welfare, a stationary kinetic operator or a new mechanism beyond Molico--Zhang.
