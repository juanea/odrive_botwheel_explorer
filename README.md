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

After pairing the controller (it shows up as `/dev/input/js0`),
`teleop-launch.py` brings up both the joystick driver and the teleop node in one
shot. Use `joy_vel` to remap the output topic, `publish_stamped_twist` to emit
the `TwistStamped` the diff-drive controller expects, and `config_filepath` to
point at the axis/scale/button config:

```bash
ros2 launch teleop_twist_joy teleop-launch.py \
  joy_vel:='/botwheel_explorer/cmd_vel' \
  publish_stamped_twist:='true' \
  config_filepath:='/botwheel_ws/src/botwheel_explorer_deps/config/xbox.config.yaml'
```

The in-project [`xbox.config.yaml`](botwheel_ws/src/botwheel_explorer_deps/config/xbox.config.yaml)
defines the axis→velocity mappings, scaling, and a **deadman/enable button that
must be held** for the robot to move (plus a turbo button). Adjust axes/scales by
editing that file.
