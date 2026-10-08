#!/usr/bin/env python3
"""Convert a verified retained BIGANN prefix using canonical PipeANN change_pts."""
import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
import struct
import subprocess
import sys
from package_manifest import digest_file, finalize
from acquire_bigann_prefix import SOURCES


def prepare(root,subject):
    root=Path(root).expanduser().resolve();subject=Path(subject).expanduser().resolve()
    canonical=root/'canonical';canonical.mkdir(exist_ok=True)
    output=root/'manifests/INPUT_PACKAGE.json'
    if output.exists() or output.with_suffix('.sha256').exists(): raise FileExistsError('Input package already exists')
    tool=subject/'build/tests/utils/change_pts'
    commit=subprocess.check_output(['git','-C',str(subject),'rev-parse','HEAD'],text=True).strip()
    if commit!='b9ec4ba86ff5d70bec277984777197f28dc2cf42' or subprocess.check_output(['git','-C',str(subject),'status','--porcelain'],text=True).strip():
        raise ValueError('Expected clean canonical subject b9ec4ba')
    provenance=[];conversions=[];entries=[]
    for role,(name,total,size,shape) in SOURCES.items():
        source=root/'source'/(name.rsplit('/',1)[-1]+('.first10M' if role=='base' else ''))
        record=json.loads(source.with_name(source.name+'.acquisition.json').read_text())
        if source.stat().st_size!=size or record['size_bytes']!=size or record['path']!=str(source): raise ValueError('Acquisition size/path mismatch')
        with source.open('rb') as stream:
            if struct.unpack('<II',stream.read(8))!=shape: raise ValueError('Acquisition header mismatch')
        # Acquisition computed each source hash while receiving; source remains untouched.
        provenance.append(record)
        target=canonical/{'base':'base_10m.bbin','query':'query.bbin','ground_truth':'gt_10m.bin'}[role]
        if target.exists(): raise FileExistsError(str(target))
        if role=='base':
            generated=Path(str(source)+'10000000')
            if generated.exists(): raise FileExistsError(str(generated))
            argv=[str(tool),'uint8',str(source),'10000000']
            with (root/'manifests/conversion.log').open('x') as log:
                subprocess.run(argv,stdout=log,stderr=subprocess.STDOUT,check=True)
            if generated.stat().st_size!=1280000008: raise ValueError('Canonical utility output size mismatch')
            os.link(generated,target);generated.unlink() # move only our newly generated file
            conversions.append({'role':role,'exact_command':shlex.join(argv),'tool_path':str(tool),'tool_repo':str(subject),
                                'tool_commit':commit,'tool_binary_sha256':digest_file(tool)})
        else:
            with source.open('rb') as inp,target.open('xb') as out:
                shutil.copyfileobj(inp,out,4*1024*1024);out.flush();os.fsync(out.fileno())
            conversions.append({'role':role,'method':'Native-format identity copy; IDs then distances unchanged',
                'exact_command':shlex.join([sys.executable,str(Path(__file__).resolve()),'--root',str(root),'--subject-repo',str(subject)]),
                'tool_path':str(Path(__file__).resolve()),'tool_repo':str(Path(__file__).resolve().parents[2]),
                'tool_commit':subprocess.check_output(['git','-C',str(Path(__file__).resolve().parents[2]),'rev-parse','HEAD'],text=True).strip(),
                'tool_git_dirty':True,'tool_source_sha256':digest_file(__file__)})
        item={'role':role,'path':str(target),'vector_count':10000000 if role=='base' else 10000,
              'dtype':'uint32_ids_float32_distances' if role=='ground_truth' else 'uint8'}
        item['top_k' if role=='ground_truth' else 'dimension']=100 if role=='ground_truth' else 128
        entries.append(item)
    provenance.append({'source_spec_repo':'https://github.com/harsha-simhadri/big-ann-benchmarks',
                       'source_spec_commit':'89a3abaafa63dda46b94b308bdf039e699841b3b',
                       'source_spec_path':'benchmark/datasets.py','ordering':'first 10,000,000 vectors of canonical BIGANN base',
                       'original_family':'ANN_SIFT1B / TexMex; official mirror native format equivalent'})
    spec={'package_kind':'input','package_id':'bigann-sift10m-uint8-l2-v1','logical_dataset':'sift10m','N':10000000,'D':128,
          'dtype':'uint8','metric':'l2','files':entries,'source_provenance':provenance,'conversion':conversions}
    digest=finalize(spec,output)
    for entry in entries: Path(entry['path']).chmod(0o444)
    output.chmod(0o444);output.with_suffix('.sha256').chmod(0o444)
    print(json.dumps({'manifest':str(output),'sha256':digest}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',required=True);p.add_argument('--subject-repo',required=True)
    args=p.parse_args();prepare(args.root,args.subject_repo)
