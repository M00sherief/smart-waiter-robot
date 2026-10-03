import rclpy
from rclpy.node import Node


class AppBridge(Node):
    def __init__(self):
        super().__init__('app_bridge')
        self.get_logger().info('app_bridge started (stub)')


def main(args=None):
    rclpy.init(args=args)
    node = AppBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
