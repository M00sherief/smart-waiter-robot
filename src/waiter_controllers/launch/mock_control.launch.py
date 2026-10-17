import os
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    desc_share = get_package_share_directory("waiter_description")
    ctrl_share = get_package_share_directory("waiter_controllers")

    xacro_file = os.path.join(desc_share, "urdf", "waiter.urdf.xacro")
    controllers_yaml = os.path.join(ctrl_share, "config", "waiter_controllers.yaml")
    rviz_config = os.path.join(desc_share, "rviz", "view3d.rviz")

    robot_description = ParameterValue(Command(["xacro ", xacro_file]), value_type=str)

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description}],
    )

    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[{"robot_description": robot_description}, controllers_yaml],
        output="screen",
    )

    spawners = [
        Node(package="controller_manager", executable="spawner", arguments=[name])
        for name in (
            "joint_state_broadcaster",
            "diff_drive_controller",
            "imu_sensor_broadcaster",
        )
    ]

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        arguments=["-d", rviz_config],
    )

    return LaunchDescription([robot_state_publisher, controller_manager, *spawners, rviz])