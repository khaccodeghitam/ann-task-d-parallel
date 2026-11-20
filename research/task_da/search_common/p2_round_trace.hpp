// SPDX-License-Identifier: MIT
// Bounded observer records only. No assignment policy is executed by search.
#pragma once
#include <array>
#include <ostream>
#include <vector>
namespace task_da {
struct TraceSeed {
  Id id;
  uint32_t worker, rank, degree;
  double distance;
  std::vector<Id> eligible;
};
struct TraceWorker {
  uint64_t start_ns = 0, done_ns = 0, attempts = 0, insertions = 0;
  std::vector<Id> expanded;
  std::vector<std::pair<Id, Id>> evaluated; // parent, evaluated neighbor
};
struct RoundTrace {
  uint64_t prepare_ns = 0, release_ns = 0, arrived_ns = 0, end_ns = 0;
  uint64_t snapshot_ns = 0, copy_ns = 0;
  std::vector<TraceSeed> seeds;
  std::array<TraceWorker, 2> workers;
};
inline void write_round_trace(std::ostream& os, const std::vector<RoundTrace>& rounds,
                              bool overflow) {
  os << ",\"trace_overflow\":" << (overflow ? "true" : "false") << ",\"rounds\":[";
  for (size_t r = 0; r < rounds.size(); ++r) {
    if (r) os << ',';
    const auto& x = rounds[r];
    os << "{\"round\":" << r << ",\"prepare_ns\":" << x.prepare_ns
       << ",\"release_ns\":" << x.release_ns << ",\"arrived_ns\":" << x.arrived_ns
       << ",\"end_ns\":" << x.end_ns << ",\"snapshot_ns\":" << x.snapshot_ns
       << ",\"copy_ns\":" << x.copy_ns << ",\"seeds\":[";
    for (size_t i = 0; i < x.seeds.size(); ++i) {
      if (i) os << ',';
      const auto& s = x.seeds[i];
      os << "{\"id\":" << s.id << ",\"worker\":" << s.worker << ",\"rank\":" << s.rank
         << ",\"degree\":" << s.degree << ",\"distance\":" << s.distance << ",\"eligible\":[";
      for (size_t j = 0; j < s.eligible.size(); ++j) { if (j) os << ','; os << s.eligible[j]; }
      os << "]}";
    }
    os << "],\"workers\":[";
    for (size_t w = 0; w < 2; ++w) {
      if (w) os << ',';
      const auto& t = x.workers[w];
      os << "{\"start_ns\":" << t.start_ns << ",\"done_ns\":" << t.done_ns
         << ",\"attempts\":" << t.attempts << ",\"insertions\":" << t.insertions << ",\"expanded\":[";
      for (size_t j = 0; j < t.expanded.size(); ++j) { if (j) os << ','; os << t.expanded[j]; }
      os << "],\"evaluated\":[";
      for (size_t j = 0; j < t.evaluated.size(); ++j) {
        if (j) os << ',';
        os << '[' << t.evaluated[j].first << ',' << t.evaluated[j].second << ']';
      }
      os << "]}";
    }
    os << "]}";
  }
  os << ']';
}
} // namespace task_da
