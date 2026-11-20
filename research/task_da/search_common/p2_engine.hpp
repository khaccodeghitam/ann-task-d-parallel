// SPDX-License-Identifier: MIT
// Independent P2 multi-walker search session built atop task_da::Graph and Vectors.
#pragma once

#include "engine.hpp"

#include <atomic>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <limits>
#include <numeric>
#include <set>
#include <stdexcept>
#include <string>
#include <thread>
#include <utility>
#include <vector>
#ifdef TASK_DA_ROUND_TRACE
#include "p2_round_trace.hpp"
#endif

#ifdef __linux__
#include <pthread.h>
#include <sched.h>
#endif

namespace task_da {

enum class MergeImpl { kSet, kFlat };
enum class VisitedPolicy { kBaseline, kBarrierAllEvaled };
enum class FrontierMode { kFull, kIncremental };

struct P2Counters {
  uint64_t distance_evaluations = 0;
  uint64_t unique_distance_evaluations = 0;
  uint64_t duplicate_distance_evaluations = 0;
  uint64_t expansions = 0;
  uint64_t unique_expansions = 0;
  uint64_t duplicate_expansions = 0;
  uint64_t neighbor_attempts = 0;
  uint64_t already_seen_attempts = 0;
  uint64_t frontier_insertions = 0;
  uint64_t sync_merge_count = 0;
  uint64_t sync_wait_ns = 0;
  uint64_t barrier_wait_ns = 0;
  uint64_t merge_time_ns = 0;
  uint64_t worker_idle_ns = 0;
  std::vector<uint64_t> per_worker_expansions;
  std::vector<uint64_t> per_worker_distance_evaluations;
  std::vector<uint64_t> per_worker_idle_rounds;
};

struct P2Result {
  std::vector<Hit> hits;
  P2Counters counters;
#ifdef TASK_DA_ROUND_TRACE
  std::vector<RoundTrace> rounds;
  bool trace_overflow = false;
#endif
};

namespace detail {

inline uint64_t now_ns() noexcept {
  return static_cast<uint64_t>(
      std::chrono::duration_cast<std::chrono::nanoseconds>(
          std::chrono::steady_clock::now().time_since_epoch())
          .count());
}

inline void cpu_relax() noexcept {
#if defined(__x86_64__) || defined(_M_X64) || defined(__i386__)
  __builtin_ia32_pause();
#endif
}

inline int pin_current_thread(int cpu_id) {
#ifdef __linux__
  if (cpu_id < 0) return -1;
  cpu_set_t cpuset;
  CPU_ZERO(&cpuset);
  CPU_SET(cpu_id, &cpuset);
  if (pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset) != 0) {
    throw std::runtime_error("pthread_setaffinity_np failed for CPU " + std::to_string(cpu_id));
  }
  return sched_getcpu();
#else
  (void)cpu_id;
  return -1;
#endif
}

inline int current_cpu() noexcept {
#ifdef __linux__
  return sched_getcpu();
#else
  return -1;
#endif
}

// Fast O(1)-reset power-of-two flat open-addressing set for intra-round discovery tracking.
struct LocalRoundSet {
  std::vector<Id> keys;
  std::vector<uint32_t> stamps;
  uint32_t epoch = 1;
  size_t count = 0;

  explicit LocalRoundSet(size_t initial_cap = 4096)
      : keys(initial_cap, 0), stamps(initial_cap, 0) {}

  void reset() {
    count = 0;
    ++epoch;
    if (epoch == 0) {
      std::fill(stamps.begin(), stamps.end(), 0);
      epoch = 1;
    }
  }

  void grow() {
    std::vector<Id> old_keys = std::move(keys);
    std::vector<uint32_t> old_stamps = std::move(stamps);
    const size_t new_cap = old_keys.size() * 2;
    keys.assign(new_cap, 0);
    stamps.assign(new_cap, 0);
    const size_t mask = new_cap - 1;
    for (size_t i = 0; i < old_keys.size(); ++i) {
      if (old_stamps[i] == epoch) {
        size_t pos = (static_cast<size_t>(old_keys[i]) * 2654435761u) & mask;
        while (stamps[pos] == epoch) pos = (pos + 1) & mask;
        keys[pos] = old_keys[i];
        stamps[pos] = epoch;
      }
    }
  }

  // Returns true if id was already present in this round, false if newly inserted.
  bool contains_or_insert(Id id) {
    if ((count + 1) * 2 >= keys.size()) grow();
    const size_t mask = keys.size() - 1;
    size_t pos = (static_cast<size_t>(id) * 2654435761u) & mask;
    while (stamps[pos] == epoch) {
      if (keys[pos] == id) return true;
      pos = (pos + 1) & mask;
    }
    keys[pos] = id;
    stamps[pos] = epoch;
    ++count;
    return false;
  }
};

struct alignas(64) WorkerState {
#ifdef TASK_DA_ROUND_TRACE
  TraceWorker trace;
#endif
  std::atomic<uint64_t> done_seq{0};
  std::vector<Hit> init_seeds;
  std::set<Hit> local_top;
  std::set<Hit> local_pending;
  std::vector<Hit> local_discovered;
  std::vector<Id> local_expanded;
  std::vector<Id> local_newly_evaled;
  LocalRoundSet local_seen;

