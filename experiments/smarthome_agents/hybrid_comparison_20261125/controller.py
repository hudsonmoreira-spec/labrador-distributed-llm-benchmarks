#!/usr/bin/env python3
"""Rules-first fallback; operational input only, original study grammar unchanged."""
import json,time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.request import Request,build_opener,ProxyHandler
import study_v1 as study
OPENER=build_opener(ProxyHandler({}))
def interpret(operational,condition,seed,call):
    case={k:operational[k] for k in ('resident_request','initial_state','permissions')}
    assert condition in ['rules','05','hybrid']
    rule=None
    if condition in ['rules','hybrid']:
        rule=study.rule_response(case)
        # Original grammar's sole no_action branch means unrecognised, not a
        # separately recognised refusal. Do not invent oracle-aware rejection.
        if condition=='rules' or rule['action']!='no_action':
            return {'content':json.dumps(rule,ensure_ascii=False),'completed':True,'origin':'rules','fallback':False,'rule_action':rule,'model_request':None,'model_response':None}
    payload=study.query('',case,{'temperature':0,'seed':seed,'max_tokens':128})
    response=call(payload)
    choice=response['choices'][0]
    return {'content':choice['message'].get('content',''),'completed':choice.get('finish_reason')=='stop','origin':'model_fallback' if condition=='hybrid' else 'model','fallback':condition=='hybrid','rule_action':rule,'model_request':payload,'model_response':response}

def model_call(payload):
    req=Request('http://127.0.0.1:19115/v1/chat/completions',data=json.dumps(payload,ensure_ascii=False).encode(),headers={'Content-Type':'application/json'})
    with OPENER.open(req,timeout=185) as r:return json.load(r)
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def answer(self,status,body):
        raw=json.dumps(body,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
    def do_GET(self):
        if self.path=='/health':self.answer(200,{'status':'ok','controller':'rules_first_v1'})
        else:self.answer(404,{'error':'not_found'})
    def do_POST(self):
        if self.path!='/action':return self.answer(404,{'error':'not_found'})
        try:
            n=int(self.headers.get('Content-Length','0'));assert 0<n<32768
            b=json.loads(self.rfile.read(n));assert b['seed'] in [801,802]
            start=time.monotonic();result=interpret(b['case'],b['condition'],b['seed'],model_call);result['controller_elapsed_s']=time.monotonic()-start
            self.answer(200,result)
        except Exception as e:self.answer(500,{'error':str(e),'inference_may_have_been_dispatched':True})
if __name__=='__main__':ThreadingHTTPServer(('0.0.0.0',19121),Handler).serve_forever()
