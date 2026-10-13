# Data and artifact provisioning

Git contains no SIFT binaries, disk indexes or raw campaigns. Set `ANN_DATA_ROOT` to canonical files and `ANN_INDEX_ROOT` to the selected paper-native package. The portable manifest [paper_native_sift10m.json](../manifests/paper_native_sift10m.json) records relative names, nine required components, sizes/hashes, source and dataset binding. The builder's unused random warmup sample is not required for search.

Dataset: first10M canonical BigANN vectors, uint8×128,L2;10K ordered queries; matching top100 GT. Source provenance was verified in the setup campaign. Source URLs:

- `https://dl.fbaipublicfiles.com/billion-scale-ann-benchmarks/bigann/base.1B.u8bin` (only exact first10M prefix; **do not download full1B**).
- `https://dl.fbaipublicfiles.com/billion-scale-ann-benchmarks/bigann/query.public.10K.u8bin`
- `https://dl.fbaipublicfiles.com/billion-scale-ann-benchmarks/GT_10M/bigann-10M`

The native source base header says1B even for prefix acquisition; canonical base must say10M. Existing [preparation tool](../tools/research/prepare_bigann_package.py) records this conversion. No automatic acquisition occurs in the new CLI. Require correct HTTP206/Content-Range/byte count if acquiring a prefix; otherwise stop. Source descriptor context: [Big ANN benchmark](https://big-ann-benchmarks.com/neurips21.html), [original TexMex corpus](http://corpus-texmex.irisa.fr/). Public download availability and framework MIT licensing do not establish dataset redistribution rights. **Redistribution permission remains unverified**; no public index/data upload is offered. Obtain permission/provision data from the original source independently.

| File | Bytes | SHA256 |
|---|---:|---|
|base_10m.bbin|1280000008|`3f92342f582ebe3aa50751be105791e11894c4caac5b9d3321999457c56b054d`|
|query.bbin|1280008|`eca755831fc9a8004e14886df48b81109a8ed3bfc6b632509c93c0460a30d552`|
|gt_10m.bin|8000008|`80a4e35d5dc918e00e55f81e133e333e3b65f4de1426728c8a3ca93ac5ce74df`|

## Authorized transfer, fastest route

The owner can create a separately transferred directory using byte copies:

```sh
python scripts/ann.py copy-bundle --output /path/to/ABSENT/transfer
```

This verifies source hashes, copies into `data/` and `index/`, verifies destination hashes, and includes `MANIFEST.json`. No hardlinks, overwrites or upload. A failed partial transfer is preserved for inspection. Set peer roots to those directories and run `verify --full`; no owner home path is needed. No hosted transfer is currently promised.

Current original native INDEX_PACKAGE digest: `7140a47ac53b0480752059b5cb428b4d56dc627533974803b5ae4413827a7470`. Disk4,096,004,096bytes; six search files4,441,377,744bytes; entry100,004 nodes. Original manifest absolute paths stay local; portable manifest carries equivalent component identities. Modern index digest`8955f8bca0c8ebb5afbd2a69e9760fc829d22ba76a4ef7b482339e88b2489595` is a different package and must not be mixed.

Full hash once pre/post campaign; between runs check verified size/mtime. This is content identity at audit boundaries, not a cryptographic guarantee against transient undetectable in-place modification. Metadata/header/PQ/dataset checks reject missing, truncated, wrong-version and mixed components.
