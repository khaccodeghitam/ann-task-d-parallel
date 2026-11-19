// SPDX-License-Identifier: MIT
#include "engine.hpp"
#include <atomic>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

namespace {

uint32_t parse_u32(const std::string& value) {
  if (value.empty() || value.find_first_not_of("0123456789") != std::string::npos)
    throw std::invalid_argument("expected unsigned integer");
  const auto parsed = std::stoull(value);
  if (parsed > UINT32_MAX) throw std::invalid_argument("integer out of range");
  return static_cast<uint32_t>(parsed);
}

std::vector<uint32_t> parse_beams(const std::string& csv, uint32_t k, size_t n, uint32_t max_beam) {
  std::vector<uint32_t> beams;
  std::set<uint32_t> seen;
  std::stringstream ss(csv);
  std::string piece;
  while (std::getline(ss, piece, ',')) {
    if (piece.empty()) throw std::invalid_argument("empty beam");
    const uint32_t beam = parse_u32(piece);
    if (beam < k || beam > n || beam > max_beam || !seen.insert(beam).second)
      throw std::invalid_argument("invalid/duplicate beam or exceeds cap");
    beams.push_back(beam);
  }
  if (beams.empty()) throw std::invalid_argument("no beams specified");
  return beams;
}

std::vector<uint32_t> load_query_ids(const std::string& path, size_t query_count) {
  std::ifstream in(path);
  if (!in) throw std::invalid_argument("cannot open query-ids file");
  std::vector<uint32_t> ids;
  std::vector<uint8_t> seen(query_count, 0);
  std::string token;
  while (in >> token) {
    const uint32_t qid = parse_u32(token);
    if (qid >= query_count) throw std::invalid_argument("query_id out of range");
    if (seen[qid]) throw std::invalid_argument("duplicate query_id");
    seen[qid] = 1;
    ids.push_back(qid);
  }
  if (ids.empty()) throw std::invalid_argument("empty query-ids file");
  return ids;
}

std::vector<task_da::Result> evaluate_queries(const task_da::Index& index,
                                              const task_da::Vectors& queries,
                                              const std::vector<uint32_t>& qids,
                                              uint32_t k,
                                              uint32_t beam,
                                              bool instrument,
                                              uint32_t jobs) {
  const size_t total = qids.size();
  std::vector<task_da::Result> results(total);
  const size_t worker_count = std::min<size_t>(jobs, total);
  if (worker_count <= 1) {
    std::vector<float> query(queries.dim);
    for (size_t idx = 0; idx < total; ++idx) {
      const size_t q = qids[idx];
      std::copy(queries.values.begin() + q * queries.dim,
                queries.values.begin() + (q + 1) * queries.dim,
                query.begin());
      results[idx] = instrument ? index.search<true>(query, k, beam)
                                : index.search<false>(query, k, beam);
    }
    return results;
  }

  std::atomic<size_t> next_idx{0};
  std::vector<std::thread> pool;
  pool.reserve(worker_count);
  for (size_t t = 0; t < worker_count; ++t) {
    pool.emplace_back([&]() {
      std::vector<float> query(queries.dim);
      for (;;) {
        const size_t idx = next_idx.fetch_add(1, std::memory_order_relaxed);
        if (idx >= total) break;
        const size_t q = qids[idx];
        std::copy(queries.values.begin() + q * queries.dim,
                  queries.values.begin() + (q + 1) * queries.dim,
                  query.begin());
        results[idx] = instrument ? index.search<true>(query, k, beam)
                                  : index.search<false>(query, k, beam);
      }
    });
  }
  for (auto& th : pool) th.join();
  return results;
}

}  // namespace

