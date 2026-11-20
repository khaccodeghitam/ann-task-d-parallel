// SPDX-License-Identifier: MIT
// P2 multi-walker exploratory evaluator (workers in {1, 2, 4}, strict jobs == 1).

#include "p2_engine.hpp"

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace fs = std::filesystem;

namespace {

std::vector<size_t> parse_size_list(const std::string& raw) {
  std::vector<size_t> out;
  std::stringstream ss(raw);
  std::string item;
  while (std::getline(ss, item, ',')) {
    if (item.empty()) throw std::invalid_argument("empty integer list entry");
    size_t idx = 0;
    const unsigned long long val = std::stoull(item, &idx);
    if (idx != item.size() || !val) throw std::invalid_argument("invalid positive integer: " + item);
    out.push_back(static_cast<size_t>(val));
  }
  if (out.empty()) throw std::invalid_argument("empty integer list");
  return out;
}

std::vector<int> parse_cpu_list(const std::string& raw) {
  std::vector<int> out;
  if (raw.empty()) return out;
  std::stringstream ss(raw);
  std::string item;
  while (std::getline(ss, item, ',')) {
    if (item.empty()) throw std::invalid_argument("empty cpu id");
    size_t idx = 0;
    const long val = std::stol(item, &idx);
    if (idx != item.size() || val < 0 || val >= 1024) {
      throw std::invalid_argument("invalid cpu id: " + item);
    }
    out.push_back(static_cast<int>(val));
  }
  return out;
}

std::vector<size_t> load_ids_file(const std::string& path, size_t limit) {
  std::ifstream in(path);
  if (!in) throw std::invalid_argument("cannot open id list: " + path);
  std::vector<size_t> ids;
  std::string line;
  while (std::getline(in, line)) {
    const auto first = line.find_first_not_of(" \t\r\n");
    if (first == std::string::npos) continue;
    const auto last = line.find_last_not_of(" \t\r\n");
    const std::string token = line.substr(first, last - first + 1);
    if (!token.empty() && token[0] == '#') continue;
    size_t idx = 0;
    const unsigned long long id = std::stoull(token, &idx);
    if (idx != token.size() || id >= limit) {
      throw std::invalid_argument("query id out of range: " + token);
    }
    ids.push_back(static_cast<size_t>(id));
  }
  if (ids.empty()) throw std::invalid_argument("empty id list: " + path);
  return ids;
}

std::string json_escape(const std::string& s) {
  std::string out;
  out.reserve(s.size() + 8);
  for (unsigned char c : s) {
    if (c == '"') out += "\\\"";
    else if (c == '\\') out += "\\\\";
    else if (c == '\n') out += "\\n";
    else if (c == '\r') out += "\\r";
    else if (c == '\t') out += "\\t";
    else out.push_back(static_cast<char>(c));
  }
  return out;
}

template <typename T>
void write_json_array(std::ostream& os, const std::vector<T>& vals) {
  os << '[';
  for (size_t i = 0; i < vals.size(); ++i) {
    if (i) os << ',';
    os << vals[i];
  }
  os << ']';
}

long long read_vm_hwm_kib() {
#ifdef __linux__
  std::ifstream status("/proc/self/status");
  std::string line;
  while (std::getline(status, line)) {
    if (line.rfind("VmHWM:", 0) == 0) {
      std::stringstream ss(line.substr(6));
      long long kib = -1;
      ss >> kib;
      return kib;
    }
  }
#endif
  return -1;
}

double percentile_us(const std::vector<uint64_t>& sorted_ns, double q) {
  if (sorted_ns.empty()) return 0.0;
  const double pos = q * static_cast<double>(sorted_ns.size() - 1);
  const size_t lo = static_cast<size_t>(pos);
  const size_t hi = std::min(lo + 1, sorted_ns.size() - 1);
  const double frac = pos - static_cast<double>(lo);
  const double ns = static_cast<double>(sorted_ns[lo]) * (1.0 - frac) +
                    static_cast<double>(sorted_ns[hi]) * frac;
  return ns * 1e-3;
}

struct Options {
  std::string format;
  std::string graph_path;
  std::string base_path;
  std::string query_path;
  std::string out_dir;
  std::string query_ids_path;
  std::string warmup_ids_path;
  std::string mode;
  std::string merge_impl = "set";
  std::string visited_policy = "baseline";
  std::string frontier_mode = "full";
  std::vector<size_t> beams;
  std::vector<int> cpu_list;
  task_da::Id entry = 0;
  size_t k = 10;
  size_t workers = 1;
  size_t sync_interval = 8;
  size_t max_beam = 4096;
  size_t jobs = 1;
  bool round_trace = false;
};

Options parse_args(int argc, char** argv) {
  if (argc < 5) {
    throw std::invalid_argument(
        "usage: task_da_p2_eval <pipnn|nsg> <graph> <base.fbin> <query.fbin> "
        "--beams <b1,b2> --mode <ON|OFF> --out-dir <dir> "
        "[--workers 1|2|4] [--sync-interval 8] [--merge-impl set|flat] "
        "[--visited-policy baseline|barrier_all_evaled] [--frontier-mode full|incremental] "
        "[--k 10] [--entry 0] [--query-ids file] [--warmup-ids file] [--cpu-list c0,...] "
        "[--max-beam 4096] [--jobs 1]");
  }
  Options opt;
  opt.format = argv[1];
  opt.graph_path = argv[2];
  opt.base_path = argv[3];
  opt.query_path = argv[4];

  for (int i = 5; i < argc; ++i) {
    const std::string flag = argv[i];
    auto need = [&](const std::string& name) -> std::string {
      if (i + 1 >= argc) throw std::invalid_argument("missing value for " + name);
      return argv[++i];
    };
    if (flag == "--round-trace") {
#ifdef TASK_DA_ROUND_TRACE
      opt.round_trace = true;
#else
      throw std::invalid_argument("round trace not compiled into this binary");
#endif
    } else if (flag == "--beams") {
      opt.beams = parse_size_list(need(flag));
    } else if (flag == "--mode") {
      opt.mode = need(flag);
    } else if (flag == "--out-dir") {
      opt.out_dir = need(flag);
    } else if (flag == "--query-ids") {
      opt.query_ids_path = need(flag);
    } else if (flag == "--warmup-ids") {
      opt.warmup_ids_path = need(flag);
    } else if (flag == "--cpu-list") {
      opt.cpu_list = parse_cpu_list(need(flag));
    } else if (flag == "--entry") {
      opt.entry = static_cast<task_da::Id>(std::stoull(need(flag)));
    } else if (flag == "--k") {
      opt.k = std::stoull(need(flag));
    } else if (flag == "--workers") {
      opt.workers = std::stoull(need(flag));
    } else if (flag == "--sync-interval") {
      opt.sync_interval = std::stoull(need(flag));
    } else if (flag == "--merge-impl") {
      opt.merge_impl = need(flag);
    } else if (flag == "--visited-policy") {
      opt.visited_policy = need(flag);
    } else if (flag == "--frontier-mode") {
      opt.frontier_mode = need(flag);
    } else if (flag == "--max-beam") {
      opt.max_beam = std::stoull(need(flag));
    } else if (flag == "--jobs") {
      opt.jobs = std::stoull(need(flag));
    } else {
      throw std::invalid_argument("unknown argument: " + flag);
    }
  }

  if (opt.mode != "ON" && opt.mode != "OFF") throw std::invalid_argument("--mode must be ON or OFF");
  if (opt.round_trace && opt.mode != "ON") throw std::invalid_argument("trace requires ON");
  if (opt.merge_impl != "set" && opt.merge_impl != "flat") {
    throw std::invalid_argument("--merge-impl must be set or flat");
  }
  if (opt.visited_policy != "baseline" && opt.visited_policy != "barrier_all_evaled") {
    throw std::invalid_argument("--visited-policy must be baseline or barrier_all_evaled");
  }
  if (opt.frontier_mode != "full" && opt.frontier_mode != "incremental") {
    throw std::invalid_argument("--frontier-mode must be full or incremental");
  }
  if (opt.frontier_mode == "incremental" && opt.merge_impl != "flat") {
    throw std::invalid_argument("--frontier-mode incremental requires --merge-impl flat");
  }
  if (opt.out_dir.empty()) throw std::invalid_argument("--out-dir required");
  if (opt.beams.empty()) throw std::invalid_argument("--beams required");
  if (opt.jobs != 1) {
    throw std::invalid_argument("p2_eval enforces inter-query --jobs 1; use --workers for P2");
  }
  if (opt.workers != 1 && opt.workers != 2 && opt.workers != 4) {
    throw std::invalid_argument("--workers must be 1, 2, or 4");
  }
  if (!opt.cpu_list.empty() && opt.cpu_list.size() != opt.workers) {
    throw std::invalid_argument("--cpu-list length must equal --workers");
  }
  for (size_t b : opt.beams) {
    if (b < opt.k || b > opt.max_beam) {
      throw std::invalid_argument("beam violates k <= beam <= max_beam");
    }
  }
  return opt;
}

template <bool Instrument>
struct BeamRunOutput {
  size_t beam = 0;
  uint64_t batch_wall_ns = 0;
  uint64_t sum_latency_ns = 0;
  std::vector<uint64_t> latencies_ns;
  std::vector<task_da::P2Result> results;
};

template <bool Instrument>
BeamRunOutput<Instrument> execute_beam(
    task_da::P2SearchSession& session,
    const std::vector<std::vector<float>>& queries,
    const std::vector<size_t>& warmup_ids,
    const std::vector<size_t>& query_ids,
    size_t k,
    size_t beam,
    bool round_trace) {
#ifndef TASK_DA_ROUND_TRACE
  (void)round_trace;
#endif
  BeamRunOutput<Instrument> out;
  out.beam = beam;
  out.latencies_ns.resize(query_ids.size(), 0);
  out.results.resize(query_ids.size());

  for (size_t wid : warmup_ids) {
    volatile size_t sink = session.search<Instrument>(queries[wid], k, beam).hits.size();
    (void)sink;
  }

  const uint64_t t_batch_start = task_da::detail::now_ns();
#ifdef TASK_DA_ROUND_TRACE
  session.enable_round_trace(round_trace);
#endif
  for (size_t i = 0; i < query_ids.size(); ++i) {
    const size_t qid = query_ids[i];
    const uint64_t t0 = task_da::detail::now_ns();
    out.results[i] = session.search<Instrument>(queries[qid], k, beam);
    const uint64_t t1 = task_da::detail::now_ns();
    const uint64_t dt = (t1 >= t0) ? (t1 - t0) : 0;
    out.latencies_ns[i] = dt;
    out.sum_latency_ns += dt;
  }
  const uint64_t t_batch_end = task_da::detail::now_ns();
  out.batch_wall_ns = (t_batch_end >= t_batch_start) ? (t_batch_end - t_batch_start) : 0;
#ifdef TASK_DA_ROUND_TRACE
  session.enable_round_trace(false);
#endif
  return out;
}

}  // namespace

