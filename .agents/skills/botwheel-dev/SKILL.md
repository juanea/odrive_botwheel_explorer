---
name: botwheel-dev
description: >-
  Use this skill when building, running, or debugging the ROS 2 BotWheel Explorer
  workspace inside Docker, resolving rosdep dependencies, or bringing up the SocketCAN
  interface.
---

# BotWheel Dev Workflow

Standard procedure for working in the containerized ROS 2 workspace.

## Steps

1. Start the dev container if it is not already running:
   ```bash
   task up
   ```
2. Install or update workspace dependencies when `package.xml` changes:
   ```bash
   task rosdep
   ```
3. Build the ROS 2 workspace:
   ```bash
   task colcon
   ```
4. Bring up the CAN interface when testing with ODrive hardware:
   ```bash
   task can-up
   ```

## Verification

- Confirm the container is healthy with `docker compose ps`.
- Confirm `task colcon` exits with code `0` and no package errors.
- Run `prek run --all-files` to verify formatting and linting before finishing.
