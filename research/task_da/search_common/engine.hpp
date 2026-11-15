// SPDX-License-Identifier: MIT
// Independent P1 correctness baseline. No upstream search implementation copied.
#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <limits>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

namespace task_da {
using Id = uint32_t;
using Hit = std::pair<double, Id>;

// Decode explicitly; reject malformed lengths before allocating from headers.
inline std::vector<Id> words(const std::string& path) {
  std::ifstream in(path, std::ios::binary | std::ios::ate);
  if (!in) throw std::invalid_argument("cannot open input");
  const auto bytes = in.tellg();
  if (bytes < 8 || bytes % 4) throw std::invalid_argument("invalid binary size");
  in.seekg(0);
  std::vector<Id> data(static_cast<size_t>(bytes) / 4);
  for (auto& value : data) {
    unsigned char b[4];
    if (!in.read(reinterpret_cast<char*>(b), 4)) throw std::invalid_argument("truncated input");
    value = Id(b[0]) | (Id(b[1]) << 8) | (Id(b[2]) << 16) | (Id(b[3]) << 24);
  }
  return data;
}

struct Graph {
  Id entry = 0, max_degree = 0;
  std::vector<size_t> offsets;
  std::vector<Id> edges;
  size_t size() const { return offsets.empty() ? 0 : offsets.size() - 1; }
};

inline Graph load_graph(const std::string& path, const std::string& format,
                        Id expected_n, Id entry) {
  if (format != "pipnn" && format != "nsg") throw std::invalid_argument("graph format");
  const auto data = words(path);
  Graph g;
  const size_t n = expected_n;
  if (!n || n > data.size() - 2 || entry >= n) throw std::invalid_argument("vertex count/entry");
  if (format == "pipnn") {
    if (data[0] != n) throw std::invalid_argument("graph/base count mismatch");
    g.max_degree = data[1];
  } else {
    g.max_degree = data[0];
    if (data[1] != entry) throw std::invalid_argument("NSG entry mismatch");
  }
  g.entry = entry;
  size_t pos = format == "pipnn" ? 2 + n : 2;
  g.offsets.reserve(n + 1);
  for (size_t node = 0; node < n; ++node) {
    if (format == "nsg" && pos >= data.size()) throw std::invalid_argument("missing degree");
    const size_t degree = format == "pipnn" ? data[2 + node] : data[pos++];
    if (degree > g.max_degree || degree > data.size() - pos) throw std::invalid_argument("invalid degree");
    g.offsets.push_back(g.edges.size());
    for (size_t j = 0; j < degree; ++j) {
      const Id neighbor = data[pos++];
      if (neighbor >= n) throw std::invalid_argument("neighbor out of range");
      g.edges.push_back(neighbor);  // Keep direction, order, duplicates and self-loops.
    }
  }
  g.offsets.push_back(g.edges.size());
  if (pos != data.size()) throw std::invalid_argument("trailing graph words");
  return g;
}

struct Vectors {
  size_t n = 0, dim = 0;
  std::vector<float> values;
};

inline Vectors load_fbin(const std::string& path) {
  static_assert(sizeof(float) == 4 && std::numeric_limits<float>::is_iec559);
  const auto data = words(path);
  const size_t n = data[0], dim = data[1];
  if (!n || !dim || n > (data.size() - 2) / dim || n * dim != data.size() - 2)
    throw std::invalid_argument("fbin shape/length mismatch");
  Vectors vectors{n, dim, {}};
  vectors.values.reserve(n * dim);
  for (size_t i = 2; i < data.size(); ++i) {
    float value;
    std::memcpy(&value, &data[i], 4);
    if (!std::isfinite(value)) throw std::invalid_argument("nonfinite vector");
    vectors.values.push_back(value);
  }
  return vectors;
}

struct Counters {
  uint64_t distance_evaluations = 0, expansions = 0, neighbor_attempts = 0;
  uint64_t already_seen_attempts = 0, frontier_insertions = 0;
};
struct Result { std::vector<Hit> hits; Counters counters; };

class Index {
  const Graph graph_;
  const Vectors base_;
 public:
  Index(Graph graph, Vectors base) : graph_(std::move(graph)), base_(std::move(base)) {
    if (!graph_.size() || graph_.size() != base_.n || graph_.entry >= base_.n || !base_.dim ||
        base_.n > std::numeric_limits<Id>::max() || base_.n > base_.values.size() / base_.dim ||
        base_.n * base_.dim != base_.values.size() || graph_.offsets.front() != 0 ||
        graph_.offsets.back() != graph_.edges.size()) throw std::invalid_argument("index shape");
    for (size_t i = 0; i < graph_.size(); ++i)
      if (graph_.offsets[i] > graph_.offsets[i + 1] ||
          graph_.offsets[i + 1] - graph_.offsets[i] > graph_.max_degree)
        throw std::invalid_argument("index offsets");
    for (Id id : graph_.edges) if (id >= base_.n) throw std::invalid_argument("index neighbor");
    for (float x : base_.values) if (!std::isfinite(x)) throw std::invalid_argument("index vector");
  }

  // A bounded best-first beam; discovered nodes never re-enter after eviction.
  // Only the entry seeds traversal. No cyclic-ID padding or hidden full scan.
  template<bool Instrument>
  Result search(const std::vector<float>& query, size_t k, size_t beam) const {
    if (query.size() != base_.dim || !k || k > beam || beam > base_.n)
      throw std::invalid_argument("search shape/k/beam");
    for (float x : query) if (!std::isfinite(x)) throw std::invalid_argument("nonfinite query");
    Result result;
    std::vector<uint8_t> seen(base_.n, 0);
    std::set<Hit> best, pending;
    auto discover = [&](Id node) {
      if (seen[node]) {
        if constexpr (Instrument) ++result.counters.already_seen_attempts;
        return;
      }
      seen[node] = 1;
      double distance = 0;
      for (size_t d = 0; d < base_.dim; ++d) {
        const double delta = double(base_.values[size_t(node) * base_.dim + d]) - double(query[d]);
        distance += delta * delta;
      }
      if constexpr (Instrument) ++result.counters.distance_evaluations;
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
      if constexpr (Instrument) ++result.counters.expansions;
      for (size_t edge = graph_.offsets[node]; edge < graph_.offsets[node + 1]; ++edge) {
        if constexpr (Instrument) ++result.counters.neighbor_attempts;
        discover(graph_.edges[edge]);
      }
    }
    for (const Hit& hit : best) {
      if (result.hits.size() == k) break;
      result.hits.push_back(hit);
    }
    return result;
  }
};
}  // namespace task_da
