"""Development controller: Qwen interprets intent; explicit rules resolve rooms and missing context."""
import re
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'../scripts'))
# Runtime integration supplies study_v1 through the existing controller.
INTENT_SYSTEM=('Classifique a intenção do pedido SOMENTE para iluminação. '
'Ligar/acender/iluminar significa on. Apagar/desligar/escurecer significa off. '
'Pedido sobre aparelho, porta ou assunto diferente de iluminação significa unsupported. '
'Não execute nada. Retorne somente JSON com intent igual a on, off ou unsupported.')
INTENT_SCHEMA={'type':'object','additionalProperties':False,'required':['intent'],'properties':{'intent':{'enum':['on','off','unsupported']}}}
EXAMPLES=[{'role':'user','content':'Desligue a lâmpada do dormitório.'},{'role':'assistant','content':'{"intent":"off"}'},{'role':'user','content':'Ilumine este ambiente.'},{'role':'assistant','content':'{"intent":"on"}'},{'role':'user','content':'Ative o ar-condicionado.'},{'role':'assistant','content':'{"intent":"unsupported"}'}]
def payload(text):
 return {'messages':[{'role':'system','content':INTENT_SYSTEM},*EXAMPLES,{'role':'user','content':text}],'temperature':0,'seed':801,'max_tokens':24,'cache_prompt':False,'response_format':{'type':'json_schema','json_schema':{'name':'light_intent','strict':True,'schema':INTENT_SCHEMA}}}

def interpret(case,call,normalize):
 text=case['resident_request'];location=case['initial_state'].get('known_location')
 # Same conservative room vocabulary used by the original executor; no evaluator access.
 def rooms(t):return [r for r in ['sala','quarto'] if re.search(r'\b'+r+r'\b',normalize(t))]
 clauses=[x.strip() for x in re.split(r'\s+e\s+|[,;]',text) if x.strip()]
 if len(clauses)>2:clauses=[text]
 traces=[];steps=[]
 for clause in clauses:
  response=call(payload(clause));traces.append(response)
  import json
  content=response['choices'][0]['message']['content']
  if response['choices'][0]['finish_reason']!='stop':raise ValueError('Geração de intenção incompleta')
  item=json.loads(content)
  if set(item)!={'intent'} or item['intent'] not in ['on','off','unsupported']:raise ValueError('Intenção inválida')
  if item['intent']=='unsupported':return {'action':'no_action','reason':'Pedido fora do controle de iluminação.'},traces,'model_intent_and_rules'
  targets=rooms(clause)
  if not targets:
   if location in ['sala','quarto']:targets=[location]
   else:return {'action':'ask_clarification','missing_field':'room','question':'Em qual cômodo: sala ou quarto?'},traces,'model_intent_and_missing_room_rule'
  steps.extend({'action':'set_light','room':r,'value':item['intent']} for r in targets)
 if not steps:return {'action':'no_action','reason':'Não foi identificada uma ação de iluminação.'},traces,'model_intent_and_rules'
 if len({s['room'] for s in steps})!=len(steps):return {'action':'no_action','reason':'Há comandos repetidos ou conflitantes para o mesmo cômodo.'},traces,'model_intent_and_conflict_rule'
 return (steps[0] if len(steps)==1 else {'action':'set_lights','steps':steps}),traces,'model_intent_and_rules'
