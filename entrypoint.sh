#!/usr/bin/env bash
set -e

# Source the ROS 2 distro
source "/opt/ros/${ROS_DISTRO}/setup.bash"

# Source the workspace overlay if it has been built
if [ -f /botwheel_ws/install/setup.bash ]; then
    source /botwheel_ws/install/setup.bash
fi

exec "$@"
