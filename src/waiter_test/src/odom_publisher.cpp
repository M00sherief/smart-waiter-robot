#include <algorithm>
#include <chrono>
#include <cmath>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "geometry_msgs/msg/twist_stamped.hpp"

using namespace std::chrono_literals;
using std::placeholders::_1;

class GoToPoint : public rclcpp::Node
{
public:
  GoToPoint() : Node("go_to_point")
  {
    this->declare_parameter<double>("goal_x", 2.0);
    this->declare_parameter<double>("goal_y", 1.67);
    this->declare_parameter<double>("tolerance", 0.05);
    this->declare_parameter<double>("max_linear", 0.3);
    this->declare_parameter<double>("max_angular", 0.8);
    this->declare_parameter<double>("k_linear", 0.8);
    this->declare_parameter<double>("k_angular", 1.5);

    cmd_pub_ = this->create_publisher<geometry_msgs::msg::TwistStamped>(
      "/diff_drive_controller/cmd_vel", 10);
    odom_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
      "/diff_drive_controller/odom", 10, std::bind(&GoToPoint::odom_cb, this, _1));
    timer_ = this->create_wall_timer(50ms, std::bind(&GoToPoint::control_loop, this));

    RCLCPP_INFO(this->get_logger(), "Waiting for odom...");
  }

private:
  void odom_cb(const nav_msgs::msg::Odometry::SharedPtr msg)
  {
    x_ = msg->pose.pose.position.x;
    y_ = msg->pose.pose.position.y;

    const auto & q = msg->pose.pose.orientation;
    yaw_ = std::atan2(2.0 * (q.w * q.z + q.x * q.y),
                      1.0 - 2.0 * (q.y * q.y + q.z * q.z));
    have_odom_ = true;
  }

  void control_loop()
  {
    if (!have_odom_) {
      return;
    }

    const double goal_x = this->get_parameter("goal_x").as_double();
    const double goal_y = this->get_parameter("goal_y").as_double();
    const double tol = this->get_parameter("tolerance").as_double();
    const double max_lin = this->get_parameter("max_linear").as_double();
    const double max_ang = this->get_parameter("max_angular").as_double();
    const double k_lin = this->get_parameter("k_linear").as_double();
    const double k_ang = this->get_parameter("k_angular").as_double();

    const double dx = goal_x - x_;
    const double dy = goal_y - y_;
    const double dist = std::hypot(dx, dy);

    geometry_msgs::msg::TwistStamped cmd;
    cmd.header.stamp = this->now();
    cmd.header.frame_id = "base_link";

    if (dist < tol) {
      cmd_pub_->publish(cmd);  // zero velocity
      RCLCPP_INFO(this->get_logger(), "Goal reached at (%.2f, %.2f)", x_, y_);
      rclcpp::shutdown();
      return;
    }

    const double target_yaw = std::atan2(dy, dx);
    double err = target_yaw - yaw_;
    err = std::atan2(std::sin(err), std::cos(err));  // wrap to [-pi, pi]

    if (std::fabs(err) > 0.4) {
      // Turn in place until roughly facing the goal
      cmd.twist.linear.x = 0.0;
      cmd.twist.angular.z = std::clamp(k_ang * err, -max_ang, max_ang);
    } else {
      cmd.twist.linear.x = std::min(max_lin, k_lin * dist);
      cmd.twist.angular.z = std::clamp(k_ang * err, -max_ang, max_ang);
    }

    cmd_pub_->publish(cmd);
  }

  rclcpp::Publisher<geometry_msgs::msg::TwistStamped>::SharedPtr cmd_pub_;
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;
  rclcpp::TimerBase::SharedPtr timer_;

  double x_{0.0}, y_{0.0}, yaw_{0.0};
  bool have_odom_{false};
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<GoToPoint>());
  return 0;
}
