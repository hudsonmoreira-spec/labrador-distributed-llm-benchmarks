import sys
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'experiments/smarthome_agents/scripts'))
import run_study_v1 as controller

class ReadinessTests(unittest.TestCase):
    def test_waits_for_both_models_after_timeout(self):
        replies=[[{'is_processing':True}],[{'is_processing':False}],[{'is_processing':False}],[{'is_processing':False}]]
        with patch.object(controller,'get',side_effect=replies) as query, patch.object(controller.time,'sleep') as sleep:
            result=controller.wait_board_idle('test')
        self.assertTrue(result['ready'])
        self.assertEqual(query.call_count,4)
        self.assertEqual(sleep.call_count,1)
        self.assertIn('19015',query.call_args_list[1].args[0])

    def test_readiness_failure_is_not_permission_to_dispatch(self):
        with patch.object(controller,'get',side_effect=TimeoutError('offline')):
            result=controller.wait_board_idle('test')
        self.assertFalse(result['ready'])
        self.assertIn('TimeoutError',result['error'])

if __name__=='__main__':unittest.main()
