"""Controlled G2 v2 amendment design-3.1 contract (p2/S16 OFF counters parser fix).

Preserves 100% of design-3 (and design-2) quality, statistical, beam=432, p=2, S=16,
6-graph R90 v1.3 cohort, 144-OFF schedule, hardware safety, and topology-aware B1
noise-guard contracts. Leaves frozen design-3 (26/26) and design-2 (24/24) untouched.

Authorizes reuse of immutable design-3 Qualification PASS and 18/18 Quality ON receipts
ONLY under strict cryptographic invariance checks against the pinned parent design-3
freeze manifest, and strictly rejects design-2 and prior design-3 approval receipts.
"""
from datetime import datetime
import importlib.metadata
import json
from pathlib import Path
import sys

from .g2_v2_design3_contract import (
    ALL_HOST_CPUS, BEAM, BLOCKS, BOOTSTRAPS, CCX0_CPUS, CPUS, GRAPHS, N, ORDER,
    POLICIES, PROTOCOL, QUALIFICATION_DURATION_S, QUERY_BLOCK, ROOT, SEED,
    THETA, TIE_EPS, WORKER_CORES_CPUS, Z_FLOOR, argv_for, canonical, number,
    quality_schedule, require, require_default_loader, schedule, sha, write_new,
)

REVISION = 'design-3.1'
SCHEMA = 'axd_g2_v2.3.1'

PARENT_DESIGN3_REVISION = 'design-3'
PARENT_DESIGN3_SCHEMA = 'axd_g2_v2.3'
PARENT_DESIGN3_FREEZE = ROOT / 'docs/research/task-da/AXD_G2_V2_DESIGN3_FREEZE_MANIFEST.json'
PARENT_DESIGN3_FREEZE_SHA256 = '425c748329292ffe15db2c52bdf53f5d219b47d1ecf95ac3c76a5429814159ae'
PARENT_DESIGN3_SCHEMA_PATH = ROOT / 'configs/axd_g2_v2_design3.schema.json'

FREEZE = ROOT / 'docs/research/task-da/AXD_G2_V2_DESIGN3_1_FREEZE_MANIFEST.json'
SCHEMA_PATH = ROOT / 'configs/axd_g2_v2_design3_1.schema.json'

# Preserved OFF_EXECUTION_HOLD evidence directory from design-3 (must NEVER be overwritten/reused)
PRESERVED_HOLD_OFF_DIR = Path(
    '/home/thinhbui/Documents/ChatGPT/Research ANN/artifact-evidence/axd-g2-v2-off-design3'
).resolve()

# Shared immutable components whose SHA-256 must match parent design-3 identically for upstream reuse
REUSE_INVARIANT_COMPONENTS = (
    'research/task_da/g2_v2_design3_guard.py',
    'research/task_da/g2_v2_design3_qualify.py',
    'research/task_da/g2_v2_design3_contract.py',
    'research/task_da/g2_v2_design3_analyzer.py',
    'research/task_da/evaluate_p2.py',
    'research/task_da/evaluate_p1.py',
    'research/task_da/evaluate_smoke.py',
    'configs/axd_g2_v2_design3.schema.json',
    'configs/axd_g2_v2_design3_artifacts.proposed.json',
    'configs/axd_g2_v2_build_reference.json',
    'requirements-g2-v2-design3.lock',
    'tools/research/run_paper_fullfan_check.py',
    'tools/research/paper_portable_v2.py',
    'tools/research/paper_rebaseline.py',
    'tools/research/run_ann_experiment.py',
    'tools/research/trace_sampling.py',
    'docs/research/task-da/AXD_G2_PREREG_V2.md',
    'docs/research/task-da/AXD_G2_V2_STATISTICAL_DESIGN.md',
    'docs/research/task-da/AXD_G2_V2_QUERY_SPLIT_AUDIT.md',
    'docs/research/task-da/AXD_G2_V2_GO_NO_GO_CRITERIA.md',
    'docs/research/task-da/AXD_G2_PREREG_V2_DESIGN3_AMENDMENT.md',
)

REUSE_INVARIANT_SECTIONS = (
    'workers',
    'cpus',
    'worker_cores_cpus',
    'ccx0_cpus',
    'beam',
    'sync_interval',
    'queries',
    'warmup',
    'blocks',
    'python',
    'python_executable_sha256',
    'dependencies',
    'compiler',
    'artifact_sha256',
    'graph_sha256',
    'validation_baseline',
    'build_reference',
    'host_profile',
    'statistical_contract',
    'frozen_search_source_files',
    'native_runtime_sha256',
)


def validate_schema(value, kind, *, schema_path=None):
    from jsonschema import Draft202012Validator, ValidationError
    canonical(value)
    schema = json.loads(Path(schema_path or SCHEMA_PATH).read_text())
    schema['$ref'] = '#/$defs/' + kind
    try:
        Draft202012Validator(schema).validate(value)
    except ValidationError as exc:
        raise ValueError(f'invalid {kind} schema: {exc.message}') from exc


