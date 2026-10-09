# Reproduce the G0-C1 subject

Start from the exact prior subject `3bdcc064cb96aae4cd845bd2bb6adc5f5ba63e19` in a separate clone/worktree. Original P0_CAUSAL_PIPEANN.patch and P0_CAUSAL_SUBJECT_COMMIT.txt reproduce that subject from golden; never modify the golden tree.

```sh
git switch -c research/g0c1-distributed-detail-sampling 3bdcc064cb96aae4cd845bd2bb6adc5f5ba63e19
git apply --index /path/to/G0C1_SAMPLER.patch
git write-tree
# Must print a0f730206dd5d5e7e2c06bdf5894c583a79613ca
git hash-object -t commit -w /path/to/G0C1_SUBJECT_COMMIT.txt
# Must print 35222026893ff7d1b45586fcdd8165a5ce592cd3
git update-ref refs/heads/research/g0c1-distributed-detail-sampling 35222026893ff7d1b45586fcdd8165a5ce592cd3 3bdcc064cb96aae4cd845bd2bb6adc5f5ba63e19
```

The expected-old ref argument rejects conflicting state. No reset or force push. The standalone temporary-index reproduction was tested on this machine without changing worktree files. Source commit identity is reproducible; another host/toolchain may produce a different binary SHA. Build command/flags/compiler/CMake metadata are recorded in G0C1_SUBJECT.json. Exact current binary hash is the measurement identity. Prior subject binary was retained externally. No upstream subject push.
