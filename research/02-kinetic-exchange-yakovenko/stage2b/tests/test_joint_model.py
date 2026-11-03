"""Executed economic tests for Stage 2-B fixed-price, NOT an equilibrium certificate."""
import sys,unittest
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'src'))
from joint_model import Model,Params
from validation import check_nash,check_kinetic,one_step_particles

class TestJointPrototype(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=Model()
        cls.s=cls.m.solve_inner(4.5,.97,.65)
    def test_interior_partial_bellman_consistency(self):
        x=self.s['info']
        self.assertTrue(x['converged'])
        self.assertLess(x['value_residual'],1e-7)
        self.assertLess(x['distribution_residual'],1e-8)
    def test_exact_discrete_nash_optimality(self):
        d=check_nash(self.m,self.s)
        self.assertGreater(d['accepted_contracts'],0)
        self.assertGreater(d['buyer_min_positive_gain'],0)
        self.assertGreater(d['seller_min_positive_gain'],0)
    def test_boltzmann_accounting(self):
        d=check_kinetic(self.m,self.s)
        for k in ['population_mass_change','capital_in_DM_change','money_in_DM_change']:
            self.assertLess(abs(d[k]),1e-10)
        self.assertGreaterEqual(d['minimum_after_DM_probability'],-1e-12)
        self.assertGreater(d['service_output'],0)
        self.assertGreater(d['market_labor_reduction'],0)
    def test_money_and_capital_jointly_in_budget(self):
        self.assertNotEqual(self.s['info']['capital_money_cov'],0)
        self.assertTrue(np.any(self.s['pi'][:,0,:]>.001))
        self.assertTrue(np.any(self.s['pi'][:,0,:]<.999))
    def test_particle_one_step_matches_mean_field(self):
        a=one_step_particles(self.m,self.s,n=20000,seed=19)
        self.assertEqual(a['dm_money_conservation_error'],0)
        self.assertLess(a['total_variation_next_distribution'],.05)
        self.assertLess(a['max_next_distribution_abs_error'],.015)
    def test_walras_goods_gap_is_implied_by_factor_market_gaps(self):
        self.assertLess(abs(self.s['info']['goods_accounting_identity_error']),1e-10)
    def test_must_not_call_fixed_prices_ge(self):
        x=self.s['info']
        self.assertGreater(abs(x['capital_price_consistency']),.1)
        self.assertGreater(abs(x['money_supply_excess']),.01)
    def test_price_root_rejects_unconverged_household_fixed_point(self):
        from unittest.mock import patch
        dummy={'info': {'converged':False,'value_residual':.2,
                        'max_boundary_asset_mass':0.}}
        with patch.object(self.m,'solve_inner',return_value=dummy):
            with self.assertRaisesRegex(RuntimeError,'household/distribution'):
                self.m.solve_prices(start=(4.5,.97,.65))

    def test_no_meetings_no_service(self):
        p=Params(lambda_meet=0,max_inner=1000)
        m=Model(p);x=m.solve_inner(4.5,.97,.65)
        self.assertLess(abs(x['info']['service']),1e-12)
        # Portfolio taste shocks themselves generate money demand: a structural defect.
        self.assertGreater(x['info']['money'],0)
if __name__=="__main__":unittest.main()
