import rclpy
from rclpy.node import Node


class AudioIo(Node):
    def __init__(self):
        super().__init__('audio_io')
        self.get_logger().info('audio_io started (stub)')


def main(args=None):
    rclpy.init(args=args)
    node = AudioIo()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
