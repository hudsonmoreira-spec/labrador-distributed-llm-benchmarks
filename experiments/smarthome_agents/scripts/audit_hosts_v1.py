#!/usr/bin/env python3
"""Verify binaries, dependencies, model files and resident service configuration."""
import concurrent.futures as cf
import hashlib
import json
import sys
from pathlib import Path
from prepare_hosts_v1 import HOSTS,BASE,BIN,ssh
from run_study_v1 import get,PORTS

OUT=Path(sys.argv[1]);OUT.mkdir(parents=True,exist_ok=True)
EXPECTED={'qwen2.5-0.5b-instruct-q5_k_m.gguf':'041474553fcabfc2a2d67903f9d2c2e50bd92528e670da4f33b5d0ce6e59fd55',
          'qwen2.5-1.5b-instruct-q5_k_m.gguf':'b46661073c18e5b56a41fa320975f866a00def1ff08feef4718e013258896f8c'}
HERE=Path(__file__).resolve().parent

def audit(h):
    properties={m:get(f'http://{h}:{p}'+('/health' if m=='rules' else '/props')) for m,p in PORTS.items()}
    for m in ['05','15']:
        assert properties[m]['total_slots']==1
        assert properties[m]['default_generation_settings']['n_ctx']==512
        assert properties[m]['build_info']=='b9584-e25a32e98'
    paths=[properties[m]['model_path'] for m in ['05','15']]
    hashes=ssh(h,'sha256sum '+BIN+'/llama-server '+BIN+'/lib*.so '+BASE+'/rules/*.py '+' '.join(paths),timeout=300)
    (OUT/(h+'-hashes.txt')).write_text(hashes)
    runtime={}
    for line in hashes.splitlines():
        digest,path=line.split(maxsplit=1);name=Path(path).name
        if name.endswith('.gguf'):assert EXPECTED[name]==digest
        elif '/rules/' in path:assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==digest
        else:runtime[name]=digest
    command=ssh(h,'for d in '+BASE+'/05 '+BASE+'/15 '+BASE+'/rules; do p=$(cat "$d/server.pid"); tr "\\0" " " < /proc/$p/cmdline; printf "\\n"; done; hostname; uname -a; free -k; ps -eo pid,pcpu,rss,args | grep -E "llama|rules_server"',timeout=30)
    (OUT/(h+'-processes.txt')).write_text(command)
    (OUT/(h+'-properties.json')).write_text(json.dumps(properties,indent=2)+'\n')
    print('verified '+h,flush=True)
    return runtime
with cf.ThreadPoolExecutor(max_workers=6) as pool:
    runtime=list(pool.map(audit,HOSTS))
assert all(r==runtime[0] for r in runtime)
(OUT/'verified.json').write_text(json.dumps({'hosts':HOSTS,'runtime_components':runtime[0],'models':EXPECTED,'all_components_identical':True},indent=2)+'\n')
