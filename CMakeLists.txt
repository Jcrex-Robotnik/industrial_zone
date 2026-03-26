cmake_minimum_required(VERSION 3.8)
project(industrial_zone)

find_package(ament_cmake REQUIRED)

# Install world, launch and model assets
install(DIRECTORY
  launch
  worlds
  models
  config
  maps
  DESTINATION share/${PROJECT_NAME}
)

# Environment hook: adds models/ to GZ_SIM_RESOURCE_PATH on `source install/setup.bash`
ament_environment_hooks("${CMAKE_CURRENT_SOURCE_DIR}/hooks/industrial_zone.dsv.in")

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
