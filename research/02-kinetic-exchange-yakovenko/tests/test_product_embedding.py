"""Check joint stationary product law and optimized policy evaluation."""
from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from product_embedding import product_checks

class TestProductEconomy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=product_checks()
    def test_equilibrium_market_clearing(self):
        self.assertLess(self.d["capital_market_rel_error"],1e-6)
        self.assertLess(abs(self.d["goods_market_error"]),1e-6)
        self.assertEqual(self.d["service_market_error"],0.)
        self.assertLess(self.d["token_market_error"],1e-12)
    def test_rational_fixed_price_policy_and_joint_invariance(self):
        self.assertLess(self.d["stationary_product_joint_sup_error"],1e-10)
        self.assertLess(self.d["joint_separable_policy_bellman_sup_error"],1e-8)
        self.assertEqual(self.d["optimal_trade_participation_failures"],0)
if __name__=="__main__":
    unittest.main()
