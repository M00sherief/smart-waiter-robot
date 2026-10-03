import rclpy
from rclpy.node import Node


class Amcl(Node):
    def __init__(self):
        super().__init__('amcl')
        self.get_logger().info('amcl started (stub)')


def main(args=None):
    rclpy.init(args=args)
    node = Amcl()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
