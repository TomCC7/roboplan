from pathlib import Path
import re
import tomllib
from typing import cast

ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _read_pyproject(path: str) -> dict[str, object]:
    return cast(dict[str, object], tomllib.loads(_read(path)))


def test_root_pyproject_defines_unified_roboplan_distribution() -> None:
    pyproject = ROOT / "pyproject.toml"

    assert (
        pyproject.exists()
    ), "root pyproject.toml is required for the unified roboplan wheel"

    data = cast(dict[str, object], tomllib.loads(pyproject.read_text(encoding="utf-8")))
    build_system = cast(dict[str, object], data["build-system"])
    build_requires = cast(list[str], build_system["requires"])
    project = cast(dict[str, object], data["project"])

    assert project["name"] == "roboplan-dimos"
    assert project["version"] == "0.4.0"
    assert project["requires-python"] == ">=3.10,<3.15"
    assert "cmeel-eigen[build]" in build_requires
    assert "cmeel-yaml-cpp[build]" in build_requires
    assert "libpinocchio[build] == 4.0.0" in build_requires
    assert "patchelf; platform_system == 'Linux'" in build_requires
    dependencies = cast(list[str], project["dependencies"])
    assert "roboplan-core" not in dependencies
    assert "numpy" in dependencies
    assert "pin" in dependencies
    assert "matplotlib" in dependencies

    tool = cast(dict[str, object], data["tool"])
    scikit_build = cast(dict[str, object], tool["scikit-build"])
    cmake = cast(dict[str, object], scikit_build["cmake"])
    assert cmake["source-dir"] == "packaging/python"
    defines = cast(dict[str, str], cmake["define"])
    assert defines["CMAKE_POLICY_VERSION_MINIMUM"] == "3.5"
    assert defines["CMAKE_INSTALL_LIBDIR"] == "lib"
    assert defines["CMAKE_INSTALL_RPATH"] == "$ORIGIN/../../lib"
    assert defines["CMAKE_INSTALL_RPATH_USE_LINK_PATH"] == "FALSE"

    sdist = cast(dict[str, list[str]], scikit_build["sdist"])
    assert ".omo/**" in sdist["exclude"]


def test_packaging_directory_is_ignored_by_colcon() -> None:
    assert (ROOT / "packaging/COLCON_IGNORE").exists()


def test_packaging_cmake_uses_scikit_build_dependency_prefix_only() -> None:
    packaging_cmake = _read("packaging/python/CMakeLists.txt")
    helper = _read("packaging/python/cmake/roboplan_python_packaging.cmake")

    assert "include(cmake/roboplan_python_packaging.cmake)" in packaging_cmake
    assert "roboplan_configure_scikit_build_prefix()" in packaging_cmake
    assert "roboplan_ensure_hpp_fcl_target" not in packaging_cmake
    assert "hpp-fcl" not in helper
    assert "/opt/ros" not in helper


def test_cmeel_split_packages_define_native_and_python_wheels() -> None:
    libroboplan = _read_pyproject("packaging/cmeel/libroboplan/pyproject.toml")
    roboplan = _read_pyproject("packaging/cmeel/roboplan/pyproject.toml")

    lib_build = cast(dict[str, object], libroboplan["build-system"])
    lib_project = cast(dict[str, object], libroboplan["project"])
    lib_tool = cast(dict[str, object], libroboplan["tool"])
    lib_cmeel = cast(dict[str, object], lib_tool["cmeel"])
    lib_args = cast(list[str], lib_cmeel["configure-args"])

    assert lib_build["build-backend"] == "cmeel"
    assert lib_project["name"] == "libroboplan"
    assert lib_cmeel["source"] == "../../python"
    assert lib_cmeel["has-sitelib"] is False
    assert "-DROBOPLAN_CMEEL=ON" in lib_args
    assert "-DBUILD_PYTHON_BINDINGS=OFF" in lib_args
    assert "-DBUILD_TESTING=OFF" in lib_args
    assert "-DBUILD_TESTING_OINK=OFF" not in lib_args

    py_build = cast(dict[str, object], roboplan["build-system"])
    py_project = cast(dict[str, object], roboplan["project"])
    py_tool = cast(dict[str, object], roboplan["tool"])
    py_cmeel = cast(dict[str, object], py_tool["cmeel"])
    py_args = cast(list[str], py_cmeel["configure-args"])
    py_dependencies = cast(list[str], py_project["dependencies"])

    assert py_build["build-backend"] == "cmeel"
    assert py_project["name"] == "roboplan"
    assert py_cmeel["source"] == "../../python"
    assert "libroboplan == 0.4.0" in py_dependencies
    assert "pin == 4.0.0" in py_dependencies
    assert "-DROBOPLAN_CMEEL=ON" in py_args
    assert "-DBUILD_STANDALONE_PYTHON_BINDINGS=ON" in py_args
    assert "-DGENERATE_PYTHON_STUBS=OFF" in py_args


