#!/usr/bin/env python3
import concurrent.futures as cf
import json
from pathlib import Path
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import run_prompt_diagnostic as d
import profiles
OUT=Path(__file__).resolve().parent/'sbc_adjusted_v1'
REMOTE='/home/caninos/smarthome_agents/model15_adjustment_20261123'
HOSTS=['192.168.50.89','192.168.50.169']
def test(item):
 h,case=item;folder=OUT/case['scenario_id'];folder.mkdir()
 payload=d.study.query('',case,{'temperature':0,'seed':801,'max_tokens':128});payload['messages']=profiles.messages(case)
 d.save(folder/'request.json',payload)
 try:
  cmd=f'mkdir -p {REMOTE}; env LD_LIBRARY_PATH={d.BIN} nohup {d.BIN}/llama-server --model {d.MODEL} --host 0.0.0.0 --port {d.PORT} --threads 4 --threads-batch 4 --ctx-size 1024 --parallel 1 --n-predict 128 --device none --no-warmup >{REMOTE}/server.log 2>&1 </dev/null & echo $! >{REMOTE}/server.pid'
  d.ssh(h,cmd)
  for _ in range(60):
   try:
    if d.http(h,'/health',timeout=2).get('status')=='ok':break
   except Exception:pass
   time.sleep(1)
  d.save(folder/'props.json',d.http(h,'/props'))
  start=time.monotonic();response=d.http(h,'/v1/chat/completions',payload,360);elapsed=time.monotonic()-start
  d.save(folder/'response.json',response)
  content=response['choices'][0]['message']['content'];parsed=d.study.parse(content);final,permission,_=d.study.execute(case,parsed['action']);ev=d.study.evaluate(case,parsed['action'],final,permission,response['choices'][0]['finish_reason']=='stop',parsed['structured_valid'])
  r={'host':h,'case':case['scenario_id'],'content':content,'elapsed_s':elapsed,'evaluation':ev,'usage':response.get('usage')};d.save(folder/'summary.json',r);print(json.dumps(r,ensure_ascii=False),flush=True)
 except Exception as e:d.save(folder/'error.json',{'host':h,'error':repr(e)});print(h,repr(e),flush=True)
 finally:
  try:
   stop=f'p=$(cat {REMOTE}/server.pid); if test -r /proc/$p/cmdline && tr "\\0" " " </proc/$p/cmdline | grep -q -- "--port {d.PORT}"; then kill "$p"; fi; cat {REMOTE}/server.log'
   (folder/'server.log').write_text(d.ssh(h,stop,timeout=20))
  except Exception as e:(folder/'cleanup-error.txt').write_text(repr(e))
if __name__=='__main__':
 d.PORT=19117;OUT.mkdir(exist_ok=False)
 cases=json.loads((d.ROOT/'experiments/smarthome_agents/study_v1/development.json').read_text())
 cases=[next(c for c in cases if c['scenario_id']==sid) for sid in ['dev2-02','dev2-06']]
 d.save(OUT/'plan_before_dispatch.json',{'at':d.now(),'purpose':'Exploratory tuning; not original scientific evaluation','hosts':HOSTS,'cases':cases,'system':profiles.SYSTEM,'examples':profiles.EXAMPLES,'context':1024,'runtime':'b9584-e25a32e98','model_sha256':'b46661073c18e5b56a41fa320975f866a00def1ff08feef4718e013258896f8c','changes':['Portuguese instructions','three demonstrations','omit light states in language interpretation; executor still uses full state','context1024'],'seed':801,'temperature':0,'max_tokens':128})
 with cf.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(test,zip(HOSTS,cases)))
