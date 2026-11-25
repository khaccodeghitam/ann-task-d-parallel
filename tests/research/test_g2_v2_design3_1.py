"""Offline regression and contract audit suite for G2 v2 controlled amendment design-3.1.

Never invokes any native ANN binary, never modifies frozen design-3/design-2 files,
never modifies preserved HOLD evidence (`axd-g2-v2-off-design3`), and never draws
performance/research conclusions from failed OFF timing.
"""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from research.task_da import g2_v2_design3_1_analyzer as a31
from research.task_da import g2_v2_design3_1_contract as c31
from research.task_da import g2_v2_design3_1_runner as r31
from research.task_da import g2_v2_design3_analyzer as a3
from research.task_da import g2_v2_design3_contract as c3
from research.task_da import g2_v2_design3_runner as r3

EVIDENCE_ROOT = Path('/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence')
HOLD_DIR = EVIDENCE_ROOT / 'axd-g2-v2-off-design3'
QUAL_PASS_PATH = EVIDENCE_ROOT / 'axd-g2-v2-design3-qualification-20261124T094602Z/qualification_result.json'
QUAL_HOLD_PATH = EVIDENCE_ROOT / 'axd-g2-v2-design3-qualification-20261124T082344Z/qualification_result.json'
QUALITY_JSON_PATH = EVIDENCE_ROOT / 'axd-g2-v2-quality-design3/quality.json'
DESIGN3_OFF_APPROVAL = EVIDENCE_ROOT / 'axd-g2-v2-approvals/design3_off_approval.json'


def make_valid_counters():
    return dict(
        distance_evaluations=15,
        unique_distance_evaluations=10,
        duplicate_distance_evaluations=5,
        expansions=3,
        unique_expansions=3,
        duplicate_expansions=0,
        neighbor_attempts=20,
        already_seen_attempts=6,
        frontier_insertions=10,
        sync_merge_count=2,
        sync_wait_ns=0,
        barrier_wait_ns=0,
        merge_time_ns=0,
        worker_idle_ns=0,
        per_worker_expansions=[2, 1],
        per_worker_distance_evaluations=[8, 7],
        per_worker_idle_rounds=[0, 1],
    )


def make_off_row(qid=0, *, policy='base'):
    visited, frontier = c31.POLICIES[policy]
    return dict(
        scope='task_d_a_common_p2_exploratory',
        graph_format='pipnn',
        entry=0,
        k=10,
        beam=432,
        workers=2,
        sync_interval=16,
        merge_impl='flat',
        visited_policy=visited,
        frontier_mode=frontier,
        jobs=1,
        mode='OFF',
        instrumentation=False,
        query_id=qid,
        complete_top_k=True,
        latency_ns=3000000,
        ids=list(range(10)),
        squared_l2=list(map(float, range(10))),
    )


def make_on_row(qid=0, *, policy='base'):
    row = make_off_row(qid=qid, policy=policy)
    row['mode'] = 'ON'
    row['instrumentation'] = True
    row['counters'] = make_valid_counters()
    return row


