"""Economic feasibility, FOC and clearing tests for the Aiyagari benchmark."""
import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from aiyagari import Calibration,rouwenhorst,equilibrium,firm_from_r,histogram_step
class TestAiyagari(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=Calibration(na=200,amax=600.)
        cls.eq=equilibrium(cls.c)
    def test_rouwenhorst_stationarity(self):
        z,P,pi=rouwenhorst(5,.9,.2)
        self.assertAlmostEqual(float(np.dot(pi,z)),1.,places=12)
        self.assertLess(float(np.max(abs(P.sum(axis=1)-1))),1e-13)
        self.assertLess(float(np.max(abs(pi@P-pi))),1e-13)
    def test_feasibility(self):
        e=self.eq; a=e["a"];z=e["z"];c=e["c"];g=e["g"];s=e["summary"]
        self.assertGreater(float(c.min()),0.)
        self.assertGreaterEqual(float(g.min()),0.)
        self.assertLessEqual(float(g.max()),a[-1])
        cash=(1+s["r"])*a[None,:]+s["w"]*z[:,None]
        self.assertLess(float(np.max(abs(c+g-cash))),1e-10)
    def test_distribution_and_clearing(self):
        e=self.eq;s=e["summary"];mu=e["mu"]
        self.assertAlmostEqual(float(mu.sum()),1.,places=9)
        self.assertTrue((mu>=0).all())
        nxt,flag=histogram_step(mu,e["a"],e["g"],e["P"])
        self.assertEqual(flag,0)
        self.assertLess(float(np.max(abs(nxt-mu))),1e-10)
        self.assertLess(s["ge_relative_capital_error"],1e-6)
        self.assertLess(abs(s["goods_resource_error"]/s["Y"]),1e-6)
        self.assertLess(abs(s["next_assets_stationarity_error"]),1e-6)
        self.assertLess(s["income_state_max_error"],1e-8)
        self.assertEqual(s["asset_top_mass"],0.)
    def test_optimality(self):
        s=self.eq["summary"]
        self.assertLess(s["weighted_p99_kkt_or_log_euler"],5e-5)
        self.assertLess(s["weighted_mean_kkt_or_log_euler"],5e-5)
    def test_firm_prices(self):
        s=self.eq["summary"];K,w=firm_from_r(s["r"],self.c,s["L"])
        self.assertAlmostEqual(K,s["K_demand"],places=11)
        self.assertAlmostEqual(w,s["w"],places=11)
if __name__=="__main__":unittest.main()
