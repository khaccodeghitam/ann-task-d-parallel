// Compile with the actual portable src/distance.cpp, never a copied kernel.
#include "distance.h"
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <algorithm>
int main() {
  alignas(64) float a[512], b[512];
  alignas(64) uint8_t u[512], v[512];
  std::mt19937 rng(20261012);
  diskann::DistanceL2 f;
  diskann::DistanceL2UInt8 g;
  double max_double_rel=0, max_float_rel=0;
  unsigned cases=0, byte_cases=0;
  for (unsigned n : {8u, 32u, 128u, 256u, 512u}) {
    for (unsigned trial=0;trial<2000;trial++) {
      for(unsigned i=0;i<n;i++) {
        float scale=trial%5==0 ? (i%2 ? 1e-3f : 1e3f) : 1.f;
        a[i]=(float(int(rng()%20001)-10000)/100.f)*scale;
        b[i]=trial%7==0 ? a[i] : (float(int(rng()%20001)-10000)/100.f)*scale;
        u[i]=rng()%256; v[i]=trial%11==0 ? u[i] : rng()%256;
      }
      if(trial==0) for(unsigned i=0;i<n;i++) {u[i]=0;v[i]=255;}
      double ref=0; float rf=0; uint64_t ri=0;
      for(unsigned i=0;i<n;i++) {
        double d=double(a[i])-double(b[i]);ref+=d*d;
        float df=a[i]-b[i];rf+=df*df;
        int di=int(u[i])-int(v[i]);ri+=di*di;
      }
      double got=f.compare(a,b,n);
      double rel=std::abs(got-ref)/std::max(1.,ref);
      double relf=std::abs(got-rf)/std::max(1.,double(rf));
      max_double_rel=std::max(max_double_rel,rel);
      max_float_rel=std::max(max_float_rel,relf);
      if(!std::isfinite(got)||rel>2e-6||relf>5e-6) {std::cerr<<"float failure\n";return 1;}
      // D128's maximum is <2^24, hence exactly float-representable.
      if(n<=128) {
        if(g.compare(u,v,n)!=float(ri)) {std::cerr<<"uint8 failure\n";return 2;}
        byte_cases++;
      }
      cases++;
    }
  }
  std::cout<<"{\"float_cases\":"<<cases<<",\"uint8_exact_cases\":"<<byte_cases
           <<",\"max_double_relative_error\":"<<max_double_rel
           <<",\"max_scalar_float_relative_error\":"<<max_float_rel<<"}\n";
}
