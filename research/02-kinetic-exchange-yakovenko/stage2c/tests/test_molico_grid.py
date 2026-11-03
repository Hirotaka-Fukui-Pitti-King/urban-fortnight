"""Economic tests for the original CM-DM equation set, not a GE certificate."""
import unittest
import numpy as np
from molico_grid import Calibration,MonetarySearch,u,g,bargaining,calc_W

class TestMolicoEquations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=MonetarySearch(Calibration(nk=5,nm=5,kmax=3,mmax=2,maxit=325))
    def test_type_specialization(self):
        self.assertEqual(self.m.p.Ntypes,3)
    def test_original_utility_and_labor_disutility(self):
        self.assertAlmostEqual(u(0.,.2,5.),0.)
        self.assertEqual(g(0.,1.,.36,1.),0.)
        self.assertGreater(g(.6,1.,.36,1.),g(.3,1.,.36,1.))
    def test_voluntary_discrete_nash_bargaining(self):
        m=self.m
        ww=np.linspace(0,10,501)
        W,_=calc_W(np.zeros(m.n),m.k,m.m,1.4,m.p.beta,m.p.b,m.p.eta,ww)
        y,d,bg,sg,effort=bargaining(m.k,m.m,1.4,W,ww,m.p.alpha,m.p.A,m.p.theta,m.p.y_choices,m.p.d_choices,m.p.delta)
        self.assertGreater(int(np.sum(d>0)),0)
        self.assertTrue(np.all(bg[d>0]>0))
        self.assertTrue(np.all(sg[d>0]>0))
        self.assertTrue(np.all(d[d>0]<=m.m[np.where(d>0)[0]]))
        self.assertTrue(np.all(effort[d>0]<1))
        self.assertTrue(np.all(d[m.m==0,:]==0))
        self.assertTrue(np.all(y[:,m.k==0]==0))
    def test_dm_mass_money_and_product_accounting(self):
        m=self.m;f=np.full(m.n,1/m.n)
        _,fn,info=m.step(np.zeros(m.n),f,1.4)
        cm=info["preCM"]
        upper=(1-m.p.delta)*m.p.kmax+.90*m.p.A*m.p.kmax**m.p.alpha
        kg=np.linspace(0,upper,max(2*m.p.nk,m.p.nk+8))
        kp=np.repeat(kg,m.p.nm);mp=np.tile(m.mg,len(kg))
        self.assertEqual(info["invalid"],0)
        self.assertAlmostEqual(float(cm.sum()),1.,places=12)
        self.assertAlmostEqual(float(cm@mp),float(f@m.m),places=12)
        self.assertAlmostEqual(float(cm@kp),float((1-m.p.delta)*(f@m.k)+info["production"]),places=11)
        self.assertAlmostEqual(float(fn.sum()),1.,places=12)
        self.assertEqual(info["invalid_CM"],0.)
        self.assertGreater(info["trades"],0.)
    def test_cm_combined_budget_identity(self):
        m=self.m;f=np.full(m.n,1/m.n)
        _,fn,info=m.step(np.zeros(m.n),f,1.4)
        gap=(info["consumption"]+(fn@m.k)+(fn@m.m)/1.4
             -((1-m.p.delta)*(f@m.k)+info["production"]+(f@m.m)/1.4))
        self.assertAlmostEqual(gap,0.,places=10)
    def test_fixed_price_is_not_monetary_GE(self):
        report,_=self.m.solve(price=1.4)
        self.assertTrue(report["converged"])
        self.assertEqual(report["invalid_transition_count"],0)
        self.assertLess(abs(report["mass"]-1),1e-10)
        self.assertGreater(abs(report["money_supply_residual"]),.05)
    def test_no_artificial_portfolio_taste(self):
        import inspect
        src=inspect.getsource(MonetarySearch)
        self.assertNotIn("taste_scale",src)
        self.assertNotIn("softmax",src)
if __name__=="__main__":unittest.main()
