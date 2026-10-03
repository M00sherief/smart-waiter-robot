import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from waiter_interfaces.action import Dock
from waiter_interfaces.msg import (AppGoal, MissionStatus, OrderNew,
                                   OrderStatus, PowerAlert)


class MissionManager(Node):
    def __init__(self):
        super().__init__('mission_manager')
        self.tables = {}
        self.docking = False
        self.status_pub = self.create_publisher(MissionStatus, '/mission/status', 10)
        self.create_subscription(OrderNew, '/order/new', self.on_new_order, 10)
        self.create_subscription(OrderStatus, '/order/status', self.on_order_status, 10)
        self.create_subscription(AppGoal, '/app/goal', self.on_app_goal, 10)
        self.create_subscription(PowerAlert, '/power/alert', self.on_power_alert, 10)
        self.dock_client = ActionClient(self, Dock, 'dock')
        self.get_logger().info('mission_manager started')

    def publish_state(self, mission_id, table_id, state):
        msg = MissionStatus()
        msg.mission_id = mission_id
        msg.table_id = table_id
        msg.state = state
        self.status_pub.publish(msg)
        self.get_logger().info(f'Mission {mission_id}: state {state}, table {table_id}')

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

    def on_power_alert(self, msg):
        self.get_logger().info(
            f'Power alert level {msg.level} ({msg.battery_percent:.0f}%)')
        if msg.dock_required and not self.docking:
            self.docking = True
            self.publish_state('dock', 0, MissionStatus.DOCKING)
            self.send_dock_goal()

    def send_dock_goal(self):
        if not self.dock_client.wait_for_server(timeout_sec=2.0):
            self.get_logger().warn('Dock server not available')
            self.docking = False
            return
        goal = Dock.Goal()
        goal.force = False
        future = self.dock_client.send_goal_async(
            goal, feedback_callback=self.on_dock_feedback)
        future.add_done_callback(self.on_goal_response)

    def on_goal_response(self, future):
        handle = future.result()
        if not handle.accepted:
            self.get_logger().warn('Dock goal rejected')
            self.docking = False
            return
        handle.get_result_async().add_done_callback(self.on_dock_result)

    def on_dock_feedback(self, feedback_msg):
        self.get_logger().info(f'Dock stage: {feedback_msg.feedback.stage}')

    def on_dock_result(self, future):
        result = future.result().result
        self.get_logger().info(f'Dock finished: {result.message}')
        self.docking = False
        self.publish_state('dock', 0, MissionStatus.IDLE)


def main(args=None):
    rclpy.init(args=args)
    node = MissionManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()