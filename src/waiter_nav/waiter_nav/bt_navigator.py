import rclpy
from rclpy.node import Node


class BtNavigator(Node):
    def __init__(self):
        super().__init__('bt_navigator')
        self.get_logger().info('bt_navigator started (stub)')


def main(args=None):
    rclpy.init(args=args)
    node = BtNavigator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
