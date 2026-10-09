import copy
import csv
import importlib.util
import json
import os
from pathlib import Path
import statistics
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(os.environ.get('G0B_REPO', str(Path(__file__).resolve().parents[2])))
SCRIPT = Path(os.environ.get('G0B_ANALYZER_UNDER_TEST', str(ROOT / 'tools/research/analyze_g0b_light.py')))
sys.path.insert(0, str(ROOT / 'tools/research'))
spec = importlib.util.spec_from_file_location('light', SCRIPT)
light = importlib.util.module_from_spec(spec)
spec.loader.exec_module(light)


def rows(count=2, run_id='run', cache=0):
    result = []
    for i in range(count):
        r = dict.fromkeys((*light.ZERO_HEALTH, 'events_written', 'is_sampled'), 0)
        r.update(query_id=i, run_id=run_id, trace_mode='LIGHT', worker_id=0, linux_tid=1,
                 initial_width=4, final_width=5+i, width_change_count=1+i, max_inflight=5,
                 max_completed_hidden=3, selected=10+cache, submitted=10, cqe_seen=10, published=10,
                 cqe_count=10, expanded=9, cache_ready=cache, cache_published=cache)
        result.append(r)
    return result


def fixture():
    subject = dict(commit=light.SUBJECT_COMMIT, root='/test/PipeANN-p0', binary_sha256='binary')
    plan = dict(schema_version=1, issue=14, orders=copy.deepcopy(light.ORDERS), sentinels=copy.deepcopy(light.SENTINELS),
                accepted_run_count=25, repetitions=5, harness_commit=light.HARNESS_COMMIT,
                subjects={'instrumented': subject}, input_package_sha256=light.EXPECTED_PACKAGES['input'],
                index_package_sha256=light.EXPECTED_PACKAGES['index'],
                search=dict(benchmark_profile='pipeann-b9ec4ba', dataset_id='sift10m', data_type='uint8',
                            distance_metric='l2', k=10, l_search=100, mem_l=0, neighbor_type='pq', query_count=10000, search_mode=2),
                environment=dict(OMP_NUM_THREADS='REQUESTED_T', MKL_NUM_THREADS='8', OMP_DYNAMIC='FALSE',
                                 OMP_PROC_BIND=None, OMP_PLACES=None, GOMP_CPU_AFFINITY=None),
                pause={'after_finalized_run_s':5}, telemetry={'interval_s':1, 'collectors':list(light.COLLECTORS)},
                trace=dict(mode='LIGHT', causal_trace_enabled=True, detail_first_n=16, event_capacity=65536))
    records = []
    for rep, order in enumerate(light.ORDERS, 1):
        for config in order:
            run_id = str(rep)+config; conf=light.SENTINELS[config]
            q=light.query_aggregates(rows(run_id=run_id), 2, conf['wcap'], conf['threads'], run_id)
            q['query_count']=10000;q['per_query']={k:v/10000 for k,v in q['totals'].items()}
            h=dict.fromkeys((*light.ZERO_HEALTH, 'events_written', 'sample_requested', 'sample_observed'),0)
            h.update(q['totals'], trace_valid=True, trace_mode='LIGHT', query_rows=10000,
                     width_change_count=q['width_increase_total'], max_inflight=q['max_inflight'],
                     max_completed_hidden=q['max_completed_hidden'])
            m=dict(plan['search'], **conf, run_id=run_id, repetition=rep, benchmark_status='success', status='success',
                   trace_valid=True, subject_git_commit=subject['commit'], subject_repo_root=subject['root'],
                   subject_git_branch='research/p0-causal-instrumentation', subject_git_dirty=False,
                   executable_sha256='binary', executable='/test/PipeANN-p0/build/tests/search_disk_index',
                   harness_git_commit=plan['harness_commit'], harness_git_dirty=False,
                   harness_git_branch='research/g0b-sift10m-light-sentinels', harness_repo_root='/test/Parallel_ANN_Research',
                   input_package_manifest_sha256=plan['input_package_sha256'], index_package_manifest_sha256=plan['index_package_sha256'],
                   environment={'OMP_NUM_THREADS':str(conf['threads']),'MKL_NUM_THREADS':'8'},
                   trace_mode='LIGHT', causal_trace_enabled=True, trace_config=plan['trace'].copy(),
                   host_telemetry_requested=True, host_telemetry_option=True, telemetry_interval_s=1,
                   host_telemetry_collectors={c:dict(status='stopped',metric_rows=1) for c in light.COLLECTORS},
                   mlflow_enabled=True, mlflow_status='success', mlflow_run_id=run_id)
            s=dict(run_id=run_id, benchmark_status='success', trace_valid=True, run_status='success',
                   qps=100+rep, mean_latency_us=1000-rep, p99_latency_us=2000, recall=99.1, mean_ios=10)
            records.append(dict(round=rep, config=config, run_id=run_id, runner_return_code=0, mlflow_run_id=run_id,
                                manifest=m, summary=s, trace_health=h, queries=q,
                                telemetry_presence=dict.fromkeys(light.COLLECTORS,True)))
    return plan, records


