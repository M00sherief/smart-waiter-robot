import rclpy
from rclpy.node import Node
from waiter_interfaces.msg import OrderNew


class VoiceAssistant(Node):
    def __init__(self):
        super().__init__('voice_assistant')
        self.order_pub = self.create_publisher(OrderNew, '/order/new', 10)
        self.demo_timer = self.create_timer(10.0, self.send_demo_order)
        self.get_logger().info('voice_assistant started (fake order in 10 s)')

    def send_demo_order(self):
        self.demo_timer.cancel()
        msg = OrderNew()
        msg.order_id = 'order_001'
        msg.table_id = 5
        msg.items = ['coffee', 'water']
        msg.language = 'en'
        self.order_pub.publish(msg)
        self.get_logger().info('Published demo order_001 for table 5')


def main(args=None):
    rclpy.init(args=args)
    node = VoiceAssistant()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()