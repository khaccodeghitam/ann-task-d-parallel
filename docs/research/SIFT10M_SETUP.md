# SIFT10M immutable development package

Issue #6 prepares data/index provenance and minimal loading/search validation. This is development-scale setup, not SIFT100M paper reproduction or a hypothesis result. No FIFO, width, I/O scheduling, D1/D4 or ANN algorithm changes are involved.

## Preflight decision (before acquisition/build)

On 2026-10-08, `/dev/nvme0n1p6` (ext4, `/`) had 136,615,587,840 free bytes. RAM totals 16,542,253,056 bytes, with approximately 9.7 GB available. Keep existing SIFT1M inputs/indexes and all 357 historical run files.

Budget: approximately 2.58 GB for source plus canonical data, 4.5 GB final index estimate, 20 GiB build temporaries, 1 GiB evidence, and 20 GiB untouched safety margin. This fits the measured space. No complete 1B/100M base download is authorized or needed.

Choose Vamana R64/L100/PQ32, memory budget 8 GiB, 8 build workers, uint8/L2/pq, mem_L=0. Canonical `estimate_ram_usage` estimates 5,068,800,000 bytes for R64 versus 6,899,200,000 bytes for R96; these estimates exclude some real runtime overhead. R64/PQ32 match verified SIFT1M index metadata; L100 matches the documented historical development configuration (the original build log was not recovered). Eight workers reduce scratch/CPU pressure. The 100M recommendation R96/L128/M256/T112 is unsuitable for this laptop. Record peak RSS and actual storage, and preserve/analyze failures before retrying.

## Canonical source and ordering

