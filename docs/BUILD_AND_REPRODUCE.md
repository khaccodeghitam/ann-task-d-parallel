# Build and reproduce

Start with [START_HERE](START_HERE.md) and separately provision dependencies. Verified upstream requirements: native x86 Linux, GCC/CMake/make, OpenMP, AVX2 for this subject, libaio, bundled liburing, Intel MKL ILP64 and Intel OpenMP libraries. Official [artifact README](https://github.com/thustorage/PipeANN/blob/d18dcd16fece1c9d1dea356d783ebba2ed649e54/README.md) lists Ubuntu packages. No helper installs packages or uses sudo. This machine uses GCC13.3/CMake3.28. Missing libraries/toolchain on a peer host are explicit provisioning blockers; a complete fresh compilation is not assumed tested on that host.

## Separate pinned stock and portable clones

Set absent `PIPEANN_STOCK_ROOT` and `PIPEANN_PAPER_ROOT` destinations in `.env`:

```sh
python scripts/ann.py build-source --dry-run
python scripts/ann.py build-source
```

The command pins official d18dcd1, keeps the original clean, applies only the checked patch to a separate clone, records a distinct local commit, builds bundled liburing with2 jobs and required CMake targets with DYN_PIPE_WIDTH (the artifact build.sh default) and OVERLAP_INIT. It refuses existing destinations. `-march=native` binaries are host-specific. Source/tree/binary hashes must be captured, not assumed identical to the owner's build.

## Rebuild instead of transfer: explicit long operation

Never overwrite a valid or failed prefix. Ensure ≥45GiB initial free space and ≥9GiB available RAM for this development build; retain ≥20GiB disk/≥1GiB RAM safety guard. Prior successful build took25m26s with sampled5.39GiB VmHWM; that is not a peer-host duration/peak guarantee. User manages cooling; no fan/power/affinity changes.

```sh
python scripts/ann.py build-index --output "$ANN_RESEARCH_ROOT/indexes/NEW_PAPER_PACKAGE" --dry-run
python scripts/ann.py build-index --output "$ANN_RESEARCH_ROOT/indexes/NEW_PAPER_PACKAGE"
```

CLI: `build_disk_index uint8 BASE PREFIX 64 100 0.298023223876953125 8 8 l2 0`. B is PQ RAM GiB, **not32**; require log/header chunks32. Search requires a separate memory entry, copied from a matching verified package or built using artifact utilities:

```sh
"$PIPEANN_PAPER_ROOT/build/tests/utils/gen_random_slice" uint8 "$ANN_DATA_ROOT/base_10m.bbin" "$ANN_RESEARCH_ROOT/entry_sample" 0.01
"$PIPEANN_PAPER_ROOT/build/tests/build_memory_index" uint8 "$ANN_RESEARCH_ROOT/entry_sample_data.bin" "$ANN_RESEARCH_ROOT/entry_sample_ids.bin" "$ANN_INDEX_ROOT/sift10m_mem.index" 0 0 32 64 1.2 8 l2
```

Create these only in absent destinations **after** disk builder completion: builder uses/deletes its own `_mem.index` temporary. Random sampling has no exposed fixed seed; new sample/index bytes need new hashes/cardinality/ID-membership validation and a new portable manifest. The supplied portable manifest pins the existing package and will reject a different rebuild until that new package is explicitly finalized. Full disk validation code is in `finalize_paper_native_index.py`; its historical hardcoded entry path is not a portable peer finalizer. Use its source-grounded `validate_structure` function and explicitly copy a matching entry. Automated peer rebuild finalization is therefore PARTIAL; transfer of the verified package is the tested fast workflow.

## No-build correctness and stock search

```sh
python scripts/ann.py verify --full
python scripts/ann.py quality-build --output "$ANN_RESEARCH_ROOT/quality-probe"
python scripts/ann.py smoke --output "$ANN_RESEARCH_ROOT/evidence/NEW_SMOKE"
"$PIPEANN_PAPER_ROOT/build/tests/search_disk_index" uint8 "$ANN_INDEX_ROOT/sift10m" 8 32 "$ANN_DATA_ROOT/query.bbin" "$ANN_DATA_ROOT/gt_10m.bin" 10 l2 2 10 100
```

The direct last command is the native CLI, not a monitored integration entrypoint. Prefer the campaign wrapper for official performance work. No positional `pq` field appears in this artifact CLI. OVERLAP_INIT/mem_L10 and two full L200 warmups are retained. Quality probe is an explicitly separate driver compiled against the unchanged portable library; post-timer export and a per-query return-count store are not stock.
