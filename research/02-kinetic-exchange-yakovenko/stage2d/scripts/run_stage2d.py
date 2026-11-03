"""Run conditional money-clearing and failed stationary fixed-point diagnostics."""
from pathlib import Path
import sys,json,csv,time,platform,argparse
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'stage2c'/'src'))
sys.path.insert(0,str(ROOT/'src'))
from molico_grid import MonetarySearch,Calibration
from exact_core import ExactCMModel
from clearing import clear_cm_price,stationary_attempt

def run(high_grid=False,stationary_steps=30):
    tic=time.monotonic()
    rows=[]
    for n in ([5,7,9] if high_grid else [5,7]):
        model=ExactCMModel(Calibration(nk=n,nm=n,kmax=3,mmax=2))
        f=np.zeros(model.n);f[(n//2)*n+n//2]=1.
        V=5*(model.k+model.m/3)
        clearing=clear_cm_price(model,V,f,bracket=(.5,10),tolerance=1e-11)
        rows.append(dict(grid=n,
            price=clearing.price,money_initial=clearing.incoming_money,
            money_next=clearing.next_money,money_gap=clearing.next_money-1,
            demand_below=clearing.money_lower,demand_above=clearing.money_upper,
            indifference_regret=clearing.inner_optimality_gap,
            mixing_probability=clearing.mixing_probability,
            next_capital=clearing.next_capital,production=clearing.production,
            consumption=clearing.consumption,budget_residual=clearing.budget_residual,
            stationary_GE=False))
        print('ONE_PERIOD',n,clearing.price,clearing.next_money,
              clearing.budget_residual,flush=True)
    model=ExactCMModel(Calibration(nk=5,nm=5,kmax=3,mmax=2))
    f=np.zeros(model.n);f[12]=1.
    V=5*(model.k+model.m/3)
    old=MonetarySearch(model.p)
    ov,_,od=old.step(V,f,2.7)
    nv,_,nd=model.step(V,f,2.7)
    state,_=stationary_attempt(model,V,f,max_iter=stationary_steps,
         init_price=3.11,damping_value=.20,damping_distribution=.15)
    if state['status'].startswith('CANDIDATE_'):
        raise RuntimeError('possible stationary candidate needs additional validation')
    result=dict(
        status='ONE_PERIOD_CM_CLEARED_NO_VERIFIED_STATIONARY_MONETARY_GE',
        source='Molico-Zhang equation-level finite grid; NOT original numerical replication',
        source_verification='indexed text available; no original PDF visual page audit',
        python_version=platform.python_version(),
        initial_distribution='all mass at middle money-and-capital state, M=1',
        continuation_guess='5*(capital+money/3); not an optimized Bellman solution',
        price_grids=rows,
        interpolation_repair=dict(
            old_vs_exact_Bellman_update_sup_at_p2_7=float(np.max(abs(nv-ov))),
            changed_Nash_contracts=int(np.count_nonzero(nd['d']!=od['d'])),
            old_seller_top_money_trades=int(np.count_nonzero(
                od['d'][:,model.m==model.p.mmax])),
            new_seller_top_money_trades=int(np.count_nonzero(
                nd['d'][:,model.m==model.p.mmax]))),
        stationary_attempt=state,
        issuer_balance_artificially_renormalized=False,
        economic_caveat='Money clearing conditional on a guessed V and initial f is not stationary GE',
        executed_seconds=time.monotonic()-tic)
    folder=ROOT/'results'
    folder.mkdir(parents=True,exist_ok=True)
    (folder/'stage2d_diagnostics.json').write_text(json.dumps(result,indent=2)+'\n')
    with (folder/'one_period_price_grid.csv').open('w',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig,ax=plt.subplots(figsize=(6,4))
        ax.plot([x['grid'] for x in rows],[x['price'] for x in rows],marker='o')
        ax.set(xlabel='Grid nodes per portfolio dimension',
               ylabel='Conditional one-period CM clearing price',
               title='Not a stationary general equilibrium')
        fig.tight_layout()
        (folder/'figures').mkdir(exist_ok=True)
        fig.savefig(folder/'figures'/'one_period_CM_prices.svg')
        plt.close(fig)
    except ImportError:
        pass
    print('RESULT',result['status'],state['status'],state['iterations'])
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--high-grid',action='store_true')
    p.add_argument('--stationary-steps',type=int,default=30)
    a=p.parse_args()
    run(a.high_grid,a.stationary_steps)
