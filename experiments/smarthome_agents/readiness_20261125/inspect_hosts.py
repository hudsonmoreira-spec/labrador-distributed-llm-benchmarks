import concurrent.futures as cf,json,subprocess
from pathlib import Path
out=Path('/home/hudymoreira/labrador-distributed-llm-benchmarks/experiments/smarthome_agents/readiness_20261125')
known=out.parent/'revision_20261123/inventory/known_hosts'
script=r'''import json,socket,os,subprocess
from pathlib import Path
def read(p):
 try:return Path(p).read_text().strip()
 except OSError:return None
bin='/home/caninos/llama-offline/llama.cpp/build/bin'
paths=[bin+'/llama-server','/home/caninos/llama-offline/models/qwen2.5-1.5b-instruct-q5_k_m.gguf','/home/caninos/smarthome_agents/revision_20261123_backup/models/qwen2.5-0.5b-instruct-q5_k_m.gguf','/home/caninos/smarthome_agents/study_v1/models/qwen2.5-0.5b-instruct-q5_k_m.gguf']
r={'hostname':socket.gethostname(),'mac':read('/sys/class/net/end0/address'),'arch':os.uname().machine,'ethernet_carrier':read('/sys/class/net/end0/carrier'),'ethernet_speed':read('/sys/class/net/end0/speed'),'files':{p:Path(p).stat().st_size if Path(p).is_file() else None for p in paths},'uptime':read('/proc/uptime'),'memory':read('/proc/meminfo').splitlines()[:3],'load':read('/proc/loadavg'),'processes':subprocess.run(['pgrep','-af','llama-server'],capture_output=True,text=True).stdout}
if Path(paths[0]).is_file():
 env=os.environ.copy();env['LD_LIBRARY_PATH']=bin
 p=subprocess.run([paths[0],'--version'],env=env,capture_output=True,text=True,timeout=10)
 r['runtime_version']=(p.stdout+p.stderr).strip();r['runtime_exit']=p.returncode
print(json.dumps(r))
'''
def inspect(h):
 try:
  p=subprocess.run(['ssh','-F','/dev/null','-o','BatchMode=yes','-o','ConnectTimeout=4','-o','ServerAliveInterval=4','-o','ServerAliveCountMax=1','-o','StrictHostKeyChecking=accept-new','-o','UserKnownHostsFile='+str(known),'caninos@'+h,'python3 -'],input=script,capture_output=True,text=True,timeout=20)
  r=json.loads(p.stdout) if p.returncode==0 else {'error':p.stderr[-300:]}
 except Exception as e:r={'error':str(e)}
 r['ip']=h
 (out/'inventory').mkdir(exist_ok=True);(out/'inventory'/f'{h}.json').write_text(json.dumps(r,indent=2))
 print(json.dumps({k:r.get(k) for k in ['ip','hostname','mac','runtime_exit','error']}),flush=True)
 return r
hosts=json.loads((out/'ssh_hosts.json').read_text())
with cf.ThreadPoolExecutor(7) as pool:rs=list(pool.map(inspect,hosts))
(out/'inventory.json').write_text(json.dumps(rs,indent=2))
