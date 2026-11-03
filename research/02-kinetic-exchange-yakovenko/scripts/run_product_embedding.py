from pathlib import Path
import sys,json
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/"src"))
from product_embedding import product_checks
d=product_checks()
out=BASE/"results"
out.mkdir(parents=True,exist_ok=True)
(out/"product_embedding_checks.json").write_text(json.dumps(d,indent=2)+"\n")
print("SEPARABLE_PRODUCT_EQUILIBRIUM",d)
