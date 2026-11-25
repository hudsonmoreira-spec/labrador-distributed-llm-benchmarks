#!/usr/bin/env python3
"""Reconstruct decisions/scores offline and check planned operational-only inputs."""
import argparse,json,sys,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'scripts'))
import study_v1 as study
import run
ROOT=HERE.parents[2]
def load(p):return json.loads(p.read_text())
def main(phase):
 out=HERE/phase;plan=load(out/'plan_before_dispatch.json')
 for name,digest in plan['input_hashes'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
 ids={t['id'] for t in plan['tasks']};paths=list((out/'attempts').glob('*/result.json'));assert len(ids)==len(paths)==plan['task_count']
 byid={t['id']:t for t in plan['tasks']}
 for p in paths:
  result=load(p);task=byid[result['id']];case=task['case'];req=load(p.parent/'request.json')
  assert set(req['case'])=={'resident_request','initial_state','permissions'}
  assert req['case']=={k:case[k] for k in req['case']}
  assert req['condition']==task['condition'] and req['seed']==task['seed']
  assert result['infrastructure_ok'],result['id']
  raw=load(p.parent/'response.json');rule=study.rule_response(req['case'])
  expected_model=task['condition']=='05' or (task['condition']=='hybrid' and rule['action']=='no_action')
  assert bool(raw['model_request'])==expected_model
  assert raw['fallback']==(expected_model and task['condition']=='hybrid')
  if expected_model:
   assert raw['model_request']==study.query('',req['case'],{'temperature':0,'seed':task['seed'],'max_tokens':128})
   choice=raw['model_response']['choices'][0]
   assert raw['content']==choice['message'].get('content','')
  else:assert json.loads(raw['content'])==rule
  parsed=study.parse(raw['content']) if raw['completed'] else {'structured_valid':False,'action':None}
  final,permission,_=study.execute(case,parsed['action'])
  ev=study.evaluate(case,parsed['action'],final,permission,raw['completed'],parsed['structured_valid'])
  assert final==result['final'] and ev==result['evaluation']
  assert result['elapsed_s']>=raw['controller_elapsed_s']
 summary=run.summarize(out)
 report={'status':'pass','phase':phase,'planned_attempts':len(paths),'all_operational_inputs_without_evaluator':True,'routing_and_model_requests_verified':True,'scores_reconstructed':True,'frozen_inputs_unchanged':True}
 run.save(out/'audit.json',report);print(json.dumps(report))
 print(json.dumps(summary,ensure_ascii=False))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('phase',choices=['development','comparison']);main(p.parse_args().phase)
