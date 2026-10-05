#!/usr/bin/env python3
"""Rebuild the immutable discussion preview assets from preserved raw attempts."""
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / 'generated'
RUN = ROOT / 'experiments/smarthome_agents/runs/20261005T1445-single-agent-chat-schema-1p5b-validatorfix'
rows = [json.loads(p.read_text()) for p in sorted(RUN.glob('*/summary.json'))]
assert len(rows) == 12
assert sum(r['result_flags']['structured_response_valid'] for r in rows) == 12
assert sum(r['result_flags']['task_completed'] for r in rows) == 9
assert sum(r['validation']['reason'] == 'scenario_prohibited_action' for r in rows) == 3
latencies = sorted(r['inference']['elapsed_s'] for r in rows)
groups = defaultdict(list)
for r in rows:
    groups[r['scenario_id']].append(r)
assert len(groups) == 4 and all(len(rs) == 3 for rs in groups.values())
labels = {'dev-ambiguous-light-clarify': 'Luz sem cômodo', 'dev-light-off-sala': 'Apagar sala', 'dev-light-on-sala': 'Acender sala', 'dev-light-quarto-preserve-sala': 'Quarto; preservar sala'}
OUT.mkdir(exist_ok=True)
table_rows = []
for k, rs in sorted(groups.items()):
    valid = sum(r['result_flags']['structured_response_valid'] for r in rs)
    success = sum(r['result_flags']['task_completed'] for r in rs)
    median = statistics.median(r['inference']['elapsed_s'] for r in rs)
    table_rows.append(f"{labels[k]} & {valid}/3 & {success}/3 & {median:.3f}" + chr(92)*2)
(OUT/'rows.tex').write_text(chr(10).join(table_rows) + chr(10) + chr(92) + 'bottomrule' + chr(10))

metrics = {'Median': statistics.median(latencies), 'Pninetyfive': latencies[math.ceil(.95*len(latencies))-1], 'Mean': statistics.mean(latencies), 'Min': min(latencies), 'Max': max(latencies)}
(OUT/'pilot.tex').write_text(''.join('\\newcommand{\\Pilot'+k+'}{'+f'{v:.3f}'+'}\n' for k,v in metrics.items()))
(OUT/'audit.json').write_text(json.dumps({'source': str(RUN.relative_to(ROOT)), 'attempts':len(rows), 'scenarios':len(groups), 'latency_s':metrics, 'p95_method':'nearest rank', 'structured_valid':12, 'task_completed':9, 'blocked_by_historical_evaluator':3}, indent=2)+'\n')
print(json.dumps(metrics))