class CountersSchemaDiscriminationTests(unittest.TestCase):
    def test_classify_counters_distinguishes_all_four_states(self):
        off = make_off_row()
        self.assertEqual(a31.classify_counters_field(off), 'absent')
        self.assertEqual(a31.classify_counters_field(dict(off, counters=None)), 'explicit_null')
        self.assertEqual(a31.classify_counters_field(dict(off, counters={})), 'object')
        self.assertEqual(a31.classify_counters_field(dict(off, counters=make_valid_counters())), 'object')
        for bad in (0, 1, False, True, '', 'null', [], [1], 0.0):
            with self.subTest(bad=bad):
                self.assertEqual(a31.classify_counters_field(dict(off, counters=bad)), 'malformed')
        with self.assertRaises(ValueError):
            a31.classify_counters_field(['not', 'a', 'dict'])

    def test_off_schema_accepts_absent_and_rejects_explicit_null_nonnull_and_malformed(self):
        valid_off = [make_off_row(0), make_off_row(1)]
        digest, qids = a31.output_digest(valid_off, mode='OFF', policy='base')
        self.assertEqual(len(digest), 64)
        self.assertEqual(qids, [0, 1])

        # Explicit null MUST be explicitly distinguished and rejected (native p2_eval omits counters)
        explicit_null = [dict(make_off_row(0), counters=None)]
        with self.assertRaisesRegex(ValueError, 'explicit null'):
            a31.output_digest(explicit_null, mode='OFF', policy='base')

        # Non-null counters objects (populated or empty {}) MUST be rejected
        with self.assertRaisesRegex(ValueError, 'must not contain counters object'):
            a31.output_digest([dict(make_off_row(0), counters={})], mode='OFF', policy='base')
        with self.assertRaisesRegex(ValueError, 'must not contain counters object'):
            a31.output_digest([dict(make_off_row(0), counters=make_valid_counters())], mode='OFF', policy='base')

        # Malformed non-null counter scalars/lists MUST be rejected
        for bad in (0, False, True, '', 'null', [], 3.14):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(ValueError, 'malformed non-null counters'):
                    a31.output_digest([dict(make_off_row(0), counters=bad)], mode='OFF', policy='base')

        # Mode/instrumentation mismatch MUST be rejected
        with self.assertRaisesRegex(ValueError, 'mode/instrumentation'):
            a31.output_digest([dict(make_off_row(0), instrumentation=True)], mode='OFF', policy='base')

    def test_on_schema_accepts_valid_counters_and_rejects_absent_null_malformed_and_bad_invariants(self):
        valid_on = [make_on_row(0), make_on_row(1)]
        digest_on, qids_on = a31.output_digest(valid_on, mode='ON', policy='base')
        digest_off, qids_off = a31.output_digest([make_off_row(0), make_off_row(1)], mode='OFF', policy='base')
        # Exact same byte digest across ON and OFF for identical Top-10 outputs
        self.assertEqual(digest_on, digest_off)
        self.assertEqual(qids_on, qids_off)

        # Missing counters in ON -> rejected specifically as missing
        no_cnt = make_on_row(0)
        del no_cnt['counters']
        with self.assertRaisesRegex(ValueError, 'missing required counters'):
            a31.output_digest([no_cnt], mode='ON', policy='base')

        # Explicit null in ON -> rejected specifically as null
        with self.assertRaisesRegex(ValueError, 'must not be null'):
            a31.output_digest([dict(make_on_row(0), counters=None)], mode='ON', policy='base')

        # Malformed counters type in ON -> rejected
        for bad in (0, False, '', 'null', []):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(ValueError, 'must be a JSON object'):
                    a31.output_digest([dict(make_on_row(0), counters=bad)], mode='ON', policy='base')

        # Empty / missing key / extra key inside ON counters -> ValueError (never raw KeyError)
        with self.assertRaisesRegex(ValueError, 'key mismatch'):
            a31.output_digest([dict(make_on_row(0), counters={})], mode='ON', policy='base')
        partial = make_on_row(0)
        del partial['counters']['sync_merge_count']
        with self.assertRaisesRegex(ValueError, 'key mismatch'):
            a31.output_digest([partial], mode='ON', policy='base')
        extra_c = make_on_row(0)
        extra_c['counters']['unexpected'] = 0
        with self.assertRaisesRegex(ValueError, 'key mismatch'):
            a31.output_digest([extra_c], mode='ON', policy='base')

        # Bool masquerading as int inside counters -> rejected
        bool_c = make_on_row(0)
        bool_c['counters']['sync_merge_count'] = True
        with self.assertRaisesRegex(ValueError, 'strict integer'):
            a31.output_digest([bool_c], mode='ON', policy='base')

        # Broken algebraic counter invariant -> rejected
        bad_inv = make_on_row(0)
        bad_inv['counters']['distance_evaluations'] = 16
        bad_inv['counters']['unique_distance_evaluations'] = 11
        bad_inv['counters']['per_worker_distance_evaluations'] = [9, 7]
        with self.assertRaises(ValueError):
            a31.output_digest([bad_inv], mode='ON', policy='base')

    def test_malformed_records_and_unexpected_fields_fail_closed_with_value_error(self):
        # Empty / non-list / non-dict row
        for bad_rows in ([], [None], [['list']], ['{"mode":"OFF"}']):
            with self.subTest(bad_rows=bad_rows), self.assertRaises(ValueError):
                a31.output_digest(bad_rows, mode='OFF', policy='base')

        # Missing required row field -> ValueError (not KeyError)
        for field in ('mode', 'instrumentation', 'ids', 'squared_l2', 'query_id', 'complete_top_k'):
            row = make_off_row(0)
            del row[field]
            with self.subTest(missing=field), self.assertRaisesRegex(ValueError, 'missing required field'):
                a31.output_digest([row], mode='OFF', policy='base')

        # Unexpected / trace / typo fields -> rejected
        for extra_k, extra_v in [('rounds', []), ('trace_overflow', False), ('phase_audit', {}), ('counter', None)]:
            row = make_off_row(0)
            row[extra_k] = extra_v
            with self.subTest(extra=extra_k), self.assertRaisesRegex(ValueError, 'unexpected field'):
                a31.output_digest([row], mode='OFF', policy='base')

        # Bool masquerading as int for jobs/query_id/entry
        for field, val in [('jobs', True), ('query_id', True), ('entry', False)]:
            row = make_off_row(0)
            row[field] = val
            with self.subTest(field=field), self.assertRaises(ValueError):
                a31.output_digest([row], mode='OFF', policy='base')

        # Bad ids / distances / duplicate query_id
        with self.assertRaises(ValueError):
            a31.output_digest([dict(make_off_row(0), ids='0123456789')], mode='OFF', policy='base')
        with self.assertRaises(ValueError):
            a31.output_digest([dict(make_off_row(0), squared_l2=[float('nan')] + [1.0] * 9)],
                              mode='OFF', policy='base')
        with self.assertRaises(ValueError):
            a31.output_digest([make_off_row(0), make_off_row(0)], mode='OFF', policy='base')


