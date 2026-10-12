#!/usr/bin/env python3
"""Validate/finalize one completed native 0.1.0 split index. Never repairs partials."""
import argparse
import json
from pathlib import Path
import shutil
import struct
import numpy as np
from paper_rebaseline import canonical_bytes, digest
from paper_portable_v2 import utc
from paper_native_v3 import check_diagnostics, verify_native_package


def validate_structure(prefix, base, n=10000000, d=128, r=64):
    disk = Path(str(prefix)+'_disk.index')
    with disk.open('rb') as f:
        rows, cols = struct.unpack('<II', f.read(8))
        if (rows, cols)!=(9,1):
            raise ValueError('Native disk metadata shape mismatch')
        meta = struct.unpack('<'+str(rows)+'Q', f.read(rows*8))
    if (rows, cols) != (9, 1) or meta[0:2] != (n,d) or not 0 <= meta[2] < n:
        raise ValueError('Native disk header/cardinality/dimension/medoid mismatch')
    node_bytes, slots = meta[3:5]
    expected = (1+(n+slots-1)//slots)*4096
    if node_bytes != d+4*(r+1) or slots != 4096//node_bytes or disk.stat().st_size != expected or meta[7] != expected:
        raise ValueError('Native disk geometry/byte-size mismatch')
    pq = Path(str(prefix)+'_pq_compressed.bin')
    with pq.open('rb') as f:
        if struct.unpack('<II',f.read(8)) != (n,32) or pq.stat().st_size != 8+n*32:
            raise ValueError('PQ32 header/size mismatch')
    with Path(base).open('rb') as f:
        if struct.unpack('<II',f.read(8)) != (n,d):
            raise ValueError('Canonical base header mismatch')
    vectors = np.memmap(base,mode='r',offset=8,dtype='u1',shape=(n,d))
    count=0; min_degree=r; max_degree=0; edge_count=0
    with disk.open('rb') as f:
        f.seek(4096)
        while count<n:
            sectors=min(1024,(n-count+slots-1)//slots)
            data=f.read(sectors*4096)
            if len(data)!=sectors*4096: raise ValueError('Truncated disk body')
            degrees=np.ndarray((sectors,slots),dtype='<u4',buffer=data,offset=d,strides=(4096,node_bytes)).reshape(-1)
            neighbors=np.ndarray((sectors,slots,r),dtype='<u4',buffer=data,offset=d+4,strides=(4096,node_bytes,4)).reshape(-1,r)
            coords=np.ndarray((sectors,slots,d),dtype='u1',buffer=data,strides=(4096,node_bytes,1)).reshape(-1,d)
            take=min(sectors*slots,n-count); degrees=degrees[:take];neighbors=neighbors[:take];coords=coords[:take]
            if np.any(degrees<1) or np.any(degrees>r): raise ValueError('Invalid native adjacency degree')
            active=np.arange(r)[None,:]<degrees[:,None]
            if np.any((neighbors>=n)&active): raise ValueError('Out-of-range native graph edge')
            ordered=np.sort(np.where(active,neighbors,n),axis=1)
            if np.any((ordered[:,1:]==ordered[:,:-1]) & (np.arange(r-1)[None,:]<degrees[:,None]-1)):
                raise ValueError('Duplicate native graph edge')
            if not np.array_equal(coords,vectors[count:count+take]):
                raise ValueError('Native disk vector bytes differ from canonical order')
            min_degree=min(min_degree,int(degrees.min()));max_degree=max(max_degree,int(degrees.max()))
            edge_count+=int(degrees.sum());count+=take
    return dict(metadata=list(meta),disk_size_bytes=expected,pq_chunks=32,nodes_checked=count,
                all_coordinates_equal_canonical=True,all_edges_unique_in_range=True,
                min_degree=min_degree,max_degree=max_degree,total_edges=edge_count)


def finalize(root, build_plan='BUILD_PLAN.json'):
    root=Path(root);plan=json.loads((root/build_plan).read_text())
    build_dir=root/plan.get('build_directory','disk_build')
    prefix=Path(plan['prefix']);build=json.loads((build_dir/'manifest.json').read_text())
    if build['exit_code']!=0 or build['guard_failure']:
        raise ValueError('Incomplete/failed build; no native package can be finalized')
    check_diagnostics((build_dir/'stdout.log').read_text()+'\n'+(build_dir/'stderr.log').read_text())
    structure=validate_structure(prefix,plan['argv'][2])
    # Builder uses/deletes its own temporary _mem.index. Copy entry only AFTER success.
    old=Path('/home/irthn/ann-research/indexes/sift10m-paper/sift10m_mem.index')
    copied=[]
    for suffix in ('','.data','.tags'):
        src=Path(str(old)+suffix);dest=Path(str(prefix)+'_mem.index'+suffix)
        if dest.exists():raise FileExistsError('Never overwrite entry destination')
        shutil.copyfile(src,dest)
        if digest(src)!=digest(dest):raise ValueError('Entry copy hash mismatch')
        copied.append(dict(source=str(src),destination=str(dest),sha256=digest(dest)))
    roles={'disk_index':'_disk.index','pq_compressed':'_pq_compressed.bin','pq_pivots':'_pq_pivots.bin',
           'memory_graph':'_mem.index','memory_data':'_mem.index.data','memory_tags':'_mem.index.tags'}
    files=[]
    for role,suffix in roles.items():
        p=Path(str(prefix)+suffix);s=p.stat()
        files.append(dict(role=role,path=str(p.resolve()),size_bytes=s.st_size,mtime_ns=s.st_mtime_ns,sha256=digest(p)))
    manifest=dict(schema='pipeann-paper-native-index-v1',created_at=utc(),package_id=root.name+'_INDEX',
                  logical_dataset='sift10m',N=10000000,D=128,dtype='uint8',metric='l2',index_prefix=str(prefix),
                  input_package_manifest_sha256=plan['index_inputs'][0],source_commit=plan['source_commit'],source_tree=plan['source_tree'],
                  tag_mapping='implicit_identity_no_tag_file',parameters=dict(R=64,L=100,pq_bytes=32,PQ_budget_GiB='0.298023223876953125',M_GiB=8,T=int(plan['argv'][8]),single_file=0),
                  build=build,structure=structure,files=files,entry_copy_mapping=copied,
                  entry_manifest_sha256=plan['entry_manifest_sha256'],build_plan_sha256=digest(root/build_plan),build_log_sha256=digest(build_dir/'stdout.log'))
    out=prefix.parent/'INDEX_PACKAGE.json'
    with out.open('xb') as f:f.write(canonical_bytes(manifest))
    with out.with_suffix('.sha256').open('x') as f:f.write(digest(out)+'  '+out.name+'\n')
    verify_native_package(out,full=True)
    (root/'NATIVE_INDEX_VALIDATION.json').write_bytes(canonical_bytes(structure))
    print(json.dumps(dict(index_package_sha256=digest(out),structure=structure,total_bytes=sum(f['size_bytes'] for f in files))))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--evidence',required=True,type=Path)
    parser.add_argument('--build-plan',default='BUILD_PLAN.json')
    args=parser.parse_args();finalize(args.evidence,args.build_plan)
