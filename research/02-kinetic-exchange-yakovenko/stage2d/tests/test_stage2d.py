"""Stage 2-D tests: exact CM and one-period money clearing, NOT stationary GE."""
import unittest,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'stage2c'/'src'))
sys.path.insert(0,str(ROOT/'src'))
from molico_grid import MonetarySearch,Calibration,u
from exact_core import ExactCMModel,CM_exact
from clearing import clear_cm_price,stationary_attempt

class TestMoneyAuction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=Calibration(nk=5,nm=5,kmax=3,mmax=2)
        cls.m=ExactCMModel(cls.p)
        cls.old=MonetarySearch(cls.p)
        cls.f=np.zeros(cls.m.n);cls.f[12]=1.
        cls.V=5*(cls.m.k+cls.m.m/3)
        cls.c=clear_cm_price(cls.m,cls.V,cls.f,bracket=(2,5),tolerance=1e-12)
    def test_true_indifference_and_money_market(self):
        c=self.c
        self.assertLess(abs(c.next_money-1),1e-12)
        self.assertLess(c.inner_optimality_gap,1e-8)
        self.assertLess(c.mass_residual,1e-12)
        self.assertEqual(c.changed_bargaining_contracts,0)
        self.assertGreater(c.mixing_probability,0.)
        self.assertLess(c.mixing_probability,1.)
    def test_money_not_posthoc_normalized(self):
        c=self.c
        self.assertAlmostEqual(c.incoming_money,1,places=12)
        self.assertLess(c.money_lower,1.)
        self.assertGreater(c.money_upper,1.)
        self.assertGreater(c.money_upper-c.money_lower,.1)
    def test_budget_and_production(self):
        self.assertLess(abs(self.c.budget_residual),1e-10)
        self.assertGreater(self.c.production,0)
        self.assertGreater(self.c.trades,0)
    def test_original_W_interpolation_changes_Bellman(self):
        va,_,_=self.old.step(self.V,self.f,2.7)
        vb,_,_=self.m.step(self.V,self.f,2.7)
        self.assertGreater(np.max(abs(va-vb)),.1)
    def test_exact_Centralized_Market_max(self):
        w=1.375;p=2.7
        costs=self.m.k+self.m.m/p
        value,j=CM_exact(w,costs,self.V,self.p.beta,self.p.b,self.p.eta)
        scores=[u(max(w-costs[i],0),self.p.b,self.p.eta)+self.p.beta*self.V[i]
                 if w-costs[i]>=-1e-12 else -np.inf for i in range(len(costs))]
        self.assertEqual(j,int(np.argmax(scores)))
        self.assertAlmostEqual(value,max(scores),places=12)
    def test_seller_may_receive_above_savings_money_grid(self):
        old=self.old.step(self.V,self.f,2.7)[2]
        new=self.m.step(self.V,self.f,2.7)[2]
        top=self.m.m==self.p.mmax
        self.assertEqual(np.count_nonzero(old['d'][:,top]),0)
        self.assertGreater(np.count_nonzero(new['d'][:,top]),0)
        self.assertEqual(new['invalid'],0)
        self.assertLess(abs(new['preCM'].sum()-1),1e-12)
    def test_seven_by_seven_not_a_converged_grid_price(self):
        model=ExactCMModel(Calibration(nk=7,nm=7,kmax=3,mmax=2))
        f=np.zeros(model.n);f[(model.p.nk//2)*model.p.nm+model.p.nm//2]=1.
        V=5*(model.k+model.m/3)
        c=clear_cm_price(model,V,f,bracket=(.5,10),tolerance=1e-11)
        self.assertLess(abs(c.next_money-1),1e-10)
        self.assertLess(abs(c.budget_residual),1e-10)
        self.assertGreater(abs(c.price-self.c.price),.01)
    def test_one_period_auction_is_not_stationary_equilibrium(self):
        c=self.c
        self.assertTrue(c.status.endswith('NOT_STATIONARY_GE'))
        self.assertGreater(abs(c.next_capital-self.f@self.m.k),.01)
        self.assertGreater(np.max(abs(c.next_distribution-self.f)),.01)
        attempt,_=stationary_attempt(self.m,self.V,self.f,max_iter=2,
              init_price=3.11,damping_value=.20,damping_distribution=.15)
        self.assertEqual(attempt['status'],'NOT_CONVERGED_JOINT_PRICE_BELLMAN_DISTRIBUTION')
        self.assertTrue(all(abs(r['money']-1)<1e-9 for r in attempt['history']))
if __name__=='__main__':unittest.main()
