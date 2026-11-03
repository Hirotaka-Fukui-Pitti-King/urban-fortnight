"""Find coexisting fixed-price private stationary regimes; not monetary GE.

Money clearing must hold separately. This never resets end-of-CM money to the
exogenous stock, which would conceal missing equilibrium price determination.
"""
from pathlib import Path
import json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from molico_grid import Calibration,MonetarySearch

def solve_from_start(model,price,value,distribution,maxit=1650):
    V=value.copy();f=distribution.copy()
    assert abs(f.sum()-1)<1e-12
    for it in range(maxit):
        vv,ff,detail=model.step(V,f,price)
        err_v=float(np.max(abs(vv-V)))
        err_f=float(np.max(abs(ff-f)))
        V=.55*V+.45*vv
        f=.75*f+.25*ff
        if err_v<1e-7 and err_f<1e-8:
            break
    vv,ff,detail=model.step(V,f,price)
    err_v=float(np.max(abs(vv-V)))
    err_f=float(np.max(abs(ff-f)))
    return {'iterations':it+1,'converged':bool(err_v<1e-7 and err_f<1e-8),
            'value_residual':err_v,'distribution_residual':err_f,
            'mean_money':float(f@model.m),'money_excess':float(f@model.m-1.),
            'mean_capital':float(f@model.k),'trades':float(detail['trades']),
            'population_mass_error':float(abs(f.sum()-1)),
            'asset_top_mass':float(f[model.k==model.p.kmax].sum())}

def main():
    price=3.
    model=MonetarySearch(Calibration(nk=5,nm=5,kmax=3,mmax=2))
    uniform=np.ones(model.n)/model.n
    concentrated=np.zeros(model.n);concentrated[2*model.p.nm+2]=1.
    rows=[]
    starts=[('zero_value_uniform',np.zeros(model.n),uniform),
            ('positive_value_concentrated',5*(model.k+model.m/price),concentrated)]
    for name,V,f in starts:
        result=solve_from_start(model,price,V,f)
        result.update(initialization=name,quoted_capital_price=price)
        rows.append(result)
        print(name,result,flush=True)
    assert all(x['converged'] for x in rows)
    assert rows[0]['mean_capital']<.01 and rows[0]['trades']<1e-8
    assert rows[1]['mean_capital']>.9 and rows[1]['trades']>.20
    assert rows[1]['money_excess']>.1
    assert all(x['population_mass_error']<1e-10 for x in rows)
    out=ROOT/'results';out.mkdir(parents=True,exist_ok=True)
    (out/'monetary_multistart.json').write_text(json.dumps({
        'status':'TWO_PRIVATE_FIXED_PRICE_REGIMES_NOT_MONEY_CLEARING_GE',
        'money_supply':1.,'quoted_price':price,'solutions':rows,
        'caveat':'Both private stationarity solutions violate fiat-money clearing; not a multiple-GE theorem.'
    },indent=2)+'\n')

if __name__=='__main__':
    main()
