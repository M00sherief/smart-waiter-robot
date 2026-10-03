import time

import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
from sensor_msgs.msg import BatteryState
from waiter_interfaces.action import Dock
from waiter_interfaces.msg import PowerAlert

LOW_PERCENT = 30.0
CRITICAL_PERCENT = 15.0


class PowerManager(Node):
    def __init__(self):
        super().__init__('power_manager')
        self.last_level = None
        self.alert_pub = self.create_publisher(PowerAlert, '/power/alert', 10)
        self.create_subscription(BatteryState, '/battery/status', self.on_battery, 10)
        self.dock_server = ActionServer(self, Dock, 'dock', self.execute_dock)
        self.get_logger().info('power_manager started')

    def on_battery(self, msg):
        percent = msg.percentage * 100.0
        if percent <= CRITICAL_PERCENT:
            level = PowerAlert.CRITICAL
        elif percent <= LOW_PERCENT:
            level = PowerAlert.LOW
        else:
            level = PowerAlert.OK
        if level == self.last_level:
            return
        self.last_level = level
        alert = PowerAlert()
        alert.level = level
        alert.battery_percent = float(percent)
        alert.dock_required = (level == PowerAlert.CRITICAL)
        self.alert_pub.publish(alert)
        self.get_logger().info(f'Battery {percent:.0f}% -> alert level {level}')

    def execute_dock(self, goal_handle):
        self.get_logger().info('Dock request received')
        for stage in ['driving_to_dock', 'aligning', 'charging']:
            feedback = Dock.Feedback()
            feedback.stage = stage
            goal_handle.publish_feedback(feedback)
            time.sleep(1.0)
        goal_handle.succeed()
        result = Dock.Result()
        result.success = True
        result.message = 'Docked and charging'
        return result


def main(args=None):
    rclpy.init(args=args)
    node = PowerManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()