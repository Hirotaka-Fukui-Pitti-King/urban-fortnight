"""One original-Step-6 adaptive regridding connected to the CM->DM transition.

This is an accounting/integration smoke test, NOT an adaptive stationary GE
solver. Old V is linearly extended to NEW nodes *only as a guess*. To solve a
true adaptive Bellman fixed point, re-evaluate its operator on new nodes.
"""
from dataclasses import replace
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from adaptive_grids import (Grid,original_step6_grid,occupied_support,
                            regrid_measure)
from continuous_core import ContinuousModel
from source_aligned import clear_CM_entrants, next_DM, CMPriceFailure

def adapt_single_source_step(old,V,entrants,price_hint=3.):
    """First CM price clear on old nodes, then source Step 6 regridding and a
    fresh conditional CM/DM market update on new nodes, preserving issuer cash.
    """
    previous=clear_CM_entrants(old,V,entrants,price_hint=price_hint)
    old_post=Grid(old.postkg,old.postmg)
    old_savings=Grid(old.kg,old.mg)
    supported=entrants>1e-15
    wealth=old.postk[supported]+old.postm[supported]/previous["price"]
    wmax=float(np.max(wealth))
    occupied=occupied_support(previous["f"],old_savings)
    new_bounds=original_step6_grid(wmax,previous["price"],old.p.nk,
                                   old.p.nm,existing=occupied)
    new_par=replace(old.p,kmax=float(new_bounds.capital[-1]),
                     mmax=float(new_bounds.money[-1]))
    new=ContinuousModel(new_par)
    new_savings=Grid(new.kg,new.mg)
    new_post=Grid(new.postkg,new.postmg)
    carried_ent=regrid_measure(entrants,old_post,new_post)
    carried_dm=regrid_measure(previous["f"],old_savings,new_savings)
    prior=np.array([entrants.sum(),entrants@old.postk,entrants@old.postm])
    regridded=np.array([carried_ent.sum(),carried_ent@new.postk,
                        carried_ent@new.postm])
    # The old V grid does not cover the expanded new grid. This extrapolation
    # is strictly a STARTING GUESS; it is not an accurate Bellman update.
    interpolation=RegularGridInterpolator((old.kg,old.mg),
            np.asarray(V).reshape(old.p.nk,old.p.nm),
            method="linear",bounds_error=False,fill_value=None)
    guess=interpolation(np.column_stack((new.k,new.m)))
    report=dict(status="ADAPTIVE_STEP_ACCOUNTING_ONLY_NOT_STATIONARY_GE",
         wmax=wmax,old_price=float(previous["price"]),
         old_bounds=dict(k=float(old.kg[-1]),m=float(old.mg[-1])),
         new_bounds=dict(k=float(new.kg[-1]),m=float(new.mg[-1])),
         incoming_moment_differences=(regridded-prior).tolist(),
         remapped_DM_moments=dict(money=float(carried_dm@new.m),
             capital=float(carried_dm@new.k)),
         issuer_money_before=float(entrants@old.postm),
         issuer_money_after_regrid=float(carried_ent@new.postm),
         old_CM_money=float(previous["money"]),
         value_on_new_grid="LINEARLY_EXTRAPOLATED_INITIAL_GUESS_ONLY",
         source_step6_implemented=True,source_steps7_8_adaptive_fixed_point=False,
         certified_GE=False)
    try:
        auction=clear_CM_entrants(new,guess,carried_ent,
                                  price_hint=previous["price"])
        nv,after,dm=next_DM(new,guess,auction["f"],auction["price"])
        report.update(second_auction_status="CLEARED",
            second_price=float(auction["price"]),
            second_CM_fiat=float(auction["money"]),
            second_DM_fiat=float(after@new.postm),
            second_CM_budget=float(auction["budget_error"]),
            second_distribution_mass=float(after.sum()),
            second_Bellman_guess_residual=float(max(abs(nv-guess))),
            second_DM_trade_rate=float(dm["trades"]))
        assert abs(auction["money"]-1)<1e-8
        assert abs(after@new.postm-1)<1e-8
        assert abs(auction["budget_error"])<1e-8
        assert abs(after.sum()-1)<1e-9
    except CMPriceFailure as exc:
        report.update(second_auction_status="NO_CONDITIONAL_PRICE",
                      second_auction_failure=str(exc))
    return report
