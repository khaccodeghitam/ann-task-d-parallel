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
    def custom_contract(self):
        b=self.baseline()
        b['platform_profile']='custom'
        b['rapl']={
            '/sys/class/powercap/intel-rapl-mmio/intel-rapl-mmio:0/constraint_0_power_limit_uw':'60000000',
            '/sys/class/powercap/intel-rapl-mmio/intel-rapl-mmio:0/constraint_1_power_limit_uw':'90000000'}
        expected=dict(platform_profile='custom',mmio_PL1_W=60,mmio_PL2_W=90,tolerance_W=1)
        return b,expected
    def test_expected_custom_fullfan_passes_without_setting_host(self):
        b,expected=self.custom_contract()
        self.assertEqual(campaign.expected_host_violations(b,expected),[])
        campaign.qualify_start(b,b,expected)
    def test_expected_custom_rejects_performance_mode(self):
        b,expected=self.custom_contract()
        b['platform_profile']='performance'
        with self.assertRaisesRegex(ValueError,'EXPECTED_ENVIRONMENT'):
            campaign.qualify_start(b,b,expected)
    def test_expected_custom_rejects_mmio_mismatch(self):
        b,expected=self.custom_contract()
        key=next(x for x in b['rapl'] if 'constraint_0_' in x)
        b['rapl'][key]='115000000'
        with self.assertRaisesRegex(ValueError,'PL1 MMIO'):
            campaign.qualify_start(b,b,expected)
    def test_expected_custom_rejects_missing_or_ambiguous_mmio(self):
        b,expected=self.custom_contract()
        b['rapl']={}
        self.assertTrue(any('missing or ambiguous' in e for e in campaign.expected_host_violations(b,expected)))
        b,expected=self.custom_contract()
        b['rapl']['/tmp/intel-rapl-mmio:1/constraint_0_power_limit_uw']='60000000'
        with self.assertRaisesRegex(ValueError,'ambiguous'):
            campaign.qualify_start(b,b,expected)
    def test_expected_custom_rejects_corrupt_fixed_contract(self):
        b,expected=self.custom_contract()
        expected['mmio_PL2_W']=135
        with self.assertRaisesRegex(ValueError,'invalid frozen config'):
            campaign.qualify_start(b,b,expected)
    def test_custom_config_fixed(self):
        repo_root=Path(__file__).resolve().parents[2]
        obj=json.loads((repo_root/'configs/custom_fullfan_campaign.json').read_text())
        self.assertEqual(obj['expected_operating_condition'],{
            'platform_profile':'custom','mmio_PL1_W':60,'mmio_PL2_W':90,'tolerance_W':1})

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


class Orchestration(unittest.TestCase):
    def fake(self, fail=None, hot=False):
        from contextlib import ExitStack
        from paper_rebaseline import digest as real_digest
        td=tempfile.TemporaryDirectory();self.addCleanup(td.cleanup);root=Path(td.name)
        host=HostContract().baseline()
        if hot:host['sensors']['p']['value_C']=85
        c=dict(subject_repo=str(root),binary='stock',quality_binary='quality',quality_sha256='q',
               input_package='input-package',index_package='index-package',manifest='bundle',data_root='data',index_root='index')
        hashes={'stock':'5f5fa8d99cc83b523c71b7025e5f0b9aa61f45d42816804ed6d88755ebaa310b','quality':'q',
                'input-package':'47d4bf47e6e515a3f3c4caeb357bdbc1af3bfcc4b319b0ae335678ca586dccc3',
                'index-package':'7140a47ac53b0480752059b5cb428b4d56dc627533974803b5ae4413827a7470'}
        def digest(p):return hashes[str(p)] if str(p) in hashes else real_digest(p)
        def git(cmd,**kw):
            if 'status' in cmd:return ''
            return '23fbb256528c67454cd4348bc58dfee700dffa06' if 'HEAD^{tree}' in cmd else 'c4cd32c6816c063f56ecc64f9d7b63c909202cab'
        calls=[]
        def run(spec,d):
            d=Path(d);d.mkdir();calls.append(d.name)
            if spec.get('extra_environment'):Path(spec['extra_environment']['PAPER_QUALITY_OUTPUT']).write_text('fake')
            failed=d.name==fail
            m=dict(exit_code=-15 if failed else 0,guard_failure='Package>=99C' if failed else None)
            (d/'manifest.json').write_text(json.dumps(m));(d/'stderr.log').write_text('')
            (d/'stdout.log').write_text(f"Metadata: #pts = 10000, #dims = 128\n{spec['argv'][-1]} {spec['argv'][4]} 5000 1000 2000 0 100 99\n")
            (d/'host.jsonl').write_text(json.dumps(host)+'\n');return m
        with ExitStack() as stack:
            for target,value in [('issue29_campaign.digest',digest),('issue29_campaign.snapshot',lambda *a:copy.deepcopy(host)),
                ('issue29_campaign.subprocess.check_output',git),('issue29_campaign.run',run),
                ('issue29_campaign.time.sleep',lambda *a:None),('issue29_campaign.unchanged',lambda *a:None),
                ('issue29_campaign.verify',lambda *a:dict(valid=True,files={})),
                ('issue29_campaign.quality_against_canonical',lambda *a:dict(recall=99,rows=100000))]:stack.enter_context(patch(target,value))
            result=campaign.execute(c,root/'campaign')
        return root/'campaign',calls,result
    def test_complete_eligible_fake(self):
        root,calls,result=self.fake();self.assertEqual(result['stock_qualified'],36)
        self.assertEqual(calls[:2],['QUALIFICATION_T16','QUALIFICATION_T8'])
        self.assertEqual(len([s for s in calls if s.startswith('R')]),36)
        self.assertLess(calls.index('POST_CORE_T16'),calls.index('R13_T1_W32_L100'))
    def test_first_quality_failure_no_stock(self):
        root,calls,result=self.fake('QUALIFICATION_T16');self.assertEqual(calls,['QUALIFICATION_T16'])
        self.assertEqual(result['stock_completed'],0);self.assertEqual(result['failed_job'],'QUALIFICATION_T16')
    def test_second_quality_thermal_no_stock(self):
        root,calls,result=self.fake('QUALIFICATION_T8');self.assertEqual(len(calls),2)
        self.assertEqual(result['quality_completed'],1);self.assertEqual(result['stock_completed'],0)
    def test_post_quality_failure_preserves_stock(self):
        root,calls,result=self.fake('POST_CORE_T16');self.assertEqual(result['stock_completed'],12)
        self.assertEqual(result['failed_job'],'POST_CORE_T16');self.assertEqual(result['stock_qualified'],0)
        self.assertTrue(all(r['status']=='PROVISIONAL' for r in json.loads((root/'RUNS.json').read_text())))
    def test_hot_preflight_no_invocations(self):
        root,calls,result=self.fake(hot=True);self.assertEqual(calls,[]);self.assertEqual(result['status'],'SKIPPED_THERMAL')


class ReadOnlyAnalysis(unittest.TestCase):
    def test_tampered_seal_fails(self):
        from analyze_issue29 import check_seal
        from paper_portable_v2 import seal
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'evidence').write_text('first');seal(root);check_seal(root)
            (root/'evidence').write_text('second')
            with self.assertRaisesRegex(ValueError,'Checksum'):check_seal(root)
    def test_unsafe_seal_fails(self):
        from analyze_issue29 import check_seal
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'SHA256SUMS').write_text('abc  ../escape\n')
            with self.assertRaisesRegex(ValueError,'Unsafe'):check_seal(root)


if __name__=='__main__':unittest.main()