  uint64_t work_done_ns = 0;
  uint64_t round_dist_evals = 0;
  uint64_t round_expansions = 0;
  uint64_t round_neighbor_attempts = 0;
  uint64_t round_already_seen = 0;
  uint64_t round_frontier_insertions = 0;
  bool was_idle = false;
};

}  // namespace detail

class P2SearchSession {
 public:
  P2SearchSession(const Graph& graph, const Vectors& base, size_t workers,
                  size_t sync_interval = 8, std::vector<int> cpu_list = {},
                  MergeImpl merge_impl = MergeImpl::kSet,
                  VisitedPolicy visited_policy = VisitedPolicy::kBaseline,
                  FrontierMode frontier_mode = FrontierMode::kFull)
      : graph_(graph),
        base_(base),
        workers_(workers),
        sync_interval_(sync_interval),
        cpu_list_(std::move(cpu_list)),
        merge_impl_(merge_impl),
        visited_policy_(visited_policy),
        frontier_mode_(frontier_mode),
        settled_epoch_(base.n, 0),
        global_expanded_epoch_(base.n, 0),
        worker_states_(workers) {
    if (graph_.size() != base_.n || !base_.n || !base_.dim) {
      throw std::invalid_argument("P2SearchSession graph/base shape mismatch");
    }
    if (workers_ != 1 && workers_ != 2 && workers_ != 4) {
      throw std::invalid_argument("workers must be 1, 2, or 4");
    }
    if (!sync_interval_) {
      throw std::invalid_argument("sync_interval must be >= 1");
    }
    if (!cpu_list_.empty() && cpu_list_.size() != workers_) {
      throw std::invalid_argument("cpu_list length must match workers");
    }
    if (frontier_mode_ == FrontierMode::kIncremental && merge_impl_ != MergeImpl::kFlat) {
      throw std::invalid_argument("frontier_mode incremental requires merge_impl flat");
    }

    observed_cpus_.assign(workers_, -1);
    if (!cpu_list_.empty()) {
      observed_cpus_[0] = detail::pin_current_thread(cpu_list_[0]);
    } else {
      observed_cpus_[0] = detail::current_cpu();
    }

    if (workers_ > 1) {
      threads_.reserve(workers_ - 1);
      for (size_t w = 1; w < workers_; ++w) {
        threads_.emplace_back([this, w]() { worker_loop(w); });
      }
      // Wait for helper threads to finish pinning/initialization before returning.
      for (size_t w = 1; w < workers_; ++w) {
        while (worker_states_[w].done_seq.load(std::memory_order_acquire) == 0) {
          detail::cpu_relax();
        }
        worker_states_[w].done_seq.store(0, std::memory_order_relaxed);
      }
    }
  }

  ~P2SearchSession() { stop_threads(); }

  P2SearchSession(const P2SearchSession&) = delete;
  P2SearchSession& operator=(const P2SearchSession&) = delete;

  void stop_threads() {
    if (threads_.empty()) return;
    shutdown_.store(true, std::memory_order_release);
    work_seq_.store(round_seq_ + 1, std::memory_order_release);
    for (auto& t : threads_) {
      if (t.joinable()) t.join();
    }
    threads_.clear();
  }

  const std::vector<int>& observed_cpus() const noexcept { return observed_cpus_; }
  size_t workers() const noexcept { return workers_; }
  size_t sync_interval() const noexcept { return sync_interval_; }
  MergeImpl merge_impl() const noexcept { return merge_impl_; }
  VisitedPolicy visited_policy() const noexcept { return visited_policy_; }
  FrontierMode frontier_mode() const noexcept { return frontier_mode_; }
#ifdef TASK_DA_ROUND_TRACE
  void enable_round_trace(bool enabled) {
    if (enabled && (workers_ != 2 || sync_interval_ != 16 || graph_.max_degree > 64 ||
        merge_impl_ != MergeImpl::kFlat || visited_policy_ != VisitedPolicy::kBarrierAllEvaled ||
        frontier_mode_ != FrontierMode::kIncremental))
      throw std::invalid_argument("trace requires p2 S16 flat+B1+A1 degree<=64");
    trace_enabled_ = enabled;
    if (enabled) for (auto& ws : worker_states_) {
      ws.trace.evaluated.reserve(1024);
      ws.trace.expanded.reserve(16);
    }
  }
#endif

