"""Synthetic graph-format and exact-oracle tests; no ANN benchmark evidence."""
import json
import os
from pathlib import Path
import random
import struct
import subprocess
import tempfile
import unittest

from research.task_da.graph_audit import Graph, audit, compare, convert, sha256
from research.task_da.preflight import check_artifact, preflight
from research.task_da.evaluate_smoke import evaluate


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
            self.assertEqual(evaluate(rows,path,4,2)['recall_at_k'],.5)
            self.assertEqual(evaluate(rows,path,4,2)['incomplete_top_k_queries'],1)
            for invalid in ([rows[0],rows[0]], [dict(rows[0],ids=[1,1])], [dict(rows[0],query_id=2)],
                            [dict(rows[0],squared_l2=[float('nan'),1.])]):
                with self.assertRaises(ValueError):
                    evaluate(invalid,path,4,2)
            path.write_bytes(path.read_bytes()[:-4])
            with self.assertRaises(ValueError):
                evaluate(rows,path,4,2)


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


if __name__ == '__main__':
    unittest.main()
