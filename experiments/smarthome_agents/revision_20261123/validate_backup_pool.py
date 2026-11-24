#!/usr/bin/env python3
"""Prepare isolated experimental launchers and smoke-test the verified backup boards."""
import concurrent.futures as cf
import json
import shlex
from pathlib import Path
import run_prompt_diagnostic as d

HOSTS=['192.168.50.85','192.168.50.200']
OUT=d.HERE/'backup_validation'
BIN=d.BIN
REMOTE='/home/caninos/smarthome_agents/revision_20261123_backup'
MODEL_SHA='b46661073c18e5b56a41fa320975f866a00def1ff08feef4718e013258896f8c'
RUNTIME_SHA='a46782e75231c0a4a75a1e38afbbc5d7b72d92c8d834d6bb8b5020a0e1e79a87'
ssh0=d.ssh
def ssh(h,c,timeout=90):return ssh0(h,c,max(timeout,90))
d.ssh=ssh
def snapshot(h):return ssh(h,'cat /proc/meminfo; cat /proc/loadavg; ps -eo pid,pcpu,rss,comm')
d.snapshot=snapshot
d.REMOTE=REMOTE

def validate(h):
    result={'host':h,'started_at':d.now(),'purpose':'Backup readiness only, not a benchmark score'}
    audit=ssh(h,f'sha256sum {d.MODEL} {BIN}/llama-server; uname -m; getconf _NPROCESSORS_ONLN; sha256sum {BIN}/*.so')
    (OUT/(h+'-hashes.txt')).write_text(audit)
    assert MODEL_SHA in audit and RUNTIME_SHA in audit
    # Install an isolated, explicit launcher; does not alter existing services or boot settings.
    launcher=f'''#!/bin/sh
set -eu
export LD_LIBRARY_PATH={BIN}
exec {BIN}/llama-server --model {d.MODEL} --host 0.0.0.0 --port 19115 --threads 4 --threads-batch 4 --ctx-size 512 --parallel 1 --n-predict 128 --device none --metrics --no-warmup
'''
    ssh(h,f'mkdir -p {REMOTE}; printf %s {shlex.quote(launcher)} > {REMOTE}/start-1.5b.sh; chmod 700 {REMOTE}/start-1.5b.sh')
    try:
        d.prepare(h,OUT)
        result['health']=d.http(h,'/health')
        result['props']=json.loads((OUT/(h+'-props.json')).read_text())
        # One generated token validates actual model execution, not task accuracy.
        result['smoke_response']=d.http(h,'/v1/chat/completions',{'messages':[{'role':'user','content':'Oi'}],'max_tokens':1,'temperature':0,'seed':801,'cache_prompt':False},timeout=90)
        assert result['smoke_response'].get('choices')
        result['ready']=True
    except Exception as e:
        result['ready']=False;result['error']=repr(e)
    finally:
        try:
            stop=f'p=$(cat {REMOTE}/server.pid 2>/dev/null); if test -n "$p" && test -r /proc/$p/cmdline && tr "\\0" " " </proc/$p/cmdline | grep -q -- "--port 19115"; then kill "$p"; fi; cat {REMOTE}/server.log'
            (OUT/(h+'-server.log')).write_text(ssh(h,stop))
            result['temporary_server_stopped']=True
        except Exception as e:result['cleanup_error']=repr(e)
        result['finished_at']=d.now();d.save(OUT/(h+'-validation.json'),result)
    print(json.dumps({k:result[k] for k in ['host','ready','finished_at']}),flush=True)
    return result

if __name__=='__main__':
    OUT.mkdir(exist_ok=False)
    with cf.ThreadPoolExecutor(max_workers=2) as pool:rs=list(pool.map(validate,HOSTS))
    d.save(d.HERE/'backup_pool.json',{'validated_at':d.now(),'network':'Ethernet','configuration':{'runtime':'b9584-e25a32e98','model_sha256':MODEL_SHA,'runtime_sha256':RUNTIME_SHA,'ctx':512,'threads':4,'port':19115},'backups':[{'host':r['host'],'ready':r['ready'],'evidence':str((OUT/(r['host']+'-validation.json')).relative_to(d.HERE)),'launcher':REMOTE+'/start-1.5b.sh'} for r in rs]})
    assert all(r['ready'] for r in rs)
