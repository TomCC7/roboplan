install(CODE "
  function(_roboplan_cmeel_patch_rpath file rpath)
    set(_patch_file \"\${file}\")
    if(IS_SYMLINK \"\${_patch_file}\")
      file(READ_SYMLINK \"\${_patch_file}\" _symlink_target)
      if(IS_ABSOLUTE \"\${_symlink_target}\")
        return()
      endif()
      get_filename_component(_symlink_dir \"\${_patch_file}\" DIRECTORY)
      set(_patch_file \"\${_symlink_dir}/\${_symlink_target}\")
    endif()

    if(EXISTS \"\${_patch_file}\")
      execute_process(
        COMMAND chmod u+w \"\${_patch_file}\"
        COMMAND_ERROR_IS_FATAL ANY
      )
      execute_process(
        COMMAND \"${ROBOPLAN_CMEEL_PATCHELF}\" --set-rpath \"\${rpath}\" \"\${_patch_file}\"
        COMMAND_ERROR_IS_FATAL ANY
      )
    endif()
  endfunction()

  file(GLOB_RECURSE _roboplan_cmeel_installed_shared_objects
    \"\$ENV{DESTDIR}\${CMAKE_INSTALL_PREFIX}/*.so\"
    \"\$ENV{DESTDIR}\${CMAKE_INSTALL_PREFIX}/*.so.*\"
  )

  set(_roboplan_cmeel_extensions)
  set(_roboplan_cmeel_libraries)
  foreach(_file IN LISTS _roboplan_cmeel_installed_shared_objects)
    if(_file MATCHES \"/site-packages/roboplan/.+\\\\.so$\")
      list(APPEND _roboplan_cmeel_extensions \"\${_file}\")
    elseif(_file MATCHES \"/lib/lib(filters|roboplan.*|OsqpEigen|osqp|qdldl|toppra)\\\\.so(\\\\..*)?$\")
      list(APPEND _roboplan_cmeel_libraries \"\${_file}\")
    endif()
  endforeach()

  if(BUILD_STANDALONE_PYTHON_BINDINGS AND NOT _roboplan_cmeel_extensions)
    message(FATAL_ERROR \"ROBOPLAN_CMEEL RPATH repair found no Python extensions\")
  endif()

  foreach(_file IN LISTS _roboplan_cmeel_extensions)
    _roboplan_cmeel_patch_rpath(\"\${_file}\" \"\\\$ORIGIN/../../../..\")
  endforeach()

  foreach(_file IN LISTS _roboplan_cmeel_libraries)
    _roboplan_cmeel_patch_rpath(\"\${_file}\" \"\\\$ORIGIN\")
  endforeach()
")
