import copy
import importlib.util
import json
from pathlib import Path
import random
import unittest
import tempfile

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('g0', ROOT / 'tools/research/analyze_g0_causal.py')
g0 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g0)


def fixture(qid=0, worker=0):
    def event(kind, time, **fields):
        return dict(event=kind, timestamp_ns=time, query_id=qid, worker_id=worker,
                    linux_tid=100 + worker, **fields)
    request = dict(request_seq=1, node_id=10, request_key=20)
    return [event('QUERY_START', 0), event('WIDTH_INIT', 1000, width=4, wcap=5),
            event('IO_SELECT', 2000, **request), event('IO_SUBMIT', 3000, **request),
            event('IO_CQE_SEEN', 5000, **request), event('WIDTH_CHANGE', 6000, old_width=4, width=5, wcap=5),
            event('IO_PUBLISH', 7000, **request), event('QUERY_END', 10000, outstanding_correlations=0),
            event('TRACE_HEALTH', 10000, outstanding_correlations=0)]


class QueryTests(unittest.TestCase):
    def test_out_of_order_jsonl(self):
        events = fixture(); random.Random(17).shuffle(events)
        decoded = [json.loads(line) for line in '\n'.join(json.dumps(e) for e in events).splitlines()]
        self.assertEqual(g0.analyze_events(decoded), g0.analyze_events(fixture()))

    def test_equal_timestamps(self):
        events = fixture()
        for e in events:
            if e['event'] in ('IO_SELECT', 'IO_SUBMIT', 'IO_CQE_SEEN', 'IO_PUBLISH'):
                e['timestamp_ns'] = 3000
        events.reverse()
        q = g0.analyze_events(events)['queries'][0]
        self.assertEqual(q['publication_hol_us']['p95'], 0)
        self.assertEqual(q['time_weighted']['mean_hidden'], 0)
        self.assertIsNone(q['request_metrics'][0]['hol_to_observed_io_ratio'])

    def test_submit_cqe_publish_reconstruction(self):
        q = g0.analyze_events(fixture())['queries'][0]
        self.assertEqual(q['request_metrics'][0]['observed_io_us'], 2)
        self.assertEqual(q['request_metrics'][0]['publication_hol_us'], 2)
        self.assertEqual(q['time_weighted']['mean_device_outstanding'], .2)
        self.assertEqual(q['time_weighted']['mean_total_unpublished'], .4)

    def test_time_weighted_hidden(self):
        q = g0.analyze_events(fixture())['queries'][0]
        self.assertEqual(q['time_weighted']['mean_hidden'], .2)
        self.assertEqual(q['time_weighted']['fraction_hidden_gt0'], .2)
        self.assertEqual(q['time_weighted']['fraction_hidden_ge2'], 0)
        self.assertEqual(q['time_weighted']['max_hidden'], 1)

    def test_width_residency(self):
        width = g0.analyze_events(fixture())['queries'][0]['width']
        self.assertEqual(width['initial'], 4)
        self.assertEqual(width['final'], 5)
        self.assertEqual(width['changes'], 1)
        self.assertAlmostEqual(width['time_weighted_mean'], 40/9)
        self.assertEqual(width['unknown_fraction'], .1)
        self.assertEqual(width['bucket_fractions']['1-4'], .5)
        self.assertEqual(width['bucket_fractions']['5-8'], .4)

    def test_wcap_residency(self):
        width = g0.analyze_events(fixture())['queries'][0]['width']
        self.assertEqual(width['fraction_at_wcap'], .4)
        self.assertEqual(width['fraction_above32'], 0)

    def test_negative_snapshot_rejected(self):
        events = fixture(); events[4]['completed_hidden'] = -1
        with self.assertRaisesRegex(ValueError, 'Negative hidden'):
            g0.analyze_events(events)

    def test_cqe_before_submit_rejected(self):
        events = fixture(); events[4]['timestamp_ns'] = 2500
        with self.assertRaisesRegex(ValueError, 'order violation'):
            g0.analyze_events(events)

    def test_publish_before_cqe_rejected(self):
        events = fixture(); events[6]['timestamp_ns'] = 4000
        with self.assertRaisesRegex(ValueError, 'order violation'):
            g0.analyze_events(events)

    def test_duplicate_sequence_rejected(self):
        events = fixture(); events.insert(3, copy.deepcopy(events[2]))
        with self.assertRaisesRegex(ValueError, 'request_seq'):
            g0.analyze_events(events)

    def test_unfinished_request_rejected(self):
        events = [e for e in fixture() if e['event'] != 'IO_PUBLISH']
        with self.assertRaisesRegex(ValueError, 'Unfinished'):
            g0.analyze_events(events)

    def test_missing_optional_expansion(self):
        q = g0.analyze_events(fixture())['queries'][0]
        self.assertEqual(q['logical_work']['expanded'], 0)
        self.assertEqual(q['logical_work']['published_not_expanded'], 1)

    def test_width_decrease_and_jump_rejected(self):
        for value in (3, 6):
            events = fixture(); events[5]['width'] = value
            with self.assertRaisesRegex(ValueError, 'Width decrease/jump'):
                g0.analyze_events(events)

    def test_multiple_workers_and_queries(self):
        events = fixture(8, 2) + fixture(3, 1)
        random.Random(5).shuffle(events)
        result = g0.analyze_events(events)
        self.assertEqual([q['query_id'] for q in result['queries']], [3, 8])
        self.assertEqual([q['worker_id'] for q in result['queries']], [1, 2])
        self.assertEqual(result['publication_hol_us']['n'], 2)

    def test_health_contradiction_rejected(self):
        events = fixture(); events[-1]['submitted'] = 50
        with self.assertRaisesRegex(ValueError, 'contradicts'):
            g0.analyze_events(events)

    def test_worker_change_rejected(self):
        events = fixture(); events[3]['worker_id'] = 2
        with self.assertRaisesRegex(ValueError, 'identity changed'):
            g0.analyze_events(events)

    def test_cache_path_separate(self):
        events = fixture()
        events = [e for e in events if e['event'] != 'IO_SUBMIT']
        next(e for e in events if e['event'] == 'IO_CQE_SEEN')['event'] = 'IO_CACHE_READY'
        q = g0.analyze_events(events)['queries'][0]
        self.assertEqual(q['logical_work']['cache_published'], 1)
        self.assertEqual(q['time_weighted']['mean_hidden'], 0)
        self.assertEqual(q['publication_hol_us']['n'], 0)

    def test_hol_percentiles(self):
        result = g0.quantiles([0, 10, 20, 30])
        self.assertEqual(result['p50'], 15)
        self.assertAlmostEqual(result['p95'], 28.5)
        self.assertAlmostEqual(result['p99'], 29.7)
        self.assertEqual(result['max'], 30)

    def test_fifo_rejected(self):
        events = fixture()
        second = copy.deepcopy(events[2]); second.update(timestamp_ns=2200, request_seq=2, node_id=11, request_key=21)
        submitted = copy.deepcopy(second); submitted.update(event='IO_SUBMIT', timestamp_ns=3500)
        cqe = copy.deepcopy(second); cqe.update(event='IO_CQE_SEEN', timestamp_ns=5500)
        pub = copy.deepcopy(second); pub.update(event='IO_PUBLISH', timestamp_ns=6500)
        with self.assertRaisesRegex(ValueError, 'FIFO'):
            g0.analyze_events(events + [second, submitted, cqe, pub])


