import rclpy
from rclpy.node import Node


class Camera(Node):
    def __init__(self):
        super().__init__('camera')
        self.get_logger().info('camera started (stub)')


def main(args=None):
    rclpy.init(args=args)
    node = Camera()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
