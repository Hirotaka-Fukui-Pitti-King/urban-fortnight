"""Fixed contracts do not imply optimizing Nash/monetary equilibrium."""
import unittest
import numpy as np
from exact_core import ExactCMModel
from molico_grid import Calibration
from fixed_contracts import (fixed_contract_bellman,evaluate_contracts,
    improve_nash_contracts,iterate_policy_evaluation)
class TestFixedContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=ExactCMModel(Calibration(nk=5,nm=5,kmax=3,mmax=2,y_choices=3,d_choices=4))
        cls.f=np.zeros(cls.m.n);cls.f[12]=1.
    def test_fixed_contract_converges(self):
        m=self.m;V=np.zeros(m.n);y,d=improve_nash_contracts(m,V,3.)
        z=evaluate_contracts(m,self.f,3.,y,d,tol=1e-7,maxiter=1500)
        self.assertTrue(z["converged"])
        self.assertLess(z["residual"],1e-7)
        self.assertLess(z["iterations"],800)
    def test_fixed_contract_beta_lipschitz(self):
        m=self.m;p=m.p
        y,d=improve_nash_contracts(m,np.zeros(m.n),3.)
        V=np.linspace(0,10,m.n);Z=V+.123
        def F(v):
            return fixed_contract_bellman(v,m.k,m.m,self.f,3.,y,d,
                p.beta,p.b,p.eta,p.alpha,p.A,p.delta,p.Ntypes)
        self.assertLessEqual(float(np.max(abs(F(V)-F(Z)))),p.beta*.123+1e-10)
    def test_nash_improvement_may_cycle(self):
        m=self.m;z=iterate_policy_evaluation(m,self.f,price=3.,max_policy_iter=6)
        self.assertIn(z["status"],{"FINITE_DISCRETE_NASH_FIXED_PRICE_PRIVATE_EQUILIBRIUM",
            "ENDOGENOUS_NASH_POLICY_DID_NOT_STABILIZE"})
        self.assertLessEqual(len(z["history"]),6)
        self.assertTrue(np.isfinite(z["value"]).all())
if __name__=="__main__":unittest.main()
