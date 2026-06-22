function(roboplan_configure_scikit_build_prefix)
  find_package(Python COMPONENTS Interpreter REQUIRED)
  execute_process(
    COMMAND
      "${Python_EXECUTABLE}"
      -c
      "import pathlib, sysconfig; prefix = pathlib.Path(sysconfig.get_path('purelib')) / 'cmeel.prefix'; print(prefix if prefix.exists() else '')"
    OUTPUT_VARIABLE ROBOPLAN_CMEEL_PREFIX
    OUTPUT_STRIP_TRAILING_WHITESPACE
  )
  set(ROBOPLAN_CMEEL_PREFIX "${ROBOPLAN_CMEEL_PREFIX}" PARENT_SCOPE)
  if(ROBOPLAN_CMEEL_PREFIX)
    list(PREPEND CMAKE_PREFIX_PATH "${ROBOPLAN_CMEEL_PREFIX}")
    set(CMAKE_PREFIX_PATH "${CMAKE_PREFIX_PATH}" PARENT_SCOPE)
  endif()
endfunction()

function(roboplan_ensure_hpp_fcl_target)
  find_package(hpp-fcl CONFIG QUIET)
  if(TARGET hpp-fcl::hpp-fcl)
    return()
  endif()

  find_path(ROBOPLAN_HPP_FCL_INCLUDE_DIR
    NAMES hpp/fcl/fwd.hh
    HINTS "/opt/ros/$ENV{ROS_DISTRO}/include"
  )
  find_library(ROBOPLAN_HPP_FCL_LIBRARY
    NAMES hpp-fcl
    HINTS
      "/opt/ros/$ENV{ROS_DISTRO}/lib/${CMAKE_LIBRARY_ARCHITECTURE}"
      "/opt/ros/$ENV{ROS_DISTRO}/lib"
  )
  if(ROBOPLAN_HPP_FCL_INCLUDE_DIR AND ROBOPLAN_HPP_FCL_LIBRARY)
    add_library(hpp-fcl::hpp-fcl SHARED IMPORTED GLOBAL)
    set_target_properties(hpp-fcl::hpp-fcl PROPERTIES
      IMPORTED_LOCATION "${ROBOPLAN_HPP_FCL_LIBRARY}"
      INTERFACE_INCLUDE_DIRECTORIES "${ROBOPLAN_HPP_FCL_INCLUDE_DIR}"
    )
  endif()
endfunction()

function(roboplan_register_build_tree_package package_name)
  set(options)
  set(one_value_args)
  set(multi_value_args ALIASES)
  cmake_parse_arguments(ARG "${options}" "${one_value_args}" "${multi_value_args}" ${ARGN})

  set(_package_dir "${PROJECT_BINARY_DIR}/packaging-python-package-configs/${package_name}")
  file(MAKE_DIRECTORY "${_package_dir}")
  set(_config_file "${_package_dir}/${package_name}Config.cmake")
  file(WRITE "${_config_file}" "# Generated for the packaging/python build tree.\n")

  foreach(alias_pair IN LISTS ARG_ALIASES)
    string(REPLACE "=" ";" alias_parts "${alias_pair}")
    list(GET alias_parts 0 namespaced_target)
    list(GET alias_parts 1 local_target)
    file(APPEND "${_config_file}"
      "if(TARGET ${local_target} AND NOT TARGET ${namespaced_target})\n"
      "  add_library(${namespaced_target} ALIAS ${local_target})\n"
      "endif()\n"
    )
  endforeach()

  set(${package_name}_DIR "${_package_dir}" CACHE PATH "Build-tree ${package_name} package config" FORCE)
endfunction()

function(roboplan_register_build_tree_packages)
  roboplan_register_build_tree_package(roboplan_example_models
    ALIASES roboplan_example_models::roboplan_example_models=roboplan_example_models)
  roboplan_register_build_tree_package(roboplan
    ALIASES roboplan::roboplan=roboplan roboplan::filters=filters)
  roboplan_register_build_tree_package(roboplan_simple_ik
    ALIASES roboplan_simple_ik::roboplan_simple_ik=roboplan_simple_ik)
  roboplan_register_build_tree_package(roboplan_oink
    ALIASES roboplan_oink::roboplan_oink=roboplan_oink)
  roboplan_register_build_tree_package(roboplan_rrt
    ALIASES roboplan_rrt::roboplan_rrt=roboplan_rrt)
  roboplan_register_build_tree_package(roboplan_toppra
    ALIASES roboplan_toppra::roboplan_toppra=roboplan_toppra)
endfunction()

function(roboplan_configure_unified_python_wheel)
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
    configure_file(
      "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/repair_unified_rpaths.cmake.in"
      "${PROJECT_BINARY_DIR}/roboplan_repair_unified_rpaths.cmake"
      @ONLY
    )
    install(SCRIPT "${PROJECT_BINARY_DIR}/roboplan_repair_unified_rpaths.cmake")
  endif()
endfunction()

function(roboplan_configure_cmeel_package)
  if(NOT CMAKE_SYSTEM_NAME STREQUAL "Linux")
    return()
  endif()

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

  configure_file(
    "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/repair_cmeel_rpaths.cmake.in"
    "${PROJECT_BINARY_DIR}/roboplan_repair_cmeel_rpaths.cmake"
    @ONLY
  )
  install(SCRIPT "${PROJECT_BINARY_DIR}/roboplan_repair_cmeel_rpaths.cmake")
endfunction()
