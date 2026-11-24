#!/usr/bin/env python3
import json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import run_prompt_diagnostic as d
import hybrid_v2 as hybrid
HERE=Path(__file__).resolve().parent;OUT=HERE/'hybrid_v2_validation';OUT.mkdir(exist_ok=False);d.PORT=19119
base={'rooms':{'sala':{'light':'off'},'quarto':{'light':'on'}},'known_location':None}
plan=[('off_paraphrase','Deixe apagada a luz do quarto.',None,{'action':'set_light','room':'quarto','value':'off'}),('explicit_over_location','Ilumine o quarto.','sala',{'action':'set_light','room':'quarto','value':'on'}),('missing_room','Acenda a luz.',None,{'action':'ask_clarification','missing_field':'room','question':'Em qual cômodo: sala ou quarto?'}),('unsupported','Ligue o ar-condicionado da sala.',None,{'action':'no_action','reason':'Este modo controla somente iluminação da sala e do quarto.'})]
d.save(OUT/'plan_before_dispatch.json',{'at':d.now(),'purpose':'Developer smoke validation of changed hybrid controller, not reserved evaluation','cases':[{'id':i,'text':t,'location':l,'expected_action':a} for i,t,l,a in plan],'profile_sha256':__import__('hashlib').sha256(Path(hybrid.__file__).read_bytes()).hexdigest()})
for i,text,location,expected in plan:
 c={'resident_request':text,'initial_state':json.loads(json.dumps(base))};c['initial_state']['known_location']=location
 p=OUT/i;p.mkdir();calls=[]
 def call(body):
  n=len(calls);d.save(p/f'request-{n}.json',body);r=d.http('127.0.0.1','/v1/chat/completions',body,120);calls.append(r);d.save(p/f'response-{n}.json',r);return r
 start=time.monotonic();action,traces,origin=hybrid.interpret(c,call,d.study.pilot.normalize_text)
 r={'id':i,'action':action,'expected':expected,'passed':action==expected,'elapsed_s':time.monotonic()-start,'origin':origin,'inference_calls':len(calls)};d.save(p/'summary.json',r);print(json.dumps(r,ensure_ascii=False),flush=True)
