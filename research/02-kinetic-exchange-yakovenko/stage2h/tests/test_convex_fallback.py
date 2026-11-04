"""Do not silently discard a convex branch after a conic-solver failure.

This checks that invalid first-choice solver names trigger the documented
independent SCS recovery rather than promoting an incomplete global optimum.
The source approximation is piecewise affine; this test is not a 5x5 root.
"""
import sys
import unittest
from pathlib import Path
import numpy as np

root=Path(__file__).resolve().parents[1]
research=root.parent
for p in (root/"src",research/"stage2g"/"src",
          research/"stage2c"/"src",research/"stage2e"/"src"):
    sys.path.insert(0,str(p))
from convex_nash import solve_pair
from private_nash_bellman import fixture_3x3


class ConvexFallbackTests(unittest.TestCase):
    def test_bad_primary_solver_uses_secondary_without_false_certificate(self):
        model,_=fixture_3x3()
        result=solve_pair(model,np.zeros(model.n),2.5,4,4,solver="INVALID_SOLVER")
        self.assertGreater(result.triangles_solved,0)
        self.assertFalse(result.global_proof)
        self.assertGreaterEqual(result.unresolved_branches,0)
        self.assertFalse(np.isnan(result.log_nash))
        if result.unresolved_branches:
            self.assertFalse(result.dcp_pass)
            self.assertGreater(result.unresolved_branch_upper_log_nash,
                               result.log_nash)
        else:
            self.assertTrue(result.dcp_pass)


if __name__=="__main__":
    unittest.main()
