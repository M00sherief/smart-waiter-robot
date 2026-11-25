import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    slam_share = get_package_share_directory("waiter_slam")
    slam_toolbox_share = get_package_share_directory("slam_toolbox")

    params_file = LaunchConfiguration("slam_params_file")
    use_sim_time = LaunchConfiguration("use_sim_time")

    # Uses slam_toolbox's own online async launch file (works on Humble and Jazzy).
    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(slam_toolbox_share, "launch", "online_async_launch.py")
        ),
        launch_arguments={
            "slam_params_file": params_file,
            "use_sim_time": use_sim_time,
        }.items(),
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            "slam_params_file",
            default_value=os.path.join(slam_share, "config", "slam_toolbox_params.yaml"),
            description="Full path to the slam_toolbox parameters file",
        ),
        DeclareLaunchArgument("use_sim_time", default_value="false"),
        slam,
    ])