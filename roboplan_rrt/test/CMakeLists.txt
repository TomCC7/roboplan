find_package(GTest REQUIRED)
if(NOT TARGET roboplan_example_models::roboplan_example_models)
  if(TARGET roboplan_example_models)
    add_library(roboplan_example_models::roboplan_example_models ALIAS roboplan_example_models)
  else()
    find_package(roboplan_example_models REQUIRED)
  endif()
endif()

# Build tests
add_executable(test_rrt test_rrt.cpp)
set_property(TARGET test_rrt PROPERTY CXX_STANDARD 20)
target_link_libraries(
  test_rrt
  roboplan_rrt
  roboplan::roboplan
  roboplan_example_models::roboplan_example_models
  GTest::gtest_main
)

# TODO: Define tests as a variable

# If ament_gtest is detected, make the tests visible in ROS 2.
find_package(ament_cmake_gtest QUIET)
if ( ament_cmake_gtest_FOUND )
    ament_add_gtest_test(test_rrt)
else()
    include(GoogleTest)
    gtest_add_tests(TARGET test_rrt)
endif()
