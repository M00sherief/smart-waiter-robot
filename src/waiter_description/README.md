# waiter_description

ROS 2 package that describes the **waiter robot** (a differential-drive robot built on a
hoverboard base) so it can be shown in RViz, used by `robot_state_publisher`, and later used in
simulation and navigation.

This document explains everything that was built in this project, why each choice was made,
which numbers are measured and which are only estimates, and how to change or extend it.

---

## 1. What this project is

| Item | Value |
|---|---|
| Workspace | `~/waiter_ws` |
| Package | `waiter_description` (build type `ament_cmake`) |
| Robot name | `waiter_robot` |
| Drive | 2 hoverboard wheels (differential drive) |
| Support | 1 ball caster at the front |
| Chassis | Custom body (back block + sloped nose), loaded from one STL mesh |
| Sensors (frames only) | 1 IMU (`imu_link`). Battery level has no frame, it is only a topic |
| Tested in | Not yet run in simulation. RViz display was checked by the user |

---

## 2. Folder structure

```
waiter_ws/
└── src/
    └── waiter_description/
        ├── CMakeLists.txt
        ├── package.xml
        ├── README.md                  <- this file
        ├── urdf/
        │   └── waiter.urdf.xacro      <- the robot model
        ├── meshes/
        │   └── chassis.stl            <- the chassis shape
        ├── launch/
        │   └── view3d_rviz.py         <- starts everything needed to see the robot
        └── rviz/
            └── view3d.rviz            <- RViz layout (panels, displays, camera)
```

After `colcon build`, the folders `urdf`, `launch`, `rviz` and `meshes` are installed to
`~/waiter_ws/install/waiter_description/share/waiter_description/`. The launch file and
RViz look for files there, not in `src`. With `--symlink-install` those installed files are links
to the files in `src`, so editing a file in `src` takes effect without rebuilding.

---

## 3. Coordinate conventions

- Units: meters, kilograms, radians, seconds.
- Axes (ROS standard, REP 103): **x forward, y left, z up**.
- A positive rotation of a wheel joint (axis `0 1 0`) rolls the robot **forward**.

---

## 4. Dimensions

### 4.1 Chassis (`meshes/chassis.stl`)

| Part | Size |
|---|---|
| Back block | 55 cm long, 41 cm wide, 34 cm high |
| Nose | 25 cm long, 41 cm wide at the top, 18 cm wide at the floor front |
| Whole chassis | 80 cm long, 41 cm wide, 34 cm high |
| Nose slope | drops 34 cm over 25 cm |
| Floor height | 12 cm above the ground (estimate, see section 12) |
| Top height | 46 cm above the ground |
| Mass | 8 kg (estimate) |

The chassis frame `chassis_link` has its origin at the **back, bottom, center** of the chassis.
So the back face is at x = 0, the nose tip is at x = 0.80, and the sides are at y = ±0.205.

### 4.2 Wheels (2, hoverboard)

| Item | Value |
|---|---|
| Diameter | 19 cm (radius 0.095 m), provided by the user |
| Width | 5.5 cm (assumption) |
| Mass | 2 kg each (estimate) |
| Distance between wheels | 51 cm, center to center (provided by the user) |
| Left wheel position | y = +0.255 m from `base_link` |
| Right wheel position | y = -0.255 m from `base_link` |
| Total width across both wheels | 56.5 cm (51 + 5.5) |
| Gap between the two wheels (inside) | 45.5 cm |
| Gap between wheel and chassis | 2.25 cm on each side ((45.5 - 41) / 2) |
| Axle height | 9.5 cm above the ground |

The chassis sits **between** the wheels, on top of the hoverboard deck. The wheel top is at
19 cm and the chassis floor is at 12 cm, so the wheels are beside the chassis, not under it.
The wheels do not touch the chassis.

### 4.3 Caster (1, front)

| Item | Value |
|---|---|
| Ball | radius 3 cm (6 cm diameter), mass 0.2 kg (estimate) |
| Post | radius 1 cm, length 6 cm, connects the ball to the chassis floor |
| Position | 72 cm from the back of the chassis (42 cm ahead of the wheel axle) |
| Ball center height | 3 cm above the ground |

