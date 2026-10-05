#!/usr/bin/env python3
"""Reconstruct all study tables from raw HTTP responses and immutable attempts."""
import argparse
import csv
import json
import math
import statistics as stats
from collections import defaultdict
from pathlib import Path
import study_v1 as study
import smarthome_pilot as pilot

ROOT=Path(__file__).resolve().parents[3]

def percentile(xs,p=.95):
    return sorted(xs)[math.ceil(p*len(xs))-1] if xs else None

def write_csv(path,rows):
    if not rows:return
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def memory_values(path):
    values={}
    if path.exists():
        for line in path.read_text().splitlines():
            if line.startswith(('VmRSS:','VmHWM:')):
                key,val,*_=line.split();values[key.rstrip(':')]=int(val)
    return values

def main():
    a=argparse.ArgumentParser();a.add_argument('--run',type=Path,required=True);a.add_argument('--out',type=Path,required=True);args=a.parse_args()
    args.run=args.run.resolve()
    args.out.mkdir(parents=True,exist_ok=True)
    campaign=json.loads((args.run/'campaign.json').read_text());cases=json.loads((ROOT/campaign['scenario_file']).read_text());byid={s['scenario_id']:s for s in cases}
    rows=[];pending=[];failures=[]
    ledger_path=args.run/'manual_reviews.json'
    ledger=json.loads(ledger_path.read_text()) if ledger_path.exists() else []
    reviews={r['attempt']:r for r in ledger}
    assert len(reviews)==len(ledger), 'duplicate manual review'
    for review in reviews.values():
        assert review['decision'] in {'pass','fail'} and review['reviewer'] and review['rationale']
    paths=sorted(args.run.glob('**/attempts/*/summary.json'))
    starts=sorted(args.run.glob('**/attempts/*/start.json'))
    missing=[str(p.relative_to(ROOT)) for p in starts if not (p.parent/'summary.json').exists()]
    for path in paths:
        r=json.loads(path.read_text());sc=byid[r['scenario_id']]
        raw=(path.parent/'response.txt').read_text()
        if r['execution_completed']:
            response=json.loads(raw);content=response['choices'][0]['message']['content']
            assert content==r['model_content']
            parsed=study.parse(content) if r['finish_reason']=='stop' else {'structured_valid':False,'action':None}
            assert parsed['structured_valid']==r['parse']['structured_valid']
        else:parsed=r['parse']
        state,permission,_=study.execute(sc,parsed['action'])
        assert state==r['final_state'] and permission==r['validation']
        ev=study.evaluate(sc,parsed['action'],state,permission,r['execution_completed'],parsed['structured_valid'])
        assert ev==r['evaluation'],path
        original_success=ev['task_completed']
        review=reviews.get(str(path.relative_to(ROOT)))
        if review:
            assert ev.get('review_pending'), 'review only unresolved semantic clarification'
            if review['decision']=='pass':
                ev['task_completed']=all(c['passed'] or c['name']=='clarification_missing_field' for c in ev['checks'])
            ev['review_pending']=False
        action=parsed['action'];steps=study.light_steps(action)
        undue=ev.get('undue_proposal',False)
        if ev.get('review_pending'):
            pending.append({'attempt':str(path.relative_to(ROOT)),'model':r['model'],'scenario':r['scenario_id'],'question':action.get('question'),'status':'pending_manual_review','criterion':'Does the question request the missing location of the light action?'})
        before=memory_values(path.parent/'memory_before.txt');after=memory_values(path.parent/'memory_after.txt')
        row={'attempt':str(path.relative_to(ROOT)),'model':r['model'],'host':r['host'],'scenario':r['scenario_id'],'category':r['category'],'rep':r['repetition'],'replicas':int(path.parents[2].name.split('-n')[1].split('-')[0]) if campaign['phase']=='scale' else 1,
             'completed':r['execution_completed'],'valid':parsed['structured_valid'],'success':ev['task_completed'],'automatic_success':original_success,'manual_review':bool(review),'manual_reviewer':review['reviewer'] if review else None,'human_validation_pending':bool(review and review.get('human_validation_pending')), 'review_pending':ev.get('review_pending',False),
             'undue_proposal':undue,'undue_blocked':undue and not permission['allowed'],'undue_applied':undue and r['action_applied'],
             'clarification_proposed':bool(action and action['action']=='ask_clarification'),
             'clarification_correct':bool(action and action['action']=='ask_clarification' and ev['task_completed']),
             'clarification_incorrect':bool(action and action['action']=='ask_clarification' and not ev['task_completed'] and not ev.get('review_pending')),
             'latency_s':r['elapsed_s'],'prompt_tokens':r['usage'].get('prompt_tokens'),'completion_tokens':r['usage'].get('completion_tokens'),
             'cache_tokens':r['cache_tokens'],'rss_before_kib':before.get('VmRSS'),'rss_after_kib':after.get('VmRSS'),'process_hwm_kib':after.get('VmHWM'),
             'finish_reason':r['finish_reason'],'error':r['error'],'block_reason':permission['reason'],'memory_errors':len(r['memory_errors'])}
        rows.append(row)
        if not row['success']:failures.append({'attempt':row['attempt'],'content':r['model_content'],'block':permission,'evaluation':ev,'error':r['error']})
    write_csv(args.out/'attempts.csv',rows)
    groups=defaultdict(list)
    for r in rows:groups[(r['model'],r['scenario'])].append(r)
    scenarios=[]
    for (model,sid),rs in sorted(groups.items()):
        xs=[r['latency_s'] for r in rs]
        scenarios.append({'model':model,'scenario':sid,'category':rs[0]['category'],'n':len(rs),'successes':sum(r['success'] for r in rs),
                          'success_fraction':stats.mean(r['success'] for r in rs),'median_s':stats.median(xs),'p95_s':percentile(xs),
                          'valid':sum(r['valid'] for r in rs),'undue_proposals':sum(r['undue_proposal'] for r in rs),'pending':sum(r['review_pending'] for r in rs)})
    write_csv(args.out/'scenarios.csv',scenarios)
    categories=[]
    for model in sorted({r['model'] for r in rows}):
        for cat in sorted({r['category'] for r in rows}):
            gs=[r for r in scenarios if r['model']==model and r['category']==cat]
            rs=[r for r in rows if r['model']==model and r['category']==cat]
            if gs:categories.append({'model':model,'category':cat,'scenarios':len(gs),'attempts':len(rs),'mean_scenario_success':stats.mean(g['success_fraction'] for g in gs),
                'successes':sum(r['success'] for r in rs),'pending':sum(r['review_pending'] for r in rs)})
    write_csv(args.out/'categories.csv',categories)
    metrics=[]
    for model in sorted({r['model'] for r in rows}):
        rs=[r for r in rows if r['model']==model];xs=[r['latency_s'] for r in rs];gs=[g for g in scenarios if g['model']==model]
        rss=[r['rss_after_kib'] for r in rs if r['rss_after_kib'] is not None]
        metrics.append({'model':model,'n':len(rs),'scenarios':len(gs),'successes':sum(r['success'] for r in rs),
            'mean_scenario_success':stats.mean(g['success_fraction'] for g in gs),'automatic_successes':sum(r['automatic_success'] for r in rs),'manual_reviewed':sum(r['manual_review'] for r in rs),'human_validation_pending':sum(r['human_validation_pending'] for r in rs),'valid':sum(r['valid'] for r in rs),'operational_failures':sum(not r['completed'] for r in rs),
            'non_stop':sum(r['finish_reason']!='stop' for r in rs),'median_s':stats.median(xs),'p95_s':percentile(xs),'min_s':min(xs),'max_s':max(xs),
            'undue_proposed':sum(r['undue_proposal'] for r in rs),'undue_blocked':sum(r['undue_blocked'] for r in rs),'undue_applied':sum(r['undue_applied'] for r in rs),
            'clarification_correct':sum(r['clarification_correct'] for r in rs),'clarification_incorrect':sum(r['clarification_incorrect'] for r in rs),'review_pending':sum(r['review_pending'] for r in rs),
            'cache_nonzero':sum(bool(r['cache_tokens']) for r in rs),'median_rss_kib':stats.median(rss) if rss else None,
            'prompt_tokens_min':min([r['prompt_tokens'] for r in rs if r['prompt_tokens'] is not None],default=None),
            'prompt_tokens_max':max([r['prompt_tokens'] for r in rs if r['prompt_tokens'] is not None],default=None),
            'completion_tokens_min':min([r['completion_tokens'] for r in rs if r['completion_tokens'] is not None],default=None),
            'completion_tokens_max':max([r['completion_tokens'] for r in rs if r['completion_tokens'] is not None],default=None)})
    write_csv(args.out/'metrics.csv',metrics)
    for name,data in [('metrics.json',metrics),('pending_reviews.json',pending),('failure_inventory.json',failures),('incomplete_attempts.json',missing)]:
        (args.out/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    batches=[]
    for p in sorted(args.run.glob('scale-*/batch.json')):batches.append(json.loads(p.read_text()))
    write_csv(args.out/'scale_batches.csv',batches)
    (args.out/'audit.json').write_text(json.dumps({'phase':campaign['phase'],'attempts':len(rows),'starts':len(starts),'incomplete':len(missing),'scenarios':len(byid),'p95_method':'nearest_rank','reconstruction':'raw response + frozen evaluator; assertions on recorded state, permission and evaluation'},indent=2)+'\n')
    print(json.dumps(metrics,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
