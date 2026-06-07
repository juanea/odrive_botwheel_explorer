# odrive_botwheel_explorer
Development environment for the ODrive BotWheel Explorer a platform for building and improving autonomous navigation.

## Teleop

### Keyboard

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/botwheel_explorer/cmd_vel -p qos_reliability:=best_effort -p stamped:=true
```

### Gamepad (Bluetooth Xbox controller)

The `joy` and `teleop_twist_joy` packages are declared as dependencies of the
`botwheel_explorer_deps` meta-package, so `rosdep` installs them automatically
when the image is built — no `apt install` and no Dockerfile changes needed.

After pairing the controller (it shows up as `/dev/input/js0`), run the joystick
driver and the teleop node. Note that `teleop_twist_joy`'s `teleop-launch.py`
always publishes to `/cmd_vel` and offers no CLI remap, so the topic is remapped
on the `teleop_node` directly:

```bash
# Terminal 1 — joystick driver (publishes /joy)
ros2 run joy joy_node

# Terminal 2 — convert /joy to TwistStamped on the robot's cmd_vel topic
ros2 run teleop_twist_joy teleop_node --ros-args \
  --params-file /opt/ros/$ROS_DISTRO/share/teleop_twist_joy/config/xbox.config.yaml \
  -r cmd_vel:=/botwheel_explorer/cmd_vel \
  -p publish_stamped_twist:=true
```

The `xbox.config.yaml` shipped with `teleop_twist_joy` defines the axis→velocity
mappings, scaling, and a **deadman/enable button that must be held** for the
robot to move (plus a turbo button). Adjust axes/scales by copying that file and
pointing `--params-file` at your copy. `publish_stamped_twist:=true` matches the
`stamped` twist the diff-drive controller expects.