class LightTests(unittest.TestCase):
    def test_exact_25_order(self):
        p,r=fixture();light.validate_records(r,p)
        self.assertEqual(light.analyze_records(r,p)['classification'],'G0B_COMPLETE')

    def reject(self, change, message):
        p,r=fixture();change(p,r)
        with self.assertRaisesRegex(ValueError,message):light.validate_records(r,p)

    def test_wrong_order(self):self.reject(lambda p,r:r.reverse(),'order')
    def test_missing_run(self):self.reject(lambda p,r:r.pop(),'Missing run')
    def test_duplicate_run(self):self.reject(lambda p,r:r[0].update(run_id=r[1]['run_id']),'Duplicate')
    def test_config_mismatch(self):self.reject(lambda p,r:r[0]['manifest'].update(threads=8),'configuration')
    def test_package_mismatch(self):self.reject(lambda p,r:r[0]['manifest'].update(input_package_manifest_sha256='wrong'),'Package')
    def test_plan_package_mismatch(self):self.reject(lambda p,r:p.update(input_package_sha256='wrong'),'package')
    def test_subject_mismatch(self):self.reject(lambda p,r:r[0]['manifest'].update(subject_git_commit='wrong'),'Subject')
    def test_harness_mismatch(self):self.reject(lambda p,r:r[0]['manifest'].update(harness_git_dirty=True),'Harness')
    def test_trace_false(self):self.reject(lambda p,r:r[0]['summary'].update(trace_valid=False),'Experiment')
    def test_drop(self):self.reject(lambda p,r:r[0]['trace_health'].update(events_dropped=1),'health')
    def test_outstanding(self):self.reject(lambda p,r:r[0]['trace_health'].update(outstanding_at_query_end=1),'health')
    def test_query_health_disagreement(self):self.reject(lambda p,r:r[0]['trace_health'].update(submitted=21),'aggregate')
    def test_telemetry_missing(self):self.reject(lambda p,r:r[0]['telemetry_presence'].update(iostat=False),'telemetry')
    def test_telemetry_disabled(self):self.reject(lambda p,r:r[0]['manifest'].update(host_telemetry_option=False),'telemetry')
    def test_runtime_affinity(self):self.reject(lambda p,r:r[0].update(runtime_snapshots=[{'benchmark_environment':{'OMP_PROC_BIND':'spread'}}]),'affinity')
    def test_environment_requested_t(self):self.reject(lambda p,r:r[0]['manifest']['environment'].update(OMP_NUM_THREADS='8'),'placement')
    def test_unavailable_fdinfo_allowed(self):
        p,r=fixture();r[0]['runtime_snapshots']=[{'benchmark_environment':None,'io_uring_fdinfo_available':False}];light.validate_records(r,p)
    def test_width_distribution(self):
        q=light.query_aggregates(rows(),2,32,1,'run');self.assertEqual(q['final_width_distribution'],{5:1,6:1});self.assertEqual(q['mean_final_width'],5.5)
    def test_wcap_fraction(self):
        data=rows();data[0].update(final_width=32,width_change_count=28)
        self.assertEqual(light.query_aggregates(data,2,32,1,'run')['ending_at_wcap_fraction'],.5)
    def test_width_increase_count_mismatch(self):
        data=rows();data[0]['width_change_count']=2
        with self.assertRaisesRegex(ValueError,'width count'):light.query_aggregates(data,2,32,1,'run')
    def test_duplicate_query(self):
        data=rows();data[1]['query_id']=0
        with self.assertRaisesRegex(ValueError,'duplicate'):light.query_aggregates(data,2,32,1,'run')
    def test_worker_tid_consistency(self):
        data=rows();data[1]['linux_tid']=2
        with self.assertRaisesRegex(ValueError,'Worker/TID'):light.query_aggregates(data,2,32,1,'run')

    def test_cache_physical_distinction(self):
        q=light.query_aggregates(rows(cache=2),2,32,1,'run')
        self.assertEqual(q['totals']['selected'],24);self.assertEqual(q['totals']['submitted'],20)
        self.assertEqual(q['totals']['cache_published'],4);self.assertEqual(q['published_not_expanded'],6)
    def test_cache_as_cqe_rejected(self):
        data=rows(cache=2);data[0]['cqe_seen']=12
        with self.assertRaisesRegex(ValueError,'lifecycle'):light.query_aggregates(data,2,32,1,'run')
    def test_run_level_descriptive(self):
        p,r=fixture();a=light.analyze_records(r,p)
        self.assertEqual(a['groups']['A']['metrics']['qps']['values'],[101,102,103,104,105])
        self.assertEqual(a['groups']['A']['metrics']['qps']['sample_sd'],statistics.stdev([101,102,103,104,105]))
        self.assertEqual(a['groups']['A']['metrics']['qps']['n'],5)
        self.assertEqual(a['D6'],'D6_INCONCLUSIVE');self.assertEqual(a['D1_observability'],'NO')
    def test_sample_sd_one_is_null(self):self.assertIsNone(light.descriptive([1])['sample_sd'])
    def test_nonfinite_rejected(self):
        with self.assertRaises(ValueError):light.descriptive([float('nan')])
    def test_short_telemetry_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/'system_metrics.csv').write_text('collector,entity,metric,sample_time_local\nmpstat,all,%sys,23:59:59\nmpstat,all,%sys,00:00:00\n')
            c=light.telemetry_coverage(p,1)['mpstat|all|%sys'];self.assertEqual(c['sample_count'],2);self.assertEqual(c['first_to_last_span_s'],1)
    def test_iso_telemetry_timestamps(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/'system_metrics.csv').write_text('collector,entity,metric,sample_time_local\niostat,nvme0n1,r/s,2026-10-09T13:38:27+0700\niostat,nvme0n1,r/s,2026-10-09T13:38:28+0700\n')
            c=light.telemetry_coverage(p,1)['iostat|nvme0n1|r/s'];self.assertEqual(c['sample_count'],2);self.assertEqual(c['first_to_last_span_s'],1)

    def test_corrupt_plan_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/'PLAN.json').write_text('{}');(p/'PLAN.sha256').write_text('bad PLAN.json')
            with self.assertRaisesRegex(ValueError,'SHA mismatch'):light.analyze_campaign(p)
    def test_required_checksum_coverage(self):
        p,_=fixture()
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);(folder/'SHA256SUMS').write_text('0  manifest.json\n')
            with self.assertRaisesRegex(ValueError,'checksum coverage'):
                light.load_light({'config':'A','run_directory':str(folder)},p)

    def test_missing_audit_invalid(self):
        p,r=fixture()
        p['frozen_at']='2026-01-01T00:00:00+00:00'
        for record in r:
            record['manifest'].update(timestamp_start='2026-01-02T00:00:00+00:00',timestamp_end='2026-01-02T00:00:01+00:00')
        with tempfile.TemporaryDirectory() as tmp:
            c=Path(tmp);(c/'PLAN.json').write_text(json.dumps(p));(c/'PLAN.sha256').write_text(light.digest(c/'PLAN.json')+' PLAN.json');(c/'results.json').write_text(json.dumps(r))
            with patch.object(light,'load_light',side_effect=lambda record,plan:record):
                with self.assertRaises(FileNotFoundError):light.analyze_campaign(c)


if __name__=='__main__':unittest.main()