Golden PipeANN at b9ec4ba86ff5d70bec277984777197f28dc2cf42, `docs/cpp-interface.md`, identifies original TexMex SIFT and recommends the [Big ANN benchmark mirror](https://big-ann-benchmarks.com/neurips21.html) when TexMex is unavailable. TexMex currently fails TLS hostname verification on this machine; verification remains enabled.

The official [dataset loader](https://github.com/harsha-simhadri/big-ann-benchmarks/blob/89a3abaafa63dda46b94b308bdf039e699841b3b/benchmark/datasets.py) defines BIGANN as uint8, D128, L2, 10,000 queries, and provides the first-10M subset ground truth. Its subset procedure takes a prefix from `base.1B.u8bin` and rewrites only the count header. This is the verified equivalent native-format family, rather than a third-party repackaging chosen by filename.

Sources:

- https://dl.fbaipublicfiles.com/billion-scale-ann-benchmarks/bigann/base.1B.u8bin
- https://dl.fbaipublicfiles.com/billion-scale-ann-benchmarks/bigann/query.public.10K.u8bin
- https://dl.fbaipublicfiles.com/billion-scale-ann-benchmarks/GT_10M/bigann-10M

The mirror base uses an 8-byte little-endian uint32 count/dimension header followed by contiguous uint8 vectors. It is **not bvecs**: the first 10M require **1,280,000,008 bytes**, not 1,320,000,000 bytes. Probe responses returned 206, Accept-Ranges: bytes, exact Content-Range, N=1B/D=128. Retain the downloaded prefix with its original 1B header; convert its verified 10M payload with golden `change_pts uint8 <prefix> 10000000`. Query is native N=10K/D128. Official 10M GT is Nq=10K/K100 with uint32 IDs and float32 distances, directly compatible with PipeANN; it is not claimed to be a downloaded `idx_10M.ivecs` file.

Range acquisition must reject a 200/full-body response before reading it, check exact Content-Range/length/ETag, count all received bytes, and compare first/middle/last vector payloads with independent tiny remote ranges. Store failed partials, never overwrite existing finals. Source ETags/version IDs identify server representations; locally computed SHA256 describes only bytes actually retained.

## Immutable package contract

External roots: `~/ann-research/data/bigann/sift10m/{source,canonical,manifests}`, `~/ann-research/indexes/sift10m`, and existing `~/ann-research/research-v3` evidence. Versioned package tooling and harness bindings are described below as they are finalized. No binaries, vectors, indexes, traces, virtualenvs or MLflow databases belong in Git.

## Reproduce acquisition and input finalization

Use the existing `.venv-research` (`requirements-research.txt`: MLflow/jsonschema). Historical unbound SIFT1M runs still use only the standard library; package workflows additionally validate against `schemas/research/package.schema.json` with jsonschema.

```sh
.venv-research/bin/python tools/research/acquire_bigann_prefix.py \
  --source-root ~/ann-research/data/bigann/sift10m/source
.venv-research/bin/python tools/research/prepare_bigann_package.py \
  --root ~/ann-research/data/bigann/sift10m \
  --subject-repo ~/ann-research/PipeANN
```

Run only into new empty destinations. Acquisition refuses existing final/partial/metadata paths. Finalization refuses an existing JSON or digest sidecar. A failed finalization must be diagnosed; do not erase files and retry blindly. Input conversion writes only new files, and applies read-only permissions after finalization. Native structural checks cover shape, exact size, all GT IDs and finite nonnegative distances; no clamping or repair is performed. The base utility copies exactly 10M vectors; the prefix's initial 1B header is intentionally retained solely in `source/`.

For another package, supply a small JSON specification to:

```sh
.venv-research/bin/python tools/research/package_manifest.py create \
  --spec /absolute/path/to/package-spec.json --output /new/path/INPUT_PACKAGE.json
.venv-research/bin/python tools/research/package_manifest.py verify \
  ~/ann-research/data/bigann/sift10m/manifests/INPUT_PACKAGE.json
```

The specification selects `package_kind: input|index`, dataset N/D/type/metric, unique file roles and absolute paths. Input entries also declare counts/dimensions/top-k, sources and conversion metadata. Index specs add the input digest, prefix, parameters and build provenance. Finalization captures size/mtime and computes a **full SHA256 once for every canonical component**, without the harness's historical 64 MiB limit. Stable JSON serialization sorts keys and ends with a newline. The `.sha256` sidecar hashes the exact manifest bytes. It is an integrity binding, not a signature or independent authentication of downloaded content; no published upstream checksum is invented.

Normal verification checks manifest SHA256, versioned schema, unique roles/canonical paths, component existence, size and mtime. It never rehashes large components. Read-only files and the immutable package contract prevent routine mutation; size/mtime checks alone cannot prove absence of same-size tampering with a restored timestamp. Explicit `verify --full-components` performs an audit when needed, rather than every repetition. The full-source base checksum is unknown because only a prefix was downloaded. Source prefix SHA256 is recorded separately.

## Index build and package

Reuse the clean canonical b9ec4ba builder; do not rebuild golden sources or SIFT1M. Build into a new dedicated prefix:

```sh
MKL_NUM_THREADS=8 OMP_NUM_THREADS=8 \
  ~/ann-research/PipeANN/build/tests/build_disk_index uint8 \
  ~/ann-research/data/bigann/sift10m/canonical/base_10m.bbin \
  ~/ann-research/indexes/sift10m/sift10m 64 100 32 8 8 l2 pq
```

Record exact argv/environment, binary digest, clean subject commit, CMake/compile metadata, UTC boundaries, wall time, `/usr/bin/time -v`, combined output, and coarse available RAM/disk samples. The setup monitor terminates only its own build process group if available memory falls below 1 GiB or free disk below 20 GiB; failures are retained and analyzed. Memory budget is a builder planning parameter, not a hard RSS limit. Check successful logs and final components because this builder's main does not reliably propagate internal failure as a nonzero exit.

After build, check native disk metadata/cardinality/layout, tags, PQ compressed shape/size, and pivot offset metadata before finalizing `INDEX_PACKAGE.json` with full hashes of all final components and the log. Search loading by both binaries is the final corruption/codec check. No separate canonical standalone index validator was found at the audited commit. Package logs remain outside Git.

## Bind every SIFT10M smoke to both packages

The existing runner adds optional `--input-package-manifest` and `--index-package-manifest`. Both are **required when dataset-id is sift10m**. It verifies schema/digest and cheap component metadata; query/GT roles, dataset type/metric/shape, index prefix/component roles, neighbor codec, and the index's input digest must agree. An index binding requires its input binding. Historical SIFT1M commands without packages remain supported; old finalized manifests are not rewritten. Optional nullable package path/digest fields extend manifest v2. MLflow gets both digests as params and tags; raw events stay local. The derived run-index schema is unchanged; authoritative package bindings are in each manifest.

```sh
.venv-research/bin/python tools/research/run_ann_experiment.py \
  --benchmark-profile pipeann-b9ec4ba \
  --executable ~/ann-research/PipeANN/build/tests/search_disk_index \
  --subject-repo ~/ann-research/PipeANN \
  --dataset-id sift10m --data-type uint8 \
  --dataset-path ~/ann-research/data/bigann/sift10m/canonical/base_10m.bbin \
  --query ~/ann-research/data/bigann/sift10m/canonical/query.bbin \
  --ground-truth ~/ann-research/data/bigann/sift10m/canonical/gt_10m.bin \
  --index-id sift10m-R64-L100-PQ32 \
  --index-prefix ~/ann-research/indexes/sift10m/sift10m \
  --input-package-manifest ~/ann-research/data/bigann/sift10m/manifests/INPUT_PACKAGE.json \
  --index-package-manifest ~/ann-research/indexes/sift10m/INDEX_PACKAGE.json \
  --threads 8 --wcap 32 --k 10 --l-search 100 --mem-l 0 \
  --distance-metric l2 --neighbor-type pq --search-mode 2 --trace-mode OFF \
  --mlflow --evidence-root ~/ann-research/research-v3 --dry-run
```

Remove `--dry-run` for the golden smoke. For instrumented OFF, change executable/subject to `PipeANN-p0` and add `--causal-trace`. For DETAIL also use `--trace-mode DETAIL --trace-detail-first-n 4`. Initial smoke L100 is chosen before observing results; freeze it if recall is useful (90% or higher). At most one higher L trial is permitted if this loading validation would otherwise have poor recall. These are loading/provenance/tracer checks, not matched performance repetitions or overhead estimates.

For required traces, benchmark success alone is insufficient: overall `run_status` must be success and `trace_valid` true. DETAIL requires zero drops, ordering violations and outstanding correlations. Retain the merged timing definition: submit is immediately before io_uring_submit; CQE-seen is userspace poll processing. Their difference is a **userspace-observed I/O interval**, never device hardware latency.

Finalize the index once after successful build using the captured metadata:

```sh
.venv-research/bin/python tools/research/finalize_bigann_index.py \
  --input-package-manifest ~/ann-research/data/bigann/sift10m/manifests/INPUT_PACKAGE.json \
  --build-metadata /absolute/path/to/setup-notes/build_metadata.json \
  --output ~/ann-research/indexes/sift10m/INDEX_PACKAGE.json
```

This validates the canonical disk sector layout, every identity tag, compressed PQ shape, and all pivot block offsets/shapes. Package JSON/sidecars and input/PQ/tag components are made read-only after finalization. The disk index retains owner-write because canonical `LinuxAlignedFileReader::open()` unconditionally requests `O_RDWR` even for read-only search. No search writes are requested; its bytes/size/mtime remain immutable under the package contract. Making this file 0444 causes EBADF CQEs with NDEBUG and can yield a spurious zero-recall benchmark table. The harness rejects explicit canonical reader ERROR diagnostics even if the process exits 0. The setup build-monitor script itself is preserved and hashed in external evidence; the canonical builder command above is sufficient to reproduce the index build, while `finalize_bigann_index.py` preserves that metadata in the immutable index manifest.
