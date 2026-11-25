import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import controller
class Routing(unittest.TestCase):
 def case(self,text,loc=None):return {'resident_request':text,'initial_state':{'rooms':{'sala':{'light':'off'},'quarto':{'light':'on'}},'known_location':loc},'permissions':{'set_light':{'rooms':['sala','quarto'],'values':['on','off']}}}
 def test_recognised_uses_rules_without_model(self):
  for text in ['Acenda a luz da sala.','Acenda a luz.','Acenda a luz da sala e apague a luz do quarto.']:
   r=controller.interpret(self.case(text),'hybrid',801,lambda _:self.fail('Unexpected model call'))
   self.assertFalse(r['fallback']);self.assertEqual(r['origin'],'rules')
 def test_unrecognised_falls_back_with_same_original_prompt(self):
  for text in ['Pode deixar a sala iluminada?','Ligue o ar-condicionado da sala.']:
   calls=[]
   def call(p):calls.append(p);return {'choices':[{'message':{'content':'{"action":"no_action","reason":"unsupported"}'},'finish_reason':'stop'}]}
   c=self.case(text);r=controller.interpret(c,'hybrid',802,call)
   self.assertTrue(r['fallback']);self.assertEqual(calls,[controller.study.query('',c,{'temperature':0,'seed':802,'max_tokens':128})])
 def test_rules_baseline_never_calls_model(self):
  r=controller.interpret(self.case('Abra a porta.'),'rules',801,lambda _:self.fail('Unexpected model call'))
  self.assertEqual(r['rule_action']['action'],'no_action');self.assertFalse(r['fallback'])
if __name__=='__main__':unittest.main()
