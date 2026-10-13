#!/usr/bin/env python3
"""Minimal portable entrypoint. No command silently builds or downloads an index."""
import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile

REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO/'tools/research'))
from artifact_bundle import verify,copy_bundle
from paper_paired_campaign import resolved,schedule,argv,run_campaign,summarize
from paper_rebaseline import canonical_bytes,digest


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['preflight','verify','copy-bundle','campaign','summarize','smoke','quality-build','build-source','build-index'])
    p.add_argument('--config',type=Path,default=REPO/'configs/paper_campaign.json');p.add_argument('--output',type=Path)
    p.add_argument('--dry-run',action='store_true');p.add_argument('--full',action='store_true');p.add_argument('--core-only',action='store_true')
    a=p.parse_args()
    if a.command=='summarize':
        if not a.output:p.error('--output CAMPAIGN required')
        print(json.dumps(summarize(a.output),indent=2));return
    c=resolved(json.loads(a.config.read_text()));c['manifest']=str((REPO/c['manifest']).resolve())
    if a.core_only:c['extension']=False
    if a.command=='campaign':
        rows=schedule(c.get('seed',20261013),c.get('extension',True))
        if a.dry_run:
            print(json.dumps(dict(core=18,optional=18 if c.get('extension',True) else 0,monitor='same rich1Hz guard/watchdog for all main runs',raw_space_budget_MiB=256,order=[dict(r,argv=argv(c,r)) for r in rows]),indent=2));return
        if not a.output:p.error('--output NEW_DIRECTORY required')
        run_campaign(c,a.output);return
    if a.command=='preflight':
        tools={n:shutil.which(n) for n in ['git','cmake','g++','make','patch']}
        paths={k:dict(path=c[k],exists=Path(c[k]).exists()) for k in ['binary','subject_repo','data_root','index_root','quality_binary']}
        print(json.dumps(dict(platform=sys.platform,tools=tools,paths=paths,no_automatic_install=True),indent=2));return
    if a.command=='verify':print(json.dumps(verify(c['manifest'],c['data_root'],c['index_root'],a.full),indent=2));return
    if a.command=='copy-bundle':
        if not a.output:p.error('--output ABSENT_TRANSFER_DIRECTORY required')
        print(json.dumps(copy_bundle(c['manifest'],c['data_root'],c['index_root'],a.output)));return
    if a.command=='quality-build':
        subject=Path(c['subject_repo']);out=a.output
        if out is None:p.error('--output NEW_PROBE_DIRECTORY required')
        flags=subject/'build/tests/CMakeFiles/search_disk_index.dir/flags.make';link=subject/'build/tests/CMakeFiles/search_disk_index.dir/link.txt'
        cmds=['copy original driver','apply patches/quality-export.patch','compile using existing subject flags/link recipe']
        if a.dry_run:print(json.dumps(cmds));return
        out.mkdir(parents=True,exist_ok=False);src=out/'quality_driver.cpp';shutil.copyfile(subject/'tests/search_disk_index.cpp',src)
        subprocess.run(['patch',str(src),str(REPO/'patches/quality-export.patch')],check=True)
        values=dict(line.split(' = ',1) for line in flags.read_text().splitlines() if line.startswith(('CXX_DEFINES =','CXX_INCLUDES =')))
        cmd=shlex.split(link.read_text());cmd[cmd.index('-o')+1]=str((out/'quality_search').resolve())
        for i,x in enumerate(cmd):
            if x.endswith('search_disk_index.cpp.o'):cmd[i]=str(src.resolve())
        cmd[1:1]=shlex.split(values['CXX_DEFINES']+' '+values['CXX_INCLUDES'])
        subprocess.run(cmd,cwd=subject/'build/tests',check=True)
        print(json.dumps(dict(binary=str(out/'quality_search'),sha256=digest(out/'quality_search'))));return
    if a.command=='build-source':
        original=Path(c['stock_source']);portable=Path(c['subject_repo'])
        cmds=[['git','clone','https://github.com/thustorage/PipeANN.git',str(original)],['git','-C',str(original),'checkout','--detach','d18dcd16fece1c9d1dea356d783ebba2ed649e54'],['git','clone',str(original),str(portable)],['git','-C',str(portable),'checkout','--detach','d18dcd16fece1c9d1dea356d783ebba2ed649e54'],['git','-C',str(portable),'apply',str(REPO/'patches/gcc13-portability.patch')],['git','-C',str(portable),'add','src/distance.cpp'],['git','-C',str(portable),'commit','-m','artifact: GCC13 AVX2 horizontal reduction portability'],['./configure'],['make','library','-j2'],['cmake','-S',str(portable),'-B',str(portable/'build')],['cmake','--build',str(portable/'build'),'--target','search_disk_index','build_disk_index','build_memory_index','gen_random_slice','-j2']]
        if a.dry_run:print(json.dumps(cmds,indent=2));return
        if original.exists() or portable.exists():raise FileExistsError('Source destinations must both be absent; preserve existing clones')
        for i,cmd in enumerate(cmds):
            cwd=portable/'third_party/liburing' if i in (7,8) else REPO
            env=dict(os.environ,ADDITIONAL_DEFINITIONS='-DDYN_PIPE_WIDTH')
            subprocess.run(cmd,cwd=cwd,env=env,check=True)
        print(json.dumps(dict(search_sha256=digest(c['binary']))));return
    if a.command=='build-index':
        if a.output is None:p.error('--output NEW_INDEX_DIRECTORY required')
        prefix=a.output/'sift10m';cmd=[str(Path(c['subject_repo'])/'build/tests/build_disk_index'),'uint8',str(Path(c['data_root'])/'base_10m.bbin'),str(prefix),'64','100','0.298023223876953125','8','8','l2','0']
        if a.dry_run:print(shlex.join(cmd));return
        if a.output.exists():raise FileExistsError('Never overwrite existing index directory')
        # Explicit long operation only; entry construction is documented separately.
        from run_paper_fullfan_check import run
        a.output.mkdir(parents=True)
        result=run(dict(argv=cmd,binary_sha256=digest(cmd[0]),threads=8,timeout_s=7200),a.output/'build_evidence')
        if result['exit_code'] or result['guard_failure']:raise ValueError('Build incomplete; preserve outputs, no automatic retry')
        print('Disk build done. Validate structure and provision matching memory entry before search.');return
    if a.command=='smoke':
        if not a.output:p.error('--output NEW_SMOKE_DIRECTORY required')
        if a.dry_run:print(json.dumps(dict(queries=32,binary=c['quality_binary'],builds_index=False)));return
        verify(c['manifest'],c['data_root'],c['index_root'],a.full)
        if not Path(c['quality_binary']).is_file():raise ValueError('Separate quality probe missing; explicitly run quality-build first')
        import struct
        import numpy as np
        from run_paper_fullfan_check import run
        from paper_native_v3 import quality_against_canonical,check_diagnostics
        a.output.mkdir(parents=True,exist_ok=False);b=Path(c['data_root']);n=32
        query=a.output/'query.bbin';truth=a.output/'gt.bin'
        with (b/'query.bbin').open('rb') as f:f.seek(8);query.write_bytes(struct.pack('<II',n,128)+f.read(n*128))
        ids=np.memmap(b/'gt_10m.bin',mode='r',dtype='<u4',offset=8,shape=(10000,100));ds=np.memmap(b/'gt_10m.bin',mode='r',dtype='<f4',offset=4000008,shape=(10000,100))
        truth.write_bytes(struct.pack('<II',n,100)+ids[:n].tobytes()+ds[:n].tobytes());out=a.output/'results.csv';row=dict(T=8,W=32,L=100)
        result=run(dict(argv=argv(c,row,c['quality_binary'],query,truth),threads=8,binary_sha256=digest(c['quality_binary']),timeout_s=120,extra_environment={'PAPER_QUALITY_OUTPUT':str(out)}),a.output/'run')
        if result['exit_code'] or result['guard_failure']:raise ValueError('Smoke process failed')
        check_diagnostics((a.output/'run/stdout.log').read_text()+(a.output/'run/stderr.log').read_text())
        print(json.dumps(quality_against_canonical(out,b/'base_10m.bbin',query,truth,query_count=n),indent=2))


if __name__=='__main__':
    try:main()
    except (ValueError,OSError,KeyError) as e:raise SystemExit(str(e))
