#!/usr/bin/env python3
"""Verify smart-home submission evidence offline, without contacting any board."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
BASE = Path('experiments/smarthome_agents')
PAPER = Path('paper/smarthome_agents/study_v1')
EVIDENCE = 'a834b8255f736fb59425b146be183c17866a2c7d'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    return json.loads(path.read_text())


def check(source, manifest):
    metadata = load(manifest)
    require(metadata['evidence_commit'] == EVIDENCE, 'Unexpected evidence snapshot')
    for name, expected in metadata['sha256'].items():
        require(hashlib.sha256((source / name).read_bytes()).hexdigest() == expected, f'Hash mismatch: {name}')
    freeze = load(source / BASE / 'study_v1/freeze.json')
    for name, expected in freeze['files'].items():
        require(hashlib.sha256((source / name).read_bytes()).hexdigest() == expected, f'Frozen protocol changed: {name}')
    with tempfile.TemporaryDirectory(prefix='smarthome-submission-') as folder:
        work = Path(folder)
        for name in metadata['sha256']:
            target = work / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / name, target)
        metrics = {}
        compared = []
        for phase, total in [('quality', 240), ('scale', 108)]:
            run = work / BASE / 'runs' / ('20261006-study-v1-' + phase)
            out = work / BASE / 'analysis' / (phase + '-v1')
            for script in ['analyze_study_v1.py', 'analyze_action_steps_v1.py']:
                subprocess.run([sys.executable, str(work / BASE / 'scripts' / script), '--run', str(run), '--out', str(out)], check=True, capture_output=True, text=True)
            for original in sorted((source / BASE / 'analysis' / (phase + '-v1')).iterdir()):
                if original.is_file():
                    require(original.read_bytes() == (out / original.name).read_bytes(), f'Reconstruction differs: {phase}/{original.name}')
                    compared.append(str(original.relative_to(source)))
            audit = load(out / 'audit.json')
            require(audit['attempts'] == audit['starts'] == total and audit['incomplete'] == 0, f'Incomplete {phase} campaign')
            require(load(run / 'completed.json')['status'] == 'all_planned_attempts_recorded', 'Missing completion marker')
            metrics[phase] = {r['model']: r for r in load(out / 'metrics.json')}
        generated = work / 'regenerated'
        # This maintained reporting script adds explicit provenance flags only;
        # the frozen evaluator and measurements are not changed.
        subprocess.run([sys.executable, str(ROOT / BASE / 'scripts/make_study_assets.py'), '--quality', str(work / BASE / 'analysis/quality-v1'), '--scale', str(work / BASE / 'analysis/scale-v1'), '--out', str(generated), '--protocol-commit', '2bab455', '--data-commit', 'd2efabd', '--date', '2026-10-06'], check=True, capture_output=True, text=True)
        asset_count = 0
        for original in sorted((source / PAPER / 'generated').iterdir()):
            if original.suffix in {'.tex', '.json'}:
                require(original.read_bytes() == (generated / original.name).read_bytes(), f'Asset differs: {original.name}')
                asset_count += 1
        quality = metrics['quality']
        for model, count in [('rules',42),('05',30),('15',12)]:
            m = quality[model]
            require(m['n'] == 80 and m['scenarios'] == 40 and m['valid'] == 80, 'Quality denominator/validity mismatch')
            require(m['successes'] == m['automatic_successes'] == count, 'Success count differs')
            require(m['operational_failures'] == m['non_stop'] == m['cache_nonzero'] == 0, 'Unexpected failure/cache condition')
        ledger = load(work / BASE / 'runs/20261006-study-v1-quality/manual_reviews.json')
        require(len(ledger) == 4 and all(r['decision'] == 'fail' and r['human_validation_pending'] for r in ledger), 'Review status changed')
        require(quality['05']['manual_reviewed'] == quality['05']['human_validation_pending'] == 4, 'Assisted-review count differs')
        cases = load(work / BASE / 'study_v1/reserved.json')
        require(len(cases) == 40 and set(Counter(r['category'] for r in cases).values()) == {8}, 'Case/category coverage differs')
        # Recheck request parameters and chronology directly from immutable attempts.
        per_host = defaultdict(list)
        for phase in ['quality','scale']:
            run = work / BASE / 'runs' / ('20261006-study-v1-' + phase)
            campaign = load(run / 'campaign.json')
            require(datetime.fromisoformat(campaign['started_at']) > datetime.fromisoformat(freeze['frozen_at']), 'Held-out campaign started before freeze')
            require(campaign['configuration'] == {'cache_prompt':False,'max_tokens':128,'seeds':[801,802],'temperature':0,'timeout_s':180}, 'Campaign settings differ')
            for path in sorted(run.glob('**/attempts/*/summary.json')):
                row = load(path)
                request = load(path.with_name('request.json'))
                if row['model'] != 'rules':
                    require(request['cache_prompt'] is False and request['max_tokens'] == 128 and request['temperature'] == 0 and request['seed'] in [801,802], 'Request differs from protocol')
                else:
                    require(set(request) == {'scenario'} and set(request['scenario']) == {'resident_request','initial_state','permissions'}, 'Rules service received evaluator-only fields')
                require(row['execution_completed'] and row['dispatched'] and row['finish_reason'] == 'stop', 'Unexpected completion')
                require(row['host'] in campaign['hosts'], 'Unexpected host')
                per_host[(phase,row['host'])].append((row['dispatch_monotonic_s'],row['response_monotonic_s']))
            for (ph,host), intervals in per_host.items():
                if ph == phase:
                    intervals.sort()
                    require(all(a[1] <= b[0] for a,b in zip(intervals,intervals[1:])), f'Concurrent inference recorded on {host}')
        scale_rows = load(generated / 'scale_summary.json')
        batch_count = 0
        for batch_path in sorted((work / BASE / 'runs/20261006-study-v1-scale').glob('scale-*/batch.json')):
            batch = load(batch_path)
            attempts = [load(p) for p in batch_path.parent.glob('attempts/*/summary.json')]
            require(len(attempts) == batch['requests'] == 6, 'Batch size differs')
            span = max(r['response_monotonic_s'] for r in attempts) - min(r['dispatch_monotonic_s'] for r in attempts)
            require(math.isclose(span,batch['window_s'],rel_tol=1e-10,abs_tol=1e-9), 'Batch window differs from dispatch/response timestamps')
            successes = sum(r['evaluation']['task_completed'] for r in attempts)
            require(successes == batch['successes'], 'Batch success differs')
            require(math.isclose(successes*60/span,batch['completed_tasks_per_min'],rel_tol=1e-10), 'Batch rate differs')
            require(len(set(r['host'] for r in attempts)) == batch['replicas'], 'Replica/host assignment differs')
            batch_count += 1
        require(batch_count == 18, 'Batch count differs')
        final = work / BASE / 'runs/20261006-study-v1-final-audit'
        verified = load(final / 'verified.json')
        hardware = []
        for host in verified['hosts']:
            hashes = {Path(parts[1]).name:parts[0] for line in (final / (host+'-hashes.txt')).read_text().splitlines() if len(parts:=line.split())==2}
            require(all(hashes[name] == sha for name,sha in (verified['runtime_components'] | verified['models']).items()), 'Runtime/model hash differs across hosts')
            process = (final / (host+'-processes.txt')).read_text()
            for port in ['19005','19015']:
                line = next(l for l in process.splitlines() if '--port '+port+' ' in l)
                require(all(flag in line for flag in ['--threads 4','--threads-batch 4','--ctx-size 512','--parallel 1','--n-predict 128','--device none']), 'Resident server settings differ')
            inventory = (work / BASE / 'runs/20261005T130126Z-inventory-v2' / (host+'.txt')).read_text()
            record = dict(line.split('=',1) for line in inventory.splitlines() if '=' in line)
            require(record['arch'] == 'aarch64' and record['cpu_count'] == '4' and 'Debian GNU/Linux 12' in record['os'], 'Hardware/OS record differs')
            memory = int(record['mem_total_kb'])
            hardware.append({'host':host,'memtotal_kib':memory,'os_visible_gib':memory/1024**2})
        development = {}
        for name in ['20261005-study-v1-development','20261006-study-v1-development-2']:
            run = work / BASE / 'runs' / name
            require((run / 'completed.json').exists(), 'Development completion marker missing')
            count = len(list(run.glob('attempts/*/summary.json')))
            require(count == 48, 'Development count differs')
            development[name] = count
        return {'status':'pass','evidence_commit':EVIDENCE,'hashed_files':len(metadata['sha256']),'frozen_protocol_files':len(freeze['files']),'analysis_files_reconstructed_byte_for_byte':len(compared),'generated_text_assets_reconstructed_byte_for_byte':asset_count,'quality':quality,'scale':scale_rows,'scale_batches_checked':batch_count,'development_attempts':development,'hardware':hardware,'assisted_reviews':{'count':4,'human_validation_pending':True,'added_successes':0,'qwen05_success_count_if_all_four_were_accepted':34,'qwen05_success_percent_range':[37.5,42.5],'rules_success_percent':52.5,'ranking_unchanged_under_this_bound':True},'scope':'Offline raw-response/evaluator reconstruction, recorded hashes/settings and batch timing checks; no new experiment or human semantic validation.','generator_sha256':hashlib.sha256((ROOT / BASE / 'scripts/make_study_assets.py').read_bytes()).hexdigest()}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,default=ROOT)
    p.add_argument('--manifest',type=Path,default=ROOT / PAPER / 'artifact/evidence-manifest.json')
    p.add_argument('--output',type=Path)
    args = p.parse_args()
    result = json.dumps(check(args.source.resolve(),args.manifest.resolve()),indent=2)+'\n'
    if args.output:args.output.write_text(result)
    print(result,end='')


if __name__ == '__main__':
    main()
