"""Fast correctness checks; expensive precision experiment is manual."""
import sys
import unittest
from pathlib import Path
import numpy as np

SRC=Path(__file__).resolve().parents[1]/"src"
sys.path.insert(0,str(SRC))
from private_nash_bellman import (fixture_3x3, _nash_log, nash_grad,
                                  endogenous_operator, nash_polish,
                                  nash_candidate, _frozen_operator)

class NashPrivateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model,cls.f=fixture_3x3()
        cls.p=2.5
        cls.v=np.asarray([
            0.,2946.7179991,3152.75508697,3278.52358795,3406.10697095,
            3457.64688968,3489.92849979,3526.98090514,3546.06220954])
    def test_payment_feasibility_and_participation(self):
        m=self.model;p=m.p
        for i,j in [(1,4),(2,4),(4,4),(5,4),(7,4)]:
            q,d,_=nash_candidate(i,j,self.p,m.k,m.m,self.v,m.edges,
                                  p.beta,p.b,p.eta,p.alpha,p.A,p.theta,
                                  p.delta,7,7)
            q,d,kkt=nash_polish(i,j,q,d,m,self.v,self.p)
            self.assertGreater(q,0)
            self.assertLess(q,p.A*m.k[j]**p.alpha)
            self.assertGreaterEqual(d,0)
            self.assertLessEqual(d,m.m[i]+1e-10)
            self.assertTrue(np.isfinite(kkt))
    def test_translation_covariance(self):
        m=self.model;p=m.p
        T,_,_,_=endogenous_operator(self.v,self.f,self.p,m,nq=7,nx=7)
        shift=300.
        TT,_,_,_=endogenous_operator(self.v+shift,self.f,self.p,m,nq=7,nx=7)
        self.assertLess(max(abs((TT-T)-p.beta*shift)),1e-8)
    def test_frozen_policy_is_contraction_for_constant_shift(self):
        m=self.model;p=m.p
        T,y,d,_=endogenous_operator(self.v,self.f,self.p,m,nq=7,nx=7)
        def F(z):
            return _frozen_operator(z,self.f,self.p,m.k,m.m,m.edges,p.beta,
                                    p.b,p.eta,p.alpha,p.A,p.delta,p.Ntypes,y,d)
        self.assertLess(max(abs((F(self.v+2)-F(self.v))-2*p.beta)),1e-8)

if __name__=="__main__":
    unittest.main()
