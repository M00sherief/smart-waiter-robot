import rclpy
from rclpy.node import Node


class BatteryMonitor(Node):
    def __init__(self):
        super().__init__('battery_monitor')
        self.get_logger().info('battery_monitor started (stub)')


def main(args=None):
    rclpy.init(args=args)
    node = BatteryMonitor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
