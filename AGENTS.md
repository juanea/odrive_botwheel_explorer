# AGENTS.md

Project instructions for AI coding agents working in `odrive_botwheel_explorer`.

## Project Overview

Development environment for the **ODrive BotWheel Explorer** — a ROS 2 (`lyrical`) autonomous navigation platform built around Docker, `colcon`, SocketCAN (`can0`), and Build123d hardware CAD.

## Repository Layout

- `botwheel_ws/` — ROS 2 workspace (bind-mounted into `/botwheel_ws` in the dev container)
- `hardware/` — Parametric 3D CAD models (`build123d`), exports, and renders
- `ansible/` — Host provisioning playbooks
- `Dockerfile`, `docker-compose.yaml`, `entrypoint.sh` — Dev and runtime container setup
- `Taskfile.yaml` — Primary command runner (`task`)
- `.agents/skills/` — Project skills (shared across Antigravity, Codex, Claude Code, and Cursor)

## Common Commands

Prefer `Taskfile.yaml` tasks over raw `docker compose` commands:

- `task build` — Build the dev container image
- `task up` / `task down` — Start or stop the dev container
- `task shell` — Open a sourced ROS 2 shell inside the dev container
- `task colcon` — Build `botwheel_ws` inside the container (`colcon build --symlink-install`)
- `task rosdep` — Resolve ROS 2 workspace dependencies inside the container
- `task can-up` — Bring up `can0` (override with `BITRATE=500000`)
- `task clean` — Remove `botwheel_ws/{build,install,log}` on the host

## Conventions & Quality Checks

- Run pre-commit hooks before committing: `prek run --all-files`
- Keep `botwheel_ws/{build,install,log}` out of git (ignored via `.gitignore`).
- Do not modify vendor/submodule files under `botwheel_ws/src/` unless explicitly requested.
- When adding new repeatable workflows, create a skill under `.agents/skills/<skill-name>/SKILL.md`.
