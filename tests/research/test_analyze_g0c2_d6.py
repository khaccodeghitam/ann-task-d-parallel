import copy
import json
from pathlib import Path
import random
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/research'))
import analyze_g0c2_d6 as c2
from test_analyze_g0_causal import fixture


class Reconstruction(unittest.TestCase):
    def test_out_of_order_multiple_workers_queries(self):
        events=fixture(3,1)+fixture(8,2);random.Random(18).shuffle(events)
        actual=c2.analyze_events(events)
        self.assertEqual(actual,c2.analyze_events(fixture(3,1)+fixture(8,2)))
        self.assertEqual([q['linux_tid'] for q in actual['queries']],[101,102])

    def test_hol_hidden_and_width(self):
        q=c2.analyze_query(fixture())
        self.assertEqual(q['publication_hol_us']['p95'],2)
        self.assertEqual(q['observed_io_us']['p95'],2)
        self.assertEqual(q['time_weighted']['mean_hidden'],.2)
        self.assertEqual(q['time_weighted']['mean_device_outstanding'],.2)
        self.assertEqual(q['time_weighted']['mean_total_unpublished'],.4)
        self.assertAlmostEqual(q['width']['time_weighted_mean'],40/9)
        self.assertEqual(q['width']['fraction_at_wcap'],.4)
        self.assertEqual(q['width']['unknown_fraction'],.1)
        self.assertEqual(q['logical_work']['expanded'],0)

    def test_equal_timestamps_zero_intervals(self):
        events=fixture()
        for e in events:
            if e['event'].startswith('IO_'):e['timestamp_ns']=3000
        events.reverse();q=c2.analyze_query(events)
        self.assertIsNone(q['request_metrics'][0]['hol_to_observed_io_ratio'])
        self.assertEqual(q['time_weighted']['mean_hidden'],0)

    def test_equal_width_ties_use_stock_chain(self):
        events=fixture();init=events[1];init.update(wcap=12)
        events[5].update(wcap=12,width=5)
        for old in range(5,11):events.append(dict(events[5],old_width=old,width=old+1))
        random.Random(2).shuffle(events)
        self.assertEqual(c2.analyze_query(events)['width']['final'],11)

    def test_out_of_order_cqe_fifo_publish(self):
        events=fixture();second=[]
        for kind,time in [('IO_SELECT',2200),('IO_SUBMIT',3500),('IO_CQE_SEEN',4000),('IO_PUBLISH',7500)]:
            second.append(dict(events[2],event=kind,timestamp_ns=time,request_seq=2,node_id=11,request_key=21))
        q=c2.analyze_query(events+second)
        self.assertEqual(q['request_metrics'][1]['publication_hol_us'],3.5)
        self.assertEqual(q['time_weighted']['max_hidden'],2)
        self.assertEqual(q['time_weighted']['fraction_hidden_ge2'],.2)
        second[-1]['timestamp_ns']=6500
        with self.assertRaisesRegex(ValueError,'FIFO'):c2.analyze_query(events+second)

    def test_cache_only_not_physical(self):
        events=[e for e in fixture() if e['event']!='IO_SUBMIT']
        next(e for e in events if e['event']=='IO_CQE_SEEN')['event']='IO_CACHE_READY'
        q=c2.analyze_query(events)
        self.assertEqual(q['publication_hol_us']['n'],0)
        self.assertEqual(q['logical_work']['cache_published'],1)
        self.assertEqual(q['time_weighted']['mean_hidden'],0)

    def test_missing_query_lifecycle(self):
        for kind in ('QUERY_START','QUERY_END','WIDTH_INIT','TRACE_HEALTH'):
            with self.subTest(kind=kind),self.assertRaises(ValueError):c2.analyze_query([e for e in fixture() if e['event']!=kind])

    def test_missing_cqe_submit_publish(self):
        for kind in ('IO_CQE_SEEN','IO_SUBMIT','IO_PUBLISH'):
            with self.subTest(kind=kind),self.assertRaises(ValueError):c2.analyze_query([e for e in fixture() if e['event']!=kind])

    def test_negative_counter(self):
        events=fixture();events[3]['submitted']=-1
        with self.assertRaisesRegex(ValueError,'Negative causal'):c2.analyze_query(events)

    def test_negative_hidden(self):
        events=fixture();events[4]['completed_hidden']=-1
        with self.assertRaisesRegex(ValueError,'Negative hidden'):c2.analyze_query(events)

    def test_cqe_before_submit(self):
        events=fixture();events[4]['timestamp_ns']=2500
        with self.assertRaises(ValueError):c2.analyze_query(events)

    def test_duplicate_request(self):
        events=fixture();events.append(events[2])
        with self.assertRaises(ValueError):c2.analyze_query(events)

    def test_unfinished_request(self):
        events=fixture();events[-1]['outstanding_correlations']=1
        with self.assertRaises(ValueError):c2.analyze_query(events)

    def test_width_decrease_jump(self):
        for width in (3,6):
            events=fixture();events[5]['width']=width
            with self.subTest(width=width),self.assertRaises(ValueError):c2.analyze_query(events)

    def test_histogram_nonindependent(self):
        self.assertEqual(c2.histogram([0,.5,1000])['counts'],[1,1,0,0,0,0,0,0,0,0,1])

    def test_quantiles_interpolated(self):
        self.assertAlmostEqual(c2.quantiles([0,10,20,30])['p95'],28.5)


