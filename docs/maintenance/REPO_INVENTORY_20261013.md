# Repository inventory and migration ledger,2026-10-13

Audit was recorded **before changes** in external archive `PAPER_BASELINE_RESEARCH_20261013T092006889480Z/audit`. Original branch`research/pipeann-paper-portable-v2-20261012`, HEAD`abc7915b12cd2a4716c73e3c99415b0111f04849`. Three untracked files (full-fan report/wrapper/tests) were copied to a scoped tar plus SHA256 map before reconciliation. All397 baseline tests passed. Repo has777 tracked files before this task; largest tracked assets are legacy Windows DLLs(~2.3MB), not datasets/indexes.

Remote verified via connected GitHub: `Irthn1311/Parallel_ANN_Research`, **private**, defaultmain. Terminal HTTPS credentials are unavailable; connected Git-data API is used if publication succeeds. Main`32939fc4b5a952a588e7708e756a1eba8d673f0f`. PR23/24/25/26/27 allopen Draft/unmerged, heads59d0a48/b415ee5/638e58d/d06d3d9/abc7915 respectively at read time; none edited/merged/closed. No remote branch deletion, force-push or history rewrite.

| Important path | Classification | Mapping/rationale |
|---|---|---|
|README.md|CONSOLIDATE|Old guide→docs/archive/LEGACY_README.md; one active research entrypoint|
|AGENTS.md / RESEARCH_PHILOSOPHY.md|KEEP_ACTIVE|Stable charter imported from actual archived PR25 snapshot; no merge assertion|
|scripts/ann.py / configs / manifests / patches|KEEP_ACTIVE|One portable config-driven CLI; sibling source builds, no silent index build|
|tools/research|KEEP_ACTIVE / ARCHIVE_COMPACT|New workflow reuses parsers/guard; historical runners retained for replay, no path-breaking mass move|
|docs/research/* and frozen PLANs|ARCHIVE_COMPACT|Keep bytes/paths; index through docs/archive/HISTORY.md rather than competing root guides|
|src/include/tests C++/third_party/dependencies|ARCHIVE_COMPACT / UNKNOWN_REVIEW|Historical bundled source, inactive primary baseline. Retained with license and Windows compatibility references; no aesthetic deletion|
|full-fan untracked report|CONSOLIDATE|Original absolute-path raw copy stays sealed local; portable derived report replaces owner root with environment placeholder|
|full-fan wrapper/tests|KEEP_ACTIVE|Now versioned; native safety guard remains unchanged in this mission|
|new stock raw runs/thermal logs/proc snapshots|LOCAL_ONLY|External archive; Git gets compact uncertified rows/statistics and audit hashes|
|canonical SIFT10M/index/memory entry|LOCAL_ONLY|Immutable, full-hash verified; no rebuild, hardlink or binary upload|
|old quiet/G0/D campaigns|LOCAL_ONLY|Retained original IDs/statuses, no reuse as matched blocks|
|old root WSL guide / vendor binaries|UNKNOWN_REVIEW|Still reachable from legacy tree; review separately before removing dependencies|

No historical source file or frozen protocol was deleted or moved. This is a navigation/portability refresh, not wholesale source unvendoring. Old Git history may contain owner-specific paths; it was not rewritten. New active docs/config/results use relative paths/environment variables. `.gitignore` now excludes environment secrets, raw outputs and common binary dataset/index formats; already-tracked vendor artifacts are explicitly identified above rather than falsely claimed untracked.

Execution commits are retained locally; API publication may re-encode commit metadata while preserving identical Git trees. If so, local→published SHA/tree mapping is recorded in the delivery manifest, and original local execution commits remain on a provenance branch. This preserves history rather than resetting it. A feature-branch checkout is required until review/merge.
