#!/usr/bin/env python3
"""Prepare six independent replicas in a new namespace; preserve existing services."""
import argparse
import concurrent.futures as cf
import json
import shlex
import subprocess
from pathlib import Path
from datetime import datetime,timezone
HOSTS=['192.168.50.129','192.168.50.89','192.168.50.169','192.168.50.200','192.168.50.240','192.168.50.195']
BASE='/home/caninos/smarthome_agents/study_v1'
BIN='/home/caninos/llama-offline/llama.cpp/build/bin'
MODEL05='qwen2.5-0.5b-instruct-q5_k_m.gguf'
MODEL15='qwen2.5-1.5b-instruct-q5_k_m.gguf'
SSH=['ssh','-F','/dev/null','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','StrictHostKeyChecking=accept-new']

def ssh(host,cmd,timeout=300):
    p=subprocess.run(SSH+['caninos@'+host,cmd],text=True,capture_output=True,timeout=timeout)
    if p.returncode:raise RuntimeError(f'{host}: {p.returncode}: {p.stderr}\n{p.stdout}')
    return p.stdout

def prepare(host,source,out):
    d=out/host;d.mkdir(parents=True,exist_ok=True)
    inventory=ssh(host,'hostname; uname -a; free -k; df -h /; ps -eo pid,pcpu,rss,args | grep -E "llama|rpc"; sha256sum '+BIN+'/llama-server '+BIN+'/libllama-server-impl.so '+BIN+'/libllama.so '+BIN+'/libggml-cpu.so; '+'LD_LIBRARY_PATH='+BIN+' '+BIN+'/llama-server --version')
    (d/'inventory_before.txt').write_text(inventory)
    ssh(host,'mkdir -p '+BASE+'/models')
    model05=BASE+'/models/'+MODEL05
    exists=ssh(host,'test -f '+model05+' && echo yes || echo no').strip()=='yes'
    if not exists:
        if host=='192.168.50.89':ssh(host,'ln -s /home/caninos/models/'+MODEL05+' '+model05)
        else:
            p=subprocess.run(['scp','-F','/dev/null','-o','BatchMode=yes',str(source),'caninos@'+host+':'+model05+'.partial'],capture_output=True,text=True,timeout=1200)
            if p.returncode:raise RuntimeError(p.stderr)
            ssh(host,'mv '+model05+'.partial '+model05)
    path15=ssh(host,'for p in /home/caninos/models/'+MODEL15+' /home/caninos/llama-offline/models/'+MODEL15+'; do if test -f "$p"; then printf "%s" "$p"; break; fi; done').strip()
    if not path15:raise RuntimeError('1.5B missing '+host)
    hashes=ssh(host,'sha256sum '+model05+' '+path15,timeout=300)
    (d/'model_hashes.txt').write_text(hashes)
    for model,path,port in [('05',model05,19005),('15',path15,19015)]:
        run=BASE+'/'+model
        command=f'{BIN}/llama-server --model {path} --host 0.0.0.0 --port {port} --threads 4 --threads-batch 4 --ctx-size 512 --parallel 1 --n-predict 128 --device none --metrics --no-warmup'
        # New namespace only. Do not overwrite live service or logs.
        startup=f'mkdir -p {run}; if test -f {run}/server.pid && kill -0 "$(cat {run}/server.pid)" 2>/dev/null; then echo already_running; else LD_LIBRARY_PATH={BIN} nohup {command} > {run}/server.log 2>&1 < /dev/null & echo $! > {run}/server.pid; fi'
        (d/(model+'-startup.txt')).write_text(ssh(host,startup))
        (d/(model+'-command.txt')).write_text(command+'\n')
    print('prepared '+host,flush=True)
    return host

def main():
    a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);args=a.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    source=Path('/tmp/smarthome-v1-model05.gguf')
    if not source.exists():
        subprocess.run(['scp','-F','/dev/null','-o','BatchMode=yes','caninos@192.168.50.89:/home/caninos/models/'+MODEL05,str(source)],check=True,timeout=300)
    results=[]
    with cf.ThreadPoolExecutor(max_workers=6) as pool:
        tasks={pool.submit(prepare,h,source,args.out):h for h in HOSTS}
        for f in cf.as_completed(tasks):
            try:results.append({'host':f.result(),'ok':True})
            except Exception as e:results.append({'host':tasks[f],'ok':False,'error':str(e)});print(str(e),flush=True)
    (args.out/'summary.json').write_text(json.dumps(results,indent=2)+'\n')
    return 0 if all(r['ok'] for r in results) else 1
if __name__=='__main__':raise SystemExit(main())
