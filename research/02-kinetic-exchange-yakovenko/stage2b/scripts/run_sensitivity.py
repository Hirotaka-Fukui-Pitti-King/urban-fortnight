"""Fixed-price sensitivity, not general equilibrium comparative statics."""
from pathlib import Path
import csv,dataclasses,sys
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'src'))
from joint_model import Model,Params
scenarios=[
 ('baseline',{}),('zero_meeting',{'lambda_meet':0}),
 ('low_meeting',{'lambda_meet':.2}),('high_meeting',{'lambda_meet':.7}),
 ('buyer_power',{'eta':.8}),('seller_power',{'eta':.2}),
 ('high_buyer_utility',{'buyer_strength':9.}),
 ('no_service_utility',{'buyer_strength':0.})]
rows=[]
for name,changes in scenarios:
    p=dataclasses.replace(Params(),**changes)
    i=Model(p).solve_inner(4.5,.97,.65)['info']
    row={'case':name,'converged':bool(i['converged']),
         'bellman_sup':i['value_residual'],'dist_sup':i['distribution_residual'],
         'K_conditional':i['capital'],'M_conditional':i['money'],
         'L_conditional':i['labor'],'services':i['service'],
         'K_market_excess':i['capital_price_consistency'],
         'M_market_excess':i['money_supply_excess'],
         'goods_market_excess':i['goods_residual']}
    rows.append(row)
out=HERE/'results';out.mkdir(parents=True,exist_ok=True)
with (out/'fixed_price_sensitivity.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
print('conditional cases',len(rows),'all inner converged',
      all(x['converged'] for x in rows))
assert all(x['converged'] for x in rows)
assert all(abs(x['K_market_excess'])>.1 for x in rows)
