#!/usr/bin/env python3
"""Resume undispatched/missing diagnostic records without replacing any completed result."""
import concurrent.futures as cf
import hashlib
import json
from pathlib import Path
import run_prompt_diagnostic as d

def main():
    previous=d.HERE/'prompt_diagnostic_v1'
    out=d.HERE/'prompt_diagnostic_resume_v3'
    out.mkdir(exist_ok=False)
    plan=json.loads((previous/'plan_frozen_before_dispatch.json').read_text())
    cases={c['scenario_id']:c for c in json.loads((d.ROOT/'experiments/smarthome_agents/study_v1/development.json').read_text())}
    done={(r['host'],r['variant'],r['scenario_id']) for p in previous.glob('*/summary.json') for r in [json.loads(p.read_text())]}
    queues={h:[a for a in plan['queues'][h] if (h,a['variant'],a['scenario_id']) not in done] for h in d.HOSTS}
    queues['192.168.50.89']=queues.pop('192.168.50.195')
    d.save(out/'resume_plan_before_dispatch.json',{'created_at':d.now(),'original_plan_sha256':hashlib.sha256((previous/'plan_frozen_before_dispatch.json').read_bytes()).hexdigest(),'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'reason':'SSH snapshot timeout interrupted host queues. Resume v2 completed no inference because lab8 (.195) became unreachable. Reassign its three missing requests to lab2 (.89), with identical audited runtime/model hashes. Retain all existing summaries; do not replace responses. Prompts and inference settings unchanged; host reassignment limits timing comparison.','retained_records':len(done),'queues':queues})
    original_ssh=d.ssh
    def robust_ssh(h,command,timeout=90):return original_ssh(h,command,timeout=max(timeout,90))
    d.ssh=robust_ssh
    def safe_snapshot(h):
        try:return d.ssh(h,'cat /proc/meminfo; cat /proc/loadavg; ps -eo pid,pcpu,rss,comm',timeout=90)
        except Exception as e:return 'INSTRUMENTATION ERROR (not inference): '+repr(e)+'\n'
    d.snapshot=safe_snapshot
    active=[h for h in d.HOSTS if queues.get(h)]
    # Separate log namespace keeps the original logs intact.
    d.REMOTE='/home/caninos/smarthome_agents/revision_20261123_resume_v3'
    try:
        with cf.ThreadPoolExecutor(max_workers=len(active)) as pool:list(pool.map(lambda h:d.prepare(h,out),active))
        def worker(h):
            for a in queues[h]:d.attempt(h,a['variant'],cases[a['scenario_id']],a['index'],out)
        with cf.ThreadPoolExecutor(max_workers=len(active)) as pool:list(pool.map(worker,active))
    finally:
        for h in active:
            try:
                stop=f'p=$(cat {d.REMOTE}/server.pid 2>/dev/null); if test -n "$p" && test -r /proc/$p/cmdline && tr "\\0" " " </proc/$p/cmdline | grep -q -- "--port {d.PORT}"; then kill "$p"; fi; cat {d.REMOTE}/server.log'
                (out/(h+'-server.log')).write_text(d.ssh(h,stop))
            except Exception as e:(out/(h+'-cleanup-error.txt')).write_text(repr(e))
if __name__=='__main__':main()