  template <bool Instrument>
  P2Result search(const std::vector<float>& query, size_t k, size_t beam) {
#ifdef TASK_DA_ROUND_TRACE
    if (!Instrument && trace_enabled_) throw std::invalid_argument("trace requires counters ON");
#endif
    if (query.size() != base_.dim || !k || k > beam || beam > base_.n) {
      throw std::invalid_argument("search shape/k/beam");
    }
    for (float x : query) {
      if (!std::isfinite(x)) throw std::invalid_argument("nonfinite query");
    }
    if (workers_ > 1 && threads_.empty()) {
      throw std::runtime_error("P2SearchSession worker pool already stopped");
    }
    if (workers_ == 1) {
      return search_single<Instrument>(query, k, beam);
    }
    const bool mark_all = (visited_policy_ == VisitedPolicy::kBarrierAllEvaled);
    const bool inc_frontier = (frontier_mode_ == FrontierMode::kIncremental);
    if (merge_impl_ == MergeImpl::kFlat) {
      if (mark_all) {
        if (inc_frontier) return search_multi<Instrument, true, true, true>(query, k, beam);
        return search_multi<Instrument, true, true, false>(query, k, beam);
      }
      if (inc_frontier) return search_multi<Instrument, true, false, true>(query, k, beam);
      return search_multi<Instrument, true, false, false>(query, k, beam);
    }
    if (mark_all) return search_multi<Instrument, false, true, false>(query, k, beam);
    return search_multi<Instrument, false, false, false>(query, k, beam);
  }

 private:
  struct FlatEntry {
    Hit hit;
    uint8_t expanded;
  };

  const Graph& graph_;
  const Vectors& base_;
  const size_t workers_;
  const size_t sync_interval_;
  const std::vector<int> cpu_list_;
  const MergeImpl merge_impl_;
  const VisitedPolicy visited_policy_;
  const FrontierMode frontier_mode_;
  std::vector<int> observed_cpus_;

  // Persistent epoch arrays avoid per-query O(n) memset overhead fairly across p=1,2,4.
  std::vector<uint16_t> settled_epoch_;
  std::vector<uint16_t> global_expanded_epoch_;
  uint16_t query_epoch_ = 0;

  // Lazy Mode-ON distinct tracking arrays (never allocated/touched in Mode OFF).
  std::vector<uint32_t> disc_seen_epoch_;
  std::vector<uint32_t> exp_seen_epoch_;
  uint32_t on_epoch_ = 0;

  // Shared global containers reused across queries by worker 0.
  std::set<Hit> global_best_;
  std::vector<Hit> global_best_vec_;
  std::vector<Hit> merge_scratch_;
  std::vector<Hit> next_best_vec_;
  std::vector<FlatEntry> global_best_flat_;
  std::vector<FlatEntry> next_best_flat_;
  std::vector<Hit> active_frontier_;

  alignas(64) std::atomic<uint64_t> work_seq_{0};
  alignas(64) std::atomic<bool> shutdown_{false};
  uint64_t round_seq_ = 0;

  // Active round parameters published before advancing work_seq_.
  const std::vector<float>* active_query_ = nullptr;
  size_t active_beam_ = 0;
  bool active_instrument_ = false;
  bool global_has_full_beam_ = false;
  Hit global_worst_hit_{0.0, 0};

  std::vector<detail::WorkerState> worker_states_;
  std::vector<std::thread> threads_;
#ifdef TASK_DA_ROUND_TRACE
  bool trace_enabled_ = false, trace_active_ = false;
#endif

  uint16_t next_query_epoch() {
    ++query_epoch_;
    if (query_epoch_ == 0) {
      std::fill(settled_epoch_.begin(), settled_epoch_.end(), uint16_t{0});
      std::fill(global_expanded_epoch_.begin(), global_expanded_epoch_.end(), uint16_t{0});
      query_epoch_ = 1;
    }
    return query_epoch_;
  }

  uint32_t next_on_epoch() {
    if (disc_seen_epoch_.empty()) {
      disc_seen_epoch_.assign(base_.n, 0);
      exp_seen_epoch_.assign(base_.n, 0);
    }
    ++on_epoch_;
    if (on_epoch_ == 0) {
      std::fill(disc_seen_epoch_.begin(), disc_seen_epoch_.end(), 0);
      std::fill(exp_seen_epoch_.begin(), exp_seen_epoch_.end(), 0);
      on_epoch_ = 1;
    }
    return on_epoch_;
  }

  double squared_l2(Id node, const std::vector<float>& query) const noexcept {
    const size_t dim = base_.dim;
    const size_t base_offset = static_cast<size_t>(node) * dim;
    double distance = 0.0;
    for (size_t d = 0; d < dim; ++d) {
      const double delta =
          static_cast<double>(base_.values[base_offset + d]) - static_cast<double>(query[d]);
      distance += delta * delta;
    }
    return distance;
  }

