"""Execute finite-grid continuous CM and conditional money-market audits.

The continuation value here is deliberately NOT a stationary Bellman solution.
"""
from pathlib import Path
import sys,json,csv,platform
import numpy as np
import scipy,numba
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'stage2c'/'src'))
sys.path.insert(0,str(ROOT/'src'))
from molico_grid import Calibration
from continuous_core import ContinuousModel,evaluate_auction
from nash_continuous import continuous_nash
from auction import clear_price,stationary_iteration

def run():
    out=ROOT/'results';out.mkdir(parents=True,exist_ok=True)
    rows=[];demand=[]
    for n in (5,7):
        m=ContinuousModel(Calibration(
            nk=n,nm=n,kmax=3.,mmax=2.,y_choices=4,d_choices=5))
        f=np.zeros(m.n);f[(n//2)*n+n//2]=1.
        V=5*(m.k+m.m/3.)+.02*np.sin(m.k)+.003*np.sin(2*m.m)
        a=clear_price(m,V,f,price_hint=3.,
             prices=[2.7,2.8,2.9,3,3.1,3.2],opt_tol=5e-8)
        rows.append(dict(asset_nodes=n,money_nodes=n,
            CM_price_conditional=a.price,issuer_stock_initial=a.money_start,
            end_CM_money=a.money,CM_money_residual=a.money-1.,
            CM_regret_bound=a.regret_bound,budget_residual=a.goods_residual,
            next_capital=a.capital,trade_rate=a.trade_rate,
            next_distribution_sup=float(np.max(abs(a.distribution-f))),
            Bellman_sup=float(np.max(abs(a.value-V))),stationary_GE=False))
        print('ONE PERIOD',n,a.price,a.money,a.goods_residual,flush=True)
        if n==5:
            for price in np.linspace(2.8,3.2,17):
                b=evaluate_auction(m,V,f,price,opt_tol=5e-8)
                demand.append(dict(price=float(price),
                     min_money=b['money_min'],max_money=b['money_max'],
                     trade_rate=b['trades']))
            nash=continuous_nash(m,V,a.price,12,12)
            stationary,_=stationary_iteration(m,V,f,maxit=1,price_guess=a.price)
            assert stationary['status']=='STATIONARY_DID_NOT_CONVERGE'
    summary=dict(status='ONLY_CONDITIONAL_CM_AUCTIONS_NO_STATIONARY_GE',
        python=platform.python_version(),numpy=np.__version__,
        scipy=scipy.__version__,numba=numba.__version__,
        source='Molico--Zhang November 2005 draft; numerical variant, not author-code replication',
        money_issuer_stock=1,
        CM_interpolant='diagonal triangle piecewise affine in continuous capital and money',
        CM_method='global edge maximization exact for defined V interpolant',
        DM_method='discrete Nash menu for all pairs; independent continuous Nash at one active pair',
        continuation_value='unoptimized illustrative 5*(k+m/3)+0.02*sin(k)+0.003*sin(2*m)',
        equilibrium_certified=False,arbitrary_money_normalization=False,
        grids=rows,continuous_Nash=nash,stationary_attempt=stationary)
    (out/'conditional_report.json').write_text(json.dumps(summary,indent=2)+'\n')
    for name,data in (('conditional_grid.csv',rows),('money_demand_scan.csv',demand)):
        with (out/name).open('w',newline='') as file:
            writer=csv.DictWriter(file,fieldnames=list(data[0]))
            writer.writeheader();writer.writerows(data)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    figdir=out/'figures';figdir.mkdir(exist_ok=True)
    fig,ax=plt.subplots(figsize=(7,4))
    ax.plot([a['price'] for a in demand],[a['min_money'] for a in demand],
            marker='o',label='Minimum optimal money')
    ax.plot([a['price'] for a in demand],[a['max_money'] for a in demand],
            marker='s',label='Maximum optimal money')
    ax.axhline(1,linestyle='--',label='Fiat supply 1')
    ax.set(xlabel='Nominal capital price',
           ylabel='Conditional CM money demand',
           title='Continuous CM policy correspondence (not stationary GE)')
    ax.legend();fig.tight_layout()
    fig.savefig(figdir/'conditional_money_demand.svg');plt.close(fig)
    fig,ax=plt.subplots(figsize=(6,4))
    ax.plot([x['asset_nodes'] for x in rows],
            [x['CM_price_conditional'] for x in rows],marker='o')
    ax.set(xlabel='Number of nodes per portfolio axis',
           ylabel='One-period price',title='Not stationary GE')
    fig.tight_layout();fig.savefig(figdir/'conditional_grid_price.svg')
    plt.close(fig)
    assert all(abs(x['CM_money_residual'])<1e-9
               and abs(x['budget_residual'])<1e-9 for x in rows)
    print('COMPLETE: conditional CM clearing; stationary monetary GE NOT certified.')
    return summary
if __name__=='__main__':run()
