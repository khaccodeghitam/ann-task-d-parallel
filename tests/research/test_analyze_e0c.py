import importlib.util
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(os.environ.get('E0C_REPO', str(Path(__file__).resolve().parents[2])))
SCRIPT = Path(os.environ.get('E0C_ANALYZER_UNDER_TEST', str(ROOT / 'tools/research/analyze_e0c.py')))
sys.path.insert(0, str(SCRIPT.parent))
sys.path.insert(0, str(ROOT / 'tests/research'))
spec = importlib.util.spec_from_file_location('native', SCRIPT)
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)
from test_analyze_e0b import fixture as paired_fixture


def fixture():
    plan, records = paired_fixture()
    plan['environment'].update(native.NATIVE_ENVIRONMENT)
    plan['native_sanity'] = dict(native.SANITY_THRESHOLDS)
    for record in records:
        record['manifest']['environment'].update(native.NATIVE_ENVIRONMENT)
        record['summary'].update(qps=5000, mean_latency_us=1600)
    return plan, records


class NativeE0Tests(unittest.TestCase):
    def test_unbound_environment(self):
        plan, records = fixture()
        native.validate_native_environment(records, plan)
        native.paired.validate_records(records, plan)

    def reject_placement(self, key, value, plan_only=False):
        plan, records = fixture()
        if plan_only:
            plan['environment'][key] = value
        else:
            records[0]['manifest']['environment'][key] = value
        with self.assertRaisesRegex(ValueError, 'Native/unbound'):
            native.validate_native_environment(records, plan)

    def test_proc_bind_set_rejected(self):
        self.reject_placement('OMP_PROC_BIND', 'spread')

    def test_places_set_rejected(self):
        self.reject_placement('OMP_PLACES', 'threads')

    def test_gomp_affinity_set_rejected(self):
        self.reject_placement('GOMP_CPU_AFFINITY', '0-7')

    def test_bound_plan_rejected(self):
        self.reject_placement('OMP_PROC_BIND', 'spread', plan_only=True)

    def test_places_plan_rejected(self):
        self.reject_placement('OMP_PLACES', 'threads', plan_only=True)

    def test_gomp_plan_rejected(self):
        self.reject_placement('GOMP_CPU_AFFINITY', '0-7', plan_only=True)

    def test_empty_setting_is_not_unset(self):
        self.reject_placement('OMP_PROC_BIND', '')

    def test_dynamic_setting_rejected(self):
        self.reject_placement('OMP_DYNAMIC', 'TRUE')

    def test_missing_explicit_unset_in_plan(self):
        plan, records = fixture()
        del plan['environment']['GOMP_CPU_AFFINITY']
        with self.assertRaisesRegex(ValueError, 'GOMP_CPU_AFFINITY'):
            native.validate_native_environment(records, plan)

    def test_runtime_environment_checked(self):
        plan, records = fixture()
        observed = dict(native.NATIVE_ENVIRONMENT)
        observed['OMP_PROC_BIND'] = 'true'
        records[0]['runtime_snapshots'] = [{'benchmark_environment': observed}]
        with self.assertRaisesRegex(ValueError, 'process environment'):
            native.validate_native_environment(records, plan)

    def test_unavailable_kernel_metadata_is_diagnostic(self):
        plan, records = fixture()
        records[0]['runtime_snapshots'] = [{'benchmark_environment': None,
                                          'io_uring_fdinfo_available': False}]
        native.validate_native_environment(records, plan)

    def test_native_sanity_pass(self):
        plan, records = fixture()
        self.assertTrue(native.native_sanity(records, plan)['pass'])

    def test_native_sanity_inclusive_boundary(self):
        plan, records = fixture()
        for r in records:
            r['summary'].update(qps=2471.42, mean_latency_us=3212.82)
        self.assertTrue(native.native_sanity(records, plan)['pass'])

    def test_native_sanity_qps_fail(self):
        plan, records = fixture()
        for r in records:
            r['summary']['qps'] = 100
        result = native.analyze_records(records, plan)
        self.assertFalse(result['native_regime_sanity']['pass'])
        self.assertEqual(result['relative_classification'], 'PROCEED')
        self.assertEqual(result['classification'], 'E0C_INCONCLUSIVE')

    def test_native_sanity_latency_fail(self):
        plan, records = fixture()
        for r in records:
            r['summary']['mean_latency_us'] = 5000
        self.assertFalse(native.native_sanity(records, plan)['pass'])

    def test_sanity_threshold_change_rejected(self):
        plan, records = fixture()
        plan['native_sanity']['stock_median_qps_min'] = 100
        with self.assertRaisesRegex(ValueError, 'thresholds differ'):
            native.native_sanity(records, plan)

    def test_paired_proceed(self):
        plan, records = fixture()
        self.assertEqual(native.analyze_records(records, plan)['classification'], 'E0C_PROCEED')

    def test_paired_fail(self):
        plan, records = fixture()
        for r in records:
            if r['case'] != 'STOCK':
                r['summary']['qps'] = 5500
        self.assertEqual(native.analyze_records(records, plan)['classification'], 'E0C_FAIL')

    def test_paired_inconclusive(self):
        plan, records = fixture()
        for r in records:
            if r['case'] != 'STOCK':
                r['summary']['qps'] = 4700 if r['block'] <= 6 else 5300
        self.assertEqual(native.analyze_records(records, plan)['classification'], 'E0C_INCONCLUSIVE')

    def test_recall_boundary_gate(self):
        plan, records = fixture()
        for r in records:
            if r['case'] != 'STOCK':
                r['summary']['recall'] = 99.16
        self.assertEqual(native.analyze_records(records, plan)['classification'], 'E0C_PROCEED')

    def test_recall_fail(self):
        plan, records = fixture()
        for r in records:
            if r['case'] != 'STOCK':
                r['summary']['recall'] = 99.17
        self.assertEqual(native.analyze_records(records, plan)['classification'], 'E0C_FAIL')

    def test_invalid_trace_overrides_sanity_failure(self):
        plan, records = fixture()
        for r in records:
            r['summary']['qps'] = 100
        records[1]['summary']['trace_valid'] = False
        self.assertEqual(native.analyze_records(records, plan)['classification'], 'E0C_FAIL')

    def test_wrong_order(self):
        plan, records = fixture()
        records[0], records[1] = records[1], records[0]
        with self.assertRaisesRegex(ValueError, 'order violation'):
            native.analyze_records(records, plan)

    def test_missing_block(self):
        plan, records = fixture()
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            native.analyze_records(records[:-3], plan)

    def test_telemetry_mismatch(self):
        plan, records = fixture()
        records[0]['telemetry_presence']['mpstat'] = False
        with self.assertRaisesRegex(ValueError, 'telemetry presence'):
            native.analyze_records(records, plan)

    def test_package_mismatch(self):
        plan, records = fixture()
        records[0]['manifest']['input_package_manifest_sha256'] = 'bad'
        with self.assertRaisesRegex(ValueError, 'Package mismatch'):
            native.analyze_records(records, plan)

    def test_subject_mismatch(self):
        plan, records = fixture()
        records[0]['manifest']['subject_git_commit'] = 'bad'
        with self.assertRaisesRegex(ValueError, 'provenance mismatch'):
            native.analyze_records(records, plan)

    def test_bootstrap_unchanged(self):
        self.assertEqual(native.paired.bootstrap_median(list(range(12))), [3, 8])


if __name__ == '__main__':
    unittest.main()
