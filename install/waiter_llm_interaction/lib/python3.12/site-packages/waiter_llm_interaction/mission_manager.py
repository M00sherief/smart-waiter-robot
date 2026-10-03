import rclpy
from rclpy.node import Node


class MissionManager(Node):
    def __init__(self):
        super().__init__('mission_manager')
        self.get_logger().info('mission_manager started (stub)')


def main(args=None):
    rclpy.init(args=args)
    node = MissionManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
