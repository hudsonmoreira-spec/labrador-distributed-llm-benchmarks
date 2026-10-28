#!/usr/bin/env python3
"""Post-hoc reporting of existing checks; never changes frozen evaluation or awards success."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
import statistics
import study_v1 as study

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'experiments/smarthome_agents'
MODELS = ['rules', '05', '15']
# Exact equality unless the selector ends in ':', in which case startswith.
GROUPS = {
    'expected_action': ['expected_action'],
    'expected_steps': ['exact_proposed_steps'],
    'final_state': ['final:'],
    'preservation': ['unchanged:'],
    'clarification': ['clarification_allowed', 'clarification_missing_field'],
    'no_action': ['no_action_policy'],
    'executor_permission': ['action_allowed'],
    'prohibited_steps': ['prohibited:', 'no_prohibited_plan_steps'],
}
DEFINITIONS = {
    'expected_action': 'Only ambiguity/invalid cases: study.evaluate deliberately exempts set_light/set_lights wrappers; step equivalence is assessed separately.',
    'expected_steps': 'Clear/paraphrase/routine: sorted (room,value) steps must equal expected_steps, with no omissions/extras; single-action/one-step-plan wrappers equivalent.',
    'final_state': 'Any final_state_equals path differs; only clear/paraphrase/routine. Does not count unchanged paths.',
    'preservation': 'Any unchanged path differs. Clear/paraphrase preserve unrelated light; ambiguity/invalid preserve both; routine has no unchanged light.',
    'clarification': 'Only when ask_clarification was proposed: allowed in scenario AND question requests expected missing field. Pending semantic checks are not automatic passes; four assisted failure judgments remain provisional.',
    'no_action': 'Only when no_action was proposed: no_action_is_success must be true (invalid requests). Failure means an undue no_action, including ambiguity needing clarification.',
    'executor_permission': 'Returned permission allowed=false. Intervention is not an independent causal explanation or a correction of a wrong proposal.',
    'prohibited_steps': 'Union of legacy top-level prohibited: checks and plan-aware no_prohibited_plan_steps; top-level check alone can miss a set_lights wrapper. No-prohibited check exists even with an empty prohibited set; observed pass is not evidence of a prohibition challenge.',
}
LABELS = {
    'expected_steps': ('Wrong step set (48)', 'Passos diferentes (48)'),
    'final_state': ('Wrong target state (48)', 'Estado-alvo incorreto (48)'),
    'preservation': ('Preservation failed (64)', 'Preservação falhou (64)'),
    'no_action': (r'Undue \texttt{no\_action} ($p$)', r'\texttt{no\_action} indevido ($p$)'),
    'executor_permission': ('Proposal blocked (80)', 'Proposta bloqueada (80)'),
    'prohibited_steps': ('Prohibited step (80)', 'Passo proibido (80)'),
}
EXAMPLES = [('rules','held-paraphrase-01'), ('05','held-ambiguity-01'), ('05','held-ambiguity-03'), ('15','held-clear-01')]


def read(p):
    return json.loads(p.read_text())


def csv_read(p):
    with p.open() as f:
        return list(csv.DictReader(f))


def csv_write(p, rows):
    with p.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader(); w.writerows(rows)


def dump(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def tex(s):
    return ''.join({'\\':r'\textbackslash{}','_':r'\_','%':r'\%','&':r'\&','#':r'\#','{':r'\{','}':r'\}'}.get(c,c) for c in s)


def texrow(xs):
    return ' & '.join(str(x) for x in xs) + r'\\' + '\n'


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--out',type=Path,default=BASE/'analysis/failure-review-20261028')
    a.add_argument('--tex-out',type=Path,default=ROOT/'paper/smarthome_agents/study_v1/failure_analysis')
    args=a.parse_args()
    # Refuse all historical analysis destinations and scientific source trees.
    protected = [BASE/'analysis/quality-v1',BASE/'analysis/scale-v1',BASE/'analysis/development-1',BASE/'analysis/development-2',BASE/'runs',BASE/'study_v1',ROOT/'paper/icce2027',ROOT/'paper/smarthome_agents/preview_20261005',ROOT/'paper/smarthome_agents/study_v1/generated']
    for dest in [args.out.resolve(),args.tex_out.resolve()]:
        assert not any(dest == p or p in dest.parents for p in protected), 'Use a new complementary output directory'
    for p in [args.out,args.tex_out]: p.mkdir(parents=True,exist_ok=True)
    freeze=read(BASE/'study_v1/freeze.json')
    for name, expected in freeze['files'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected, name
    run=BASE/'runs/20261006-study-v1-quality'
    historical=BASE/'analysis/quality-v1'
    cases={s['scenario_id']:s for s in read(BASE/'study_v1/reserved.json')}
    ledger={r['attempt']:r for r in read(run/'manual_reviews.json')}
    old={r['attempt']:r for r in csv_read(historical/'attempts.csv')}
    paths=sorted(run.glob('attempts/*/summary.json'))
    assert len(paths)==len(list(run.glob('attempts/*/start.json')))==240
    records=[]; long=[]; sources=set(); commands=[]
    def source(p):
        sources.add(str(p.relative_to(ROOT)))
    for p in paths:
        source(p); r=read(p); rel=str(p.relative_to(ROOT)); sc=cases[r['scenario_id']]
        raw=p.with_name('response.txt'); source(raw)
        content=read(raw)['choices'][0]['message']['content']
        assert content==r['model_content']
        parsed=study.parse(content)
        assert parsed==r['parse']
        state,permission,decisions=study.execute(sc,parsed['action'])
        assert state==r['final_state'] and permission==r['validation'] and decisions==r['step_permissions']
        ev=study.evaluate(sc,parsed['action'],state,permission,r['execution_completed'],parsed['structured_valid'])
        assert ev==r['evaluation']
        original=old[rel]; success=ev['task_completed']; review=ledger.get(rel)
        assert (original['success']=='True')==success==(original['automatic_success']=='True')
        if review:
            assert review['decision']=='fail' and review['human_validation_pending'] and ev['review_pending']
        assert (original['human_validation_pending']=='True')==bool(review)
        groups={}
        # Operational/format status comes from explicit recorded fields, not missing early-return checks.
        groups['operational']={'status':'passed' if r['execution_completed'] and r['finish_reason']=='stop' else 'failed','checks':['execution_completed','finish_reason'],'pending_assisted':False}
        groups['format']={'status':('passed' if parsed['structured_valid'] else 'failed') if r['execution_completed'] else 'absent','checks':['parse.structured_valid'],'pending_assisted':False}
        for key,selectors in GROUPS.items():
            checks=[c for c in ev['checks'] if any(c['name'].startswith(s) if s.endswith(':') else c['name']==s for s in selectors)]
            status='absent' if not checks else 'failed' if any(not c['passed'] for c in checks) else 'passed'
            groups[key]={'status':status,'checks':[c['name'] for c in checks], 'pending_assisted': bool(review and key=='clarification')}
        assert (any(g['status']=='failed' for g in groups.values())) == (not success)
        action=parsed['action']; steps=study.light_steps(action)
        for index,step in enumerate(steps,1):
            expected=sc['evaluator'].get('expected_steps')
            prohibited=any(all(v=='*' or step.get(k)==v for k,v in rule.items()) for rule in sc['evaluator'].get('prohibited_actions',[]))
            unexpected=expected is not None and (step['room'],step['value']) not in [(s['room'],s['value']) for s in expected]
            undue=prohibited or unexpected
            commands.append({'attempt':rel,'model':r['model'],'host':r['host'],'scenario':r['scenario_id'],'step':index,'room':step['room'],'value':step['value'],'undue':undue,'blocked':not permission['allowed'],'undue_blocked':undue and not permission['allowed'],'applied':r['action_applied'],'undue_applied':undue and r['action_applied']})
        rec={'attempt':rel,'attempt_id':r['attempt_id'],'model':r['model'],'scenario':r['scenario_id'],'category':r['category'],'success':success,'action':action,'groups':groups,'checks':ev['checks'],'review':review,'clarification_proposed':action['action']=='ask_clarification','clarification_correct':action['action']=='ask_clarification' and success}
        records.append(rec)
        for k,g in groups.items():
            long.append({'attempt':rel,'model':r['model'],'scenario':r['scenario_id'],'category':r['category'],'criterion':k,**g})
    assert {r['attempt'] for r in records}==set(old)
    failed_old={r['attempt']:r for r in read(historical/'failure_inventory.json')}
    assert set(failed_old)=={r['attempt'] for r in records if not r['success']}
    for r in records:
        if not r['success']:
            assert failed_old[r['attempt']]['evaluation']['checks']==r['checks']
    old_commands=csv_read(historical/'action_steps.csv')
    assert [{k:str(v) for k,v in r.items()} for r in commands]==old_commands
    summaries=[]; totals=[]; cats=[]
    for model in MODELS:
        rs=[r for r in records if r['model']==model]
        assert len(rs)==80 and len({r['scenario'] for r in rs})==40
        assert set(Counter(r['scenario'] for r in rs).values())=={2}
        m=next(m for m in read(historical/'metrics.json') if m['model']==model)
        assert sum(r['success'] for r in rs)==m['successes']
        totals.append({'model':model,'attempts':len(rs),'scenarios':40,'successes':m['successes'],'unsuccessful':80-m['successes'],'clarifications_proposed':sum(r['clarification_proposed'] for r in rs),'clarifications_correct':sum(r['clarification_correct'] for r in rs),'human_validation_pending':sum(bool(r['review']) for r in rs),'no_action_proposed':sum(r['action']['action']=='no_action' for r in rs)})
        for criterion in rs[0]['groups']:
            counts=Counter(r['groups'][criterion]['status'] for r in rs)
            summaries.append({'model':model,'criterion':criterion,'attempts':80,'observed':counts['passed']+counts['failed'],'passed':counts['passed'],'failed':counts['failed'],'absent_or_not_applicable':counts['absent'],'provisional_failed':sum(r['groups'][criterion]['pending_assisted'] for r in rs),'unit':'attempt; overlapping indicators'})
        for cat in ['clear','paraphrase','routine','ambiguity','invalid']:
            subset=[r for r in rs if r['category']==cat]
            sid=sorted({r['scenario'] for r in subset})
            mean=statistics.mean(statistics.mean(r['success'] for r in subset if r['scenario']==s) for s in sid)
            original=next(r for r in csv_read(historical/'categories.csv') if r['model']==model and r['category']==cat)
            assert len(sid)==8 and len(subset)==16 and mean==float(original['mean_scenario_success']) and sum(r['success'] for r in subset)==int(original['successes'])
            row={'model':model,'category':cat,'scenarios':8,'attempts':16,'successes':sum(r['success'] for r in subset),'mean_scenario_success':mean,'human_validation_pending':sum(bool(r['review']) for r in subset)}
            row.update({k+'_failed':sum(r['groups'][k]['status']=='failed' for r in subset) for k in rs[0]['groups']})
            cats.append(row)
        cs=[r for r in commands if r['model']==model]
        cs_summary={'model':model,'structured_light_commands':len(cs),'undue_commands':sum(r['undue'] for r in cs),'undue_commands_blocked':sum(r['undue_blocked'] for r in cs),'undue_commands_applied':sum(r['undue_applied'] for r in cs)}
        assert cs_summary==next(r for r in read(historical/'action_summary.json') if r['model']==model)
    csv_write(args.out/'criteria_by_attempt.csv',long)
    csv_write(args.out/'criteria_by_condition.csv',summaries)
    csv_write(args.out/'categories.csv',cats)
    dump(args.out/'attempts.json',records);dump(args.out/'summary.json',{'totals':totals,'criteria':summaries,'mapping':GROUPS,'definitions':DEFINITIONS,'unit':'attempt; each group at most once per attempt; groups overlap; no causal attribution','operational':'execution_completed AND finish_reason=stop; explicit fields, not absent checks','format':'parse.structured_valid if execution completed; otherwise absent','pending':'Raw clarification_missing_field=false with pending review retained; four ledger decisions=fail remain provisional, not human judgments'})
    examples=[]
    for model,sid in EXAMPLES:
        rec=next(r for r in records if r['model']==model and r['scenario']==sid and '-rep1-' in r['attempt_id'])
        r=read(ROOT/rec['attempt']);sc=cases[sid]
        examples.append({'attempt':rec['attempt'],'response':str(Path(rec['attempt']).with_name('response.txt')),'attempt_id':rec['attempt_id'],'scenario':sid,'model':model,'request':sc['resident_request'],'initial_state':sc['initial_state'],'expected':sc['evaluator'],'content':r['model_content'],'executor':r['validation'],'action_applied':r['action_applied'],'final_state':r['final_state'],'failed_checks':[c['name'] for c in r['evaluation']['checks'] if not c['passed']],'review':rec['review']})
    dump(args.out/'examples.json',examples)
    # Table cells use failed counts; separate observed denominators are explicit in labels/caption.
    for lang,index in [('en',0),('pt',1)]:
        category_labels={'clear':('Clear instructions','Instruções claras'),'paraphrase':('Paraphrases','Paráfrases'),'routine':('Routines','Rotinas'),'ambiguity':('Ambiguity','Ambiguidade'),'invalid':('Invalid requests','Pedidos inválidos')}
        category_lines=[]
        for category,labels in category_labels.items():
            cells=[]
            for model in MODELS:
                c=next(r for r in cats if r['model']==model and r['category']==category)
                cell=f"{c['successes']}/{c['attempts']}"
                if c['human_validation_pending']:cell+=r'$^{*}$'
                cells.append(cell)
            category_lines.append(texrow([labels[index],*cells]))
        (args.tex_out/f'category_rows_{lang}.tex').write_text(''.join(category_lines)+r'\bottomrule'+'\n')
        lines=[]
        for key,labels in LABELS.items():
            lines.append(texrow([labels[index],*[next(r['failed'] for r in summaries if r['model']==m and r['criterion']==key) for m in MODELS]]))
        clarification_cells=[]
        for m in MODELS:
            s=next(r for r in summaries if r['model']==m and r['criterion']=='clarification')
            cell=f"{s['failed']}/{s['observed']}" if s['observed'] else '--/0'
            if s['provisional_failed']: cell+=r'$^{*}$'
            clarification_cells.append(cell)
        lines.append(texrow([('Inadequate clarification ($p$)' if lang=='en' else 'Esclarecimento inadequado ($p$)'), *clarification_cells]))
        (args.tex_out/f'failure_rows_{lang}.tex').write_text(''.join(lines)+r'\bottomrule'+'\n')
        proposed=[t['clarifications_proposed'] for t in totals]; correct=[t['clarifications_correct'] for t in totals]; noact=[t['no_action_proposed'] for t in totals]
        if lang=='en':
            detail=f"Clarifications proposed/correct were {proposed[0]}/{correct[0]}, {proposed[1]}/{correct[1]}, and {proposed[2]}/{correct[2]} for rules, 0.5B, and 1.5B. All {proposed[1]} proposed 0.5B clarifications failed the question criterion; {totals[1]['human_validation_pending']} are provisional assisted judgments. The 1.5B model proposed none; zero clarification-check failures would not demonstrate clarification ability. The $p$ denominators for proposed \\texttt{{no\\_action}} are {noact[0]}, {noact[1]}, and {noact[2]}."
        else:
            detail=f"Esclarecimentos propostos/corretos foram {proposed[0]}/{correct[0]}, {proposed[1]}/{correct[1]} e {proposed[2]}/{correct[2]} para regras, 0.5B e 1.5B. Os {proposed[1]} esclarecimentos do 0.5B falharam no critério da pergunta; {totals[1]['human_validation_pending']} têm julgamento assistido provisório. O 1.5B não propôs esclarecimentos: zero falhas nessa verificação não demonstra capacidade de esclarecer. Os denominadores $p$ de \\texttt{{no\\_action}} propostos são {noact[0]}, {noact[1]} e {noact[2]}."
        (args.tex_out/f'clarification_{lang}.tex').write_text(detail+'\n')
        def count(model, criterion):
            return next(r['failed'] for r in summaries if r['model']==model and r['criterion']==criterion)
        def cat(model, category, key):
            return next(r[key] for r in cats if r['model']==model and r['category']==category)
        if lang=='en':
            patterns=f"Rules' {count('rules','no_action')} unsuccessful attempts all returned \\texttt{{no\\_action}} outside the accepted rejection policy: {cat('rules','paraphrase','no_action_failed')} paraphrases, {cat('rules','routine','no_action_failed')} routines, and {cat('rules','ambiguity','no_action_failed')} ambiguities. They preserved unrelated state but omitted required actions or clarification. The 0.5B configuration instead proposed prohibited light steps in {cat('05','invalid','prohibited_steps_failed')}/16 invalid attempts and inappropriate clarification in the other {cat('05','invalid','clarification_failed')}; {cat('05','invalid','preservation_failed')} invalid attempts changed protected state. For 1.5B, all {cat('15','clear','expected_steps_failed')}/16 clear attempts had incorrect step sets, but only {cat('15','clear','final_state_failed')} failed the target-state check: a correct target value alone can conceal an extra change. Its {count('15','expected_steps')} wrong-step attempts and {count('15','preservation')} preservation failures characterize this configuration, without establishing why it behaved this way."
        else:
            patterns=f"As {count('rules','no_action')} tentativas malsucedidas das regras retornaram \\texttt{{no\\_action}} fora da política de rejeição: {cat('rules','paraphrase','no_action_failed')} paráfrases, {cat('rules','routine','no_action_failed')} rotinas e {cat('rules','ambiguity','no_action_failed')} ambiguidades. Preservaram estados não relacionados, mas omitiram ações ou esclarecimento exigidos. O 0.5B propôs passos de luz proibidos em {cat('05','invalid','prohibited_steps_failed')}/16 pedidos inválidos e esclarecimento inadequado nos outros {cat('05','invalid','clarification_failed')}; {cat('05','invalid','preservation_failed')} tentativas inválidas alteraram estados protegidos. No 1.5B, todas as {cat('15','clear','expected_steps_failed')}/16 tentativas claras tiveram passos incorretos, mas só {cat('15','clear','final_state_failed')} falharam no estado-alvo: acertar o valor da luz pedida pode esconder uma mudança extra. Suas {count('15','expected_steps')} tentativas com passos incorretos e {count('15','preservation')} falhas de preservação caracterizam esta configuração, sem estabelecer por que ela se comportou assim."
        (args.tex_out/f'patterns_{lang}.tex').write_text(patterns+'\n')
    # Literal recorded outputs are quoted without reconstructing a model dialogue.
    for lang in ['en','pt']:
        texts=[]
        for i,e in enumerate(examples,1):
            prefix=f"\\noindent\\textbf{{E{i}}} (\\path{{{e['attempt_id']}}}).\\par\\nopagebreak[4]\n"
            request=tex(e['request']); action=e['content']
            # Compact, exact field excerpts; full JSON is retained in examples.json.
            if i==1:
                en=f"``{request}'' expects sala=on and quarto=on unchanged. Rules returned \\texttt{{no\\_action}} with reason ``Pedido fora das regras explícitas.''. No block occurred; sala stayed off. Final-state, exact-step, and no-action checks failed."
                pt=f"``{request}'' exige sala=on e quarto=on preservado. Regras retornaram \\texttt{{no\\_action}} com motivo ``Pedido fora das regras explícitas.''. Não houve bloqueio; sala ficou off. Falharam estado final, passos exatos e política de no-action."
                assert e['model']=='rules' and json.loads(action)['action']=='no_action'
            elif i==2:
                en=f"``{request}'', with no known location, requires asking the room. The 0.5B reply was \\texttt{{set\\_light}}, \\texttt{{room=sala}}, \\texttt{{value=on}}. The executor blocked it for insufficient room information; both lights remained unchanged (sala=off, quarto=on). Permission, expected-action, and prohibited-step checks failed despite preservation."
                pt=f"``{request}'', sem localização conhecida, exige perguntar o cômodo. O 0.5B retornou \\texttt{{set\\_light}}, \\texttt{{room=sala}}, \\texttt{{value=on}}. O executor bloqueou por informação insuficiente de cômodo; luzes preservadas (sala=off, quarto=on). Falharam permissão, ação esperada e passos proibidos, apesar da preservação."
                assert json.loads(action)=={'action':'set_light','room':'sala','value':'on'} and not e['executor']['allowed']
            elif i==3:
                en=f"``{request}'', with no known location, also requires asking the room. The 0.5B returned \\texttt{{ask\\_clarification}}, \\texttt{{missing\\_field=room}}, with question ``Quero a luz acender.''. No block or state change occurred (sala=off, quarto=on). Only the informative-question check failed provisionally: the recorded Codex judgment awaits human validation."
                pt=f"``{request}'', sem localização conhecida, também exige perguntar o cômodo. O 0.5B retornou \\texttt{{ask\\_clarification}}, \\texttt{{missing\\_field=room}}, com pergunta ``Quero a luz acender.''. Sem bloqueio nem mudança (sala=off, quarto=on). Apenas a pergunta informativa falhou provisoriamente: o julgamento registrado por Codex aguarda validação humana."
                assert e['review']['human_validation_pending'] and json.loads(action)['question']=='Quero a luz acender.'
            else:
                en=f"``{request}'' expects only sala=on, preserving quarto=on. The 1.5B returned a \\texttt{{set\\_lights}} plan with \\texttt{{(sala,on)}} and \\texttt{{(quarto,off)}}. Both commands were permitted and simulated; final sala=on, quarto=off. Exact-step and preservation checks failed, although the target-light check passed. One reply contains two commands, including one extra change."
                pt=f"``{request}'' exige apenas sala=on, preservando quarto=on. O 1.5B retornou plano \\texttt{{set\\_lights}} com \\texttt{{(sala,on)}} e \\texttt{{(quarto,off)}}. Ambos os comandos foram permitidos e simulados; final sala=on, quarto=off. Falharam passos exatos e preservação, embora a luz-alvo estivesse correta. Uma resposta contém dois comandos, com uma mudança extra."
                assert json.loads(action)['steps']==[{'action':'set_light','room':'sala','value':'on'},{'action':'set_light','room':'quarto','value':'off'}]
            texts.append('\\begin{samepage}\n'+prefix+(en if lang=='en' else pt)+'\\par\\end{samepage}\n\n')
        (args.tex_out/f'examples_{lang}.tex').write_text(''.join(texts).rstrip()+'\n')
    report=['# Complementary failure analysis (2026-10-28)\n', 'Post-hoc aggregation of frozen checks, not a new evaluator or causal classification. No success is newly awarded. Unit: one attempt per grouped criterion; indicators overlap and must not be summed.\n', '## Totals\n', '| Condition | Success/80 | Clarifications proposed/correct | Provisional assisted failures |\n|---|---:|---:|---:|']
    for t in totals:report.append(f"| {t['model']} | {t['successes']}/80 | {t['clarifications_proposed']}/{t['clarifications_correct']} | {t['human_validation_pending']} |")
    report += ['\n## Failed attempts by criterion\n', '| Criterion | Rules | 0.5B | 1.5B |\n|---|---:|---:|---:|']
    for key in records[0]['groups']:
        cells=[]
        for m in MODELS:
            s=next(r for r in summaries if r['model']==m and r['criterion']==key)
            cells.append(f"{s['failed']}/{s['observed']} observed ({s['absent_or_not_applicable']} absent; {s['provisional_failed']} provisional)")
        report.append('| '+key+' | '+' | '.join(cells)+' |')
    report+=['\n## Grouping and applicability\n', 'Selectors ending in `:` use startswith; every other selector uses exact equality. A group fails if ANY matching check fails; absent matching checks yield `absent`, never `passed`. Counts include observed, passed, failed, absent and provisional_failed. Multiple failed paths in a group count once. Operational/format indicators use explicit recorded fields, documented in summary.json.']
    for key,selectors in GROUPS.items():report.append(f"\n- **{key}**: `{selectors}`. {DEFINITIONS[key]}")
    report+=['\n`smarthome_pilot.evaluate_scenario` defines final/unchanged, top-level prohibition, conditional clarification and no_action checks. `study_v1.evaluate` adds exact step equality, non-light expected action and plan-aware prohibited steps. These are correlated contractual checks, not independent causes. A blocked wrong proposal remains a proposal error. no_action is correct for invalid requests, incorrect for valid commands and missing-room requests.\n', 'Raw pending clarification checks and all four ledger entries are retained in attempts.json. Counts treating them as unsuccessful follow the existing published totals, provisionally. If all four were accepted, 0.5B success would become 34/80; clarification-check failures 8/12 rather than 12/12; ambiguity success 4/16 rather than 0/16. Nothing is regraded here.\n', '## Files and reproduction\n', 'Run from repository root: `python3 experiments/smarthome_agents/scripts/analyze_failure_criteria.py`. Optional `--out` and `--tex-out` permit temporary reconstruction. `criteria_by_attempt.csv` links every check group to summary.json; attempts.json preserves exact checks and review details. criteria_by_condition.csv gives denominators, categories.csv groups two repetitions per scenario (8 scenarios, 16 attempts per category). examples.json preserves all original requests, outputs, state, permission and failed checks. Paper excerpts retain original Portuguese text; full JSON is in examples.json.\n', 'Command-level action_steps.csv and action_summary.json are reconstructed in memory and compared exactly, separately from attempt indicators. Existing attempts/categories/failure inventory/metrics are cross-checked. Inputs are hashed in input_manifest.json; all 18 frozen hashes verified. No network or inference is used.\n', '## Illustrative examples\n']
    for e in examples:
        report.append(f"\n### {e['attempt_id']}\n\nSource: `{e['attempt']}`; raw HTTP: `{e['response']}`\n\nRequest: {e['request']}\n\nRecorded output: `{e['content']}`\n\nExecutor: `{json.dumps(e['executor'])}`; final state: `{json.dumps(e['final_state'])}`\n\nFailed checks: `{e['failed_checks']}`. Full expected/initial state and assisted status: examples.json.\n")
    (args.out/'README.md').write_text('\n'.join(report))
    for p in [BASE/'study_v1/reserved.json',BASE/'study_v1/freeze.json',run/'manual_reviews.json',*historical.iterdir(),BASE/'scripts/study_v1.py',BASE/'scripts/smarthome_pilot.py']:
        if p.is_file():source(p)
    dump(args.out/'input_manifest.json',{'scientific_snapshot':'a834b8255f736fb59425b146be183c17866a2c7d','sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in sorted(sources)}})
    print(json.dumps({'totals':totals,'criteria':summaries},indent=2))

if __name__=='__main__':main()
