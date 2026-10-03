import rclpy
from rclpy.node import Node


class Llm(Node):
    def __init__(self):
        super().__init__('llm')
        self.get_logger().info('llm started (stub)')


def main(args=None):
    rclpy.init(args=args)
    node = Llm()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
