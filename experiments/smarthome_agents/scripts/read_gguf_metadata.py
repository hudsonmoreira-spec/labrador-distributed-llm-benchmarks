#!/usr/bin/env python3
"""Read GGUF metadata without redistributing model weights."""
import argparse
import json
import struct
from pathlib import Path

def read_metadata(path):
    with Path(path).open('rb') as f:
        def unpack(fmt):return struct.unpack('<'+fmt,f.read(struct.calcsize('<'+fmt)))[0]
        def string():return f.read(unpack('Q')).decode('utf-8',errors='replace')
        def value(kind):
            if kind==8:return string()
            if kind==9:
                subtype=unpack('I');n=unpack('Q');items=[value(subtype) for _ in range(n)]
                return {'type':subtype,'length':n} if n>100 else items
            return unpack({0:'B',1:'b',2:'H',3:'h',4:'I',5:'i',6:'f',7:'?',10:'Q',11:'q',12:'d'}[kind])
        assert f.read(4)==b'GGUF'
        version=unpack('I');tensors=unpack('Q');n=unpack('Q')
        metadata={}
        for _ in range(n):
            key=string();metadata[key]=value(unpack('I'))
        return {'gguf_version':version,'tensor_count':tensors,'metadata':metadata}
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('model');a.add_argument('--out',required=True);args=a.parse_args()
    Path(args.out).write_text(json.dumps(read_metadata(args.model),ensure_ascii=False,indent=2)+'\n')
