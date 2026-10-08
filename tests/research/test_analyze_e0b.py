import copy
import importlib.util
import os
from pathlib import Path
import unittest
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = Path(os.environ.get('E0B_ANALYZER_UNDER_TEST', str(ROOT / 'tools/research/analyze_e0b.py')))
spec = importlib.util.spec_from_file_location('e0b', SCRIPT)
e0b = importlib.util.module_from_spec(spec); spec.loader.exec_module(e0b)


def fixture():
    plan = {'orders': [list(o) for o in e0b.ORDERS], 'harness_commit': 'harness',
        'input_package_sha256': 'input', 'index_package_sha256': 'index',
        'subjects': {'STOCK': {'commit': 'stock', 'root': '/stock', 'binary_sha256': 'stock-binary'},
                     'instrumented': {'commit': 'instrumented', 'root': '/instrumented', 'binary_sha256': 'instrumented-binary'}},
        'search': {'threads': 8, 'wcap': 32, 'l_search': 100, 'k': 10, 'query_count': 10000},
        'environment': {'OMP_NUM_THREADS': '8', 'MKL_NUM_THREADS': '8', 'OMP_PROC_BIND': 'spread', 'OMP_PLACES': 'threads'},
        'trace': {'detail_first_n':16, 'event_capacity':65536}, 'telemetry': {'interval_s': 1},
        'variants': {'STOCK': {'trace_mode': 'OFF', 'causal_trace_enabled': False},
                     'OFF': {'trace_mode': 'OFF', 'causal_trace_enabled': True},
                     'LIGHT': {'trace_mode': 'LIGHT', 'causal_trace_enabled': True}},
        'bootstrap': {'unit':'block', 'block_count':12, 'samples':20000, 'seed':20261008, 'ci_percent':90},
        'effect_margins_percent': {'OFF_vs_STOCK':3, 'LIGHT_vs_OFF':5}, 'recall_tolerance_percentage_points': .02}
    records = []
    for block, order in enumerate(e0b.ORDERS,1):
        for case in order:
            sid = plan['subjects']['STOCK' if case == 'STOCK' else 'instrumented']
            identity = f'B{block:02}_{case}'
            manifest = {'run_id': identity, 'repetition':block, **plan['search'], **plan['variants'][case],
                'input_package_manifest_sha256': 'input', 'index_package_manifest_sha256': 'index',
                'subject_git_commit': sid['commit'], 'subject_repo_root':sid['root'],
                'subject_git_dirty':False, 'executable_sha256':sid['binary_sha256'],
                'harness_git_commit':'harness', 'harness_git_dirty':False,
                'environment':copy.deepcopy(plan['environment']), 'trace_config':copy.deepcopy(plan['trace']),
                'host_telemetry_requested':True, 'host_telemetry_option':True, 'telemetry_interval_s':1,
                'host_telemetry_collectors':{c:{'status':'stopped','metric_rows':1} for c in e0b.COLLECTORS},
                'mlflow_enabled':True}
            records.append({'block':block, 'case':case, 'run_id':identity, 'manifest':manifest,
                'summary':{'run_id':identity, 'benchmark_status':'success', 'qps':100, 'mean_latency_us':100,
                           'recall':99.14, 'trace_valid':None if case=='STOCK' else True},
                'trace_health':{'trace_valid':True}, 'telemetry_presence':dict.fromkeys(e0b.COLLECTORS,True)})
    return plan, records


