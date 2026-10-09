// Read-only source audit probes, not an ANN observer or readiness implementation.
// Compile against the exact real PipeANN-p0 include directory, without stubs.
#include "candidate_pool.h"
#include <functional>
#include <iostream>
#include <stdexcept>
#include <unordered_set>

using pipeann::Neighbor;
using Pool = pipeann::CandidatePool<std::function<bool(unsigned)>>;

static void require(bool value, const char *message) {
  if (!value) throw std::runtime_error(message); // active even under -DNDEBUG
}
static Pool make_pool(std::unordered_set<unsigned> &published, unsigned capacity = 3) {
  return Pool(capacity, capacity + 1, [&published](unsigned id) { return published.count(id) != 0; });
}

int main() {
  unsigned passed = 0;
  auto test = [&](const char *name, auto body) {
    body();
    ++passed;
    std::cout << "PASS " << name << '\n';
  };
  test("empty pool selectors", [] {
    std::unordered_set<unsigned> map;
    auto p = make_pool(map);
    require(!p.next_read_nbr() && !p.next_calc_nbr(), "empty must have no eligible candidate");
  });
  test("read result does not clear selected flag", [] {
    std::unordered_set<unsigned> map;
    auto p = make_pool(map);
    p.insert(Neighbor(10, 1));
    auto *selected = p.next_read_nbr();
    require(selected && selected->flag && p.next_read_nbr() == selected, "read selector preserves flag");
  });
  test("flag cleared before send is not submitted evidence", [] {
    std::unordered_set<unsigned> map;
    auto p = make_pool(map);
    p.insert(Neighbor(10, 1));
    auto *selected = p.next_read_nbr();
    selected->flag = false; // same caller mutation, deliberately no physical I/O
    require(!p.next_read_nbr() && !p.next_calc_nbr(), "no eligible work can coexist with no submit");
    require(p.size() == 1 && !p[0].visited, "candidate remains live before send");
  });
  test("calc ready exists before selector despite zero inflight", [] {
    std::unordered_set<unsigned> map{10};
    auto p = make_pool(map);
    p.insert(Neighbor(10, 1));
    p[0].flag = false;
    require(!p[0].visited && map.count(p[0].id), "ready but unselected control");
    auto *selected = p.next_calc_nbr();
    require(selected && selected->id == 10, "existing selector chooses actual ready node");
  });
  test("calc selector itself consumes eligibility", [] {
    std::unordered_set<unsigned> map{10};
    auto p = make_pool(map);
    p.insert(Neighbor(10, 1));
    auto *selected = p.next_calc_nbr();
    require(selected && selected->visited && !selected->flag, "calc mutates both flags at selection");
    require(!p.next_calc_nbr(), "second measurement-only call would observe different state");
  });
  test("frontier mutates settled prefix", [] {
    std::unordered_set<unsigned> map{10};
    auto p = make_pool(map);
    p.insert(Neighbor(10, 1));
    p.insert(Neighbor(20, 2));
    require(p.next_calc_nbr()->id == 10 && p.first_unvisited() == 0, "calc does not advance prefix");
    require(p.frontier() == 1 && p.first_unvisited() == 1, "frontier advances both markers");
  });
  test("insertion rewinds frontier", [] {
    std::unordered_set<unsigned> map{10};
    auto p = make_pool(map);
    p.insert(Neighbor(10, 1));
    p.next_calc_nbr();
    p.frontier();
    p.insert(Neighbor(5, .5f));
    require(p.first_unvisited() == 0 && p.next_read_nbr()->id == 5, "new closer candidate rewinds");
  });
  test("batch eviction does not remove outstanding identity", [] {
    std::unordered_set<unsigned> map;
    auto p = make_pool(map, 2);
    p.insert(Neighbor(10, 1));
    p.insert(Neighbor(20, 2));
    p[1].flag = false;
    const Neighbor outstanding = p[1]; // io_t also owns a copy
    uint32_t ids[]{5}; float distances[]{.5f};
    p.insert_batch(ids, distances, 1);
    require(p.size() == 2 && p[0].id == 5 && p[1].id == 10, "old node evicted");
    map.insert(outstanding.id); // later publication of outstanding node
    require(map.count(20) && !p.next_calc_nbr(), "nonempty published map has no live ready candidate");
  });
  test("published visited node is calc ineligible", [] {
    std::unordered_set<unsigned> map{10};
    auto p = make_pool(map);
    p.insert(Neighbor(10, 1));
    p.next_calc_nbr();
    require(!map.empty() && !p.next_calc_nbr(), "map size is not calc-ready count");
  });
  test("full pool rejection preserves membership", [] {
    std::unordered_set<unsigned> map;
    auto p = make_pool(map, 2);
    p.insert(Neighbor(10, 1)); p.insert(Neighbor(20, 2));
    require(p.insert(Neighbor(30, 3)) == 2 && p.size() == 2 && p[1].id == 20, "full cutoff rejection");
  });
  test("batch rejected discoveries never become live", [] {
    std::unordered_set<unsigned> map;
    auto p = make_pool(map, 2);
    p.insert(Neighbor(10, 1)); p.insert(Neighbor(20, 2));
    uint32_t ids[]{30, 40}; float distances[]{3, 4};
    p.insert_batch(ids, distances, 2);
    require(p.size() == 2 && p[0].id == 10 && p[1].id == 20, "discovery is not admission");
  });
  test("rescore moves identities with flags", [] {
    std::unordered_set<unsigned> map;
    auto p = make_pool(map);
    p.seed(Neighbor(10, 1)); p.seed(Neighbor(20, 2));
    p.next_read_nbr()->flag = false;
    float distances[]{3, 1};
    p.rescore_seeds(distances);
    require(p[0].id == 20 && p[0].flag && p[1].id == 10 && !p[1].flag, "rank is not identity");
    require(p.next_read_nbr()->id == 20, "rescore rewinds read marker");
  });
  test("duplicate sentinel has existing non-full size side effect", [] {
    std::unordered_set<unsigned> map;
    auto p = make_pool(map);
    p.insert(Neighbor(10, 1));
    require(p.insert(Neighbor(10, 1)) == 2 && p.size() == 2, "document actual generic duplicate semantics");
    // No assumption that the extra slot is a valid admission. Normal batch dedup avoids this path.
  });
  test("equal distance has stable node-id order", [] {
    std::unordered_set<unsigned> map;
    auto p = make_pool(map);
    uint32_t ids[]{20, 10}; float distances[]{1, 1};
    p.insert_batch(ids, distances, 2);
    require(p[0].id == 10 && p[1].id == 20, "ordering matches node-id tie break");
  });
  std::cout << "RESULT " << passed << " source-contract probes passed\n";
}
