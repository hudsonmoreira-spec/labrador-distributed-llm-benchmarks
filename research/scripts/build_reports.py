#!/usr/bin/env python3
import csv, json, re, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
runs=sorted((ROOT/'data/runs').glob('*/hosts'))
if not runs: raise SystemExit('no runs')
run=runs[-1].parent
hosts=[x.strip() for x in (ROOT/'config/hosts.txt').read_text().splitlines() if x.strip()]
def section(raw, name):
    m=re.search(r'^---'+re.escape(name)+r'---\n(.*?)(?=^---|\Z)',raw,re.M|re.S)
    return m.group(1) if m else ''
def first(pat, src):
    m=re.search(pat,src,re.M); return (m.group(1) if m.lastindex else m.group(0)).strip() if m else ''
rows=[]
for i,h in enumerate(hosts,1):
    d=run/'hosts'/h
    raw=(d/'raw.txt').read_text(errors='replace') if (d/'raw.txt').exists() else ''
    err=(d/'error.txt').read_text(errors='replace') if (d/'error.txt').exists() else ''
    access=section(raw,'ACCESS'); ident=section(raw,'IDENTITY'); cpu=section(raw,'CPU'); os=section(raw,'OS'); therm=section(raw,'THERMAL'); tools=section(raw,'TOOLS')
    mem=section(raw,'MEMORY'); load=section(raw,'LOAD'); net=section(raw,'NETWORK'); storage=section(raw,'STORAGE'); link=section(raw,'LINK_STATS'); dt=section(raw,'DEVICE_TREE'); logs=section(raw,'LOG_EVIDENCE')
    rows.append({'node':f'node{i:02d}','ip':h,'ssh_ok':bool(raw),'sudo_n':first(r'^sudo_n=(.*)$',access),'hostname':first(r'^[^\n]+$',ident),'machine_id':first(r'^[0-9a-f]{32}$',ident),'device_tree':dt,'model':first(r'^([^\n]+)$',dt),'arch':first(r'^Architecture:\s*(.*)$',cpu),'cpu_count':first(r'^CPU\(s\):\s*(.*)$',cpu),'cpu_raw':cpu,'os_raw':os,'memory_raw':mem,'storage_raw':storage,'network_raw':net,'link_raw':link,'load_raw':load,'thermal_raw':therm,'tools_raw':tools,'models_raw':re.search(r'find /.*',tools,re.S).group(0) if re.search(r'find /.*',tools,re.S) else '','log_evidence':logs,'kernel':first(r'^Linux .*? \S+ (\S+)',os),'uptime':first(r'^up .*$',os),'raw_file':str((d/'raw.txt').relative_to(ROOT)),'error':err[-4000:]})
(ROOT/'data').mkdir(exist_ok=True)
(ROOT/'data/inventory.json').write_text(json.dumps({'run':str(run.relative_to(ROOT)),'generated_utc':subprocess.check_output(['date','-u','+%FT%TZ'],text=True).strip(),'hosts':rows},ensure_ascii=False,indent=2)+'\n')
with (ROOT/'data/inventory.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
rep=ROOT/'reports'; rep.mkdir(exist_ok=True)
good=[r for r in rows if r['ssh_ok'] and r['sudo_n']=='0']; bad=[r for r in rows if r not in good]
lines=['# Inventory report','',f'Run: `{run.relative_to(ROOT)}`','',f'Accessed: **{sum(r["ssh_ok"] for r in rows)}/{len(rows)}**; passwordless SSH and sudo confirmed: **{len(good)}**.','', 'This report is preliminary and contains no inference benchmarks. Complete fields remain in the raw data.','', 'Hosts without confirmation:','']
lines += [f"- {r['node']} ({r['ip']}): {r['error'][:300].replace(chr(10),' ')}" for r in bad]
lines += ['', 'Limitations: extraction is text-based and should be reviewed before final selection; a missing tool is not evidence of a hardware defect.']
(rep/'inventory_report.md').write_text('\n'.join(lines)+'\n')
