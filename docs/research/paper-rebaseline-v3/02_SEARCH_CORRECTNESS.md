# Search correctness: not reached

**DIRECT MEASUREMENT:** Zero paper or modern ANN search process was launched in v3. No loading success, IDs, distances, recall or 10K result rows exist. Exit−15 records are index builders, not search results. No index is finalized from partial PQ files, and the correctness exporter is not used as headline performance evidence.

**VERIFIED SOURCE FACT:** Artifact CMake enables OVERLAP_INIT; [pipe_search.cpp](<https://github.com/thustorage/PipeANN/blob/d18dcd16fece1c9d1dea356d783ebba2ed649e54/src/v2/pipe_search.cpp#L178>) requires positive mem_L. Native target remains mem_L10 and `<prefix>_mem.index` plus `.data/.tags`. Modern uses its preserved native mem_L0 path. Paper has two full-query L200 warmups before its timed run; modern has no equivalent driver warmup. These differences cannot be hidden as a matched mem0 experiment.

Prospective canonical correctness command, **currently blocked**:

```sh
/home/irthn/ann-research/PipeANN-paper-portable/build/tests/search_disk_index uint8 <NEW_COMPLETED_PREFIX> 8 32 /home/irthn/ann-research/data/bigann/sift10m/canonical/query.bbin /home/irthn/ann-research/data/bigann/sift10m/canonical/gt_10m.bin 10 l2 2 10 100
```

Paper CLI has no positional nbr_type. Modern appends `pq` between metric and mode. Paper printed “P99 Lat” is0.999; modern is0.99. No percentile meaning is inferred from that shared label.

The separately identified existing post-timer probes are paper SHA256 `e4a4d2703000b0269aabbc0f98ae2419d1c0a7a276bf99f9123b416b771b8624` and modern `2ca9c418ba8c6665fc84c5840312ea4107b47903cf5bcb247a395a1442afc00a`; verified but never executed. Their driver captures actual returned count, IDs and distances without a second selector call; exports only the timed phase after the timer, preventing warmup/timed query-ID aliasing. Hot-loop count-store effects remain uncalibrated, so their QPS cannot replace stock-like headline data.

Independent synthetic validation passed: exact K, unique/in-range IDs, finite distance/stats, every exported uint8 squared-L2 recomputed from base/query, and source-compatible tie-aware recall over the supplied GT top100. A wrong distance and corruption fail. Real 10K validation is **NOT_MEASURED**. A32-query subset was prepared in a new evidence folder for bounded smoke only; it was not executed or substituted for the official10K workload.

**VERIFIED SOURCE FACT:** Native untagged static graph uses implicit identity mapping in [load_tags](<https://github.com/thustorage/PipeANN/blob/d18dcd16fece1c9d1dea356d783ebba2ed649e54/src/pq_flash_index.cpp#L432>) with mode2 no_mapping=true. Adding a fabricated10M tags file would change loading behavior. The scoped native-package adapter records this absent-file semantics. The merged generic package schema requires tags, so the new native adapter is explicit, not a false modern-package binding. Full real-index structure/load validation remains pending.
