"""Do not mistake local distribution feedback for a new GE policy effect."""
import sys,unittest
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/"src"))
from joint_model import Model
from collision_feedback import collision,symmetric_reference,feedback_diagnostic

class TestCollisionFeedback(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=Model();cls.sol=cls.model.solve_inner(4.5,.97,.65)
        assert cls.sol['info']['converged']
    def test_pair_conservation(self):
        m=self.model;f=self.sol['f']
        q=collision(m,f,f,self.sol)
        self.assertLess(abs(q.sum()),1e-12)
        self.assertLess(abs(q@m.m[m.im]),1e-12)
        self.assertLess(abs(q@m.a[m.ia]),1e-12)
        self.assertGreaterEqual(float((f+q).min()),-1e-12)
    def test_frozen_matches_reference_at_stationarity(self):
        f=self.sol['f'];m=self.model
        np.testing.assert_allclose(collision(m,f,f,self.sol),
            symmetric_reference(m,f,f,self.sol),atol=1e-14)
    def test_exact_derivative_and_same_marginal_perturbation(self):
        x=feedback_diagnostic(self.model,self.sol)
        self.assertLess(x['maximum_bilinear_derivative_error'],1e-9)
        self.assertAlmostEqual(x['initial_asset_mean_change'],0,places=13)
        self.assertAlmostEqual(x['initial_money_mean_change'],0,places=13)
        self.assertLess(abs(x['money_change_actual']),1e-12)
        self.assertLess(abs(x['money_change_reference']),1e-12)
        self.assertGreater(x['kinetic_feedback_sup'],.001)
        self.assertGreater(x['next_distribution_tv'],.001)
        self.assertGreater(abs(x['next_capital_difference']),1e-5)
if __name__=="__main__":unittest.main()
