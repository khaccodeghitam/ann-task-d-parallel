"""Synthetic graph-format and exact-oracle tests; no ANN benchmark evidence."""
import json
import os
from pathlib import Path
import random
import struct
import subprocess
import sys
import tempfile
import unittest

from research.task_da.graph_audit import Graph, audit, compare, convert, sha256
from research.task_da.preflight import check_artifact, preflight
from research.task_da.evaluate_smoke import evaluate
from research.task_da.evaluate_p1 import evaluate_p1, check_on_off_parity
from research.task_da.evaluate_p2 import evaluate_p2, check_p2_on_off_parity, validate_p2_counters_row


def pipnn(path, edges, maximum=None):
    values = [len(edges), max(map(len, edges)) if maximum is None else maximum]
    values += list(map(len, edges))
    values += [x for row in edges for x in row]
    path.write_bytes(struct.pack('<' + 'I' * len(values), *values))


def fbin(path, rows):
    path.write_bytes(struct.pack('<II', len(rows), len(rows[0])) +
                     b''.join(struct.pack('<' + 'f' * len(row), *row) for row in rows))


class GraphTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.path = self.root / 'input.pipnn'
        self.edges = [[2, 1, 2, 0], [2], [0], []]
        pipnn(self.path, self.edges, maximum=8)

    def test_structural_audit_preserves_non_simple_directed_graph(self):
        with Graph(self.path, 'pipnn', entry=0, expected_n=4) as g:
            result = audit(g)
            self.assertEqual([g.neighbors(i) for i in range(4)], self.edges)
            self.assertEqual(result['arcs'], 6)
            self.assertEqual(result['self_loops'], 1)
            self.assertEqual(result['duplicate_arcs'], 1)
            self.assertEqual(result['reachable_from_entry'], 3)
            self.assertEqual(result['degree_histogram'], {0: 1, 1: 2, 4: 1})
            self.assertEqual(result['degree_p95'], 4)
            self.assertEqual(result['declared_max_degree'], 8)

    def test_roundtrip_is_byte_exact_and_has_per_node_digests(self):
        nsg, back, digests = self.root/'converted.nsg', self.root/'back.pipnn', self.root/'nodes.jsonl'
        with Graph(self.path, 'pipnn', entry=0) as before:
            self.assertEqual(convert(before, nsg, 'nsg')['status'], 'PASS')
            with Graph(nsg, 'nsg', expected_n=4) as after:
                self.assertEqual(compare(before, after, digests)['status'], 'PASS')
                convert(after, back, 'pipnn')
        self.assertEqual(back.read_bytes(), self.path.read_bytes())
        rows = [json.loads(x) for x in digests.read_text().splitlines()]
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(r['before_sha256'] == r['after_sha256'] for r in rows))

    def test_order_change_and_entry_change_fail_semantic_parity(self):
        other = self.root/'other.pipnn'
        pipnn(other, [[1, 2, 2, 0], [2], [0], []], 8)
        with Graph(self.path, 'pipnn', entry=0) as a, Graph(other, 'pipnn', entry=0) as b:
            self.assertEqual(compare(a, b)['changed_nodes'], [0])
            self.assertEqual(compare(a, b)['status'], 'NO-GO')
        with Graph(self.path, 'pipnn', entry=0) as a, Graph(self.path, 'pipnn', entry=1) as b:
            self.assertEqual(compare(a, b)['status'], 'NO-GO')

    def test_missing_or_invalid_entry_count_and_format_rejected(self):
        for kwargs in ({}, {'entry': -1}, {'entry': 4}, {'entry': True}, {'entry': 0, 'expected_n': 5}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                Graph(self.path, 'pipnn', **kwargs)
        with self.assertRaises(ValueError):
            Graph(self.path, 'unknown', entry=0)

    def test_malformed_files_fail_closed(self):
        valid = self.path.read_bytes()
        cases = [valid[:i] for i in range(len(valid))]
        cases += [valid + b'\0\0\0\0', struct.pack('<II', 0xffffffff, 8),
                  valid[:4] + struct.pack('<I', 1) + valid[8:],
                  valid[:-4] + struct.pack('<I', 4)]
        for i, data in enumerate(cases):
            bad = self.root/'bad'
            bad.write_bytes(data)
            with self.subTest(case=i), self.assertRaises(ValueError):
                Graph(bad, 'pipnn', entry=0)

    def test_nsg_requires_count_rejects_truncation_override_and_extra(self):
        nsg = self.root/'g.nsg'
        with Graph(self.path, 'pipnn', entry=0) as g:
            convert(g, nsg, 'nsg')
        for kwargs in ({}, {'expected_n': 3}, {'expected_n': 4, 'entry': 1}, {'expected_n': 5}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                Graph(nsg, 'nsg', **kwargs)
        raw = nsg.read_bytes()
        for length in range(len(raw)):
            nsg.write_bytes(raw[:length])
            with self.subTest(length=length), self.assertRaises(ValueError):
                Graph(nsg, 'nsg', expected_n=4)

    def test_output_is_never_overwritten(self):
        with Graph(self.path, 'pipnn', entry=0) as g, self.assertRaises(FileExistsError):
            convert(g, self.path, 'nsg')

    def test_empty_adjacency_valid_singleton(self):
        pipnn(self.path, [[]])
        with Graph(self.path, 'pipnn', entry=0) as g:
            self.assertEqual(audit(g)['reachable_from_entry'], 1)

    def test_artifact_hash_not_presence_determines_availability(self):
        item = dict(path='input.pipnn', reported_sha256=sha256(self.path))
        self.assertEqual(check_artifact(item, self.root)['status'], 'AVAILABLE')
        item['reported_sha256'] = '0' * 64
        self.assertEqual(check_artifact(item, self.root)['status'], 'NO-GO')
        item['path'] = None
        self.assertEqual(check_artifact(item, self.root)['status'], 'MISSING')
        item['reported_sha256'] = None
        self.assertEqual(check_artifact(item, self.root)['status'], 'NOT_VERIFIED')

    def test_manifest_cannot_promote_missing_artifacts_to_pass(self):
        manifest = json.loads((Path(__file__).parents[2]/'docs/research/task-da/experiment_manifest.yaml').read_text())
        report = preflight(manifest, self.root)
        self.assertEqual(report['P0'], 'HOLD')
        self.assertEqual(report['P1'], 'HOLD')
        self.assertFalse(report['benchmark_executed'])
        self.assertTrue(all(r['status'] == 'MISSING' for r in report['artifacts'].values()))


class RecallTests(unittest.TestCase):
    def test_split_gt_recall_short_results_and_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'gt.ibin'
            path.write_bytes(struct.pack('<II4I4f', 2, 2, 1, 2, 3, 0, 0., 1., 0., 2.))
            rows = [dict(scope='CORRECTNESS_SMOKE_NOT_BENCHMARK',query_id=0,ids=[1,0],squared_l2=[0.,1.]),
                    dict(scope='CORRECTNESS_SMOKE_NOT_BENCHMARK',query_id=1,ids=[3],squared_l2=[0.])]
            report = evaluate(rows, path, 4, 2)
            self.assertEqual(report['recall_at_k'], .5)
            self.assertEqual(report['incomplete_top_k_queries'], 1)
            self.assertEqual(report['gt_aux_min'], 0.0)
            self.assertEqual(report['accepted_negative_gt_distances'], 0)
            self.assertEqual(report['accepted_negative_gt_queries'], 0)
            self.assertEqual(report['gt_distance_semantics'], 'NOT_USED_FOR_RECALL')
            for invalid in ([rows[0],rows[0]], [dict(rows[0],ids=[1,1])], [dict(rows[0],query_id=2)],
                            [dict(rows[0],squared_l2=[float('nan'),1.])],
                            [dict(rows[0],squared_l2=[-1e-7,1.])]):
                with self.assertRaises(ValueError):
                    evaluate(invalid,path,4,2)
            path.write_bytes(path.read_bytes()[:-4])
            with self.assertRaises(ValueError):
                evaluate(rows,path,4,2)

    def test_opt_in_gt_aux_min_handles_bounded_ulp_negatives_and_rejects_abuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root/'gt.ibin'
            neg_a, neg_b = -3.5762786865234375e-07, -2.384185791015625e-07
            path.write_bytes(struct.pack('<II4I4f', 2, 2, 1, 2, 3, 0, neg_a, 1.0, neg_b, 2.0))
            rows = [dict(scope='CORRECTNESS_SMOKE_NOT_BENCHMARK',query_id=0,ids=[1,2],squared_l2=[0.,1.]),
                    dict(scope='CORRECTNESS_SMOKE_NOT_BENCHMARK',query_id=1,ids=[3,0],squared_l2=[0.,2.])]
            # Default gt_aux_min=0.0 remains strictly fail-closed.
            with self.assertRaises(ValueError):
                evaluate(rows, path, 4, 2)
            # Opt-in -1e-5 accepts finite monotonic ULP negatives and counts them explicitly.
            report = evaluate(rows, path, 4, 2, gt_aux_min=-1e-5)
            self.assertEqual(report['recall_at_k'], 1.0)
            self.assertEqual(report['gt_aux_min'], -1e-5)
            self.assertEqual(report['accepted_negative_gt_distances'], 2)
            self.assertEqual(report['accepted_negative_gt_queries'], 2)
            self.assertEqual(report['gt_distance_semantics'], 'ID_ONLY_WITH_OPT_IN_BOUNDED_AUX_NEGATIVE_TOLERANCE')
            # Engine negative squared_l2 remains rejected even with opt-in GT aux tolerance.
            with self.assertRaises(ValueError):
                evaluate([dict(rows[0], squared_l2=[-1e-7, 1.0])], path, 4, 2, gt_aux_min=-1e-5)
            # Invalid gt_aux_min thresholds rejected.
            for bad_min in (1e-6, -0.1, float('nan'), float('-inf'), True):
                with self.subTest(bad_min=bad_min), self.assertRaises(ValueError):
                    evaluate(rows, path, 4, 2, gt_aux_min=bad_min)
            # Below threshold, NaN/Inf, out-of-order GT distances, and bad GT IDs still rejected.
            for bad_gt in (
                struct.pack('<II4I4f', 2, 2, 1, 2, 3, 0, -2e-5, 1.0, 0.0, 2.0),
                struct.pack('<II4I4f', 2, 2, 1, 2, 3, 0, float('nan'), 1.0, 0.0, 2.0),
                struct.pack('<II4I4f', 2, 2, 1, 2, 3, 0, float('inf'), 1.0, 0.0, 2.0),
                struct.pack('<II4I4f', 2, 2, 1, 2, 3, 0, -1e-7, -2e-7, 0.0, 2.0),
                struct.pack('<II4I4f', 2, 2, 1, 1, 3, 0, neg_a, 1.0, 0.0, 2.0),
                struct.pack('<II4I4f', 2, 2, 4, 2, 3, 0, neg_a, 1.0, 0.0, 2.0),
            ):
                path.write_bytes(bad_gt)
                with self.assertRaises(ValueError):
                    evaluate(rows, path, 4, 2, gt_aux_min=-1e-5)
            # CLI opt-in vs default and bad flag check.
            path.write_bytes(struct.pack('<II4I4f', 2, 2, 1, 2, 3, 0, neg_a, 1.0, neg_b, 2.0))
            rows_file = root/'rows.jsonl'
            rows_file.write_text('\n'.join(json.dumps(r) for r in rows) + '\n')
            repo_root = Path(__file__).resolve().parents[2]
            cmd_base = [sys.executable, '-m', 'research.task_da.evaluate_smoke',
                        str(rows_file), str(path), '--base-count', '4', '--k', '2']
            fail_default = subprocess.run(cmd_base, cwd=repo_root, capture_output=True, text=True)
            self.assertNotEqual(fail_default.returncode, 0)
            ok_opt_in = subprocess.run(cmd_base + ['--gt-aux-min', '-1e-5'],
                                       cwd=repo_root, capture_output=True, text=True)
            self.assertEqual(ok_opt_in.returncode, 0, ok_opt_in.stderr)
            parsed = json.loads(ok_opt_in.stdout)
            self.assertEqual(parsed['accepted_negative_gt_distances'], 2)
            fail_abuse = subprocess.run(cmd_base + ['--gt-aux-min', '-0.1'],
                                        cwd=repo_root, capture_output=True, text=True)
            self.assertNotEqual(fail_abuse.returncode, 0)


@unittest.skipUnless(os.environ.get('TASK_DA_SMOKE'), 'native smoke requires explicit CMake-built binary')
class NativeTests(unittest.TestCase):
    def run_native(self, fmt='pipnn', graph=None, *, entry=0, k=2, beam=4, mode='ON', limit=1, ok=True):
        result = subprocess.run([os.environ['TASK_DA_SMOKE'], fmt, str(graph or self.path),
                                 str(self.root/'base.fbin'), str(self.root/'query.fbin'),
                                 str(entry), str(k), str(beam), mode, str(limit)],
                                capture_output=True, text=True, timeout=10)
        if not ok:
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertNotIn('Sanitizer', result.stderr)
            return None
        self.assertEqual(result.returncode, 0, result.stderr)
        return [json.loads(row) for row in result.stdout.splitlines()]

    def setUp(self):
        GraphTests.setUp(self)
        fbin(self.root/'base.fbin', [[0., 0.], [1., 0.], [2., 0.], [0., 0.]])
        fbin(self.root/'query.fbin', [[1.5, 0.]])

    def test_native_format_and_on_off_parity(self):
        nsg = self.root/'g.nsg'
        with Graph(self.path, 'pipnn', entry=0) as g:
            convert(g, nsg, 'nsg')
        a, b = self.run_native()[0], self.run_native('nsg', nsg)[0]
        self.assertEqual(a, b)
        off = self.run_native(mode='OFF')[0]
        self.assertEqual(a['ids'], [1, 2])
        self.assertEqual(a['ids'], off['ids'])
        self.assertEqual(a['squared_l2'], off['squared_l2'])
        self.assertIsNone(off['counters'])
        self.assertEqual(a['counters'], dict(distance_evaluations=3, expansions=3,
            neighbor_attempts=6, already_seen_attempts=4, frontier_insertions=3))

    def test_native_random_connected_graph_against_independent_exact_oracle(self):
        rng = random.Random(20261115)
        n, dim = 37, 5
        base = [[float(rng.randrange(-8, 9)) for _ in range(dim)] for _ in range(n)]
        queries = [[float(rng.randrange(-8, 9)) for _ in range(dim)] for _ in range(12)]
        edges = [[(i+1)%n] + [rng.randrange(n) for _ in range(4)] for i in range(n)]
        pipnn(self.path, edges)
        fbin(self.root/'base.fbin', base)
        fbin(self.root/'query.fbin', queries)
        results = self.run_native(k=10, beam=n, limit=len(queries))
        for query, result in zip(queries, results):
            exact = sorted((sum((a-b)**2 for a,b in zip(row, query)), i) for i,row in enumerate(base))[:10]
            self.assertEqual(result['ids'], [i for _,i in exact])
            self.assertEqual(result['squared_l2'], [d for d,_ in exact])
            self.assertEqual(result['counters']['distance_evaluations'], n)
            self.assertEqual(result['counters']['expansions'], n)

    def test_bounded_beams_have_format_and_instrumentation_parity(self):
        rng = random.Random(17)
        n = 19
        pipnn(self.path, [[(i+1)%n] + [rng.randrange(n) for _ in range(3)] for i in range(n)])
        fbin(self.root/'base.fbin', [[float(rng.randrange(20)),float(rng.randrange(20))] for _ in range(n)])
        fbin(self.root/'query.fbin', [[3.,7.], [11.,1.]])
        nsg = self.root/'g.nsg'
        with Graph(self.path, 'pipnn', entry=0) as g:
            convert(g,nsg,'nsg')
        for beam in (1,2,4,10,19):
            for fmt,path in [('pipnn',self.path),('nsg',nsg)]:
                on=self.run_native(fmt,path,k=min(beam,3),beam=beam,limit=2)
                off=self.run_native(fmt,path,k=min(beam,3),beam=beam,limit=2,mode='OFF')
                canonical=self.run_native(k=min(beam,3),beam=beam,limit=2)
                self.assertEqual(on,canonical)
                self.assertEqual([r['ids'] for r in on],[r['ids'] for r in off])

    def test_bounded_beam_can_miss_routing_node(self):
        # Full traversal reaches nearest node 3 through distant node 2; beam=1 does not.
        pipnn(self.path, [[1, 2], [], [3], []])
        fbin(self.root/'base.fbin', [[4.], [2.], [10.], [0.]])
        fbin(self.root/'query.fbin', [[0.]])
        self.assertEqual(self.run_native(k=1, beam=1)[0]['ids'], [1])
        self.assertEqual(self.run_native(k=1, beam=4)[0]['ids'], [3])

    def test_disconnected_graph_does_not_fabricate_neighbors_or_pad(self):
        result = self.run_native(entry=3, k=2)[0]
        self.assertEqual(result['ids'], [3])
        self.assertFalse(result['complete_top_k'])

    def test_ties_follow_id_and_duplicate_distances_count_once(self):
        pipnn(self.path, [[3, 2, 1, 3], [0], [0], [0]])
        fbin(self.root/'base.fbin', [[0., 0.]] * 4)
        result = self.run_native(k=4)[0]
        self.assertEqual(result['ids'], [0, 1, 2, 3])
        self.assertEqual(result['counters']['distance_evaluations'], 4)

    def test_native_rejects_corruption_shapes_and_search_options(self):
        for kwargs in ({'entry':4}, {'entry':-1}, {'k':0}, {'k':3,'beam':2}, {'beam':5},
                       {'mode':'maybe'}, {'limit':0}, {'limit':33}, {'limit':2}):
            with self.subTest(kwargs=kwargs):
                self.run_native(ok=False, **kwargs)
        raw = self.path.read_bytes()
        for length in range(len(raw)):
            self.path.write_bytes(raw[:length])
            self.run_native(ok=False)
        self.path.write_bytes(raw + b'\0\0\0\0')
        self.run_native(ok=False)
        self.path.write_bytes(raw[:-4] + struct.pack('<I', 4))
        self.run_native(ok=False)
        self.path.write_bytes(raw)
        for value in (float('nan'), float('inf')):
            fbin(self.root/'query.fbin', [[value, 0.]])
            self.run_native(ok=False)
        fbin(self.root/'query.fbin', [[0.]])
        self.run_native(ok=False)


class FullP1Tests(unittest.TestCase):
    def test_evaluate_p1_large_split_gt_aux_and_on_off_parity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nq = 40
            # Synthetic GT width=2 over nq=40 with one bounded negative distance
            ids_data = []
            dist_data = []
            for q in range(nq):
                ids_data.extend([0, 1])
                dist_data.extend([-2e-7 if q == 5 else 0.0, 1.0])
            gt_path = root / 'gt.ibin'
            gt_path.write_bytes(
                struct.pack('<II', nq, 2)
                + struct.pack('<' + 'I' * (nq * 2), *ids_data)
                + struct.pack('<' + 'f' * (nq * 2), *dist_data)
            )
            qids_path = root / 'val.ids'
            qids = list(range(0, nq, 2)) + list(range(1, nq, 2))
            qids_path.write_text('\n'.join(map(str, qids)) + '\n')

            on_path = root / 'beam_4_ON.jsonl'
            off_path = root / 'beam_4_OFF.jsonl'
            on_rows, off_rows = [], []
            for q in qids:
                on_rows.append(dict(
                    scope='P1_VALIDATION_NOT_BENCHMARK',
                    query_id=q,
                    search_policy='entry_best_first_v1',
                    workers=1,
                    beam=4,
                    instrumentation='ON',
                    ids=[0, 1] if q != 0 else [0, 2],
                    squared_l2=[0.0, 1.0],
                    counters=dict(distance_evaluations=3, expansions=2, neighbor_attempts=3,
                                  already_seen_attempts=1, frontier_insertions=2),
                    complete_top_k=True,
                ))
                off_rows.append(dict(
                    scope='P1_VALIDATION_NOT_BENCHMARK',
                    query_id=q,
                    search_policy='entry_best_first_v1',
                    workers=1,
                    beam=4,
                    instrumentation='OFF',
                    ids=[0, 1] if q != 0 else [0, 2],
                    squared_l2=[0.0, 1.0],
                    counters=None,
                    complete_top_k=True,
                ))
            on_path.write_text('\n'.join(json.dumps(r) for r in on_rows) + '\n')
            off_path.write_text('\n'.join(json.dumps(r) for r in off_rows) + '\n')

            with self.assertRaises(ValueError):
                evaluate_p1(on_path, gt_path, base_count=4, k=2, gt_aux_min=0.0, query_ids_path=qids_path)
            res = evaluate_p1(
                on_path, gt_path, base_count=4, k=2, gt_aux_min=-1e-5,
                query_ids_path=qids_path, parity_off_path=off_path,
            )
            self.assertEqual(res['queries'], nq)
            self.assertEqual(res['hits'], nq * 2 - 1)
            self.assertEqual(res['accepted_negative_gt_distances'], 1)
            self.assertEqual(res['accepted_negative_gt_queries'], 1)
            self.assertTrue(res['on_off_parity']['exact_ids_match'])
            self.assertTrue(res['on_off_parity']['exact_squared_l2_match'])
            self.assertTrue(res['on_off_parity']['counter_invariants_pass'])

            # Detect mismatch and split divergence
            off_rows[0]['ids'] = [1, 0]
            with self.assertRaises(ValueError):
                check_on_off_parity(on_rows, off_rows, 4)
            bad_qids = root / 'bad.ids'
            bad_qids.write_text('\n'.join(map(str, range(nq - 1))) + '\n')
            with self.assertRaises(ValueError):
                evaluate_p1(on_path, gt_path, base_count=4, k=2, gt_aux_min=-1e-5, query_ids_path=bad_qids)


@unittest.skipUnless(
    os.environ.get('TASK_DA_P1_EVAL') and os.environ.get('TASK_DA_SMOKE'),
    'native P1 tests require CMake-built task_da_p1_eval and task_da_smoke',
)
class NativeP1EvalTests(unittest.TestCase):
    def test_p1_eval_matches_smoke_and_enforces_exclusive_and_caps(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rng = random.Random(12345)
            n = 25
            edges = [[(i + 1) % n] + [rng.randrange(n) for _ in range(3)] for i in range(n)]
            base = [[float(rng.randrange(20)), float(rng.randrange(20))] for _ in range(n)]
            queries = [[float(rng.randrange(20)), float(rng.randrange(20))] for _ in range(6)]
            gpath = root / 'g.pipnn'
            bpath = root / 'base.fbin'
            qpath = root / 'query.fbin'
            pipnn(gpath, edges)
            fbin(bpath, base)
            fbin(qpath, queries)
            qids_path = root / 'q.ids'
            qids_path.write_text('5\n2\n0\n4\n')

            out_dir = root / 'out'
            cmd_on = [
                os.environ['TASK_DA_P1_EVAL'], 'pipnn', str(gpath), str(bpath), str(qpath),
                '--entry', '0', '--k', '3', '--beams', '4,10', '--mode', 'ON',
                '--query-ids', str(qids_path), '--out-dir', str(out_dir), '--max-beam', '12',
            ]
            run_on = subprocess.run(cmd_on, capture_output=True, text=True, check=True)
            meta = json.loads(run_on.stdout)
            self.assertEqual([r['beam'] for r in meta['runs']], [4, 10])

            cmd_off = cmd_on[:cmd_on.index('ON')] + ['OFF'] + cmd_on[cmd_on.index('ON') + 1:]
            subprocess.run(cmd_off, capture_output=True, text=True, check=True)

            # Refuse overwrite
            dup = subprocess.run(cmd_on, capture_output=True, text=True)
            self.assertEqual(dup.returncode, 1)

            # Compare beam=10 ON vs OFF and against task_da_smoke
            on_rows = [json.loads(l) for l in (out_dir / 'beam_10_ON.jsonl').read_text().splitlines()]
            off_rows = [json.loads(l) for l in (out_dir / 'beam_10_OFF.jsonl').read_text().splitlines()]
            self.assertEqual([r['query_id'] for r in on_rows], [5, 2, 0, 4])
            parity = check_on_off_parity(on_rows, off_rows, n)
            self.assertTrue(parity['exact_ids_match'])

            smoke = subprocess.run(
                [os.environ['TASK_DA_SMOKE'], 'pipnn', str(gpath), str(bpath), str(qpath),
                 '0', '3', '10', 'ON', '6'],
                capture_output=True, text=True, check=True,
            )
            smoke_by_q = {r['query_id']: r for r in map(json.loads, smoke.stdout.splitlines())}
            for row in on_rows:
                s = smoke_by_q[row['query_id']]
                self.assertEqual(row['ids'], s['ids'])
                self.assertEqual(row['squared_l2'], s['squared_l2'])
                self.assertEqual(row['counters'], s['counters'])

            # Reject exceeding --max-beam and verify --jobs 4 matches --jobs 1 bit-for-bit
            out_dir_par = root / 'out_par'
            subprocess.run(cmd_on[:cmd_on.index(str(out_dir))] + [str(out_dir_par), '--max-beam', '12', '--jobs', '4'],
                           capture_output=True, text=True, check=True)
            self.assertEqual((out_dir / 'beam_10_ON.jsonl').read_bytes(), (out_dir_par / 'beam_10_ON.jsonl').read_bytes())

            over = subprocess.run(
                cmd_on[:cmd_on.index('4,10')] + ['13'] + cmd_on[cmd_on.index('4,10') + 1:],
                capture_output=True, text=True,
            )
            self.assertEqual(over.returncode, 1)


class P2EvaluatorUnitTests(unittest.TestCase):
    def test_evaluate_p2_invariants_and_rejects_broken_counters(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gt_path = root / 'gt.ibin'
            nq = 4
            gt_path.write_bytes(
                struct.pack('<II', nq, 2)
                + struct.pack('<' + 'I' * (nq * 2), *([0, 1] * nq))
                + struct.pack('<' + 'f' * (nq * 2), *([0.0, 1.0] * nq))
            )
            qids_path = root / 'q.ids'
            qids_path.write_text('0\n1\n2\n3\n')

            def make_row(q, mode, workers, dup_exp=0, bad_balance=False):
                pw_exp = [2] if workers == 1 else [2, 1 + dup_exp]
                ex = sum(pw_exp)
                u_ex = ex - dup_exp
                na = 6
                as_ = 2
                de = (1 + na - as_) + (1 if bad_balance else 0)
                pw_dist = [de] if workers == 1 else [de - 2, 2]
                counters = None if mode == 'OFF' else dict(
                    distance_evaluations=de,
                    unique_distance_evaluations=de - (1 if workers > 1 else 0),
                    duplicate_distance_evaluations=(1 if workers > 1 else 0),
                    expansions=ex,
                    unique_expansions=u_ex,
                    duplicate_expansions=dup_exp,
                    neighbor_attempts=na,
                    already_seen_attempts=as_,
                    frontier_insertions=3,
                    sync_merge_count=(0 if workers == 1 else 1),
                    sync_wait_ns=(0 if workers == 1 else 500),
                    barrier_wait_ns=(0 if workers == 1 else 300),
                    merge_time_ns=(0 if workers == 1 else 200),
                    worker_idle_ns=0,
                    per_worker_expansions=pw_exp,
                    per_worker_distance_evaluations=pw_dist,
                    per_worker_idle_rounds=([0] if workers == 1 else [0, 0]),
                )
                return dict(
                    scope='task_d_a_common_p2_exploratory',
                    query_id=q,
                    workers=workers,
                    jobs=1,
                    beam=4,
                    mode=mode,
                    instrumentation=(mode == 'ON'),
                    complete_top_k=True,
                    ids=[0, 1],
                    squared_l2=[0.0, 1.0],
                    counters=counters,
                )

            on_p2 = root / 'p2_ON.jsonl'
            off_p2 = root / 'p2_OFF.jsonl'
            on_p2.write_text('\n'.join(json.dumps(make_row(q, 'ON', 2, dup_exp=1)) for q in range(nq)) + '\n')
            off_p2.write_text('\n'.join(json.dumps(make_row(q, 'OFF', 2)) for q in range(nq)) + '\n')
            res = evaluate_p2(on_p2, gt_path, base_count=8, k=2, query_ids_path=qids_path, parity_off_path=off_p2)
            self.assertEqual(res['recall_at_k'], 1.0)
            self.assertEqual(res['workers'], 2)
            self.assertTrue(res['on_off_parity']['counter_invariants_pass'])
            self.assertAlmostEqual(res['on_off_parity']['duplicate_expansion_rate'], 1.0 / 4.0)

            with self.assertRaises(ValueError):
                validate_p2_counters_row(make_row(0, 'ON', 1, dup_exp=1), 8)
            with self.assertRaises(ValueError):
                validate_p2_counters_row(make_row(0, 'ON', 2, bad_balance=True), 8)


@unittest.skipUnless(
    os.environ.get('TASK_DA_P2_EVAL') and os.environ.get('TASK_DA_P1_EVAL'),
    'native P2 tests require CMake-built task_da_p2_eval and task_da_p1_eval',
)
class NativeP2MultiWalkerTests(unittest.TestCase):
    def _run_p2(self, root, gpath, bpath, qpath, *, workers, beam, mode, out_name,
                k=3, entry=0, sync_interval=8, qids=None, wids=None, cpu_list=None,
                merge_impl=None, jobs=1, ok=True):
        out_dir = root / out_name
        cmd = [
            os.environ['TASK_DA_P2_EVAL'], 'pipnn', str(gpath), str(bpath), str(qpath),
            '--entry', str(entry), '--k', str(k), '--beams', str(beam),
            '--workers', str(workers), '--sync-interval', str(sync_interval),
            '--mode', mode, '--out-dir', str(out_dir), '--jobs', str(jobs),
        ]
        if qids is not None:
            cmd += ['--query-ids', str(qids)]
        if wids is not None:
            cmd += ['--warmup-ids', str(wids)]
        if cpu_list is not None:
            cmd += ['--cpu-list', cpu_list]
        if merge_impl is not None:
            cmd += ['--merge-impl', merge_impl]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if not ok:
            self.assertNotEqual(proc.returncode, 0, msg=proc.stdout)
            return None, None
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        summary = json.loads(proc.stdout)
        rows = [
            json.loads(l)
            for l in (out_dir / f'beam_{beam}_p{workers}_{mode}.jsonl').read_text().splitlines()
        ]
        return summary, rows

    def test_p1_bit_identical_parity_and_exact_oracle_across_p124(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rng = random.Random(20261118)
            n = 48
            # Bidirectional ring + random shortcuts so full-beam (48) reaches all vertices
            adj = [set() for _ in range(n)]
            for i in range(n):
                adj[i].add((i + 1) % n)
                adj[(i + 1) % n].add(i)
                for _ in range(4):
                    adj[i].add(rng.randrange(n))
            edges = [sorted(s) for s in adj]
            base = [[rng.uniform(-10.0, 10.0) for _ in range(6)] for _ in range(n)]
            queries = [[rng.uniform(-10.0, 10.0) for _ in range(6)] for _ in range(12)]

            gpath = root / 'g.pipnn'
            bpath = root / 'base.fbin'
            qpath = root / 'query.fbin'
            pipnn(gpath, edges)
            fbin(bpath, base)
            fbin(qpath, queries)
            qids = root / 'q.ids'
            wids = root / 'w.ids'
            qids.write_text('\n'.join(map(str, range(2, 12))) + '\n')
            wids.write_text('0\n1\n')

            # Brute-force exact oracle top-5 per query
            k = 5
            gt_ids, gt_dists = [], []
            for q in queries:
                scored = sorted(
                    ((sum((float(base[i][d]) - float(q[d])) ** 2 for d in range(6)), i) for i in range(n)),
                )
                gt_ids.extend(idx for _, idx in scored[:k])
                gt_dists.extend(dist for dist, _ in scored[:k])
            gt_path = root / 'gt.ibin'
            gt_path.write_bytes(
                struct.pack('<II', len(queries), k)
                + struct.pack('<' + 'I' * (len(queries) * k), *gt_ids)
                + struct.pack('<' + 'f' * (len(queries) * k), *gt_dists)
            )

            # 1) P2 p=1 must match task_da_p1_eval bit-for-bit on IDs, distances, and P1 counters
            p1_out = root / 'p1_ref'
            subprocess.run([
                os.environ['TASK_DA_P1_EVAL'], 'pipnn', str(gpath), str(bpath), str(qpath),
                '--entry', '0', '--k', str(k), '--beams', '24,48', '--mode', 'ON',
                '--query-ids', str(qids), '--out-dir', str(p1_out),
            ], capture_output=True, text=True, check=True)
            p1_ref_24 = [json.loads(l) for l in (p1_out / 'beam_24_ON.jsonl').read_text().splitlines()]

            _, p2_1_on_24 = self._run_p2(
                root, gpath, bpath, qpath, workers=1, beam=24, mode='ON', out_name='p2_1_24_on',
                k=k, qids=qids, wids=wids, cpu_list='0',
            )
            _, p2_1_off_24 = self._run_p2(
                root, gpath, bpath, qpath, workers=1, beam=24, mode='OFF', out_name='p2_1_24_off',
                k=k, qids=qids,
            )
            for ref, cur in zip(p1_ref_24, p2_1_on_24):
                self.assertEqual(cur['ids'], ref['ids'])
                self.assertEqual(cur['squared_l2'], ref['squared_l2'])
                for key in ('distance_evaluations', 'expansions', 'neighbor_attempts',
                            'already_seen_attempts', 'frontier_insertions'):
                    self.assertEqual(cur['counters'][key], ref['counters'][key])
            check_p2_on_off_parity(p2_1_on_24, p2_1_off_24, n)

            # 2) Exact brute-force oracle top-k recall == 1.0 when beam=n for p=1,2,4 + repeated determinism
            for p in (1, 2, 4):
                sum_on, rows_on = self._run_p2(
                    root, gpath, bpath, qpath, workers=p, beam=n, mode='ON',
                    out_name=f'oracle_p{p}_on', k=k, qids=qids, wids=wids, sync_interval=4,
                )
                _, rows_off_1 = self._run_p2(
                    root, gpath, bpath, qpath, workers=p, beam=n, mode='OFF',
                    out_name=f'oracle_p{p}_off1', k=k, qids=qids, wids=wids, sync_interval=4,
                )
                _, rows_off_2 = self._run_p2(
                    root, gpath, bpath, qpath, workers=p, beam=n, mode='OFF',
                    out_name=f'oracle_p{p}_off2', k=k, qids=qids, wids=wids, sync_interval=4,
                )
                self.assertEqual([r['ids'] for r in rows_off_1], [r['ids'] for r in rows_off_2])
                parity = check_p2_on_off_parity(rows_on, rows_off_1, n)
                self.assertTrue(parity['exact_ids_match'])
                ev = evaluate_p2(
                    root / f'oracle_p{p}_on' / f'beam_{n}_p{p}_ON.jsonl',
                    gt_path, base_count=n, k=k, query_ids_path=qids,
                    parity_off_path=root / f'oracle_p{p}_off1' / f'beam_{n}_p{p}_OFF.jsonl',
                )
                self.assertEqual(ev['recall_at_k'], 1.0)
                self.assertEqual(ev['incomplete_top_k_queries'], 0)
                self.assertGreaterEqual(sum_on['vm_hwm_kib'], 0)

            # 3) Flat merge must match std::set merge bit-for-bit on bounded beam=24 across p=1,2,4
            for p in (1, 2, 4):
                _, rows_set_on = self._run_p2(
                    root, gpath, bpath, qpath, workers=p, beam=24, mode='ON',
                    out_name=f'mset_p{p}_on', k=k, qids=qids, sync_interval=4, merge_impl='set',
                )
                _, rows_flat_on = self._run_p2(
                    root, gpath, bpath, qpath, workers=p, beam=24, mode='ON',
                    out_name=f'mflat_p{p}_on', k=k, qids=qids, sync_interval=4, merge_impl='flat',
                )
                _, rows_flat_off = self._run_p2(
                    root, gpath, bpath, qpath, workers=p, beam=24, mode='OFF',
                    out_name=f'mflat_p{p}_off', k=k, qids=qids, sync_interval=4, merge_impl='flat',
                )
                check_p2_on_off_parity(rows_flat_on, rows_flat_off, n)
                for rs, rf in zip(rows_set_on, rows_flat_on):
                    self.assertEqual(rf['ids'], rs['ids'])
                    self.assertEqual(rf['squared_l2'], rs['squared_l2'])
                    for ckey in ('distance_evaluations', 'unique_distance_evaluations',
                                 'duplicate_distance_evaluations', 'expansions',
                                 'unique_expansions', 'duplicate_expansions',
                                 'neighbor_attempts', 'already_seen_attempts',
                                 'frontier_insertions', 'sync_merge_count',
                                 'per_worker_expansions', 'per_worker_idle_rounds'):
                        self.assertEqual(rf['counters'][ckey], rs['counters'][ckey])

    def test_disconnected_ties_selfloop_chain_and_diamond_duplicate_expansions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # 1) Diamond + shared hub producing true duplicate_expansions when p=2, S=4
            # Node 0 -> {1, 2} (symmetrically assigned to w0 and w1); 1 -> {3, 4}, 2 -> {3, 5}, 3 -> {6, 7}
            edges = [
                [1, 2],       # 0 (entry)
                [3, 4],       # 1
                [3, 5],       # 2
                [6, 7],       # 3 (shared hub discovered & expanded inside same round by both workers)
                [], [], [], [],
            ]
            # Make distances favor 3 (< 4, 5) strongly so both workers expand 3 immediately in Round 0!
            base = [
                [10.0, 0.0],  # 0
                [2.0, 0.0],   # 1
                [2.1, 0.0],   # 2
                [0.5, 0.0],   # 3
                [5.0, 0.0],   # 4
                [5.5, 0.0],   # 5
                [0.1, 0.0],   # 6
                [0.2, 0.0],   # 7
            ]
            gpath = root / 'diamond.pipnn'
            bpath = root / 'diamond_b.fbin'
            qpath = root / 'diamond_q.fbin'
            pipnn(gpath, edges)
            fbin(bpath, base)
            fbin(qpath, [[0.0, 0.0]])

            _, rows_d = self._run_p2(
                root, gpath, bpath, qpath, workers=2, beam=8, mode='ON',
                out_name='diamond_p2', k=3, sync_interval=4,
            )
            c = validate_p2_counters_row(rows_d[0], 8)
            self.assertEqual(rows_d[0]['ids'], [6, 7, 3])
            self.assertGreaterEqual(c['duplicate_expansions'], 1)
            self.assertGreaterEqual(c['duplicate_distance_evaluations'], 1)
            self.assertEqual(c['expansions'], c['unique_expansions'] + c['duplicate_expansions'])

            # 2) Disconnected + ties + self-loop + duplicate edges + single-edge chain across p=1,2,4
            edges_disc = [
                [3, 2, 1, 3, 0],  # 0 -> ties & dup arcs & self-loop, never reaches nodes 4..7
                [0], [0], [0],
                [5], [6], [7], [4],
            ]
            base_disc = [[0.0, 0.0]] * 8
            g_disc = root / 'disc.pipnn'
            b_disc = root / 'disc_b.fbin'
            pipnn(g_disc, edges_disc)
            fbin(b_disc, base_disc)
            for p in (1, 2, 4):
                _, r_on = self._run_p2(
                    root, g_disc, b_disc, qpath, workers=p, beam=6, mode='ON',
                    out_name=f'disc_p{p}_on', k=6,
                )
                _, r_off = self._run_p2(
                    root, g_disc, b_disc, qpath, workers=p, beam=6, mode='OFF',
                    out_name=f'disc_p{p}_off', k=6,
                )
                self.assertEqual(r_on[0]['ids'], [0, 1, 2, 3])
                self.assertFalse(r_on[0]['complete_top_k'])
                validate_p2_counters_row(r_on[0], 8)
                check_p2_on_off_parity(r_on, r_off, 8)

            # 3) Degree-1 chain triggering worker idle rounds on p=2,4
            chain_edges = [[i + 1] if i < 9 else [] for i in range(10)]
            chain_base = [[float(9 - i), 0.0] for i in range(10)]
            g_chain = root / 'chain.pipnn'
            b_chain = root / 'chain_b.fbin'
            pipnn(g_chain, chain_edges)
            fbin(b_chain, chain_base)
            _, r_chain = self._run_p2(
                root, g_chain, b_chain, qpath, workers=4, beam=10, mode='ON',
                out_name='chain_p4', k=3, sync_interval=2,
            )
            c_chain = validate_p2_counters_row(r_chain[0], 10)
            self.assertEqual(r_chain[0]['ids'], [9, 8, 7])
            self.assertGreater(sum(c_chain['per_worker_idle_rounds']), 0)

            # 4) Reject invalid CLI options & overwrite
            self._run_p2(root, g_chain, b_chain, qpath, workers=2, beam=10, mode='ON',
                         out_name='chain_p4', k=3, ok=False)  # overwrite
            self._run_p2(root, g_chain, b_chain, qpath, workers=2, beam=10, mode='ON',
                         out_name='bad_jobs', k=3, jobs=2, ok=False)
            self._run_p2(root, g_chain, b_chain, qpath, workers=3, beam=10, mode='ON',
                         out_name='bad_w', k=3, ok=False)
            self._run_p2(root, g_chain, b_chain, qpath, workers=2, beam=10, mode='ON',
                         out_name='bad_cpu', k=3, cpu_list='0', ok=False)
            self._run_p2(root, g_chain, b_chain, qpath, workers=2, beam=10, mode='ON',
                         out_name='bad_merge', k=3, merge_impl='bogus', ok=False)


if __name__ == '__main__':
    unittest.main()
