import sys
import unittest
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'experiments/smarthome_agents/scripts'))
import study_v1 as study
import smarthome_pilot as pilot
DEV=pilot.load_json(ROOT/'experiments/smarthome_agents/study_v1/development.json')

class StudyTests(unittest.TestCase):
    def test_atomic_plan_blocks_unknown_room(self):
        sc=DEV[4]
        action={'action':'set_lights','steps':[{'action':'set_light','room':'sala','value':'on'},{'action':'set_light','room':'garage','value':'on'}]}
        final,permission,decisions=study.execute(sc,action)
        self.assertFalse(permission['allowed'])
        self.assertEqual(final,sc['initial_state'])

    def test_plan_extra_step_and_duplicates_fail(self):
        self.assertFalse(study.parse('{"action":"set_lights","steps":[{"action":"set_light","room":"sala","value":"on"},{"action":"set_light","room":"sala","value":"off"}]}')['structured_valid'])
        sc=DEV[0]
        action={'action':'set_lights','steps':[{'action':'set_light','room':'sala','value':'on'},{'action':'set_light','room':'quarto','value':'off'}]}
        final,permission,_=study.execute(sc,action)
        self.assertFalse(study.evaluate(sc,action,final,permission,True,True)['task_completed'])

    def test_independent_evaluation_of_wrong_room(self):
        sc=deepcopy(DEV[0]);action={'action':'set_light','room':'quarto','value':'on'}
        final,p,_=study.execute(sc,action)
        self.assertTrue(p['allowed'])
        ev=study.evaluate(sc,action,final,p,True,True)
        self.assertFalse(ev['task_completed'])
        self.assertTrue(ev['undue_proposal'])
        sc['evaluator']={'invalid':'oracle must not be used'}
        self.assertEqual(study.execute(sc,action),(final,p,[p]))

    def test_rules_do_not_use_oracle(self):
        sc=deepcopy(DEV[0]);a=study.rule_response(sc);del sc['evaluator'];del sc['category']
        self.assertEqual(a,study.rule_response(sc))

    def test_plan_success_and_prompt_has_no_evaluator(self):
        sc=DEV[4];action=study.rule_response(sc)
        final,p,_=study.execute(sc,action)
        self.assertTrue(study.evaluate(sc,action,final,p,True,True)['task_completed'])
        sc=deepcopy(sc);sc['evaluator']={'secret':'never disclose'}
        self.assertNotIn('never disclose',str(study.messages(sc)))

if __name__=='__main__':unittest.main()
