"""No ANN invocation; positive identity proof required for MMIO aliases."""
import sys
from pathlib import Path
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/research'))
from issue29_campaign import expected_host_violations


class AliasTests(unittest.TestCase):
    expected=dict(platform_profile='custom',mmio_PL1_W=60,mmio_PL2_W=90,tolerance_W=1)
    def snapshot(self,root,alias=True,conflict=False,missing=False):
        physical=root/'intel-rapl-mmio:0';physical.mkdir()
        for i,v in [(0,'60000000'),(1,'90000000')]: (physical/f'constraint_{i}_power_limit_uw').write_text(v)
        duplicate=root/'duplicate-intel-rapl-mmio:0'
        if alias:duplicate.symlink_to(physical,target_is_directory=True)
        elif not missing:
            duplicate.mkdir()
            for i,v in [(0,'60000000'),(1,'90000000')]: (duplicate/f'constraint_{i}_power_limit_uw').write_text(v)
        entries={str(physical/f'constraint_{i}_power_limit_uw'):v for i,v in [(0,'60000000'),(1,'90000000')]}
        entries.update({str(duplicate/f'constraint_{i}_power_limit_uw'):('61000000' if conflict and i==0 else v) for i,v in [(0,'60000000'),(1,'90000000')]})
        return dict(platform_profile='custom',rapl=entries)
    def test_same_register_alias_pass(self):
        with tempfile.TemporaryDirectory() as d:self.assertEqual(expected_host_violations(self.snapshot(Path(d)),self.expected),[])
    def test_alias_conflicting_values_rejected(self):
        with tempfile.TemporaryDirectory() as d:self.assertTrue(expected_host_violations(self.snapshot(Path(d),conflict=True),self.expected))
    def test_distinct_registers_same_value_rejected(self):
        with tempfile.TemporaryDirectory() as d:self.assertTrue(expected_host_violations(self.snapshot(Path(d),alias=False),self.expected))
    def test_unproven_alias_rejected(self):
        with tempfile.TemporaryDirectory() as d:self.assertTrue(expected_host_violations(self.snapshot(Path(d),alias=False,missing=True),self.expected))
    def test_wrong_profile_still_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            s=self.snapshot(Path(d));s['platform_profile']='performance';self.assertTrue(expected_host_violations(s,self.expected))


if __name__=='__main__':unittest.main()


class AnalysisTests(unittest.TestCase):
    def initial(self):
        keys=[f'/a/intel-rapl-mmio:0/constraint_{i}_power_limit_uw' for i in (0,1)]
        return dict(platform_profile='custom',power={'AC':'1'},rapl=dict(zip(keys,['60000000','90000000'])),
                    mmio_identity={k:dict(realpath=k,device=1,inode=i) for i,k in enumerate(keys)},
                    sensors={'p':dict(name='coretemp',label='Package id 0',value_C=50)})
    def test_observed_custom_valid(self):
        from analyze_custom_fullfan import verify_environment
        s=self.initial();verify_environment([s],s)
    def test_observed_missing_identity_reject(self):
        from analyze_custom_fullfan import verify_environment
        s=self.initial();s['mmio_identity']={}
        with self.assertRaisesRegex(ValueError,'identity'):verify_environment([s],s)
    def test_observed_transition_reject(self):
        from analyze_custom_fullfan import verify_environment
        import copy
        s=self.initial();t=copy.deepcopy(s);t['rapl'][next(iter(t['rapl']))]='115000000'
        with self.assertRaisesRegex(ValueError,'mismatch'):verify_environment([t],s)
    def test_observed_unsafe_reject(self):
        from analyze_custom_fullfan import verify_environment
        s=self.initial();s['sensors']['p']['value_C']=99
        with self.assertRaisesRegex(ValueError,'unsafe'):verify_environment([s],s)
    def test_observed_startup_threshold_reject(self):
        from analyze_custom_fullfan import verify_environment
        s=self.initial();s['sensors']['p']['value_C']=85
        with self.assertRaisesRegex(ValueError,'Startup'):verify_environment([s],s)
    def test_observed_missing_package_sensor_reject(self):
        from analyze_custom_fullfan import verify_environment
        s=self.initial();s['sensors']={}
        with self.assertRaisesRegex(ValueError,'temperature'):verify_environment([s],s)
    def test_paired_units_and_bootstrap(self):
        from analyze_custom_fullfan import pair_statistics
        rows=[]
        for b in range(1,7):
            for t in (8,16):rows.append(dict(configuration=dict(stage='core',block=b,T=t),metrics=dict(qps=100 if t==8 else 110,mean_latency_us=100,recall=99)))
        a=pair_statistics(rows,20261029);self.assertEqual(a,pair_statistics(rows,20261029))
        self.assertAlmostEqual(a['QPS_delta_percent']['median'],10);self.assertEqual(len(a['QPS_delta_percent']['values']),6)
        self.assertEqual(a['QPS_delta_percent']['descriptive']['n'],6)
        with self.assertRaisesRegex(ValueError,'Missing'):pair_statistics(rows[:-1],20261029)
    def test_descriptive_run_clustering(self):
        from analyze_custom_fullfan import aggregate
        rows=[dict(configuration=dict(T=8,W=32,L=100),metrics=dict(qps=q,mean_latency_us=100,p999_latency_us=200,recall=99,mean_ios=90)) for q in (100,110,120)]
        stats=aggregate(rows)['T8_W32_L100']['qps'];self.assertEqual(stats['n'],3);self.assertEqual(stats['median'],110);self.assertEqual(stats['sample_sd'],10)
