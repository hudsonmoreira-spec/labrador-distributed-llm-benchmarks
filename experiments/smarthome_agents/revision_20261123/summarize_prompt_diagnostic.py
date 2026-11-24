#!/usr/bin/env python3
"""Verify and summarize the complete prespecified development-only follow-up."""
import csv
import hashlib
import json
import statistics
from pathlib import Path
import run_prompt_diagnostic as d

b=Path(__file__).resolve().parent
plan=json.loads((b/'prompt_diagnostic_v1/plan_frozen_before_dispatch.json').read_text())
expected={a['index']:(a['variant'],a['scenario_id'],h) for h,q in plan['queues'].items() for a in q}
records={}
for campaign in ['prompt_diagnostic_v1','prompt_diagnostic_resume_v3']:
    for f in sorted((b/campaign).glob('*/summary.json')):
        i=int(f.parent.name.split('-')[0]);assert i not in records,('Duplicate',i)
        r=json.loads(f.read_text());v,case,host=expected[i]
        assert (r['variant'],r['scenario_id'])==(v,case)
        assert r['host']==host or (host=='192.168.50.195' and r['host']=='192.168.50.89')
        payload=json.loads((f.parent/'request.json').read_text())
        assert payload['temperature']==0 and payload['seed']==801 and payload['max_tokens']==128
        assert payload['cache_prompt'] is False
        assert payload['response_format']['json_schema']['schema']==plan['schema']
        system=plan['variants'][v];system=system['system'] if isinstance(system,dict) else system
        assert payload['messages'][0]['content']==system
        if v=='pt_two_examples':assert payload['messages'][1:5]==plan['variants'][v]['examples']
        assert r['completed'] and r['error'] is None,('Incomplete inference',i)
        r['record_path']=str(f.relative_to(b));r['record_sha256']=hashlib.sha256(f.read_bytes()).hexdigest()
        records[i]=r
assert set(records)==set(expected),('Missing planned records',sorted(set(expected)-set(records)))
summary={}
for v in plan['variants']:
    rs=[r for r in records.values() if r['variant']==v]
    summary[v]={'attempts':len(rs),'task_successes':sum(r['evaluation']['task_completed'] for r in rs),'review_pending':sum(r['evaluation'].get('review_pending',False) for r in rs),'structured_valid':sum(r['parse']['structured_valid'] for r in rs),'median_s':statistics.median(r['elapsed_s'] for r in rs),'clear_successes':sum(r['evaluation']['task_completed'] for r in rs if r['category']=='clear'),'clear_attempts':sum(r['category']=='clear' for r in rs),'prompt_tokens_range':[min(r['usage']['prompt_tokens'] for r in rs),max(r['usage']['prompt_tokens'] for r in rs)]}
d.save(b/'diagnostic_summary.json',{'created_at':d.now(),'scope':'Exploratory development-only, eight pre-existing cases, one repetition; not reserved-set scores','conditions':summary,'completed':24,'instrumentation':'18 original records retained; six remaining requests resumed after memory snapshot timeouts. Lab8 became unreachable; its three remaining requests reassigned to lab2 with identical audited runtime/model hashes. No completed inference replaced. SSH memory errors not graded as inference failures.','attempts':[records[i] for i in sorted(records)]})
with (b/'diagnostic_attempts.csv').open('w') as f:
    w=csv.writer(f);w.writerow(['index','variant','case','host','success','seconds','raw_record','sha256'])
    for i,r in sorted(records.items()):w.writerow([i,r['variant'],r['scenario_id'],r['host'],r['evaluation']['task_completed'],r['elapsed_s'],r['record_path'],r['record_sha256']])
lines=['# Exploratory prompt diagnostic — 23 November 2026','','This separate follow-up reuses eight existing DEVELOPMENT cases, one repetition each. It does not replace or regrade any of the original 240 reserved quality attempts. Prompts/assignments were recorded before dispatch. Qwen2.5-1.5B-Instruct Q5_K_M, original audited b9584 runtime, CPU 4 threads, ctx512, max128, seed801, temperature0, no prompt caching, original JSON schema throughout.','','| Instructions | Success | Clear instructions | Valid structure | Median HTTP latency | Prompt tokens |','|---|---|---|---|---|---|']
for v,r in summary.items():lines.append(f"| {v} | {r['task_successes']}/8 | {r['clear_successes']}/{r['clear_attempts']} | {r['structured_valid']}/8 | {r['median_s']:.1f} s | {r['prompt_tokens_range'][0]}–{r['prompt_tokens_range'][1]} |")
lines+=['','English baseline uses the unchanged original system prompt. Portuguese zero-shot translates/explicates the same policy. Portuguese two-example adds one off-command example and one missing-room clarification example; their phrasings differ from development requests. See the original frozen plan for exact text.','','## Limits and interruptions','','The initial campaign stopped two host queues after SSH memory-snapshot timeouts. It retained 18 completed inference records. The first resume ran no inference because lab8 became unreachable. Six missing requests were then resumed, preserving prompts and settings. Three originally assigned to lab8 were reassigned to lab2. Host reassignment, single repetition, and development reuse preclude causal attribution, generalization or a validated model ranking. No new six-board scaling measurement was made. Missing memory instrumentation is disclosed rather than reconstructed.','','All 24 unique planned requests are checked by summarize_prompt_diagnostic.py; completed records are never overwritten. Existing port8080 services are preserved; temporary supplementary servers are stopped after use. Server cleanup on the unreachable lab8 cannot be verified until connectivity returns.','','These observations test configuration sensitivity; they do not establish a size-dependent explanation of the original 1.5B result or validate a rules-first hybrid. The four original assisted clarification judgments remain a separate human-review requirement.','']
(b/'DIAGNOSTIC_REPORT.md').write_text('\n'.join(lines))
print(json.dumps(summary,ensure_ascii=False,indent=2))
