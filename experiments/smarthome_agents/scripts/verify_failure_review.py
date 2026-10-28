#!/usr/bin/env python3
"""Verify the complementary editorial report offline, without touching source evidence."""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'experiments/smarthome_agents'
OUT=BASE/'analysis/failure-review-20261028'
PAPER=ROOT/'paper/smarthome_agents/study_v1'


def load(p):
    return json.loads(p.read_text())


def rows(p):
    with p.open() as f:return list(csv.DictReader(f))


def require(test,message):
    if not test:raise ValueError(message)


def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--output',type=Path);args=a.parse_args()
    manifest=load(OUT/'input_manifest.json')
    require(manifest['scientific_snapshot']=='a834b8255f736fb59425b146be183c17866a2c7d','Snapshot changed')
    # Every scientific input must also match the original public-evidence manifest.
    scientific=load(PAPER/'artifact/evidence-manifest.json')['sha256']
    for name,sha in manifest['sha256'].items():
        require(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha, 'Input changed: '+name)
        require(scientific.get(name)==sha, 'Complementary input is not in original snapshot: '+name)
    compared=[]
    with tempfile.TemporaryDirectory(prefix='smarthome-failures-') as d:
        tmp=Path(d)
        subprocess.run([sys.executable,str(BASE/'scripts/analyze_failure_criteria.py'),'--out',str(tmp/'analysis'),'--tex-out',str(tmp/'tex')],check=True,capture_output=True,text=True)
        for source,dest in [(OUT,tmp/'analysis'),(PAPER/'failure_analysis',tmp/'tex')]:
            require({p.name for p in source.iterdir() if p.is_file()}=={p.name for p in dest.iterdir() if p.is_file()},'Generated file set differs')
            for p in source.iterdir():
                if p.is_file():
                    require(p.read_bytes()==(dest/p.name).read_bytes(),'Nondeterministic output: '+str(p))
                    compared.append(str(p.relative_to(ROOT)))
    attempts=load(OUT/'attempts.json'); detail=rows(OUT/'criteria_by_attempt.csv')
    summary=load(OUT/'summary.json'); grouped=summary['criteria']
    require(len(attempts)==240 and len(detail)==2400,'Attempt/group coverage differs')
    require(set(Counter((r['attempt'],r['criterion']) for r in detail).values())=={1},'Duplicate attempt/group')
    missing_total=0; overlapping=0
    for r in attempts:
        checks=load(ROOT/r['attempt'])['evaluation']['checks']
        require(r['checks']==checks,'Copied checks differ')
        # Independently inspect statuses against individual raw checks.
        for group,selectors in summary['mapping'].items():
            matches=[c for c in checks if any(c['name'].startswith(s) if s.endswith(':') else c['name']==s for s in selectors)]
            expected='absent' if not matches else 'failed' if not all(c['passed'] for c in matches) else 'passed'
            require(r['groups'][group]['status']==expected,'Group status differs from raw checks')
            missing_total+=not matches
        failures=sum(g['status']=='failed' for g in r['groups'].values())
        overlapping+=failures>1
        require((failures==0)==r['success'],'Union differs from original success')
    for g in grouped:
        require(g['passed']+g['failed']==g['observed'] and g['observed']+g['absent_or_not_applicable']==80,'Denominator mismatch')
        require(g['provisional_failed']<=g['failed'],'Provisional count mismatch')
    require(missing_total>0 and overlapping>0,'Absent/overlapping cases not exercised')
    for m in ['rules','05','15']:
        for key,n in [('expected_action',32),('expected_steps',48),('final_state',48),('preservation',64),('executor_permission',80),('prohibited_steps',80)]:
            require(next(g for g in grouped if g['model']==m and g['criterion']==key)['observed']==n,'Table applicability differs')
        subset=[r for r in attempts if r['model']==m]
        atomic=sum(sum(c['name'].startswith('unchanged:') and not c['passed'] for c in r['checks']) for r in subset)
        unique=sum(any(c['name'].startswith('unchanged:') and not c['passed'] for c in r['checks']) for r in subset)
        require(next(g['failed'] for g in grouped if g['model']==m and g['criterion']=='preservation')==unique<=atomic,'Path failures double-counted')
        require(all(r['category'] in ['ambiguity','invalid'] for r in subset if r['groups']['prohibited_steps']['status']=='failed'),'Prohibition applicability differs')
    totals=summary['totals']
    require([(t['model'],t['successes'],t['unsuccessful']) for t in totals]==[('rules',42,38),('05',30,50),('15',12,68)],'Original outcomes changed')
    ledger=load(BASE/'runs/20261006-study-v1-quality/manual_reviews.json')
    require(len(ledger)==4 and all(r['decision']=='fail' and r['human_validation_pending'] for r in ledger),'Assisted status changed')
    require(sum(bool(r['review']) for r in attempts)==4,'Review count changed')
    for e in load(OUT/'examples.json'):
        raw=load(ROOT/e['attempt'])
        sc=next(s for s in load(BASE/'study_v1/reserved.json') if s['scenario_id']==e['scenario'])
        require(e['content']==raw['model_content']==load(ROOT/e['response'])['choices'][0]['message']['content'],'Example output differs')
        require(e['request']==sc['resident_request'] and e['initial_state']==sc['initial_state'] and e['expected']==sc['evaluator'],'Example scenario differs')
        require(e['executor']==raw['validation'] and e['final_state']==raw['final_state'] and e['action_applied']==raw['action_applied'],'Example execution differs')
        require(e['failed_checks']==[c['name'] for c in raw['evaluation']['checks'] if not c['passed']],'Example checks differ')
        for lang in ['en','pt']:
            text=(PAPER/f'failure_analysis/examples_{lang}.tex').read_text()
            require(e['attempt_id'] in text and '``'+e['request']+"''" in text,'Example source/quote missing from manuscript')
    # Bilingual generated text must retain identical numbers, IDs, and original-language quotes.
    for stem in ['category_rows','failure_rows','patterns','clarification','examples']:
        en=(PAPER/f'failure_analysis/{stem}_en.tex').read_text()
        pt=(PAPER/f'failure_analysis/{stem}_pt.tex').read_text()
        require(re.findall(r'\d+(?:\.\d+)?',en)==re.findall(r'\d+(?:\.\d+)?',pt),'PT/EN numerical mismatch: '+stem)
        require(re.findall(r"``(.*?)''",en)==re.findall(r"``(.*?)''",pt),'PT/EN quote mismatch: '+stem)
    en=(PAPER/'main_en.tex').read_text();pt=(PAPER/'main_pt.tex').read_text()
    require(re.findall(r'\\cite\{([^}]+)\}',en)==re.findall(r'\\cite\{([^}]+)\}',pt),'PT/EN citation mismatch')
    normalize=lambda s:re.findall(r'\\input\{([^}]+)\}',re.sub(r'_(en|pt)(?=[.}])','',s))
    require(normalize(en)==normalize(pt),'PT/EN table/content inputs differ')
    require('empirical' in en and 'empirical' in pt and '10.1145/3736721' in (PAPER/'references.bib').read_text(),'New reference missing')
    result={'status':'pass','scientific_input_hashes':len(manifest['sha256']),'deterministic_files':len(compared),'quality_attempts':240,'criterion_attempt_rows':len(detail),'original_totals':totals,'attempts_with_multiple_failed_groups':overlapping,'absent_group_observations':missing_total,'assisted_reviews_pending':4,'newly_awarded_successes':0,'example_count':4,'bilingual_numbers_quotes_citations_inputs':'pass; prose equivalence additionally reviewed editorially','command_units':'generator independently reconstructs every command and compares action_steps.csv and action_summary.json exactly','checked_outputs':compared,'scope':'Offline reconstruction and consistency checks; no inference, regrading or human semantic validation'}
    text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.output:args.output.write_text(text)
    print(text,end='')

if __name__=='__main__':main()
