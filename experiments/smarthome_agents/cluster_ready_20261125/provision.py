#!/usr/bin/env python3
"""Install isolated, persistent model profiles on identified study boards."""
import concurrent.futures as cf
import json, shlex, subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
KNOWN=HERE.parent/'revision_20261123/inventory/known_hosts'
REMOTE='/home/caninos/smarthome_agents/cluster_ready_20261125'
HASH05='041474553fcabfc2a2d67903f9d2c2e50bd92528e670da4f33b5d0ce6e59fd55'
HASH15='b46661073c18e5b56a41fa320975f866a00def1ff08feef4718e013258896f8c'
RUNTIME_HASH='a46782e75231c0a4a75a1e38afbbc5d7b72d92c8d834d6bb8b5020a0e1e79a87'
LAUNCHER=r'''#!/usr/bin/env python3
import hashlib,json,os,sys
from pathlib import Path
base=Path(__file__).resolve().parent
cfg=json.loads((base/'profile.json').read_text())
variant=sys.argv[1]
assert variant in ['05','15']
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 return h.hexdigest()
assert Path('/sys/class/net/end0/address').read_text().strip()==cfg['mac'], 'Unexpected board identity'
model=base/'models'/('qwen'+variant+'.gguf')
assert sha(model)==cfg['model_hashes'][variant], 'Model integrity failure'
assert sha(cfg['binary'])==cfg['runtime_sha256'], 'Runtime integrity failure'
for name,digest in cfg['library_hashes'].items():
 assert sha(Path(cfg['binary']).parent/name)==digest, 'Library integrity failure: '+name
args=[cfg['binary'],'--model',str(model),'--host','0.0.0.0','--port',str(cfg['port']),'--threads','4','--threads-batch','4','--ctx-size','512','--parallel','1','--n-predict','128','--device','none','--metrics','--no-warmup']
env=os.environ.copy();env['LD_LIBRARY_PATH']=str(Path(cfg['binary']).parent)
os.execve(args[0],args,env)
'''
REMOTE_SCRIPT=r"""import hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
cfg=json.load(sys.stdin);base=Path(cfg['remote'])
assert Path('/sys/class/net/end0/address').read_text().strip()==cfg['mac']
subprocess.run(['sudo','-n','true'],check=True)
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 return h.hexdigest()
binary=Path(cfg['binary']);assert sha(binary)==cfg['runtime_sha256']
models={
 '05':next(p for p in [Path('/home/caninos/smarthome_agents/study_v1/models/qwen2.5-0.5b-instruct-q5_k_m.gguf'),Path('/home/caninos/smarthome_agents/revision_20261123_backup/models/qwen2.5-0.5b-instruct-q5_k_m.gguf')] if p.is_file()),
 '15':Path('/home/caninos/llama-offline/models/qwen2.5-1.5b-instruct-q5_k_m.gguf')}
for variant,path in models.items():assert sha(path)==cfg['model_hashes'][variant], 'Model hash mismatch: '+variant
libs={p.name:sha(p) for p in sorted(binary.parent.glob('*.so*')) if p.is_file()}
assert libs
cfg['library_hashes']=libs
cfg['resolved_models']={k:str(v) for k,v in models.items()}
launcher=cfg.pop('launcher');base.mkdir(parents=True,exist_ok=True);(base/'models').mkdir(exist_ok=True)
for variant,path in models.items():
 link=base/'models'/('qwen'+variant+'.gguf')
 if link.is_symlink():link.unlink()
 elif link.exists():raise RuntimeError('Refusing to replace non-symlink '+str(link))
 link.symlink_to(path)
(base/'profile.json').write_text(json.dumps(cfg,indent=2)+'\n')
(base/'launch.py').write_text(launcher);(base/'launch.py').chmod(0o755)
for variant,other in [('05','15'),('15','05')]:
 unit=f'''[Unit]
Description=SmartHome isolated benchmark Qwen {variant}
Wants=network-online.target
After=network-online.target
Conflicts=smarthome-benchmark-{other}.service
StartLimitIntervalSec=300
StartLimitBurst=5
[Service]
Type=simple
User=caninos
WorkingDirectory={base}
ExecStart=/usr/bin/python3 {base}/launch.py {variant}
Restart=always
RestartSec=5
TimeoutStopSec=30
KillSignal=SIGTERM
[Install]
WantedBy=multi-user.target
'''
 (base/f'smarthome-benchmark-{variant}.service').write_text(unit)
 subprocess.run(['sudo','-n','install','-m','644',str(base/f'smarthome-benchmark-{variant}.service'),f'/etc/systemd/system/smarthome-benchmark-{variant}.service'],check=True)
subprocess.run(['sudo','-n','systemctl','daemon-reload'],check=True)
subprocess.run(['sudo','-n','systemctl','disable','smarthome-benchmark-15.service'],check=True,capture_output=True)
subprocess.run(['sudo','-n','systemctl','enable','--now','smarthome-benchmark-05.service'],check=True,capture_output=True)
print(json.dumps({'profile':cfg,'enabled_05':subprocess.check_output(['systemctl','is-enabled','smarthome-benchmark-05.service'],text=True).strip(),'disk':subprocess.check_output(['df','-Pk',str(base)],text=True),'memory':Path('/proc/meminfo').read_text().splitlines()[:3]}))
"""
def ssh(host,command,stdin=None,timeout=240):
 p=subprocess.run(['ssh','-F','/dev/null','-o','BatchMode=yes','-o','ConnectTimeout=5','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=2','-o','UserKnownHostsFile='+str(KNOWN),'caninos@'+host,command],input=stdin,text=True,capture_output=True,timeout=timeout)
 if p.returncode:raise RuntimeError(p.stderr[-1500:])
 return p.stdout

