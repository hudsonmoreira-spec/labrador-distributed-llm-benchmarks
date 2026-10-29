from pathlib import Path
import subprocess, json, hashlib, re, xml.etree.ElementTree as ET
from pypdf import PdfReader
P=Path(__file__).resolve().parent.parent
result={'checked_on':'2026-10-29','format':'IEEEtran conference, US Letter; unchanged fonts and margins','pdfs':{},'visual_review':'All five pages per language rendered and inspected; final changed pages rechecked','ICCE':{'official_source':'https://icce.org/2027/submission-guidelines/','initial_max_pages':6,'journal_route_conditional_max_pages':4,'eligibility_or_open_deadline_asserted':False},'new_inferences':0,'submission_to_EDAS':False}
for lang in ['en','pt']:
 pdf=P/f'main_{lang}.pdf'; reader=PdfReader(pdf)
 alltext='\n'.join(p.extract_text() for p in reader.pages)
 assert len(reader.pages)==5
 assert all(float(p.mediabox.width)==612 and float(p.mediabox.height)==792 for p in reader.pages)
 assert '??' not in alltext
 logs=(P/f'main_{lang}.log').read_text()
 assert 'Overfull' not in logs and 'undefined' not in logs.lower()
 assert 'LaTeX Warning' not in logs
 fonts=subprocess.check_output(['pdffonts',str(pdf)],text=True)
 fontlines=fonts.splitlines()[2:]
 assert all('Type 3' not in l and re.search(r'\byes\s+yes\s+',l) for l in fontlines)
 external=[]; internal=0
 for page in reader.pages:
  for ref in page.get('/Annots',[]):
   obj=ref.get_object();a=obj.get('/A',{})
   if a.get('/URI'):external.append(str(a['/URI']))
   target=obj.get('/Dest',a.get('/D'))
   if target is not None:
    if isinstance(target,str):assert target in reader.named_destinations,target
    else:assert len(target)>0
    internal+=1
 assert any('/tree/f2f566b179fcf3893099d7d1b12b888455e531ae/' in u for u in external)
 assert any('/tree/a834b8255f736fb59425b146be183c17866a2c7d' in u for u in external)
 # Poppler supplies word-level geometry independently of PDF text extraction.
 xml=subprocess.check_output(['pdftotext','-bbox',str(pdf),'-'])
 root=ET.fromstring(xml);words=root.findall('.//{*}word')
 assert words
 bounds=[min(float(w.attrib['xMin']) for w in words),min(float(w.attrib['yMin']) for w in words),max(float(w.attrib['xMax']) for w in words),max(float(w.attrib['yMax']) for w in words)]
 assert bounds[0]>=48 and bounds[1]>=40 and bounds[2]<=564 and bounds[3]<=740,bounds
 titles=['Unsupported paraphrase','Missing-room assumption','Uninformative clarification','Unrequested state change'] if lang=='en' else ['Paráfrase não reconhecida','Suposição de cômodo','Esclarecimento não informativo','Mudança não solicitada']
 flat=' '.join(alltext.split())
 for t in titles:assert t in flat,t
 result['pdfs'][lang]={'pages':len(reader.pages),'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'page_size_pt':[612,792],'all_fonts_embedded':True,'type3_fonts':False,'overfull_boxes':False,'undefined_references':False,'external_targets':sorted(set(external)),'resolved_internal_links':internal,'text_bounds_pt':bounds,'named_cases':4,'table_count':5,'figure_count':1,'source_and_mapping_checks':'editorial-check.json'}
(P/'editorial_20261029/pdf-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({l:{'pages':v['pages'],'internal_links':v['resolved_internal_links']} for l,v in result['pdfs'].items()},indent=2))