int main(int argc, char** argv) {
  try {
    if (argc < 5) {
      throw std::invalid_argument(
          "usage: task_da_p1_eval pipnn|nsg graph base.fbin query.fbin "
          "--entry N --k N --beams CSV --mode ON|OFF --query-ids FILE --out-dir DIR [--max-beam N] [--jobs N]");
    }
    const std::string fmt(argv[1]), graph_path(argv[2]), base_path(argv[3]), query_path(argv[4]);
    uint32_t entry = 0, k = 10, max_beam = 4096, jobs = 1;
    bool has_entry = false, has_k = false, has_beams = false, has_mode = false, has_qids = false, has_out = false;
    std::string beams_csv, mode, qids_path, out_dir_str;

    for (int i = 5; i < argc; ++i) {
      const std::string flag(argv[i]);
      if (i + 1 >= argc) throw std::invalid_argument("missing value for " + flag);
      const std::string val(argv[++i]);
      if (flag == "--entry") { entry = parse_u32(val); has_entry = true; }
      else if (flag == "--k") { k = parse_u32(val); has_k = true; }
      else if (flag == "--beams") { beams_csv = val; has_beams = true; }
      else if (flag == "--mode") { mode = val; has_mode = true; }
      else if (flag == "--query-ids") { qids_path = val; has_qids = true; }
      else if (flag == "--out-dir") { out_dir_str = val; has_out = true; }
      else if (flag == "--max-beam") { max_beam = parse_u32(val); }
      else if (flag == "--jobs") { jobs = parse_u32(val); }
      else { throw std::invalid_argument("unknown argument: " + flag); }
    }
    if (!has_entry || !has_k || !has_beams || !has_mode || !has_qids || !has_out)
      throw std::invalid_argument("missing required option");
    if ((mode != "ON" && mode != "OFF") || !k || jobs == 0 || jobs > 32)
      throw std::invalid_argument("invalid mode, k, or jobs");

    const auto base = task_da::load_fbin(base_path);
    const auto queries = task_da::load_fbin(query_path);
    if (queries.dim != base.dim) throw std::invalid_argument("query dimension mismatch");
    const auto beams = parse_beams(beams_csv, k, base.n, max_beam);
    const auto qids = load_query_ids(qids_path, queries.n);
    const std::filesystem::path out_dir(out_dir_str);
    std::filesystem::create_directories(out_dir);
    for (uint32_t beam : beams) {
      const auto p = out_dir / ("beam_" + std::to_string(beam) + "_" + mode + ".jsonl");
      if (std::filesystem::exists(p)) throw std::runtime_error("refusing to overwrite existing output");
    }

    const task_da::Index index(task_da::load_graph(graph_path, fmt, static_cast<uint32_t>(base.n), entry), base);
    const bool instrument = (mode == "ON");

    std::cout << "{\"scope\":\"P1_VALIDATION_NOT_BENCHMARK\",\"workers\":1,\"query_batch_jobs\":" << jobs
              << ",\"search_policy\":\"entry_best_first_v1\","
              << "\"instrumentation\":\"" << mode << "\",\"entry\":" << entry << ",\"k\":" << k
              << ",\"queries\":" << qids.size() << ",\"runs\":[";
    for (size_t bi = 0; bi < beams.size(); ++bi) {
      const uint32_t beam = beams[bi];
      const auto out_path = out_dir / ("beam_" + std::to_string(beam) + "_" + mode + ".jsonl");
      std::ofstream out(out_path, std::ios::out | std::ios::trunc);
      if (!out) throw std::runtime_error("cannot open output file");
      out << std::setprecision(17);

      const auto results = evaluate_queries(index, queries, qids, k, beam, instrument, jobs);
      size_t complete_top_k = 0;
      for (size_t idx = 0; idx < qids.size(); ++idx) {
        const auto& res = results[idx];
        const bool ok_k = res.hits.size() == k;
        if (ok_k) ++complete_top_k;
        out << "{\"scope\":\"P1_VALIDATION_NOT_BENCHMARK\",\"query_id\":" << qids[idx]
            << ",\"search_policy\":\"entry_best_first_v1\",\"workers\":1,\"beam\":" << beam
            << ",\"instrumentation\":\"" << mode << "\",\"ids\":[";
        for (size_t i = 0; i < res.hits.size(); ++i) out << (i ? "," : "") << res.hits[i].second;
        out << "],\"squared_l2\":[";
        for (size_t i = 0; i < res.hits.size(); ++i) out << (i ? "," : "") << res.hits[i].first;
        out << "],\"counters\":";
        if (!instrument) {
          out << "null";
        } else {
          const auto& c = res.counters;
          out << "{\"distance_evaluations\":" << c.distance_evaluations
              << ",\"expansions\":" << c.expansions
              << ",\"neighbor_attempts\":" << c.neighbor_attempts
              << ",\"already_seen_attempts\":" << c.already_seen_attempts
              << ",\"frontier_insertions\":" << c.frontier_insertions << "}";
        }
        out << ",\"complete_top_k\":" << (ok_k ? "true" : "false") << "}\n";
      }
      out.flush();
      if (!out) throw std::runtime_error("write error");
      std::cout << (bi ? "," : "") << "{\"beam\":" << beam
                << ",\"complete_top_k\":" << complete_top_k
                << ",\"jsonl\":\"" << out_path.filename().string() << "\"}";
    }
    std::cout << "]}\n";
    return 0;
  } catch (const std::exception& e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
}
