"""Explicit opt-in synthetic correctness/conservation for the copy-only observer."""
import json
import os
from pathlib import Path
import random
import struct
import subprocess
import tempfile
import unittest


@unittest.skipUnless(os.environ.get('TASK_DA_PHASE_EVAL') and os.environ.get('TASK_DA_P2_EVAL'),
                     'explicit native observer and frozen reference required')
class PhaseObserverTest(unittest.TestCase):
    def test_exact_output_logical_counters_and_phase_conservation(self):
        rng = random.Random(20261120)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);n=96
            adj=[sorted({(i+1)%n,(i+5)%n,rng.randrange(n)}) for i in range(n)]
            (root/'g').write_bytes(struct.pack('<II',n,max(map(len,adj)))+
                struct.pack('<'+'I'*n,*map(len,adj))+b''.join(struct.pack('<'+'I'*len(a),*a) for a in adj))
            for name,rows in [('b',[[rng.random() for _ in range(3)] for _ in range(n)]),
                              ('q',[[rng.random() for _ in range(3)] for _ in range(8)])]:
                (root/name).write_bytes(struct.pack('<II',len(rows),3)+b''.join(struct.pack('<fff',*v) for v in rows))
            outputs={}
            for label,binary in [('ref',os.environ['TASK_DA_P2_EVAL']),('phase',os.environ['TASK_DA_PHASE_EVAL'])]:
                for mode in ('OFF','ON'):
                    out=root/f'{label}_{mode}'
                    argv=[binary,'pipnn',str(root/'g'),str(root/'b'),str(root/'q'),'--beams','64',
                        '--k','10','--workers','2','--sync-interval','16','--merge-impl','flat',
                        '--visited-policy','barrier_all_evaled','--frontier-mode','incremental',
                        '--mode',mode,'--out-dir',str(out)]
                    r=subprocess.run(argv,capture_output=True,text=True,timeout=30)
                    self.assertEqual(r.returncode,0,r.stderr)
                    outputs[label,mode]=[json.loads(x) for x in (out/f'beam_64_p2_{mode}.jsonl').read_text().splitlines()]
            ref=outputs['ref','OFF']
            for rows in outputs.values():
                self.assertEqual([(r['ids'],r['squared_l2']) for r in rows],[(r['ids'],r['squared_l2']) for r in ref])
            timers={'sync_wait_ns','barrier_wait_ns','merge_time_ns','worker_idle_ns'}
            for a,b in zip(outputs['ref','ON'],outputs['phase','ON']):
                self.assertEqual({k:v for k,v in a['counters'].items() if k not in timers},
                                 {k:v for k,v in b['counters'].items() if k not in timers})
            for mode in ('OFF','ON'):
                for r in outputs['phase',mode]:
                    p=r['phase_audit']
                    self.assertGreater(p['rounds'],0)
                    self.assertLessEqual(sum(p[k] for k in ('worker_phase_ns','gather_publish_ns','frontier_dispatch_ns')),r['latency_ns'])
                    self.assertLessEqual(p['arrival_tail_ns'],p['worker_phase_ns'])
                    self.assertLessEqual(p['imbalance_ns'],p['ideal_balance_ns'])
                    self.assertLessEqual(p['worker_duration_sum_ns'],2*p['worker_duration_max_ns'])
                    if mode=='ON':self.assertEqual(p['rounds'],r['counters']['sync_merge_count'])


if __name__=='__main__':unittest.main()
