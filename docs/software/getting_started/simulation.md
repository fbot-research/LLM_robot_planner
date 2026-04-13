# MICKY Simulation - Mapping Tutorial

---

## Pre Requisite:

- **ROS 2 Humble**
- **Gazebo Harmonic** (or Garden)

--- 

## Installing the Simulation Repository

Navigate to your workspace source directory and clone the repository:

```bash
cd ~/micky_ws/src
git clone https://github.com/FBOTWork/micky_simulation.git
```

Install rosdep dependencies:

```bash
cd ~/micky_ws
rosdep update
rosdep install --from-paths src --ignore-src -r -y
```

Install required ROS 2 packages:

```bash
sudo apt install -y \
  ros-humble-ros-gz-sim \
  ros-humble-ros-gz-bridge \
  ros-humble-robot-state-publisher \
  ros-humble-slam-toolbox \
  ros-humble-nav2-map-server \
  ros-humble-xacro \
  ros-humble-rviz2
```

Source the ROS 2 environment in every terminal (or add to `~/.bashrc`):

```bash
source /opt/ros/humble/setup.bash
source ~/micky_ws/install/setup.bash
```

---

## Building the Workspace

Run **once** after cloning or modifying package files:

```bash
cd ~/micky_ws
colcon build --symlink-install
source install/setup.bash
```

---

## Step 1 — Launch Gazebo

Opens Gazebo Harmonic with the `turtlebot3_world` world and spawns the Micky robot.

```bash
ros2 launch micky_simulation gazebo.launch.py
```

Wait until Gazebo GUI is fully open and the robot model is visible in the scene.

---

## Step 2 — Launch SLAM

In a **new terminal**, start the SLAM node and RViz:

```bash
ros2 launch micky_slam sim_slam.launch.py
```

RViz will open with the `/map` topic displayed. The map starts empty and is built as the robot moves.

---

## Step 3 — Drive the Robot (Teleop)

In a **third terminal**, start the keyboard teleop:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

| Key | Action |
|---|---|
| `i` / `,` | Forward / backward |
| `j` / `l` | Strafe left / right |
| `u` / `o` | Rotate left / right |
| `space` | Stop |
| `w` / `x` | Increase / decrease linear speed |

Drive the robot around the entire environment. The map in RViz fills in as new areas are scanned. For best results, make at least one full loop so slam_toolbox can close the loop.

---

## Step 4 — Save the Map

Once the environment is fully mapped, run in any terminal:

```bash
ros2 run nav2_map_server map_saver_cli -f ~/micky_map
```

This generates two files:
- `~/your_map.pgm` — the occupancy grid image
- `~/your_map.yaml` — metadata (resolution, origin, thresholds)

---

## Common Troubleshooting

### Gazebo does not open / freezes on startup

```bash
pkill -f gz_sim && pkill -f gzserver
unset IGN_PARTITION GZ_PARTITION
```

Then re-run Step 1.

### Map stays empty in RViz

1. Check that the LiDAR is publishing:
   ```bash
   ros2 topic echo /laser_scan_front
   # Expected: ~10 Hz
   ```
2. Move the robot — slam_toolbox only registers a new scan after the robot travels at least **0.5 m**.

### Robot does not move

```bash
# Test the command manually
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.2, y: 0.0, z: 0.0}, angular: {z: 0.0}}" --once
```

If the robot moves in Gazebo but not from teleop, make sure the teleop terminal has focus (keyboard input is captured there).

