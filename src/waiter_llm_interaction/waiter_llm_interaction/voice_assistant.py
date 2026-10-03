import rclpy
from rclpy.node import Node


class VoiceAssistant(Node):
    def __init__(self):
        super().__init__('voice_assistant')
        self.get_logger().info('voice_assistant started (stub)')


def main(args=None):
    rclpy.init(args=args)
    node = VoiceAssistant()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
