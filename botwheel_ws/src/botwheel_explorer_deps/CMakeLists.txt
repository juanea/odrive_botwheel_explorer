cmake_minimum_required(VERSION 3.8)
project(botwheel_explorer_deps)

# Dependency-only meta-package: nothing to compile or install. The dependencies
# are declared in package.xml so rosdep installs them; ament_package() just makes
# this a valid package that colcon can process as a no-op.
find_package(ament_cmake REQUIRED)

ament_package()
