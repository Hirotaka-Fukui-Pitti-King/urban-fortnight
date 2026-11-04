"""Small deterministic checks for Stage 2-H's convex decomposition."""
import sys
import unittest
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parents[1]
BASE=HERE.parent
for p in (HERE/"src",BASE/"stage2g"/"src",BASE/"stage2c"/"src",
          BASE/"stage2e"/"src"):
    sys.path.insert(0,str(p))

from convex_nash import enumerate_triangles,solve_pair
from private_nash_bellman import fixture_3x3
from continuous_core import cm_opt
from molico_grid import g


class ConvexBranchTests(unittest.TestCase):
    def test_triangle_partition(self):
        self.assertEqual(len(enumerate_triangles(3,3)),8)
        self.assertEqual(len(enumerate_triangles(5,5)),32)
        self.assertEqual(len(enumerate_triangles(9,9)),128)
        self.assertEqual(len(set(enumerate_triangles(5,5))),32)

    def test_labor_cost_increasing_and_convex(self):
        k=1.5
        y=np.linspace(.01,.8,20)
        vals=np.array([g(q,k,.36,1.) for q in y])
        self.assertTrue(np.all(np.diff(vals)>0))
        self.assertTrue(np.all(np.diff(vals,2)>0))

    def test_no_money_no_trade(self):
        model,_=fixture_3x3()
        out=solve_pair(model,np.zeros(model.n),2.5,3,4)
        self.assertEqual(out.y,0.)
        self.assertEqual(out.d,0.)

    def test_dcp_positive_trade_and_outside_constraints(self):
        model,_=fixture_3x3()
        # At zero continuation values the CM selects only current
        # consumption. Buyer/seller positive Nash is still feasible.
        result=solve_pair(model,np.zeros(model.n),2.5,4,4)
        self.assertEqual(result.dcp_pass, result.unresolved_branches==0,
                         f"Numerical Nash uncertainty must be exposed: {result}")
        self.assertGreater(result.y,0.)
        self.assertGreater(result.d,0.)
        self.assertLess(result.y,model.p.A*model.k[4]**model.p.alpha)
        self.assertLessEqual(result.d,model.m[4]+1e-6)
        self.assertGreater(result.buyer_surplus,0.)
        self.assertGreater(result.seller_surplus,0.)


if __name__=="__main__":
    unittest.main()