class ChecksumTests(unittest.TestCase):
    def test_nested_telemetry_checksum(self):
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            (directory / 'telemetry').mkdir()
            path = directory / 'telemetry/iostat.log'; path.write_text('evidence')
            (directory / 'SHA256SUMS').write_text(g0.digest(path) + '  telemetry/iostat.log\n')
            g0.verify_sums(directory)
            path.write_text('changed')
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                g0.verify_sums(directory)

    def test_checksum_cannot_escape_run(self):
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name); run = directory / 'run'; run.mkdir()
            path = directory / 'other'; path.write_text('outside')
            (run / 'SHA256SUMS').write_text(g0.digest(path) + '  ../other\n')
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                g0.verify_sums(run)


class GroupAndGateTests(unittest.TestCase):
    thresholds = dict(OFF_vs_STOCK_percent=3, LIGHT_vs_OFF_percent=5,
                      metrics=['qps', 'mean_latency_us'], recall_max_range_percentage_points=.02)

    def records(self):
        return [dict(stage='A', case=case, repetition=i, summary=dict(qps=100, mean_latency_us=100,
                    p99_latency_us=150, mean_ios=50, recall=99, run_status='success', trace_valid=case != 'STOCK'))
                for case in ('STOCK', 'OFF', 'LIGHT') for i in range(1, 6)]

    def test_multiple_runs_cluster_grouping(self):
        records = self.records()
        records[0]['summary']['qps'] = 200
        grouped = g0.group_runs(records)
        self.assertEqual(grouped['A/STOCK']['qps']['n'], 5)
        self.assertEqual(grouped['A/STOCK']['qps']['values'], [200, 100, 100, 100, 100])
        self.assertEqual(grouped['A/OFF']['qps']['values'], [100]*5)
        self.assertEqual(grouped['A/STOCK']['qps']['sample_sd'], g0.statistics.stdev([200,100,100,100,100]))

    def test_run_query_clusters_not_flattened(self):
        runs = [g0.analyze_events(fixture(0) + fixture(1)), g0.analyze_events(fixture(0))]
        self.assertEqual([len(r['queries']) for r in runs], [2, 1])
        self.assertEqual([r['publication_hol_us']['n'] for r in runs], [2, 1])

    def test_detail_configuration_preserves_run_clusters(self):
        records = [dict(case='B', run_id=str(i), detail=g0.analyze_events(fixture(0))) for i in range(3)]
        result = g0.detail_distributions(records)['B']
        self.assertEqual(result['p95_publication_hol_us']['n'], 3)
        self.assertEqual(result['query_counts'], [1, 1, 1])
        self.assertEqual(result['run_ids'], ['0', '1', '2'])

    def test_e0_valid_proceeds(self):
        self.assertEqual(g0.e0_gate(self.records(), self.thresholds)['status'], 'PROCEED')

    def test_e0_noise_priority_preserves_recall_failure(self):
        records = self.records(); records[0]['summary'].update(qps=104, recall=99.03)
        gate = g0.e0_gate(records, self.thresholds)
        self.assertEqual(gate['status'], 'INCONCLUSIVE')
        self.assertFalse(gate['recall_guard_pass'])
        self.assertTrue(gate['performance_margins_pass'])

    def test_e0_noise_at_boundary(self):
        records = self.records(); records[0]['summary']['qps'] = 103
        self.assertEqual(g0.e0_gate(records, self.thresholds)['status'], 'INCONCLUSIVE')

    def test_e0_invalid_trace_fails(self):
        records = self.records(); records[-1]['summary']['trace_valid'] = False
        self.assertEqual(g0.e0_gate(records, self.thresholds)['status'], 'FAIL')

    def test_e0_missing_repetition(self):
        self.assertEqual(g0.e0_gate(self.records()[:-1], self.thresholds)['status'], 'INCONCLUSIVE')

    def test_e0_quiet_median_exceeds_limit(self):
        records = self.records()
        for r in records:
            if r['case'] == 'OFF': r['summary']['qps'] = 104
        self.assertEqual(g0.e0_gate(records, self.thresholds)['status'], 'FAIL')

    def d6(self, hol=2, hidden=.01):
        return {c: [dict(repetition=i, detail=dict(analysis_valid=True,
                  publication_hol_us=dict(p95=hol if c != 'B' else 2), observed_io_us=dict(p95=100),
                  hidden_gt0_fraction=hidden)) for i in (1,2,3)] for c in ('B','C','D')}

    d6_thresholds = dict(hol_relative_factor=2, majority=2, material_scale_ratio=.25,
                         material_hidden_fraction=.25, low_ratio=.1, low_hidden_fraction=.1)

    def test_d6_low(self):
        self.assertEqual(g0.d6_gate(self.d6(), self.d6_thresholds)['classification'], 'D6_LOW')

    def test_d6_material(self):
        self.assertEqual(g0.d6_gate(self.d6(hol=25), self.d6_thresholds)['classification'], 'D6_MATERIAL')

    def test_d6_material_hidden_alternative(self):
        self.assertEqual(g0.d6_gate(self.d6(hol=4, hidden=.25), self.d6_thresholds)['classification'], 'D6_MATERIAL')

    def test_d6_missing_is_inconclusive(self):
        self.assertEqual(g0.d6_gate({}, self.d6_thresholds)['classification'], 'D6_INCONCLUSIVE')

    def test_d6_middle_is_inconclusive(self):
        self.assertEqual(g0.d6_gate(self.d6(hol=15), self.d6_thresholds)['classification'], 'D6_INCONCLUSIVE')


if __name__ == '__main__':
    unittest.main()
