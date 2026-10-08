#!/usr/bin/env python3
"""Finalize immutable input/index packages; verify manifest digests without rehashing components."""
import argparse
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct
import sys

VERSION=1
HEX=re.compile(r'^[0-9a-f]{64}$')
ROLES={'input':{'base','query','ground_truth'}, 'index':{'disk_index','tags','pq_compressed','pq_pivots'}}

def digest_file(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(4*1024*1024),b''): digest.update(block)
    return digest.hexdigest()

def serialize(value):
    return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()

def valid_hash(value):
    return isinstance(value,str) and HEX.fullmatch(value) is not None

def validate_manifest(value):
    """Standard-library validation of the versioned schema's required contract."""
    if not isinstance(value,dict) or type(value.get('schema_version')) is not int or value['schema_version']!=VERSION:
        raise ValueError('Unsupported package schema version')
    try:
        from jsonschema import Draft202012Validator
    except ImportError as error:
        raise ValueError("Package workflows require jsonschema; use .venv-research and requirements-research.txt") from error
    schema = json.loads((Path(__file__).resolve().parents[2] / "schemas/research/package.schema.json").read_text())
    errors = list(Draft202012Validator(schema).iter_errors(value))
    if errors:
        raise ValueError("Package schema validation failed: " + errors[0].message)
    kind=value.get('package_kind')
    if kind not in ROLES: raise ValueError('Unknown package kind')
    for key in ('package_id','logical_dataset','metric','dtype','created_at'):
        if not isinstance(value.get(key),str) or not value[key]: raise ValueError('Missing package field: '+key)
    if value['metric']!='l2' or value['dtype']!='uint8': raise ValueError('This package version supports uint8 L2 only')
    for key in ('N','D'):
        if type(value.get(key)) is not int or value[key]<1: raise ValueError('Invalid '+key)
    if not isinstance(value.get('files'),list) or not value['files']: raise ValueError('Empty package files')
    roles=set();paths=set()
    for entry in value['files']:
        if not isinstance(entry,dict): raise ValueError('Invalid file entry')
        role=entry.get('role');path=entry.get('path')
        if not isinstance(role,str) or not role or role in roles: raise ValueError('Duplicate/invalid role')
        if not isinstance(path,str) or not Path(path).is_absolute() or path in paths: raise ValueError('Duplicate/nonabsolute path')
        roles.add(role);paths.add(path)
        if not valid_hash(entry.get('sha256')): raise ValueError('Missing full component SHA256')
        for key in ('size_bytes','mtime_ns'):
            if type(entry.get(key)) is not int or entry[key]<0: raise ValueError('Invalid '+key)
        if entry['size_bytes']==0: raise ValueError('Empty package component')
        for key in ('vector_count','dimension','top_k'):
            if key in entry and (type(entry[key]) is not int or entry[key]<1): raise ValueError('Invalid '+key)
        if not isinstance(entry.get('dtype'),str) or not entry['dtype']: raise ValueError('Missing component dtype')
        if kind=='input':
            required=('vector_count','top_k') if role=='ground_truth' else ('vector_count','dimension')
            if any(key not in entry for key in required): raise ValueError('Missing input shape metadata')
    if not ROLES[kind].issubset(roles): raise ValueError('Required component roles missing')
    if kind=='input':
        for key in ('source_provenance','conversion'):
            if not isinstance(value.get(key),list) or not value[key] or any(not isinstance(item,dict) for item in value[key]):
                raise ValueError('Missing '+key)
        entries={entry['role']:entry for entry in value['files']}
        for role in ('base','query'):
            item=entries[role]
            if item['dtype']!='uint8' or item['dimension']!=value['D'] or item['size_bytes']!=8+item['vector_count']*item['dimension']:
                raise ValueError('Input vector shape/type/size mismatch')
        if entries['base']['vector_count']!=value['N']: raise ValueError('Base cardinality mismatch')
        gt=entries['ground_truth']
        if gt['vector_count']!=entries['query']['vector_count'] or gt['dtype']!='uint32_ids_float32_distances' or gt['size_bytes']!=8+gt['vector_count']*gt['top_k']*8:
            raise ValueError('Ground truth shape/type/size mismatch')
    else:
        if not valid_hash(value.get('input_package_manifest_sha256')): raise ValueError('Missing input package digest')
        if not isinstance(value.get('index_prefix'),str) or not Path(value['index_prefix']).is_absolute(): raise ValueError('Invalid index prefix')
        if not isinstance(value.get('build'),dict) or not isinstance(value.get('parameters'),dict): raise ValueError('Missing index build metadata')
        params=value['parameters']
        for key in ('R','L','pq_bytes','memory_budget_GiB','threads'):
            if type(params.get(key)) is not int or params[key]<1: raise ValueError('Invalid index parameter '+key)
        if params.get('metric')!='l2' or params.get('neighbor_type')!='pq' or params.get('algorithm')!='Vamana': raise ValueError('Invalid index format')
        build=value['build']
        for key in ('builder_binary_sha256','builder_commit','command','timestamp_start','timestamp_end','wall_time_s','log_path','log_sha256'):
            if key not in build: raise ValueError('Missing build field '+key)
        if not valid_hash(build['builder_binary_sha256']) or not valid_hash(build['log_sha256']): raise ValueError('Invalid build digest')
    return value

