#!/usr/bin/env python3
"""Local human-review console. Original study artifacts are read-only."""
import concurrent.futures
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import threading
import time
from urllib.request import Request, build_opener, ProxyHandler
from uuid import uuid4, UUID
from datetime import datetime, timezone

HERE=Path(__file__).resolve().parent
REV=HERE.parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'experiments/smarthome_agents/scripts'))
import study_v1 as study
sys.path.insert(0,str(REV/'model15_adjustment'))
import hybrid_v2 as hybrid
DATA=HERE/'records'
DATA.mkdir(exist_ok=True)
LEDGER=ROOT/'experiments/smarthome_agents/runs/20261006-study-v1-quality/manual_reviews.json'
BIN='/home/caninos/llama-offline/llama.cpp/build/bin'
REMOTE='/home/caninos/smarthome_agents/review_console_20261123'
PORT=19116
HOSTS=[h.strip() for h in os.environ.get('SMARTHOME_CONSOLE_HOSTS','192.168.50.85,192.168.50.200').split(',') if h.strip()]
MODELS={
 '05':{'label':'Qwen 0,5B · modelo dos quatro casos','path':os.environ.get('SMARTHOME_CONSOLE_MODEL_05','/home/caninos/smarthome_agents/revision_20261123_backup/models/qwen2.5-0.5b-instruct-q5_k_m.gguf'),'sha':'041474553fcabfc2a2d67903f9d2c2e50bd92528e670da4f33b5d0ce6e59fd55'},
 '15':{'label':'Qwen 1,5B · original na Labrador','path':'/home/caninos/llama-offline/models/qwen2.5-1.5b-instruct-q5_k_m.gguf','sha':'b46661073c18e5b56a41fa320975f866a00def1ff08feef4718e013258896f8c'}}
