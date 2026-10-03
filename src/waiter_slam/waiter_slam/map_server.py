import rclpy
from rclpy.node import Node


class MapServer(Node):
    def __init__(self):
        super().__init__('map_server')
        self.get_logger().info('map_server started (stub)')


def main(args=None):
    rclpy.init(args=args)
    node = MapServer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
