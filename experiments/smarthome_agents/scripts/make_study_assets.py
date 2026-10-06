#!/usr/bin/env python3
"""Generate manuscript tables and standalone pgfplots from reconstructed data."""
import argparse
import csv
import json
import statistics
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
LABEL={'05':'Qwen 0.5B','15':'Qwen 1.5B','rules':'Rules'}
def records(path):
    with path.open() as f:return list(csv.DictReader(f))
def line(parts):return ' & '.join(str(x) for x in parts)+chr(92)*2+'\n'
def main():
    a=argparse.ArgumentParser();a.add_argument('--quality',type=Path,required=True);a.add_argument('--scale',type=Path,required=True);a.add_argument('--out',type=Path,required=True);args=a.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    actions={r['model']:r for r in json.loads((args.quality/'action_summary.json').read_text())}
    metrics=sorted(json.loads((args.quality/'metrics.json').read_text()),key=lambda r:['rules','05','15'].index(r['model']));categories=records(args.quality/'categories.csv');batches=records(args.scale/'scale_batches.csv');scale_attempts=records(args.scale/'attempts.csv')
    assert {r['model'] for r in metrics}==set(LABEL)
    assert all(r['n']==80 and r['scenarios']==40 for r in metrics), 'quality campaign must be complete'
    assert len(batches)==18 and len(scale_attempts)==108, 'scale campaign must be complete'
    root=Path(__file__).resolve().parents[3]
    freeze_name='experiments/smarthome_agents/study_v1/freeze.json'
    commit=subprocess.check_output(['git','log','-1','--format=%h','--',freeze_name],cwd=root,text=True).strip()
    data_commit=subprocess.check_output(['git','log','-1','--format=%h','--','experiments/smarthome_agents/runs/20261006-study-v1-scale'],cwd=root,text=True).strip()
    date=datetime.now(ZoneInfo('America/Sao_Paulo')).strftime('%Y-%m-%d')
    (args.out/'provenance.tex').write_text('\\newcommand{\\StudyCommit}{'+commit+'}\n'+'\\newcommand{\\StudyDataCommit}{'+data_commit+'}\n'+'\\newcommand{\\StudyDate}{'+date+'}\n')
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
    (args.out/'quality_rows.tex').write_text(''.join(line([LABEL[r['model']],f"{r['successes']}/{r['n']}",f"{r['median_s']:.3f}",f"{r['p95_s']:.3f}",actions[r['model']]['undue_commands'],actions[r['model']]['undue_commands_blocked']]) for r in metrics)+'\\bottomrule\n')
    cats=sorted({r['category'] for r in categories})
    (args.out/'category_rows.tex').write_text(''.join(line([cat,*[next(r['successes'] for r in categories if r['model']==m and r['category']==cat)+'/16' for m in ['rules','05','15']]]) for cat in cats)+'\\bottomrule\n')
    summary=[]
    for model in ['rules','05','15']:
        for n in [1,3,6]:
            rs=[r for r in batches if r['model']==model and int(r['replicas'])==n]
            assert len(rs)==2
            rates=[]
            batch_successes=[]
            for batch in rs:
                attempts=[r for r in scale_attempts if r['model']==model and int(r['replicas'])==n and int(r['rep'])==int(batch['repetition'])]
                assert len(attempts)==6
                successes=sum(r['success']=='True' for r in attempts)
                batch_successes.append(successes)
                rates.append(successes*60/float(batch['window_s']))
            latencies=sorted(float(r['latency_s']) for r in scale_attempts if r['model']==model and int(r['replicas'])==n)
            assert len(latencies)==12
            summary.append({'model':model,'replicas':n,'batches':2,'tasks_per_min_mean':statistics.mean(rates),'min':min(rates),'max':max(rates),
                            'successes':sum(batch_successes),'requests':12,'individual_median_s':statistics.median(latencies),'individual_p95_s':latencies[-1]})
    (args.out/'scale_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (args.out/'scale_rows.tex').write_text(''.join(line([LABEL[r['model']],r['replicas'],f"{r['successes']}/12",f"{r['tasks_per_min_mean']:.3f}",f"{r['individual_median_s']:.3f}",f"{r['individual_p95_s']:.3f}"]) for r in summary)+'\\bottomrule\n')
    quality_points=' '.join(f"({i},{100*r['mean_scenario_success']:.3f})" for i,r in enumerate(sorted(metrics,key=lambda r:['rules','05','15'].index(r['model'])),1))
    plots=r'''\documentclass{standalone}
\usepackage[T1]{fontenc}
\usepackage{mathptmx}
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
    (args.out/'quality_figure_pt.tex').write_text(plots.replace('Scenario success','Sucesso por cenário').replace('Rules','Regras'))
    lines=[]
    for model in ['05','15']:
        coords=' '.join(f"({r['replicas']},{r['tasks_per_min_mean']:.4f})" for r in summary if r['model']==model)
        lines.append('\\addplot+[mark=*] coordinates {'+coords+'};\\addlegendentry{'+LABEL[model]+'}')
    scaleplot=r'''\documentclass{standalone}
\usepackage[T1]{fontenc}
\usepackage{mathptmx}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\begin{document}\begin{tikzpicture}
\begin{axis}[width=9cm,height=6cm,xlabel={Independent replicas},ylabel={Correct tasks/min},xtick={1,3,6},ymin=0,grid=major,legend pos=north west]
LINES
\end{axis}\end{tikzpicture}\end{document}
'''.replace('LINES','\n'.join(lines))
    (args.out/'scale_figure.tex').write_text(scaleplot)
    (args.out/'scale_figure_pt.tex').write_text(scaleplot.replace('Independent replicas','Réplicas independentes').replace('Correct tasks/min','Tarefas corretas/min'))
    quality_rows=(args.out/'quality_rows.tex').read_text()
    (args.out/'quality_rows_pt.tex').write_text(quality_rows.replace('Rules','Regras'))
    (args.out/'scale_rows_pt.tex').write_text((args.out/'scale_rows.tex').read_text().replace('Rules','Regras'))
    translations={'ambiguity':'Ambiguidade','clear':'Claros','invalid':'Inválidos','paraphrase':'Paráfrases','routine':'Rotinas'}
    (args.out/'category_rows_pt.tex').write_text(''.join(line([translations[cat],*[next(r['successes'] for r in categories if r['model']==m and r['category']==cat)+'/16' for m in ['rules','05','15']]]) for cat in cats)+'\\bottomrule\n')
    en=[];pt=[]
    for r in metrics:
        label=LABEL[r['model']];ptlabel=label.replace('Rules','Regras')
        en.append(f"{label} completed {r['successes']}/{r['n']} attempts across {r['scenarios']} scenarios; {r['automatic_successes']} passed automatically. The request-latency sample has $n={r['latency_n']}$. Valid structured replies: {r['valid']}; transport/readiness failures: {r['operational_failures']}; non-stop completions: {r['non_stop']}. Lighting replies outside the complete expected-step contract: {r['undue_proposed']} (this reply-level count can include omissions). Undue light commands: {actions[r['model']]['undue_commands']}, including {actions[r['model']]['undue_commands_blocked']} blocked and {actions[r['model']]['undue_commands_applied']} applied only in the simulator. Correct clarifications: {r['clarification_correct']}; incorrect: {r['clarification_incorrect']}; unresolved: {r['review_pending']}.\n\n")
        pt.append(f"{ptlabel} concluiu {r['successes']}/{r['n']} tentativas em {r['scenarios']} cenários; {r['automatic_successes']} passaram automaticamente. A amostra de latência tem $n={r['latency_n']}$. Respostas estruturadas válidas: {r['valid']}; falhas de transporte/prontidão: {r['operational_failures']}; terminações diferentes de stop: {r['non_stop']}. Respostas de iluminação fora do contrato completo de passos: {r['undue_proposed']} (essa contagem por resposta pode incluir omissões). Comandos de luz indevidos: {actions[r['model']]['undue_commands']}, dos quais {actions[r['model']]['undue_commands_blocked']} foram bloqueados e {actions[r['model']]['undue_commands_applied']} aplicados somente no simulador. Esclarecimentos corretos: {r['clarification_correct']}; incorretos: {r['clarification_incorrect']}; não resolvidos: {r['review_pending']}.\n\n")
        if r['model']!='rules':
            en.append(f"Input tokens ranged from {r['prompt_tokens_min']} to {r['prompt_tokens_max']}; output tokens from {r['completion_tokens_min']} to {r['completion_tokens_max']}. Median post-request RSS was {r['median_rss_kib']/1024:.1f} MiB. Nonzero cache counts occurred in {r['cache_nonzero']} attempts.\n\n")
            pt.append(f"As entradas usaram {r['prompt_tokens_min']}--{r['prompt_tokens_max']} tokens; as saídas, {r['completion_tokens_min']}--{r['completion_tokens_max']}. A mediana de RSS após a requisição foi {r['median_rss_kib']/1024:.1f} MiB. Houve cache não zero em {r['cache_nonzero']} tentativas.\n\n")
        if r['manual_reviewed']:
            en.append(f"{r['manual_reviewed']} questions underwent recorded case-by-case review; {r['human_validation_pending']} assisted reviews await human validation. Automatic and assisted counts are distinguished in the artifact.\n\n")
            pt.append(f"{r['manual_reviewed']} perguntas tiveram revisão caso a caso registrada; {r['human_validation_pending']} revisões assistidas aguardam validação humana. Contagens automáticas e assistidas estão separadas no artefato.\n\n")
    (args.out/'results_en.tex').write_text(''.join(en))
    (args.out/'results_pt.tex').write_text(''.join(pt))
    (args.out/'scale_en.tex').write_text('The batch CSV preserves each window, successful-task rate, and response rate separately. Table~\\ref{tab:scale} pools twelve individual requests per condition/size for latency and averages two batch rates; ranges remain in the machine-readable summary.\n')
    (args.out/'scale_pt.tex').write_text('O CSV de lotes preserva cada janela, taxa de tarefas corretas e taxa de respostas separadamente. A Tabela~\\ref{tab:scale} agrupa doze requisições por condição/tamanho para latência e calcula a média de duas taxas de lote; os intervalos permanecem no resumo legível por máquina.\n')
    (args.out/'discussion_en.tex').write_text('Task completion and schema validity are separate outcomes. A blocked incorrect proposal remains an incorrect model decision, and higher response volume cannot repair that decision. Replication changes service concurrency, while the model and simulator contract remain fixed.\n\n')
    (args.out/'discussion_pt.tex').write_text('Conclusão de tarefa e validade estrutural são resultados distintos. Uma proposta incorreta bloqueada continua sendo erro de decisão do modelo; aumentar o volume de respostas não corrige essa decisão. A replicação muda a concorrência de atendimento, mantendo modelo e contrato do simulador.\n\n')
    small=[r for r in summary if r['model']=='05'];large=[r for r in summary if r['model']=='15']
    en_scale=f"For 0.5B, mean correct-task response rates were {small[0]['tasks_per_min_mean']:.3f}, {small[1]['tasks_per_min_mean']:.3f}, and {small[2]['tasks_per_min_mean']:.3f}/min with one, three, and six replicas; 1.5B rates were {large[0]['tasks_per_min_mean']:.3f}, {large[1]['tasks_per_min_mean']:.3f}, and {large[2]['tasks_per_min_mean']:.3f}/min. Each six-request batch retained three correct tasks for 0.5B, one for 1.5B, and five for rules. The rule rate at six replicas reflects a response window of about 9--11 ms and removal of between-wave instrumentation gaps, so it must not be interpreted as measured sustained service capacity.\n"
    pt_scale=f"No 0.5B, as médias de respostas corretas às tarefas foram {small[0]['tasks_per_min_mean']:.3f}, {small[1]['tasks_per_min_mean']:.3f} e {small[2]['tasks_per_min_mean']:.3f}/min com uma, três e seis réplicas; no 1.5B, {large[0]['tasks_per_min_mean']:.3f}, {large[1]['tasks_per_min_mean']:.3f} e {large[2]['tasks_per_min_mean']:.3f}/min. Cada lote de seis pedidos manteve três tarefas corretas no 0.5B, uma no 1.5B e cinco nas regras. A taxa das regras em seis réplicas reflete janela de respostas de cerca de 9--11 ms e ausência dos intervalos de instrumentação entre ondas; não deve ser interpretada como capacidade sustentada medida.\n"
    for language,extra in [('en',en_scale),('pt',pt_scale)]:
        path=args.out/('scale_'+language+'.tex');path.write_text(path.read_text()+'\n'+extra)
    for path in args.out.glob('*.tex'):
        path.write_text(path.read_text().rstrip()+'\n')
    print('Assets generated from raw-data analysis; plot values are means, batch ranges are tabulated.')
if __name__=='__main__':main()
