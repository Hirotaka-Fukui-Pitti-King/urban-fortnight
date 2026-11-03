"""Stage 2-E: conditional economics, NOT stationary money-capital GE."""
import sys,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'stage2c'/'src'))
sys.path.insert(0,str(ROOT/'src'))
from molico_grid import Calibration,u
from continuous_core import ContinuousModel,cm_extreme_portfolios
from nash_continuous import continuous_nash
from auction import clear_price,stationary_iteration

class TestStage2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=ContinuousModel(Calibration(nk=5,nm=5,kmax=3.,mmax=2.,y_choices=4,d_choices=5))
        cls.f=np.zeros(cls.m.n);cls.f[12]=1.
        cls.V=5*(cls.m.k+cls.m.m/3.)+.02*np.sin(cls.m.k)+.003*np.sin(2*cls.m.m)

    def test_global_cm_vs_independent_continuous_deviations(self):
        m=self.m
        for wealth in (.8,1.5,2.11,3.25):
            W,k,mm,c=m.cm_value(wealth,3.,self.V)
            self.assertAlmostEqual(c,wealth-k-mm/3.,places=11)
            self.assertGreaterEqual(k,0);self.assertLessEqual(k,m.p.kmax)
            self.assertGreaterEqual(mm,0);self.assertLessEqual(mm,m.p.mmax)
            values=[]
            # Independently approximate all possible feasible policies on a
            # 200x40 grid, NOT merely the original discrete savings nodes.
            for kp in np.linspace(0,m.p.kmax,200):
                for mp in np.linspace(0,m.p.mmax,40):
                    cp=wealth-kp-mp/3.
                    if cp < -1e-10:continue
                    ia=min(max(np.searchsorted(m.kg,kp,side='right')-1,0),m.p.nk-2)
                    im=min(max(np.searchsorted(m.mg,mp,side='right')-1,0),m.p.nm-2)
                    a=(kp-m.kg[ia])/(m.kg[ia+1]-m.kg[ia])
                    b=(mp-m.mg[im])/(m.mg[im+1]-m.mg[im])
                    z=ia*m.p.nm+im
                    if b<=a:
                        cont=(1-a)*self.V[z]+(a-b)*self.V[z+m.p.nm]+b*self.V[z+m.p.nm+1]
                    else:
                        cont=(1-b)*self.V[z]+(b-a)*self.V[z+1]+a*self.V[z+m.p.nm+1]
                    values.append(u(max(0.,cp),m.p.b,m.p.eta)+m.p.beta*cont)
            self.assertGreaterEqual(W,max(values)-1e-7)

    def test_continuous_cm_budget_and_optimal_correspondence(self):
        m=self.m;w=2.11;p=3.01125
        W,kl,ml,cl,kh,mh,ch=cm_extreme_portfolios(
            w,p,m.k,m.m,self.V,m.edges,m.p.beta,m.p.b,m.p.eta,1e-9)
        self.assertLessEqual(ml,mh)
        self.assertAlmostEqual(kl+ml/p+cl,w,places=11)
        self.assertAlmostEqual(kh+mh/p+ch,w,places=11)
        self.assertAlmostEqual(W,m.cm_value(w,p,self.V)[0],places=10)

    def test_continuous_nash_improves_discrete_contract(self):
        sol=continuous_nash(self.m,self.V,3.01125,12,12)
        self.assertTrue(sol['trade']);self.assertTrue(sol['success'])
        self.assertGreater(sol['buyer_gain'],0)
        self.assertGreater(sol['seller_gain'],0)
        self.assertGreater(sol['improvement_over_coarse'],.01)
        self.assertGreaterEqual(sol['payment_feasibility'],-1e-10)
        self.assertGreater(sol['seller_labor'],0)
        self.assertLess(sol['seller_labor'],1)

    def test_dm_mass_money_and_production_accounting(self):
        m=self.m
        _,f,d=m.step(self.V,self.f,3.01125)
        self.assertEqual(d['invalid'],0)
        self.assertEqual(d['invalid_CM'],0)
        self.assertAlmostEqual(d['preCM'].sum(),1.,places=11)
        self.assertAlmostEqual(d['preCM']@m.postm,self.f@m.m,places=11)
        self.assertAlmostEqual(d['preCM']@m.postk,
           (1-m.p.delta)*(self.f@m.k)+d['production'],places=11)
        self.assertAlmostEqual(f.sum(),1.,places=11)

    def test_one_period_money_market_clears_without_rescaling(self):
        a=clear_price(self.m,self.V,self.f,price_hint=3.,
             prices=[2.7,2.8,2.9,3,3.1,3.2],opt_tol=5e-8)
        self.assertAlmostEqual(a.money,1.,places=10)
        self.assertLess(abs(a.goods_residual),1e-9)
        self.assertLess(abs(a.mass_residual),1e-10)
        self.assertLess(a.regret_bound,1e-7)
        self.assertGreater(a.trade_rate,0)
        self.assertEqual(a.status,'ONE_PERIOD_OPTIMAL_CM_CLEARING_NOT_STATIONARY_GE')
        self.assertGreater(abs(a.capital-(self.f@self.m.k)),.01)

    def test_no_false_stationary_GE(self):
        r,a=stationary_iteration(self.m,self.V,self.f,maxit=1,price_guess=3.)
        self.assertEqual(r['status'],'STATIONARY_DID_NOT_CONVERGE')
        self.assertGreater(r['history'][0]['bellman_sup'],1.)
        self.assertGreater(r['history'][0]['distribution_sup'],.01)
if __name__=='__main__':unittest.main()
