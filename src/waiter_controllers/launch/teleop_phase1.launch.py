import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    desc_share = get_package_share_directory("waiter_description")
    ctrl_share = get_package_share_directory("waiter_controllers")

    xacro_file = os.path.join(desc_share, "urdf", "waiter.urdf.xacro")
    controllers_yaml = os.path.join(ctrl_share, "config", "waiter_controllers.yaml")
    rviz_config = os.path.join(desc_share, "rviz", "view3d.rviz")

    use_mock = LaunchConfiguration("use_mock")
    serial_port = LaunchConfiguration("serial_port")
    baud_rate = LaunchConfiguration("baud_rate")
    use_rviz = LaunchConfiguration("use_rviz")

    robot_description = ParameterValue(
        Command([
            "xacro ", xacro_file,
            " use_mock:=", use_mock,
            " serial_port:=", serial_port,
            " baud_rate:=", baud_rate,
        ]),
        value_type=str,
    )

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
        condition=IfCondition(use_rviz),
    )

    distro = os.environ.get("ROS_DISTRO", "humble")
    if distro == "humble":
        teleop_hint = (
            "Teleop in a NEW terminal:  ros2 run teleop_twist_keyboard teleop_twist_keyboard "
            "--ros-args -r cmd_vel:=/diff_drive_controller/cmd_vel_unstamped"
        )
    else:
        teleop_hint = (
            "Teleop in a NEW terminal:  ros2 run teleop_twist_keyboard teleop_twist_keyboard "
            "--ros-args -p stamped:=true -r cmd_vel:=/diff_drive_controller/cmd_vel"
        )

    return LaunchDescription([
        DeclareLaunchArgument("use_mock", default_value="false",
                              description="true = fake hardware inside ROS, false = real Arduino"),
        DeclareLaunchArgument("serial_port", default_value="/dev/ttyACM0"),
        DeclareLaunchArgument("baud_rate", default_value="115200"),
        DeclareLaunchArgument("use_rviz", default_value="true"),
        LogInfo(msg=teleop_hint),
        robot_state_publisher,
        controller_manager,
        *spawners,
        rviz,
    ])