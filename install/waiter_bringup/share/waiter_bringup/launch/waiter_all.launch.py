from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    nodes = [
        ('waiter_hal', 'arduino_bridge'),
        ('waiter_hal', 'camera'),
        ('waiter_hal', 'battery_monitor'),
        ('waiter_hal', 'audio_io'),
        ('waiter_hal', 'imu_data'),
        ('waiter_sensor_processing', 'ekf'),
        ('waiter_sensor_processing', 'laser_scan'),
        ('waiter_slam', 'amcl'),
        ('waiter_slam', 'slam_toolbox'),
        ('waiter_slam', 'map_server'),
        ('waiter_nav', 'local_costmap'),
        ('waiter_nav', 'global_costmap'),
        ('waiter_nav', 'planner'),
        ('waiter_nav', 'controller'),
        ('waiter_nav', 'bt_navigator'),
        ('waiter_external_functionalities', 'app_bridge'),
        ('waiter_external_functionalities', 'power_manager'),
        ('waiter_llm_interaction', 'order_manager'),
        ('waiter_llm_interaction', 'llm'),
        ('waiter_llm_interaction', 'speech_to_text'),
        ('waiter_llm_interaction', 'text_to_speech'),
        ('waiter_llm_interaction', 'mission_manager'),
    ]
    return LaunchDescription(
        [Node(package=p, executable=e) for p, e in nodes]
    )