The post length is `ground_clearance - 2 * caster_radius` (12 - 6 = 6 cm). It is needed because
the chassis floor is 12 cm up and the ball is only 6 cm tall.

### 4.4 Layout summary

- The wheel axle is 30 cm from the back of the chassis. The chassis extends 30 cm behind the
  axle and 50 cm ahead of it.
- The center of mass of the chassis is at x = 0.329 m from the back. That is 2.9 cm ahead of the
  axle, so the caster always carries a little weight and the robot does not tip backward.
- Wheelbase (axle to caster): 0.42 m.
- Overall robot: about 80 cm long, 56.5 cm wide, 46 cm tall.

---

## 5. The TF tree (frames)

```
base_footprint            on the ground, under the wheel axle
└── base_link             center of the wheel axle (9.5 cm above the ground)
    ├── chassis_link      back-bottom-center of the chassis body
    ├── left_wheel_link   (continuous joint, rotates around y)
    ├── right_wheel_link  (continuous joint, rotates around y)
    ├── caster_link       ball + post (fixed)
    └── imu_link          IMU frame (fixed)
```

### 5.1 Joints

| Joint | Type | Parent -> child | Origin (x y z, meters) |
|---|---|---|---|
| `base_footprint_joint` | fixed | `base_footprint` -> `base_link` | 0 0 0.095 |
| `chassis_joint` | fixed | `base_link` -> `chassis_link` | -0.30 0 0.025 |
| `left_wheel_joint` | continuous | `base_link` -> `left_wheel_link` | 0 0.255 0 |
| `right_wheel_joint` | continuous | `base_link` -> `right_wheel_link` | 0 -0.255 0 |
| `caster_joint` | fixed | `base_link` -> `caster_link` | 0.42 0 -0.065 |
| `imu_joint` | fixed | `base_link` -> `imu_link` | 0 0 0.06 |

Why these values:

- `base_footprint_joint` z = wheel radius, so `base_link` is at the axle height.
- `chassis_joint` x = -axle_from_back (the axle is 0.30 m from the chassis back).
  z = ground_clearance - wheel_radius = 0.12 - 0.095 = 0.025.
- `caster_joint` x = caster_x_from_back - axle_from_back = 0.72 - 0.30 = 0.42.
  z = caster_radius - wheel_radius = 0.03 - 0.095 = -0.065, so the ball touches the ground.

### 5.2 Wheel joint details

- Axis `0 1 0` (the y axis).
- `limit effort="10.0" velocity="20.0"`: placeholder limits (N·m and rad/s). Replace with the
  real motor values. For a `continuous` joint there is no position limit.
- `dynamics damping="0.01" friction="0.01"`: small values so simulators behave smoothly.

---

## 6. Links in detail

| Link | Visual | Collision | Inertial |
|---|---|---|---|
| `base_footprint` | none | none | none (frame only) |
| `base_link` | none | none | none (frame only) |
| `chassis_link` | `chassis.stl`, white | `chassis.stl` | 8 kg, from the mesh |
| `left_wheel_link` | cylinder r=0.095, l=0.055, black | same cylinder | 2 kg, cylinder formula |
| `right_wheel_link` | same as left | same | same as left |
| `caster_link` | sphere r=0.03 + post, grey | same shapes | 0.2 kg, sphere formula |
| `imu_link` | tiny black box 3 x 2 x 0.5 cm | none | none |

Cylinders are rotated by `rpy="1.5708 0 0"` (`pi/2` in the xacro) so their axis lies along y,
which is the wheel axle direction.

### 6.1 Inertia numbers

**Wheel** (solid cylinder, axis along y, m = 2 kg, r = 0.095, w = 0.055):

- `ixx = izz = m/12 * (3r² + w²)` = 0.005017
- `iyy = m r² / 2` = 0.009025

**Caster ball** (solid sphere, m = 0.2 kg, r = 0.03): `2/5 * m * r²` = 0.000072 on each axis.

**Chassis** (the mesh treated as a solid body of uniform density). Values for 1 kg, which the
xacro multiplies by `chassis_mass`:

