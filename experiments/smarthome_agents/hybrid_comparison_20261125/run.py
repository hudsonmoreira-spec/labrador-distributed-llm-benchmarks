#!/usr/bin/env python3
"""Append-only supplementary comparison; known scenarios, no silent replay."""
import argparse,concurrent.futures as cf,hashlib,json,math,random,statistics,sys,threading,time
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,build_opener,ProxyHandler
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'scripts'))
import study_v1 as study
sys.path.insert(0,str(HERE.parent/'cluster_ready_20261125'))
import provision,select_host
OPENER=build_opener(ProxyHandler({}));LOCK=threading.Lock()
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,obj):
 p.parent.mkdir(parents=True,exist_ok=True)
 tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');tmp.replace(p)
def get(h,port,path,payload=None,timeout=5):
 req=Request(f'http://{h}:{port}{path}',data=None if payload is None else json.dumps(payload,ensure_ascii=False).encode(),headers={'Content-Type':'application/json'})
 with OPENER.open(req,timeout=timeout) as f:return json.load(f)
def healthy(board):
 try:
  assert select_host.probe(board,POOL,'05')['ready']
  assert get(board['ip'],19121,'/health')['controller']=='rules_first_v1'
  return True
 except Exception:return False

def summarize(out):
 rows=[json.loads(p.read_text()) for p in (out/'attempts').glob('*/result.json')]
 summary={'phase':out.name,'generated_at':now(),'attempts_recorded':len(rows),'conditions':{}}
 for condition in ['rules','05','hybrid']:
  rs=[r for r in rows if r['condition']==condition];good=[r for r in rs if r['infrastructure_ok']]
  times=sorted(r['elapsed_s'] for r in good)
  summary['conditions'][condition]={'attempts':len(rs),'infra_failures':len(rs)-len(good),'successes':sum(r.get('evaluation',{}).get('task_completed',False) for r in rs),'pending_semantic_reviews':sum(r.get('evaluation',{}).get('review_pending',False) for r in rs),'structured_valid':sum(r.get('structured_valid',False) for r in rs),'model_calls':sum(r.get('origin') in ['model','model_fallback'] for r in rs),'fallback_calls':sum(r.get('fallback',False) for r in rs),'median_s':statistics.median(times) if times else None,'mean_s':statistics.mean(times) if times else None,'p95_s':times[math.ceil(.95*len(times))-1] if times else None,'categories':{}}
  for cat in sorted({r['category'] for r in rs}):
   cr=[r for r in rs if r['category']==cat];summary['conditions'][condition]['categories'][cat]={'attempts':len(cr),'successes':sum(r.get('evaluation',{}).get('task_completed',False) for r in cr)}
 save(out/'summary.json',summary);return summary

def make_plan(phase):
 out=HERE/phase;out.mkdir(exist_ok=False)
 path=HERE.parent/'study_v1'/('development.json' if phase=='development' else 'reserved.json')
 cases=json.loads(path.read_text());reps=1 if phase=='development' else 2
 primary=[b for b in POOL['boards'] if b['role']=='primary']
 tasks=[]
 for i,case in enumerate(cases):
  for rep in range(1,reps+1):
   for condition in ['rules','05','hybrid']:
    tasks.append({'id':f'{case["scenario_id"]}-{condition}-r{rep}','case':case,'condition':condition,'rep':rep,'seed':800+rep,'assigned_host':primary[(i+rep-1)%len(primary)]['ip']})
 random.Random(20261125).shuffle(tasks)
 inputs=[HERE/'controller.py',HERE/'run.py',HERE.parent/'scripts/study_v1.py',HERE.parent/'scripts/smarthome_pilot.py',path,HERE.parent/'cluster_ready_20261125/pool.json']
 plan={'created_before_dispatch':now(),'phase':phase,'input_hashes':{str(p.relative_to(HERE.parent.parent.parent)):sha(p) for p in inputs},'cases':len(cases),'repetitions':reps,'conditions':['rules','05','hybrid'],'task_count':len(tasks),'known_data_limitation':'Reused authored cases already inspected; supplementary descriptive comparison, not new held-out validation. No reserved outcome used to tune controller.','routing':'Original rule_response unchanged. Its single no_action means unrecognised and triggers fallback only for hybrid; recognised clarification/actions retained, including execution-policy failures. No additional invalid-request detector.','settings':{'model':'Qwen2.5-0.5B-Instruct Q5_K_M','runtime':'b9584-e25a32e98','context':512,'threads':4,'slot':1,'temperature':0,'seeds':[800+i for i in range(1,reps+1)],'max_tokens':128,'cache_prompt':False,'original_prompt_and_schema':True},'measurement':'All three conditions execute on SBC through same HTTP wrapper (19121); model calls are local loopback19115. Notebook times complete HTTP response, then executes/evaluates virtual action separately. Model loading/preparation excluded.','order_seed':20261125,'workers':5,'reserves':2,'failover':'Before dispatch only. A dispatched failure/timeout is retained, never silently retried; subsequent tasks may move to unused validated reserve.','manual_review':'Original conservative evaluator unchanged; newly pending semantic reviews remain pending, no automatic reuse of prior human judgments.','tasks':tasks}
 save(out/'plan_before_dispatch.json',plan);return out,plan

