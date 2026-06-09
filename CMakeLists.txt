cmake_minimum_required(VERSION 3.22)
project(roboplan VERSION 0.4.0)

option(ROBOPLAN_CMEEL "Build RoboPlan with cmeel packaging conventions" OFF)
option(
  BUILD_STANDALONE_PYTHON_BINDINGS
  "Build only Python bindings against pre-installed RoboPlan native packages"
  OFF
)

if(SKBUILD)
  find_package(Python COMPONENTS Interpreter REQUIRED)
  execute_process(
    COMMAND
      "${Python_EXECUTABLE}"
      -c
      "import pathlib, sysconfig; prefix = pathlib.Path(sysconfig.get_path('purelib')) / 'cmeel.prefix'; print(prefix if prefix.exists() else '')"
    OUTPUT_VARIABLE ROBOPLAN_CMEEL_PREFIX
    OUTPUT_STRIP_TRAILING_WHITESPACE
  )
  if(ROBOPLAN_CMEEL_PREFIX)
    list(PREPEND CMAKE_PREFIX_PATH "${ROBOPLAN_CMEEL_PREFIX}")
  endif()
endif()

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

  add_subdirectory(roboplan_example_models/bindings)
  add_subdirectory(roboplan/bindings)
  add_subdirectory(roboplan_simple_ik/bindings)
  add_subdirectory(roboplan_oink/bindings)
  add_subdirectory(roboplan_rrt/bindings)
  add_subdirectory(roboplan_toppra/bindings)
else()
  add_subdirectory(roboplan_example_models)
  add_subdirectory(roboplan)
  add_subdirectory(roboplan_simple_ik)
  add_subdirectory(roboplan_oink)
  add_subdirectory(roboplan_rrt)
  add_subdirectory(roboplan_toppra)
endif()

if(SKBUILD)
  if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    find_program(ROBOPLAN_UNIFIED_PATCHELF patchelf REQUIRED)
  endif()

  foreach(target IN ITEMS
      roboplan_example_models
      roboplan
      filters
      roboplan_simple_ik
      roboplan_oink
      roboplan_rrt
      roboplan_toppra)
    if(TARGET ${target})
      set_property(TARGET ${target} PROPERTY INSTALL_RPATH "$ORIGIN")
    endif()
  endforeach()

  foreach(target IN ITEMS
      _example_models_ext
      _core_ext
      _filters_ext
      _simple_ik_ext
      _optimal_ik_ext
      _rrt_ext
      _toppra_ext)
    if(TARGET ${target})
      set_property(TARGET ${target} PROPERTY INSTALL_RPATH "$ORIGIN/../../lib")
    endif()
  endforeach()

  foreach(library IN ITEMS
      OsqpEigen
      boost_atomic
      boost_filesystem
      boost_serialization
      boost_system
      coal
      console_bridge
      gz-math
      gz-utils
      octomap
      octomath
      osqp
      pinocchio_collision
      pinocchio_default
      pinocchio_extra
      pinocchio_parsers
      qdldl
      qhull_r
      sdformat
      tinyxml2
      toppra
      urdfdom_model
      urdfdom_sensor
      urdfdom_world
      yaml-cpp)
    find_library(ROBOPLAN_UNIFIED_${library}_LIBRARY NAMES ${library})
    if(ROBOPLAN_UNIFIED_${library}_LIBRARY)
      install(FILES "${ROBOPLAN_UNIFIED_${library}_LIBRARY}" DESTINATION lib)
      file(REAL_PATH "${ROBOPLAN_UNIFIED_${library}_LIBRARY}" ROBOPLAN_UNIFIED_${library}_REAL_LIBRARY)
      install(FILES "${ROBOPLAN_UNIFIED_${library}_REAL_LIBRARY}" DESTINATION lib)
    endif()
  endforeach()

  foreach(library IN ITEMS
      libassimp.so.6
      libboost_atomic.so.1.90.0
      libboost_filesystem.so.1.88.0
      libboost_filesystem.so.1.90.0
      libboost_serialization.so.1.88.0
      libboost_serialization.so.1.90.0
      libboost_system.so.1.88.0
      libconsole_bridge.so.1.0
      libgz-math.so.9
      libgz-utils.so.4
      liboctomap.so.1.10
      liboctomath.so.1.10
      libqhull_r.so.8.0
      libsdformat.so.16
      libtinyxml2.so.11
      liburdfdom_model.so.6
      liburdfdom_sensor.so.6
      liburdfdom_world.so.6
      libyaml-cpp.so.0.8)
    find_file(ROBOPLAN_UNIFIED_${library}_FILE NAMES ${library}
      PATHS "$ENV{CONDA_PREFIX}/lib" "${CMAKE_PREFIX_PATH}/lib" "${ROBOPLAN_CMEEL_PREFIX}/lib"
      NO_DEFAULT_PATH)
    if(ROBOPLAN_UNIFIED_${library}_FILE)
      install(FILES "${ROBOPLAN_UNIFIED_${library}_FILE}" DESTINATION lib)
      file(REAL_PATH "${ROBOPLAN_UNIFIED_${library}_FILE}" ROBOPLAN_UNIFIED_${library}_REAL_FILE)
      install(FILES "${ROBOPLAN_UNIFIED_${library}_REAL_FILE}" DESTINATION lib)
    endif()
  endforeach()

  find_library(ROBOPLAN_UNIFIED_YAML_CPP_LIBRARY NAMES yaml-cpp)
  if(ROBOPLAN_UNIFIED_YAML_CPP_LIBRARY)
    install(FILES "${ROBOPLAN_UNIFIED_YAML_CPP_LIBRARY}" DESTINATION lib RENAME libyaml-cpp.so.0.8)
  endif()

  if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    add_subdirectory(cmake/roboplan_unified_repair)
  endif()
endif()

if(ROBOPLAN_CMEEL AND CMAKE_SYSTEM_NAME STREQUAL "Linux")
  find_program(ROBOPLAN_CMEEL_PATCHELF patchelf REQUIRED)
  foreach(library IN ITEMS
      OsqpEigen
      osqp
      qdldl
      toppra)
    find_library(ROBOPLAN_CMEEL_${library}_LIBRARY NAMES ${library})
    if(ROBOPLAN_CMEEL_${library}_LIBRARY)
      install(FILES "${ROBOPLAN_CMEEL_${library}_LIBRARY}" DESTINATION lib)
      file(REAL_PATH "${ROBOPLAN_CMEEL_${library}_LIBRARY}" ROBOPLAN_CMEEL_${library}_REAL_LIBRARY)
      install(FILES "${ROBOPLAN_CMEEL_${library}_REAL_LIBRARY}" DESTINATION lib)
    endif()
  endforeach()

  foreach(library IN ITEMS
      libOsqpEigen.so.0.11.0)
    find_file(ROBOPLAN_CMEEL_${library}_FILE NAMES ${library}
      PATHS "$ENV{CONDA_PREFIX}/lib" "${CMAKE_PREFIX_PATH}/lib"
      NO_DEFAULT_PATH)
    if(ROBOPLAN_CMEEL_${library}_FILE)
      install(FILES "${ROBOPLAN_CMEEL_${library}_FILE}" DESTINATION lib)
      file(REAL_PATH "${ROBOPLAN_CMEEL_${library}_FILE}" ROBOPLAN_CMEEL_${library}_REAL_FILE)
      install(FILES "${ROBOPLAN_CMEEL_${library}_REAL_FILE}" DESTINATION lib)
    endif()
  endforeach()

  add_subdirectory(cmake/roboplan_cmeel_repair)
endif()
