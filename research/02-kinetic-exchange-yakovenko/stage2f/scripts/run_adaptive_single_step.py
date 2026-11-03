"""Execute one asset-conserving original-Step-6 adaptive CM->DM update."""
from pathlib import Path
import sys,json
import numpy as np
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/"src"))
sys.path.insert(0,str(HERE.parent/"stage2e"/"src"))
sys.path.insert(0,str(HERE.parent/"stage2c"/"src"))
from molico_grid import Calibration
from continuous_core import ContinuousModel
from source_aligned import make_CM_entrants
from adaptive_source_step import adapt_single_source_step
model=ContinuousModel(Calibration(nk=5,nm=5,kmax=3,mmax=2,y_choices=4,d_choices=5))
V=5*(model.k+model.m/3.)+.02*np.sin(model.k)+.003*np.sin(2*model.m)
entrants=make_CM_entrants(model,1.5,1.)
report=adapt_single_source_step(model,V,entrants)
print(json.dumps(report,indent=2))
assert not report["certified_GE"]
assert abs(report["issuer_money_after_regrid"]-1)<1e-10
assert max(abs(x) for x in report["incoming_moment_differences"])<1e-9
out=HERE/"results";out.mkdir(exist_ok=True)
(out/"adaptive_single_source_step.json").write_text(json.dumps(report,indent=2)+"\n")
