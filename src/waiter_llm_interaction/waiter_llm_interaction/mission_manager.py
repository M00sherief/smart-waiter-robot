import rclpy
from rclpy.node import Node
from waiter_interfaces.msg import AppGoal, MissionStatus, OrderNew, OrderStatus


class MissionManager(Node):
    def __init__(self):
        super().__init__('mission_manager')
        self.tables = {}
        self.status_pub = self.create_publisher(MissionStatus, '/mission/status', 10)
        self.create_subscription(OrderNew, '/order/new', self.on_new_order, 10)
        self.create_subscription(OrderStatus, '/order/status', self.on_order_status, 10)
        self.create_subscription(AppGoal, '/app/goal', self.on_app_goal, 10)
        self.get_logger().info('mission_manager started')

    def publish_state(self, order_id, table_id, state):
        msg = MissionStatus()
        msg.mission_id = order_id
        msg.table_id = table_id
        msg.state = state
        self.status_pub.publish(msg)
        self.get_logger().info(f'Mission {order_id}: state {state}, table {table_id}')

    def on_new_order(self, msg):
        self.tables[msg.order_id] = msg.table_id
        self.get_logger().info(f'Remembered {msg.order_id} -> table {msg.table_id}')

    def on_order_status(self, msg):
        if msg.status == OrderStatus.READY:
            table = self.tables.get(msg.order_id, 0)
            self.publish_state(msg.order_id, table, MissionStatus.DELIVERING)
            timer = self.create_timer(
                5.0, lambda: self.on_arrived(msg.order_id, table, timer))

    def on_arrived(self, order_id, table, timer):
        timer.cancel()
        self.destroy_timer(timer)
        self.publish_state(order_id, table, MissionStatus.AT_TABLE)

    def on_app_goal(self, msg):
        self.get_logger().info(
            f'App goal {msg.goal_id}: table {msg.table_id}, {msg.goal_type}')


def main(args=None):
    rclpy.init(args=args)
    node = MissionManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()