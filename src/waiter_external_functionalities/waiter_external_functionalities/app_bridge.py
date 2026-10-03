import rclpy
from rclpy.node import Node
from waiter_interfaces.msg import AppGoal, MissionStatus

STATE_NAMES = {
    0: 'IDLE', 1: 'GOING_TO_KITCHEN', 2: 'WAITING_FOR_FOOD',
    3: 'DELIVERING', 4: 'AT_TABLE', 5: 'RETURNING', 6: 'DOCKING',
}


class AppBridge(Node):
    def __init__(self):
        super().__init__('app_bridge')
        self.goal_pub = self.create_publisher(AppGoal, '/app/goal', 10)
        self.create_subscription(MissionStatus, '/mission/status', self.on_status, 10)
        self.get_logger().info('app_bridge started')

    def on_status(self, msg):
        name = STATE_NAMES.get(msg.state, 'UNKNOWN')
        self.get_logger().info(
            f'App update: order {msg.mission_id} is {name} (table {msg.table_id})')


def main(args=None):
    rclpy.init(args=args)
    node = AppBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()