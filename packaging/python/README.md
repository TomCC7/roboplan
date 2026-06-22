# Python packaging

This directory contains the PyPI/cibuildwheel-specific packaging helpers for
RoboPlan. The normal ROS/ament and source-tree CMake build remains in the
package directories; the root `CMakeLists.txt` includes these helpers only to
configure Python wheel behavior when `SKBUILD` or cmeel packaging is active.

The helper CMake files cover three packaging-only concerns:

- expose cmeel's isolated native dependency prefix to scikit-build-core builds;
- install the runtime native libraries that Linux wheels need at import time;
- repair installed RPATHs with `patchelf` using checked-in CMake script
  templates rather than large embedded `install(CODE ...)` strings.

Release wheels are built by `.github/workflows/release.yml` with cibuildwheel
and are smoke-tested by importing the `roboplan` namespace and every compiled
submodule before publishing through PyPI trusted publishing.
