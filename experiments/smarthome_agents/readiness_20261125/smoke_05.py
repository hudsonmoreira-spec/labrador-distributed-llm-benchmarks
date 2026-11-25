import concurrent.futures as cf,subprocess,json,urllib.request
from pathlib import Path
out=Path('/home/hudymoreira/labrador-distributed-llm-benchmarks/experiments/smarthome_agents/readiness_20261125')
known=out.parent/'revision_20261123/inventory/known_hosts'
remote=r'''import hashlib,json,os,socket,subprocess,time,urllib.request,tempfile
from pathlib import Path
binary='/home/caninos/llama-offline/llama.cpp/build/bin/llama-server'
model='/home/caninos/smarthome_agents/study_v1/models/qwen2.5-0.5b-instruct-q5_k_m.gguf'
def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for chunk in iter(lambda:f.read(4*1024*1024),b''):h.update(chunk)
 return h.hexdigest()
r={'model_path':model,'model_sha256':sha(model),'runtime_sha256':sha(binary)}
assert r['model_sha256']=='041474553fcabfc2a2d67903f9d2c2e50bd92528e670da4f33b5d0ce6e59fd55'
assert r['runtime_sha256']=='a46782e75231c0a4a75a1e38afbbc5d7b72d92c8d834d6bb8b5020a0e1e79a87'
with socket.socket() as s:s.bind(('127.0.0.1',19120))
env=os.environ.copy();env['LD_LIBRARY_PATH']=str(Path(binary).parent)
log=tempfile.TemporaryFile()
p=subprocess.Popen([binary,'--model',model,'--host','127.0.0.1','--port','19120','--threads','4','--threads-batch','4','--ctx-size','512','--parallel','1','--n-predict','4','--device','none','--no-warmup'],env=env,stdout=log,stderr=log)
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
try:
 for _ in range(90):
  if p.poll() is not None:raise RuntimeError('Runtime exited '+str(p.returncode))
  try:
   with opener.open('http://127.0.0.1:19120/health',timeout=2) as f:health=json.load(f)
   if health.get('status')=='ok':break
  except Exception:pass
  time.sleep(1)
 else:raise RuntimeError('Loading timeout')
 payload={'messages':[{'role':'user','content':'Responda apenas OK.'}],'temperature':0,'max_tokens':1,'seed':801}
 req=urllib.request.Request('http://127.0.0.1:19120/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
 start=time.monotonic()
 with opener.open(req,timeout=60) as f:response=json.load(f)
 assert response.get('usage',{}).get('completion_tokens',0)>=1
 r.update(health=health,response=response,elapsed_s=time.monotonic()-start,ready=True)
finally:
 p.terminate()
 try:p.wait(timeout=10)
 except subprocess.TimeoutExpired:p.kill();p.wait()
 r['temporary_server_stopped']=p.poll() is not None
 log.seek(0);r['log_tail']=log.read().decode(errors='replace')[-1800:];log.close()
print(json.dumps(r))
'''
def verify(h):
 r={'ip':h}
 try:
  p=subprocess.run(['ssh','-F','/dev/null','-o','BatchMode=yes','-o','ConnectTimeout=5','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=2','-o','UserKnownHostsFile='+str(known),'caninos@'+h,'python3 -'],input=remote,capture_output=True,text=True,timeout=240)
  if p.returncode:raise RuntimeError(p.stderr[-1000:])
  r.update(json.loads(p.stdout))
 except Exception as e:r.update(ready=False,error=str(e))
 try:
  with urllib.request.urlopen('http://'+h+':8080/health',timeout=5) as f:r['existing_15_service']=json.load(f)
 except Exception as e:r['existing_15_service']={'error':str(e)}
 (out/(h+'-smoke.json')).write_text(json.dumps(r,indent=2))
 print(json.dumps({k:r.get(k) for k in ['ip','ready','elapsed_s','temporary_server_stopped','existing_15_service','error']}),flush=True)
 return r
with cf.ThreadPoolExecutor(3) as pool:r=list(pool.map(verify,['192.168.50.89','192.168.50.169','192.168.50.240']))
(out/'smoke-summary.json').write_text(json.dumps(r,indent=2))
