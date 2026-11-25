import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    ctrl_share = get_package_share_directory("waiter_controllers")
    slam_share = get_package_share_directory("waiter_slam")

    # robot_state_publisher + ros2_control (waiter_hardware) + controllers + RViz
    robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ctrl_share, "launch", "teleop_phase1.launch.py")
        ),
        launch_arguments={
            "use_mock": LaunchConfiguration("use_mock"),
            "serial_port": LaunchConfiguration("serial_port"),
            "baud_rate": LaunchConfiguration("baud_rate"),
            "use_rviz": LaunchConfiguration("use_rviz"),
        }.items(),
    )

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(slam_share, "launch", "slam.launch.py")
        )
    )

    return LaunchDescription([
        DeclareLaunchArgument("use_mock", default_value="false"),
        DeclareLaunchArgument("serial_port", default_value="/dev/ttyACM0"),
        DeclareLaunchArgument("baud_rate", default_value="115200"),
        DeclareLaunchArgument("use_rviz", default_value="true"),
        robot,
        slam,
    ])