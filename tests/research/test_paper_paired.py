import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/research'))
from artifact_bundle import components,verify,PAPER
from paper_paired_campaign import schedule,resolved,argv,paired_statistics,percentile
from paper_rebaseline import parse_output

class PairedTests(unittest.TestCase):
 def test_schedule(self):
  a=schedule();self.assertEqual(a,schedule());self.assertEqual(len(a),36)
  core=a[:18];self.assertEqual(sum(r['T']==1 for r in core),3);self.assertEqual(sum(r['T']==4 for r in core),3)
  order=[]
  for b in range(1,7):
   p=[r['T'] for r in core if r['stage']=='core' and r['block']==b];self.assertEqual(set(p),{8,16});order.append(p)
  self.assertEqual(sum(p==[8,16] for p in order),3);self.assertEqual(len(schedule(extension=False)),18)
  self.assertEqual(sum(r['stage']=='extension_L' for r in a),12)
 def test_native_argv(self):
  c=dict(binary='search',index_root='index with spaces',data_root='data',prefix='sift10m')
  self.assertEqual(argv(c,dict(T=8,W=32,L=100)),['search','uint8','index with spaces/sift10m','8','32','data/query.bbin','data/gt_10m.bin','10','l2','2','10','100'])
 def test_env_missing(self):
  with patch.dict('os.environ',{},clear=True):
   with self.assertRaises(ValueError):resolved({'binary':'${UNSET}/x'})
 def test_bootstrap(self):
  a=paired_statistics([-10,-9,-8,-7,-6,-5]);self.assertEqual(a,paired_statistics([-10,-9,-8,-7,-6,-5]));self.assertEqual(a['median'],-7.5);self.assertLess(a['CI90'][1],0)
  with self.assertRaises(ValueError):paired_statistics([1,2])
 def test_quantile(self):self.assertEqual(percentile([0,10],.9),9)
 def test_tail(self):
  v=parse_output('100 32 5000 1000 2000 0 100 99','PAPER',100,32);self.assertEqual(v['p999_latency_us'],2000);self.assertIsNone(v['p99_latency_us'])

class BundleTests(unittest.TestCase):
 def setUp(self):
  self.m=json.loads((Path(__file__).resolve().parents[2]/'manifests/paper_native_sift10m.json').read_text())
 def test_roles(self):self.assertEqual(len(components(self.m,'data','index')),9)
 def test_modern_rejected(self):
  self.m['subject']='MODERN_GOLDEN'
  with self.assertRaises(ValueError):components(self.m,'data','index')
 def test_wrong_pq(self):
  self.m['parameters']['pq_bytes']=128
  with self.assertRaises(ValueError):components(self.m,'data','index')
 def test_wrong_dataset(self):
  self.m['dataset']['N']=1000000
  with self.assertRaises(ValueError):components(self.m,'data','index')
 def test_traversal(self):
  self.m['files'][0]['path']='../escape'
  with self.assertRaises(ValueError):components(self.m,'data','index')
 def test_role_root(self):
  self.m['files'][0]['root']='index'
  with self.assertRaises(ValueError):components(self.m,'data','index')
 def test_duplicate(self):
  self.m['files'].append(self.m['files'][0])
  with self.assertRaises(ValueError):components(self.m,'data','index')
 def test_missing_files(self):
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/'m.json';f.write_text(json.dumps(self.m))
   with self.assertRaises(ValueError):verify(f,d,d,True)
 def test_corrupt_checksum(self):
  with tempfile.TemporaryDirectory() as d:
   m=copy.deepcopy(self.m)
   for f in m['files']:
    p=Path(d)/f['root']/f['path'];p.parent.mkdir(exist_ok=True);p.write_bytes(b'bad');f['size_bytes']=3
   p=Path(d)/'m.json';p.write_text(json.dumps(m))
   with self.assertRaisesRegex(ValueError,'Checksum'):verify(p,Path(d)/'data',Path(d)/'index',True)

if __name__=='__main__':unittest.main()

