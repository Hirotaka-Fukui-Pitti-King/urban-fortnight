"""Execute fixed-policy one-step feedback calculation and serialize diagnostics."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from joint_model import Model
from collision_feedback import feedback_diagnostic
m=Model()
s=m.solve_inner(4.5,.97,.65)
if not s['info']['converged']:
    raise RuntimeError("No valid fixed-price reference")
result=feedback_diagnostic(m,s)
(ROOT/"results").mkdir(parents=True,exist_ok=True)
(ROOT/"results"/"kinetic_feedback_diagnostic.json").write_text(
    json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