  template <bool Instrument, bool MarkAllEvaled>
  void run_worker_round(size_t w, uint16_t q_epoch) {
    detail::WorkerState& ws = worker_states_[w];
#ifdef TASK_DA_ROUND_TRACE
    if (trace_active_) {
      ws.trace.evaluated.clear();
      ws.trace.expanded.clear();
      ws.trace.attempts = ws.trace.insertions = 0;
      ws.trace.start_ns = detail::now_ns();
      ws.trace.done_ns = ws.trace.start_ns;
    }
#endif
    if (ws.init_seeds.empty()) {
      ws.was_idle = true;
      return;
    }
    ws.was_idle = false;
    ws.local_seen.reset();
    ws.local_top.clear();
    ws.local_pending.clear();
    ws.local_discovered.clear();
    ws.local_expanded.clear();
    if constexpr (Instrument || MarkAllEvaled) {
      ws.local_newly_evaled.clear();
    }
    if constexpr (Instrument) {
      ws.round_dist_evals = 0;
      ws.round_expansions = 0;
      ws.round_neighbor_attempts = 0;
      ws.round_already_seen = 0;
      ws.round_frontier_insertions = 0;
    }

    for (const Hit& seed : ws.init_seeds) {
      ws.local_pending.insert(seed);
    }

    const auto& query = *active_query_;
    const size_t beam = active_beam_;
    const bool has_full = global_has_full_beam_;
    const Hit global_worst = global_worst_hit_;

    size_t steps = 0;
    while (steps < sync_interval_ && !ws.local_pending.empty()) {
      const Id node = ws.local_pending.begin()->second;
      ws.local_pending.erase(ws.local_pending.begin());
      ws.local_expanded.push_back(node);
#ifdef TASK_DA_ROUND_TRACE
      if (trace_active_) ws.trace.expanded.push_back(node);
#endif
      ++steps;
      if constexpr (Instrument) ++ws.round_expansions;

      const size_t edge_end = graph_.offsets[node + 1];
      for (size_t edge = graph_.offsets[node]; edge < edge_end; ++edge) {
        if constexpr (Instrument) ++ws.round_neighbor_attempts;
        const Id nbr = graph_.edges[edge];
        if (settled_epoch_[nbr] == q_epoch || ws.local_seen.contains_or_insert(nbr)) {
          if constexpr (Instrument) ++ws.round_already_seen;
          continue;
        }
        const double distance = squared_l2(nbr, query);
#ifdef TASK_DA_ROUND_TRACE
        if (trace_active_) ws.trace.evaluated.emplace_back(node, nbr);
#endif
        if constexpr (Instrument || MarkAllEvaled) {
          ws.local_newly_evaled.push_back(nbr);
        }
        if constexpr (Instrument) {
          ++ws.round_dist_evals;
        }
        const Hit hit{distance, nbr};
        if (has_full && !(hit < global_worst)) continue;
        if (ws.local_top.size() < beam || hit < *ws.local_top.rbegin()) {
          ws.local_top.insert(hit);
          ws.local_pending.insert(hit);
          ws.local_discovered.push_back(hit);
          if constexpr (Instrument) ++ws.round_frontier_insertions;
          if (ws.local_top.size() > beam) {
            const Hit worst = *ws.local_top.rbegin();
            ws.local_top.erase(worst);
            ws.local_pending.erase(worst);
          }
        }
      }
    }

    if constexpr (Instrument) {
      ws.work_done_ns = detail::now_ns();
    }
#ifdef TASK_DA_ROUND_TRACE
    if (trace_active_) {
      ws.trace.done_ns = ws.work_done_ns;
      ws.trace.attempts = ws.round_neighbor_attempts;
      ws.trace.insertions = ws.round_frontier_insertions;
    }
#endif
  }

  void worker_loop(size_t w) {
    if (!cpu_list_.empty()) {
      observed_cpus_[w] = detail::pin_current_thread(cpu_list_[w]);
    } else {
      observed_cpus_[w] = detail::current_cpu();
    }
    worker_states_[w].done_seq.store(1, std::memory_order_release);

    const bool mark_all = (visited_policy_ == VisitedPolicy::kBarrierAllEvaled);
    uint64_t next_seq = 1;
    uint32_t spins = 0;
    while (true) {
      while (work_seq_.load(std::memory_order_acquire) < next_seq) {
        if (spins < 2048) {
          ++spins;
          detail::cpu_relax();
        } else {
          std::this_thread::yield();
        }
      }
      spins = 0;
      if (shutdown_.load(std::memory_order_acquire)) break;

      const uint16_t q_epoch = query_epoch_;
      if (active_instrument_) {
        if (mark_all) run_worker_round<true, true>(w, q_epoch);
        else run_worker_round<true, false>(w, q_epoch);
      } else {
        if (mark_all) run_worker_round<false, true>(w, q_epoch);
        else run_worker_round<false, false>(w, q_epoch);
      }
      worker_states_[w].done_seq.store(next_seq, std::memory_order_release);
      ++next_seq;
    }
  }

