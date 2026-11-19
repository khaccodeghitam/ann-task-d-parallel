#!/usr/bin/env python3
"""Run the prospectively locked, Ryzen-only B1/A1 replication."""
import argparse
import csv
import fcntl
import hashlib
import importlib.util
import json
import os
import statistics
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[2]
EVIDENCE = REPO.parent / 'artifact-evidence'
RESUME = EVIDENCE / 'p2-pivot-b1-a1-resume-20261119'
GEMINI = EVIDENCE / 'p2-pivot-b1-a1-20261119'
STAGE_D = EVIDENCE / 'p2-followup-20261118'
STAGE_D_BEAMS = STAGE_D / 'stage_d_val10k_r2_r3/stage_d_val10k_45cells_manifest.json'
DOCS = REPO / 'docs/research/task-da'
PLAN = DOCS / 'B1_A1_NARROW_REPLICATION_PLAN_20261119.md'
PILOT_COMMIT = 'f2cd634b837a70735c3e31e5956f0524bfc26675'
SEALS = {
    RESUME / 'BUNDLE.sha256': '1c0df3150aafaf5fae6aee26018a6309201e0376e41ccb016c380e3ed6c1c173',
    GEMINI / 'EVIDENCE_CHECKSUMS.csv': 'eda452166aa05eb6bd3934e45f2aaf6aecfb57122ff54d3f9340b2b99c725067',
    STAGE_D_BEAMS: 'f98c0454f065e8debf10e7849f2ebcd1061d294980c8ddad5f836269175b4bc5',
    DOCS / 'experiment_manifest_v3_reconciled.json': '9094fb348269918077b37e901b887eae7ac1662c74a45aa43a237cd227e57d16',
    DOCS / 'PROTOCOL_V4_1_P2_EXPLORATORY_0990_ADDENDUM.md': 'ea18b0530e2fa66beae342456ff34634b0ddcb49eacb5c94856cc10c4df4ba8a',
}
ARMS = {'base': ('baseline', 'full'), 'b1': ('barrier_all_evaled', 'full'),
        'a1': ('baseline', 'incremental'), 'combo': ('barrier_all_evaled', 'incremental')}
BEAMS = {'A3_r2': 986, 'A3_r3': 966}
ORDERS = ('base b1 combo a1', 'b1 a1 base combo', 'a1 combo b1 base',
          'combo base a1 b1', 'b1 base a1 combo')


def require(test, description):
    if not test:
        raise RuntimeError(description)


def write_json(path, value):
    with path.open('x') as file:
        json.dump(value, file, indent=2, sort_keys=True, allow_nan=False)
        file.write('\n')


def sha(path):
    with path.open('rb') as file:
        return hashlib.file_digest(file, 'sha256').hexdigest()


def load_pilot():
    for path, expected in SEALS.items():
        require(sha(path) == expected, f'Seal mismatch: {path.name}')
    for path in (RESUME / 'audit.py', RESUME / 'resume.py'):
        seal = next(line.split()[0] for line in (RESUME / 'BUNDLE.sha256').read_text().splitlines()
                    if line.split(maxsplit=1)[1].removeprefix('./') == path.name)
        require(sha(path) == seal, f'Seal mismatch: {path.name}')
    with (GEMINI / 'EVIDENCE_CHECKSUMS.csv').open() as file:
        originals = {row['relative_path']: row['sha256'] for row in csv.DictReader(file)}
    script = GEMINI / 'run_pivot_b1_a1_pilot.py'
    require(sha(script) == 'c6ef2c8fc02143015b7597841aeec28d3027365eb0f607bc2c4674120b82aedd',
            'Gemini runner seal mismatch')
    sys.path.insert(0, str(RESUME))
    spec = importlib.util.spec_from_file_location('sealed_resume', RESUME / 'resume.py')
    resume = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(resume)
    return resume, originals


