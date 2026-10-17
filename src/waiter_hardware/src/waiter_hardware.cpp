#include <fcntl.h>
#include <termios.h>
#include <unistd.h>

#include <algorithm>
#include <array>
#include <cerrno>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <memory>
#include <string>
#include <vector>

#include "hardware_interface/handle.hpp"
#include "hardware_interface/hardware_info.hpp"
#include "hardware_interface/system_interface.hpp"
#include "hardware_interface/types/hardware_interface_return_values.hpp"
#include "hardware_interface/types/hardware_interface_type_values.hpp"
#include "pluginlib/class_list_macros.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_lifecycle/state.hpp"
#include "sensor_msgs/msg/battery_state.hpp"

namespace waiter_hardware
{
using CallbackReturn = hardware_interface::CallbackReturn;
using SteadyClock = std::chrono::steady_clock;

class WaiterHardware : public hardware_interface::SystemInterface
{
public:
  ~WaiterHardware() override { close_port(); }

  CallbackReturn on_init(const hardware_interface::HardwareComponentInterfaceParams & params) override
  {
    if (hardware_interface::SystemInterface::on_init(params) != CallbackReturn::SUCCESS) {
      return CallbackReturn::ERROR;
    }

    auto param = [&](const std::string & key, const std::string & def) {
      auto it = info_.hardware_parameters.find(key);
      return it == info_.hardware_parameters.end() ? def : it->second;
    };
    try {
      port_ = param("port", "/dev/ttyACM0");
      baud_ = std::stoi(param("baud_rate", "115200"));
      bat_min_ = std::stod(param("battery_min_voltage", "30.0"));
      bat_max_ = std::stod(param("battery_max_voltage", "42.0"));
    } catch (const std::exception & e) {
      RCLCPP_ERROR(logger_, "Bad hardware parameter: %s", e.what());
      return CallbackReturn::ERROR;
    }

    if (info_.joints.size() != 2) {
      RCLCPP_ERROR(logger_, "Expected 2 joints, found %zu", info_.joints.size());
      return CallbackReturn::ERROR;
    }
    for (size_t i = 0; i < info_.joints.size(); ++i) {
      if (info_.joints[i].name == "right_wheel_joint") right_idx_ = static_cast<int>(i);
      if (info_.joints[i].name == "left_wheel_joint") left_idx_ = static_cast<int>(i);
    }
    if (right_idx_ < 0 || left_idx_ < 0) {
      RCLCPP_ERROR(logger_, "Joints must be named left_wheel_joint and right_wheel_joint");
      return CallbackReturn::ERROR;
    }
    if (info_.sensors.empty()) {
      RCLCPP_ERROR(logger_, "The imu sensor is missing in the ros2_control block");
      return CallbackReturn::ERROR;
    }
    imu_name_ = info_.sensors[0].name;
    if (!info_.gpios.empty()) {
      battery_name_ = info_.gpios[0].name;
      has_battery_ = true;
    }

    pos_.assign(2, 0.0);
    vel_.assign(2, 0.0);
    cmd_.assign(2, 0.0);
    imu_.fill(0.0);
    imu_[3] = 1.0;  // quaternion w = 1, a valid "no rotation" before the first data
    return CallbackReturn::SUCCESS;
  }

  std::vector<hardware_interface::StateInterface> export_state_interfaces() override
  {
    std::vector<hardware_interface::StateInterface> s;
    for (size_t i = 0; i < info_.joints.size(); ++i) {
      s.emplace_back(info_.joints[i].name, hardware_interface::HW_IF_POSITION, &pos_[i]);
      s.emplace_back(info_.joints[i].name, hardware_interface::HW_IF_VELOCITY, &vel_[i]);
    }
    static const char * names[10] = {
      "orientation.x", "orientation.y", "orientation.z", "orientation.w",
      "angular_velocity.x", "angular_velocity.y", "angular_velocity.z",
      "linear_acceleration.x", "linear_acceleration.y", "linear_acceleration.z"};
    for (size_t i = 0; i < 10; ++i) {
      s.emplace_back(imu_name_, names[i], &imu_[i]);
    }
    if (has_battery_) {
      s.emplace_back(battery_name_, "voltage", &battery_voltage_);
    }
    return s;
  }

