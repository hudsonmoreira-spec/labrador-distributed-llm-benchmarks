#!/usr/bin/env python3
"""Generate manuscript tables and standalone pgfplots from reconstructed data."""
import argparse
import csv
import json
import statistics
from pathlib import Path
LABEL={'05':'Qwen 0.5B','15':'Qwen 1.5B','rules':'Rules'}
def records(path):
    with path.open() as f:return list(csv.DictReader(f))
def line(parts):return ' & '.join(str(x) for x in parts)+chr(92)*2+'\n'
def main():
    a=argparse.ArgumentParser();a.add_argument('--quality',type=Path,required=True);a.add_argument('--scale',type=Path,required=True);a.add_argument('--out',type=Path,required=True);args=a.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    metrics=json.loads((args.quality/'metrics.json').read_text());categories=records(args.quality/'categories.csv');batches=records(args.scale/'scale_batches.csv');scale_attempts=records(args.scale/'attempts.csv')
    tex=[]
    macro={'05':'Small','15':'Large','rules':'Rules'}
    for row in metrics:
        for key,value in row.items():
            if key=='model' or value is None:continue
            name=macro[row['model']]+''.join(s.title() for s in key.split('_'))
            name=name.replace('95','NinetyFive')
            v=f'{value:.3f}' if isinstance(value,float) else str(value)
            tex.append('\\newcommand{\\'+name+'}{'+v+'}\n')
    (args.out/'metrics.tex').write_text(''.join(tex))
    (args.out/'quality_rows.tex').write_text(''.join(line([LABEL[r['model']],f"{r['successes']}/{r['n']}",f"{r['median_s']:.3f}",f"{r['p95_s']:.3f}",r['undue_proposed'],r['undue_blocked']]) for r in metrics)+'\\bottomrule\n')
    cats=sorted({r['category'] for r in categories})
    (args.out/'category_rows.tex').write_text(''.join(line([cat,*[next(r['successes'] for r in categories if r['model']==m and r['category']==cat)+'/16' for m in ['rules','05','15']]]) for cat in cats)+'\\bottomrule\n')
    summary=[]
    for model in ['rules','05','15']:
        for n in [1,3,6]:
            rs=[r for r in batches if r['model']==model and int(r['replicas'])==n]
            assert len(rs)==2
            rates=[float(r['completed_tasks_per_min']) for r in rs]
            latencies=sorted(float(r['latency_s']) for r in scale_attempts if r['model']==model and int(r['replicas'])==n)
            assert len(latencies)==12
            summary.append({'model':model,'replicas':n,'batches':2,'tasks_per_min_mean':statistics.mean(rates),'min':min(rates),'max':max(rates),
                            'successes':sum(int(r['successes']) for r in rs),'requests':12,'individual_median_s':statistics.median(latencies),'individual_p95_s':latencies[-1]})
    (args.out/'scale_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (args.out/'scale_rows.tex').write_text(''.join(line([LABEL[r['model']],r['replicas'],f"{r['successes']}/12",f"{r['tasks_per_min_mean']:.3f}",f"{r['individual_median_s']:.3f}",f"{r['individual_p95_s']:.3f}"]) for r in summary)+'\\bottomrule\n')
    quality_points=' '.join(f"({i},{100*r['mean_scenario_success']:.3f})" for i,r in enumerate(sorted(metrics,key=lambda r:['rules','05','15'].index(r['model'])),1))
    plots=r'''\documentclass{standalone}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\begin{document}
\begin{tikzpicture}
\begin{axis}[ybar,bar width=16pt,width=9cm,height=6cm,ymin=0,ymax=100,ylabel={Scenario success (\%)},xtick={1,2,3},xticklabels={Rules,Qwen 0.5B,Qwen 1.5B},grid=major,nodes near coords]
\addplot coordinates {POINTS};
\end{axis}\end{tikzpicture}
\end{document}
'''.replace('POINTS',quality_points)
    (args.out/'quality_figure.tex').write_text(plots)
    lines=[]
    for model in ['05','15']:
        coords=' '.join(f"({r['replicas']},{r['tasks_per_min_mean']:.4f})" for r in summary if r['model']==model)
        lines.append('\\addplot+[mark=*] coordinates {'+coords+'};\\addlegendentry{'+LABEL[model]+'}')
    scaleplot=r'''\documentclass{standalone}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\begin{document}\begin{tikzpicture}
\begin{axis}[width=9cm,height=6cm,xlabel={Independent replicas},ylabel={Correct tasks/min},xtick={1,3,6},ymin=0,grid=major,legend pos=north west]
LINES
\end{axis}\end{tikzpicture}\end{document}
'''.replace('LINES','\n'.join(lines))
    (args.out/'scale_figure.tex').write_text(scaleplot)
    print('Assets generated from raw-data analysis; plot values are means, batch ranges are tabulated.')
if __name__=='__main__':main()
