// SPDX-License-Identifier: MIT
#include "engine.hpp"
#include <iomanip>
#include <iostream>

static uint32_t number(const char* s) {
  const std::string value(s);
  if (value.empty() || value.find_first_not_of("0123456789") != std::string::npos)
    throw std::invalid_argument("expected unsigned integer");
  const auto parsed = std::stoull(value);
  if (parsed > UINT32_MAX) throw std::invalid_argument("integer out of range");
  return static_cast<uint32_t>(parsed);
}

int main(int argc, char** argv) {
  try {
    if (argc != 10) throw std::invalid_argument(
      "usage: task_da_smoke pipnn|nsg graph base.fbin query.fbin entry k beam ON|OFF query_limit(1..32)");
    const auto base = task_da::load_fbin(argv[3]);
    const auto queries = task_da::load_fbin(argv[4]);
    if (queries.dim != base.dim) throw std::invalid_argument("query dimension mismatch");
    const auto entry = number(argv[5]), k = number(argv[6]), beam = number(argv[7]), limit = number(argv[9]);
    const std::string mode(argv[8]);
    if ((mode != "ON" && mode != "OFF") || !limit || limit > 32 || limit > queries.n)
      throw std::invalid_argument("invalid instrumentation/query limit");
    task_da::Index index(task_da::load_graph(argv[2], argv[1], static_cast<uint32_t>(base.n), entry), base);
    std::cout << std::setprecision(17);
    for (size_t q = 0; q < limit; ++q) {
      std::vector<float> query(queries.values.begin() + q * queries.dim,
                               queries.values.begin() + (q + 1) * queries.dim);
      const auto result = mode == "ON" ? index.search<true>(query, k, beam) : index.search<false>(query, k, beam);
      std::cout << "{\"scope\":\"CORRECTNESS_SMOKE_NOT_BENCHMARK\",\"query_id\":" << q
                << ",\"search_policy\":\"entry_best_first_v1\",\"workers\":1,\"instrumentation\":\"" << mode << "\",\"ids\":[";
      for (size_t i = 0; i < result.hits.size(); ++i) std::cout << (i ? "," : "") << result.hits[i].second;
      std::cout << "],\"squared_l2\":[";
      for (size_t i = 0; i < result.hits.size(); ++i) std::cout << (i ? "," : "") << result.hits[i].first;
      std::cout << "],\"counters\":";
      if (mode == "OFF") std::cout << "null";
      else {
        const auto& c = result.counters;
        std::cout << "{\"distance_evaluations\":" << c.distance_evaluations
                  << ",\"expansions\":" << c.expansions << ",\"neighbor_attempts\":" << c.neighbor_attempts
                  << ",\"already_seen_attempts\":" << c.already_seen_attempts
                  << ",\"frontier_insertions\":" << c.frontier_insertions << "}";
      }
      std::cout << ",\"complete_top_k\":" << (result.hits.size() == k ? "true" : "false") << "}\n";
    }
  } catch (const std::exception& e) { std::cerr << e.what() << '\n'; return 1; }
}
