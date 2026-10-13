import copy
import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/research'))
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'research'))
import issue29_campaign as campaign
import oracle_disagreement as oracle


class HostContract(unittest.TestCase):
    def baseline(self):
        return dict(sensors={'p':dict(name='coretemp',label='Package id0',value_C=44,critical_mC='100000')},
                    power={'AC':'1'},rapl={'PL1':'115000000'},platform_profile='performance',
                    monotonic_s=1,mem_available=8*2**30,free_disk=100*2**30,swap_used=0,ann=[])
    def test_qualification_cold(self):
        s=self.baseline();campaign.qualify_start(s,s)
    def test_hot_reject_no_guard_override(self):
        b=self.baseline();s=copy.deepcopy(b);s['sensors']['p']['value_C']=85
        with self.assertRaisesRegex(ValueError,'85C'):campaign.qualify_start(s,b)
    def test_no_sensor(self):
        b=self.baseline();s=copy.deepcopy(b);s['sensors']={}
        with self.assertRaises(ValueError):campaign.qualify_start(s,b)
    def test_policy_change(self):
        b=self.baseline();s=copy.deepcopy(b);s['rapl']['PL1']='60000000'
        with self.assertRaisesRegex(ValueError,'condition changed'):campaign.qualify_start(s,b)
    def test_ac_off(self):
        b=self.baseline();s=copy.deepcopy(b);s['power']['AC']='0'
        with self.assertRaises(ValueError):campaign.qualify_start(s,b)
    def test_order_core_first(self):
        rows=campaign.schedule();self.assertEqual(rows,campaign.schedule());self.assertEqual(len(rows),36)
        self.assertEqual([r['stage'] for r in rows[:12]],['core']*12)
        orders=[tuple(r['T'] for r in rows if r['stage']=='core' and r['block']==b) for b in range(1,7)]
        self.assertEqual(orders.count((8,16)),3);self.assertEqual(orders.count((16,8)),3)
        self.assertEqual(sum(r['T']==1 for r in rows),3);self.assertEqual(sum(r['T']==4 for r in rows),3)


class Offline(unittest.TestCase):
    def rows(self):
        rows=[]
        for q,split in enumerate(['train']*4+['validation']*2+['test']*2):
            for step in (8,24):
                for rank in range(3):
                    rows.append(dict(query_id=q,split=split,step=step,node=q*10+rank,distance_norm=.8+rank*.1,
                        frontier_rank=rank/12,degree=64,seen=100+step,overlap=.02,G1=0,Gk=.01 if rank==0 else .03 if rank==1 else 0,
                        novel=20,useful=1,batch_marginal_Gk=.01))
        return rows
    def test_disagreement_cluster(self):
        r=oracle.disagreement(self.rows());self.assertEqual(len(r['queries']),8)
        self.assertEqual(r['query_cluster_disagreement_mean'],1);self.assertAlmostEqual(r['mean_query_gap'],.02)
        self.assertAlmostEqual(r['top1_gap_share'],1/8);self.assertAlmostEqual(r['top5_gap_share'],5/8)
    def test_zero_gap_and_ties(self):
        rows=self.rows()
        for r in rows:r['Gk']=0
        d=oracle.disagreement(rows);self.assertEqual(d['total_gap'],0);self.assertEqual(d['positive_gap_queries'],0)
        self.assertTrue(all(s['nearest_node']==s['oracle_node'] for s in d['states']))
    def test_bootstrap_deterministic(self):self.assertEqual(oracle.cluster_ci([0,.1,0]),oracle.cluster_ci([0,.1,0]))
    def test_no_feature_label_leak(self):
        rows=self.rows();a=oracle.design(rows,'cheap_margin')
        for r in rows:r.update(Gk=999,novel=0,useful=100,overlap=1)
        self.assertTrue((a==oracle.design(rows,'cheap_margin')).all())
    def test_models_fixed_and_negative_control(self):
        a=oracle.fit_models(self.rows());b=oracle.fit_models(self.rows());self.assertEqual(a,b)
        self.assertEqual(set(a),set(oracle.MODELS));self.assertEqual(a['cheap_margin']['test']['queries'],2)
    def test_query_leak_rejected(self):
        rows=self.rows();rows[0]['split']='test'
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'rows.csv'
            with p.open('w') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
            with self.assertRaisesRegex(ValueError,'split leakage'):oracle.load_rows(p)
    def test_frontier_equal_budget_quality_flag(self):
        r=oracle.branching(self.rows());self.assertEqual(len(r['synthetic_rows']),30)
        self.assertTrue(all(x['budget']==24 for x in r['synthetic_rows']))
        self.assertTrue(all(isinstance(x['equal_quality'],bool) for x in r['quality_controlled_comparisons']))
    def test_absent_raw_not_fabricated(self):
        with self.assertRaises(FileNotFoundError):oracle.load_rows('/does-not-exist')


if __name__=='__main__':unittest.main()