  std::vector<hardware_interface::CommandInterface> export_command_interfaces() override
  {
    std::vector<hardware_interface::CommandInterface> c;
    for (size_t i = 0; i < info_.joints.size(); ++i) {
      c.emplace_back(info_.joints[i].name, hardware_interface::HW_IF_VELOCITY, &cmd_[i]);
    }
    return c;
  }

  CallbackReturn on_configure(const rclcpp_lifecycle::State &) override
  {
    if (!open_port()) return CallbackReturn::ERROR;
    rx_.clear();
    connected_ = false;
    arduino_sees_cmd_ = -1;
    battery_received_ = false;
    if (has_battery_) {
      battery_node_ = std::make_shared<rclcpp::Node>("waiter_battery_publisher");
      battery_pub_ =
        battery_node_->create_publisher<sensor_msgs::msg::BatteryState>("battery_state", 10);
    }
    RCLCPP_INFO(logger_, "Opened %s at %d baud. Waiting for data from the Arduino...",
                port_.c_str(), baud_);
    return CallbackReturn::SUCCESS;
  }

  CallbackReturn on_cleanup(const rclcpp_lifecycle::State &) override
  {
    close_port();
    battery_pub_.reset();
    battery_node_.reset();
    return CallbackReturn::SUCCESS;
  }

  CallbackReturn on_activate(const rclcpp_lifecycle::State &) override
  {
    std::fill(cmd_.begin(), cmd_.end(), 0.0);
    last_rx_ = SteadyClock::now();
    last_write_ = SteadyClock::now() - std::chrono::seconds(1);
    return CallbackReturn::SUCCESS;
  }

  CallbackReturn on_deactivate(const rclcpp_lifecycle::State &) override
  {
    send_text("C,0.000,0.000\n");  // stop the motors
    return CallbackReturn::SUCCESS;
  }

  hardware_interface::return_type read(const rclcpp::Time &, const rclcpp::Duration &) override
  {
    if (fd_ < 0) return hardware_interface::return_type::OK;

    char buf[256];
    while (true) {
      ssize_t n = ::read(fd_, buf, sizeof(buf));
      if (n > 0) {
        rx_.append(buf, static_cast<size_t>(n));
      } else {
        if (n < 0 && errno != EAGAIN && errno != EWOULDBLOCK) {
          RCLCPP_ERROR_THROTTLE(logger_, clock_, 3000,
                                "Serial read failed (%s). Is the cable unplugged?",
                                std::strerror(errno));
        }
        break;
      }
    }

    bool got_valid = false;
    size_t pos;
    while ((pos = rx_.find('\n')) != std::string::npos) {
      std::string line = rx_.substr(0, pos);
      rx_.erase(0, pos + 1);
      if (!line.empty() && line.back() == '\r') line.pop_back();
      if (handle_line(line)) got_valid = true;
    }
    if (rx_.size() > 512) rx_.clear();  // garbage without newline

    const auto now = SteadyClock::now();
    if (got_valid) {
      last_rx_ = now;
      if (!connected_) {
        connected_ = true;
        RCLCPP_INFO(logger_, "Arduino data is arriving.");
      }
    } else if (std::chrono::duration<double>(now - last_rx_).count() > 0.5) {
      if (connected_) {
        connected_ = false;
        RCLCPP_WARN(logger_, "No data from the Arduino for 0.5 s. Wheel speeds set to 0.");
      } else {
        RCLCPP_WARN_THROTTLE(logger_, clock_, 3000,
                             "Still no data from the Arduino (check cable, port, baud rate).");
      }
      vel_[0] = 0.0;
      vel_[1] = 0.0;
    }

    publish_battery();
    return hardware_interface::return_type::OK;
  }

