"""Structural checks for the Stage 1 fixed-price particle experiment."""
import sys,unittest
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(BASE/"00-heterogeneous-agent-ge"/"src"),str(BASE/"01-agent-based-equilibrium"/"src")]
from aiyagari import Calibration,equilibrium
from particles import particle_path
class TestParticles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.eq=equilibrium(Calibration(na=200,amax=600.))
    def test_reproducible_optimal_policy_path(self):
        r=self.eq
        args=(r["a"],r["g"],r["c"],r["z"],r["P"],500,400,20,123)
        x=particle_path(*args);y=particle_path(*args)
        for a,b in zip(x,y):
            np.testing.assert_array_equal(a,b)
        self.assertTrue(np.all(x[0]>=0.))
        self.assertTrue(np.all(x[0]<=r["a"][-1]))
        self.assertLess(abs(x[2]/r["summary"]["K_demand"]-1),.20)
if __name__=="__main__":unittest.main()
