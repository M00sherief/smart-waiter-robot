from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    nodes = [
        ('waiter_hal', 'audio_io'),
        ('waiter_external_functionalities', 'app_bridge'),
        ('waiter_llm_interaction', 'order_manager'),
        ('waiter_llm_interaction', 'mission_manager'),
        ('waiter_llm_interaction', 'voice_assistant'),
        ('waiter_llm_interaction', 'asl_recognition'),
    ]
    return LaunchDescription(
        [Node(package=p, executable=e) for p, e in nodes]
    )
