"""Separate SVG exhibits from the executed Stage 2 experiments."""
from pathlib import Path
import argparse,json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
p=argparse.ArgumentParser()
p.add_argument("--out",type=Path,default=Path(__file__).resolve().parents[1]/"results")
a=p.parse_args()
folder=a.out/"figures";folder.mkdir(parents=True,exist_ok=True)
data=json.loads((a.out/"economic_diagnostics.json").read_text())
particles=pd.read_csv(a.out/"particle_comparison.csv")
for d in data:
    name=d["model"];m=np.arange(len(d["money_distribution"]))
    fig,ax=plt.subplots(figsize=(7,4))
    ax.bar(m-.18,d["money_distribution"],width=.36,label="Optimal equilibrium")
    ax.bar(m+.18,d["maxent_distribution"],width=.36,label="Constrained entropy comparison")
    ax.set_xlabel(r"Token holdings $m$")
    ax.set_ylabel("Household probability")
    ax.legend();fig.tight_layout()
    fig.savefig(folder/(name+"_money_distribution.svg"));plt.close(fig)
    group=particles[particles["model"]==name].groupby("n_agents").average_mass_W1.agg(["mean","std"]).reset_index()
    fig,ax=plt.subplots(figsize=(7,4))
    ax.errorbar(group.n_agents,group["mean"],yerr=group["std"],marker="o",capsize=3)
    ax.set_xlabel(r"Simulated households $N$")
    ax.set_ylabel("Stationary distribution Wasserstein distance")
    fig.tight_layout()
    fig.savefig(folder/(name+"_particle_convergence.svg"));plt.close(fig)