| Value (per 1 kg) | Result at 8 kg |
|---|---|
| ixx = 0.022882 | 0.183056 |
| iyy = 0.047268 | 0.378144 |
| izz = 0.051143 | 0.409144 |
| ixz = 0.002627 | 0.021016 |

Center of mass: x = 0.32939, y = 0, z = 0.16218 (in `chassis_link`). Volume of the mesh:
0.0908 m³. A real chassis is hollow and has batteries and electronics inside, so replace these
with measured values when you can.

---

## 7. The chassis mesh (`meshes/chassis.stl`)

### 7.1 Why a mesh

URDF only has four built-in shapes: box, cylinder, sphere and mesh. A flat sloped surface and
triangular side faces cannot be made from boxes. The first version used 7 stacked boxes and looked
like stairs, so the chassis was replaced by one mesh with flat faces and sharp edges.

### 7.2 The shape

The mesh is the convex hull of 10 points (x forward, y left, z up, meters):

| Points | Coordinates |
|---|---|
| Back block, 8 corners | x in {0, 0.55}, y in {-0.205, +0.205}, z in {0, 0.34} |
| Nose tip, 2 points on the floor | x = 0.80, y = ±0.09, z = 0 |

Result: 16 triangles, a closed (watertight) convex solid, 80 x 41 x 34 cm. Faces:
a flat top, a flat sloped nose face, two flat triangular nose sides, two flat vertical side
faces on the back block, a vertical back face, a vertical face where the back block meets the
nose, and a flat floor.

Because the shape is convex, the same mesh is used for the **collision** geometry too.

### 7.3 Regenerating the mesh

If you change a dimension, run this (needs `pip install trimesh scipy numpy`):

```python
import numpy as np, trimesh

Lb, W, H, Ln, Wn = 0.55, 0.41, 0.34, 0.25, 0.18   # back length, width, height, nose length, nose floor width

pts = []
for x in (0.0, Lb):
    for y in (-W/2, W/2):
        for z in (0.0, H):
            pts.append([x, y, z])
pts += [[Lb + Ln, -Wn/2, 0.0], [Lb + Ln, Wn/2, 0.0]]

m = trimesh.convex.convex_hull(np.array(pts))
m.merge_vertices()
print("watertight:", m.is_watertight, "extents:", m.extents)
m.export("chassis.stl")

# inertia for 1 kg (multiply by the real mass in the xacro)
m.density = 1.0 / m.volume
print("center of mass:", m.center_mass)
print(np.round(m.moment_inertia, 6))
```

Then copy the new numbers into the `chassis_link` inertial block of the xacro
(center of mass in `origin`, inertia values in `inertia`).

### 7.4 The curved edge in the drawing

The drawing showed a slightly curved edge between the back block and the nose. The mesh uses a
sharp straight edge there. A curve can be added later by building a more detailed mesh.

---

## 8. The xacro file (`urdf/waiter.urdf.xacro`)

Xacro is URDF with variables, math and macros. `xacro` converts it to plain URDF when the launch
file runs.

### 8.1 Properties (the numbers you can change)

| Property | Value | Meaning |
|---|---|---|
| `wheel_radius` | 0.095 | Wheel radius (19 cm diameter) |
| `wheel_width` | 0.055 | Wheel thickness |
| `wheel_mass` | 2.0 | Mass of one wheel (kg) |
| `track_width` | 0.51 | Distance between wheel centers |
| `ground_clearance` | 0.12 | Height of the chassis floor above the ground |
| `axle_from_back` | 0.30 | Distance from the chassis back to the wheel axle |
| `caster_radius` | 0.03 | Ball radius |
| `caster_mass` | 0.2 | Caster mass |
| `caster_x_from_back` | 0.72 | Distance from the chassis back to the caster |
| `chassis_mass` | 8.0 | Chassis mass |
| `imu_x`, `imu_y`, `imu_z` | 0, 0, 0.06 | IMU position relative to `base_link` |

Changing wheel size, track width, clearance, axle or caster position updates the joints and the
wheels automatically. Changing the **chassis size** needs a new mesh (section 7.3).

### 8.2 Materials

`white` (chassis), `black` (wheels, IMU), `grey` (caster).

### 8.3 Macro `wheel`