class Phase(unittest.TestCase):
    def queries(self):return [dict(query_id=q,start_ns=100+int(i*100/16),end_ns=101+int(i*100/16)) for i,q in enumerate(c2.QIDS)]
    def test_phase_pass_and_relative_time(self):
        q=self.queries();p=c2.phase_coverage(q,100,201)
        self.assertFalse(p['phase_coverage_insufficient']);self.assertEqual(p['occupied_bins'],5)
        self.assertEqual(q[0]['benchmark_relative_start_ns'],0)
    def test_phase_insufficient(self):
        q=self.queries()
        for row in q:row.update(start_ns=110,end_ns=120)
        self.assertTrue(c2.phase_coverage(q,100,201)['phase_coverage_insufficient'])
    def test_four_bins_suffice(self):
        q=self.queries()
        for i,row in enumerate(q):row.update(start_ns=101+20*(i%4),end_ns=102+20*(i%4))
        self.assertEqual(c2.phase_coverage(q,100,201)['occupied_bins'],4)
    def test_bad_sampling(self):
        for q in (self.queries()[:-1],self.queries()+[self.queries()[0]]):
            with self.assertRaisesRegex(ValueError,'sampling'):c2.phase_coverage(q,100,201)
    def test_outside_phase(self):
        q=self.queries();q[0]['end_ns']=202
        with self.assertRaises(ValueError):c2.phase_coverage(q,100,201)
    def test_run_query_hierarchy(self):
        events=[]
        for i,qid in enumerate(c2.QIDS):
            for e in fixture(qid,i%2):events.append({**e,'timestamp_ns':e['timestamp_ns']+100000*i+1})
        d=c2.describe_detail(events,1,1600001)
        self.assertEqual(len(d['queries']),16)
        self.assertEqual(d['publication_hol_us']['n'],16)
        self.assertEqual(d['median_query_hidden_gt0_fraction'],.2)


class Gate(unittest.TestCase):
    def groups(self,hol=2,hidden=.01):
        return {c:[dict(round=i,detail=dict(publication_hol_us=dict(p95=2 if c=='B' else hol),observed_io_us=dict(p95=100),median_query_hidden_gt0_fraction=hidden,phase=dict(phase_coverage_insufficient=False))) for i in (1,2,3)] for c in 'ABCDE'}
    def test_low(self):self.assertEqual(c2.d6_gate(self.groups())['classification'],'D6_LOW')
    def test_material_threshold_inclusive(self):self.assertEqual(c2.d6_gate(self.groups(25))['classification'],'D6_MATERIAL')
    def test_hidden_alternative(self):self.assertEqual(c2.d6_gate(self.groups(4,.25))['classification'],'D6_MATERIAL')
    def test_intermediate(self):self.assertEqual(c2.d6_gate(self.groups(15))['classification'],'D6_INCONCLUSIVE')
    def test_low_strict_boundary(self):self.assertEqual(c2.d6_gate(self.groups(10))['classification'],'D6_INCONCLUSIVE')
    def test_phase_overrides_material(self):
        g=self.groups(25);g['A'][0]['detail']['phase']['phase_coverage_insufficient']=True
        self.assertEqual(c2.d6_gate(g)['classification'],'D6_INCONCLUSIVE')
    def test_missing_run(self):
        g=self.groups();g['E'].pop();self.assertEqual(c2.d6_gate(g)['classification'],'D6_INCONCLUSIVE')
    def test_duplicate_repetition(self):
        g=self.groups();g['D'][1]['round']=1;self.assertEqual(c2.d6_gate(g)['classification'],'D6_INCONCLUSIVE')
    def test_zero_baseline_not_confirmation(self):
        g=self.groups(25)
        for row in g['B']:row['detail']['publication_hol_us']['p95']=0
        r=c2.d6_gate(g);self.assertEqual(r['classification'],'D6_INCONCLUSIVE');self.assertEqual(r['measurements']['C']['confirmations'],[False]*3)
    def test_zero_io_not_low(self):
        g=self.groups()
        for c in ('C','D'):
            for row in g[c]:row['detail']['observed_io_us']['p95']=0
        self.assertEqual(c2.d6_gate(g)['classification'],'D6_INCONCLUSIVE')
    def test_median_of_ratios_not_ratio_of_medians(self):
        g=self.groups()
        for c in ('C','D'):
            for row,h,o in zip(g[c],[4,25,100],[10,1000,500]):row['detail']['publication_hol_us']['p95']=h;row['detail']['observed_io_us']['p95']=o
        result=c2.d6_gate(g)
        self.assertEqual(result['measurements']['C']['median_ratio'],.2)
        self.assertEqual(result['classification'],'D6_INCONCLUSIVE')
    def test_non_twofold_consistent_elevation_not_low(self):self.assertEqual(c2.d6_gate(self.groups(3))['classification'],'D6_INCONCLUSIVE')
    def test_system_wide_never_generalized(self):self.assertEqual(c2.d6_gate(self.groups(25))['system_wide_D6'],'INCONCLUSIVE')
    def test_negative_metric(self):
        g=self.groups(-1)
        with self.assertRaises(ValueError):c2.d6_gate(g)