class OrchestrationTests(unittest.TestCase):
 def execute_fake(self,fail_quality=False):
  import paper_paired_campaign as pc
  from contextlib import ExitStack
  from unittest.mock import patch
  tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);root=Path(tmp.name);binary=root/'binary';binary.write_bytes(b'fake')
  c=dict(binary=str(binary),quality_binary=str(binary),manifest=str(root/'manifest'),data_root=str(root/'data'),index_root=str(root/'index'),subject_repo=str(root),extension=False,pause_s=0,between_block_s=0)
  sensor=dict(name='coretemp',label='Package id 0',value_C=40,critical_mC='100000')
  host=dict(power={'AC':'1'},rapl={'PL1':'60000000'},platform_profile='custom',sensors={'p':sensor})
  def git(cmd,**kwargs):return '' if 'status'in cmd else '23fbb256528c67454cd4348bc58dfee700dffa06\n' if 'HEAD^{tree}'in cmd else 'fakecommit\n'
  calls=[]
  def fake(spec,d):
   d=Path(d);d.mkdir();calls.append(d.name);quality=d.name.startswith('QUALITY');failed=quality and fail_quality
   m=dict(exit_code=-15 if failed else 0,guard_failure='Package >=99C' if failed else None,timestamp_start='start',timestamp_end='end',wall_time_s=1)
   (d/'manifest.json').write_text(json.dumps(m));(d/'stdout.log').write_text(f"Metadata: #pts = 10000, #dims = 128\n{spec['argv'][-1]} {spec['argv'][4]} 5000 1000 2000 0 100 99\n");(d/'stderr.log').write_text('');(d/'host.jsonl').write_text(json.dumps(host)+'\n');return m
  with ExitStack() as stack:
   for target,value in [('paper_paired_campaign.verify',lambda *a:dict(valid=True,files={},manifest_sha256='test')),('paper_paired_campaign.host_snapshot',lambda *a:host),('paper_paired_campaign.run',fake),('paper_paired_campaign.time.sleep',lambda *a:None),('subprocess.check_output',git),('paper_native_v3.quality_against_canonical',lambda *a:dict(recall=99,query_count=10000))]:stack.enter_context(patch(target,value))
   if fail_quality:
    with self.assertRaises(ValueError):pc.run_campaign(c,root/'evidence')
   else:pc.run_campaign(c,root/'evidence')
  return root/'evidence',calls
 def test_complete_fake_core(self):
  root,calls=self.execute_fake();s=json.loads((root/'EXECUTION.json').read_text());self.assertEqual(s['valid_runs'],18);self.assertEqual(len(calls),22)
  from paper_paired_campaign import summarize
  result=summarize(root);self.assertEqual(result['paired_T16_vs_T8']['median'],0)
 def test_quality_failure_does_not_blame_last_stock(self):
  root,calls=self.execute_fake(True);s=json.loads((root/'EXECUTION.json').read_text());rows=json.loads((root/'RUNS.json').read_text())
  self.assertEqual(s['valid_runs'],0);self.assertTrue(s['failed_job'].startswith('QUALITY'))
  self.assertEqual(rows[-1]['status'],'BENCHMARK_SUCCESS_PENDING_QUALITY');self.assertEqual(len(calls),19)
 def test_resume_refused(self):
  import paper_paired_campaign as pc
  root,_=self.execute_fake()
  with self.assertRaises(FileExistsError):pc.run_campaign({},root)
 def test_corrupt_checksum_rejected(self):
  from paper_paired_campaign import summarize
  root,_=self.execute_fake();p=root/'RUNS.json';p.write_text(p.read_text()+' ')
  with self.assertRaises(ValueError):summarize(root)
 def test_wrong_order_rejected_after_reseal(self):
  from paper_paired_campaign import summarize
  from paper_portable_v2 import seal
  root,_=self.execute_fake();p=root/'RUNS.json';rows=json.loads(p.read_text());rows[0],rows[1]=rows[1],rows[0];p.write_text(json.dumps(rows));seal(root)
  with self.assertRaises(ValueError):summarize(root)
 def test_missing_pair_rejected_after_reseal(self):
  from paper_paired_campaign import summarize
  from paper_portable_v2 import seal
  root,_=self.execute_fake();p=root/'RUNS.json';rows=json.loads(p.read_text());rows.pop();p.write_text(json.dumps(rows));seal(root)
  with self.assertRaises(ValueError):summarize(root)
