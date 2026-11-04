"""Verify bordered continuation can pass a saddle-node turn in a toy system.

This verifies the numerical continuation mechanism, not existence of
a Nash--Bellman private equilibrium in the monetary model.
"""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np

SCRIPTS=Path(__file__).resolve().parents[1]/"scripts"
sys.path.insert(0,str(SCRIPTS))
import solve_5x5_pseudo_arclength as continuation


class PseudoArclengthTests(unittest.TestCase):
    def test_fold_tracking(self):
        # Exact branch z^2 + lambda = 1; lambda first increases to 1
        # and then falls, so a lambda-monotonic continuation cannot pass fold.
        def residual(z,matching,*unused):
            return np.array([z[0]**2+matching-1.])
        points=[(.8,.36),(.6,.64)]
        with patch.object(continuation,"relative_residual",side_effect=residual):
            for _ in range(12):
                prev,cur=points[-2:]
                z,l,diag=continuation.correct_arc(
                    np.array([prev[0]]),prev[1],
                    np.array([cur[0]]),cur[1],
                    np.array([1.]),.09,None,None,0.,7,7,200)
                self.assertLess(diag["residual"],1e-8)
                self.assertAlmostEqual(z[0]**2+l,1.,places=8)
                points.append((float(z[0]),float(l)))
        self.assertTrue(any(points[i+1][1]<points[i][1]
                            for i in range(1,len(points)-1)))


if __name__=="__main__":
    unittest.main()
