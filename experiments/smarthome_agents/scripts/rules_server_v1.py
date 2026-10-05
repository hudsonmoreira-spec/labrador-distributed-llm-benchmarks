#!/usr/bin/env python3
"""Resident, stateless rule baseline on SBC. No evaluator input is accepted."""
import json
import time
from http.server import BaseHTTPRequestHandler,HTTPServer
import study_v1 as study

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body=json.dumps({'status':'ok','version':study.VERSION,'backend':'rules'}).encode()
        self.send_response(200);self.end_headers();self.wfile.write(body)
    def do_POST(self):
        raw=self.rfile.read(int(self.headers['Content-Length']))
        start=time.monotonic()
        data=json.loads(raw)
        sc={k:data['scenario'][k] for k in ('resident_request','initial_state','permissions')}
        content=json.dumps(study.rule_response(sc),ensure_ascii=False,separators=(',',':'))
        response={'choices':[{'finish_reason':'stop','message':{'content':content}}],
                  'usage':{},'timings':{'rule_compute_s':time.monotonic()-start},'model':'rules-v1'}
        body=json.dumps(response,ensure_ascii=False).encode()
        self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(body)
    def log_message(self,fmt,*args):pass
if __name__=='__main__':HTTPServer(('0.0.0.0',19000),Handler).serve_forever()
