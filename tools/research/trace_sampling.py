"""Versioned deterministic DETAIL policy; no interpretation of scientific phases."""
import hashlib
import re

MAX_SAMPLE_IDS = 1024
MAX_CONFIG_CHARS = 16384
MAX_EXPLICIT_QUERY_COUNT = 1000000


def explicit_policy(ids, query_count):
    if not ids or len(ids) > MAX_SAMPLE_IDS or not 0 < query_count <= MAX_EXPLICIT_QUERY_COUNT:
        raise ValueError('Explicit sample count/query bound invalid')
    if any(type(qid) is not int or not 0 <= qid < query_count for qid in ids) or any(a >= b for a,b in zip(ids, ids[1:])):
        raise ValueError('Explicit query IDs must be strictly ascending, unique and in range')
    canonical = ','.join(map(str, ids))
    if len(canonical) > MAX_CONFIG_CHARS:
        raise ValueError('Sampling configuration too large')
    return {'kind': 'explicit_qids', 'qids': list(ids),
            'sha256': hashlib.sha256((canonical + '\n').encode('ascii')).hexdigest()}


def parse_explicit_qids(text, query_count):
    if not isinstance(text, str) or not text or len(text) > MAX_CONFIG_CHARS:
        raise ValueError('Explicit sampling requires bounded nonempty CSV query IDs')
    tokens = text.split(',')
    if len(tokens) > MAX_SAMPLE_IDS or any(not re.fullmatch(r'0|[1-9][0-9]*', t, flags=re.ASCII) for t in tokens):
        raise ValueError('Noncanonical/oversized query IDs')
    return explicit_policy([int(t) for t in tokens], query_count)


def requested_ids(policy, query_count, trace_mode):
    if policy['kind'] == 'explicit_qids':
        verified = explicit_policy(policy['qids'], query_count)
        if policy != verified:
            raise ValueError('Sampling identity/digest mismatch')
        if trace_mode != 'DETAIL':
            raise ValueError('Explicit sampler requires DETAIL')
        return policy['qids']
    if policy['kind'] != 'first_n' or type(policy.get('first_n')) is not int or not 0 <= policy['first_n'] <= 1000000:
        raise ValueError('Invalid first-N policy')
    return list(range(min(policy['first_n'], query_count))) if trace_mode == 'DETAIL' else []
