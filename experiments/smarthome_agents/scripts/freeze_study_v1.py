#!/usr/bin/env python3
"""Freeze before any held-out execution; refuses to replace an existing freeze."""
import argparse
import hashlib
import json
import subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'experiments/smarthome_agents/study_v1'
a=argparse.ArgumentParser();a.add_argument('--development',type=Path,required=True);args=a.parse_args()
assert (args.development/'completed.json').exists()
rows=[json.loads(p.read_text()) for p in args.development.glob('attempts/*/summary.json')]
for model in ['05','15','rules']:
    rs=[r for r in rows if r['model']==model]
    assert len(rs)==16
    assert all(r['execution_completed'] and r['cache_tokens']==0 for r in rs)
assert len(json.loads((BASE/'reserved.json').read_text()))==40
files=list(BASE.glob('*.json'))+list(BASE.glob('*.md'))
files+=[ROOT/'experiments/smarthome_agents/scripts'/name for name in ['study_v1.py','smarthome_pilot.py','rules_server_v1.py','run_study_v1.py','analyze_study_v1.py','prepare_hosts_v1.py']]
files+=list((ROOT/'experiments/smarthome_agents/tests').glob('*.py'))
files+=[ROOT/'docs/smarthome_agents/policy_v1.md',ROOT/'experiments/smarthome_agents/runs/20261005-study-v1-audit/verified.json']
manifest={'frozen_at':datetime.now(timezone.utc).isoformat(),'reference_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
          'development_run':str(args.development),'held_out_observed_before_freeze':False,
          'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}}
with (BASE/'freeze.json').open('x') as f:json.dump(manifest,f,ensure_ascii=False,indent=2);f.write('\n')
print('Frozen',len(manifest['files']),'files')
