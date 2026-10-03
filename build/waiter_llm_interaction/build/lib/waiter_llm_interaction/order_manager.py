import rclpy
from rclpy.node import Node


class OrderManager(Node):
    def __init__(self):
        super().__init__('order_manager')
        self.get_logger().info('order_manager started (stub)')


def main(args=None):
    rclpy.init(args=args)
    node = OrderManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
