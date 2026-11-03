"""Stage 2 tests: optimality, conservation, probability, entropy and particle law."""
import sys, unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from monetary_matching import (Params,solve_candidate,diagnostics,generator,flows,
    seller_gain,optimal_trade,foley_style_transaction_benchmark,collision_operator)
from particle_simulator import simulate

class TestOptimalMatching(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=Params()
        cls.sol=solve_candidate(cls.p)
        cls.metrics=diagnostics(cls.sol,cls.p)
    def test_voluntary_trade_and_bellman(self):
        self.assertEqual(self.metrics["participation_failures"],0)
        self.assertLess(self.metrics["bellman_sup_error"],1e-11)
        for b in range(1,self.p.max_tokens+1):
            for s in range(self.p.max_tokens):
                self.assertTrue(optimal_trade(self.sol["V"],b,s,self.p))
    def test_probability_distribution_and_kinetic_conservation(self):
        s=self.sol;d=self.metrics
        np.testing.assert_allclose(s["L"].sum(axis=1),0,atol=1e-12)
        self.assertLess(np.max(np.abs(s["L"].T@s["f"])),1e-11)
        self.assertLess(d["money_mass_error"],1e-11)
        self.assertLess(d["money_conservation_error"],1e-11)
        self.assertEqual(d["service_market_error"],0.)
        self.assertAlmostEqual(d["mean_money"],self.p.average_tokens,places=10)
    def test_uniform_matching_entropy_coincidence(self):
        self.assertLess(abs(self.metrics["kl_divergence_from_money_maxent"]),1e-11)
    def test_state_dependent_matching_breaks_max_entropy(self):
        p=Params(meeting_rate=.2,assortativity=3)
        s=solve_candidate(p);d=diagnostics(s,p)
        self.assertEqual(d["participation_failures"],0)
        self.assertLess(d["stationarity_sup_error"],1e-11)
        self.assertGreater(d["kl_divergence_from_money_maxent"],.004)
    def test_token_supply_and_particle_comparison(self):
        x=simulate(self.p,self.sol,1000,11,burnin=400,measure_count=25,measure_every=10)
        self.assertAlmostEqual(x["money_supply_error"],0.,places=10)
        self.assertLess(x["average_mass_W1"],.22)
        self.assertLess(abs(x["service_trade_error"]),.03)
    def test_collision_operator_matches_forward_generator(self):
        p=self.p
        f=.5*self.sol["f"]+.5*np.array([0,0,1,0,0,0.])
        q=collision_operator(f,self.sol["trade"],p)
        np.testing.assert_allclose(q,generator(f,self.sol["trade"],p).T@f,atol=1e-14)
        self.assertAlmostEqual(float(q.sum()),0.,places=14)
        self.assertAlmostEqual(float(q@np.arange(len(f))),0.,places=14)
        self.assertGreaterEqual(float(np.min(f+q)),-1e-14)
    def test_foley_style_transaction_benchmark_differs(self):
        x=foley_style_transaction_benchmark(self.sol,self.p)
        self.assertGreater(x["transaction_kl_realized_to_maxent"],0.1)
        self.assertLess(abs(x["transaction_market_balance"]),1e-11)
    def test_no_trade_equilibrium(self):
        p=Params();V=np.zeros(p.max_tokens+1)
        for s in range(p.max_tokens):
            self.assertLess(seller_gain(V,s,p),0)
        t=np.zeros((p.max_tokens+1,p.max_tokens+1),dtype=bool)
        f=np.ones(p.max_tokens+1)/(p.max_tokens+1)
        self.assertAlmostEqual(float((generator(f,t,p).T@f).max()),0.)
    def test_off_switch_no_exchange(self):
        p=Params(meeting_rate=0)
        f=np.array([0,0,1,0,0,0.],dtype=float)
        t=np.zeros((6,6),dtype=bool)
        np.testing.assert_allclose(generator(f,t,p),np.zeros((6,6)))
        self.assertEqual(float(flows(f,t,p).sum()),0.)
if __name__=="__main__":
    unittest.main()
