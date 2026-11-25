"""Controlled G2 v2 amendment design-3.1 analyzer (strict native P2 OFF/ON schema).

Fixes ONLY the OFF `counters` parser incompatibility discovered on design-3
OFF_EXECUTION_HOLD (`b0_stock_off_r1_base_test`):
- Frozen `task_da_p2_eval` (`p2_eval.cpp:415-464`, ELF SHA `7a2685e5...`) emits
  `"counters":{...}` iff `--mode ON` (`instrumentation:true`) and omits `"counters"`
  completely when `--mode OFF` (`instrumentation:false`) — verified on 524/524
  historical native `*_p2_OFF.jsonl` files and 10,000/10,000 rows of HOLD evidence.
- Explicitly distinguishes all 4 `counters` field states (`absent`, `explicit_null`,
  `object`, `malformed`) without unchecked `.get('counters')` fallbacks, and enforces
  strict row field/type validation for both ON and OFF.
- Delegates 100% of statistical, quality, bootstrap, tail, RAM hard-gate,
  BUILD-SEARCH, and paired foreign-load noise-balance math to frozen
  `g2_v2_design3_analyzer` without modification.
"""
import argparse
import fcntl
import hashlib
from pathlib import Path
import struct
import time

from . import g2_v2_design3_analyzer as _d3_analyzer
from .evaluate_p2 import validate_p2_counters_row
from .g2_v2_design3_1_contract import (
    POLICIES, PROTOCOL, REVISION, SCHEMA, load_freeze, number, require,
    validate_schema, write_new,
)

# Re-export unchanged statistical and helper primitives from frozen design-3 analyzer
CONTRASTS = _d3_analyzer.CONTRASTS
tcrit = _d3_analyzer.tcrit
ci = _d3_analyzer.ci
reduction = _d3_analyzer.reduction
ram_pair = _d3_analyzer.ram_pair
output_rows = _d3_analyzer.output_rows
quality_gate = _d3_analyzer.quality_gate
weighted_tails = _d3_analyzer.weighted_tails
bootstrap = _d3_analyzer.bootstrap
build_search = _d3_analyzer.build_search
noise_balance_diagnostics = _d3_analyzer.noise_balance_diagnostics

REQUIRED_ROW_KEYS = frozenset({
    'mode', 'instrumentation', 'workers', 'sync_interval', 'beam', 'jobs',
    'merge_impl', 'visited_policy', 'frontier_mode', 'query_id', 'ids',
    'squared_l2', 'complete_top_k',
})
OPTIONAL_NATIVE_ROW_KEYS = frozenset({
    'scope', 'graph_format', 'entry', 'k', 'latency_ns',
})
ALLOWED_OFF_ROW_KEYS = REQUIRED_ROW_KEYS | OPTIONAL_NATIVE_ROW_KEYS
ALLOWED_ON_ROW_KEYS = ALLOWED_OFF_ROW_KEYS | frozenset({'counters'})

SCALAR_COUNTER_KEYS = frozenset({
    'distance_evaluations', 'unique_distance_evaluations', 'duplicate_distance_evaluations',
    'expansions', 'unique_expansions', 'duplicate_expansions',
    'neighbor_attempts', 'already_seen_attempts', 'frontier_insertions',
    'sync_merge_count', 'sync_wait_ns', 'barrier_wait_ns', 'merge_time_ns', 'worker_idle_ns',
})
ARRAY_COUNTER_KEYS = frozenset({
    'per_worker_expansions', 'per_worker_distance_evaluations', 'per_worker_idle_rounds',
})
REQUIRED_COUNTER_KEYS = SCALAR_COUNTER_KEYS | ARRAY_COUNTER_KEYS


def classify_counters_field(row):
    """Explicitly classify `counters` presence/type without conflating absent vs null."""
    require(isinstance(row, dict), 'malformed row: expected JSON object')
    if 'counters' not in row:
        return 'absent'
    value = row['counters']
    if value is None:
        return 'explicit_null'
    if isinstance(value, dict):
        return 'object'
    return 'malformed'


def validate_row_counters(row, *, mode, base_count=1000000):
    """Strictly validate `counters` field against the frozen task_da_p2_eval producer contract.

    - mode == 'OFF': frozen `task_da_p2_eval` omits `counters` (`state == 'absent'`).
      Explicit `null`, non-null dict (including `{}`), and malformed types are each
      explicitly distinguished and rejected fail-closed.
    - mode == 'ON': `counters` must be an exact 17-key dict of strict non-bool integers /
      lists of strict non-bool integers satisfying all frozen `validate_p2_counters_row`
      algebraic invariants.
    """
    require(mode in ('ON', 'OFF'), 'invalid mode')
    state = classify_counters_field(row)
    if mode == 'OFF':
        if state == 'absent':
            return 'absent'
        if state == 'explicit_null':
            raise ValueError(
                'OFF row contains explicit null counters; frozen task_da_p2_eval omits counters in OFF mode'
            )
        if state == 'object':
            raise ValueError('OFF row must not contain counters object')
        raise ValueError(f'OFF row contains malformed non-null counters: {type(row["counters"]).__name__}')

    # mode == 'ON'
    if state == 'absent':
        raise ValueError('ON row missing required counters field')
    if state == 'explicit_null':
        raise ValueError('ON row counters must not be null')
    if state != 'object':
        raise ValueError(f'ON row counters must be a JSON object, got {type(row["counters"]).__name__}')

    c = row['counters']
    keys = set(c.keys())
    if keys != REQUIRED_COUNTER_KEYS:
        missing = sorted(REQUIRED_COUNTER_KEYS - keys)
        extra = sorted(keys - REQUIRED_COUNTER_KEYS)
        raise ValueError(f'ON counters key mismatch: missing={missing} extra={extra}')
    for k in SCALAR_COUNTER_KEYS:
        require(type(c[k]) is int, f'ON counter {k} must be strict integer')
    for k in ARRAY_COUNTER_KEYS:
        arr = c[k]
        require(isinstance(arr, list) and all(type(v) is int for v in arr),
                f'ON counter {k} must be list of strict integers')
    validate_p2_counters_row(row, base_count)
    return 'object'


