import rclpy
from rclpy.node import Node


class SpeechToText(Node):
    def __init__(self):
        super().__init__('speech_to_text')
        self.get_logger().info('speech_to_text started (stub)')


def main(args=None):
    rclpy.init(args=args)
    node = SpeechToText()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