def check_components(value,full=False):
    """Cheap identity/size checks normally; full content verification is explicit."""
    for entry in value['files']:
        path=Path(entry['path'])
        if not path.is_file() or str(path.resolve())!=entry['path']: raise ValueError('Missing/noncanonical component: '+str(path))
        stat=path.stat()
        if stat.st_size!=entry['size_bytes'] or stat.st_mtime_ns!=entry['mtime_ns']: raise ValueError('Component size/mtime changed: '+str(path))
        if full and digest_file(path)!=entry['sha256']: raise ValueError('Component content changed: '+str(path))

def load_verified(path,kind=None):
    path=Path(path).expanduser().resolve()
    raw=path.read_bytes(); digest=hashlib.sha256(raw).hexdigest()
    sidecar=path.with_suffix('.sha256')
    fields=sidecar.read_text().strip().split()
    if len(fields)!=2 or fields[0]!=digest or fields[1]!=path.name: raise ValueError('Package manifest SHA256 mismatch')
    try: value=json.loads(raw)
    except (ValueError,UnicodeError) as error: raise ValueError('Corrupt package JSON') from error
    validate_manifest(value)
    if kind is not None and value['package_kind']!=kind: raise ValueError('Wrong package kind')
    check_components(value)
    return value,digest

def validate_native_inputs(value):
    files={entry['role']:entry for entry in value['files']}
    for role in ('base','query','ground_truth'):
        entry=files[role]
        with Path(entry['path']).open('rb') as stream:
            header=stream.read(8)
            shape=(entry['vector_count'],entry['top_k'] if role=='ground_truth' else entry['dimension'])
            if len(header)!=8 or struct.unpack('<II',header)!=shape: raise ValueError('Native input header mismatch: '+role)
            if role=='ground_truth':
                count=shape[0]*shape[1]
                # Check every ID and distance, using bounded chunks.
                remaining=count
                while remaining:
                    n=min(remaining,65536);block=stream.read(n*4)
                    if len(block)!=n*4 or any(id_>=value['N'] for (id_,) in struct.iter_unpack('<I',block)):
                        raise ValueError('Ground truth ID outside base cardinality')
                    remaining-=n
                remaining=count
                while remaining:
                    n=min(remaining,65536);block=stream.read(n*4)
                    if len(block)!=n*4 or any(not math.isfinite(x) or x<0 for (x,) in struct.iter_unpack('<f',block)):
                        raise ValueError('Invalid ground truth distance')
                    remaining-=n

def finalize(spec,output):
    """Each canonical component is hashed once here, irrespective of file size."""
    output=Path(output).expanduser().resolve();sidecar=output.with_suffix('.sha256')
    if output.exists() or sidecar.exists(): raise FileExistsError('Package already exists; preserved')
    value=json.loads(json.dumps(spec));value['schema_version']=VERSION
    value.setdefault('created_at',dt.datetime.now(dt.timezone.utc).isoformat())
    for entry in value['files']:
        path=Path(entry['path']).expanduser().resolve();entry['path']=str(path)
        before=path.stat();entry.update(size_bytes=before.st_size,mtime_ns=before.st_mtime_ns,sha256=digest_file(path))
        after=path.stat()
        if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns): raise ValueError('Component changed during hashing')
    validate_manifest(value)
    if value['package_kind']=='input': validate_native_inputs(value)
    raw=serialize(value);digest=hashlib.sha256(raw).hexdigest()
    output.parent.mkdir(parents=True,exist_ok=True)
    # Exclusive writes preserve old packages. A crash before sidecar makes verification fail closed.
    with output.open('xb') as stream: stream.write(raw);stream.flush();os.fsync(stream.fileno())
    with sidecar.open('x') as stream: stream.write(f'{digest}  {output.name}\n');stream.flush();os.fsync(stream.fileno())
    return digest

