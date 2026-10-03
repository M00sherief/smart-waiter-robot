import rclpy
from rclpy.node import Node
from waiter_interfaces.msg import OrderNew, OrderStatus


class OrderManager(Node):
    def __init__(self):
        super().__init__('order_manager')
        self.status_pub = self.create_publisher(OrderStatus, '/order/status', 10)
        self.create_subscription(OrderNew, '/order/new', self.on_new_order, 10)
        self.get_logger().info('order_manager started')

    def publish_status(self, order_id, status):
        msg = OrderStatus()
        msg.order_id = order_id
        msg.status = status
        self.status_pub.publish(msg)
        self.get_logger().info(f'Order {order_id} -> status {status}')

    def on_new_order(self, msg):
        self.get_logger().info(
            f'New order {msg.order_id}, table {msg.table_id}, items {list(msg.items)}')
        self.publish_status(msg.order_id, OrderStatus.PREPARING)
        timer = self.create_timer(5.0, lambda: self.on_ready(msg.order_id, timer))

    def on_ready(self, order_id, timer):
        timer.cancel()
        self.destroy_timer(timer)
        self.publish_status(order_id, OrderStatus.READY)


def main(args=None):
    rclpy.init(args=args)
    node = OrderManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()