class RealSavedHoldAndUpstreamEvidenceRegressionTests(unittest.TestCase):
    """Offline regression tests directly against preserved read-only HOLD and Quality ON evidence."""

    def test_reproduces_design3_keyerror_and_passes_design3_1_on_real_hold_evidence(self):
        self.assertTrue(HOLD_DIR.exists(), 'preserved HOLD evidence directory required')
        start = json.loads((HOLD_DIR / 'start.json').read_text())
        item = start['plan'][0]
        pdir = HOLD_DIR / item['name']
        manifest = json.loads((pdir / 'manifest.json').read_text())
        quality = json.loads(QUALITY_JSON_PATH.read_text())

        # 1. Confirm frozen design-3 still reproduces the exact KeyError('counters')
        with self.assertRaises(KeyError) as ctx:
            r3.process_result(item, pdir, start['artifacts'], manifest, phase='off')
        self.assertEqual(ctx.exception.args, ('counters',))

        # 2. Confirm design-3.1 parses all 10,000 real OFF rows, passes process_result,
        #    validates against axd_g2_v2.3.1 process schema, and passes exact ON/OFF parity!
        rec = r31.process_result(item, pdir, start['artifacts'], manifest, phase='off')
        c31.validate_schema(rec, 'process')
        self.assertEqual(rec['schema'], c31.SCHEMA)
        self.assertEqual(rec['revision'], c31.REVISION)
        self.assertEqual(rec['mode'], 'OFF')
        self.assertEqual(rec['query_count'], 10000)
        self.assertEqual(rec['rss_kib'], 871544)
        self.assertEqual(rec['output_digest'], quality['graphs']['stock_off_r1']['output_digest'])
        # Exact parity check against real Quality ON reference (10,000 queries)
        r31.check_reference(rec, quality)

    def test_reused_design3_qualification_and_quality_on_pass_design3_1_contracts(self):
        freeze = c31.load_freeze(environment=True)
        qual = r31.verify_qualification(QUAL_PASS_PATH, freeze=freeze)
        self.assertEqual(qual['verdict'], 'QUALIFICATION_PASS')
        self.assertEqual(qual['revision'], 'design-3')

        # QUALIFICATION_HOLD must be rejected
        with self.assertRaises(ValueError):
            r31.verify_qualification(QUAL_HOLD_PATH, freeze=freeze)

        # Real 18/18 Quality ON campaign passes design-3.1 quality_context
        artifacts_sha = c31.sha(c31.ROOT / 'configs/axd_g2_v2_design3_artifacts.proposed.json')
        qual_sha = c31.sha(QUAL_PASS_PATH)
        quality = r31.quality_context(
            QUALITY_JSON_PATH,
            expected_artifacts_sha256=artifacts_sha,
            expected_qualification_sha256=qual_sha,
        )
        self.assertTrue(quality['A_pass'] and quality['B_pass'] and quality['parity'] and quality['duplicate_reduction'])

        # Mismatched upstream artifacts_sha256 or qualification_sha256 must fail closed
        with self.assertRaises(ValueError):
            r31.quality_context(QUALITY_JSON_PATH, expected_artifacts_sha256='0' * 64)
        with self.assertRaises(ValueError):
            r31.quality_context(QUALITY_JSON_PATH, expected_qualification_sha256='0' * 64)

        # Spot-check real Quality ON output files with design-3.1 strict ON validator
        for policy in ('base', 'opt'):
            ref = quality['graphs']['stock_off_r1']['references'][policy]
            rows_on = a31.output_rows(ref['path'])
            digest_on, qids_on = a31.output_digest(rows_on, mode='ON', policy=policy)
            self.assertEqual(len(qids_on), 10000)
            self.assertEqual(digest_on, quality['graphs']['stock_off_r1']['output_digest'])


