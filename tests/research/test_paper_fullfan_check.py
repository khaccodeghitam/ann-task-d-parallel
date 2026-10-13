import copy
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'tools/research'))
from run_paper_fullfan_check import CoolingGuard, start_ticks, watchdog


def sample(t=0, temp=40):
    return dict(monotonic_s=t, sensors={'package':dict(value_C=temp,name='coretemp',label='Package id 0',critical_mC='100000')},
                power={'AC':'1'},mem_available=8*2**30,free_disk=60*2**30,swap_used=0,ann=[],rapl={'PL1':'60000000'})


class CoolingTests(unittest.TestCase):
    def test_guard_boundary_and_policy(self):
        s=sample();g=CoolingGuard(s);s['rapl']['PL1']='115000000'
        self.assertEqual(g.check(s),[])
        self.assertEqual(g.check(sample(1,98)),[])
        self.assertIn('Package temperature >=99C',g.check(sample(2,99)))

    def test_sustained_and_reset(self):
        g=CoolingGuard(sample());self.assertEqual(g.check(sample(1,97)),[])
        self.assertEqual(g.check(sample(10.9,97)),[])
        self.assertTrue(g.check(sample(11,97)))
        self.assertEqual(g.check(sample(12,96)),[])
        self.assertEqual(g.check(sample(13,97)),[])

    def test_unavailable_and_critical(self):
        s=sample();g=CoolingGuard(s);s=copy.deepcopy(s);s['sensors']={}
        self.assertTrue(g.check(s));self.assertTrue(g.check(sample(temp=100)))

    def test_resource_ac_and_foreign(self):
        for key,val in [('power',{'AC':'0'}),('mem_available',2**30),('free_disk',20*2**30),('ann',[{'pid':42}])]:
            s=sample();g=CoolingGuard(copy.deepcopy(s));s[key]=val;self.assertTrue(g.check(s))
        s=sample();s['ann']=[{'pid':42}];self.assertEqual(CoolingGuard(sample()).check(s,42),[])

    def test_swap(self):
        g=CoolingGuard(sample());s=sample(1);s['swap_used']=65*2**20
        self.assertEqual(g.check(s),[]);s['monotonic_s']=11;self.assertTrue(g.check(s))

    def test_watchdog_eof_terminates_owned_process_group(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)'],start_new_session=True)
            rd,wr=os.pipe();ticks=start_ticks(p.pid);pid=os.fork()
            if pid==0:
                try:watchdog(rd,wr,p.pid,ticks,Path(tmp)/'failure.json')
                finally:os._exit(0)
            os.close(rd);os.close(wr)
            try:
                self.assertEqual(p.wait(timeout=3),-signal.SIGTERM)
                os.waitpid(pid,0)
                self.assertEqual(json.loads((Path(tmp)/'failure.json').read_text())['owned_pid'],p.pid)
            finally:
                if p.poll() is None:p.kill();p.wait()

    def test_watchdog_done_does_not_kill(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)'],start_new_session=True)
            rd,wr=os.pipe();ticks=start_ticks(p.pid);pid=os.fork()
            if pid==0:
                try:watchdog(rd,wr,p.pid,ticks,Path(tmp)/'failure.json')
                finally:os._exit(0)
            os.close(rd);os.write(wr,b'DONE');os.close(wr);os.waitpid(pid,0)
            try:self.assertIsNone(p.poll());self.assertFalse((Path(tmp)/'failure.json').exists())
            finally:p.terminate();p.wait()


if __name__=='__main__':unittest.main()
