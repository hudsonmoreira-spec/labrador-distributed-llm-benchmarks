#!/usr/bin/env python3
"""Same GGUF/runtime commit control on x86; separate from original paper metrics."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import run_prompt_diagnostic as d
import profiles
HERE=Path(__file__).resolve().parent
RUNTIME=Path('/home/hudymoreira/.cache/labrador-revision-20261123/llama-b9584-x86/build/bin/llama-server')
MODEL=d.ROOT/'models/qwen2.5-1.5b-instruct-q5_k_m/qwen2.5-1.5b-instruct-q5_k_m.gguf'

def campaign(profile):
 out=HERE/('x86_'+profile+'_v1');out.mkdir(exist_ok=False)
 cases=json.loads((d.ROOT/'experiments/smarthome_agents/study_v1/development.json').read_text())
 assert hashlib.sha256(MODEL.read_bytes()).hexdigest()=='b46661073c18e5b56a41fa320975f866a00def1ff08feef4718e013258896f8c'
 ctx=512 if profile=='original' else 2048
 command=[str(RUNTIME),'--model',str(MODEL),'--host','127.0.0.1','--port','19118','--threads','4','--threads-batch','4','--ctx-size',str(ctx),'--parallel','1','--n-predict','128','--device','none','--no-warmup']
 d.save(out/'plan_before_dispatch.json',{'created_at':d.now(),'purpose':'Exploratory hardware/runtime comparison and development prompt tuning, not original quality scores','runtime_commit':'e25a32e98c15a1118a976685af0f4d2c1f380079','model_sha256':hashlib.sha256(MODEL.read_bytes()).hexdigest(),'command':command,'profile':profile,'case_ids':[c['scenario_id'] for c in cases],'system':d.study.SYSTEM if profile=='original' else profiles.SYSTEM,'examples':[] if profile=='original' else profiles.EXAMPLES,'temperature':0,'seed':801,'cache_prompt':False,'repetitions':1})
 with (out/'server.log').open('w') as log:
  p=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
  try:
   d.PORT=19118
   for _ in range(120):
    try:
     if d.http('127.0.0.1','/health',timeout=1).get('status')=='ok':break
    except Exception:pass
    if p.poll() is not None:raise RuntimeError('Server exited')
    time.sleep(.5)
   d.save(out/'props.json',d.http('127.0.0.1','/props'))
   results=[]
   for case in cases:
    folder=out/case['scenario_id'];folder.mkdir()
    payload=d.study.query('',case,{'temperature':0,'seed':801,'max_tokens':128})
    if profile!='original':payload['messages']=profiles.messages(case)
    d.save(folder/'request.json',payload)
    start=time.monotonic();response=d.http('127.0.0.1','/v1/chat/completions',payload,180);elapsed=time.monotonic()-start
    d.save(folder/'response.json',response)
    content=response['choices'][0]['message']['content'];parsed=d.study.parse(content);final,permission,_=d.study.execute(case,parsed['action']);ev=d.study.evaluate(case,parsed['action'],final,permission,response['choices'][0]['finish_reason']=='stop',parsed['structured_valid'])
    r={'case':case['scenario_id'],'content':content,'elapsed_s':elapsed,'evaluation':ev,'usage':response.get('usage')};d.save(folder/'summary.json',r);results.append(r);print(profile,json.dumps(r,ensure_ascii=False),flush=True)
   d.save(out/'summary.json',{'profile':profile,'successes':sum(r['evaluation']['task_completed'] for r in results),'attempts':len(results),'results':results})
  finally:p.terminate();p.wait(timeout=20)
if __name__=='__main__':
 campaign('original')
 campaign('adjusted')
