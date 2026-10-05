#!/usr/bin/env python3
import concurrent.futures as cf
import subprocess
from pathlib import Path
from prepare_hosts_v1 import HOSTS,BASE,ssh
HERE=Path(__file__).resolve().parent

def deploy(host):
    path=BASE+'/rules'
    ssh(host,'mkdir -p '+path)
    # Refresh only this study service before freeze; preserve earlier source in Git.
    ssh(host,'if test -f '+path+'/server.pid; then p=$(cat '+path+'/server.pid); if test "$(readlink /proc/$p/cwd)" = '+path+'; then kill "$p"; fi; fi')
    subprocess.run(['scp','-F','/dev/null','-o','BatchMode=yes',*[str(HERE/f) for f in ['smarthome_pilot.py','study_v1.py','rules_server_v1.py']],'caninos@'+host+':'+path+'/'],check=True,capture_output=True)
    ssh(host,'cd '+path+'; if test -f server.pid && kill -0 "$(cat server.pid)" 2>/dev/null; then echo already_running; else nohup python3 rules_server_v1.py > server.log 2>&1 < /dev/null & echo $! > server.pid; fi')
    print('rules ready '+host,flush=True)
if __name__=='__main__':
    with cf.ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(deploy,HOSTS))
