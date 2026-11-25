cmake_minimum_required(VERSION 3.8)
project(waiter_slam)

find_package(ament_cmake REQUIRED)

# Copies the launch and config folders to install/waiter_slam/share/waiter_slam/
install(DIRECTORY launch config DESTINATION share/${PROJECT_NAME})

ament_package()