def telemetry(collector, root, pid=None):
    host = collector(root, pid)
    host['swap_pages'] = {key: int(value) for key, value in
                          map(str.split, Path('/proc/vmstat').read_text().splitlines())
                          if key in ('pswpin', 'pswpout')}
    host['cpu_pressure'] = Path('/proc/pressure/cpu').read_text().splitlines()
    host['competing_processes'] = []
    # Process names and CPU ticks only. The per-sample differences show competing CPU work.
    for path in Path('/proc').glob('[0-9]*/stat'):
        try:
            prefix, fields = path.read_text().rsplit(')', 1)
            os_pid, name = prefix.split(' (', 1)
            fields = fields.split()
            os_pid = int(os_pid)
            if os_pid not in (pid, os.getpid()):
                host['competing_processes'].append(dict(pid=os_pid, name=name,
                    user_ticks=int(fields[11]), system_ticks=int(fields[12]),
                    start_ticks=int(fields[19]), last_cpu=int(fields[36])))
            if name in {'task_da_p1_eval', 'task_da_smoke'} and os_pid != pid:
                host['ann'].append(dict(pid=os_pid, comm=name))
        except (OSError, IndexError, ValueError):
            continue
    return host


def freeze(out, resume, originals):
    prior = resume.pilot
    frozen = resume.read(STAGE_D_BEAMS)
    for graph, beam in BEAMS.items():
        require(frozen['selected_45_cells'][graph]['S16']['2']['beam'] == beam, graph)
        prior.GRAPHS[graph] = prior.GRAPHS['A3_r1'].parents[1] / graph[-2:] / 'index.graph'
        require(sha(prior.GRAPHS[graph]) == frozen['graph_sha256s'][graph], graph)
    staging = resume.read(DOCS / 'experiment_manifest_v3_reconciled.json')
    artifacts = list(staging['dataset']['artifacts'].values()) + staging['graphs']
    indexed = {row['path']: row['verified_actual_sha256'] for row in artifacts}
    assets = [prior.BASE_PATH, prior.QUERY_PATH, prior.GT_PATH, *(prior.GRAPHS[g] for g in BEAMS)]
    for path in assets:
        require(sha(path) == indexed[str(path.relative_to(prior.GRAPH_ROOT))], path)
    val = prior.V3_SPLIT / 'val_10k.ids'
    test = prior.V3_SPLIT / 'test_90k.ids'
    smoke, asan, old_disjoint = (GEMINI / name for name in
        ('smoke_val_500.ids', 'asan_val_100.ids', 'disjoint_test_3000.ids'))
    for path in (smoke, asan, old_disjoint):
        require(sha(path) == originals[path.name], path)
    require(sha(val) == frozen['val_10k_sha256'], val)
    require(sha(test) == 'af871517d88aaad90549ba2fde0d4ed745f59400037a757f17bc93fa479bbfa3', test)
    require(sha(prior.PILOT_IDS) == '18d8b901e925d71c0ddb2d043bf2cba12edab4061859da833bd1ccc37790c1b0', prior.PILOT_IDS)
    require(sha(prior.WARMUP_IDS) == '199ca6066269641347280d6ef4eaab39efee3397b87c23cd74d38ee85bcd4783', prior.WARMUP_IDS)
    require(sha(prior.REL_BIN) == resume.REL_SHA, prior.REL_BIN)
    require(sha(prior.ASAN_BIN) == 'c3151165f23cffeec41d6ec508a2339b9eb7db627f708d470dcfc0b622c09ea7', prior.ASAN_BIN)
    excluded = set(resume.ids(prior.PILOT_IDS)) | set(resume.ids(old_disjoint))
    selected = [value for value in resume.ids(test) if value not in excluded][:3000]
    require(len(selected) == 3000 and not set(selected).intersection(resume.ids(val)), 'Invalid test split')
    study_ids = out / 'narrow_test_3000.ids'
    with study_ids.open('x') as file:
        file.writelines(f'{value}\n' for value in selected)
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    expected_paths = subprocess.check_output(['git', 'diff', PILOT_COMMIT, '--',
        'research/task_da/search_common', 'tests/research/test_task_da.py'], text=True)
    require(not expected_paths, 'Pilot engine or correctness suite differs from the sealed source')
    paths = [*SEALS, *assets, val, test, smoke, asan, prior.PILOT_IDS, old_disjoint,
             prior.WARMUP_IDS, prior.REL_BIN, prior.ASAN_BIN, study_ids, PLAN,
             Path(__file__), Path(resume.guard.__file__)]
    write_json(out / 'frozen.json', dict(label='EXPLORATORY_HOST_SPECIFIC', source_commit=source,
        pilot_commit=PILOT_COMMIT, beams=BEAMS, arms=ARMS, base_orders=ORDERS, cpus=[0, 2],
        floor=0.990, matched_max_span=0.0001, decision_min_percent=5,
        files_sha256={os.path.relpath(p, out): sha(p) for p in paths}))
    print(f'STUDY FROZEN {sha(out / "frozen.json")} | IDs {sha(study_ids)}', flush=True)
    return val, smoke, asan, study_ids


