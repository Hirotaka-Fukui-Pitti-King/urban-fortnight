"""Checks for mathematical claims, numerical examples, and Quarto source pairing."""
from __future__ import annotations
import importlib.util
import sys
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
import yaml

HERE=Path(__file__).resolve().parents[1]
src=HERE/"scripts"/"generate_figures.py"
spec=importlib.util.spec_from_file_location("econ_first_lecture",src)
mod=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=mod
spec.loader.exec_module(mod)


class Equations(unittest.TestCase):
    def test_kl_contraction_no_detailed_balance(self):
        f=np.array([.8,.1,.1])
        pi=np.ones(3)/3
        P=np.array([[.25,.75,0.],[0.,.25,.75],[.75,0.,.25]])
        D=lambda x: float(np.sum(x*np.log(x/pi)))
        self.assertLess(D(f@P),D(f))
        self.assertGreater(abs(pi[0]*P[0,1]-pi[1]*P[1,0]),.01)

    def test_nonlinear_markov_does_not_contract_to_fixed_pi(self):
        p=.51
        q=.5+.48*np.tanh(10*(p-.5))
        D=lambda x: x*np.log(2*x)+(1-x)*np.log(2*(1-x))
        self.assertGreater(D(q),D(p))

    def test_aiyagari_policy_and_stationary_measure(self):
        a=np.linspace(0,30,180)
        z=np.array([.7,1.3])
        P=np.array([[.94,.06],[.06,.94]])
        c,ap,k,w=mod.egm(.03409789470820705,a,z,P)
        mu,lottery=mod.stationary(ap,a,P)
        self.assertTrue(np.all(c>0))
        self.assertTrue(np.all(ap>=0))
        diag=mod.aiyagari_policy_diagnostics(.03409789470820705,a,z,P,c,ap)
        self.assertLess(diag["budget_sup"],1e-9)
        self.assertLess(diag["euler_kkt_sup"],.05)
        self.assertAlmostEqual(float(mu.sum()),1.,places=9)
        self.assertLess(float(np.max(abs(mod.forward(mu,*lottery,P)-mu))),1e-8)

    def test_voluntary_monetary_exchange(self):
        for meeting,assort in ((.45,0.),(.2,3.)):
            f,d=mod.money_candidate(meeting,assort)
            self.assertAlmostEqual(float(f.sum()),1.,places=9)
            self.assertAlmostEqual(float(f@np.arange(6)),2.,places=9)
            self.assertLess(d["stationarity_sup"],1e-10)
            self.assertGreaterEqual(d["buyer_min_gain"],-1e-9)
            self.assertGreaterEqual(d["seller_min_gain"],-1e-9)
            self.assertLess(d["bellman_sup"],1e-10)
            self.assertLess(d["conservation_money"],1e-10)
            self.assertLess(d["transition_row_sum_sup"],1e-10)
            self.assertEqual(d["transition_negative_part"],0.)


class Artifacts(unittest.TestCase):
    def test_qmd_body_matches_markdown(self):
        stems=("01-aiyagari-statistical-mechanics","02-social-interactions-ising",
               "03-monetary-search-boltzmann","04-other-economic-models")
        for stem in stems:
            md=(HERE/(stem+".md")).read_text(encoding="utf-8")
            qmd=(HERE/(stem+".qmd")).read_text(encoding="utf-8")
            self.assertTrue(qmd.startswith("---\n"))
            header,body=qmd[4:].split("\n---\n",1)
            data=yaml.safe_load(header)
            self.assertEqual(data["lang"],"ja")
            self.assertEqual(md.partition("\n\n")[2],body.lstrip("\n"))
            self.assertEqual(md.count("$$")%2,0)

    def test_svg_vectors_parse(self):
        names=("aiyagari-savings.svg","aiyagari-distribution.svg",
               "ising-finite-population.svg","monetary-matching.svg")
        for name in names:
            svg=ET.parse(HERE/"figures"/name).getroot()
            self.assertTrue(svg.tag.endswith("svg"))


if __name__=="__main__":
    unittest.main()