`<xacro:wheel prefix="left" y_pos="..."/>` creates the joint, the link (visual, collision,
inertia) and the Gazebo friction tag for one wheel. It is called twice: once for the left wheel
and once for the right wheel.

### 8.4 Gazebo tags

- Wheels: `mu1 = mu2 = 1.0` (high friction, so the wheels grip).
- Caster: `mu1 = mu2 = 0.0` (no friction, so it slides like a real ball caster).

RViz ignores these tags. They are ready for a later Gazebo simulation.

---

## 9. The launch file (`launch/view3d_rviz.py`)

Command: `ros2 launch waiter_description view3d_rviz.py`

What it does, in order:

1. **`model` argument.** Declared with `DeclareLaunchArgument`. Its default is the installed
   `urdf/waiter.urdf.xacro`. You can load another file with
   `ros2 launch waiter_description view3d_rviz.py model:=/full/path/to/file.urdf.xacro`.
2. **`robot_description`.** `Command(["xacro ", model])` runs xacro and the output is wrapped in a
   `ParameterValue(..., value_type=str)` so ROS treats it as a string.
3. **`robot_state_publisher`.** Reads `robot_description` and publishes the TF frames of all
   fixed joints and of the moving joints (using `/joint_states`). It also publishes the model on
   the `/robot_description` topic, which RViz reads.
4. **`joint_state_publisher_gui`.** Opens a small window with sliders for the wheel joints. It
   publishes `/joint_states`. Without a `/joint_states` publisher, the wheels do not appear in TF.
5. **`rviz2`.** Opens RViz with the config `rviz/view3d.rviz`.

Stop everything with `Ctrl+C` in the terminal that launched it.

---

## 10. The RViz config (`rviz/view3d.rviz`)

- **Panels:** `Displays` (left side) and `Views`.
- **Displays:** `Grid`, `RobotModel` (reads the model from the `/robot_description` topic) and
  `TF` (shows the frame axes).
- **Fixed Frame:** `base_footprint`.
- **Camera:** orbit view, distance 2.5 m, pitch 0.5, yaw 0.8, looking at the robot.

If the left panel is missing, use **Panels -> Displays** in the RViz menu. To see the IMU frame
and the caster post clearly, set the `Alpha` of `RobotModel` to about 0.5, because the white
chassis is solid and hides what is inside it.

---

## 11. Build, run and daily use

### 11.1 First time

```bash
mkdir -p ~/waiter_ws/src && cd ~/waiter_ws/src
ros2 pkg create waiter_description --build-type ament_cmake
cd waiter_description
mkdir urdf launch rviz meshes
# copy the files from the project into these folders, then:
cat > CMakeLists.txt <<'EOF'
cmake_minimum_required(VERSION 3.8)
project(waiter_description)
find_package(ament_cmake REQUIRED)
install(DIRECTORY urdf launch rviz meshes DESTINATION share/${PROJECT_NAME})
ament_package()
EOF

sudo apt install ros-$ROS_DISTRO-xacro ros-$ROS_DISTRO-joint-state-publisher-gui \
                 ros-$ROS_DISTRO-robot-state-publisher ros-$ROS_DISTRO-rviz2

cd ~/waiter_ws
colcon build --symlink-install
source install/setup.bash
ros2 launch waiter_description view3d_rviz.py
```

### 11.2 Every day

```bash
cd ~/waiter_ws
source install/setup.bash
ros2 launch waiter_description view3d_rviz.py
```

To avoid typing `source` each time:
`echo "source ~/waiter_ws/install/setup.bash" >> ~/.bashrc`

### 11.3 When do I need to rebuild?

| Change | Rebuild needed? |
|---|---|
| Edit an existing file (xacro, launch, rviz, stl) | No (because of `--symlink-install`), just relaunch |
| Add a new file or a new folder | Yes: `colcon build --symlink-install` |
| Edit `CMakeLists.txt` or `package.xml` | Yes |

### 11.4 Check the model without RViz

```bash
cd ~/waiter_ws/src/waiter_description
xacro urdf/waiter.urdf.xacro > /tmp/waiter.urdf      # expand xacro
check_urdf /tmp/waiter.urdf                          # needs: sudo apt install liburdfdom-tools
```