int main(int argc, char** argv) {
  try {
    const Options opt = parse_args(argc, argv);
    const task_da::Vectors base = task_da::load_fbin(opt.base_path);
    const task_da::Graph graph = task_da::load_graph(
        opt.graph_path, opt.format, static_cast<task_da::Id>(base.n), opt.entry);
    const task_da::Vectors query_vecs = task_da::load_fbin(opt.query_path);
    if (query_vecs.dim != base.dim) {
      throw std::invalid_argument("query/base dim mismatch");
    }

    std::vector<std::vector<float>> queries(query_vecs.n, std::vector<float>(query_vecs.dim));
    for (size_t i = 0; i < query_vecs.n; ++i) {
      for (size_t d = 0; d < query_vecs.dim; ++d) {
        queries[i][d] = query_vecs.values[i * query_vecs.dim + d];
      }
    }

    std::vector<size_t> query_ids;
    if (!opt.query_ids_path.empty()) {
      query_ids = load_ids_file(opt.query_ids_path, query_vecs.n);
    } else {
      query_ids.resize(query_vecs.n);
      std::iota(query_ids.begin(), query_ids.end(), 0);
    }

    std::vector<size_t> warmup_ids;
    if (!opt.warmup_ids_path.empty()) {
      warmup_ids = load_ids_file(opt.warmup_ids_path, query_vecs.n);
    }

    fs::create_directories(opt.out_dir);
    for (size_t beam : opt.beams) {
      const fs::path out_file =
          fs::path(opt.out_dir) /
          ("beam_" + std::to_string(beam) + "_p" + std::to_string(opt.workers) + "_" + opt.mode + ".jsonl");
      if (fs::exists(out_file)) {
        throw std::runtime_error("refusing overwrite of existing result file: " + out_file.string());
      }
    }
    const fs::path summary_file = fs::path(opt.out_dir) / "p2_eval_summary.json";
    if (fs::exists(summary_file)) {
      throw std::runtime_error("refusing overwrite of existing summary file: " + summary_file.string());
    }

    const bool instrument = (opt.mode == "ON");
    std::vector<int> observed_cpus;
    std::vector<std::string> beam_summaries;

    {
      const task_da::MergeImpl merge_impl =
          (opt.merge_impl == "flat") ? task_da::MergeImpl::kFlat : task_da::MergeImpl::kSet;
      const task_da::VisitedPolicy visited_policy =
          (opt.visited_policy == "barrier_all_evaled") ? task_da::VisitedPolicy::kBarrierAllEvaled
                                                       : task_da::VisitedPolicy::kBaseline;
      const task_da::FrontierMode frontier_mode =
          (opt.frontier_mode == "incremental") ? task_da::FrontierMode::kIncremental
                                               : task_da::FrontierMode::kFull;
      task_da::P2SearchSession session(graph, base, opt.workers, opt.sync_interval, opt.cpu_list,
                                       merge_impl, visited_policy, frontier_mode);
      observed_cpus = session.observed_cpus();

      auto write_beam_outputs = [&](auto&& run_out) {
        const fs::path out_file =
            fs::path(opt.out_dir) /
            ("beam_" + std::to_string(run_out.beam) + "_p" + std::to_string(opt.workers) + "_" +
             opt.mode + ".jsonl");
        std::ofstream os(out_file);
        if (!os) throw std::runtime_error("cannot write output file: " + out_file.string());
        os << std::setprecision(17);

        size_t complete_top_k_count = 0;
        uint64_t sum_dist = 0, sum_uniq_dist = 0, sum_dup_dist = 0;
        uint64_t sum_exp = 0, sum_uniq_exp = 0, sum_dup_exp = 0;
        uint64_t sum_nbr = 0, sum_seen = 0, sum_ins = 0;
        uint64_t sum_merge = 0, sum_sync_ns = 0, sum_barrier_ns = 0, sum_merge_ns = 0, sum_idle_ns = 0;
        std::vector<uint64_t> sum_pw_exp(opt.workers, 0);
        std::vector<uint64_t> sum_pw_dist(opt.workers, 0);
        std::vector<uint64_t> sum_pw_idle_rounds(opt.workers, 0);

        for (size_t i = 0; i < query_ids.size(); ++i) {
          const auto& res = run_out.results[i];
          const bool complete = (res.hits.size() == opt.k);
          if (complete) ++complete_top_k_count;

          os << "{\"scope\":\"task_d_a_common_p2_exploratory\""
             << ",\"graph_format\":\"" << opt.format << "\""
             << ",\"entry\":" << opt.entry
             << ",\"k\":" << opt.k
             << ",\"beam\":" << run_out.beam
             << ",\"workers\":" << opt.workers
             << ",\"sync_interval\":" << opt.sync_interval
             << ",\"merge_impl\":\"" << opt.merge_impl << "\""
             << ",\"visited_policy\":\"" << opt.visited_policy << "\""
             << ",\"frontier_mode\":\"" << opt.frontier_mode << "\""
             << ",\"jobs\":1"
             << ",\"mode\":\"" << opt.mode << "\""
             << ",\"instrumentation\":" << (instrument ? "true" : "false")
             << ",\"query_id\":" << query_ids[i]
             << ",\"complete_top_k\":" << (complete ? "true" : "false")
             << ",\"latency_ns\":" << run_out.latencies_ns[i]
             << ",\"ids\":[";
          for (size_t j = 0; j < res.hits.size(); ++j) {
            if (j) os << ',';
            os << res.hits[j].second;
          }
          os << "],\"squared_l2\":[";
          for (size_t j = 0; j < res.hits.size(); ++j) {
            if (j) os << ',';
            os << res.hits[j].first;
          }
          os << ']';

          if (instrument) {
            const auto& c = res.counters;
            sum_dist += c.distance_evaluations;
            sum_uniq_dist += c.unique_distance_evaluations;
            sum_dup_dist += c.duplicate_distance_evaluations;
            sum_exp += c.expansions;
            sum_uniq_exp += c.unique_expansions;
            sum_dup_exp += c.duplicate_expansions;
            sum_nbr += c.neighbor_attempts;
            sum_seen += c.already_seen_attempts;
            sum_ins += c.frontier_insertions;
            sum_merge += c.sync_merge_count;
            sum_sync_ns += c.sync_wait_ns;
            sum_barrier_ns += c.barrier_wait_ns;
            sum_merge_ns += c.merge_time_ns;
            sum_idle_ns += c.worker_idle_ns;
            for (size_t w = 0; w < opt.workers; ++w) {
              sum_pw_exp[w] += c.per_worker_expansions[w];
              sum_pw_dist[w] += c.per_worker_distance_evaluations[w];
              sum_pw_idle_rounds[w] += c.per_worker_idle_rounds[w];
            }

            os << ",\"counters\":{"
               << "\"distance_evaluations\":" << c.distance_evaluations
               << ",\"unique_distance_evaluations\":" << c.unique_distance_evaluations
               << ",\"duplicate_distance_evaluations\":" << c.duplicate_distance_evaluations
               << ",\"expansions\":" << c.expansions
               << ",\"unique_expansions\":" << c.unique_expansions
               << ",\"duplicate_expansions\":" << c.duplicate_expansions
               << ",\"neighbor_attempts\":" << c.neighbor_attempts
               << ",\"already_seen_attempts\":" << c.already_seen_attempts
               << ",\"frontier_insertions\":" << c.frontier_insertions
               << ",\"sync_merge_count\":" << c.sync_merge_count
               << ",\"sync_wait_ns\":" << c.sync_wait_ns
               << ",\"barrier_wait_ns\":" << c.barrier_wait_ns
               << ",\"merge_time_ns\":" << c.merge_time_ns
               << ",\"worker_idle_ns\":" << c.worker_idle_ns
               << ",\"per_worker_expansions\":";
            write_json_array(os, c.per_worker_expansions);
            os << ",\"per_worker_distance_evaluations\":";
            write_json_array(os, c.per_worker_distance_evaluations);
            os << ",\"per_worker_idle_rounds\":";
            write_json_array(os, c.per_worker_idle_rounds);
            os << '}';
          }
#ifdef TASK_DA_ROUND_TRACE
          if (opt.round_trace) task_da::write_round_trace(os, res.rounds, res.trace_overflow);
#endif
          os << "}\n";
        }

        std::vector<uint64_t> sorted_ns = run_out.latencies_ns;
        std::sort(sorted_ns.begin(), sorted_ns.end());
        const double mean_us =
            query_ids.empty() ? 0.0
                              : (static_cast<double>(run_out.sum_latency_ns) * 1e-3 /
                                 static_cast<double>(query_ids.size()));
        const double qps_wall =
            run_out.batch_wall_ns == 0
                ? 0.0
                : (static_cast<double>(query_ids.size()) /
                   (static_cast<double>(run_out.batch_wall_ns) * 1e-9));

        std::ostringstream bss;
        bss << std::setprecision(10)
            << "{\"beam\":" << run_out.beam
            << ",\"result_file\":\"" << json_escape(out_file.string()) << "\""
            << ",\"queries\":" << query_ids.size()
            << ",\"complete_top_k_count\":" << complete_top_k_count
            << ",\"batch_wall_ns\":" << run_out.batch_wall_ns
            << ",\"sum_latency_ns\":" << run_out.sum_latency_ns
            << ",\"qps_wall\":" << qps_wall
            << ",\"latency_us\":{"
            << "\"min\":" << (sorted_ns.empty() ? 0.0 : static_cast<double>(sorted_ns.front()) * 1e-3)
            << ",\"mean\":" << mean_us
            << ",\"p50\":" << percentile_us(sorted_ns, 0.50)
            << ",\"p95\":" << percentile_us(sorted_ns, 0.95)
            << ",\"p99\":" << percentile_us(sorted_ns, 0.99)
            << ",\"max\":" << (sorted_ns.empty() ? 0.0 : static_cast<double>(sorted_ns.back()) * 1e-3)
            << '}';
        if (instrument) {
          bss << ",\"counters_total\":{"
              << "\"distance_evaluations\":" << sum_dist
              << ",\"unique_distance_evaluations\":" << sum_uniq_dist
              << ",\"duplicate_distance_evaluations\":" << sum_dup_dist
              << ",\"expansions\":" << sum_exp
              << ",\"unique_expansions\":" << sum_uniq_exp
              << ",\"duplicate_expansions\":" << sum_dup_exp
              << ",\"neighbor_attempts\":" << sum_nbr
              << ",\"already_seen_attempts\":" << sum_seen
              << ",\"frontier_insertions\":" << sum_ins
              << ",\"sync_merge_count\":" << sum_merge
              << ",\"sync_wait_ns\":" << sum_sync_ns
              << ",\"barrier_wait_ns\":" << sum_barrier_ns
              << ",\"merge_time_ns\":" << sum_merge_ns
              << ",\"worker_idle_ns\":" << sum_idle_ns
              << ",\"per_worker_expansions\":";
          write_json_array(bss, sum_pw_exp);
          bss << ",\"per_worker_distance_evaluations\":";
          write_json_array(bss, sum_pw_dist);
          bss << ",\"per_worker_idle_rounds\":";
          write_json_array(bss, sum_pw_idle_rounds);
          bss << '}';
        }
        bss << '}';
        beam_summaries.push_back(bss.str());
      };

      if (instrument) {
        std::vector<BeamRunOutput<true>> beam_runs;
        beam_runs.reserve(opt.beams.size());
        for (size_t beam : opt.beams) {
          beam_runs.push_back(execute_beam<true>(session, queries, warmup_ids, query_ids, opt.k, beam, opt.round_trace));
        }
        session.stop_threads();
        for (const auto& r : beam_runs) write_beam_outputs(r);
      } else {
        std::vector<BeamRunOutput<false>> beam_runs;
        beam_runs.reserve(opt.beams.size());
        for (size_t beam : opt.beams) {
          beam_runs.push_back(execute_beam<false>(session, queries, warmup_ids, query_ids, opt.k, beam, opt.round_trace));
        }
        session.stop_threads();
        for (const auto& r : beam_runs) write_beam_outputs(r);
      }
    }

    const long long vm_hwm_kib = read_vm_hwm_kib();
    std::ostringstream meta;
    meta << std::setprecision(10)
         << "{\"scope\":\"task_d_a_common_p2_exploratory\""
         << ",\"graph_path\":\"" << json_escape(opt.graph_path) << "\""
         << ",\"base_path\":\"" << json_escape(opt.base_path) << "\""
         << ",\"query_path\":\"" << json_escape(opt.query_path) << "\""
         << ",\"graph_format\":\"" << opt.format << "\""
         << ",\"entry\":" << opt.entry
         << ",\"k\":" << opt.k
         << ",\"workers\":" << opt.workers
         << ",\"sync_interval\":" << opt.sync_interval
         << ",\"merge_impl\":\"" << opt.merge_impl << "\""
         << ",\"visited_policy\":\"" << opt.visited_policy << "\""
         << ",\"frontier_mode\":\"" << opt.frontier_mode << "\""
         << ",\"jobs\":1"
         << ",\"mode\":\"" << opt.mode << "\""
         << ",\"warmup_count\":" << warmup_ids.size()
         << ",\"query_count\":" << query_ids.size()
         << ",\"requested_cpus\":";
    write_json_array(meta, opt.cpu_list);
    meta << ",\"observed_cpus\":";
    write_json_array(meta, observed_cpus);
    meta << ",\"vm_hwm_kib\":" << vm_hwm_kib
         << ",\"runs\":[";
    for (size_t i = 0; i < beam_summaries.size(); ++i) {
      if (i) meta << ',';
      meta << beam_summaries[i];
    }
    meta << "]}\n";

    std::ofstream sum_os(summary_file);
    if (!sum_os) throw std::runtime_error("cannot write summary file: " + summary_file.string());
    sum_os << meta.str();
    std::cout << meta.str();
    return 0;
  } catch (const std::exception& exc) {
    std::cerr << "error: " << exc.what() << "\n";
    return 1;
  }
}
