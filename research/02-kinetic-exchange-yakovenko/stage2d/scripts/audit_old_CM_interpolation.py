"""Reproduce the Stage 2-C active PRIVATE branch, then audit CM interpolation."""
from pathlib import Path
import sys,json
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'stage2c'/'src'))
sys.path.insert(0,str(ROOT/'src'))
from molico_grid import MonetarySearch,Calibration
from exact_core import ExactCMModel

def run():
    m=MonetarySearch(Calibration(nk=5,nm=5,kmax=3.,mmax=2.))
    f=np.zeros(m.n);f[2*m.p.nm+2]=1.
    V=5*(m.k+m.m/3.)
    for it in range(1650):
        vv,ff,detail=m.step(V,f,3.)
        errv=float(np.max(abs(vv-V)));errf=float(np.max(abs(ff-f)))
        V=.55*V+.45*vv;f=.75*f+.25*ff
        if errv<1e-7 and errf<1e-8:break
    if errv>=1e-7 or errf>=1e-8:
        raise RuntimeError(f"Old positive private state failed: {errv}, {errf}")
    oldV,oldF,old=m.step(V,f,3.)
    newV,newF,new=ExactCMModel(m.p).step(V,f,3.)
    result=dict(status="OLD_PRIVATE_FIXED_PRICE_NOT_STATIONARY_GE",
        quoted_price=3.,iterations=it+1,
        old_bellman_residual=float(np.max(abs(oldV-V))),
        old_stationary_distribution_residual=float(np.max(abs(oldF-f))),
        old_fiat_money=float(f@m.m),
        old_money_market_excess=float(f@m.m-1),
        old_capital=float(f@m.k),old_trade_rate=float(old['trades']),
        exact_reoptimization_Bellman_sup_difference=float(np.max(abs(newV-oldV))),
        exact_reoptimization_weighted_difference=float(f@abs(newV-oldV)),
        changed_Nash_contract_pairs=int(np.count_nonzero(old['d']!=new['d'])),
        next_distribution_TV=float(.5*np.sum(abs(newF-oldF))),
        caveat="The old fixed point is for an inconsistent interpolated operator; this comparison is NOT a GE policy counterfactual.")
    out=ROOT/'results';out.mkdir(exist_ok=True,parents=True)
    (out/'old_CM_interpolation_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    assert result['exact_reoptimization_Bellman_sup_difference']>100
    assert result['changed_Nash_contract_pairs']>100
    return result

if __name__=='__main__':
    run()