### 11.5 Useful terminal tips

- `Ctrl+C` stops a running command. Click the terminal first.
- Copy and paste in the terminal: `Ctrl+Shift+C` and `Ctrl+Shift+V`.
- Open the project in VS Code: `cd ~/waiter_ws && code .`

---

## 12. Assumptions and numbers to measure

These values were estimated and should be replaced with real measurements:

| Value | Current | Where to change |
|---|---|---|
| Chassis floor height | 12 cm (axle 9.5 cm + hoverboard deck about 2.5 cm above it) | `ground_clearance` |
| Wheel width | 5.5 cm | `wheel_width` |
| Wheel mass | 2 kg | `wheel_mass` |
| Chassis mass | 8 kg | `chassis_mass` |
| Caster mass and size | 0.2 kg, radius 3 cm | `caster_mass`, `caster_radius` |
| Axle position | 30 cm from the chassis back | `axle_from_back` |
| Caster position | 72 cm from the chassis back | `caster_x_from_back` |
| Wheel joint limits | effort 10, velocity 20 | wheel macro |
| IMU position | on `base_link` axis, 6 cm above the axle | `imu_x`, `imu_y`, `imu_z` |

How the chassis numbers were decided: the drawing had labels that did not agree with each other
(for example 41 cm and 44 cm for the same top length). The final dimensions are the ones the
user gave later: whole body 80 cm = back block 55 cm + nose 25 cm, width 41 cm, height 34 cm.

---

## 13. Arduino data: IMU and battery

### 13.1 IMU

The IMU needs a frame so ROS can know where the sensor is on the robot. That frame is
`imu_link`, a fixed child of `base_link`.

- In the node that publishes the Arduino IMU data, set `header.frame_id = "imu_link"` on every
  `sensor_msgs/Imu` message (a common topic name is `/imu/data`).
- Units: acceleration in m/s², angular velocity in rad/s, orientation as a quaternion.
- Axes must follow x forward, y left, z up. If the real sensor is mounted in a different
  direction, rotate the frame with the `rpy` of `imu_joint` (do not edit the sensor numbers).
- Move the frame to the real sensor position with `imu_x`, `imu_y`, `imu_z`.
- Gazebo would also need an `<sensor type="imu">` block. That is not added yet because there is
  no simulation in this project so far.

### 13.2 Battery level

The battery level does **not** need a link. It has no position, so it is just a topic.

- Publish it as `sensor_msgs/BatteryState` (a common topic name is `/battery_state`).
- Useful fields: `voltage`, `percentage` (0.0 to 1.0 in ROS 2), `present`.
- A battery frame is not needed in the URDF.

### 13.3 Other connections you will need later

- **Joint states:** the Arduino (encoders) should publish `/joint_states` using the exact joint
  names `left_wheel_joint` and `right_wheel_joint`. Then you no longer start
  `joint_state_publisher_gui`.
- **Odometry:** the node that computes odometry should publish the transform
  `odom -> base_footprint` and the topic `/odom`. The URDF only provides everything below
  `base_footprint`.
- For navigation (Nav2), the footprint and the frame names `base_footprint`, `base_link`, `odom`
  and `map` are the standard ones, and they are already used here.

---

## 14. Problems found during the project and how they were fixed

| Problem | Cause | Fix |
|---|---|---|
| `file 'display.launch.py' was not found in the share directory` | The `CMakeLists.txt` had no `install(DIRECTORY ...)` line, so the launch folder was never installed | Add `install(DIRECTORY urdf launch rviz meshes DESTINATION share/${PROJECT_NAME})` and rebuild |
| URDF failed to parse | XML comments cannot contain two dashes in a row (`--`). A comment line made of dashes broke the file | Replace those comment lines with `=====` |
| xacro warning `redefining global symbol: len` | A macro parameter was named `len`, which is a Python built-in | Rename the parameters to `length` and `width` |
| RViz had no left panel | The first RViz config had no `Panels` section | Add `Panels` (Displays, Views) to the config |
| Chassis looked like stairs | Boxes cannot make a flat slope | Replace the boxes with one STL mesh |
| Mesh not found in RViz (possible) | The `meshes` folder was not in the `install(DIRECTORY ...)` line | Add `meshes` to it and rebuild |