  // Exact entry_best_first_v1 traversal order using persistent settled_epoch_.
  template <bool Instrument>
  P2Result search_single(const std::vector<float>& query, size_t k, size_t beam) {
    P2Result result;
    const uint16_t q_epoch = next_query_epoch();
    std::set<Hit> best, pending;

    if constexpr (Instrument) {
      result.counters.per_worker_expansions.assign(1, 0);
      result.counters.per_worker_distance_evaluations.assign(1, 0);
      result.counters.per_worker_idle_rounds.assign(1, 0);
    }

    auto discover = [&](Id node) {
      if (settled_epoch_[node] == q_epoch) {
        if constexpr (Instrument) ++result.counters.already_seen_attempts;
        return;
      }
      settled_epoch_[node] = q_epoch;
      const double distance = squared_l2(node, query);
      if constexpr (Instrument) {
        ++result.counters.distance_evaluations;
        ++result.counters.per_worker_distance_evaluations[0];
      }
      const Hit hit{distance, node};
      if (best.size() < beam || hit < *best.rbegin()) {
        best.insert(hit);
        pending.insert(hit);
        if constexpr (Instrument) ++result.counters.frontier_insertions;
        if (best.size() > beam) {
          const Hit worst = *best.rbegin();
          best.erase(worst);
          pending.erase(worst);
        }
      }
    };

    discover(graph_.entry);
    while (!pending.empty()) {
      const Id node = pending.begin()->second;
      pending.erase(pending.begin());
      if constexpr (Instrument) {
        ++result.counters.expansions;
        ++result.counters.per_worker_expansions[0];
      }
      const size_t edge_end = graph_.offsets[node + 1];
      for (size_t edge = graph_.offsets[node]; edge < edge_end; ++edge) {
        if constexpr (Instrument) ++result.counters.neighbor_attempts;
        discover(graph_.edges[edge]);
      }
    }

    if constexpr (Instrument) {
      result.counters.unique_distance_evaluations = result.counters.distance_evaluations;
      result.counters.unique_expansions = result.counters.expansions;
    }

    for (const Hit& hit : best) {
      if (result.hits.size() == k) break;
      result.hits.push_back(hit);
    }
    return result;
  }

