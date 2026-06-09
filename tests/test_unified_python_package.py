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

    assert pyproject.exists(), "root pyproject.toml is required for the unified roboplan wheel"

    data = cast(dict[str, object], tomllib.loads(pyproject.read_text(encoding="utf-8")))
    build_system = cast(dict[str, object], data["build-system"])
    build_requires = cast(list[str], build_system["requires"])
    project = cast(dict[str, object], data["project"])

    assert project["name"] == "roboplan"
    assert project["version"] == "0.4.0"
    assert project["requires-python"] == ">=3.10"
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
    defines = cast(dict[str, str], cmake["define"])
    assert defines["CMAKE_POLICY_VERSION_MINIMUM"] == "3.5"
    assert defines["CMAKE_INSTALL_RPATH"] == "$ORIGIN/../../lib"
    assert defines["CMAKE_INSTALL_RPATH_USE_LINK_PATH"] == "FALSE"

    sdist = cast(dict[str, list[str]], scikit_build["sdist"])
    assert ".omo/**" in sdist["exclude"]


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
    assert lib_cmeel["source"] == "../../.."
    assert lib_cmeel["has-sitelib"] is False
    assert "-DROBOPLAN_CMEEL=ON" in lib_args
    assert "-DBUILD_PYTHON_BINDINGS=OFF" in lib_args

    py_build = cast(dict[str, object], roboplan["build-system"])
    py_project = cast(dict[str, object], roboplan["project"])
    py_tool = cast(dict[str, object], roboplan["tool"])
    py_cmeel = cast(dict[str, object], py_tool["cmeel"])
    py_args = cast(list[str], py_cmeel["configure-args"])
    py_dependencies = cast(list[str], py_project["dependencies"])

    assert py_build["build-backend"] == "cmeel"
    assert py_project["name"] == "roboplan"
    assert py_cmeel["source"] == "../../.."
    assert "libroboplan == 0.4.0" in py_dependencies
    assert "pin == 4.0.0" in py_dependencies
    assert "-DROBOPLAN_CMEEL=ON" in py_args
    assert "-DBUILD_STANDALONE_PYTHON_BINDINGS=ON" in py_args
    assert "-DGENERATE_PYTHON_STUBS=OFF" in py_args


def test_root_cmake_superbuild_adds_all_python_binding_packages_in_order() -> None:
    cmake = ROOT / "CMakeLists.txt"

    assert cmake.exists(), "root CMakeLists.txt is required for the unified roboplan wheel"

    source = cmake.read_text(encoding="utf-8")
    package_order = re.findall(r"add_subdirectory\((roboplan(?:_[a-z_]+)?)\)", source)

    repair_source = _read("cmake/roboplan_unified_repair/CMakeLists.txt")

    assert "add_subdirectory(cmake/roboplan_unified_repair)" in source
    assert "cmeel.prefix" in source
    assert "list(PREPEND CMAKE_PREFIX_PATH" in source
    assert "${ROBOPLAN_CMEEL_PREFIX}/lib" in source
    assert "RENAME libyaml-cpp.so.0.8" in source
    assert "boost_atomic" in source
    assert "libboost_atomic.so.1.90.0" in source
    assert "libboost_filesystem.so.1.90.0" in source
    assert "liburdfdom_world.so.6" in source
    assert "--set-rpath" in repair_source
    assert "$ORIGIN/../../lib" in source
    assert package_order == [
        "roboplan_example_models",
        "roboplan",
        "roboplan_simple_ik",
        "roboplan_oink",
        "roboplan_rrt",
        "roboplan_toppra",
    ]


def test_dependent_packages_can_use_in_tree_core_target() -> None:
    for path in [
        "roboplan_simple_ik/CMakeLists.txt",
        "roboplan_oink/CMakeLists.txt",
        "roboplan_rrt/CMakeLists.txt",
        "roboplan_toppra/CMakeLists.txt",
    ]:
        source = _read(path)

        assert "if(NOT TARGET roboplan::roboplan)" in source, path
        assert "find_package(roboplan REQUIRED)" in source, path
