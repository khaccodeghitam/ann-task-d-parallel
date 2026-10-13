# Start here

**For a new native ANN benchmark on the owner's laptop:** read [Custom Full-Fan Experimental Environment v1](EXPERIMENTAL_ENVIRONMENT_V1.md) first, manually configure the host, and use `configs/custom_fullfan_campaign.json` with the Issue29 harness only after the preflight gates pass. A foreign host needs its own explicitly named measured environment profile. Synthetic tests and no-data dry runs do not require Custom Mode.

The reproducibility workflow from PR28 is merged into main at `5ec0841fcd04e9c06824ef3e10b59f4b08d58ed7`. The [Issue29 follow-up](ISSUE29_WORKFLOW.md) is on a separate Draft PR branch until reviewed/merged; it does not certify a stock baseline after its thermal stop.

```sh
git clone https://github.com/Irthn1311/Parallel_ANN_Research.git
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

Verified in PR28: a fresh detached checkout and fresh dependency-only virtualenv passed430 synthetic tests, CLI/dry-run/missing-data checks and separate quality-probe compilation. Issue29 ran that separate quality binary prospectively: T16 correctness passed; subsequent T8 hit100°C and stopped safely before stock runs. Full fresh upstream compilation and multi-GB artifact transfer/search on another host remain **NOT_VERIFIED**; TEAM_CLONE_SMOKE remains PARTIAL.
