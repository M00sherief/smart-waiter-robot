import rclpy
from rclpy.node import Node


class ImuData(Node):
    def __init__(self):
        super().__init__('imu_data')
        self.get_logger().info('imu_data started (stub)')


def main(args=None):
    rclpy.init(args=args)
    node = ImuData()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
