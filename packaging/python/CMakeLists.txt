cmake_minimum_required(VERSION 3.22)
project(roboplan VERSION 0.4.0)

get_filename_component(ROBOPLAN_REPOSITORY_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../.." ABSOLUTE)

option(ROBOPLAN_CMEEL "Build RoboPlan with cmeel packaging conventions" OFF)
option(
  BUILD_STANDALONE_PYTHON_BINDINGS
  "Build only Python bindings against pre-installed RoboPlan native packages"
  OFF
)

include(cmake/roboplan_python_packaging.cmake)

if(SKBUILD)
  roboplan_configure_scikit_build_prefix()
endif()

roboplan_ensure_hpp_fcl_target()

if(BUILD_STANDALONE_PYTHON_BINDINGS)
  find_package(roboplan_example_models REQUIRED CONFIG)
  find_package(roboplan REQUIRED CONFIG)
  find_package(roboplan_simple_ik REQUIRED CONFIG)
  find_package(roboplan_oink REQUIRED CONFIG)
  find_package(roboplan_rrt REQUIRED CONFIG)
  find_package(roboplan_toppra REQUIRED CONFIG)

  if(TARGET roboplan_example_models::roboplan_example_models AND NOT TARGET roboplan_example_models)
    add_library(roboplan_example_models ALIAS roboplan_example_models::roboplan_example_models)
  endif()
  if(TARGET roboplan::roboplan AND NOT TARGET roboplan)
    add_library(roboplan ALIAS roboplan::roboplan)
  endif()
  if(TARGET roboplan::filters AND NOT TARGET filters)
    add_library(filters ALIAS roboplan::filters)
  endif()
  if(TARGET roboplan_simple_ik::roboplan_simple_ik AND NOT TARGET roboplan_simple_ik)
    add_library(roboplan_simple_ik ALIAS roboplan_simple_ik::roboplan_simple_ik)
  endif()
  if(TARGET roboplan_oink::roboplan_oink AND NOT TARGET roboplan_oink)
    add_library(roboplan_oink ALIAS roboplan_oink::roboplan_oink)
  endif()
  if(TARGET roboplan_rrt::roboplan_rrt AND NOT TARGET roboplan_rrt)
    add_library(roboplan_rrt ALIAS roboplan_rrt::roboplan_rrt)
  endif()
  if(TARGET roboplan_toppra::roboplan_toppra AND NOT TARGET roboplan_toppra)
    add_library(roboplan_toppra ALIAS roboplan_toppra::roboplan_toppra)
  endif()

  add_subdirectory("${ROBOPLAN_REPOSITORY_ROOT}/roboplan_example_models/bindings" "bindings/roboplan_example_models")
  add_subdirectory("${ROBOPLAN_REPOSITORY_ROOT}/roboplan/bindings" "bindings/roboplan")
  add_subdirectory("${ROBOPLAN_REPOSITORY_ROOT}/roboplan_simple_ik/bindings" "bindings/roboplan_simple_ik")
  add_subdirectory("${ROBOPLAN_REPOSITORY_ROOT}/roboplan_oink/bindings" "bindings/roboplan_oink")
  add_subdirectory("${ROBOPLAN_REPOSITORY_ROOT}/roboplan_rrt/bindings" "bindings/roboplan_rrt")
  add_subdirectory("${ROBOPLAN_REPOSITORY_ROOT}/roboplan_toppra/bindings" "bindings/roboplan_toppra")
else()
  roboplan_register_build_tree_packages()

  add_subdirectory("${ROBOPLAN_REPOSITORY_ROOT}/roboplan_example_models" "roboplan_example_models")
  add_subdirectory("${ROBOPLAN_REPOSITORY_ROOT}/roboplan" "roboplan")
  add_subdirectory("${ROBOPLAN_REPOSITORY_ROOT}/roboplan_simple_ik" "roboplan_simple_ik")
  add_subdirectory("${ROBOPLAN_REPOSITORY_ROOT}/roboplan_oink" "roboplan_oink")
  add_subdirectory("${ROBOPLAN_REPOSITORY_ROOT}/roboplan_rrt" "roboplan_rrt")
  add_subdirectory("${ROBOPLAN_REPOSITORY_ROOT}/roboplan_toppra" "roboplan_toppra")
endif()

if(SKBUILD)
  roboplan_configure_unified_python_wheel()
endif()

if(ROBOPLAN_CMEEL)
  roboplan_configure_cmeel_package()
endif()
