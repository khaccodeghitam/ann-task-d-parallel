# Input and index compatibility

**DIRECT MEASUREMENT:** full-content pre-audits passed for canonical INPUT
`47d4bf47e6e515a3f3c4caeb357bdbc1af3bfcc4b319b0ae335678ca586dccc3` and existing modern INDEX `8955f8bca0c8ebb5afbd2a69e9760fc829d22ba76a4ef7b482339e88b2489595`. Exact argv, start/end, duration,
stdout/stderr and manifest digest are in `audits/pre_*.json`; corresponding post
results are in INTEGRITY.json. Nothing was downloaded, converted, rebuilt,
chmod'ed or written into those packages.

| Input | Shape / bytes | Full SHA256 |
| --- | --- | --- |
| base_10m.bbin | 10M×128 uint8 /1280000008 | 3f92342f582ebe3aa50751be105791e11894c4caac5b9d3321999457c56b054d |
| query.bbin | 10K×128 uint8 /1280008 | eca755831fc9a8004e14886df48b81109a8ed3bfc6b632509c93c0460a30d552 |
| gt_10m.bin | 10K×100 uint32 IDs +float32 distances /8000008 | 80a4e35d5dc918e00e55f81e133e333e3b65f4de1426728c8a3ca93ac5ce74df |

Acquisition/order/conversion are inherited from the verified immutable package,
not claimed newly reproduced. The original setup report documents the official
native-format10M prefix and query/GT sources. Artifact load_bin/load_truthset source
expects these bin conventions. Runtime end-to-end input acceptance is untested.

## Format signatures and interpretation

Source matrix: paper [reader](https://github.com/thustorage/PipeANN/blob/d18dcd16fece1c9d1dea356d783ebba2ed649e54/src/pq_flash_index.cpp) and
[writer](https://github.com/thustorage/PipeANN/blob/d18dcd16fece1c9d1dea356d783ebba2ed649e54/src/aux_utils.cpp); modern [SSD metadata](https://github.com/thustorage/PipeANN/blob/b9ec4ba86ff5d70bec277984777197f28dc2cf42/include/ssd_index_defs.h)
and [reader](https://github.com/thustorage/PipeANN/blob/b9ec4ba86ff5d70bec277984777197f28dc2cf42/src/ssd_index.cpp).

| Feature | Source and byte evidence | Verdict |
| --- | --- | --- |
| Little-endian count/dimension | bin uint32 N/D; modern file bytes decoded | static agreement |
| Disk node layout |128 uint8 coords +uint32 degree +64 uint32 IDs =388 bytes;10/4096 sector | eight spot nodes agree |
| Basic disk header | nr/nc then N,D,entry,node_len,nodes/sector | shared prefix |
| Extended metadata | paper frozen_points/frozen_id/tags/PQ offsets vs modern shard_count/attr_size/range/R_ood | different semantics; not interchangeable by name |
| Tags | separate N10M×1 uint32 identity mapping | package structure verified |
| PQ compressed | N10M×32 byte payload | source-compatible shape |
| PQ pivots | five offsets,256×128 centres,128 centroid/permutation,33 chunk boundaries | source-compatible shapes, not identical training |
| Alignment |4096-byte sectors,10 nodes/sector | matches current bytes |
| Actual paper open/search/GT | no paper binary | NOT_RUN; compatibility unproven |

Modern raw header after nr/nc: N10M,D128,entry6309347,node_len388,10 nodes/sector,
then10M,0,64,0,0,0. Paper interprets10M as frozen_points (its special frozen case
checks1), and64 as tags offset. Split-file readers use separate files and reset
PQ offsets. That supports a **conditional** plain static-layout hypothesis, not
proof that every header field/index feature is safely interchangeable. Detailed
raw bytes, PQ offsets and eight node tests are in `source/index_structure.json`.
Nodes0,1,9,10,123456,5000000,6309347,9999999 matched canonical coordinates;
all degree64 neighbors were unique and in range. This is not a full graph scan.

Modern components total4,456,140,468 bytes:
disk4096004096, tags40000008, PQ320000008, pivots136356. Exact per-file hashes
are retained in the existing verified INDEX_PACKAGE, copied into external
input/index identity metadata. Golden builder SHA
`e104fd3cc3f7a0a0cd3728a07efab5f4456a2807cda2abba98b0c6b1ba8d0e1c`;
historical build1053.543s/7166904KiB RSS are planning evidence from the setup,
**not new artifact measurements**. A modern-built index is not paper-native.

## Artifact-native construction contract, not an executed build

[tests/build_disk_index.cpp](https://github.com/thustorage/PipeANN/blob/d18dcd16fece1c9d1dea356d783ebba2ed649e54/tests/build_disk_index.cpp#L17-L43)
ends with single_file_index0/1, not “pq”. [aux_utils.cpp](https://github.com/thustorage/PipeANN/blob/d18dcd16fece1c9d1dea356d783ebba2ed649e54/src/aux_utils.cpp#L80-L104)
computes PQ chunks from search RAM budget B in GiB, then clamps to dimension.
For10M×32 bytes, B=320000000/2^30 = **0.298023223876953125 GiB** (below cache-budget
subtraction threshold). Passing modern “32” as B would request128 chunks after
dimension capping, not32. Native candidate command, **blocked/unexecuted**:

```sh
/home/irthn/ann-research/PipeANN-paper/build/tests/build_disk_index uint8 \
  /home/irthn/ann-research/data/bigann/sift10m/canonical/base_10m.bbin \
  /home/irthn/ann-research/indexes/sift10m-paper/sift10m \
  64 100 0.298023223876953125 8 8 l2 0
```

Verify emitted chunk count32 before accepting. R64/Lbuild100/M8/T8 can be mapped;
same nominal values still do not promise identical graph/PQ bytes, random seeds,
entry point or recall. A default OVERLAP artifact also needs an independently
versioned native entry index and mem_L>0; this target's mem_L0 does not satisfy it.

Initial disk116.7GiB free, MemAvailable13.2GiB. Planning reservation4.5GB final+
20GiB temporary+1GiB evidence+20GiB retained margin leaves about71.5GiB above
all reservations. No storage/RAM gate failure was observed. A historical6.84GiB
RSS is not a bound on this builder. Native build was **skipped for prior source/
build blockers**, not completed or aborted for resource exhaustion. No new
artifact-native index directory/components/package digest were invented.

Future non-destructive compatibility smoke must validate actual reads, all query
outputs/IDs/distances, GT recall and pre/post hashes, not just open or exit0.
Both versions' O_RDWR/O_DIRECT readers must have existing appropriate access;
do not chmod protected inputs. The historical EBADF/recall0 failure is retained
as a warning about exit-only checks, not new loading evidence.
