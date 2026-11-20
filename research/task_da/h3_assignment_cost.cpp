// Offline replay microkernel only; this program cannot perform ANN search.
#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <vector>
struct Sig { uint64_t lo=0,hi=0; };
struct Seed { uint32_t id,degree; Sig sig; };
using Round=std::vector<Seed>;
static uint64_t now_ns() { return std::chrono::duration_cast<std::chrono::nanoseconds>(
    std::chrono::steady_clock::now().time_since_epoch()).count(); }
__attribute__((noinline)) uint64_t schedule(const Round& r, const std::vector<Sig>& table, bool sketch) {
  uint64_t code=0;
  if (sketch) {
    for (size_t i=0;i+3<r.size();i+=4) {
      const auto a=table[r[i].id], b=table[r[i+1].id], c=table[r[i+2].id],d=table[r[i+3].id];
      auto count=[](Sig x,Sig y) { return __builtin_popcountll(x.lo|y.lo)+__builtin_popcountll(x.hi|y.hi); };
      const int ac=count(a,c),bd=count(b,d),ad=count(a,d),bc=count(b,c);
      const bool swap = std::make_pair(std::max(ad,bc),ad+bc)<std::make_pair(std::max(ac,bd),ac+bd);
      code += (swap?i+1:1);
    }
  } else {
    uint64_t x=0,y=0;
    for (size_t i=0;i+1<r.size();i+=2) {
      const auto a=r[i].degree,b=r[i+1].degree;
      auto score=[](uint64_t u,uint64_t v){return std::make_pair(std::max(u,v),u>v?u-v:v-u);};
      const bool swap=score(x+b,y+a)<score(x+a,y+b);
      x+=swap?b:a;y+=swap?a:b;code+=swap?i+1:1;
    }
  }
  return code;
}
int main(int argc,char**argv) {
  try {
    if(argc!=2)throw std::runtime_error("usage: offline_cost snapshots.txt");
    std::ifstream f(argv[1]); size_t count; f>>count;
    if(!f||count>10000)throw std::runtime_error("invalid round count");
    std::vector<Round> rounds(count);std::vector<Sig> table(1000000);
    for(auto&r:rounds) {
      size_t n;f>>n;if(!f||n>32)throw std::runtime_error("seed cap");
      r.resize(n);
      for(auto&s:r) {
        f>>s.id>>s.degree>>s.sig.lo>>s.sig.hi;
        if(!f||s.id>=table.size())throw std::runtime_error("bad seed");
        table[s.id]=s.sig;
      }
    }
    volatile uint64_t sink=0;
    std::vector<std::array<uint64_t,2>> times(count,{0,0});
    // 32 complete-panel replays. First is warmup and retained separately in wall time.
    for(size_t rep=0;rep<33;++rep) for(size_t k=0;k<count;++k) {
      for(size_t p=0;p<2;++p) {
        asm volatile("" ::: "memory");
        auto t=now_ns();sink=sink+schedule(rounds[k],table,p==1);auto dt=now_ns()-t;
        if(rep)times[k][p]+=dt;
      }
    }
    std::cout<<"round,degree_ns,signature_ns\n";
    for(size_t k=0;k<count;++k)std::cout<<k<<','<<times[k][0]/32.0<<','<<times[k][1]/32.0<<'\n';
    std::cerr<<"sink="<<sink<<" sidecar_bytes="<<table.size()*sizeof(Sig)<<'\n';
  } catch(const std::exception&e) {std::cerr<<e.what()<<'\n';return 1;}
}
