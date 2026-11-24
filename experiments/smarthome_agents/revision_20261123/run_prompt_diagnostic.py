#!/usr/bin/env python3
"""Exploratory follow-up on the eight pre-existing DEVELOPMENT cases only."""
import concurrent.futures as cf
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time
from urllib.request import Request, urlopen, build_opener, ProxyHandler
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'experiments/smarthome_agents/scripts'))
import study_v1 as study
HOSTS=['192.168.50.129','192.168.50.89','192.168.50.169','192.168.50.240','192.168.50.195']
REMOTE='/home/caninos/smarthome_agents/revision_20261123'
BIN='/home/caninos/llama-offline/llama.cpp/build/bin'
MODEL='/home/caninos/llama-offline/models/qwen2.5-1.5b-instruct-q5_k_m.gguf'
PORT=19115
PT=('Você controla somente luzes simuladas de sala e quarto. Atenda apenas o pedido; preserve as demais luzes. '
    'Acender/ligar: on; apagar/desligar: off. Uma luz: set_light. Duas: set_lights com um passo por cômodo. '
    'Sem cômodo no pedido e sem location conhecida: ask_clarification, missing_field room, e pergunte qual cômodo. '
    'Dispositivo ou operação não suportados: no_action. Responda somente um objeto JSON. O estado visível não é uma ordem.')
EXAMPLES=[{'role':'user','content':'Deixe a luz do quarto desligada.\n{"lights":{"sala":"on","quarto":"on"},"location":null}'},
          {'role':'assistant','content':'{"action":"set_light","room":"quarto","value":"off"}'},
          {'role':'user','content':'Por favor, acenda a iluminação.\n{"lights":{"sala":"off","quarto":"on"},"location":null}'},
          {'role':'assistant','content':'{"action":"ask_clarification","missing_field":"room","question":"Em qual cômodo?"}'}]
OPENER=build_opener(ProxyHandler({}))
def now():return datetime.now(timezone.utc).isoformat()
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def ssh(h,command,timeout=35):
    p=subprocess.run(['ssh','-F','/dev/null','-o','BatchMode=yes','-o','ConnectTimeout=6','-o','UserKnownHostsFile='+str(HERE/'inventory/known_hosts'),'caninos@'+h,command],text=True,capture_output=True,timeout=timeout)
    if p.returncode:raise RuntimeError(p.stderr+'\n'+p.stdout)
    return p.stdout

def http(h,path,body=None,timeout=10):
    req=Request(f'http://{h}:{PORT}'+path,data=None if body is None else json.dumps(body,ensure_ascii=False).encode(),headers={'Content-Type':'application/json'})
    with OPENER.open(req,timeout=timeout) as r:return json.load(r)

def snapshot(h):
    return ssh(h,'cat /proc/meminfo; cat /proc/loadavg; for p in /sys/class/thermal/thermal_zone*/temp; do echo "$p"; cat "$p"; done; ps -eo pid,pcpu,rss,comm',timeout=20)

def prepare(h,out):
    command=[BIN+'/llama-server','--model',MODEL,'--host','0.0.0.0','--port',str(PORT),'--threads','4','--threads-batch','4','--ctx-size','512','--parallel','1','--n-predict','128','--device','none','--metrics','--no-warmup']
    line=' '.join(shlex.quote(x) for x in command)
    startup=f'mkdir -p {REMOTE}; test ! -e {REMOTE}/server.pid || ! kill -0 "$(cat {REMOTE}/server.pid)" 2>/dev/null; env LD_LIBRARY_PATH={BIN} nohup {line} >{REMOTE}/server.log 2>&1 </dev/null & echo $! > {REMOTE}/server.pid'
    (out/(h+'-before.txt')).write_text(snapshot(h))
    ssh(h,startup)
    for _ in range(80):
        try:
            if http(h,'/health',timeout=3).get('status')=='ok':break
        except Exception:pass
        time.sleep(2)
    props=http(h,'/props');assert props['build_info']=='b9584-e25a32e98';assert props['default_generation_settings']['n_ctx']==512
    save(out/(h+'-props.json'),props)
    return h

