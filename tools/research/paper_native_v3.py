#!/usr/bin/env python3
"""Prospective paper-native v3: separate owned-command safety and block validity.

Reuses the v2 collectors without changing its immutable safety contract. RAPL
policy readouts are not temperatures, consumed power, or evidence of corruption.
"""
import argparse
import csv
import json
import math
from pathlib import Path
import re
import struct
import paper_portable_v2 as v2
from paper_rebaseline import canonical_bytes, digest


class SafetyGuard(v2.Guard):
    def check(self, snapshot, owned_pid=None):
        # Preserve every other v2 guard. A policy-only transition is observational.
        adjusted = dict(snapshot, rapl=self.baseline['rapl'])
        return super().check(adjusted, owned_pid)


def block_validity(snapshots):
    if not snapshots:
        return {'status': 'UNKNOWN', 'reason': 'no host observations'}
    if any(not s.get('power') or not s.get('rapl') or
           any(v is None for v in (*s['power'].values(), *s['rapl'].values())) for s in snapshots):
        return {'status': 'UNKNOWN', 'reason': 'incomplete readable power policy evidence'}
    first = snapshots[0]
    transitions = []
    previous = first
    for current in snapshots[1:]:
        changed = [key for key in ('power', 'rapl') if current[key] != previous[key]]
        if changed:
            transitions.append({'timestamp': current['timestamp'], 'changed': changed,
                                'before': {k: previous[k] for k in changed},
                                'after': {k: current[k] for k in changed}})
        previous = current
    return {'status': 'ENV_CONFOUNDED' if transitions else 'COMPARABLE',
            'transitions': transitions,
            'scope': 'sampled whole-process and gap coverage; not continuous power proof'}


def check_diagnostics(text):
    if re.search(r'\b(?:ERROR|Failed|EBADF|segmentation fault)\b|Bad file descriptor|'
                 r'File size mismatch|Unknown distance|Unknown search|No valid Lsearch', text, re.I):
        raise ValueError('Native output contains failure diagnostics, irrespective of exit code')


def verify_native_package(path, full=False):
    """Scoped native split index with source-defined implicit tags, not fabricated files."""
    path = Path(path)
    value = json.loads(path.read_bytes())
    if path.with_suffix('.sha256').read_text().split() != [digest(path), path.name]:
        raise ValueError('Native package digest mismatch')
    if value.get('schema') != 'pipeann-paper-native-index-v1':
        raise ValueError('Unknown native package schema')
    if (value.get('N'), value.get('D'), value.get('dtype'), value.get('metric')) != (10000000,128,'uint8','l2'):
        raise ValueError('Unknown native dataset contract')
    if value.get('source_commit') != 'c4cd32c6816c063f56ecc64f9d7b63c909202cab':
        raise ValueError('Unknown native portable subject')
    if value.get('input_package_manifest_sha256') != '47d4bf47e6e515a3f3c4caeb357bdbc1af3bfcc4b319b0ae335678ca586dccc3':
        raise ValueError('Native input provenance mismatch')
    if value.get('tag_mapping') != 'implicit_identity_no_tag_file':
        raise ValueError('Unknown native tag semantics')
    if Path(value['index_prefix'] + '_disk.index.tags').exists():
        raise ValueError('Unexpected explicit tags alter native load path')
    files = value['files']
    suffixes = {'disk_index': '_disk.index', 'pq_compressed': '_pq_compressed.bin',
                'pq_pivots': '_pq_pivots.bin', 'memory_graph': '_mem.index',
                'memory_data': '_mem.index.data', 'memory_tags': '_mem.index.tags'}
    required = set(suffixes)
    if len({f['role'] for f in files}) != len(files) or {f['role'] for f in files} != required:
        raise ValueError('Missing/duplicate native component')
    for f in files:
        if f['path'] != value['index_prefix']+suffixes[f['role']]:
            raise ValueError('Native role/path mismatch')
        if not re.fullmatch('[0-9a-f]{64}', f['sha256']) or f['size_bytes'] <= 0:
            raise ValueError('Invalid native component digest/size')
        p = Path(f['path'])
        stat = p.stat()
        if not p.is_file() or str(p.resolve()) != f['path'] or stat.st_size != f['size_bytes'] or stat.st_mtime_ns != f['mtime_ns']:
            raise ValueError('Native component identity changed')
        if full and digest(p) != f['sha256']:
            raise ValueError('Native component bytes changed')
    with Path(value['index_prefix']+'_pq_compressed.bin').open('rb') as stream:
        if struct.unpack('<II',stream.read(8)) != (10000000,32):
            raise ValueError('Native PQ header mismatch')
    return value


def quality_against_canonical(path, base, query, truth, query_count=10000, k=10, n=10000000):
    """Independent all-result ID/cardinality/distance/tie-aware recall validation."""
    import numpy as np
    result = v2.validate_quality(path, query_count, k, n)
    arrays = {}
    for name, p, dtype, shape in [('base', base, 'u1', (n, 128)),
                                 ('query', query, 'u1', (query_count, 128))]:
        with Path(p).open('rb') as stream:
            if struct.unpack('<II', stream.read(8)) != shape:
                raise ValueError('Canonical vector header mismatch')
        arrays[name] = np.memmap(p, mode='r', dtype=dtype, offset=8, shape=shape)
    with Path(truth).open('rb') as stream:
        nq, top = struct.unpack('<II', stream.read(8))
    if nq != query_count or top < k:
        raise ValueError('Canonical truth header mismatch')
    ids = np.memmap(truth, mode='r', dtype='<u4', offset=8, shape=(nq, top))
    dist = np.memmap(truth, mode='r', dtype='<f4', offset=8+nq*top*4, shape=(nq, top))
    observed = [[] for _ in range(nq)]
    exact_checked = 0
    with Path(path).open() as stream:
        for row in csv.DictReader(stream):
            q, node = int(row['query_id']), int(row['node_id'])
            delta = arrays['base'][node].astype(np.int32) - arrays['query'][q].astype(np.int32)
            exact = int(np.dot(delta, delta))
            if float(row['distance']) != exact:
                raise ValueError(f'Exact uint8 squared-L2 mismatch at q={q}, id={node}')
            observed[q].append(node); exact_checked += 1
    matches = 0
    for q in range(nq):
        boundary = k-1
        while boundary < top and dist[q, boundary] == dist[q, k-1]:
            boundary += 1
        matches += len(set(observed[q]) & set(map(int, ids[q, :boundary])))
    result.update(exact_squared_L2_checked=exact_checked, recall=100*matches/(nq*k),
                  recall_definition='intersection of K unique results with GT through K-boundary ties / (Nq*K)')
    return result


def execute(spec, directory):
    original = v2.Guard
    v2.Guard = SafetyGuard
    try:
        return v2.execute(spec, directory)
    finally:
        v2.Guard = original


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--verify-index', type=Path)
    parser.add_argument('--full-components', action='store_true')
    args = parser.parse_args()
    if args.verify_index:
        verify_native_package(args.verify_index, args.full_components)
        print(json.dumps({'valid': True, 'manifest_sha256': digest(args.verify_index), 'full_components': args.full_components}))
        return
    if not args.spec or not args.output:
        parser.error('Use --spec SPEC --output NEW_DIRECTORY or --verify-index PACKAGE [--full-components]')
    spec = json.loads(args.spec.read_text())
    try:
        result = execute(spec, args.output)
        print(json.dumps({k: result[k] for k in ('exit_code', 'wall_time_s', 'peak_rss_KiB', 'guard_failure')}))
    finally:
        if args.output.exists():
            v2.seal(args.output)


if __name__ == '__main__':
    main()
