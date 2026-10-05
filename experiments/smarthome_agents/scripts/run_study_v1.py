#!/usr/bin/env python3
"""Balanced, one request per host; immutable attempt files and raw responses."""
import argparse
import concurrent.futures as cf
import hashlib
import json
import math
import subprocess
import time
import threading
from datetime import datetime,timezone
from pathlib import Path
from urllib import request
import study_v1 as study
import smarthome_pilot as pilot
from prepare_hosts_v1 import HOSTS, BASE, ssh

ROOT=Path(__file__).resolve().parents[3]
CONFIG={'temperature':0,'max_tokens':128,'seeds':[801,802],'timeout_s':180,'cache_prompt':False}
PORTS={'05':19005,'15':19015,'rules':19000}

def now():return datetime.now(timezone.utc).isoformat()
def save(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
def get(url):
    with request.urlopen(url,timeout=8) as r:return json.load(r)

def memory(host,model):
    directory=BASE+'/'+('rules' if model=='rules' else model)
    return ssh(host,'p=$(cat '+directory+'/server.pid); cat /proc/$p/status; cat /proc/loadavg; cat /proc/meminfo; ps -eo pid,pcpu,rss,comm',timeout=20)

def attempt(host,model,sc,rep,out,barrier=None):
    aid=f"{model}-{sc['scenario_id']}-rep{rep+1}-{host.split('.')[-1]}"
    d=out/'attempts'/aid;d.mkdir(parents=True,exist_ok=False)
    params={'temperature':CONFIG['temperature'],'max_tokens':CONFIG['max_tokens'],'seed':CONFIG['seeds'][rep]}
    url=f'http://{host}:{PORTS[model]}'
    payload={'scenario':{k:sc[k] for k in ('resident_request','initial_state','permissions')}} if model=='rules' else study.query(url,sc,params)
    save(d/'request.json',payload)
    start_record={'attempt_id':aid,'host':host,'model':model,'scenario_id':sc['scenario_id'],'category':sc['category'],'repetition':rep+1,'params':params,'url':url,'started_at':now()}
    save(d/'start.json',start_record)
    mem_error=[]
    try:(d/'memory_before.txt').write_text(memory(host,model))
    except Exception as e:mem_error.append(str(e))
    if barrier:barrier.wait(timeout=60)
    encoded=json.dumps(payload,ensure_ascii=False).encode()
    started=time.monotonic();# Dispatch clock is immediately before the HTTP call; exclude log I/O.
    completed=False;raw='';response={};error=None
    try:
        req=request.Request(url+'/v1/chat/completions',data=encoded,headers={'Content-Type':'application/json'})
        with request.urlopen(req,timeout=CONFIG['timeout_s']) as r:
            raw=r.read().decode();response=json.loads(raw);completed=r.status==200
    except Exception as e:error=f'{type(e).__name__}: {e}'
    ended=time.monotonic();elapsed=ended-started
    (d/'response.txt').write_text(raw)
    try:(d/'memory_after.txt').write_text(memory(host,model))
    except Exception as e:mem_error.append(str(e))
    content=response.get('choices',[{}])[0].get('message',{}).get('content','')
    finish=response.get('choices',[{}])[0].get('finish_reason')
    parsed=study.parse(content) if completed and finish=='stop' else {'structured_valid':False,'action':None,'reason':error or 'non_stop_finish'}
    final,p,decisions=study.execute(sc,parsed['action'])
    ev=study.evaluate(sc,parsed['action'],final,p,completed,parsed['structured_valid'])
    usage=response.get('usage',{});timings=response.get('timings',{})
    cache_n=timings.get('cache_n',usage.get('prompt_tokens_details',{}).get('cached_tokens',0))
    result={**start_record,'finished_at':now(),'dispatch_monotonic_s':started,'response_monotonic_s':ended,
            'elapsed_s':elapsed,'execution_completed':completed,'finish_reason':finish,'error':error,
            'memory_errors':mem_error,'model_content':content,'parse':parsed,'validation':p,'step_permissions':decisions,
            'final_state':final,'evaluation':ev,'usage':usage,'timings':timings,'cache_tokens':cache_n,
            'returned_model':response.get('model'),'system_fingerprint':response.get('system_fingerprint'),
            'action_applied':bool(study.light_steps(parsed['action'])) and p['allowed']}
    save(d/'summary.json',result)
    print(aid+' '+('success' if ev['task_completed'] else 'fail')+f' {elapsed:.2f}s',flush=True)
    return result

def verify(out):
    properties={}
    for h in HOSTS:
        properties[h]={}
        for model in ['05','15','rules']:
            url=f'http://{h}:{PORTS[model]}'
            props=get(url+('/health' if model=='rules' else '/props'))
            properties[h][model]=props
            if model!='rules':
                assert props['total_slots']==1,(h,model,props['total_slots'])
                assert props['default_generation_settings']['n_ctx']==512
                assert props['build_info']=='b9584-e25a32e98'
                assert ('0.5b' if model=='05' else '1.5b') in props['model_path'].lower()
    save(out/'properties.json',properties)

def quality(cases,out,models):
    # Each scenario/model pair has repetitions on different hosts. Round robin
    # starts each host with a different model; all hosts see all models.
    queues={h:[] for h in HOSTS}
    for mi,model in enumerate(models):
        for i,sc in enumerate(cases):
            for rep in range(2):
                host=HOSTS[(i+rep*3+mi*2)%len(HOSTS)]
                queues[host].append((model,sc,rep))
    def worker(host):
        # Interleave model conditions deterministically on each host.
        tasks=sorted(queues[host],key=lambda t:(t[1]['scenario_id'],t[2],t[0]))
        return [attempt(host,*t,out) for t in tasks]
    with cf.ThreadPoolExecutor(max_workers=6) as pool:
        futures=[pool.submit(worker,h) for h in HOSTS]
        for f in cf.as_completed(futures):f.result()

def scale(cases,out,models):
    # Fixed six-request workload, independent copies of the simulator state.
    batch=[cases[i] for i in [0,8,16,24,32,17]]
    for model in models:
        for n in [1,3,6]:
            for rep in range(2):
                hosts=[HOSTS[(rep*3+j)%6] for j in range(n)]
                condition=out/f'scale-{model}-n{n}-rep{rep+1}';condition.mkdir()
                all_results=[];batch_start=time.monotonic()
                for offset in range(0,6,n):
                    barrier=threading.Barrier(n)
                    with cf.ThreadPoolExecutor(max_workers=n) as pool:
                        futures=[pool.submit(attempt,hosts[j],model,batch[offset+j],rep,condition,barrier) for j in range(n)]
                        all_results.extend(f.result() for f in futures)
                # Time window uses dispatch-to-last-response, excludes memory snapshots.
                first=min(r['dispatch_monotonic_s'] for r in all_results)
                last=max(r['response_monotonic_s'] for r in all_results)
                span=last-first
                save(condition/'batch.json',{'model':model,'replicas':n,'repetition':rep+1,'hosts':hosts,
                    'requests':6,'successes':sum(r['evaluation']['task_completed'] for r in all_results),
                    'window_s':span,'completed_tasks_per_min':sum(r['evaluation']['task_completed'] for r in all_results)*60/span,
                    'responses_per_min':sum(r['execution_completed'] for r in all_results)*60/span,
                    'note':'fixed six-request closed batch; includes dispatch gaps between waves; no inference concurrency per host'})

def main():
    a=argparse.ArgumentParser();a.add_argument('--phase',choices=['development','quality','scale'],required=True);a.add_argument('--out',type=Path,required=True);a.add_argument('--models',default='rules,05,15');args=a.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    cases_path=ROOT/'experiments/smarthome_agents/study_v1'/('development.json' if args.phase=='development' else 'reserved.json')
    models=args.models.split(',')
    assert all(m in PORTS for m in models)
    if args.phase!='development':
        freeze=pilot.load_json(ROOT/'experiments/smarthome_agents/study_v1/freeze.json')
        for name,digest in freeze['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    save(args.out/'campaign.json',{'phase':args.phase,'started_at':now(),'hosts':HOSTS,'models':models,'configuration':CONFIG,
        'scenario_file':str(cases_path.relative_to(ROOT)),'scenario_sha256':hashlib.sha256(cases_path.read_bytes()).hexdigest(),
        'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()})
    verify(args.out)
    cases=json.loads(cases_path.read_text())
    if args.phase=='scale':scale(cases,args.out,models)
    else:quality(cases,args.out,models)
    save(args.out/'completed.json',{'finished_at':now(),'status':'all_planned_attempts_recorded'})
if __name__=='__main__':main()
