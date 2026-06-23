cmake_minimum_required(VERSION 3.22)
project(roboplan VERSION 0.4.0)

get_filename_component(ROBOPLAN_REPOSITORY_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../.." ABSOLUTE)

option(ROBOPLAN_CMEEL "Build RoboPlan with cmeel packaging conventions" OFF)
option(
  BUILD_STANDALONE_PYTHON_BINDINGS
  "Build only Python bindings against pre-installed RoboPlan native packages"
  OFF
)

# The default path builds the unified PyPI wheel in one CMake tree. The
# standalone path is used by the cmeel split Python package, which builds only
# bindings against the already-installed native libroboplan package.

include(cmake/roboplan_python_packaging.cmake)

if(SKBUILD)
  roboplan_configure_scikit_build_prefix()
endif()

if(BUILD_STANDALONE_PYTHON_BINDINGS)
  find_package(roboplan_example_models REQUIRED CONFIG)
  find_package(roboplan REQUIRED CONFIG)
  find_package(roboplan_simple_ik REQUIRED CONFIG)
  find_package(roboplan_oink REQUIRED CONFIG)
  find_package(roboplan_rrt REQUIRED CONFIG)
  find_package(roboplan_toppra REQUIRED CONFIG)
  find_package(roboplan_cartesian_planning REQUIRED CONFIG)

  add_library(roboplan_example_models ALIAS roboplan_example_models::roboplan_example_models)
  add_library(roboplan ALIAS roboplan::roboplan)
  add_library(filters ALIAS roboplan::filters)
  add_library(roboplan_simple_ik ALIAS roboplan_simple_ik::roboplan_simple_ik)
  add_library(roboplan_oink ALIAS roboplan_oink::roboplan_oink)
  add_library(roboplan_rrt ALIAS roboplan_rrt::roboplan_rrt)
  add_library(roboplan_toppra ALIAS roboplan_toppra::roboplan_toppra)
  add_library(roboplan_cartesian_planning ALIAS roboplan_cartesian_planning::roboplan_cartesian_planning)

  add_subdirectory("${ROBOPLAN_REPOSITORY_ROOT}/roboplan_example_models/bindings" "bindings/roboplan_example_models")
  add_subdirectory("${ROBOPLAN_REPOSITORY_ROOT}/roboplan/bindings" "bindings/roboplan")
  add_subdirectory("${ROBOPLAN_REPOSITORY_ROOT}/roboplan_simple_ik/bindings" "bindings/roboplan_simple_ik")
  add_subdirectory("${ROBOPLAN_REPOSITORY_ROOT}/roboplan_oink/bindings" "bindings/roboplan_oink")
  add_subdirectory("${ROBOPLAN_REPOSITORY_ROOT}/roboplan_rrt/bindings" "bindings/roboplan_rrt")
  add_subdirectory("${ROBOPLAN_REPOSITORY_ROOT}/roboplan_toppra/bindings" "bindings/roboplan_toppra")
  add_subdirectory("${ROBOPLAN_REPOSITORY_ROOT}/roboplan_cartesian_planning/bindings" "bindings/roboplan_cartesian_planning")
else()
  roboplan_register_build_tree_packages()

  add_subdirectory("${ROBOPLAN_REPOSITORY_ROOT}/roboplan_example_models" "roboplan_example_models")
  add_subdirectory("${ROBOPLAN_REPOSITORY_ROOT}/roboplan" "roboplan")
  add_subdirectory("${ROBOPLAN_REPOSITORY_ROOT}/roboplan_simple_ik" "roboplan_simple_ik")
  add_subdirectory("${ROBOPLAN_REPOSITORY_ROOT}/roboplan_oink" "roboplan_oink")
  add_subdirectory("${ROBOPLAN_REPOSITORY_ROOT}/roboplan_rrt" "roboplan_rrt")
  add_subdirectory("${ROBOPLAN_REPOSITORY_ROOT}/roboplan_toppra" "roboplan_toppra")
  add_subdirectory("${ROBOPLAN_REPOSITORY_ROOT}/roboplan_cartesian_planning" "roboplan_cartesian_planning")
endif()

if(SKBUILD)
  roboplan_configure_unified_python_wheel()
endif()

if(ROBOPLAN_CMEEL)
  roboplan_configure_cmeel_package()
endif()
