import rclpy
from rclpy.node import Node


class TextToSpeech(Node):
    def __init__(self):
        super().__init__('text_to_speech')
        self.get_logger().info('text_to_speech started (stub)')


def main(args=None):
    rclpy.init(args=args)
    node = TextToSpeech()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
