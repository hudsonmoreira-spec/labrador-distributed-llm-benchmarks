#!/usr/bin/env python3
import concurrent.futures as cf,json,sys,shlex,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'cluster_ready_20261125'))
import provision,select_host
POOL=json.loads((HERE.parent/'cluster_ready_20261125/pool.json').read_text())
REMOTE='/home/caninos/smarthome_agents/hybrid_comparison_20261125'
FILES={name:(HERE/name).read_text() for name in ['controller.py']}
FILES.update({name:(HERE.parent/'scripts'/name).read_text() for name in ['study_v1.py','smarthome_pilot.py']})
CODE=r'''import json,subprocess,sys,hashlib
from pathlib import Path
b=json.load(sys.stdin);base=Path(b['remote']);base.mkdir(parents=True,exist_ok=True)
assert Path('/sys/class/net/end0/address').read_text().strip()==b['mac']
for name,text in b['files'].items():(base/name).write_text(text)
unit=f'''+'"""'+'''[Unit]
Description=SmartHome supplementary rules-first comparison endpoint
Wants=network-online.target smarthome-benchmark-05.service
After=network-online.target smarthome-benchmark-05.service
[Service]
User=caninos
WorkingDirectory={base}
ExecStart=/usr/bin/python3 {base}/controller.py
Restart=on-failure
RestartSec=3
[Install]
WantedBy=multi-user.target
'''+'"""'+'''
(base/'smarthome-hybrid-comparison.service').write_text(unit)
subprocess.run(['sudo','-n','install','-m','644',str(base/'smarthome-hybrid-comparison.service'),'/etc/systemd/system/smarthome-hybrid-comparison.service'],check=True)
subprocess.run(['sudo','-n','systemctl','daemon-reload'],check=True)
subprocess.run(['sudo','-n','systemctl','enable','--now','smarthome-hybrid-comparison.service'],check=True,capture_output=True)
print(json.dumps({'files':{n:hashlib.sha256((base/n).read_bytes()).hexdigest() for n in b['files']},'enabled':subprocess.check_output(['systemctl','is-enabled','smarthome-hybrid-comparison.service'],text=True).strip()}))
'''
def deploy(b):
 r=json.loads(provision.ssh(b['ip'],'python3 -c '+shlex.quote(CODE),json.dumps({'files':FILES,'mac':b['mac'],'remote':REMOTE}),60))
 r['ip']=b['ip'];print(b['ip'],'endpoint installed',flush=True);return r
if __name__=='__main__':
 health=select_host.select(POOL);assert all(r['ready'] for r in health['checks']),health
 with cf.ThreadPoolExecutor(7) as ex:rs=list(ex.map(deploy,POOL['boards']))
 (HERE/'deployment.json').write_text(json.dumps(rs,indent=2))
 assert all(r['files']=={n:hashlib.sha256(s.encode()).hexdigest() for n,s in FILES.items()} for r in rs)