  hardware_interface::return_type write(const rclcpp::Time &, const rclcpp::Duration &) override
  {
    if (fd_ < 0) return hardware_interface::return_type::OK;
    const auto now = SteadyClock::now();
    if (now - last_write_ < std::chrono::milliseconds(15)) {
      return hardware_interface::return_type::OK;  // limit to about 50 Hz
    }
    last_write_ = now;

    double r = cmd_[right_idx_];
    double l = cmd_[left_idx_];
    if (!std::isfinite(r)) r = 0.0;
    if (!std::isfinite(l)) l = 0.0;
    char out[64];
    int n = std::snprintf(out, sizeof(out), "C,%.3f,%.3f\n", r, l);
    if (n > 0) send_text(std::string(out, static_cast<size_t>(n)));
    return hardware_interface::return_type::OK;
  }

private:
  static std::vector<std::string> split(const std::string & s)
  {
    std::vector<std::string> out;
    std::string cur;
    for (char c : s) {
      if (c == ',') {
        out.push_back(cur);
        cur.clear();
      } else {
        cur += c;
      }
    }
    out.push_back(cur);
    return out;
  }

  static bool to_numbers(const std::vector<std::string> & t, size_t expected,
                         std::vector<double> & out)
  {
    if (t.size() != expected + 1) return false;
    out.clear();
    for (size_t i = 1; i < t.size(); ++i) {
      char * end = nullptr;
      double x = std::strtod(t[i].c_str(), &end);
      if (end == t[i].c_str() || *end != '\0' || !std::isfinite(x)) return false;
      out.push_back(x);
    }
    return true;
  }

  bool handle_line(const std::string & line)
  {
    if (line.empty()) return false;
    const auto t = split(line);
    std::vector<double> v;
    bool ok = false;

    if (t[0] == "W" && to_numbers(t, 4, v)) {
      pos_[right_idx_] = v[0];
      vel_[right_idx_] = v[1];
      pos_[left_idx_] = v[2];
      vel_[left_idx_] = v[3];
      ok = true;
    } else if (t[0] == "I" && to_numbers(t, 10, v)) {
      // Arduino order: ax ay az gx gy gz qx qy qz qw
      double norm = std::sqrt(v[6] * v[6] + v[7] * v[7] + v[8] * v[8] + v[9] * v[9]);
      if (norm > 0.5) {
        imu_[0] = v[6]; imu_[1] = v[7]; imu_[2] = v[8]; imu_[3] = v[9];
      } else {
        imu_[0] = 0.0; imu_[1] = 0.0; imu_[2] = 0.0; imu_[3] = 1.0;
      }
      imu_[4] = v[3]; imu_[5] = v[4]; imu_[6] = v[5];
      imu_[7] = v[0]; imu_[8] = v[1]; imu_[9] = v[2];
      ok = true;
    } else if (t[0] == "B" && to_numbers(t, 1, v)) {
      battery_voltage_ = v[0];
      battery_received_ = true;
      ok = true;
    } else if (t[0] == "S" && to_numbers(t, 1, v)) {
      int now_state = v[0] > 0.5 ? 1 : 0;
      if (now_state != arduino_sees_cmd_) {
        if (now_state == 1) {
          RCLCPP_INFO(logger_, "Arduino is receiving our commands.");
        } else if (arduino_sees_cmd_ == 1) {
          RCLCPP_WARN(logger_, "Arduino says it is NOT receiving our commands anymore.");
        } else {
          RCLCPP_INFO(logger_, "Arduino has not received a command yet.");
        }
        arduino_sees_cmd_ = now_state;
      }
      ok = true;
    }

    if (!ok) {
      RCLCPP_WARN_THROTTLE(logger_, clock_, 2000, "Ignoring bad line from Arduino: '%s'",
                           line.c_str());
    }
    return ok;
  }

