#!/usr/bin/env python3
"""Acquire only the verified native BIGANN first-10M prefix (never a full 1B base)."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import struct
import urllib.request

BASE_URL = 'https://dl.fbaipublicfiles.com/billion-scale-ann-benchmarks/'
SOURCES = {
 'base': ('bigann/base.1B.u8bin', 128000000008, 1280000008, (1000000000,128)),
 'query': ('bigann/query.public.10K.u8bin', 1280008,1280008,(10000,128)),
 'ground_truth': ('GT_10M/bigann-10M',8000008,8000008,(10000,100)),
}

def response(url,start,end,total,etag=None):
    headers={'Range':f'bytes={start}-{end}','Accept-Encoding':'identity'}
    if etag: headers['If-Match']=etag
    stream=urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=60)
    try:
        if stream.status != 206 or stream.headers.get('Content-Range') != f'bytes {start}-{end}/{total}':
            raise ValueError('Server did not honor exact range; refusing full-body acquisition')
        if int(stream.headers.get('Content-Length','-1')) != end-start+1:
            raise ValueError('Unexpected range length')
        if etag and stream.headers.get('ETag') != etag: raise ValueError('Source ETag changed')
        return stream
    except BaseException:
        stream.close(); raise


def acquire(root):
    root=Path(root).expanduser().resolve(); root.mkdir(parents=True,exist_ok=True)
    records=[]
    for role,(name,total,size,shape) in SOURCES.items():
        target=root/(name.rsplit('/',1)[-1]+('.first10M' if role=='base' else ''))
        partial=target.with_name(target.name+'.partial'); meta=target.with_name(target.name+'.acquisition.json')
        if target.exists() or partial.exists() or meta.exists(): raise FileExistsError(str(target))
        url=BASE_URL+name
        with response(url,0,15,total) as probe:
            header=probe.read(); etag=probe.headers.get('ETag')
        if not etag: raise ValueError('Source lacks an ETag for stable range acquisition')
        if len(header)!=16 or struct.unpack('<II',header[:8]) != shape: raise ValueError('Source shape mismatch')
        digest=hashlib.sha256(); received=0
        started=dt.datetime.now(dt.timezone.utc).isoformat()
        with response(url,0,size-1,total,etag) as stream, partial.open('xb') as output:
            info={key:stream.headers.get(key) for key in ('Content-Range','Content-Length','ETag','Last-Modified','x-amz-version-id','Accept-Ranges')}
            for chunk in iter(lambda:stream.read(4*1024*1024),b''):
                received+=len(chunk)
                if received>size: raise ValueError('Overlong source prefix')
                output.write(chunk); digest.update(chunk)
            output.flush(); os.fsync(output.fileno())
        if received!=size: raise ValueError(f'Truncated acquisition {received}/{size}')
        if role=='base':
            with partial.open('rb') as local:
                if local.read(8)!=header[:8]: raise ValueError('Header changed')
                for qid in (0,5000000,9999999):
                    start=8+qid*128
                    with response(url,start,start+127,total,etag) as remote:
                        expected=remote.read()
                    local.seek(start)
                    if len(expected)!=128 or local.read(128)!=expected: raise ValueError('Remote payload spot check mismatch')
        os.link(partial,target) # atomic publish, refuses to overwrite
        partial.unlink()
        record={'role':role,'source_url':url,'source_description':'Official Big ANN benchmark native-format mirror; canonical first-10M ordering',
                'original_filename':name.rsplit('/',1)[-1],'acquisition_method':'HTTP exact byte range prefix' if role=='base' else 'HTTP exact full-file byte range',
                'timestamp_start':started,'timestamp_end':dt.datetime.now(dt.timezone.utc).isoformat(),
                'path':str(target),'size_bytes':size,'sha256':digest.hexdigest(),'headers':info,
                'remote_original_size_bytes':total,'source_count':shape[0],'dimension_or_top_k':shape[1]}
        with meta.open('x') as output: json.dump(record,output,indent=2);output.write('\n')
        records.append(record); print(json.dumps(record),flush=True)
    return records

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-root',required=True)
    acquire(p.parse_args().source_root)
