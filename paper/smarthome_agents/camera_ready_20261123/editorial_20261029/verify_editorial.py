#!/usr/bin/env python3
"""Check editorial mappings against original evidence; no inference or regrading."""
from pathlib import Path
import csv,json,re,subprocess,hashlib
E=Path(__file__).resolve().parent
P=E.parent
R=E.parents[3]
BASE='f2f566b179fcf3893099d7d1b12b888455e531ae'
def require(value,message):
 if not value:raise ValueError(message)
def load(p):return json.loads(p.read_text())
original=load(R/'experiments/smarthome_agents/analysis/failure-review-20261028/examples.json')
mapped=load(E/'example_mapping.json')
en=(P/'main_en.tex').read_text();pt=(P/'main_pt.tex').read_text()
en_table=(E/'examples_en.tex').read_text();pt_table=(E/'examples_pt.tex').read_text()
for i,(old,new) in enumerate(zip(original,mapped),1):
 require(all(new[k]==v for k,v in old.items()),'Original example field changed')
 raw=load(R/new['attempt']);response=load(R/new['response'])
 require(new['content']==raw['model_content']==response['choices'][0]['message']['content'],'Raw response mismatch')
 require(new['case']==i,'Case mapping order mismatch')
 for text in [en_table,pt_table]:
  require(r'\label{'+new['latex_label']+'}' in text,'Missing case label')
  require(new['attempt_id'] not in text,'Long ID returned to article')
 require('``'+new['request_en']+"''" in en_table,'English request mismatch')
 require('``'+new['request']+"''" in pt_table,'Portuguese original request mismatch')
 if new['response_text_en']:require(new['response_text_en'] in en_table,'Response translation absent')
 require(r'\ref{'+new['latex_label']+'}' in en and r'\ref{'+new['latex_label']+'}' in pt,'Case not referenced')
 require(new['request'] not in en+en_table,'Untranslated Portuguese request in English article')
require(len(mapped)==len(original)==4,'Example coverage mismatch')
for text in [en,pt]:
 pins=re.findall(r'/tree/([0-9a-f]{40})/paper/smarthome_agents/study_v1/editorial_20261029',text)
 require(len(pins)==1,'Missing immutable editorial supplement link')
 pinned=subprocess.check_output(['git','show',pins[0]+':'+str((E/'example_mapping.json').relative_to(R))],cwd=R)
 require(pinned==(E/'example_mapping.json').read_bytes(),'Pinned translation mapping differs')

rows=list(csv.DictReader((R/'experiments/smarthome_agents/analysis/failure-review-20261028/criteria_by_condition.csv').open()))
keys=['expected_steps','final_state','preservation','no_action','executor_permission','prohibited_steps','clarification']
for lang in ['en','pt']:
 table=(E/f'failure_rows_{lang}.tex').read_text().splitlines()
 for key,line in zip(keys,table):
  for model,cell in zip(['rules','05','15'],line.split(' & ')[1:]):
   row=next(r for r in rows if r['model']==model and r['criterion']==key)
   expected=f"{row['failed']}/{row['observed']}" if int(row['observed']) else '--/0'
   require(cell.startswith(expected),'Displayed denominator/count mismatch')
 require(len(table)==8,'Failure table row count mismatch')
 text=(P/f'main_{lang}.tex').read_text()
 historic=subprocess.check_output(['git','show',BASE+':'+str((P/f'main_{lang}.tex').relative_to(R))],cwd=R,text=True)
 author=lambda s:s[s.index(r'\author{'):s.index(r'\begin{document}')].replace('\\newcounter{examplecase}\n','')
 approved=load(P/'submission/author-order-20261029.json')['ordered_authors']
 block=author(text); oldblock=author(historic)
 require(all(block.split(r'\IEEEauthorblockA')[0].count(n)==1 for n in approved),'Author membership changed')
 require([block.index(n) for n in approved]==sorted(block.index(n) for n in approved),'Author order differs from user confirmation')
 require(all(oldblock.split(r'\IEEEauthorblockA')[0].count(n)==1 for n in approved),'Original author membership changed')
 without_names=lambda b:re.sub(r'\\IEEEauthorblockN\{.*?\}\s*\\IEEEauthorblockA',lambda m:'<names>IEEEauthorblockA',b,flags=re.S)
 require(without_names(block)==without_names(oldblock),'Affiliation or corresponding contact changed')
 require(text.startswith(r'\documentclass[letterpaper,conference]{IEEEtran}'),'Document format changed')
 for path in re.findall(r'\\input\{\\StudyPrefix ([^}]+)\}',text):
  require((P/path).is_file(),'Missing input '+path)
 for caption in re.findall(r'\\caption\{([^}]+)\}',text+(E/f'examples_{lang}.tex').read_text()):
  require(len(caption)<90,'Long caption returned')
 require(not re.search(r'\\(?:vspace|hspace)\{\s*-|\\(?:geometry|fontsize|tiny)',text),'Font/margin/negative spacing override')
 # Historical numerical assets used by the paper must remain byte-identical.
 for folder in ['generated','failure_analysis']:
  for f in (P/folder).iterdir():
   if f.is_file():
    name=str(f.relative_to(R))
    old=subprocess.run(['git','show',BASE+':'+name],cwd=R,capture_output=True)
    if old.returncode==0:require(old.stdout==f.read_bytes(),'Historical asset changed: '+name)
 require(BASE in text,'Complementary analysis link not pinned to preceding commit')
require(re.findall(r'\\cite\{([^}]+)\}',en)==re.findall(r'\\cite\{([^}]+)\}',pt),'Citation sequence differs')
normalize=lambda s:re.findall(r'\\input\{([^}]+)\}',re.sub(r'_(en|pt)(?=[.}])','',s))
require(normalize(en)==normalize(pt),'Bilingual inputs differ')
for lang in ['en','pt']:
 f=(E/f'failure_rows_{lang}.tex').read_text()
 if lang=='en':numbers=re.findall(r'\d+(?:\.\d+)?',f)
 else:require(numbers==re.findall(r'\d+(?:\.\d+)?',f),'Bilingual failure counts differ')
ledger=load(R/'experiments/smarthome_agents/runs/20261006-study-v1-quality/manual_reviews.json')
require(len(ledger)==4 and all(x['decision']=='fail' and x['human_validation_pending'] for x in ledger),'Judgment status changed')
result={'status':'pass','based_on_commit':BASE,'cases_mapped_to_original_and_raw_http':4,'failure_table_cells_checked':42,'author_block_and_IEEE_format':'order updated per user confirmation; membership, affiliation, contact and IEEE format preserved','historical_generated_assets':'byte-identical to preceding commit','assisted_judgments_pending':4,'credited_successes_changed':0,'citations_and_inputs_bilingual':'matched','translation_review':'editorial comparison with Portuguese originals; human linguistic review remains pending','scope':'Presentation consistency; run both original scientific verifiers separately.'}
print(json.dumps(result,indent=2,ensure_ascii=False))
