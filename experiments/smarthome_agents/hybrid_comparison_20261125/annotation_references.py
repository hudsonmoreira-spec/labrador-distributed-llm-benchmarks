#!/usr/bin/env python3
"""Cross-reference existing explicit author judgments; never regrade new results."""
import json,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assessment_path=HERE.parent/'revision_20261123/author_review_20261124/assessment.json'
assessment=load(assessment_path)
references=[]
for review in assessment['reviews']:
 source=review['source'];summary=ROOT/source['source'];request=summary.parent/'request.json'
 assert sha(summary)==source['source_sha256'] and sha(request)==source['request_sha256']
 references.append({'review':review,'request':load(request),'content':source['response']})
rows=[]
for p in sorted((HERE/'comparison/attempts').glob('*/result.json')):
 r=load(p)
 if not r.get('evaluation',{}).get('review_pending'):continue
 response=load(p.parent/'response.json')
 matched=[x for x in references if x['request']==response['model_request'] and x['content']==response['content']]
 rows.append({'attempt':r['id'],'condition':r['condition'],'content':r['content'],'exact_prior_request_and_response_matches':[{'record_id':x['review']['record_id'],'decision':x['review']['decision'],'rationale':x['review']['rationale'],'source':x['review']['source']['source']} for x in matched]})
report={'method':'Post-run exact object match of original model request and exact response text to existing author-reviewed evidence. Cross-reference only; frozen evaluation results are unmodified. Not new or independent human review. No success credit added.','assessment_source':str(assessment_path.relative_to(ROOT)),'assessment_sha256':sha(assessment_path),'automatic_pending_flags':len(rows),'matching_existing_author_failures':sum(bool(r['exact_prior_request_and_response_matches']) and all(x['decision']=='fail' for x in r['exact_prior_request_and_response_matches']) for r in rows),'without_exact_prior_match':sum(not r['exact_prior_request_and_response_matches'] for r in rows),'rows':rows}
(HERE/'comparison/annotation_references.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='rows'},ensure_ascii=False))
