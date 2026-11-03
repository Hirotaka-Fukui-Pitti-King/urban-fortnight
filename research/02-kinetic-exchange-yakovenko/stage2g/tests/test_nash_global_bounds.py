"""A globally optimal nonconcave Nash search must not trust local FOCs."""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from nash_global_bounds import bound_nash


class BoundTests(unittest.TestCase):
    def test_analytic_linear_W_solution(self):
        # B=y-x and S=x-y*y/2. At theta=.5 the unique global optimum
        # is y=1, x=.75: B=S=.25, objective log(.25).
        result=bound_nash(lambda w:w,lambda y:.5*y*y,
                          buyer_wealth=1,seller_wealth=1,
                          cash_real=1,production_cap=2,buyer_weight=.5,
                          initial=(1.,.75),log_gap_tolerance=.01,
                          max_boxes=10000)
        self.assertTrue(result.bounded_to_tolerance,result)
        self.assertAlmostEqual(result.lower_log_nash,math.log(.25),places=12)
        self.assertLessEqual(result.lower_log_nash,
                             math.log(.25)+1e-12)
        self.assertGreaterEqual(result.upper_log_nash,
                                math.log(.25)-1e-12)

    def test_monotone_nonconcave_W(self):
        W=lambda w:w+0.05*math.sin(7*w)
        # W' = 1+.35 cos(7w) >0, yet W'' changes sign.
        result=bound_nash(W,lambda y:.5*y*y,1.,1.,1.,2.,.5,
                          initial=(1.,.75),log_gap_tolerance=.03,
                          max_boxes=5000)
        self.assertTrue(result.bounded_to_tolerance,result)
        self.assertLessEqual(result.lower_log_nash,
                             result.upper_log_nash)
        for y,x in [(1.,.75),(1.1,.88),(1.15,.95),(.8,.6)]:
            b=W(1+y-x)-W(1)
            s=W(1+x)-W(1)-y*y/2
            if b>0 and s>0:
                self.assertGreaterEqual(result.upper_log_nash+1e-12,
                                        .5*(math.log(b)+math.log(s)))

    def test_zero_money_means_no_trade(self):
        x=bound_nash(lambda w:w,lambda y:y*y,1.,1.,
                     0.,2.,.5)
        self.assertTrue(x.bounded_to_tolerance)
        self.assertFalse(x.candidate_positive)

    def test_failure_must_be_reported(self):
        x=bound_nash(lambda w:w,lambda y:.5*y*y,1.,1.,
                     1.,2.,.5,initial=(1.,.75),
                     log_gap_tolerance=1e-10,max_boxes=2)
        self.assertFalse(x.bounded_to_tolerance)
        self.assertGreater(x.gap_log_nash,1e-10)


if __name__=="__main__":
    unittest.main()
