import rclpy
from rclpy.node import Node


class AslRecognition(Node):
    def __init__(self):
        super().__init__('asl_recognition')
        self.get_logger().info('asl_recognition started (stub)')


def main(args=None):
    rclpy.init(args=args)
    node = AslRecognition()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