def evaluate(resume, out, graph, arm, mode, query_ids, binary=None):
    prior = resume.pilot
    binary = binary or prior.REL_BIN
    visited, frontier = ARMS[arm]
    beam = BEAMS[graph]
    out.parent.mkdir(parents=True, exist_ok=True)
    resume.preflight(out.parent, wait_for_cooling=True)
    argv = [str(binary), 'pipnn', str(prior.GRAPHS[graph]), str(prior.BASE_PATH),
            str(prior.QUERY_PATH), '--entry', '0', '--k', '10', '--beams', str(beam),
            '--workers', '2', '--sync-interval', '16', '--merge-impl', 'flat',
            '--visited-policy', visited, '--frontier-mode', frontier, '--jobs', '1',
            '--cpu-list', '0,2', '--query-ids', str(query_ids), '--warmup-ids', str(prior.WARMUP_IDS),
            '--mode', mode, '--out-dir', str(out)]
    extra = {'ASAN_OPTIONS': 'detect_leaks=1:halt_on_error=1',
             'UBSAN_OPTIONS': 'halt_on_error=1:print_stacktrace=1'} if binary == prior.ASAN_BIN else {}
    print(f'{out.parent.name}/{out.name} {mode}', flush=True)
    receipt = resume.guard.run(dict(argv=argv, binary_sha256=sha(binary), threads=1, timeout_s=180,
                                    extra_environment=extra), out)
    require(receipt['exit_code'] == 0 and not receipt['guard_failure'] and receipt['host_samples'],
            f'Guarded evaluator failed: {out}')
    summary, rows = resume.run(out, graph, 2, 16, beam, visited, frontier, mode, resume.ids(query_ids))
    write_json(out / 'checkpoint.json', {p.name: sha(p) for p in sorted(out.iterdir())})
    return summary, rows


def compare(resume, data):
    ref = resume.payload(data['base'])
    for arm, rows in data.items():
        require(resume.payload(rows) == ref, f'Exact top-10 and squared-L2 mismatch: {arm}')
    resume.invariant(data['a1'], data['base'])
    resume.invariant(data['combo'], data['b1'])
    resume.invariant(data['b1'], data['base'], True)


def smoke_check(resume, root, smoke, asan):
    for build in ('build-task-da', 'build-task-da-asan'):
        resume.preflight(root)
        with (root / f'ctest-{build}.log').open('x') as log:
            subprocess.run(['ctest', '--test-dir', build, '-V'], stdout=log, stderr=subprocess.STDOUT,
                check=True, timeout=90, env={**os.environ, 'ASAN_OPTIONS': 'detect_leaks=1:halt_on_error=1',
                                             'UBSAN_OPTIONS': 'halt_on_error=1:print_stacktrace=1'})
    for graph in BEAMS:
        on = {}
        for arm in ARMS:
            for label, query_ids, binary in (('smoke', smoke, resume.pilot.REL_BIN),
                                             ('asan', asan, resume.pilot.ASAN_BIN)):
                pair = {}
                for mode in ('ON', 'OFF'):
                    _, pair[mode] = evaluate(resume, root / label / f'{graph}_{arm}_{mode}',
                                             graph, arm, mode, query_ids, binary)
                require(resume.payload(pair['ON']) == resume.payload(pair['OFF']), 'Smoke ON/OFF mismatch')
                if label == 'smoke':
                    on[arm] = pair['ON']
                else:
                    require(resume.payload(pair['ON']) == resume.payload(on[arm][:100]), 'ASan/Release mismatch')
        compare(resume, on)


