"""Conditional collision-distribution feedback, never a general-equilibrium claim.

Hold the negotiated contract and saving policy fixed at a stationary assumed
price reference. Compare actual random-pair encounters to a symmetrized
one-factor-frozen reference. Both use the same contract and conserve each
matched pair's productive assets and nominal tokens.
"""
import numpy as np

def collision(model,fb,fs,solution):
    """Gain-loss for directed buyer-seller pairs; Q[f]=collision(f,f)."""
    b,s=np.nonzero(solution['d'])
    d=solution['d'][b,s]
    wt=.5*model.p.lambda_meet*fb[b]*fs[s]
    bi=model.sid(model.ia[b],model.im[b]-d,model.iz[b])
    si=model.sid(model.ia[s],model.im[s]+d,model.iz[s])
    change=np.zeros(model.n)
    np.add.at(change,b,-wt);np.add.at(change,s,-wt)
    np.add.at(change,bi,wt);np.add.at(change,si,wt)
    return change

def directional_derivative(model,f,h,solution):
    """Frechet derivative of fixed-policy Q(f,f), exact on discrete states."""
    return collision(model,f,h,solution)+collision(model,h,f,solution)

def symmetric_reference(model,f,fstar,solution):
    """Linear, pairwise-conserving frozen-factor comparison, same at fstar."""
    return .5*(collision(model,f,fstar,solution)
             +collision(model,fstar,f,solution))

def one_step_with_pair_weights(model,f,solution,wt):
    b,s=np.nonzero(solution['d'])
    d=solution['d'][b,s]
    bi=model.sid(model.ia[b],model.im[b]-d,model.iz[b])
    si=model.sid(model.ia[s],model.im[s]+d,model.iz[s])
    qi=solution['q'][b,s]
    mass=np.zeros((model.n,len(model.q)))
    mass[:,0]=f
    np.add.at(mass[:,0],b,-wt);np.add.at(mass[:,0],s,-wt)
    np.add.at(mass[:,0],bi,wt);np.add.at(mass,(si,qi),wt)
    if mass.min() < -1e-12:
        raise ValueError("Counterfactual distribution has negative probability")
    actions=np.einsum('sq,sqj->sj',mass,solution['pi'])
    new=np.zeros((model.na,model.nm,model.nz))
    for iz in range(model.nz):
        a=actions[model.iz==iz,:].sum(axis=0).reshape(model.na,model.nm)
        for iz2 in range(model.nz):
            new[:,:,iz2]+=a*model.Pz[iz,iz2]
    return new.ravel()

def feedback_diagnostic(model,solution,displacement=.01):
    f=solution['f']
    h=np.zeros_like(f)
    for ia,im,sign in ((0,0,1),(1,2,1),(0,2,-1),(1,0,-1)):
        h[model.sid(ia,im,0)]+=sign
    shifted=f+displacement*h
    if shifted.min()<0:
        raise ValueError("Initial distribution perturbation violates positivity")
    q1=collision(model,shifted,shifted,solution)
    qref=symmetric_reference(model,shifted,f,solution)
    b,s=np.nonzero(solution['d'])
    actual_wt=.5*model.p.lambda_meet*shifted[b]*shifted[s]
    ref_wt=.25*model.p.lambda_meet*(shifted[b]*f[s]+f[b]*shifted[s])
    next1=one_step_with_pair_weights(model,shifted,solution,actual_wt)
    nextref=one_step_with_pair_weights(model,shifted,solution,ref_wt)
    epsilon=1e-5
    finite=(collision(model,f+epsilon*h,f+epsilon*h,solution)
           -collision(model,f-epsilon*h,f-epsilon*h,solution))/(2*epsilon)
    exact=directional_derivative(model,f,h,solution)
    a=model.a[model.ia];money=model.m[model.im]
    return {
        "perturbation":displacement,
        "initial_asset_mean_change":float(displacement*h@a),
        "initial_money_mean_change":float(displacement*h@money),
        "maximum_bilinear_derivative_error":float(np.max(abs(finite-exact))),
        "kinetic_feedback_sup":float(np.max(abs(q1-qref))),
        "mass_change_actual":float(q1.sum()),
        "money_change_actual":float(q1@money),
        "money_change_reference":float(qref@money),
        "capital_change_actual":float(q1@a),
        "capital_change_reference":float(qref@a),
        "next_capital_actual":float(next1@a),
        "next_capital_reference":float(nextref@a),
        "next_capital_difference":float((next1-nextref)@a),
        "next_distribution_tv":float(.5*np.sum(abs(next1-nextref))),
        "caveat":"One-step fixed-price, fixed-policy sensitivity only; not an equilibrium comparative static."}
