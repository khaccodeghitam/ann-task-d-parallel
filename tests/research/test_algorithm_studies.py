import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('ann_studies',Path(__file__).resolve().parents[2]/'research/studies.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)

class StudyTests(unittest.TestCase):
 def test_directed_motifs(self):
  self.assertEqual(s.motif_counts({0:[1,2],1:[2],2:[0]},0),dict(transitive_ordered_wedges=1,three_cycles_rooted=1))
 def test_overlap_not_motif_count(self):
  self.assertEqual(s.jaccard([1,2],[2,3]),1/3);self.assertEqual(s.jaccard([],[]),0)
 def test_partial_topk_excluded(self):
  with self.assertRaises(ValueError):s.one_step([(1,1)],[],k=10)
 def test_one_step_reset_and_duplicate(self):
  state=[(20,1),(30,2)];original=list(state)
  a=s.one_step(state,[(5,3),(5,3),(1,1)],k=2)
  self.assertEqual(a['after'],[(5,3),(20,1)]);self.assertEqual(a['G1'],25);self.assertEqual(state,original)
  self.assertEqual(a,s.one_step(state,[(5,3)],k=2));self.assertEqual(s.one_step(state,[],k=2)['Gk'],0)
 def test_batch_marginal(self):
  state=[(20,1),(30,2)];a=s.one_step(state,[(5,3)],k=2)['Gk'];b=s.one_step(state,[(5,3),(10,4)],k=2)['Gk'];self.assertGreaterEqual(b-a,0)
 def test_tie_ranks(self):
  self.assertEqual(list(s.rankdata([1,1,3])),[.5,.5,2]);self.assertIsNone(s.spearman([1,1],[1,2]))
 def test_chain_bound(self):
  g=s.synthetic_graphs()['chain'];a=s.simulate(g,'sequential');b=s.simulate(g,'same_budget_best_first')
  self.assertEqual(a['simulated_time'],b['simulated_time']);self.assertGreaterEqual(a['simulated_time'],a['dependency_span_service_units'])
 def test_branching(self):
  g=s.synthetic_graphs()['branching_tree'];a=s.simulate(g,'sequential');b=s.simulate(g,'same_budget_best_first')
  self.assertEqual(a['expansions'],b['expansions']);self.assertLess(b['simulated_time'],a['simulated_time'])
 def test_redundant_baseline_equality(self):
  g=s.synthetic_graphs()['branching_tree'];a=s.simulate(g,'distance_batch');b=s.simulate(g,'same_budget_best_first');a.pop('policy');b.pop('policy');self.assertEqual(a,b)
 def test_decoy_counterexample(self):
  g=s.synthetic_graphs()['decoy_dense_cluster'];a=s.simulate(g,'distance_batch');b=s.simulate(g,'anchor_explore');self.assertEqual(a['recall_at1'],0);self.assertEqual(b['recall_at1'],1)
 def test_deterministic_random(self):
  g=s.synthetic_graphs()['branching_tree'];self.assertEqual(s.simulate(g,'random'),s.simulate(g,'random'))
 def test_reader(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'g';raw=bytearray(8192);struct.pack_into('<II9Q',raw,0,9,1,2,128,0,388,10,0,0,8192,8192)
   for u in range(2):struct.pack_into('<II',raw,4096+388*u+128,1,1-u)
   p.write_bytes(raw);g=s.GraphReader(p,limit_nodes=1);self.assertEqual(g.neighbors(0),(1,));self.assertEqual(len(g.vector(0)),128)
   with self.assertRaises(ValueError):g.neighbors(1)
   with self.assertRaises(ValueError):g.vector(2)
   g.close()

if __name__=='__main__':unittest.main()
