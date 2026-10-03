import rclpy
from rclpy.node import Node


class SlamToolbox(Node):
    def __init__(self):
        super().__init__('slam_toolbox')
        self.get_logger().info('slam_toolbox started (stub)')


def main(args=None):
    rclpy.init(args=args)
    node = SlamToolbox()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