class E0bTests(unittest.TestCase):
    def test_six_permutations_twice(self):
        self.assertEqual(len(set(e0b.ORDERS)),6)
        self.assertEqual(e0b.ORDERS[:6],e0b.ORDERS[6:])
        plan, records=fixture();e0b.validate_records(records,plan)

    def test_complete_12_blocks(self):
        plan,records=fixture()
        e0b.validate_records(records,plan)
        self.assertEqual(len(records),36)
        self.assertEqual({r['block'] for r in records},set(range(1,13)))

    def test_missing_block_rejected(self):
        plan,records=fixture()
        with self.assertRaisesRegex(ValueError,'incomplete'):
            e0b.validate_records(records[:-3],plan)

    def test_missing_variant_rejected(self):
        plan,records=fixture()
        with self.assertRaisesRegex(ValueError,'incomplete'):
            e0b.validate_records(records[:-1],plan)

    def test_wrong_order_rejected(self):
        plan,records=fixture();records[0],records[1]=records[1],records[0]
        with self.assertRaisesRegex(ValueError,'order violation'):
            e0b.validate_records(records,plan)

    def test_wrong_frozen_order_rejected(self):
        plan,records=fixture();plan['orders'][0].reverse()
        with self.assertRaisesRegex(ValueError,'Issue #10 order'):
            e0b.validate_records(records,plan)

    def test_paired_delta(self):
        self.assertEqual(e0b.paired_delta(103,100),3)
        self.assertEqual(e0b.paired_delta(99.14,99.12,recall=True),.02)
        with self.assertRaises(ValueError):e0b.paired_delta(1,0)

    def test_median_absolute_and_mad(self):
        stats=e0b.descriptive([-3,-2,1,2,3])
        self.assertEqual(stats['median_absolute_paired_delta'],2)
        self.assertEqual(stats['MAD'],2)
        self.assertEqual(stats['sample_sd'],e0b.statistics.stdev([-3,-2,1,2,3]))

    def test_deterministic_bootstrap(self):
        values=list(range(12))
        self.assertEqual(e0b.bootstrap_median(values),e0b.bootstrap_median(values))
        self.assertEqual(e0b.bootstrap_median(values),[3,8])

    def test_ci_calculation(self):
        self.assertEqual(e0b.bootstrap_median([.02]*12),[.02,.02])
        self.assertAlmostEqual(e0b.percentile([0,10,20,30],.95),28.5)

    def test_bootstrap_requires_block_count(self):
        with self.assertRaisesRegex(ValueError,'12 block'):e0b.bootstrap_median([0]*11)

    def test_proceed_gate_boundary(self):
        self.assertEqual(e0b.comparison_gate(3,[-3,3],3),'PROCEED')

    def test_fail_gate_both_directions(self):
        self.assertEqual(e0b.comparison_gate(4,[3.1,5],3),'FAIL')
        self.assertEqual(e0b.comparison_gate(-4,[-5,-3.1],3),'FAIL')

    def test_inconclusive_gate(self):
        self.assertEqual(e0b.comparison_gate(0,[-4,4],3),'INCONCLUSIVE')
        self.assertEqual(e0b.comparison_gate(3.1,[2,4],3),'INCONCLUSIVE')

    def test_recall_gate(self):
        self.assertEqual(e0b.comparison_gate(.02,[-.02,.02],.02,True),'PROCEED')
        self.assertEqual(e0b.comparison_gate(.03,[.01,.04],.02,True),'INCONCLUSIVE')
        self.assertEqual(e0b.comparison_gate(.03,[.021,.04],.02,True),'FAIL')

    def test_overall_proceed(self):
        plan,records=fixture();result=e0b.analyze_records(records,plan)
        self.assertEqual(result['classification'],'E0B_PROCEED')
        self.assertEqual(result['comparisons']['OFF_vs_STOCK']['qps']['values'],[0]*12)
        self.assertEqual(result['statistical_unit'],'BLOCK')

    def test_overall_fail_outside_ci(self):
        plan,records=fixture()
        for r in records:
            if r['case']=='OFF':r['summary']['qps']=110
        self.assertEqual(e0b.analyze_records(records,plan)['classification'],'E0B_FAIL')

    def test_overall_inconclusive_ci_crosses(self):
        plan,records=fixture()
        for r in records:
            if r['case'] in ('OFF','LIGHT'):r['summary']['qps']=94 if r['block']<=6 else 106
        self.assertEqual(e0b.analyze_records(records,plan)['classification'],'E0B_INCONCLUSIVE')

    def test_trace_invalidity_fails(self):
        plan,records=fixture();records[1]['summary']['trace_valid']=False
        result=e0b.analyze_records(records,plan)
        self.assertEqual(result['classification'],'E0B_FAIL')
        self.assertEqual(result['invalid_required_traces'],[records[1]['run_id']])

    def test_trace_drops_fail(self):
        plan,records=fixture();records[1]['trace_health']['events_dropped']=1
        self.assertEqual(e0b.analyze_records(records,plan)['classification'],'E0B_FAIL')

    def test_matched_telemetry_presence_required(self):
        plan,records=fixture();records[0]['telemetry_presence']['pidstat']=False
        with self.assertRaisesRegex(ValueError,'telemetry presence'):e0b.validate_records(records,plan)

    def test_telemetry_explicit_request_required(self):
        plan,records=fixture();records[0]['manifest']['host_telemetry_option']=None
        with self.assertRaisesRegex(ValueError,'telemetry request'):e0b.validate_records(records,plan)

    def test_package_mismatch(self):
        plan,records=fixture();records[0]['manifest']['input_package_manifest_sha256']='wrong'
        with self.assertRaisesRegex(ValueError,'Package mismatch'):e0b.validate_records(records,plan)

    def test_subject_mismatch(self):
        plan,records=fixture();records[0]['manifest']['subject_git_commit']='wrong'
        with self.assertRaisesRegex(ValueError,'Subject/binary'):e0b.validate_records(records,plan)

    def test_placement_environment_mismatch(self):
        plan,records=fixture();records[0]['manifest']['environment']['OMP_PROC_BIND']='close'
        with self.assertRaisesRegex(ValueError,'Placement/environment'):e0b.validate_records(records,plan)

    def test_search_mismatch(self):
        plan,records=fixture();records[0]['manifest']['l_search']=75
        with self.assertRaisesRegex(ValueError,'Search configuration'):e0b.validate_records(records,plan)

    def test_no_old_global_recall_span_gate(self):
        plan,records=fixture()
        for r in records:r['summary']['recall']=99.10+r['block']*.01
        result=e0b.analyze_records(records,plan)
        self.assertEqual(result['classification'],'E0B_PROCEED')
        self.assertEqual(result['comparisons']['OFF_vs_STOCK']['recall']['ci90_median'],[0,0])

    def test_thread_context_switch_telemetry(self):
        raw = "# Time UID TGID TID %usr %system %CPU cswch/s nvcswch/s Command\n" + \
              "12:00:01 1000 42 - 400 400 800 3 900 benchmark\n" + \
              "12:00:01 1000 - 44 0 50 50 0 100 |__iou-sqp-42\n"
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'threads.log'; path.write_text(raw)
            result = e0b.thread_telemetry(path)
        self.assertEqual(result['process:42|nvcswch/s']['mean'], 900)
        self.assertEqual(result['thread:44|%CPU']['mean'], 50)
        self.assertNotIn('median_absolute_paired_delta', result['thread:44|%CPU'])

    def test_benchmark_failure_stops_campaign(self):
        plan, records = fixture(); records[0]['summary']['benchmark_status']='timed_out'
        with self.assertRaisesRegex(ValueError, 'execution failure'):
            e0b.analyze_records(records, plan)

    def test_frozen_margins_rejected(self):
        plan,records=fixture();plan['effect_margins_percent']['OFF_vs_STOCK']=4
        with self.assertRaisesRegex(ValueError,'effect tolerance'):e0b.analyze_records(records,plan)

    def test_duplicate_run_id_rejected(self):
        plan,records=fixture();records[-1]['run_id']=records[0]['run_id']
        with self.assertRaisesRegex(ValueError,'Duplicate/reused'):e0b.validate_records(records,plan)


if __name__=='__main__':unittest.main()