def output_digest(rows, *, mode, policy):
    """Validate ON/OFF JSONL rows strictly and return deterministic (sha256_hex, qids)."""
    require(mode in ('ON', 'OFF'), 'invalid mode')
    require(policy in POLICIES, 'invalid policy')
    require(isinstance(rows, list) and bool(rows), 'empty/duplicate query output')
    visited, frontier = POLICIES[policy]
    allowed_keys = ALLOWED_ON_ROW_KEYS if mode == 'ON' else ALLOWED_OFF_ROW_KEYS

    digest, qids = hashlib.sha256(), []
    for row in rows:
        require(isinstance(row, dict), 'malformed row: expected JSON object')
        row_keys = set(row.keys())
        missing = REQUIRED_ROW_KEYS - row_keys
        require(not missing, f'malformed row: missing required field(s): {sorted(missing)}')

        # Validate counters state explicitly BEFORE unknown-key check so explicit null /
        # non-null / malformed counters in OFF emit dedicated diagnostic messages.
        validate_row_counters(row, mode=mode, base_count=1000000)

        extra = row_keys - allowed_keys
        require(not extra, f'malformed row: unexpected field(s): {sorted(extra)}')

        require(row['mode'] == mode and row['instrumentation'] is (mode == 'ON'),
                'mode/instrumentation mismatch')
        require(type(row['workers']) is int and row['workers'] == 2
                and type(row['sync_interval']) is int and row['sync_interval'] == 16
                and type(row['beam']) is int and row['beam'] == 432
                and type(row['jobs']) is int and row['jobs'] == 1
                and row['merge_impl'] == 'flat',
                'search configuration mismatch')
        require(row['visited_policy'] == visited and row['frontier_mode'] == frontier,
                'policy mismatch')

        if 'scope' in row:
            require(row['scope'] == 'task_d_a_common_p2_exploratory', 'scope mismatch')
        if 'graph_format' in row:
            require(row['graph_format'] == 'pipnn', 'graph_format mismatch')
        if 'entry' in row:
            require(type(row['entry']) is int and row['entry'] == 0, 'entry mismatch')
        if 'k' in row:
            require(type(row['k']) is int and row['k'] == 10, 'k mismatch')
        if 'latency_ns' in row:
            require(type(row['latency_ns']) is int and row['latency_ns'] > 0, 'invalid latency_ns')

        ids, distances, q = row['ids'], row['squared_l2'], row['query_id']
        require(type(q) is int and 0 <= q < 100000, 'invalid query ID')
        require(isinstance(ids, list) and isinstance(distances, list)
                and len(ids) == len(distances) == 10 and len(set(ids)) == 10
                and row['complete_top_k'] is True,
                'incomplete/nonunique Top10')
        require(all(type(i) is int and 0 <= i < 1000000 for i in ids), 'invalid returned ID')

        digest.update(struct.pack('<I', q))
        for i, d in zip(ids, distances):
            number(d)
            digest.update(struct.pack('<Id', i, d))
        qids.append(q)

    require(len(qids) == len(set(qids)) and bool(qids), 'empty/duplicate query output')
    return digest.hexdigest(), qids


def pair_on(base, opt):
    bd, bq = output_digest(base, mode='ON', policy='base')
    od, oq = output_digest(opt, mode='ON', policy='opt')
    require(bd == od and bq == oq, 'base/opt exact parity failed')
    ignored = {
        'distance_evaluations', 'duplicate_distance_evaluations', 'already_seen_attempts',
        'per_worker_distance_evaluations', 'sync_wait_ns', 'barrier_wait_ns',
        'merge_time_ns', 'worker_idle_ns',
    }
    saved = 0
    for b, c in zip(base, opt):
        u, v = b['counters'], c['counters']
        require({k: x for k, x in u.items() if k not in ignored}
                == {k: x for k, x in v.items() if k not in ignored},
                'B1/A1 invariant failed')
        delta = u['duplicate_distance_evaluations'] - v['duplicate_distance_evaluations']
        require(delta >= 0 and u['distance_evaluations'] - v['distance_evaluations'] == delta
                and v['already_seen_attempts'] - u['already_seen_attempts'] == delta,
                'saved-L2 accounting failed')
        saved += delta
    return dict(parity=True, output_digest=bd, queries=len(bq), duplicate_l2_saved=saved)


def analyze(rows, latency, quality, *, build=None):
    """Delegate 100% of statistical math to frozen design-3 analyzer; stamp design-3.1 identity."""
    result = _d3_analyzer.analyze(rows, latency, quality, build=build)
    result['schema'] = SCHEMA
    result['protocol'] = PROTOCOL
    result['revision'] = REVISION
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--campaign', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    with Path('/tmp/task-da-pivot-4650u.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        started = time.monotonic()
        freeze = load_freeze()
        from .g2_v2_design3_1_runner import load_campaign
        rows, latency, quality = load_campaign(args.campaign)
        result = analyze(rows, latency, quality, build=freeze['build_reference'])
        require(time.monotonic() - started <= 10800, 'analysis quota exhausted; no GO output')
        validate_schema(result, 'analysis')
        write_new(args.output, result)


if __name__ == '__main__':
    main()