def bindings(args):
    """Bind both package digests to actual benchmark inputs without large-file hashing."""
    result={key:None for key in ('input_package_manifest_path','input_package_manifest_sha256','index_package_manifest_path','index_package_manifest_sha256')}
    packages={}
    for kind in ('input','index'):
        supplied=getattr(args,kind+'_package_manifest',None)
        if supplied:
            path=Path(supplied).expanduser().resolve();value,digest=load_verified(path,kind)
            result[kind+'_package_manifest_path']=str(path);result[kind+'_package_manifest_sha256']=digest;packages[kind]=value
    if args.dataset_id.lower()=='sift10m' and set(packages)!={'input','index'}: raise ValueError('SIFT10M runs require both immutable package manifests')
    if 'index' in packages and 'input' not in packages: raise ValueError('Index binding requires its input package')
    if 'input' in packages:
        inp=packages['input'];entries={entry['role']:entry for entry in inp['files']}
        if inp['logical_dataset']!=args.dataset_id or inp['dtype']!=args.data_type or inp['metric']!=args.distance_metric:
            raise ValueError('Input package dataset/type/metric mismatch')
        if str(args.query)!=entries['query']['path'] or str(args.ground_truth)!=entries['ground_truth']['path']:
            raise ValueError('Query/GT paths disagree with package roles')
        if args.dataset_id.lower() == 'sift10m' and (inp['N'], inp['D'], args.query_count) != (10000000, 128, 10000):
            raise ValueError('SIFT10M package must contain canonical N=10M/D128/query10K')
        base=Path(entries['base']['path'])
        if args.dataset_path != base and args.dataset_path not in base.parents: raise ValueError('Dataset path disagrees with package base')
        if args.query_count!=entries['query']['vector_count'] or args.query_dimension!=inp['D'] or entries['ground_truth']['top_k']<args.k:
            raise ValueError('Input shape/K disagrees with package')
    if 'index' in packages:
        idx=packages['index'];inp=packages['input'];entries={entry['role']:entry for entry in idx['files']}
        if idx['input_package_manifest_sha256']!=result['input_package_manifest_sha256']:
            raise ValueError('Index was built from a different input package')
        if any(idx[key]!=inp[key] for key in ('logical_dataset','N','D','dtype','metric')) or idx['parameters']['neighbor_type']!=args.neighbor_type:
            raise ValueError('Index/input/search format mismatch')
        if idx['index_prefix']!=str(args.index_prefix): raise ValueError('Index prefix disagrees with package')
        suffixes={'disk_index':'_disk.index','tags':'_disk.index.tags','pq_compressed':'_pq_compressed.bin','pq_pivots':'_pq_pivots.bin'}
        if any(entries[role]['path']!=str(args.index_prefix)+suffix for role,suffix in suffixes.items()): raise ValueError('Index component role mismatch')
        paths={entry['path'] for entry in idx['files']}
        if any(str(path) not in paths for path in args.index_files): raise ValueError('Search index component absent from package')
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    create=sub.add_parser('create');create.add_argument('--spec',required=True);create.add_argument('--output',required=True)
    verify=sub.add_parser('verify');verify.add_argument('manifest');verify.add_argument('--full-components',action='store_true')
    args=p.parse_args()
    if args.command=='create': digest=finalize(json.loads(Path(args.spec).read_text()),args.output)
    else:
        value,digest=load_verified(args.manifest);check_components(value,full=args.full_components)
    print(json.dumps({'status':'success','manifest_sha256':digest}))
    return 0

if __name__=='__main__':
    try: sys.exit(main())
    except (OSError,ValueError,KeyError,TypeError) as error:
        print(json.dumps({'status':'failed','error':str(error)}),file=sys.stderr);sys.exit(1)