def test_root_cmake_superbuild_adds_all_python_binding_packages_in_order() -> None:
    cmake = ROOT / "packaging/python/CMakeLists.txt"

    assert (
        cmake.exists()
    ), "packaging/python/CMakeLists.txt is required for the unified roboplan wheel"

    source = cmake.read_text(encoding="utf-8")
    helper_source = _read("packaging/python/cmake/roboplan_python_packaging.cmake")
    package_order = re.findall(
        r'add_subdirectory\("\$\{ROBOPLAN_REPOSITORY_ROOT\}/(roboplan(?:_[a-z_]+)?)"\s+"[^/]+"\)',
        source,
    )

    repair_source = _read("packaging/python/cmake/repair_unified_rpaths.cmake.in")

    assert "roboplan_configure_scikit_build_prefix()" in source
    assert "roboplan_configure_unified_python_wheel()" in source
    assert "cmeel.prefix" in helper_source
    assert "list(PREPEND CMAKE_PREFIX_PATH" in helper_source
    assert "${ROBOPLAN_CMEEL_PREFIX}/lib" in helper_source
    assert "${search_prefix}/lib/${pattern}" in helper_source
    assert "boost_atomic" in helper_source
    assert "roboplan_install_matching_libraries" in helper_source
    assert "libboost_atomic.so.*" in helper_source
    assert "libboost_filesystem.so.*" in helper_source
    assert "liburdfdom_world.so.*" in helper_source
    assert "libOsqpEigen.so.*" in helper_source
    assert ".so.1.90.0" not in helper_source
    assert ".so.0.11.0" not in helper_source
    assert "install(SCRIPT" in helper_source
    assert "install(CODE" not in helper_source
    assert "--set-rpath" in repair_source
    assert "$ORIGIN/../../lib" in helper_source
    assert package_order == [
        "roboplan_example_models",
        "roboplan",
        "roboplan_simple_ik",
        "roboplan_oink",
        "roboplan_rrt",
        "roboplan_toppra",
        "roboplan_cartesian_planning",
    ]


def test_packaging_entrypoint_provides_build_tree_package_configs() -> None:
    helper = _read("packaging/python/cmake/roboplan_python_packaging.cmake")
    packaging_cmake = _read("packaging/python/CMakeLists.txt")

    assert "roboplan_register_build_tree_packages()" in packaging_cmake
    assert "function(roboplan_register_build_tree_package package_name)" in helper
    assert "${package_name}_DIR" in helper
    assert "roboplan::roboplan=roboplan" in helper
    assert "roboplan::filters=filters" in helper
    assert (
        "roboplan_example_models::roboplan_example_models=roboplan_example_models"
        in helper
    )
    assert (
        "roboplan_cartesian_planning::roboplan_cartesian_planning=roboplan_cartesian_planning"
        in helper
    )


def test_dependent_packages_keep_upstream_find_package_shape() -> None:
    for path in [
        "roboplan_simple_ik/CMakeLists.txt",
        "roboplan_oink/CMakeLists.txt",
        "roboplan_rrt/CMakeLists.txt",
        "roboplan_toppra/CMakeLists.txt",
        "roboplan_cartesian_planning/CMakeLists.txt",
    ]:
        source = _read(path)

        assert "find_package(roboplan REQUIRED)" in source, path
        assert "if(NOT TARGET roboplan::roboplan)" not in source, path


def test_binding_packages_keep_upstream_nanobind_discovery() -> None:
    for path in [
        "roboplan/bindings/CMakeLists.txt",
        "roboplan_example_models/bindings/CMakeLists.txt",
        "roboplan_simple_ik/bindings/CMakeLists.txt",
        "roboplan_oink/bindings/CMakeLists.txt",
        "roboplan_rrt/bindings/CMakeLists.txt",
        "roboplan_toppra/bindings/CMakeLists.txt",
        "roboplan_cartesian_planning/bindings/CMakeLists.txt",
    ]:
        source = _read(path)

        assert "-m nanobind --cmake_dir" in source, path
        assert "find_package(nanobind CONFIG REQUIRED)" in source, path
        assert "ROBOPLAN_NANOBIND_PYTHON_RESULT" not in source, path


def test_dependent_package_tests_keep_upstream_example_model_dependency() -> None:
    for path in [
        "roboplan/test/CMakeLists.txt",
        "roboplan_oink/test/CMakeLists.txt",
        "roboplan_rrt/test/CMakeLists.txt",
        "roboplan_toppra/test/CMakeLists.txt",
        "roboplan_cartesian_planning/test/CMakeLists.txt",
    ]:
        source = _read(path)

        assert "find_package(roboplan_example_models REQUIRED)" in source, path
        assert (
            "if(NOT TARGET roboplan_example_models::roboplan_example_models)"
            not in source
        ), path


def test_release_workflow_builds_repaired_wheels_and_uses_trusted_publishing() -> None:
    workflow = _read(".github/workflows/release.yml")

    assert "PACKAGE_NAME: roboplan-dimos" in workflow
    assert "pypa/cibuildwheel@" in workflow
    assert "CIBW_MANYLINUX_X86_64_IMAGE: manylinux_2_28" in workflow
    assert "CIBW_ARCHS_LINUX: x86_64" in workflow
    assert 'CIBW_BUILD: "cp310-* cp311-* cp312-* cp313-* cp314-*"' in workflow
    assert "cp315" not in workflow
    assert "CIBW_ENABLE: cpython-prerelease" not in workflow
    assert 'CIBW_SKIP: "pp* *-musllinux*"' in workflow
    assert "CMAKE_BUILD_PARALLEL_LEVEL=2" in workflow
    assert 'MAKEFLAGS="-j2"' in workflow
    assert 'NINJAFLAGS="-j2"' in workflow
    assert "import roboplan; import roboplan.core" in workflow
    assert "roboplan.toppra" in workflow
    assert "roboplan.cartesian_planning" in workflow
    assert "pypa/gh-action-pypi-publish@release/v1" in workflow
    assert "id-token: write" in workflow
    assert "repository-url: https://test.pypi.org/legacy/" in workflow
    assert "TWINE_PASSWORD" not in workflow
    assert "__token__" not in workflow
