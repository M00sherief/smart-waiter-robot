import rclpy
from rclpy.node import Node


class Controller(Node):
    def __init__(self):
        super().__init__('controller')
        self.get_logger().info('controller started (stub)')


def main(args=None):
    rclpy.init(args=args)
    node = Controller()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
