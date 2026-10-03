import rclpy
from rclpy.node import Node


class Planner(Node):
    def __init__(self):
        super().__init__('planner')
        self.get_logger().info('planner started (stub)')


def main(args=None):
    rclpy.init(args=args)
    node = Planner()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