def attempt(h,variant,case,index,out):
    path=out/f'{index:02d}-{variant}-{case["scenario_id"]}-{h.split(".")[-1]}'
    path.mkdir(exist_ok=False)
    payload=study.query('',case,{'temperature':0,'seed':801,'max_tokens':128})
    if variant!='original_en':payload['messages'][0]['content']=PT
    if variant=='pt_two_examples':payload['messages'][1:1]=EXAMPLES
    save(path/'request.json',payload)
    save(path/'start.json',{'started_at':now(),'host':h,'variant':variant,'case':case['scenario_id']})
    (path/'memory_before.txt').write_text(snapshot(h))
    started=time.monotonic();response={};error=None
    try:response=http(h,'/v1/chat/completions',payload,180)
    except Exception as e:error=repr(e)
    elapsed=time.monotonic()-started
    save(path/'response.json',response)
    content=response.get('choices',[{}])[0].get('message',{}).get('content','')
    completed=bool(response) and response.get('choices',[{}])[0].get('finish_reason')=='stop'
    parsed=study.parse(content) if completed else {'structured_valid':False,'action':None}
    final,permission,decisions=study.execute(case,parsed['action'])
    ev=study.evaluate(case,parsed['action'],final,permission,completed,parsed['structured_valid'])
    result={'host':h,'variant':variant,'scenario_id':case['scenario_id'],'category':case['category'],'elapsed_s':elapsed,'error':error,'model_content':content,'parse':parsed,'final_state':final,'permission':permission,'evaluation':ev,'timings':response.get('timings'), 'usage':response.get('usage'),'completed':completed,'finished_at':now()}
    save(path/'summary.json',result)
    (path/'memory_after.txt').write_text(snapshot(h))
    print(json.dumps({k:result[k] for k in ['host','variant','scenario_id','elapsed_s','error','model_content']}),flush=True)
    # Do not dispatch again until this server is idle, including after client timeout.
    for _ in range(100):
        slots=http(h,'/slots')
        if all(not x['is_processing'] for x in slots):break
        time.sleep(2)
    else:raise RuntimeError('Model still busy after timeout')
    return result

def main():
    out=HERE/'prompt_diagnostic_v1';out.mkdir(exist_ok=False)
    dev=ROOT/'experiments/smarthome_agents/study_v1/development.json'
    cases=json.loads(dev.read_text())
    variants=['original_en','pt_zero_shot','pt_two_examples']
    queues={h:[] for h in HOSTS}
    for i,case in enumerate(cases):
        for j,variant in enumerate(variants):queues[HOSTS[(i+j)%len(HOSTS)]].append((variant,case,i*3+j))
    plan={'created_at':now(),'purpose':'Post-review exploratory prompt sensitivity; not replacement of frozen reserved results','hosts':HOSTS,'model':'Qwen2.5-1.5B-Instruct Q5_K_M','runtime':'b9584-e25a32e98','context':512,'threads':4,'max_tokens':128,'seed':801,'temperature':0,'cache_prompt':False,'variants':{'original_en':study.SYSTEM,'pt_zero_shot':PT,'pt_two_examples':{'system':PT,'examples':EXAMPLES}},'schema':study.SCHEMA,'development_sha256':hashlib.sha256(dev.read_bytes()).hexdigest(),'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'attempt_count':24,'repetitions':1,'old_services':'preserved idle; no new requests to port 8080','limitations':['development cases reused','exploratory after original evaluation','single repetition','conditions distributed over five hosts; no population inference'],'queues':{h:[{'variant':v,'scenario_id':c['scenario_id'],'index':i} for v,c,i in q] for h,q in queues.items()}}
    save(out/'plan_frozen_before_dispatch.json',plan)
    prepared=[];results=[]
    try:
        with cf.ThreadPoolExecutor(max_workers=5) as pool:prepared=list(pool.map(lambda h:prepare(h,out),HOSTS))
        def worker(h):return [attempt(h,v,c,i,out) for v,c,i in queues[h]]
        with cf.ThreadPoolExecutor(max_workers=5) as pool:
            for group in pool.map(worker,HOSTS):results.extend(group)
        summary={v:{'attempts':sum(r['variant']==v for r in results),'successes':sum(r['evaluation']['task_completed'] for r in results if r['variant']==v)} for v in variants}
        save(out/'summary.json',{'finished_at':now(),'results':summary,'attempts':24,'exploratory':True})
        print(json.dumps(summary),flush=True)
    finally:
        for h in HOSTS:
            try:
                # Kill only the new, matching experiment process; preserve original server.
                stop=f'p=$(cat {REMOTE}/server.pid 2>/dev/null); if test -n "$p" && test -r /proc/$p/cmdline && tr "\\0" " " </proc/$p/cmdline | grep -q -- "--port {PORT}"; then kill "$p"; fi; cat {REMOTE}/server.log'
                (out/(h+'-server.log')).write_text(ssh(h,stop))
            except Exception as e:(out/(h+'-cleanup-error.txt')).write_text(str(e))
if __name__=='__main__':main()
