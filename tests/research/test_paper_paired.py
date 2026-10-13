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
