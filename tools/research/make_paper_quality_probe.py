#!/usr/bin/env python3
"""Build a separately identified driver-only post-timer correctness exporter.

Links the actual unchanged subject library. Never used for headline stock QPS.
Captures actual pipe_search return count, result IDs/distances and query stats.
"""
import argparse
import json
from pathlib import Path
import shlex
import subprocess


def instrument(source):
    anchor='    std::vector<uint64_t> query_result_tags_64(recall_at * query_num);'
    assert source.count(anchor)==1
    source='#include <fstream>\n#include <cstdlib>\n#include <cmath>\n'+source
    source=source.replace(anchor, '    std::vector<size_t> quality_count(query_num);\n'+anchor)
    call='_pFlashIndex->pipe_search(query + (i * query_dim)'
    assert source.count(call)==1
    source=source.replace(call, 'quality_count[i] = '+call)
    anchor='    delete[] stats;'
    assert source.count(anchor)==1
    export=r'''
    if (output && std::getenv("PAPER_QUALITY_OUTPUT")) {
      std::ofstream quality(std::getenv("PAPER_QUALITY_OUTPUT"));
      quality << "query_id,returned,rank,node_id,distance,latency_us,io_count\n";
      quality.precision(12);
      for(size_t qi=0; qi<query_num; qi++) {
        for(size_t rank=0; rank<recall_at; rank++) {
          quality << qi << ',' << quality_count[qi] << ',' << rank << ','
                  << query_result_tags_32[qi*recall_at+rank] << ','
                  << query_result_dists[test_id][qi*recall_at+rank] << ','
                  << stats[qi].total_us << ',' << stats[qi].n_ios << '\n';
        }
      }
      if(!quality) std::abort();
    }
'''
    return source.replace(anchor,export+anchor)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--subject',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    src=a.subject/'tests/search_disk_index.cpp'
    probe=a.output/'quality_driver.cpp';probe.write_text(instrument(src.read_text()))
    commands=json.loads((a.subject/'build/compile_commands.json').read_text())
    entry=next(x for x in commands if Path(x['file'])==src)
    flags=shlex.split(entry['command']);out=[];i=0
    while i<len(flags):
        if flags[i] in ('-o','-c'): i+=2;continue
        out.append(flags[i]);i+=1
    link=shlex.split((a.subject/'build/tests/CMakeFiles/search_disk_index.dir/link.txt').read_text())
    libs=link[link.index('-o')+2:]
    command=out+[str(probe),'-o',str(a.output/'quality_search'),*libs]
    result=subprocess.run(command,cwd=a.subject/'build/tests',capture_output=True,text=True)
    (a.output/'build.stdout').write_text(result.stdout);(a.output/'build.stderr').write_text(result.stderr)
    (a.output/'build.json').write_text(json.dumps(dict(argv=command,exit_code=result.returncode),indent=2))
    if result.returncode: raise SystemExit(result.returncode)


if __name__=='__main__': main()