MODELS['15_hybrid']={'label':'Qwen 1,5B + regras · notebook','local':True}
MODELS['15_pc_original']={'label':'Qwen 1,5B original · notebook','local':True}
OPENER=build_opener(ProxyHandler({}))
JOBS={};LOCK=threading.Lock();REVIEW_LOCK=threading.Lock();POOL=concurrent.futures.ThreadPoolExecutor(max_workers=1)
READY={}
def now():return datetime.now(timezone.utc).isoformat()
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ssh(h,c,timeout=30):
 p=subprocess.run(['ssh','-F','/dev/null','-o','BatchMode=yes','-o','ConnectTimeout=5','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=2','-o','UserKnownHostsFile='+str(REV/'inventory/known_hosts'),'caninos@'+h,c],capture_output=True,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError('A placa não respondeu ao acesso de preparação: '+p.stderr.strip())
 return p.stdout

def http(h,path,payload=None,timeout=5):
 target='127.0.0.1' if h=='pc_original' else h
 port=19118 if h=='pc_original' else 19119 if h=='127.0.0.1' else PORT
 req=Request(f'http://{target}:{port}'+path,data=None if payload is None else json.dumps(payload,ensure_ascii=False).encode(),headers={'Content-Type':'application/json'})
 with OPENER.open(req,timeout=timeout) as r:return json.load(r)

def originals():
 out=[]
 for i,entry in enumerate(json.loads(LEDGER.read_text())):
  p=ROOT/entry['attempt'];s=json.loads(p.read_text());q=json.loads((p.parent/'request.json').read_text())
  user=q['messages'][-1]['content'];command,state=user.rsplit('\n',1)
  out.append({'id':str(i),'command':command,'initial':json.loads(state),'response':s['model_content'],'question':entry['question'],'host':s['host'],'elapsed_s':s['elapsed_s'],'source':entry['attempt'],'source_sha256':sha(p),'request_sha256':sha(p.parent/'request.json'),'ledger_sha256':sha(LEDGER)})
 return out

def reviews():
 return [json.loads(p.read_text()) for p in sorted((DATA/'reviews').glob('*.json'))] if (DATA/'reviews').exists() else []

def prepare(h,model,job):
 if model in ['15_hybrid','15_pc_original']:
  job['message']='Verificando o modelo no notebook…'
  props=http(h,'/props')
  if model=='15_pc_original':
   assert props['build_info']=='b9584-e25a32e98' and props['default_generation_settings']['n_ctx']==512
  if http(h,'/health').get('status')!='ok':raise RuntimeError('O modelo local ainda não está pronto.')
  save(DATA/job['id']/'runtime-local.json',props)
  return
 if READY.get(h)==model:
  try:
   if http(h,'/health').get('status')=='ok':return
  except Exception:pass
 job['message']='Preparando a placa e carregando o modelo…'
 m=MODELS[model]
 # Operate only on the console's own process; preserve ports 8080 and 19115.
 command=f'''mkdir -p {REMOTE}
if test -f {REMOTE}/server.pid; then
 p=$(cat {REMOTE}/server.pid)
 if test -r /proc/$p/cmdline && tr '\\0' ' ' </proc/$p/cmdline | grep -q -- '--port {PORT}'; then kill "$p"; sleep 1; fi
fi
sha256sum {shlex.quote(m['path'])}
'''
 if m['sha'] not in ssh(h,command,timeout=180):raise RuntimeError('O arquivo do modelo não passou na conferência de integridade.')
 cmd=[BIN+'/llama-server','--model',m['path'],'--host','0.0.0.0','--port',str(PORT),'--threads','4','--threads-batch','4','--ctx-size','512','--parallel','1','--n-predict','128','--device','none','--metrics','--no-warmup']
 startup=f"env LD_LIBRARY_PATH={BIN} nohup {' '.join(shlex.quote(x) for x in cmd)} >{REMOTE}/server.log 2>&1 </dev/null & echo $! >{REMOTE}/server.pid"
 ssh(h,startup)
 for _ in range(60):
  try:
   if http(h,'/health',timeout=2).get('status')=='ok':break
  except Exception:pass
  time.sleep(1)
 else:raise RuntimeError('O modelo não ficou pronto na placa.')
 props=http(h,'/props');assert props['build_info']=='b9584-e25a32e98';assert props['default_generation_settings']['n_ctx']==512
 save(DATA/job['id']/('runtime-'+h+'.json'),props)
 READY[h]=model

def describe(a):
 if not a:return 'A resposta não pôde ser interpretada como uma ação válida.'
 if a['action']=='ask_clarification':return a.get('question','')
 if a['action']=='no_action':return 'A IA decidiu não agir. Motivo informado: '+a.get('reason','')
 return ' '.join(('Acender' if s['value']=='on' else 'Apagar')+' a luz '+('da sala.' if s['room']=='sala' else 'do quarto.' if s['room']=='quarto' else 'do cômodo '+str(s['room'])+'.') for s in study.light_steps(a))

def run(job,body):
 folder=DATA/job['id'];folder.mkdir()
 case={'resident_request':body['command'],'initial_state':{'rooms':{r:{'light':body[r]} for r in ['sala','quarto']},'known_location':body['location']},'permissions':{'set_light':{'rooms':['sala','quarto'],'values':['on','off']}}}
 payload=study.query('',case,{'temperature':0,'seed':801,'max_tokens':128})
 if body['model']=='15_hybrid':payload={'type':'hybrid_controller_input','command':body['command'],'known_location':body['location'],'profile':'hybrid_intent_v2','profile_sha256':sha(Path(hybrid.__file__))}
 save(folder/'request.json',payload);save(folder/'input.json',body)
 errors=[]
 hosts=['pc_original'] if body['model']=='15_pc_original' else ['127.0.0.1'] if body['model']=='15_hybrid' else HOSTS
 try:
  for h in hosts:
   try:prepare(h,body['model'],job)
   except Exception as e:
    errors.append({'host':h,'phase':'preparation','error':str(e)});continue
   job['message']='O controlador está interpretando e validando seu comando…' if body['model']=='15_hybrid' else 'A IA está interpretando o comando. Isso pode levar de 30 segundos a alguns minutos.';job['host']=h
   # Once dispatched, do not retry an ambiguous timeout: retain its failure and let the user choose a new test.
   start=time.monotonic();origin='model_action';model_content=[]
   if body['model']=='15_hybrid':
    calls=[]
    def call(intent_payload):
     n=len(calls);save(folder/f'intent-request-{n}.json',intent_payload)
     raw=http(h,'/v1/chat/completions',intent_payload,120);calls.append(raw);save(folder/f'intent-response-{n}.json',raw);return raw
    action,traces,origin=hybrid.interpret(case,call,study.pilot.normalize_text)
    response={'type':'hybrid_controller_output','action':action,'intent_responses':traces,'origin':origin}
    content=json.dumps(action,ensure_ascii=False);completed=True
    model_content=[t['choices'][0]['message']['content'] for t in traces]
   else:
    response=http(h,'/v1/chat/completions',payload,240)
    content=response.get('choices',[{}])[0].get('message',{}).get('content','')
    completed=response.get('choices',[{}])[0].get('finish_reason')=='stop'
   elapsed=time.monotonic()-start
   save(folder/'response.json',response)
   parsed=study.parse(content) if completed else {'structured_valid':False,'action':None}
   final,permission,decisions=study.execute(case,parsed['action'])
   result={'id':job['id'],'type':'new_interactive_test','created_at':now(),'command':body['command'],'model':body['model'],'host':h,'elapsed_s':elapsed,'initial':case['initial_state'],'final':final,'response':content,'answer':describe(parsed['action']),'valid':parsed['structured_valid'],'completed':completed,'action':parsed['action'],'permission':permission,'preparation_errors':errors,'configuration':'hybrid_intent_v2' if body['model']=='15_hybrid' else 'original_pc_v1' if body['model']=='15_pc_original' else 'original_action_v1','machine':'Notebook local (x86-64)' if h in ['127.0.0.1','pc_original'] else 'Labrador '+h,'origin':origin,'raw_model_content':model_content,'request_sha256':sha(folder/'request.json'),'response_sha256':sha(folder/'response.json')}
   save(folder/'result.json',result);job.update(status='done',result=result);return
  raise RuntimeError('Nenhuma reserva ficou disponível para iniciar o teste.')
 except Exception as e:
  err={'id':job['id'],'created_at':now(),'error':str(e),'preparation_errors':errors,'message':'Falha de comunicação ou de execução. Isso não é um julgamento sobre a resposta da IA.'}
  save(folder/'error.json',err);job.update(status='error',error=err['message']+' '+str(e))

def record_review(body):
 kind=body.get('kind');identity=body.get('id');decision=body.get('decision');name=body.get('reviewer','').strip();reason=body.get('reason','').strip()
 if kind not in ['original','interactive'] or decision not in ['pass','fail','uncertain'] or not name or len(name)>180 or len(reason)>2000:raise ValueError('Preencha seu nome e escolha uma avaliação válida.')
 if decision=='fail' and not reason:raise ValueError('Escreva brevemente o que faltou na resposta.')
 if kind=='original':
  source=next((x for x in originals() if x['id']==identity),None)
  criterion='A resposta solicita explicitamente o cômodo ausente?'
 else:
  p=DATA/str(identity)/'result.json'
  if str(UUID(str(identity)))!=str(identity) or not p.exists():raise ValueError('Teste não encontrado.')
  source={'id':identity,'source_sha256':sha(p),'result':json.loads(p.read_text())};criterion='A resposta atende ao comando e preserva o que não foi solicitado?'
 if source is None:raise ValueError('Registro não encontrado.')
 entry={'record_id':str(uuid4()),'recorded_at':now(),'kind':kind,'id':identity,'decision':decision,'reviewer':name,'rationale':reason,'criterion':criterion,'human_validation_pending':decision=='uncertain','source':source,'review_method':'Explicit form submission by the local user; name self-declared'}
 with REVIEW_LOCK:
  (DATA/'reviews').mkdir(exist_ok=True);save(DATA/'reviews'/(entry['recorded_at'].replace(':','-')+'-'+entry['record_id']+'.json'),entry)
 return entry

class Handler(BaseHTTPRequestHandler):
 def respond(self,obj,status=200):
  data=json.dumps(obj,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data)
 def do_GET(self):
  if self.path=='/api/bootstrap':return self.respond({'originals':originals(),'reviews':reviews(),'models':{k:m['label'] for k,m in MODELS.items()}})
  if self.path.startswith('/api/job/'):
   identity=self.path.rsplit('/',1)[-1];job=JOBS.get(identity)
   if job is None:
    try:
     if str(UUID(identity))==identity:
      p=DATA/identity/'result.json'
      if p.exists():job={'id':identity,'status':'done','result':json.loads(p.read_text())}
    except ValueError:pass
   return self.respond(job if job else {'error':'Teste não encontrado'},200 if job else 404)
  if self.path=='/api/export':return self.respond({'exported_at':now(),'reviews':reviews()})
  if self.path not in ['/','/index.html']:return self.respond({'error':'Não encontrado'},404)
  data=(HERE/'static/index.html').read_bytes();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
 def do_POST(self):
  if self.headers.get('Host') not in ['127.0.0.1:8092','localhost:8092'] or self.headers.get('Origin') not in [None,'http://127.0.0.1:8092','http://localhost:8092']:return self.respond({'error':'Origem não permitida'},403)
  try:
   n=int(self.headers.get('Content-Length',0))
   if n<1 or n>16000:raise ValueError('Requisição inválida')
   body=json.loads(self.rfile.read(n))
   if self.path=='/api/review':return self.respond(record_review(body))
   if self.path!='/api/run':return self.respond({'error':'Não encontrado'},404)
   if not isinstance(body.get('command'),str) or not 1<=len(body['command'].strip())<=300 or body.get('model') not in MODELS or any(body.get(r) not in ['on','off'] for r in ['sala','quarto']) or body.get('location') not in [None,'sala','quarto']:raise ValueError('Confira o comando e o estado das luzes.')
   body['command']=body['command'].strip()
   with LOCK:
    if any(j['status']=='running' for j in JOBS.values()):return self.respond({'error':'Há um teste em andamento. Aguarde a resposta.'},409)
    job={'id':str(uuid4()),'status':'running','message':'Iniciando o teste…'};JOBS[job['id']]=job;POOL.submit(run,job,body)
   return self.respond(job,202)
  except (ValueError,TypeError,json.JSONDecodeError) as e:return self.respond({'error':str(e)},400)
  except Exception:return self.respond({'error':'Não foi possível salvar. O registro original foi preservado.'},500)
 def log_message(self,fmt,*args):print(fmt%args,flush=True)

if __name__=='__main__':
 print('Interface local: http://127.0.0.1:8092',flush=True)
 ThreadingHTTPServer(('127.0.0.1',8092),Handler).serve_forever()