class Design31AuthorizationFreezeAndMathParityTests(unittest.TestCase):
    def test_rejects_design2_design3_unapproved_and_hold_directory_and_accepts_valid_3_1(self):
        freeze_sha = c31.sha(c31.FREEZE)
        artifacts_sha = c31.sha(c31.ROOT / 'configs/axd_g2_v2_design3_artifacts.proposed.json')
        qual_sha = c31.sha(QUAL_PASS_PATH)
        quality_sha = c31.sha(QUALITY_JSON_PATH)
        new_out = EVIDENCE_ROOT / 'axd-g2-v2-off-design3_1'

        # Signed design-3 OFF approval MUST be strictly rejected
        d3_signed = json.loads(DESIGN3_OFF_APPROVAL.read_text())
        with self.assertRaisesRegex(ValueError, 'design-3.1 approval required'):
            c31.authorize(d3_signed, freeze_sha, artifacts_sha, 'off', new_out,
                          qualification_digest=qual_sha, quality_digest=quality_sha)

        # Unsigned design-3.1 template MUST be rejected
        tmpl = json.loads((c31.ROOT / 'configs/axd_g2_v2_design3_1_approval.UNAPPROVED.json').read_text())
        with self.assertRaises(ValueError):
            c31.authorize(tmpl, freeze_sha, artifacts_sha, 'off', new_out,
                          qualification_digest=qual_sha, quality_digest=quality_sha)

        # Valid design-3.1 approval targeting preserved HOLD dir MUST be rejected
        ap_hold = dict(
            schema=c31.SCHEMA,
            protocol=c31.PROTOCOL,
            revision=c31.REVISION,
            owner='FIXTURE_OWNER',
            approved_at='2026-11-25T00:30:00+07:00',
            freeze_sha256=freeze_sha,
            parent_design3_freeze_sha256=c31.PARENT_DESIGN3_FREEZE_SHA256,
            artifacts_sha256=artifacts_sha,
            qualification_sha256=qual_sha,
            quality_sha256=quality_sha,
            output_directory=str(HOLD_DIR.resolve()),
            scope='OFF_AB',
            quota_s=10800,
            quiet_host_confirmed=True,
        )
        with self.assertRaisesRegex(ValueError, 'OFF_EXECUTION_HOLD'):
            c31.authorize(ap_hold, freeze_sha, artifacts_sha, 'off', HOLD_DIR,
                          qualification_digest=qual_sha, quality_digest=quality_sha)

        # Valid design-3.1 approval targeting fresh output dir PASSES
        ap_ok = dict(ap_hold, output_directory=str(new_out.resolve()))
        self.assertEqual(
            c31.authorize(ap_ok, freeze_sha, artifacts_sha, 'off', new_out,
                          qualification_digest=qual_sha, quality_digest=quality_sha),
            'OFF_AB',
        )

    def test_analyze_estimands_identical_to_design3_and_plan_matches_144_off(self):
        from tests.research.test_g2_v2_design3 import fixture_d3
        rows, latency, quality = fixture_d3()
        build = {g: dict(wall_s=42.0 if g.startswith('stock') else 34.0, graph_bytes=200000000) for g in c31.GRAPHS}
        real_b3 = a3.bootstrap
        with patch.object(a3, 'bootstrap', side_effect=lambda x, **kw: real_b3(x, resamples=64, **kw)):
            out3 = a3.analyze(rows, latency, quality, build=build)
            out31 = a31.analyze(rows, latency, quality, build=build)
        c31.validate_schema(out31, 'analysis')
        self.assertEqual(out31['schema'], 'axd_g2_v2.3.1')
        self.assertEqual(out31['revision'], 'design-3.1')
        for k, v in out3.items():
            if k in ('schema', 'revision'):
                continue
            self.assertEqual(out31[k], v, f'drift in analysis field: {k}')

        # 144-OFF schedule is identical to frozen design-3 except output directory
        artifacts = {k: '/missing/' + k for k in ['binary', 'base', 'queries', 'val', 'test', 'warmup']}
        artifacts['graphs'] = {g: '/missing/' + g for g in c31.GRAPHS}
        with patch.object(Path, 'open', side_effect=AssertionError('plan opened a file')):
            p3 = r3.plan(artifacts, 'off', '/future/off')
            p31 = r31.plan(artifacts, 'off', '/future/off')
        self.assertEqual(p3, p31)
        self.assertEqual(len(p31), 144)

    def test_freeze_tamper_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'comp.py').write_text('v1\n')
            f = dict(
                protocol=c31.PROTOCOL,
                revision=c31.REVISION,
                schema=c31.SCHEMA,
                beam=432,
                cpus=[0, 2],
                workers=2,
                components={'comp.py': c31.sha(root / 'comp.py')},
            )
            fp = root / 'freeze.json'
            fp.write_text(json.dumps(f))
            with patch.object(c31, 'ROOT', root):
                c31.load_freeze(fp, environment=False, check_parent=False)
                (root / 'comp.py').write_text('tampered\n')
                with self.assertRaises(ValueError):
                    c31.load_freeze(fp, environment=False, check_parent=False)


if __name__ == '__main__':
    unittest.main()
