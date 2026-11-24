import json
import unittest
import hybrid_v2 as hybrid
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
import smarthome_pilot as pilot

def case(text,location=None):return {'resident_request':text,'initial_state':{'known_location':location}}
def reply(intent):return {'choices':[{'finish_reason':'stop','message':{'content':json.dumps({'intent':intent})}}]}
class Rules(unittest.TestCase):
 def test_unsupported_never_calls_model(self):
  def never(_):raise AssertionError('Model should not be called')
  a,t,o=hybrid.interpret(case('Ligue o ar-condicionado da sala.'),never,pilot.normalize_text)
  self.assertEqual(a['action'],'no_action');self.assertEqual(t,[]);self.assertEqual(o,'scope_rule_without_model')
 def test_explicit_room_has_priority_over_location(self):
  a,t,o=hybrid.interpret(case('Apague a luz do quarto.','sala'),lambda p:reply('off'),pilot.normalize_text)
  self.assertEqual(a,{'action':'set_light','room':'quarto','value':'off'})
 def test_missing_room_requires_question(self):
  a,t,o=hybrid.interpret(case('Acenda a luz.'),lambda p:reply('on'),pilot.normalize_text)
  self.assertEqual(a['action'],'ask_clarification');self.assertEqual(a['missing_field'],'room');self.assertEqual(len(t),1)
 def test_routine_keeps_each_target(self):
  answers=iter(['on','off'])
  a,t,o=hybrid.interpret(case('Acenda a luz da sala e apague a luz do quarto.'),lambda p:reply(next(answers)),pilot.normalize_text)
  self.assertEqual(a['steps'],[{'action':'set_light','room':'sala','value':'on'},{'action':'set_light','room':'quarto','value':'off'}])
 def test_conflicting_room_is_rejected(self):
  answers=iter(['on','off'])
  a,t,o=hybrid.interpret(case('Acenda a luz da sala e apague a luz da sala.'),lambda p:reply(next(answers)),pilot.normalize_text)
  self.assertEqual(a['action'],'no_action')
if __name__=='__main__':unittest.main()