class Integrity(unittest.TestCase):
    def records(self):return [dict(round=i,config=c,run_id=f'{i}{c}') for i,order in enumerate(c2.ORDERS,1) for c in order]
    def test_exact_order(self):c2.validate_order(self.records())
    def test_wrong_order(self):
        rows=self.records();rows[0],rows[1]=rows[1],rows[0]
        with self.assertRaises(ValueError):c2.validate_order(rows)
    def test_missing_campaign_run(self):
        with self.assertRaises(ValueError):c2.validate_order(self.records()[:-1])
    def test_checksum_corruption(self):
        with tempfile.TemporaryDirectory() as name:
            p=Path(name);(p/'evidence').write_text('valid');(p/'SHA256SUMS').write_text(c2.digest(p/'evidence')+'  evidence\n');c2.verify_sums(p);(p/'evidence').write_text('changed')
            with self.assertRaises(ValueError):c2.verify_sums(p)
    def test_provenance_and_package_rejected_first(self):
        plan=dict(harness_commit='correct')
        r=dict(manifest=dict(run_id='r',repetition=1,harness_git_commit='wrong'),summary=dict(run_id='r'),trace_health={},runner_return_code=0,run_id='r',round=1)
        plan['subjects']=dict(instrumented={})
        with self.assertRaisesRegex(ValueError,'Harness provenance'):c2.validate_record(r,plan)


if __name__=='__main__':unittest.main()

class RecordValidation(unittest.TestCase):
    def fixture(self):
        from test_analyze_g0b_light import fixture as light_fixture
        p,records=light_fixture();r=records[0];p.update(issue=18,main_base_commit=c2.BASE,orders=c2.ORDERS,repetitions=3,accepted_run_count=15,thresholds=c2.THRESHOLDS,subject_branch='research/g0c1-distributed-detail-sampling')
        p['subjects']['instrumented'].update(commit=c2.SUBJECT,binary_sha256=c2.BINARY)
        p['subjects']['STOCK']=dict(commit='b9ec4ba86ff5d70bec277984777197f28dc2cf42')
        p['telemetry']['host_telemetry_requested']=True
        p['trace']=dict(mode='DETAIL',causal_trace_enabled=True,detail_first_n=16,event_capacity=65536,sample_policy=c2.explicit_policy(c2.QIDS,10000))
        r['runtime_snapshots']=[]
        m=r['manifest'];m.update(harness_git_branch='research/g0c2-sift10m-detail-d6',subject_git_branch=p['subject_branch'],subject_git_commit=c2.SUBJECT,executable_sha256=c2.BINARY,trace_mode='DETAIL',trace_config=p['trace'].copy())
        m['environment']={**p['environment'],'OMP_NUM_THREADS':'1'}
        r['trace_health'].update(schema_version=3,trace_mode='DETAIL',sample_requested=16,sample_observed=16,requested_sample_qids=c2.QIDS,observed_sample_qids=c2.QIDS,sample_policy=p['trace']['sample_policy'],buffer_capacity=65536)
        return p,r
    def reject(self,change,message):
        p,r=self.fixture();change(p,r)
        with self.assertRaisesRegex(ValueError,message):c2.validate_record(r,p)
    def test_valid_record(self):p,r=self.fixture();c2.validate_plan(p);c2.validate_record(r,p)
    def test_subject_mismatch(self):self.reject(lambda p,r:r['manifest'].update(subject_git_commit='wrong'),'Subject provenance')
    def test_package_mismatch(self):self.reject(lambda p,r:r['manifest'].update(input_package_manifest_sha256='wrong'),'Package mismatch')
    def test_trace_failure(self):self.reject(lambda p,r:r['summary'].update(trace_valid=False),'Benchmark/trace failure')
    def test_trace_drop(self):self.reject(lambda p,r:r['trace_health'].update(events_dropped=1),'Trace health')
    def test_overflow(self):self.reject(lambda p,r:r['trace_health'].update(table_overflows=1),'Trace health')
    def test_sampling_mismatch(self):self.reject(lambda p,r:r['trace_health'].update(observed_sample_qids=c2.QIDS[:-1]),'Trace sample')
    def test_native_affinity_rejected(self):self.reject(lambda p,r:r['manifest']['environment'].update(OMP_PLACES='threads'),'environment')
    def test_missing_telemetry(self):self.reject(lambda p,r:r['telemetry_presence'].update(iostat=False),'telemetry')
    def test_plan_threshold_rejected(self):
        p,r=self.fixture();p['thresholds']={**p['thresholds'],'material_scale_ratio':.30}
        with self.assertRaisesRegex(ValueError,'threshold'):c2.validate_plan(p)