def quality(resume, root, phase, query_ids, gt):
    observed = []
    on_rows = {}
    for graph in BEAMS:
        by_arm = {}
        for arm in ARMS:
            summary, by_arm[arm] = evaluate(resume, root / phase / f'{graph}_{arm}', graph, arm, 'ON', query_ids)
            point, se = resume.pilot.recall_stats(by_arm[arm], *gt)
            observed.append(dict(graph=graph, arm=arm, beam=BEAMS[graph], point=point,
                                 lcb95=point - 1.96 * se, se=se,
                                 counters_per_query=resume.pilot.mean_counters(summary)))
        on_rows[graph] = by_arm
    numeric_gate = True
    for row in observed:
        group = [r for r in observed if r['graph'] == row['graph']]
        baseline = next(r['point'] for r in group if r['arm'] == 'base')
        row['delta_from_baseline'] = row['point'] - baseline
        row['matched_span'] = max(r['point'] for r in group) - min(r['point'] for r in group)
        row['pass'] = row['point'] >= .990 and row['matched_span'] <= .0001
        if phase == 'validation':
            reference = resume.read(STAGE_D_BEAMS)['selected_45_cells'][row['graph']]['S16']['2']
            row['pass'] &= row['lcb95'] >= .990 and abs(row['point'] - reference['recall_at_10']) < 1e-10
        numeric_gate &= row['pass']
    span = max(row['point'] for row in observed) - min(row['point'] for row in observed)
    numeric_gate &= phase != 'validation' or span <= .0001
    write_json(root / f'{phase}_quality.json', dict(rows=observed, global_span=span, numeric_pass=numeric_gate))
    for by_arm in on_rows.values():
        compare(resume, by_arm)
    require(numeric_gate, f'{phase} quality gate failed. OFF timing remains unopened.')
    return {graph: resume.payload(by_arm['base']) for graph, by_arm in on_rows.items()}


def main(root):
    require(__debug__, 'Pilot validators require assertions')
    require(Path.cwd() == REPO, 'Run from repository root')
    require(Path('/proc/1/comm').read_text().strip() == 'systemd', 'Native Ryzen host PID visibility required')
    require(root.is_absolute() and not root.is_relative_to(REPO), 'Use a new external evidence directory')
    resume, originals = load_pilot()
    resume.verify_hardware()
    prior_snapshot = resume.augmented_snapshot

    def snapshot(path, pid=None):
        return telemetry(prior_snapshot, path, pid)

    resume.augmented_snapshot = snapshot
    resume.guard.host_snapshot = snapshot
    with Path('/tmp/task-da-pivot-4650u.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        initial = resume.preflight(root.parent)
        require(resume.RyzenGuard(initial).check({**initial, 'sensors': {}}, 1), 'Missing sensor gate failed')
        hot = {'k10temp': dict(value_C=95, name='k10temp', label='Tctl', critical_mC=None)}
        require('k10temp Tctl 95.000C >= 95C' in resume.RyzenGuard(initial).check({**initial, 'sensors': hot}, 1),
                'Thermal guard failed')
        root.mkdir()
        write_json(root / 'initial_host.json', initial)
        with (root / 'topology.txt').open('x') as log:
            for command in (['uname', '-sr'], ['lscpu'], ['lscpu', '-e'], ['free', '-h'], ['c++', '--version']):
                subprocess.run(command, stdout=log, check=True)
        phase = 'freeze'
        try:
            val, smoke, asan, query_ids = freeze(root, resume, originals)
            phase = 'correctness'
            smoke_check(resume, root, smoke, asan)
            phase = 'validation'
            gt = resume.pilot.load_gt()
            quality(resume, root, phase, val, gt)
            phase = 'test_on'
            oracle = quality(resume, root, phase, query_ids, gt)
            phase = 'off'
            for repeat, order in enumerate(ORDERS, 1):
                for graph in (tuple(BEAMS) if repeat % 2 else tuple(reversed(BEAMS))):
                    schedule = order.split() if graph == 'A3_r2' else order.split()[::-1]
                    for position, arm in enumerate(schedule, 1):
                        _, rows = evaluate(resume, root / phase / f'block{repeat}_{graph}' /
                                           f'{position}_{arm}', graph, arm, 'OFF', query_ids)
                        require(resume.payload(rows) == oracle[graph], f'OFF output mismatch: {graph}/{arm}')
            write_json(root / 'checkpoint.json', dict(status='COMPLETE', phase='off', off=40, test_on=8))
        except BaseException as error:
            write_json(root / 'checkpoint.json', dict(status='HOLD', phase=phase, reason=str(error)))
            raise
        finally:
            with (root / 'BUNDLE.sha256').open('x') as manifest:
                for path in sorted(root.rglob('*')):
                    if path.is_file() and path != root / 'BUNDLE.sha256':
                        manifest.write(f'{sha(path)}  {path.relative_to(root)}\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence', type=Path, help='New absolute path outside the repository')
    main(parser.parse_args().evidence)
