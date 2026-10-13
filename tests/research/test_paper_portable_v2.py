import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS=Path(__file__).resolve().parents[2]/'tools/research'
sys.path.insert(0,str(TOOLS))
from paper_portable_v2 import Guard, seal, validate_quality, execute
from make_paper_quality_probe import instrument
from paper_rebaseline import digest, search_argv, run_order, parse_output, paired


def state():
    return dict(mem_available=4*2**30,free_disk=40*2**30,power={'AC':'1'},rapl={'PL1':'115'},
                ann=[],sensors={},monotonic_s=0,swap_used=0)


class PortableV2Tests(unittest.TestCase):
    def test_native_cli_mem10(self):
        c=run_order()[0]
        self.assertEqual(search_argv('bin','idx','query','gt',c,10),
                         ['bin','uint8','idx','1','32','query','gt','10','l2','2','10','100'])

    def test_modern_cli_mem10(self):
        c=next(x for x in run_order() if x['version']=='MODERN')
        self.assertEqual(search_argv('bin','idx','query','gt',c,10)[8:],['l2','pq','2','10','100'])

    def test_balanced66(self):
        rows=run_order();self.assertEqual(len(rows),66)
        for block in range(1,7):
            self.assertEqual(len({x['cell'] for x in rows if x['stage']=='primary' and x['block']==block}),6)

    def test_guard_safe(self): self.assertEqual(Guard(state()).check(state()),[])
    def test_guard_memory(self):
        s=state();s['mem_available']=2**30
        self.assertTrue(Guard(state()).check(s))
    def test_guard_disk(self):
        s=state();s['free_disk']=20*2**30
        self.assertTrue(Guard(state()).check(s))
    def test_guard_power(self):
        s=state();s['power']['AC']='0'
        self.assertTrue(Guard(state()).check(s))
    def test_guard_rapl(self):
        s=state();s['rapl']['PL1']='1'
        self.assertTrue(Guard(state()).check(s))
    def test_owned_vs_foreign(self):
        s=state();s['ann']=[{'pid':42}]
        self.assertEqual(Guard(state()).check(s,42),[])
        self.assertTrue(Guard(state()).check(s,41))
    def test_sustained_thermal(self):
        s=state();s['sensors']={'p':{'name':'coretemp','label':'Package id 0','value_C':98,'critical_mC':None}}
        g=Guard(state());self.assertEqual(g.check(s),[])
        s['monotonic_s']=10;self.assertTrue(g.check(s))
    def test_transient_thermal(self):
        s=state();g=Guard(s)
        s['sensors']={'p':{'name':'coretemp','label':'Package id 0','value_C':98,'critical_mC':None}}
        g.check(s);s['sensors']={};s['monotonic_s']=10
        self.assertEqual(g.check(s),[])
    def test_immediate_critical_proximity(self):
        s=state();s['sensors']={'p':{'name':'coretemp','label':'Core 0','value_C':98,'critical_mC':'100000'}}
        self.assertTrue(Guard(state()).check(s))
    def test_sustained_swap(self):
        s=state();s['swap_used']=65*2**20;g=Guard(state());self.assertEqual(g.check(s),[])
        s['monotonic_s']=10;self.assertTrue(g.check(s))
    def test_seal_detects_change(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'data';p.write_text('before');seal(d)
            before=(Path(d)/'SHA256SUMS').read_text().split()[0]
            self.assertEqual(digest(p),before);p.write_text('after');self.assertNotEqual(digest(p),before)
    def test_quality_hook_not_hot_serialization(self):
        s='    std::vector<uint64_t> query_result_tags_64(recall_at * query_num);\n_pFlashIndex->pipe_search(query + (i * query_dim), args);\n    delete[] stats;'
        out=instrument(s)
        self.assertEqual(out.count('_pFlashIndex->pipe_search('),1)
        self.assertIn('quality_count[i] = ',out)
        self.assertLess(out.index('quality.precision'),out.index('delete[] stats'))
    def test_bad_source_fails_closed(self):
        with self.assertRaises(AssertionError):instrument('different driver')
    def test_tail_mapping(self):
        s='100 32 4000 1900 3000 0 120 95'
        self.assertIsNone(parse_output(s,'PAPER',100,32)['p99_latency_us'])
        self.assertIsNone(parse_output(s,'MODERN',100,32)['p999_latency_us'])
    def test_read_error_even_exit0_rejected(self):
        with self.assertRaises(ValueError):parse_output('ERROR EBADF\n100 32 4000 1900 3000 0 120 95','PAPER',100,32)
    def test_deterministic_block_bootstrap(self):
        a=paired([90,91,92,93,94,95],[100]*6,samples=100)
        self.assertEqual(a,paired([90,91,92,93,94,95],[100]*6,samples=100))
    def quality_fixture(self, rows):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
        p=Path(tmp.name)/'quality.csv'
        p.write_text('query_id,returned,rank,node_id,distance,latency_us,io_count\n'+rows)
        return p
    def test_quality_complete(self):
        p=self.quality_fixture('0,2,0,5,1,10,2\n0,2,1,6,2,10,2\n')
        self.assertEqual(validate_quality(p,1,2,10)['rows'],2)
    def test_quality_duplicate(self):
        p=self.quality_fixture('0,2,0,5,1,10,2\n0,2,1,5,2,10,2\n')
        with self.assertRaises(ValueError):validate_quality(p,1,2,10)
    def test_quality_nonfinite(self):
        p=self.quality_fixture('0,2,0,5,nan,10,2\n0,2,1,6,2,10,2\n')
        with self.assertRaises(ValueError):validate_quality(p,1,2,10)
    def test_quality_missing(self):
        p=self.quality_fixture('0,2,0,5,1,10,2\n')
        with self.assertRaises(ValueError):validate_quality(p,1,2,10)
    def test_quality_actual_return_not_k(self):
        p=self.quality_fixture('0,1,0,5,1,10,2\n0,1,1,6,2,10,2\n')
        with self.assertRaises(ValueError):validate_quality(p,1,2,10)
    def test_fake_execute_and_environment(self):
        # No real ANN or sysstat process is invoked in this synthetic test.
        with tempfile.TemporaryDirectory() as t:
            s=state();s['tasks']=[]
            class FakeTelemetry:
                def __init__(self,*a):pass
                def start(self,pid):pass
                def stop(self):pass
            with patch('paper_portable_v2.host_snapshot',return_value=s),patch('paper_portable_v2.Telemetry',FakeTelemetry):
                with patch.dict('os.environ',{'OMP_PROC_BIND':'spread','OMP_PLACES':'threads','GOMP_CPU_AFFINITY':'0-7'}):
                    out=Path(t)/'run'
                    result=execute(dict(argv=[sys.executable,'-c','import os;print(os.environ.get("OMP_PROC_BIND"))'],threads=8),out,s)
                self.assertEqual(result['exit_code'],0)
                self.assertEqual((out/'stdout.log').read_text().strip(),'None')
                self.assertIsNone(result['environment']['OMP_PLACES'])
    def test_failed_process_preserved(self):
        with tempfile.TemporaryDirectory() as t:
            s=state();s['tasks']=[]
            class FakeTelemetry:
                def __init__(self,*a):pass
                def start(self,pid):pass
                def stop(self):pass
            out=Path(t)/'failure'
            with patch('paper_portable_v2.host_snapshot',return_value=s),patch('paper_portable_v2.Telemetry',FakeTelemetry):
                with self.assertRaises(ValueError):execute(dict(argv=[sys.executable,'-c','print("kept");raise SystemExit(1)']),out,s)
            self.assertEqual(json.loads((out/'manifest.json').read_text())['exit_code'],1)
            self.assertEqual((out/'stdout.log').read_text().strip(),'kept')


if __name__=='__main__':unittest.main()