def verify_parent_design3_invariants(freeze, *, parent_path=PARENT_DESIGN3_FREEZE):
    """Verify parent design-3 freeze is intact and all guard/subject/statistical pins match."""
    require(freeze.get('parent_design3_freeze_sha256') == PARENT_DESIGN3_FREEZE_SHA256,
            'design-3.1 freeze missing or mismatched parent_design3_freeze_sha256')
    require(Path(parent_path).exists() and sha(parent_path) == PARENT_DESIGN3_FREEZE_SHA256,
            'parent design-3 freeze manifest missing or modified')
    parent = json.loads(Path(parent_path).read_text())
    require(parent.get('protocol') == PROTOCOL and parent.get('revision') == PARENT_DESIGN3_REVISION
            and parent.get('schema') == PARENT_DESIGN3_SCHEMA,
            'parent design-3 identity mismatch')
    for section in REUSE_INVARIANT_SECTIONS:
        require(freeze.get(section) == parent.get(section),
                f'design-3.1 diverged from parent design-3 in invariant section: {section}')
    for rel in REUSE_INVARIANT_COMPONENTS:
        require(rel in freeze['components'] and rel in parent['components']
                and freeze['components'][rel] == parent['components'][rel],
                f'design-3.1 diverged from parent design-3 component pin: {rel}')
    return parent


def load_freeze(path=FREEZE, *, environment=True, check_parent=True):
    f = json.loads(Path(path).read_text())
    require(f.get('protocol') == PROTOCOL and f.get('revision') == REVISION and f.get('schema') == SCHEMA,
            'wrong frozen design-3.1 protocol/revision/schema')
    require(f.get('beam') == BEAM and f.get('cpus') == CPUS and f.get('workers') == 2, 'retuning forbidden')
    for rel, digest in f['components'].items():
        require(sha(ROOT / rel) == digest, f'component changed: {rel}')
    if check_parent:
        verify_parent_design3_invariants(f)
    if environment:
        require('.'.join(map(str, sys.version_info[:3])) == f['python'], 'Python version mismatch')
        require(sha(Path(sys.executable).resolve()) == f['python_executable_sha256'], 'Python executable mismatch')
        for name, version in f['dependencies'].items():
            require(importlib.metadata.version(name) == version, f'dependency mismatch: {name}')
    return f


def authorize(approval, freeze_digest, artifacts_digest, phase, output, *,
              qualification_digest=None, quality_digest=None):
    """Strict design-3.1 authorization; rejects design-2, design-3, and preserved HOLD targets."""
    require(isinstance(approval, dict), 'approval must be a JSON object')
    require(approval.get('schema') == SCHEMA and approval.get('revision') == REVISION,
            'design-2/design-3 or mismatched revision approval rejected; design-3.1 approval required')
    validate_schema(approval, 'approval')
    require(phase in ('quality', 'off'), 'unknown phase')
    require(datetime.fromisoformat(approval['approved_at']).tzinfo is not None,
            'approval needs an explicit timezone')
    require(approval.get('owner') and approval.get('approved_at'), 'dated owner authorization required')
    require(approval.get('protocol') == PROTOCOL, 'approval protocol mismatch')
    require(approval.get('freeze_sha256') == freeze_digest, 'approval freeze mismatch')
    require(approval.get('parent_design3_freeze_sha256') == PARENT_DESIGN3_FREEZE_SHA256,
            'approval parent_design3_freeze_sha256 mismatch')
    require(approval.get('artifacts_sha256') == artifacts_digest, 'approval artifact map mismatch')
    require(qualification_digest and approval.get('qualification_sha256') == qualification_digest,
            '900s host qualification receipt not approved/matched')
    resolved_output = Path(output).resolve()
    require(resolved_output != PRESERVED_HOLD_OFF_DIR,
            'preserved design-3 OFF_EXECUTION_HOLD directory cannot be targeted or reused')
    require(approval.get('output_directory') == str(resolved_output), 'approval output mismatch')
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


__all__ = [
    'ALL_HOST_CPUS', 'BEAM', 'BLOCKS', 'BOOTSTRAPS', 'CCX0_CPUS', 'CPUS',
    'FREEZE', 'GRAPHS', 'N', 'ORDER', 'PARENT_DESIGN3_FREEZE',
    'PARENT_DESIGN3_FREEZE_SHA256', 'PARENT_DESIGN3_REVISION',
    'PARENT_DESIGN3_SCHEMA', 'PARENT_DESIGN3_SCHEMA_PATH', 'POLICIES',
    'PRESERVED_HOLD_OFF_DIR', 'PROTOCOL', 'QUALIFICATION_DURATION_S',
    'QUERY_BLOCK', 'REUSE_INVARIANT_COMPONENTS', 'REUSE_INVARIANT_SECTIONS',
    'REVISION', 'ROOT', 'SCHEMA', 'SCHEMA_PATH', 'SEED', 'THETA', 'TIE_EPS',
    'WORKER_CORES_CPUS', 'Z_FLOOR', 'argv_for', 'authorize', 'canonical',
    'load_freeze', 'number', 'quality_schedule', 'require',
    'require_default_loader', 'schedule', 'sha', 'validate_schema',
    'verify_parent_design3_invariants', 'write_new',
]
