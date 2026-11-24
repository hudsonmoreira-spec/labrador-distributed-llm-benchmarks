#!/usr/bin/env python3
import json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import run_prompt_diagnostic as d
import profiles
out=Path(__file__).resolve().parent/'generation_probe_v1';out.mkdir(exist_ok=False)
cases=json.loads((d.ROOT/'experiments/smarthome_agents/study_v1/development.json').read_text())
plan=[('plain_question',{'messages':[{'role':'user','content':'Qual é a capital do Brasil? Responda em uma frase.'}],'temperature':0,'seed':801,'max_tokens':64,'cache_prompt':False},None)]
for sid in ['dev2-02','dev2-06','dev2-05','dev2-08']:
 c=next(c for c in cases if c['scenario_id']==sid)
 p=d.study.query('',c,{'temperature':0,'seed':801,'max_tokens':128});p['messages']=profiles.messages(c);p.pop('response_format')
 plan.append((sid,p,c))
d.save(out/'plan_before_dispatch.json',{'at':d.now(),'purpose':'Probe unconstrained generation, not original evaluation','requests':[{ 'id':i,'payload':p} for i,p,c in plan]})
d.PORT=19119
for _ in range(60):
 try:
  if d.http('127.0.0.1','/health',timeout=1).get('status')=='ok':break
 except Exception:pass
 time.sleep(.5)
for i,p,c in plan:
 path=out/i;path.mkdir();d.save(path/'request.json',p)
 start=time.monotonic();r=d.http('127.0.0.1','/v1/chat/completions',p,120);elapsed=time.monotonic()-start;d.save(path/'response.json',r)
 content=r['choices'][0]['message']['content'];result={'id':i,'content':content,'elapsed_s':elapsed,'usage':r.get('usage')}
 if c:
  parsed=d.study.parse(content);final,permission,_=d.study.execute(c,parsed['action']);result['evaluation']=d.study.evaluate(c,parsed['action'],final,permission,r['choices'][0]['finish_reason']=='stop',parsed['structured_valid'])
 d.save(path/'summary.json',result);print(json.dumps(result,ensure_ascii=False),flush=True)
