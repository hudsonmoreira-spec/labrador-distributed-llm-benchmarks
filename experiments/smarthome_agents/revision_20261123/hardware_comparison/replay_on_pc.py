#!/usr/bin/env python3
"""Replay exact recorded SBC requests on x86; preserve all original records."""
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import run_prompt_diagnostic as d
HERE=Path(__file__).resolve().parent
OUT=HERE/'pc_exact_replay_v1'
RUNTIME=Path('/home/hudymoreira/.cache/labrador-revision-20261123/llama-b9584-x86/build/bin/llama-server')
MODEL=d.ROOT/'models/qwen2.5-1.5b-instruct-q5_k_m/qwen2.5-1.5b-instruct-q5_k_m.gguf'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 OUT.mkdir(exist_ok=False)
 previous=json.loads((d.HERE/'diagnostic_summary.json').read_text())
 sbcs=[r for r in previous['attempts'] if r['variant']=='original_en']
 assert len(sbcs)==8
 cases={c['scenario_id']:c for c in json.loads((d.ROOT/'experiments/smarthome_agents/study_v1/development.json').read_text())}
 command=[str(RUNTIME),'--model',str(MODEL),'--host','127.0.0.1','--port','19118','--threads','4','--threads-batch','4','--ctx-size','512','--parallel','1','--n-predict','128','--device','none','--metrics','--no-warmup']
 model_sha=sha(MODEL);assert model_sha=='b46661073c18e5b56a41fa320975f866a00def1ff08feef4718e013258896f8c'
 plan={'started_at':d.now(),'purpose':'Hardware/runtime comparison, original model/prompt only, no hybrid or post-processing repair','command':command,'model_sha256':model_sha,'runtime_commit':'e25a32e98c15a1118a976685af0f4d2c1f380079','runtime_sha256_x86':sha(RUNTIME),'cpu':json.loads(subprocess.check_output(['lscpu','-J'],text=True)),'seed':801,'temperature':0,'repetitions':1,'cases':[{'scenario_id':r['scenario_id'],'sbc_host':r['host'],'sbc_record':r['record_path'],'request_sha256':sha((d.HERE/r['record_path']).parent/'request.json'),'sbc_summary_sha256':sha(d.HERE/r['record_path'])} for r in sbcs],'limits':['eight reused development cases, not reserved data','SBC baseline recorded earlier across five recovered hosts; lab8 missing cases moved as recorded','architecture/compiler/backend differ; comparison does not certify physical hardware health','HTTP timings include Ethernet on SBC and loopback on PC','not a pure CPU microbenchmark; other desktop services not stopped']}
 d.save(OUT/'plan_before_dispatch.json',plan)
 (OUT/'runtime-version.txt').write_text(subprocess.check_output([str(RUNTIME),'--version'],stderr=subprocess.STDOUT,text=True))
 (OUT/'memory-before.txt').write_text(Path('/proc/meminfo').read_text())
 with (OUT/'server.log').open('w') as log:
  proc=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
  try:
   d.PORT=19118
   for _ in range(120):
    try:
     if d.http('127.0.0.1','/health',timeout=1).get('status')=='ok':break
    except Exception:pass
    if proc.poll() is not None:raise RuntimeError('Comparison server exited')
    time.sleep(.5)
   props=d.http('127.0.0.1','/props');assert props['build_info']=='b9584-e25a32e98';assert props['default_generation_settings']['n_ctx']==512;d.save(OUT/'props.json',props)
   rows=[]
   for old in sbcs:
    case=cases[old['scenario_id']];src=(d.HERE/old['record_path']).parent/'request.json'
    p=OUT/case['scenario_id'];p.mkdir();(p/'request.json').write_bytes(src.read_bytes());payload=json.loads(src.read_text())
    assert sha(p/'request.json')==sha(src)
    assert payload['messages']==d.study.messages(case) and payload['max_tokens']==128 and payload['seed']==801 and payload['temperature']==0
    (p/'load-before.txt').write_text(Path('/proc/loadavg').read_text())
    start=time.monotonic();raw=d.http('127.0.0.1','/v1/chat/completions',payload,180);elapsed=time.monotonic()-start;d.save(p/'response.json',raw)
    content=raw['choices'][0]['message']['content'];completed=raw['choices'][0]['finish_reason']=='stop';parsed=d.study.parse(content);final,permission,_=d.study.execute(case,parsed['action']);ev=d.study.evaluate(case,parsed['action'],final,permission,completed,parsed['structured_valid'])
    row={'scenario_id':case['scenario_id'],'command':case['resident_request'],'sbc_host':old['host'],'sbc_response':old['model_content'],'pc_response':content,'identical_text':old['model_content']==content,'identical_json':json.loads(old['model_content'])==json.loads(content),'sbc_success':old['evaluation']['task_completed'],'pc_success':ev['task_completed'],'sbc_s':old['elapsed_s'],'pc_s':elapsed,'request_sha256':sha(src),'pc_completed':completed,'pc_valid':parsed['structured_valid'],'pc_evaluation':ev,'usage':raw.get('usage')}
    d.save(p/'comparison.json',row);rows.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
   summary={'completed_at':d.now(),'cases':len(rows),'identical_json':sum(r['identical_json'] for r in rows),'identical_text':sum(r['identical_text'] for r in rows),'sbc_successes':sum(r['sbc_success'] for r in rows),'pc_successes':sum(r['pc_success'] for r in rows),'sbc_median_s':statistics.median(r['sbc_s'] for r in rows),'pc_median_s':statistics.median(r['pc_s'] for r in rows),'rows':rows,'scope':plan['limits']};d.save(OUT/'summary.json',summary)
   print('SUMMARY',json.dumps({k:v for k,v in summary.items() if k not in ['rows','scope']}),flush=True)
  finally:
   proc.terminate();proc.wait(timeout=20)
if __name__=='__main__':main()
