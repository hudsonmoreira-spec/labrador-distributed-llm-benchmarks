#!/usr/bin/env python3
import json,time,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import run_prompt_diagnostic as d
import hybrid
HERE=Path(__file__).resolve().parent
OUT=HERE/'hybrid_development_v1';OUT.mkdir(exist_ok=False)
d.PORT=19119
cases=json.loads((d.ROOT/'experiments/smarthome_agents/study_v1/development.json').read_text())
d.save(OUT/'plan_before_dispatch.json',{'at':d.now(),'purpose':'Development-only hybrid intent classification; separate configuration, not pure model action evaluation','cases':[c['scenario_id'] for c in cases],'intent_system':hybrid.INTENT_SYSTEM,'examples':hybrid.EXAMPLES,'schema':hybrid.INTENT_SCHEMA,'rules':['explicit room matching','known-location fallback','ask missing room','split conjunction into at most two clauses','no evaluator access in controller']})
rs=[]
for c in cases:
 p=OUT/c['scenario_id'];p.mkdir();calls=[]
 def call(body):
  i=len(calls);d.save(p/f'request-{i}.json',body)
  response=d.http('127.0.0.1','/v1/chat/completions',body,120);d.save(p/f'response-{i}.json',response);calls.append(response);return response
 start=time.monotonic();action,traces,origin=hybrid.interpret(c,call,d.study.pilot.normalize_text);elapsed=time.monotonic()-start
 parsed=d.study.parse(json.dumps(action));final,permission,_=d.study.execute(c,action);ev=d.study.evaluate(c,action,final,permission,True,parsed['structured_valid'])
 r={'case':c['scenario_id'],'action':action,'origin':origin,'elapsed_s':elapsed,'evaluation':ev};rs.append(r);d.save(p/'summary.json',r);print(json.dumps(r,ensure_ascii=False),flush=True)
d.save(OUT/'summary.json',{'successes':sum(r['evaluation']['task_completed'] for r in rs),'attempts':len(rs),'results':rs,'scope':'Development calibration, not reserved set or generalization evidence'})
