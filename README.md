# odrive_botwheel_explorer
Development environment for the ODrive BotWheel Explorer a platform for building and improving autonomous navigation.

## Teleop

Drive the robot with the keyboard:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/botwheel_explorer/cmd_vel -p qos_reliability:=best_effort -p stamped:=true
```