  template <bool Instrument, bool FlatMerge, bool MarkAllEvaled, bool IncFrontier>
  P2Result search_multi(const std::vector<float>& query, size_t k, size_t beam) {
    static_assert(!IncFrontier || FlatMerge, "IncFrontier requires FlatMerge");
    P2Result result;
    const uint16_t q_epoch = next_query_epoch();
    uint32_t on_epoch = 0;
    if constexpr (Instrument) {
      on_epoch = next_on_epoch();
      result.counters.per_worker_expansions.assign(workers_, 0);
      result.counters.per_worker_distance_evaluations.assign(workers_, 0);
      result.counters.per_worker_idle_rounds.assign(workers_, 0);
    }

    if constexpr (IncFrontier) {
      global_best_flat_.clear();
      merge_scratch_.clear();
      if (global_best_flat_.capacity() < beam) global_best_flat_.reserve(beam);
      if (next_best_flat_.capacity() < beam) next_best_flat_.reserve(beam);
    } else if constexpr (FlatMerge) {
      global_best_vec_.clear();
      merge_scratch_.clear();
      if (global_best_vec_.capacity() < beam) global_best_vec_.reserve(beam);
      if (next_best_vec_.capacity() < beam) next_best_vec_.reserve(beam);
    } else {
      global_best_.clear();
    }
    global_has_full_beam_ = false;
    active_query_ = &query;
    active_beam_ = beam;
    active_instrument_ = Instrument;

    // Initial serial entry expansion on Worker 0 before Round 0.
    const Id entry = graph_.entry;
    settled_epoch_[entry] = q_epoch;
    global_expanded_epoch_[entry] = q_epoch;
    const Hit entry_hit{squared_l2(entry, query), entry};
    if constexpr (IncFrontier) {
      global_best_flat_.push_back(FlatEntry{entry_hit, 1});
    } else if constexpr (FlatMerge) {
      global_best_vec_.push_back(entry_hit);
    } else {
      global_best_.insert(entry_hit);
    }

    if constexpr (Instrument) {
      disc_seen_epoch_[entry] = on_epoch;
      exp_seen_epoch_[entry] = on_epoch;
      result.counters.distance_evaluations = 1;
      result.counters.unique_distance_evaluations = 1;
      result.counters.per_worker_distance_evaluations[0] = 1;
      result.counters.expansions = 1;
      result.counters.unique_expansions = 1;
      result.counters.per_worker_expansions[0] = 1;
      result.counters.frontier_insertions = 1;
    }

    const size_t entry_end = graph_.offsets[entry + 1];
    for (size_t edge = graph_.offsets[entry]; edge < entry_end; ++edge) {
      if constexpr (Instrument) ++result.counters.neighbor_attempts;
      const Id nbr = graph_.edges[edge];
      if (settled_epoch_[nbr] == q_epoch) {
        if constexpr (Instrument) ++result.counters.already_seen_attempts;
        continue;
      }
      settled_epoch_[nbr] = q_epoch;
      const double distance = squared_l2(nbr, query);
      if constexpr (Instrument) {
        disc_seen_epoch_[nbr] = on_epoch;
        ++result.counters.distance_evaluations;
        ++result.counters.unique_distance_evaluations;
        ++result.counters.per_worker_distance_evaluations[0];
      }
      const Hit hit{distance, nbr};
      if constexpr (IncFrontier) {
        if (global_best_flat_.size() < beam || hit < global_best_flat_.back().hit) {
          auto pos = std::lower_bound(
              global_best_flat_.begin(), global_best_flat_.end(), hit,
              [](const FlatEntry& e, const Hit& h) { return e.hit < h; });
          global_best_flat_.insert(pos, FlatEntry{hit, 0});
          if constexpr (Instrument) ++result.counters.frontier_insertions;
          if (global_best_flat_.size() > beam) {
            global_best_flat_.pop_back();
          }
        }
      } else if constexpr (FlatMerge) {
        if (global_best_vec_.size() < beam || hit < global_best_vec_.back()) {
          auto pos = std::lower_bound(global_best_vec_.begin(), global_best_vec_.end(), hit);
          global_best_vec_.insert(pos, hit);
          if constexpr (Instrument) ++result.counters.frontier_insertions;
          if (global_best_vec_.size() > beam) {
            global_best_vec_.pop_back();
          }
        }
      } else {
        if (global_best_.size() < beam || hit < *global_best_.rbegin()) {
          global_best_.insert(hit);
          if constexpr (Instrument) ++result.counters.frontier_insertions;
          if (global_best_.size() > beam) {
            global_best_.erase(std::prev(global_best_.end()));
          }
        }
      }
    }

    const size_t max_dispatch = workers_ * sync_interval_;
    size_t dispatched = 0;
    size_t first_unexp = 0;
    size_t prev_last_disp = 0;

    if constexpr (IncFrontier) {
      for (size_t w = 0; w < workers_; ++w) {
        worker_states_[w].init_seeds.clear();
      }
      first_unexp = global_best_flat_.size();
      for (size_t i = 0; i < global_best_flat_.size(); ++i) {
        if (global_best_flat_[i].expanded == 0) {
          if (first_unexp == global_best_flat_.size()) first_unexp = i;
          worker_states_[dispatched % workers_].init_seeds.push_back(global_best_flat_[i].hit);
          ++dispatched;
          prev_last_disp = i;
          if (dispatched == max_dispatch) break;
        }
      }
    } else {
      active_frontier_.clear();
      if constexpr (FlatMerge) {
        for (const Hit& hit : global_best_vec_) {
          if (global_expanded_epoch_[hit.second] != q_epoch) {
            active_frontier_.push_back(hit);
          }
        }
      } else {
        for (const Hit& hit : global_best_) {
          if (global_expanded_epoch_[hit.second] != q_epoch) {
            active_frontier_.push_back(hit);
          }
        }
      }
    }

    while (IncFrontier ? (dispatched > 0) : !active_frontier_.empty()) {
      if constexpr (IncFrontier) {
        global_has_full_beam_ = (global_best_flat_.size() == beam);
        if (global_has_full_beam_) {
          global_worst_hit_ = global_best_flat_.back().hit;
        }
      } else if constexpr (FlatMerge) {
        global_has_full_beam_ = (global_best_vec_.size() == beam);
        if (global_has_full_beam_) {
          global_worst_hit_ = global_best_vec_.back();
        }
      } else {
        global_has_full_beam_ = (global_best_.size() == beam);
        if (global_has_full_beam_) {
          global_worst_hit_ = *global_best_.rbegin();
        }
      }

      if constexpr (!IncFrontier) {
        for (size_t w = 0; w < workers_; ++w) {
          worker_states_[w].init_seeds.clear();
        }
        for (size_t i = 0; i < active_frontier_.size(); ++i) {
          worker_states_[i % workers_].init_seeds.push_back(active_frontier_[i]);
        }
      }

      const uint64_t next_seq = ++round_seq_;
#ifdef TASK_DA_ROUND_TRACE
      // At most 128 records, conservatively <64KiB owned payload/capacity each.
      // Only worker-private append buffers are written while workers run.
      trace_active_ = trace_enabled_ && result.rounds.size() < 128;
      if (trace_enabled_ && !trace_active_) result.trace_overflow = true;
      if (trace_active_) {
        const auto before = detail::now_ns();
        result.rounds.emplace_back();
        auto& tr = result.rounds.back();
        tr.prepare_ns = before;
        tr.seeds.reserve(32);
        for (size_t w = 0; w < workers_; ++w) {
          for (size_t i = 0; i < worker_states_[w].init_seeds.size(); ++i) {
            const auto& hit = worker_states_[w].init_seeds[i];
            const auto node = hit.second;
            const auto degree = graph_.offsets[node+1] - graph_.offsets[node];
            TraceSeed seed{node, static_cast<uint32_t>(w), static_cast<uint32_t>(i*2+w),
                           static_cast<uint32_t>(degree), hit.first, {}};
            seed.eligible.reserve(degree);
            for (size_t e = graph_.offsets[node]; e < graph_.offsets[node+1]; ++e)
              if (settled_epoch_[graph_.edges[e]] != q_epoch) seed.eligible.push_back(graph_.edges[e]);
            tr.seeds.push_back(std::move(seed));
          }
        }
        tr.snapshot_ns = detail::now_ns() - before;
      }
#endif
      uint64_t t_dispatch = 0;
      if constexpr (Instrument) t_dispatch = detail::now_ns();
#ifdef TASK_DA_ROUND_TRACE
      if (trace_active_) result.rounds.back().release_ns = t_dispatch;
#endif
      work_seq_.store(next_seq, std::memory_order_release);

      run_worker_round<Instrument, MarkAllEvaled>(0, q_epoch);

      for (size_t w = 1; w < workers_; ++w) {
        uint32_t spins = 0;
        while (worker_states_[w].done_seq.load(std::memory_order_acquire) < next_seq) {
          if (spins < 2048) {
            ++spins;
            detail::cpu_relax();
          } else {
            std::this_thread::yield();
          }
        }
      }

      uint64_t t_all_arrived = 0;
      if constexpr (Instrument) t_all_arrived = detail::now_ns();
#ifdef TASK_DA_ROUND_TRACE
      if (trace_active_) {
        auto& tr = result.rounds.back();
        tr.arrived_ns = t_all_arrived;
        for (size_t w = 0; w < 2; ++w) tr.workers[w] = worker_states_[w].trace;
        tr.copy_ns = detail::now_ns() - t_all_arrived;
      }
#endif

      // Single-writer merge phase while helpers remain parked on work_seq_ == next_seq.
      for (size_t w = 0; w < workers_; ++w) {
        detail::WorkerState& ws = worker_states_[w];
        if constexpr (Instrument) {
          if (ws.was_idle) {
            ++result.counters.per_worker_idle_rounds[w];
            if (t_all_arrived > t_dispatch) {
              result.counters.worker_idle_ns += (t_all_arrived - t_dispatch);
            }
            continue;
          }
          result.counters.per_worker_distance_evaluations[w] += ws.round_dist_evals;
          result.counters.per_worker_expansions[w] += ws.round_expansions;
          result.counters.distance_evaluations += ws.round_dist_evals;
          result.counters.expansions += ws.round_expansions;
          result.counters.neighbor_attempts += ws.round_neighbor_attempts;
          result.counters.already_seen_attempts += ws.round_already_seen;
          result.counters.frontier_insertions += ws.round_frontier_insertions;
          for (Id id : ws.local_newly_evaled) {
            if (disc_seen_epoch_[id] != on_epoch) {
              disc_seen_epoch_[id] = on_epoch;
              ++result.counters.unique_distance_evaluations;
            } else {
              ++result.counters.duplicate_distance_evaluations;
            }
          }
        } else if (ws.was_idle) {
          continue;
        }

        if constexpr (MarkAllEvaled) {
          for (Id id : ws.local_newly_evaled) {
            settled_epoch_[id] = q_epoch;
          }
        }

        for (Id id : ws.local_expanded) {
          global_expanded_epoch_[id] = q_epoch;
          settled_epoch_[id] = q_epoch;
          if constexpr (Instrument) {
            if (exp_seen_epoch_[id] != on_epoch) {
              exp_seen_epoch_[id] = on_epoch;
              ++result.counters.unique_expansions;
            } else {
              ++result.counters.duplicate_expansions;
            }
          }
        }

        if constexpr (IncFrontier) {
          const bool has_full = (global_best_flat_.size() == beam);
          const Hit cur_worst = has_full ? global_best_flat_.back().hit : Hit{0.0, 0};
          for (const Hit& hit : ws.local_discovered) {
            if constexpr (!MarkAllEvaled) {
              settled_epoch_[hit.second] = q_epoch;
            }
            if (!has_full || hit < cur_worst) {
              merge_scratch_.push_back(hit);
            }
          }
        } else if constexpr (FlatMerge) {
          const bool has_full = (global_best_vec_.size() == beam);
          const Hit cur_worst = has_full ? global_best_vec_.back() : Hit{0.0, 0};
          for (const Hit& hit : ws.local_discovered) {
            if constexpr (!MarkAllEvaled) {
              settled_epoch_[hit.second] = q_epoch;
            }
            if (!has_full || hit < cur_worst) {
              merge_scratch_.push_back(hit);
            }
          }
        } else {
          for (const Hit& hit : ws.local_discovered) {
            if constexpr (!MarkAllEvaled) {
              settled_epoch_[hit.second] = q_epoch;
            }
            if (global_best_.size() < beam || hit < *global_best_.rbegin()) {
              global_best_.insert(hit);
              if (global_best_.size() > beam) {
                global_best_.erase(std::prev(global_best_.end()));
              }
            }
          }
        }
      }

      if constexpr (IncFrontier) {
        for (size_t w = 0; w < workers_; ++w) {
          worker_states_[w].init_seeds.clear();
        }
        dispatched = 0;
        size_t next_first_unexp = beam;
        size_t next_last_disp = 0;

        if (!merge_scratch_.empty()) {
          std::sort(merge_scratch_.begin(), merge_scratch_.end());
          merge_scratch_.erase(
              std::unique(merge_scratch_.begin(), merge_scratch_.end()),
              merge_scratch_.end());
          next_best_flat_.clear();
          size_t i = 0;
          size_t j = 0;
          const size_t n1 = global_best_flat_.size();
          const size_t n2 = merge_scratch_.size();
          while ((i < n1 || j < n2) && next_best_flat_.size() < beam) {
            FlatEntry entry_out;
            if (j >= n2 || (i < n1 && global_best_flat_[i].hit < merge_scratch_[j])) {
              entry_out = global_best_flat_[i];
              if (entry_out.expanded == 0 && i <= prev_last_disp &&
                  global_expanded_epoch_[entry_out.hit.second] == q_epoch) {
                entry_out.expanded = 1;
              }
              ++i;
            } else if (i >= n1 || merge_scratch_[j] < global_best_flat_[i].hit) {
              const Hit& h = merge_scratch_[j++];
              const uint8_t exp = (global_expanded_epoch_[h.second] == q_epoch) ? 1 : 0;
              entry_out = FlatEntry{h, exp};
            } else {
              entry_out = global_best_flat_[i];
              if (entry_out.expanded == 0 &&
                  global_expanded_epoch_[entry_out.hit.second] == q_epoch) {
                entry_out.expanded = 1;
              }
              ++i;
              ++j;
            }
            const size_t out_idx = next_best_flat_.size();
            next_best_flat_.push_back(entry_out);
            if (entry_out.expanded == 0) {
              if (next_first_unexp == beam) next_first_unexp = out_idx;
              if (dispatched < max_dispatch) {
                worker_states_[dispatched % workers_].init_seeds.push_back(entry_out.hit);
                ++dispatched;
                next_last_disp = out_idx;
              }
            }
          }
          global_best_flat_.swap(next_best_flat_);
          merge_scratch_.clear();
        } else {
          const size_t n1 = global_best_flat_.size();
          for (size_t i = first_unexp; i < n1; ++i) {
            FlatEntry& e = global_best_flat_[i];
            if (e.expanded == 0) {
              if (i <= prev_last_disp &&
                  global_expanded_epoch_[e.hit.second] == q_epoch) {
                e.expanded = 1;
                continue;
              }
              if (next_first_unexp == beam) next_first_unexp = i;
              if (dispatched < max_dispatch) {
                worker_states_[dispatched % workers_].init_seeds.push_back(e.hit);
                ++dispatched;
                next_last_disp = i;
              }
              if (dispatched == max_dispatch && i >= prev_last_disp) {
                break;
              }
            }
          }
        }
        first_unexp = (next_first_unexp == beam) ? global_best_flat_.size() : next_first_unexp;
        prev_last_disp = next_last_disp;
      } else if constexpr (FlatMerge) {
        if (!merge_scratch_.empty()) {
          std::sort(merge_scratch_.begin(), merge_scratch_.end());
          merge_scratch_.erase(
              std::unique(merge_scratch_.begin(), merge_scratch_.end()),
              merge_scratch_.end());
          next_best_vec_.clear();
          size_t i = 0;
          size_t j = 0;
          const size_t n1 = global_best_vec_.size();
          const size_t n2 = merge_scratch_.size();
          while ((i < n1 || j < n2) && next_best_vec_.size() < beam) {
            if (j >= n2 || (i < n1 && global_best_vec_[i] < merge_scratch_[j])) {
              next_best_vec_.push_back(global_best_vec_[i++]);
            } else if (i >= n1 || merge_scratch_[j] < global_best_vec_[i]) {
              next_best_vec_.push_back(merge_scratch_[j++]);
            } else {
              next_best_vec_.push_back(global_best_vec_[i++]);
              ++j;
            }
          }
          global_best_vec_.swap(next_best_vec_);
          merge_scratch_.clear();
        }
        active_frontier_.clear();
        for (const Hit& hit : global_best_vec_) {
          if (global_expanded_epoch_[hit.second] != q_epoch) {
            active_frontier_.push_back(hit);
          }
        }
      } else {
        active_frontier_.clear();
        for (const Hit& hit : global_best_) {
          if (global_expanded_epoch_[hit.second] != q_epoch) {
            active_frontier_.push_back(hit);
          }
        }
      }

      if constexpr (Instrument) {
        ++result.counters.sync_merge_count;
        const uint64_t t_merge_end = detail::now_ns();
        const uint64_t merge_ns = (t_merge_end > t_all_arrived) ? (t_merge_end - t_all_arrived) : 0;
        result.counters.merge_time_ns += merge_ns;
        uint64_t round_barrier_wait = 0;
        size_t active_helpers = 0;
        for (size_t w = 0; w < workers_; ++w) {
          if (worker_states_[w].was_idle) continue;
          if (w > 0) ++active_helpers;
          if (t_all_arrived > worker_states_[w].work_done_ns) {
            round_barrier_wait += (t_all_arrived - worker_states_[w].work_done_ns);
          }
        }
        result.counters.barrier_wait_ns += round_barrier_wait;
        result.counters.sync_wait_ns +=
            round_barrier_wait + static_cast<uint64_t>(active_helpers) * merge_ns;
      }
#ifdef TASK_DA_ROUND_TRACE
      if (trace_active_) result.rounds.back().end_ns = detail::now_ns();
#endif
    }

    if constexpr (IncFrontier) {
      for (const FlatEntry& e : global_best_flat_) {
        if (result.hits.size() == k) break;
        result.hits.push_back(e.hit);
      }
    } else if constexpr (FlatMerge) {
      for (const Hit& hit : global_best_vec_) {
        if (result.hits.size() == k) break;
        result.hits.push_back(hit);
      }
    } else {
      for (const Hit& hit : global_best_) {
        if (result.hits.size() == k) break;
        result.hits.push_back(hit);
      }
    }
    return result;
  }
};

}  // namespace task_da
