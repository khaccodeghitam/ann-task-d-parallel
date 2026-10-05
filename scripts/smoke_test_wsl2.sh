#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BUILD_DIR="${BUILD_DIR:-${PROJECT_ROOT}/build}"
SMOKE_DIR="${SMOKE_DIR:-${PROJECT_ROOT}/smoke_test}"
THREADS="${THREADS:-4}"

DATA_DIR="${SMOKE_DIR}/data"
INDEX_DIR="${SMOKE_DIR}/index"
INDEX_PREFIX="${INDEX_DIR}/test"

required_bins=(
  "${BUILD_DIR}/tests/build_disk_index"
  "${BUILD_DIR}/tests/build_memory_index"
  "${BUILD_DIR}/tests/search_disk_index"
  "${BUILD_DIR}/tests/utils/compute_groundtruth"
)

for binary in "${required_bins[@]}"; do
  if [[ ! -x "${binary}" ]]; then
    echo "ERROR: Missing executable: ${binary}" >&2
    echo "Build the project first; see HUONG_DAN_WSL2_VA_CHAY_BASELINE.md" >&2
    exit 1
  fi
done

if ! grep -q -- '-DUSE_AIO' "${BUILD_DIR}/compile_commands.json"; then
  echo "ERROR: This WSL2 smoke test requires a build configured with -DUSE_AIO." >&2
  echo "Reconfigure with: env ADDITIONAL_DEFINITIONS=-DUSE_AIO cmake -S . -B build -DCMAKE_BUILD_TYPE=Release" >&2
  exit 1
fi

mkdir -p "${DATA_DIR}" "${INDEX_DIR}"

if [[ ! -f "${DATA_DIR}/base.bin" || ! -f "${DATA_DIR}/query.bin" ]]; then
  echo "[1/5] Generating deterministic float32 data (10000 x 128) and queries (100 x 128)..."
  python3 - "${DATA_DIR}/base.bin" "${DATA_DIR}/query.bin" <<'PY'
from array import array
import random
import struct
import sys

base_path, query_path = sys.argv[1:]
num_points = 10_000
num_queries = 100
dims = 128
rng = random.Random(20261003)

base = array("f", (rng.random() for _ in range(num_points * dims)))
queries = array("f")
for query_id in range(num_queries):
    point_id = (query_id * 97) % num_points
    begin = point_id * dims
    queries.extend(base[begin:begin + dims])

with open(base_path, "wb") as stream:
    stream.write(struct.pack("<II", num_points, dims))
    base.tofile(stream)

with open(query_path, "wb") as stream:
    stream.write(struct.pack("<II", num_queries, dims))
    queries.tofile(stream)
PY
else
  echo "[1/5] Reusing existing base.bin and query.bin."
fi

if [[ ! -f "${DATA_DIR}/truthset.bin" ]]; then
  echo "[2/5] Computing exact top-10 ground truth..."
  "${BUILD_DIR}/tests/utils/compute_groundtruth" \
    float \
    "${DATA_DIR}/base.bin" \
    "${DATA_DIR}/query.bin" \
    10 \
    "${DATA_DIR}/truthset.bin"
else
  echo "[2/5] Reusing existing truthset.bin."
fi

if [[ ! -f "${INDEX_PREFIX}_disk.index" ]]; then
  echo "[3/5] Building the disk index and PQ files..."
  "${BUILD_DIR}/tests/build_disk_index" \
    float \
    "${DATA_DIR}/base.bin" \
    "${INDEX_PREFIX}" \
    32 64 0.001 1 "${THREADS}" \
    l2 0
else
  echo "[3/5] Reusing existing disk index."
fi

if [[ ! -f "${INDEX_PREFIX}_mem.index" ]]; then
  echo "[4/5] Building the PipeANN in-memory entry index..."
  "${BUILD_DIR}/tests/build_memory_index" \
    float \
    "${INDEX_PREFIX}_sample_data.bin" \
    "${INDEX_PREFIX}_sample_ids.bin" \
    "${INDEX_PREFIX}_mem.index" \
    0 0 32 64 1.2 "${THREADS}" l2
else
  echo "[4/5] Reusing existing in-memory index."
fi

echo "[5/5] Running PipeANN (search_mode=2)..."
"${BUILD_DIR}/tests/search_disk_index" \
  float \
  "${INDEX_PREFIX}" \
  1 4 \
  "${DATA_DIR}/query.bin" \
  "${DATA_DIR}/truthset.bin" \
  10 l2 2 10 \
  10 20 30

echo "Smoke test completed successfully."
