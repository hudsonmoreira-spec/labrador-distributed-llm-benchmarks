#!/usr/bin/env python3
import concurrent.futures as cf
import hashlib
import json
import shlex
from pathlib import Path
import validate_backup_pool as v
import run_prompt_diagnostic as d

SHA='041474553fcabfc2a2d67903f9d2c2e50bd92528e670da4f33b5d0ce6e59fd55'
LOCAL=Path('/home/hudymoreira/.cache/labrador-revision-20261123/qwen2.5-0.5b-instruct-q5_k_m.gguf')
MODEL=v.REMOTE+'/models/qwen2.5-0.5b-instruct-q5_k_m.gguf'
OUT=d.HERE/'backup_validation_05'

def run(h):
    r={'host':h,'model':'Qwen2.5-0.5B-Instruct Q5_K_M','started_at':d.now()}
    check=v.ssh(h,f'sha256sum {MODEL}.partial')
    assert check.split()[0]==SHA,check
    v.ssh(h,f'mv {MODEL}.partial {MODEL}')
    r['model_sha256']=SHA
    launcher=f'''#!/bin/sh
set -eu
export LD_LIBRARY_PATH={d.BIN}
exec {d.BIN}/llama-server --model {MODEL} --host 0.0.0.0 --port 19115 --threads 4 --threads-batch 4 --ctx-size 512 --parallel 1 --n-predict 128 --device none --metrics --no-warmup
'''
    v.ssh(h,f'printf %s {shlex.quote(launcher)} > {v.REMOTE}/start-0.5b.sh; chmod 700 {v.REMOTE}/start-0.5b.sh')
    try:
        d.prepare(h,OUT)
        r['health']=d.http(h,'/health')
        r['props']=json.loads((OUT/(h+'-props.json')).read_text())
        r['smoke_response']=d.http(h,'/v1/chat/completions',{'messages':[{'role':'user','content':'Oi'}],'max_tokens':1,'temperature':0,'seed':801,'cache_prompt':False},90)
        assert r['smoke_response'].get('choices');r['ready']=True
    except Exception as e:r['ready']=False;r['error']=repr(e)
    finally:
        try:
            cmd=f'p=$(cat {d.REMOTE}/server.pid 2>/dev/null); if test -n "$p" && test -r /proc/$p/cmdline && tr "\\0" " " </proc/$p/cmdline | grep -q -- "--port 19115"; then kill "$p"; fi; cat {d.REMOTE}/server.log'
            (OUT/(h+'-server.log')).write_text(v.ssh(h,cmd));r['temporary_server_stopped']=True
        except Exception as e:r['cleanup_error']=repr(e)
        r['finished_at']=d.now();d.save(OUT/(h+'-validation.json'),r)
    print(json.dumps({k:r[k] for k in ['host','ready','finished_at']}),flush=True)
    return r

if __name__=='__main__':
    assert hashlib.sha256(LOCAL.read_bytes()).hexdigest()==SHA
    OUT.mkdir(exist_ok=False)
    d.MODEL=MODEL;d.REMOTE=v.REMOTE+'_05'
    with cf.ThreadPoolExecutor(max_workers=2) as pool:rs=list(pool.map(run,v.HOSTS))
    p=d.HERE/'backup_pool.json';manifest=json.loads(p.read_text())
    manifest['model_05_sha256']=SHA
    for backup in manifest['backups']:
        r=next(r for r in rs if r['host']==backup['host'])
        backup['model_05_ready']=r['ready'];backup['model_05_launcher']=v.REMOTE+'/start-0.5b.sh'
        backup['model_05_evidence']=str((OUT/(r['host']+'-validation.json')).relative_to(d.HERE))
    d.save(p,manifest)
    assert all(r['ready'] for r in rs)
