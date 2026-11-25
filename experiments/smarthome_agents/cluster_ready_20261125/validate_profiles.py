#!/usr/bin/env python3
"""Actual generation for each profile, then restore the boot-default 0.5B."""
import concurrent.futures as cf,json,time,urllib.request,subprocess
from pathlib import Path
import provision
HERE=Path(__file__).resolve().parent
OPENER=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def http(h,path,payload=None,timeout=5):
 req=urllib.request.Request(f'http://{h}:19115'+path,data=None if payload is None else json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
 with OPENER.open(req,timeout=timeout) as f:return json.load(f)
def wait(h,v):
 last=None
 for _ in range(180):
  try:
   if http(h,'/health').get('status')=='ok':
    p=http(h,'/props')
    if p['model_path'].endswith('/qwen'+v+'.gguf'):
     assert p['build_info']=='b9584-e25a32e98'
     assert p['default_generation_settings']['n_ctx']==512
     assert p['total_slots']==1
     return p
  except Exception as e:last=str(e)
  time.sleep(1)
 raise RuntimeError('Profile '+v+' did not become ready: '+str(last))
def validate(b):
 h=b['ip'];r={'ip':h,'name':b['name'],'role':b['role'],'profiles':{},'ready':False}
 try:
  for v in ['05','15']:
   provision.ssh(h,'sudo -n systemctl start smarthome-benchmark-'+v+'.service',timeout=45)
   props=wait(h,v)
   payload={'messages':[{'role':'user','content':'Oi'}],'max_tokens':1,'temperature':0,'seed':801,'cache_prompt':False}
   start=time.monotonic();response=http(h,'/v1/chat/completions',payload,90)
   assert response.get('usage',{}).get('completion_tokens',0)>=1
   r['profiles'][v]={'props':props,'request':payload,'response':response,'elapsed_s':time.monotonic()-start}
   print(json.dumps({'ip':h,'profile':v,'generation':'pass'}),flush=True)
  r['ready']=True
 except Exception as e:r['error']=str(e)
 finally:
  try:
   provision.ssh(h,'sudo -n systemctl start smarthome-benchmark-05.service',timeout=45)
   r['final_props']=wait(h,'05')
   r['services']=provision.ssh(h,'systemctl is-enabled smarthome-benchmark-05.service; systemctl is-active smarthome-benchmark-05.service; systemctl is-enabled smarthome-benchmark-15.service; systemctl is-active smarthome-benchmark-15.service; free -m; df -Pk /home/caninos; cat /proc/loadavg',timeout=30)
   r['restored_05']=True
  except Exception as e:r['restored_05']=False;r['restore_error']=str(e)
  (HERE/'validation').mkdir(exist_ok=True);(HERE/'validation'/(h+'.json')).write_text(json.dumps(r,indent=2))
 return r
if __name__=='__main__':
 pool=json.loads((HERE/'pool.json').read_text())
 with cf.ThreadPoolExecutor(7) as ex:results=list(ex.map(validate,pool['boards']))
 (HERE/'validation.json').write_text(json.dumps(results,indent=2))
 assert all(r['ready'] and r['restored_05'] for r in results)
 pool['status']='7 boards verified: both model profiles generated tokens; 0.5B boot default ready'
 (HERE/'pool.json').write_text(json.dumps(pool,indent=2))
 print('All seven boards passed both model profiles; restored 0.5B.',flush=True)
