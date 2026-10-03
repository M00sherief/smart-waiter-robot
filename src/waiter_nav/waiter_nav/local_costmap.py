import rclpy
from rclpy.node import Node


class LocalCostmap(Node):
    def __init__(self):
        super().__init__('local_costmap')
        self.get_logger().info('local_costmap started (stub)')


def main(args=None):
    rclpy.init(args=args)
    node = LocalCostmap()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
