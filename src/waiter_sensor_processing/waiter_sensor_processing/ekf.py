import rclpy
from rclpy.node import Node


class Ekf(Node):
    def __init__(self):
        super().__init__('ekf')
        self.get_logger().info('ekf started (stub)')


def main(args=None):
    rclpy.init(args=args)
    node = Ekf()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