  void publish_battery()
  {
    if (!battery_pub_ || !battery_received_) return;
    const auto now = SteadyClock::now();
    if (now - last_bat_pub_ < std::chrono::seconds(1)) return;
    last_bat_pub_ = now;

    const float nan = std::numeric_limits<float>::quiet_NaN();
    sensor_msgs::msg::BatteryState msg;
    msg.header.stamp = battery_node_->now();
    msg.header.frame_id = "base_link";
    msg.voltage = static_cast<float>(battery_voltage_);
    msg.current = nan;
    msg.charge = nan;
    msg.capacity = nan;
    msg.design_capacity = nan;
    double pct = (battery_voltage_ - bat_min_) / (bat_max_ - bat_min_);
    msg.percentage = static_cast<float>(std::clamp(pct, 0.0, 1.0));  // 0.0 to 1.0
    msg.power_supply_status = sensor_msgs::msg::BatteryState::POWER_SUPPLY_STATUS_DISCHARGING;
    msg.power_supply_technology = sensor_msgs::msg::BatteryState::POWER_SUPPLY_TECHNOLOGY_LION;
    msg.present = true;
    battery_pub_->publish(msg);
  }

  void send_text(const std::string & text)
  {
    if (fd_ < 0) return;
    ssize_t n = ::write(fd_, text.data(), text.size());
    if (n < 0 && errno != EAGAIN && errno != EWOULDBLOCK) {
      RCLCPP_WARN_THROTTLE(logger_, clock_, 3000, "Serial write failed: %s", std::strerror(errno));
    }
  }

  bool open_port()
  {
    fd_ = ::open(port_.c_str(), O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (fd_ < 0) {
      RCLCPP_ERROR(logger_, "Cannot open %s: %s", port_.c_str(), std::strerror(errno));
      return false;
    }
    termios tty;
    if (tcgetattr(fd_, &tty) != 0) {
      RCLCPP_ERROR(logger_, "tcgetattr failed: %s", std::strerror(errno));
      close_port();
      return false;
    }
    cfmakeraw(&tty);
    speed_t speed;
    switch (baud_) {
      case 9600: speed = B9600; break;
      case 19200: speed = B19200; break;
      case 38400: speed = B38400; break;
      case 57600: speed = B57600; break;
      case 115200: speed = B115200; break;
      case 230400: speed = B230400; break;
      default:
        RCLCPP_ERROR(logger_, "Unsupported baud rate %d", baud_);
        close_port();
        return false;
    }
    cfsetispeed(&tty, speed);
    cfsetospeed(&tty, speed);
    tty.c_cflag |= (CLOCAL | CREAD);
    tty.c_cflag &= ~(CSTOPB | PARENB | CRTSCTS);
    tty.c_cc[VMIN] = 0;
    tty.c_cc[VTIME] = 0;
    if (tcsetattr(fd_, TCSANOW, &tty) != 0) {
      RCLCPP_ERROR(logger_, "tcsetattr failed: %s", std::strerror(errno));
      close_port();
      return false;
    }
    tcflush(fd_, TCIOFLUSH);
    return true;
  }

  void close_port()
  {
    if (fd_ >= 0) {
      ::close(fd_);
      fd_ = -1;
    }
  }

  rclcpp::Logger logger_ = rclcpp::get_logger("WaiterHardware");
  rclcpp::Clock clock_{RCL_STEADY_TIME};

  std::string port_;
  int baud_ = 115200;
  int fd_ = -1;
  std::string rx_;

  int right_idx_ = -1;
  int left_idx_ = -1;
  std::vector<double> pos_, vel_, cmd_;
  std::array<double, 10> imu_;
  std::string imu_name_;

  bool has_battery_ = false;
  std::string battery_name_;
  double battery_voltage_ = 0.0;
  double bat_min_ = 30.0;
  double bat_max_ = 42.0;
  bool battery_received_ = false;
  std::shared_ptr<rclcpp::Node> battery_node_;
  rclcpp::Publisher<sensor_msgs::msg::BatteryState>::SharedPtr battery_pub_;

  bool connected_ = false;
  int arduino_sees_cmd_ = -1;
  SteadyClock::time_point last_rx_{};
  SteadyClock::time_point last_write_{};
  SteadyClock::time_point last_bat_pub_{};
};

}  // namespace waiter_hardware

PLUGINLIB_EXPORT_CLASS(waiter_hardware::WaiterHardware, hardware_interface::SystemInterface)