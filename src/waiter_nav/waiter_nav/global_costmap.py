import rclpy
from rclpy.node import Node


class GlobalCostmap(Node):
    def __init__(self):
        super().__init__('global_costmap')
        self.get_logger().info('global_costmap started (stub)')


def main(args=None):
    rclpy.init(args=args)
    node = GlobalCostmap()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
