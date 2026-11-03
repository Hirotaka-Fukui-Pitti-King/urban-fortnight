"""Mass/first-moment conserving adaptive portfolio grids, Molico-Zhang Section 4.

Regridding must not create or destroy capital/fiat money, or silently clip a
positive-mass portfolio. Grid expansion of continuation V is NOT a simple
extrapolation: evaluate the Bellman operator at new nodes when expanding.
"""
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class Grid:
    capital: np.ndarray
    money: np.ndarray
    def __post_init__(self):
        for name in ("capital","money"):
            a=np.asarray(getattr(self,name))
            if a.ndim!=1 or len(a)<2 or not np.all(np.isfinite(a)):
                raise ValueError(f"invalid {name}")
            if a[0]<0 or np.any(np.diff(a)<=0):
                raise ValueError(f"{name} grid must be nonnegative and strictly increasing")
    @property
    def k(self):return np.repeat(self.capital,len(self.money))
    @property
    def m(self):return np.tile(self.money,len(self.capital))
    @property
    def shape(self):return (len(self.capital),len(self.money))

def original_step6_grid(wmax,price,nk,nm,existing=None,safety=1.):
    """Source step 6: kmax=2wmax; mmax=2wmax*price; cover existing support."""
    if not np.isfinite(wmax) or wmax<=0 or not np.isfinite(price) or price<=0:
        raise ValueError("positive finite wealth and price required")
    if nk<2 or nm<2 or safety<1:raise ValueError("bad dimension/safety")
    kmax=2*wmax*safety;mmax=2*wmax*price*safety
    if existing is not None:
        oldk,oldm=existing
        kmax=max(kmax,float(oldk));mmax=max(mmax,float(oldm))
    return Grid(np.linspace(0,kmax,nk),np.linspace(0,mmax,nm))

def _bracket(nodes,x,atol=1e-12):
    if x<nodes[0]-atol or x>nodes[-1]+atol:
        raise ValueError(f"state {x} outside new grid [{nodes[0]},{nodes[-1]}]")
    x=min(max(x,nodes[0]),nodes[-1])
    i=int(np.clip(np.searchsorted(nodes,x,side="right")-1,0,len(nodes)-2))
    return i,(x-nodes[i])/(nodes[i+1]-nodes[i])

def regrid_measure(weights,source,target,moment_tolerance=1e-10):
    """Barycentric tensor projection preserves mass, E[k], E[m] exactly.

    This does NOT preserve joint covariance, nonlinear utilities, or an
    invariant distribution; it cannot be used to conceal boundary problems.
    """
    f=np.asarray(weights,dtype=float).reshape(source.shape)
    if not np.isfinite(f).all() or f.min()<-1e-14:
        raise ValueError("invalid original weights")
    if abs(f.sum()-1)>1e-9:raise ValueError("old mass must sum to one")
    output=np.zeros(target.shape)
    for a in range(len(source.capital)):
        for b in range(len(source.money)):
            mass=f[a,b]
            if mass<=0:continue
            i,x=_bracket(target.capital,source.capital[a])
            j,z=_bracket(target.money,source.money[b])
            output[i,j]+=mass*(1-x)*(1-z)
            output[i+1,j]+=mass*x*(1-z)
            output[i,j+1]+=mass*(1-x)*z
            output[i+1,j+1]+=mass*x*z
    old=np.array([f.sum(),f.ravel()@source.k,f.ravel()@source.m])
    new=np.array([output.sum(),output.ravel()@target.k,output.ravel()@target.m])
    if np.max(np.abs(old-new))>moment_tolerance*max(1,np.max(abs(old))):
        raise AssertionError(f"mass/first moments changed: {old-new}")
    if output.min()<-1e-12:raise AssertionError("negative mass")
    return output.ravel()

def occupied_support(weights,grid,tol=1e-15):
    f=np.asarray(weights).ravel()
    if len(f)!=len(grid.k) or not np.isfinite(f).all():raise ValueError("invalid weights")
    mask=f>tol
    if not mask.any():raise ValueError("empty occupied mass")
    return float(grid.k[mask].max()),float(grid.m[mask].max())

def interpolate_value_bilinear(values,source,target):
    """No extrapolation: source V domain must contain every target node."""
    V=np.asarray(values).reshape(source.shape);out=np.empty(target.shape)
    for i,k in enumerate(target.capital):
        a,x=_bracket(source.capital,k)
        for j,m in enumerate(target.money):
            b,z=_bracket(source.money,m)
            out[i,j]=(V[a,b]*(1-x)*(1-z)+V[a+1,b]*x*(1-z)
                      +V[a,b+1]*(1-x)*z+V[a+1,b+1]*x*z)
    return out.ravel()
