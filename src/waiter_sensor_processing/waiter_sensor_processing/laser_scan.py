import rclpy
from rclpy.node import Node


class LaserScan(Node):
    def __init__(self):
        super().__init__('laser_scan')
        self.get_logger().info('laser_scan started (stub)')


def main(args=None):
    rclpy.init(args=args)
    node = LaserScan()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
