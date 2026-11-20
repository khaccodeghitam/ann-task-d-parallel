"""Synthetic mechanism and trace contracts; no private artifacts."""
import json
import os
from pathlib import Path
import random
import struct
import subprocess
import tempfile
import unittest

from research.task_da.h3_overlap import assign, exact_oracle, metrics


class OfflineTests(unittest.TestCase):
    def test_oracle_and_counterexample(self):
        sets = [set(range(20)),set(range(5))|set(range(20,35)),
                set(range(20)),set(range(5,10))|set(range(35,50))]
        seeds = [dict(eligible=list(s),degree=len(s)) for s in sets]
        rr = metrics(sets,assign(seeds,'rr'))
        opt = metrics(sets,exact_oracle(seeds))
        self.assertEqual((rr['max_work'],rr['duplicate']), (40,10))
        self.assertEqual((opt['max_work'],opt['duplicate']), (35,20))

    def test_rank_pair_caps_ties_and_oracle_dominance(self):
        rng = random.Random(555)
        for n in range(1,12):
            seeds=[dict(eligible=rng.sample(range(24),rng.randrange(10)),degree=10) for _ in range(n)]
            sets=[set(s['eligible']) for s in seeds]
            oracle=metrics(sets,exact_oracle(seeds))['max_work']
            for policy in ('rr','degree','eligible','exact_greedy','exact_quartet','signature'):
                a=assign(seeds,policy,[0]*n)
                self.assertEqual(len(a),n)
                self.assertLessEqual(abs(a.count(0)-a.count(1)),1)
                self.assertTrue(all(a[i]!=a[i+1] for i in range(0,n-1,2)))
                self.assertLessEqual(oracle,metrics(sets,a)['max_work'])
            self.assertEqual(assign(seeds,'signature',[0]*n),assign(seeds,'rr'))


@unittest.skipUnless(os.environ.get('TASK_DA_P2_TRACE_EVAL'), 'explicit native trace target required')
class TraceTests(unittest.TestCase):
    def run_fixture(self,n,chain=False):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);rng=random.Random(20261120)
            adj=[[(i+1)%n] if chain else sorted({(i+1)%n,(i+2)%n,rng.randrange(n)}) for i in range(n)]
            (root/'g').write_bytes(struct.pack('<II',n,max(map(len,adj)))+
                struct.pack('<'+'I'*n,*map(len,adj))+b''.join(struct.pack('<'+'I'*len(a),*a) for a in adj))
            for name,rows in [('b',[[rng.random(),rng.random()] for _ in range(n)]),('q',[[.2,.7],[.8,.1]])]:
                (root/name).write_bytes(struct.pack('<II',len(rows),2)+b''.join(struct.pack('<ff',*v) for v in rows))
            outputs=[]
            for label,mode,trace in [('off','OFF',False),('on','ON',False),('trace','ON',True)]:
                cmd=[os.environ['TASK_DA_P2_TRACE_EVAL'],'pipnn',str(root/'g'),str(root/'b'),str(root/'q'),
                    '--beams',str(n),'--k','3','--workers','2','--sync-interval','16','--merge-impl','flat',
                    '--visited-policy','barrier_all_evaled','--frontier-mode','incremental',
                    '--mode',mode,'--out-dir',str(root/label)]+(['--round-trace'] if trace else [])
                r=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
                self.assertEqual(r.returncode,0,r.stderr)
                outputs.append([json.loads(x) for x in (root/label/f'beam_{n}_p2_{mode}.jsonl').read_text().splitlines()])
            for off,on,tr in zip(*outputs):
                self.assertEqual((off['ids'],off['squared_l2']),(on['ids'],on['squared_l2']))
                self.assertEqual((on['ids'],on['squared_l2']),(tr['ids'],tr['squared_l2']))
                timers={'sync_wait_ns','barrier_wait_ns','merge_time_ns','worker_idle_ns'}
                self.assertEqual({k:v for k,v in on['counters'].items() if k not in timers},
                                 {k:v for k,v in tr['counters'].items() if k not in timers})
                self.assertEqual(tr['trace_overflow'],chain)
                if chain:self.assertEqual(len(tr['rounds']),128)
                else:
                    self.assertEqual(len(tr['rounds']),tr['counters']['sync_merge_count'])
                    ev=sum(len(w['evaluated']) for r in tr['rounds'] for w in r['workers'])
                    self.assertEqual(ev+1+len(set(adj[0])-{0}),tr['counters']['distance_evaluations'])
                    for r in tr['rounds']:
                        seeds=sorted(r['seeds'],key=lambda x:x['rank'])
                        self.assertEqual([s['worker'] for s in seeds],[i%2 for i in range(len(seeds))])
                        self.assertTrue(all(set(s['eligible'])<=set(adj[s['id']]) for s in seeds))
                        self.assertLessEqual(r['release_ns'],r['arrived_ns'])
                        self.assertLessEqual(r['arrived_ns'],r['end_ns'])

    def test_parity_and_trace_reconciliation(self):self.run_fixture(80)
    def test_overflow_finishes_search_and_retains_outputs(self):self.run_fixture(2300,True)