---

## 15. History of design decisions

1. First model: chassis built from boxes, 6.5 inch hoverboard wheels (assumed).
2. Wheel diameter changed to 19 cm and the distance between wheels set to 51 cm (center to
   center). If 51 cm was meant as the inside gap, change `track_width` to 0.565.
3. URDF turned into xacro (`waiter.urdf.xacro`) with properties and a wheel macro.
4. Launch file `view3d_rviz.py` created in the style of a typical description package.
5. Chassis stairs replaced by a flat-faced STL mesh.
6. Chassis dimensions updated to 55 cm back block + 25 cm nose, 41 cm wide, 34 cm high, floor at
   12 cm. The caster got a post. The axle moved to 30 cm from the back.
7. `imu_link` added for the Arduino IMU data.

---

## 16. Ideas for next steps

- Measure the real values from section 12 and update the properties.
- Add the real IMU mounting position and orientation.
- Add a lidar and/or camera link (fixed joints on `base_link`) when those sensors are chosen.
- Write the Arduino bridge node (`/joint_states`, `/imu/data`, `/battery_state`, `/odom`).
- Add a `ros2_control` block and Gazebo plugin for simulation.
- Add the slightly curved edge of the drawing to the mesh if it matters visually.

---

## 17. ros2_control (added later)

### 17.1 New file in this package: `urdf/waiter_control.xacro`

It is included at the end of `waiter.urdf.xacro` with
`<xacro:include filename="$(find waiter_description)/urdf/waiter_control.xacro"/>`.
It contains one `<ros2_control name="WaiterSystem" type="system">` block:

| Part | Content |
|---|---|
| Hardware plugin | `mock_components/GenericSystem` (a fake hardware, for testing without the robot) with `calculate_dynamics = true` |
| `left_wheel_joint`, `right_wheel_joint` | command interface: `velocity`. State interfaces: `position`, `velocity` |
| `imu_sensor` | state interfaces: `orientation.x/y/z/w`, `angular_velocity.x/y/z`, `linear_acceleration.x/y/z` |

When the Arduino bridge exists, replace the plugin line with the real hardware interface plugin.
The joints and the sensor stay the same, because they define what the controllers use.
`robot_state_publisher` ignores the `ros2_control` block, so `view3d_rviz.py` works as before.

### 17.2 New package: `waiter_controllers`

```
waiter_controllers/
├── CMakeLists.txt
├── package.xml
└── config/
    └── waiter_controllers.yaml
```

`config/waiter_controllers.yaml` has three controllers:

| Controller | Type | Job |
|---|---|---|
| `joint_state_broadcaster` | `joint_state_broadcaster/JointStateBroadcaster` | Publishes `/joint_states` |
| `diff_drive_controller` | `diff_drive_controller/DiffDriveController` | Drives the wheels from velocity commands, publishes `odom` and the transform `odom -> base_footprint` |
| `imu_sensor_broadcaster` | `imu_sensor_broadcaster/IMUSensorBroadcaster` | Publishes the IMU as `sensor_msgs/Imu` with `frame_id = imu_link` |

Main `diff_drive_controller` values: wheel separation 0.51 m, wheel radius 0.095 m, odom frame
`odom`, base frame `base_footprint`, command timeout 0.5 s, speed limits 0.5 m/s and 1.0 rad/s
(with acceleration limits). These limits are starting values, change them as you like.

Command topic: on ROS 2 Humble the file uses `use_stamped_vel: false`, so the robot listens to
`geometry_msgs/Twist` on `cmd_vel_unstamped`. On Jazzy and later that setting does not exist and
the command is `geometry_msgs/TwistStamped` on `cmd_vel`.

### 17.3 Install the needed packages

```bash
sudo apt install ros-$ROS_DISTRO-ros2-control ros-$ROS_DISTRO-ros2-controllers
```

### 17.4 Not done yet

There is no launch file for the controllers yet. It still has to start `ros2_control_node`
(controller manager) with this YAML and the robot description, and then spawn
`joint_state_broadcaster`, `diff_drive_controller` and `imu_sensor_broadcaster`.
