"""Bound Nash surplus globally for a monotone CM value W.

This verifies the *interpolated* fixed-price private problem, not the
undiscretized source economy. Exact-arithmetic box bounds require only W
nondecreasing and cost nondecreasing, not concavity or differentiability.
Finite floating-point rounding is not interval-enclosed: numerical_only=True.
"""
from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush
from math import isfinite, log
from typing import Callable


@dataclass(frozen=True)
class NashCertificate:
    quantity: float
    real_payment: float
    lower_log_nash: float
    upper_log_nash: float
    gap_log_nash: float
    boxes_examined: int
    bounded_to_tolerance: bool
    candidate_positive: bool
    numerical_only: bool = True


def bound_nash(
    W: Callable[[float], float],
    cost: Callable[[float], float],
    buyer_wealth: float,
    seller_wealth: float,
    cash_real: float,
    production_cap: float,
    buyer_weight: float,
    *,
    initial: tuple[float, float] | None = None,
    log_gap_tolerance: float = 1e-2,
    max_boxes: int = 100_000,
) -> NashCertificate:
    """Numerically bracket the best positive generalized Nash product.

    Use real payment x=d/p, and y in [0,cap), x in [0,cash_real].
    Positive buyer surplus requires x<y. For a box [yl,yu] x [xl,xu],
    monotonicity gives
        B <= W(wb + yu-xl)-W(wb)
        S <= W(ws+min(xu,yu))-W(ws)-cost(max(yl,xl)).
    Thus the Nash log upper bound is theta*log(Bupper) +
    (1-theta)*log(Supper), provided both upper surpluses are positive.
    """
    if not 0 < buyer_weight < 1:
        raise ValueError("buyer_weight must lie in (0,1)")
    if cash_real < 0 or production_cap < 0:
        raise ValueError("economic bounds must be nonnegative")
    if log_gap_tolerance <= 0 or max_boxes <= 0:
        raise ValueError("numeric tolerances and budget must be positive")
    if cash_real == 0 or production_cap == 0:
        return NashCertificate(0., 0., float("-inf"), float("-inf"), 0.,
                               0, True, False)
    base_b, base_s = W(buyer_wealth), W(seller_wealth)
    if not (isfinite(base_b) and isfinite(base_s)):
        raise ValueError("CM outside values were not finite")

    def objective(y: float, x: float) -> float:
        if not (0 < y < production_cap and 0 < x <= cash_real and x < y):
            return float("-inf")
        B = W(buyer_wealth+y-x)-base_b
        S = W(seller_wealth+x)-base_s-cost(y)
        if not (isfinite(B) and isfinite(S)):
            raise ValueError("nonfinite surplus")
        if B <= 0 or S <= 0:
            return float("-inf")
        return buyer_weight*log(B)+(1-buyer_weight)*log(S)

    def bound(box: tuple[float,float,float,float]) -> float:
        yl,yu,xl,xu=box
        if xl >= yu:
            return float("-inf")
        yl=max(yl,xl)
        xu=min(xu,yu)
        if yl >= yu or xu <= 0:
            return float("-inf")
        B=W(buyer_wealth+yu-xl)-base_b
        S=W(seller_wealth+xu)-base_s-cost(yl)
        if B <= 0 or S <= 0:
            return float("-inf")
        if not (isfinite(B) and isfinite(S)):
            raise ValueError("nonfinite box bound")
        return buyer_weight*log(B)+(1-buyer_weight)*log(S)

    best=float("-inf")
    best_y=best_x=0.
    def consider(y: float,x: float) -> None:
        nonlocal best,best_y,best_x
        v=objective(y,x)
        if v>best:
            best,best_y,best_x=v,y,x

    if initial is not None:
        consider(*initial)

    def try_box(box: tuple[float,float,float,float]) -> None:
        yl,yu,xl,xu=box
        y=(yl+yu)*0.5
        if not 0<y<production_cap:
            return
        consider(y,min((xl+xu)*0.5,y*0.75))
        upper=min(xu,cash_real,y)
        if upper>xl:
            consider(y,(xl+upper)*0.5)

    box0=(0.,production_cap,0.,cash_real)
    try_box(box0)
    heap=[]
    heappush(heap,(-bound(box0),0,box0))
    examined=0
    counter=0
    while heap and examined<max_boxes:
        if best>float("-inf") and -heap[0][0]-best<=log_gap_tolerance:
            break
        neg,_,box=heappop(heap)
        if -neg<=best:
            continue
        yl,yu,xl,xu=box
        if (yu-yl)/production_cap>=(xu-xl)/cash_real:
            mid=(yl+yu)*0.5
            children=((yl,mid,xl,xu),(mid,yu,xl,xu))
        else:
            mid=(xl+xu)*0.5
            children=((yl,yu,xl,mid),(yl,yu,mid,xu))
        examined+=1
        for child in children:
            ub=bound(child)
            if ub<=best:
                continue
            try_box(child)
            if ub<=best:
                continue
            counter+=1
            heappush(heap,(-ub,counter,child))
    upper=max(best,-heap[0][0]) if heap else best
    gap=max(0.,upper-best) if best>float("-inf") else (
        0. if upper==float("-inf") else float("inf"))
    return NashCertificate(best_y,best_x,best,upper,gap,examined,
                           gap<=log_gap_tolerance,best>float("-inf"))
