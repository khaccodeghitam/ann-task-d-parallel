"""Build one copy-only, aggregate phase observer for the final A3 p2 audit.

The frozen common engine and executable are never edited. No clocks/events in
the neighbor loop, no scheduling changes, no per-round retained trace.
"""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

REPO = Path(__file__).resolve().parents[2]
FIELDS = ('rounds', 'worker_phase_ns', 'gather_publish_ns', 'frontier_dispatch_ns',
          'arrival_tail_ns', 'worker_wait_sum_ns', 'imbalance_ns', 'ideal_balance_ns',
          'worker_duration_sum_ns', 'worker_duration_max_ns', 'active_workers')


def replace_once(source, old, new):
    if source.count(old) != 1:
        raise ValueError(f'Frozen source anchor changed: {old[:70]!r}')
    return source.replace(old, new, 1)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(root):
    root.mkdir(parents=True, exist_ok=False)
    src = REPO/'research/task_da/search_common'
    for name in ('engine.hpp', 'p2_engine.hpp', 'p2_eval.cpp'):
        shutil.copyfile(src/name, root/name)
    p = root/'p2_engine.hpp'
    before = s = p.read_text()
    s = replace_once(s, '  P2Counters counters;\n', '  P2Counters counters;\n' +
        ''.join(f'  uint64_t phase_{f} = 0;\n' for f in FIELDS))
    s = replace_once(s, '  uint64_t work_done_ns = 0;\n',
        '  uint64_t phase_start_ns = 0, phase_done_ns = 0;\n  uint64_t work_done_ns = 0;\n')
    s = replace_once(s, '    ws.was_idle = false;\n',
        '    ws.was_idle = false;\n    ws.phase_start_ns = detail::now_ns();\n')
    s = replace_once(s, '    if constexpr (Instrument) {\n      ws.work_done_ns = detail::now_ns();',
        '    ws.phase_done_ns = detail::now_ns();\n    if constexpr (Instrument) {\n      ws.work_done_ns = detail::now_ns();')
    s = replace_once(s, '      uint64_t t_dispatch = 0;\n',
        '      const uint64_t phase_release = detail::now_ns();\n      uint64_t t_dispatch = 0;\n')
    s = replace_once(s, '      uint64_t t_all_arrived = 0;\n',
        '      const uint64_t phase_arrived = detail::now_ns();\n      uint64_t t_all_arrived = 0;\n')
    s = replace_once(s, '      if constexpr (IncFrontier) {\n        for (size_t w = 0; w < workers_; ++w) {\n          worker_states_[w].init_seeds.clear();',
        '      const uint64_t phase_gather_end = detail::now_ns();\n'
        '      if constexpr (IncFrontier) {\n        for (size_t w = 0; w < workers_; ++w) {\n          worker_states_[w].init_seeds.clear();')
    aggregate = '''      const uint64_t phase_frontier_end = detail::now_ns();
      ++result.phase_rounds;
      result.phase_worker_phase_ns += phase_arrived - phase_release;
      result.phase_gather_publish_ns += phase_gather_end - phase_arrived;
      result.phase_frontier_dispatch_ns += phase_frontier_end - phase_gather_end;
      uint64_t phase_sum = 0, phase_max = 0, phase_last = 0;
      for (size_t w = 0; w < workers_; ++w) {
        const auto& ps = worker_states_[w];
        if (ps.was_idle) continue;
        ++result.phase_active_workers;
        const uint64_t d = ps.phase_done_ns - ps.phase_start_ns;
        phase_sum += d;
        phase_max = std::max(phase_max, d);
        phase_last = std::max(phase_last, ps.phase_done_ns);
        result.phase_worker_wait_sum_ns += phase_arrived - ps.phase_done_ns;
      }
      result.phase_worker_duration_sum_ns += phase_sum;
      result.phase_worker_duration_max_ns += phase_max;
      result.phase_arrival_tail_ns += phase_arrived - phase_last;
      result.phase_imbalance_ns += phase_max - phase_sum / workers_;
      result.phase_ideal_balance_ns += phase_arrived - phase_release - phase_sum / workers_;

'''
    s = replace_once(s, '      if constexpr (Instrument) {\n        ++result.counters.sync_merge_count;',
        aggregate + '      if constexpr (Instrument) {\n        ++result.counters.sync_merge_count;')
    p.write_text(s)
    patch = ''.join(difflib.unified_diff(before.splitlines(True), s.splitlines(True),
                    fromfile='frozen/p2_engine.hpp', tofile='observer/p2_engine.hpp'))
    p = root/'p2_eval.cpp'
    before = s = p.read_text()
    emit = '          os << ",\\\"phase_audit\\\":{\\\"kind\\\":\\\"aggregate_clock_only\\\"";\n'
    emit += ''.join(f'          os << ",\\\"{f}\\\":" << res.phase_{f};\n' for f in FIELDS)
    emit += '          os << \'}\';\n'
    s = replace_once(s, '          if (instrument) {\n            const auto& c = res.counters;',
        emit + '          if (instrument) {\n            const auto& c = res.counters;')
    p.write_text(s)
    patch += ''.join(difflib.unified_diff(before.splitlines(True), s.splitlines(True),
                    fromfile='frozen/p2_eval.cpp', tofile='observer/p2_eval.cpp'))
    (root/'observer.patch').write_text(patch)
    flags = ['-O3', '-DNDEBUG', '-g', '-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror', '-pthread']
    argv = ['c++', *flags, str(root/'p2_eval.cpp'), '-o', str(root/'task_da_phase_eval')]
    run = subprocess.run(argv, capture_output=True, text=True)
    (root/'build.log').write_text(run.stdout + run.stderr)
    run.check_returncode()
    identity = dict(argv=argv, compiler=subprocess.check_output(['c++','--version'],text=True),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        frozen_source_sha256={n:sha(src/n) for n in ('engine.hpp','p2_engine.hpp','p2_eval.cpp')},
        copied_source_sha256={n:sha(root/n) for n in ('engine.hpp','p2_engine.hpp','p2_eval.cpp')},
        binary_sha256=sha(root/'task_da_phase_eval'), patch_sha256=sha(root/'observer.patch'))
    (root/'build_identity.json').write_text(json.dumps(identity,indent=2)+'\n')
    print(json.dumps(identity,indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    build(parser.parse_args().output.resolve())
