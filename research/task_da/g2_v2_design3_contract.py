"""Independent G2 v2 design-3 p2/S16 contract. Importing never reads ANN artifacts.

Preserves 100% of design-2 quality/statistical/beam/schedule/resource estimands;
only amends the B1 CPU noise guard, telemetry accounting, and qualification gate.
Strictly rejects design-2 approval receipts (schema axd_g2_v2.2 / revision design-2).
"""
from datetime import datetime
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import sys

PROTOCOL = 'AXD-G2-V2-3A-20261123'
REVISION = 'design-3'
SCHEMA = 'axd_g2_v2.3'
GRAPHS = tuple(f'{arm}_off_r{r}' for arm in ('stock', 'fast') for r in (1, 2, 3))
ORDER = ('stock_off_r1', 'fast_off_r1', 'stock_off_r2', 'fast_off_r2', 'stock_off_r3', 'fast_off_r3')
POLICIES = {'base': ('baseline', 'full'), 'opt': ('barrier_all_evaled', 'incremental')}
CPUS = [0, 2]
WORKER_CORES_CPUS = (0, 1, 2, 3)
CCX0_CPUS = (0, 1, 2, 3, 4, 5)
ALL_HOST_CPUS = tuple(range(12))
BEAM = 432
N = 10000
BLOCKS = 12
SEED = 20261123
BOOTSTRAPS = 10000
QUERY_BLOCK = 100
THETA = -math.log(.97)
TIE_EPS = 1e-12  # conservative numerical ties, never a post-data tolerance
Z_FLOOR = 2.3939797998185104
QUALIFICATION_DURATION_S = 900
ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / 'docs/research/task-da/AXD_G2_V2_DESIGN3_FREEZE_MANIFEST.json'
SCHEMA_PATH = ROOT / 'configs/axd_g2_v2_design3.schema.json'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def number(x, *, positive=False):
    require(type(x) in (int, float) and math.isfinite(x), 'missing/nonfinite numeric field')
    require(x > 0 if positive else x >= 0, 'negative/zero numeric field')
    return float(x)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def require_default_loader(environment):
    for key in ('LD_PRELOAD', 'LD_LIBRARY_PATH', 'LD_AUDIT'):
        require(not environment.get(key), f'unsupported native loader override: {key}')


def write_new(path, value):
    path = Path(path)
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def validate_schema(value, kind):
    from jsonschema import Draft202012Validator, ValidationError
    canonical(value)
    schema = json.loads(SCHEMA_PATH.read_text())
    schema['$ref'] = '#/$defs/' + kind
    try:
        Draft202012Validator(schema).validate(value)
    except ValidationError as exc:
        raise ValueError(f'invalid {kind} schema: {exc.message}') from exc


def schedule():
    rows = []
    for b in range(BLOCKS):
        for graph in ORDER[b % 6:] + ORDER[:b % 6]:
            i = ORDER.index(graph)
            policies = ('base', 'opt') if (i + b + b // 6) % 2 == 0 else ('opt', 'base')
            rows.extend(dict(block=b, graph=graph, policy=p, panel='test', mode='OFF') for p in policies)
    return rows


def quality_schedule():
    return ([dict(block=-1, graph=g, policy='opt', panel='validation', mode='ON') for g in GRAPHS]
            + [dict(block=-1, graph=g, policy=p, panel='test', mode='ON') for g in GRAPHS for p in POLICIES])


def load_freeze(path=FREEZE, *, environment=True):
    f = json.loads(Path(path).read_text())
    require(f.get('protocol') == PROTOCOL and f.get('revision') == REVISION and f.get('schema') == SCHEMA,
            'wrong frozen design-3 protocol/revision/schema')
    require(f.get('beam') == BEAM and f.get('cpus') == CPUS and f.get('workers') == 2, 'retuning forbidden')
    for rel, digest in f['components'].items():
        require(sha(ROOT / rel) == digest, f'component changed: {rel}')
    if environment:
        require('.'.join(map(str, sys.version_info[:3])) == f['python'], 'Python version mismatch')
        require(sha(Path(sys.executable).resolve()) == f['python_executable_sha256'], 'Python executable mismatch')
        for name, version in f['dependencies'].items():
            require(importlib.metadata.version(name) == version, f'dependency mismatch: {name}')
    return f


def argv_for(item, artifacts, output):
    require(item['graph'] in GRAPHS and item['policy'] in POLICIES, 'unknown subject')
    require(item['mode'] in ('ON', 'OFF') and item['panel'] in ('validation', 'test'), 'wrong phase')
    visited, frontier = POLICIES[item['policy']]
    return [str(artifacts['binary']), 'pipnn', str(artifacts['graphs'][item['graph']]),
            str(artifacts['base']), str(artifacts['queries']), '--entry', '0', '--k', '10',
            '--beams', str(BEAM), '--workers', '2', '--sync-interval', '16', '--merge-impl', 'flat',
            '--visited-policy', visited, '--frontier-mode', frontier, '--jobs', '1', '--cpu-list', '0,2',
            '--query-ids', str(artifacts['val' if item['panel'] == 'validation' else 'test']),
            '--warmup-ids', str(artifacts['warmup']), '--mode', item['mode'], '--out-dir', str(output)]


def authorize(approval, freeze_digest, artifacts_digest, phase, output, *,
              qualification_digest=None, quality_digest=None):
    # Explicitly reject design-2 or older schema/revision before full schema validation
    require(isinstance(approval, dict), 'approval must be a JSON object')
    require(approval.get('schema') == SCHEMA and approval.get('revision') == REVISION,
            'design-2 or mismatched revision approval rejected; design-3 approval required')
    validate_schema(approval, 'approval')
    require(phase in ('quality', 'off'), 'unknown phase')
    require(datetime.fromisoformat(approval['approved_at']).tzinfo is not None,
            'approval needs an explicit timezone')
    require(approval.get('owner') and approval.get('approved_at'), 'dated owner authorization required')
    require(approval.get('protocol') == PROTOCOL, 'approval protocol mismatch')
    require(approval.get('freeze_sha256') == freeze_digest, 'approval freeze mismatch')
    require(approval.get('artifacts_sha256') == artifacts_digest, 'approval artifact map mismatch')
    require(qualification_digest and approval.get('qualification_sha256') == qualification_digest,
            'design-3 900s host qualification receipt not approved/matched')
    require(approval.get('output_directory') == str(Path(output).resolve()), 'approval output mismatch')
    scopes = ('QUALITY_ONLY',) if phase == 'quality' else ('OFF_A', 'OFF_AB')
    require(approval.get('scope') in scopes, 'phase not authorized')
    if phase == 'off':
        require(quality_digest and approval.get('quality_sha256') == quality_digest,
                'quality receipt not approved')
    else:
        require('quality_sha256' not in approval, 'quality_sha256 not permitted in QUALITY_ONLY approval')
    require(approval.get('quota_s') == (3600 if phase == 'quality' else 10800), 'quota must be frozen')
    require(approval.get('quiet_host_confirmed') is True, 'quiet_host_confirmed must be true')
    return approval['scope']
