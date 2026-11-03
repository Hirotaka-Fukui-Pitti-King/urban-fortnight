"""Economic invariants of adaptive money-capital grid transport."""
import unittest
import numpy as np
from adaptive_grids import (Grid,original_step6_grid,regrid_measure,
    interpolate_value_bilinear,occupied_support)
class TestAdaptiveGrid(unittest.TestCase):
    def test_source_bounds(self):
        g=original_step6_grid(1.5,3.,20,21)
        self.assertAlmostEqual(g.capital[-1],3.)
        self.assertAlmostEqual(g.money[-1],9.)
    def test_cover_occupied_support(self):
        a=Grid(np.linspace(0,4,9),np.linspace(0,8,9))
        f=np.zeros(a.shape);f[7,7]=.2;f[2,2]=.8
        mx=occupied_support(f,a)
        b=original_step6_grid(.5,1.2,10,11,existing=mx)
        self.assertGreaterEqual(b.capital[-1],mx[0])
        self.assertGreaterEqual(b.money[-1],mx[1])
        self.assertAlmostEqual(regrid_measure(f,a,b).sum(),1,places=13)
    def test_first_moments_and_nonnegative(self):
        rng=np.random.default_rng(20261103)
        a=Grid(np.linspace(0,6,17),np.linspace(0,9,18))
        b=Grid(np.linspace(0,9,12),np.linspace(0,15,13))
        f=rng.random(a.shape);f/=f.sum()
        z=regrid_measure(f,a,b)
        np.testing.assert_allclose([z.sum(),z@b.k,z@b.m],
            [f.sum(),f.ravel()@a.k,f.ravel()@a.m],atol=2e-13,rtol=0)
        self.assertGreaterEqual(z.min(),0)
    def test_no_clipping(self):
        a=Grid(np.linspace(0,4,5),np.linspace(0,3,6))
        b=Grid(np.linspace(0,3.5,5),np.linspace(0,3,5))
        f=np.zeros(a.shape);f[-1,-1]=1
        with self.assertRaises(ValueError):regrid_measure(f,a,b)
    def test_affine_value(self):
        a=Grid(np.linspace(0,5,6),np.linspace(0,6,7))
        b=Grid(np.linspace(.1,4.8,18),np.linspace(.2,5.8,17))
        V=2.5+4*a.k-2*a.m
        np.testing.assert_allclose(interpolate_value_bilinear(V,a,b),
            2.5+4*b.k-2*b.m,rtol=0,atol=2e-14)
    def test_regrid_is_not_equilibrium(self):
        a=Grid(np.linspace(0,3,7),np.linspace(0,2,9))
        b=Grid(np.linspace(0,6,15),np.linspace(0,8,17))
        f=np.zeros(a.shape);f[4,4]=.5;f[2,6]=.5
        g=regrid_measure(f,a,b)
        self.assertAlmostEqual(g@b.m,f.ravel()@a.m,places=13)
        self.assertAlmostEqual(g@b.k,f.ravel()@a.k,places=13)
if __name__=="__main__":unittest.main()
