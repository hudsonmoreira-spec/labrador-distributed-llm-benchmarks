#!/usr/bin/env python3
"""Choose a healthy prepared endpoint before dispatch; never replay inference."""
import argparse,concurrent.futures as cf,json,subprocess,urllib.request
from pathlib import Path
HERE=Path(__file__).resolve().parent
OPENER=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def get(host,port,path):
 with OPENER.open(f'http://{host}:{port}{path}',timeout=3) as f:return json.load(f)
def probe(board,pool,variant):
 r={'ip':board['ip'],'name':board['name'],'role':board['role'],'ready':False}
 try:
  assert get(board['ip'],pool['port'],'/health').get('status')=='ok'
  props=get(board['ip'],pool['port'],'/props')
  assert props['build_info']=='b9584-e25a32e98'
  assert props['default_generation_settings']['n_ctx']==512
  assert props['model_path'].endswith('/qwen'+variant+'.gguf'), 'Wrong model loaded'
  p=subprocess.run(['ssh','-F','/dev/null','-o','BatchMode=yes','-o','ConnectTimeout=3','-o','UserKnownHostsFile='+str(HERE.parent/'revision_20261123/inventory/known_hosts'),'caninos@'+board['ip'],'cat /sys/class/net/end0/address'],capture_output=True,text=True,timeout=6)
  assert p.returncode==0 and p.stdout.strip()==board['mac'], 'Identity mismatch/unreachable'
  r['ready']=True
 except Exception as e:r['error']=str(e) or type(e).__name__
 return r

def select(pool,variant='05',reserve_only=False):
 boards=[b for b in pool['boards'] if not reserve_only or b['role']=='reserve']
 with cf.ThreadPoolExecutor(7) as ex:checks=list(ex.map(lambda b:probe(b,pool,variant),boards))
 ready=[b for b in checks if b['ready']]
 return {'selected':ready[0] if ready else None,'checks':checks,'scope':'Endpoint selection before dispatch only; no request sent or silently replayed.'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--reserve-only',action='store_true');p.add_argument('--model',choices=['05','15'],default='05');a=p.parse_args()
 result=select(json.loads((HERE/'pool.json').read_text()),a.model,a.reserve_only)
 print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(0 if result['selected'] else 1)