def provision(r):
 host=r['ip'];cfg={'remote':REMOTE,'binary':'/home/caninos/llama-offline/llama.cpp/build/bin/llama-server','mac':r['mac'],'hostname':r['hostname'],'ip_at_setup':host,'role':'reserve' if host in ['192.168.50.85','192.168.50.200'] else 'primary','port':19115,'runtime_sha256':RUNTIME_HASH,'model_hashes':{'05':HASH05,'15':HASH15},'server_settings':{'threads':4,'threads_batch':4,'context':512,'parallel':1,'cpu_only':True},'request_defaults':{'temperature':0,'seed':801,'max_tokens':128,'cache_prompt':False},'second_repetition_seed':802,'launcher':LAUNCHER}
 try:
  result=json.loads(ssh(host,'python3 -c '+shlex.quote(REMOTE_SCRIPT),json.dumps(cfg),300));result['installed']=True
 except Exception as e:result={'installed':False,'error':str(e)}
 result['ip']=host;(HERE/'provisioning').mkdir(exist_ok=True);(HERE/'provisioning'/(host+'.json')).write_text(json.dumps(result,indent=2))
 print(json.dumps({'ip':host,'installed':result['installed'],'role':cfg['role'],'error':result.get('error')}),flush=True)
 return result
if __name__=='__main__':
 inventory=json.loads((HERE/'inventory.json').read_text())
 hosts=[r for r in inventory if r.get('runtime_exit')==0 and r['ip']!='192.168.50.141']
 assert len(hosts)==7
 with cf.ThreadPoolExecutor(4) as pool:results=list(pool.map(provision,hosts))
 (HERE/'provisioning.json').write_text(json.dumps(results,indent=2))
 assert all(r['installed'] for r in results)
 # Libraries must match between every prepared SBC, not just match locally.
 assert len({json.dumps(r['profile']['library_hashes'],sort_keys=True) for r in results})==1
 print('Seven profiles installed; model/runtime/library hashes match across boards.',flush=True)
