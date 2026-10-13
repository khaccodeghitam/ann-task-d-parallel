# Start here

This workflow is introduced on `research/paper-baselines-algorithm-studies-20261013`. Until reviewed and merged, a default-main clone does not contain it. If that branch has not been pushed, use an owner-supplied Git bundle/local clone; publication status is in the final handoff.

```sh
git clone --branch research/paper-baselines-algorithm-studies-20261013 https://github.com/Irthn1311/Parallel_ANN_Research.git
cd Parallel_ANN_Research
python3 -m venv .venv
.venv/bin/pip install -r requirements-lite.txt
cp .env.example .env
# Edit .env to existing external artifacts, then:
set -a; . ./.env; set +a
.venv/bin/python scripts/ann.py preflight
.venv/bin/python scripts/ann.py campaign --dry-run
```

Repository access may require the owner's GitHub permission. Never paste credentials into config or logs. Shell quoting supports spaces; configs expand named environment variables and reject unset placeholders. `.env` is ignored.

Provision the [pinned sources/binaries](BUILD_AND_REPRODUCE.md) and [input/index package](DATASETS_AND_ARTIFACTS.md) separately. Verify before search:

```sh
.venv/bin/python scripts/ann.py verify --full
.venv/bin/python scripts/ann.py quality-build --output "$ANN_RESEARCH_ROOT/quality-probe"
# Set ANN_QUALITY_BINARY to its quality_search, then:
.venv/bin/python scripts/ann.py smoke --output "$ANN_RESEARCH_ROOT/evidence/peer-smoke"
```

Smoke uses32 queries with independently checked IDs/distances/recall, explicitly separate from stock performance. It never constructs an index. Missing artifacts produce errors rather than a hidden download/build. Existing output directories are never overwritten.

Tests without real data:

```sh
.venv/bin/python -m unittest discover -s tests/research -v
```

CPU-only synthetic CI requires no private package. A different CPU/toolchain produces its own binary hash (`-march=native`); bind that hash in the new protocol, do not impersonate the owner's executable. Currently tested sensor guard is Intel `coretemp` on native Linux; unsupported temperature/AC observations fail closed.

Verified in this mission: a fresh detached checkout and fresh dependency-only virtualenv passed all430 synthetic tests, CLI/dry-run/missing-data checks and separate quality-probe compilation against the preserved local subject. No real ANN search was launched from that probe after the thermal stop. Full fresh upstream compilation and multi-GB artifact transfer on another host remain unexecuted; TEAM_CLONE_SMOKE is PARTIAL for those integration stages.
