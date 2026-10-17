cmake_minimum_required(VERSION 3.8)
project(waiter_hardware)

find_package(ament_cmake REQUIRED)
find_package(hardware_interface REQUIRED)
find_package(pluginlib REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_lifecycle REQUIRED)
find_package(sensor_msgs REQUIRED)

add_library(waiter_hardware SHARED src/waiter_hardware.cpp)
target_compile_features(waiter_hardware PUBLIC cxx_std_17)
ament_target_dependencies(waiter_hardware
  hardware_interface pluginlib rclcpp rclcpp_lifecycle sensor_msgs)

pluginlib_export_plugin_description_file(hardware_interface waiter_hardware.xml)

install(TARGETS waiter_hardware DESTINATION lib)

ament_package()
