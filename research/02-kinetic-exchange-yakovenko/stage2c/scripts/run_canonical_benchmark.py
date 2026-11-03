"""Execute small text-derived monetary-search candidate; not source-verified GE.

Source verification status for Molico--Zhang: web-indexed text only; PDF pages and equations have NOT been visually verified.
"""
from pathlib import Path
import sys,json,csv,dataclasses,platform
import numpy as np,scipy
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/"src"))
from molico_grid import MonetarySearch,Calibration
out=HERE/"results";out.mkdir(parents=True,exist_ok=True)
rows=[]
for nk,nm,p in ((5,5,.5),(5,5,1.4),(5,5,2.),(7,7,1.4)):
    calibration=Calibration(nk=nk,nm=nm,kmax=3,mmax=2,maxit=325)
    model=MonetarySearch(calibration)
    r,_=model.solve(p)
    status="fixed_price_private_solution" if r["converged"] else "inner_not_converged"
    if (r["converged"] and abs(r["money_supply_residual"])<1e-6
        and max(r["capital_grid_top_mass"],r["money_grid_top_mass"])<.01):
        status="candidate_further_validation_required"
    r.update(status=status,asset_nodes=nk,money_nodes=nm)
    rows.append(r)
    print(f"nK={nk} nM={nm} price={p} inner={r['converged']} money excess={r['money_supply_residual']:.6g}, trade={r['trades']:.6g}",flush=True)
with (out/"price_grid_audit.csv").open("w",newline="") as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]))
    writer.writeheader();writer.writerows(rows)
report={
 "status":"NO_VERIFIED_MONETARY_GENERAL_EQUILIBRIUM",
 "source":"Molico and Zhang November 2005 draft, provisional indexed-text equations (1)-(14); not visually verified",
 "model_claim":"Unverified text-derived finite-grid illustration, NOT literal equation replication or original numerical results",
 "source_calibration":dataclasses.asdict(Calibration()),
 "economic_timing":{
   "DM":"Single coincidence buyer or seller, each 1/N. Money-for-produced-goods Nash trade.",
   "CM":"No production; choose consumption, own-type capital and fiat money jointly.",
   "individual_state":"(own-type productive capital, fiat balances)",
   "price":"price of capital goods in units of fiat money",
   "monetary_market_clearing":"mean normalized end-of-CM money holdings equals one"},
 "numerical_method":{"python":platform.python_version(),"numpy":np.__version__,
                     "scipy":scipy.__version__,
                     "description":"Numba bargaining and mass-preserving post-DM histogram, discrete CM choice",
                     "deviation":"Original 100x100 spline state grid, 10,000-agent simulated density; this 5x5 and 7x7 numerical pilot is much coarser"},
 "grid_and_price_scans":rows,
 "limitations":["No candidate clearing monetary market was certified",
                "Positive stationary trade not established; no monetary equilibrium selected",
                "Grid upper money bound restricts admissible contracts",
                "Nonconvex discrete policies and grid sensitivity",
                "No canonical macro-policy comparative static or novel economic effect inferred"]}
(out/"audit.json").write_text(json.dumps(report,indent=2)+"\n")
assert all(x["invalid_transition_count"]==0 for x in rows)
assert all(abs(x["mass"]-1)<1e-8 for x in rows)
assert not any(x["status"]=="candidate_further_validation_required" for x in rows), "A monetary candidate needs separate full certification"
print("COMPLETE: finite-grid primitive tests executed; no verified money-market-clearing solution.")