def run_phase(phase):
 global POOL
 POOL=json.loads((HERE.parent/'cluster_ready_20261125/pool.json').read_text())
 if phase=='comparison':
  dev=json.loads((HERE/'development/summary.json').read_text())
  assert dev['attempts_recorded']==24 and all(c['infra_failures']==0 for c in dev['conditions'].values())
 health=select_host.select(POOL);assert all(r['ready'] for r in health['checks']),health
 out,plan=make_plan(phase)
 # Freeze before dispatch, and validate identical controller source on every node.
 deploy=json.loads((HERE/'deployment.json').read_text())
 assert all(r['files']['controller.py']==sha(HERE/'controller.py') for r in deploy)
 for board in POOL['boards']:assert healthy(board),board
 reserves=[b for b in POOL['boards'] if b['role']=='reserve'];claimed=set();events=[]
 def replacement(old):
  with LOCK:
   for board in reserves:
    if board['ip'] not in claimed and healthy(board):
     claimed.add(board['ip']);events.append({'at':now(),'from':old['ip'],'to':board['ip']});save(out/'host_changes.json',events);return board
  raise RuntimeError('No healthy unused reserve; remaining tasks blocked, not skipped')
 def worker(initial):
  board=initial
  for task in [t for t in plan['tasks'] if t['assigned_host']==initial['ip']]:
   folder=out/'attempts'/task['id'];assert not folder.exists();folder.mkdir(parents=True)
   if not healthy(board):board=replacement(board)
   case=task['case'];operational={k:case[k] for k in ['resident_request','initial_state','permissions']}
   request={'condition':task['condition'],'seed':task['seed'],'case':operational};save(folder/'request.json',request)
   save(folder/'dispatch.json',{'at':now(),'actual_host':board,'assigned_host':initial,'id':task['id']})
   result={'id':task['id'],'scenario_id':case['scenario_id'],'category':case['category'],'condition':task['condition'],'rep':task['rep'],'host':board['ip'],'assigned_host':initial['ip'],'created_at':now(),'infrastructure_ok':False}
   started=time.monotonic()
   try:
    response=get(board['ip'],19121,'/action',request,timeout=195);elapsed=time.monotonic()-started;save(folder/'response.json',response)
    parsed=study.parse(response['content']) if response['completed'] else {'structured_valid':False,'action':None}
    final,permission,steps=study.execute(case,parsed['action'])
    evaluation=study.evaluate(case,parsed['action'],final,permission,response['completed'],parsed['structured_valid'])
    result.update(infrastructure_ok=True,elapsed_s=elapsed,origin=response['origin'],fallback=response['fallback'],completed=response['completed'],structured_valid=parsed['structured_valid'],action=parsed['action'],content=response['content'],final=final,permission=permission,evaluation=evaluation,controller_elapsed_s=response['controller_elapsed_s'])
   except Exception as e:
    result.update(elapsed_s=time.monotonic()-started,error=str(e),dispatched_outcome_uncertain=True)
    # Never replay this attempt. Quarantine the endpoint for later tasks.
    result['quarantined_host']=board['ip'];save(folder/'result.json',result)
    board=replacement(board)
   save(folder/'result.json',result)
   print(json.dumps({'id':task['id'],'host':result['host'],'infra':result['infrastructure_ok'],'success':result.get('evaluation',{}).get('task_completed'),'pending':result.get('evaluation',{}).get('review_pending'),'s':round(result['elapsed_s'],2)}),flush=True)
 with cf.ThreadPoolExecutor(5) as ex:
  list(ex.map(worker,[b for b in POOL['boards'] if b['role']=='primary']))
 summary=summarize(out);assert summary['attempts_recorded']==plan['task_count']
 print('COMPLETE '+json.dumps(summary),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('phase',choices=['development','comparison']);a=p.parse_args();run_phase(a.phase)
