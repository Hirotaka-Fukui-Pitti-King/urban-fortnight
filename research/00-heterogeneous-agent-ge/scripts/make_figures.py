"""Standalone SVG exhibits from the computed stationary distribution and policies."""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
p=argparse.ArgumentParser()
p.add_argument("--input",type=Path,default=Path(__file__).resolve().parents[1]/"results")
args=p.parse_args()
f=args.input
(f/"figures").mkdir(exist_ok=True,parents=True)
pol=pd.read_csv(f/"policy_functions.csv")
fig,ax=plt.subplots(figsize=(7,4))
for z,sub in pol.groupby("z"):
    sub=sub[sub.a<=30]
    ax.plot(sub.a,sub.savings,label=fr"$z={z:.2f}$")
ax.set_xlabel("Current assets");ax.set_ylabel("Optimal next-period assets")
ax.legend();fig.tight_layout()
fig.savefig(f/"figures"/"savings_policy.svg");plt.close(fig)
dist=pd.read_csv(f/"stationary_distribution.csv").groupby("a",as_index=False).probability.sum()
fig,ax=plt.subplots(figsize=(7,4))
ax.plot(dist.a,np.cumsum(dist.probability))
ax.set_xlabel("Assets");ax.set_ylabel("Cumulative household probability")
ax.set_xlim(0,30);ax.set_ylim(0,1)
fig.tight_layout();fig.savefig(f/"figures"/"asset_cdf.svg");plt.close(fig)
