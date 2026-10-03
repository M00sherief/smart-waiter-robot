import rclpy
from rclpy.node import Node


class PowerManager(Node):
    def __init__(self):
        super().__init__('power_manager')
        self.get_logger().info('power_manager started (stub)')


def main(args=None):
    rclpy.init(args=args)
    node = PowerManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
