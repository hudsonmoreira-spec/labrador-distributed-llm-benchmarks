#!/usr/bin/env python3
"""Check explicit author-review provenance without modifying historical evidence."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]

def load(p):
    return json.loads(p.read_text())

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assessment = load(HERE / 'assessment.json')
    ledger_path = ROOT / 'experiments/smarthome_agents/runs/20261006-study-v1-quality/manual_reviews.json'
    ledger = load(ledger_path)
    reviews = assessment['reviews']
    assert len(reviews) == len(ledger) == 4
    assert {r['id'] for r in reviews} == {'0', '1', '2', '3'}
    for r in reviews:
        raw = load(ROOT / r['review_file'])
        assert raw == {k: v for k, v in r.items() if k != 'review_file'}
        assert r['kind'] == 'original' and r['decision'] == 'fail'
        assert not r['human_validation_pending'] and r['rationale'].strip()
        source = r['source']
        assert source['source'] == ledger[int(r['id'])]['attempt']
        path = ROOT / source['source']
        assert sha(path) == source['source_sha256']
        assert sha(path.parent / 'request.json') == source['request_sha256']
        assert sha(ledger_path) == source['ledger_sha256']
        summary = load(path)
        assert summary['model'] == '05'
        assert summary['model_content'] == source['response']
        assert json.loads(source['response'])['question'] == source['question']
    assert all(r['human_validation_pending'] for r in ledger)
    assert assessment['new_success_credit'] == 0
    print(json.dumps({'status': 'pass', 'explicit_author_assessments': 4,
                      'confirmed_failures': 4, 'new_success_credit': 0,
                      'historical_assisted_ledger': 'unchanged; superseded only by separate author-assessment layer'}))

if __name__ == '__main__':
    main()
