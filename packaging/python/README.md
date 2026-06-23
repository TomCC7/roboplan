# Python packaging

This directory contains the PyPI/cibuildwheel-specific packaging helpers for
RoboPlan. The normal ROS/ament and source-tree CMake build remains in the
package directories; `pyproject.toml` points scikit-build-core at this directory
with `tool.scikit-build.cmake.source-dir`.

The helper CMake files cover three packaging-only concerns:

- expose cmeel's isolated native dependency prefix to scikit-build-core builds;
- install the runtime native libraries that Linux wheels need at import time;
- repair installed RPATHs with `patchelf` using checked-in CMake script
  templates rather than large embedded `install(CODE ...)` strings.

Release wheels are built by `.github/workflows/build-pypi-wheels.yml` with
cibuildwheel and are smoke-tested by importing the `roboplan` namespace and
every compiled submodule. That workflow runs on pull requests so wheel build
breakage is caught before release. `.github/workflows/release.yml` invokes the
same build workflow from the tagged commit, downloads those fresh artifacts, and
publishes them through PyPI trusted publishing.

The initial wheel target is Linux x86_64 (`manylinux_2_28`). macOS and arm64 can
be added later with cibuildwheel once native dependency bundling has matching
import-smoke validation on those platforms.

## Local checks

Run commands from the repository root. Keep native parallelism capped on small
machines, matching CI:

```bash
export CMAKE_BUILD_PARALLEL_LEVEL=2
export MAKEFLAGS=-j2
export NINJAFLAGS=-j2
```

Source-build and import-test the unified wheel path:

```bash
uv venv --seed --python 3.13 /tmp/roboplan-wheel-check
uv pip install --python /tmp/roboplan-wheel-check/bin/python --no-cache .
cd /tmp
/tmp/roboplan-wheel-check/bin/python - <<'PY'
import roboplan
import roboplan.core
import roboplan.filters
import roboplan.example_models
import roboplan.simple_ik
import roboplan.optimal_ik
import roboplan.rrt
import roboplan.toppra
import roboplan.cartesian_planning
print("roboplan imports ok")
PY
```

Build one Linux wheel locally with cibuildwheel and the same import smoke test
used by CI:

```bash
CIBW_ARCHS_LINUX=x86_64 \
CIBW_BUILD='cp313-*' \
CIBW_SKIP='pp* *-musllinux*' \
CIBW_MANYLINUX_X86_64_IMAGE=manylinux_2_28 \
CIBW_ENVIRONMENT='CMAKE_BUILD_PARALLEL_LEVEL=2 MAKEFLAGS="-j2" NINJAFLAGS="-j2"' \
uvx --from cibuildwheel cibuildwheel --platform linux
```

Check the structural packaging contract:

```bash
uvx pytest tests/unified_python_package_test.py -q
```
