#!/usr/bin/env python3
"""Validate canonical b9ec4ba Vamana/PQ layout, then freeze a SIFT10M index package."""
import argparse
import json
from pathlib import Path
import struct
from package_manifest import digest_file, finalize, load_verified


def validate_index(prefix,n,dimension,degree,pq_bytes):
    prefix=Path(prefix).expanduser().resolve()
    files={role:Path(str(prefix)+suffix) for role,suffix in {
        'disk_index':'_disk.index','tags':'_disk.index.tags',
        'pq_compressed':'_pq_compressed.bin','pq_pivots':'_pq_pivots.bin'}.items()}
    if any(not p.is_file() or p.stat().st_size==0 for p in files.values()): raise ValueError('Required index component missing/empty')
    with files['disk_index'].open('rb') as stream:
        raw=stream.read(80)
    if len(raw)!=80: raise ValueError('Truncated disk metadata')
    nr,nc,*values=struct.unpack('<II9Q',raw)
    npoints,d,entry,node_len,nodes_sector,shard_n,attr,stored_degree,r_ood=values
    if (nr,nc,npoints,d,shard_n,attr,stored_degree,r_ood)!=(9,1,n,dimension,n,0,degree,0) or entry>=n:
        raise ValueError('Unexpected canonical disk metadata')
    expected_len=dimension+4*(degree+1)
    if node_len!=expected_len or nodes_sector!=4096//node_len: raise ValueError('Disk node/sector layout mismatch')
    expected_size=4096*(1+(n+nodes_sector-1)//nodes_sector)
    if files['disk_index'].stat().st_size!=expected_size: raise ValueError('Disk index size mismatch')
    for role,shape,size in (('tags',(n,1),8+n*4),('pq_compressed',(n,pq_bytes),8+n*pq_bytes)):
        with files[role].open('rb') as stream:
            if stream.read(8)!=struct.pack('<II',*shape) or files[role].stat().st_size!=size:
                raise ValueError('Index component shape/size mismatch: '+role)
            if role=='tags':
                for start in range(0,n,65536):
                    block=stream.read(min(65536,n-start)*4)
                    if any(id_!=start+i for i,(id_,) in enumerate(struct.iter_unpack('<I',block))):
                        raise ValueError('Canonical identity tags mismatch')
    pivot=files['pq_pivots']
    with pivot.open('rb') as stream:
        if stream.read(8)!=struct.pack('<II',5,1): raise ValueError('PQ offset header mismatch')
        offsets=struct.unpack('<5Q',stream.read(40))
        if offsets[0]!=4096 or offsets[-1]!=pivot.stat().st_size: raise ValueError('PQ offsets/file size mismatch')
        shapes=((256,dimension),(dimension,1),(dimension,1),(pq_bytes+1,1))
        for i,(rows,cols) in enumerate(shapes):
            stream.seek(offsets[i])
            if stream.read(8)!=struct.pack('<II',rows,cols) or offsets[i+1]-offsets[i]!=8+rows*cols*4:
                raise ValueError('PQ pivot block shape/offset mismatch')
            if i==3:
                chunks=struct.unpack('<'+str(rows)+'I',stream.read(rows*4))
                if chunks[0]!=0 or chunks[-1]!=dimension or any(a>=b for a,b in zip(chunks,chunks[1:])):
                    raise ValueError('PQ dimension partition mismatch')
    return files,{'disk_metadata':dict(zip(('npoints','dimension','entry_point','max_node_len','nodes_per_sector','shard_n','attr_size','range','R_ood'),values)),
                  'expected_disk_size_bytes':expected_size,'identity_tags_valid':True,'pq_offsets':list(offsets),'pq_structure_valid':True}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input-package-manifest',required=True)
    p.add_argument('--build-metadata',required=True);p.add_argument('--output',required=True)
    args=p.parse_args();input_,input_digest=load_verified(args.input_package_manifest,'input')
    build=json.loads(Path(args.build_metadata).read_text());argv=build['argv']
    if build.get('exit_code')!=0 or build.get('failure_reason'): raise ValueError('Build did not complete successfully')
    if len(argv)!=11 or argv[1]!='uint8' or argv[9:]!=['l2','pq']: raise ValueError('Unexpected canonical Vamana argv')
    if argv[2]!=next(e['path'] for e in input_['files'] if e['role']=='base'): raise ValueError('Builder base differs from input package')
    r,l,pq,m,t=map(int,argv[4:9]);files,validation=validate_index(argv[3],input_['N'],input_['D'],r,pq)
    build['log_sha256']=digest_file(build['log_path'])
    build['validation']=validation
    components=[{'role':role,'path':str(path),'dtype':{'disk_index':'uint8_vectors_uint32_edges','tags':'uint32','pq_compressed':'uint8_pq_codes','pq_pivots':'mixed_pq_tables'}[role]} for role,path in files.items()]
    # Retain/hash any extra final components too; do not silently omit builder outputs.
    known=set(files.values())
    for path in sorted(Path(argv[3]).parent.glob(Path(argv[3]).name+'_*')):
        if path.is_file() and path not in known: components.append({'role':'extra_'+path.name,'path':str(path),'dtype':'opaque'})
    spec={'package_kind':'index','package_id':f"bigann-sift10m-vamana-R{r}-L{l}-PQ{pq}-v1",
          **{key:input_[key] for key in ('logical_dataset','N','D','dtype','metric')},
          'input_package_manifest_sha256':input_digest,'input_package_manifest_path':str(Path(args.input_package_manifest).resolve()),
          'index_prefix':argv[3],'parameters':{'R':r,'L':l,'pq_bytes':pq,'memory_budget_GiB':m,'threads':t,'metric':'l2','neighbor_type':'pq','algorithm':'Vamana'},
          'build':build,'files':components}
    digest=finalize(spec,args.output)
    # Canonical reader opens disk index O_RDWR even for search; keep owner-write.
    # Immutability is a content contract, not an incompatible chmod guarantee.
    for entry in components:
        Path(entry['path']).chmod(0o644 if entry['role'] == 'disk_index' else 0o444)
    output=Path(args.output);output.chmod(0o444);output.with_suffix('.sha256').chmod(0o444)
    print(json.dumps({'index_package_manifest_sha256':digest,'validation':validation},indent=2))

if __name__=='__main__':main()
