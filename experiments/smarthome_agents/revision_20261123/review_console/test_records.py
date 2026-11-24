"""Persistence/provenance tests; fixture judgments never enter real review records."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import app

class ReviewRecords(unittest.TestCase):
 def setUp(self):
  self.temp=TemporaryDirectory();self.old=app.DATA;app.DATA=Path(self.temp.name);self.before=app.sha(app.LEDGER)
 def tearDown(self):
  self.assertEqual(self.before,app.sha(app.LEDGER));app.DATA=self.old;self.temp.cleanup()
 def test_originals_match_source_without_assisted_labels(self):
  rows=app.originals();self.assertEqual(len(rows),4)
  for r in rows:
   self.assertEqual(r['source_sha256'],app.sha(app.ROOT/r['source']))
   self.assertNotIn('decision',r)
 def test_uncertain_stays_pending_and_reviews_are_append_only(self):
  b={'kind':'original','id':'0','decision':'uncertain','reviewer':'Automated fixture; not human review','reason':'Fixture'}
  a=app.record_review(b);self.assertTrue(a['human_validation_pending'])
  b['decision']='fail';c=app.record_review(b);self.assertFalse(c['human_validation_pending'])
  self.assertNotEqual(a['record_id'],c['record_id']);self.assertEqual(len(app.reviews()),2)
  self.assertEqual(a['source']['question'],'Quero a luz acender.')
 def test_no_implicit_judgment_or_unidentified_reviewer(self):
  for b in [{'kind':'original','id':'0','reviewer':'Fixture'}, {'kind':'original','id':'0','decision':'fail','reviewer':'Fixture'}, {'kind':'original','id':'999','decision':'pass','reviewer':'Fixture'}, {'kind':'original','id':'0','decision':'pass','reviewer':''}]:
   with self.assertRaises(ValueError):app.record_review(b)
  self.assertEqual(app.reviews(),[])

if __name__=='__main__':unittest.main()
