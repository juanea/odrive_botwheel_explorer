# syntax=docker/dockerfile:1

# ROS 2 Lyrical Luth
ARG ROS_DISTRO=lyrical

###############################################################################
# Stage: base
# ROS 2 distro + build / dev tooling, CAN utilities (can0) and video tooling.
###############################################################################
FROM ros:${ROS_DISTRO}-ros-base AS base

SHELL ["/bin/bash", "-c"]
ENV DEBIAN_FRONTEND=noninteractive
ENV WS=/botwheel_ws

# Non-root user matching the host UID/GID so bind-mounted files keep their
# ownership (no root-owned artifacts after building the workspace).
ARG USERNAME=botwheel
ARG USER_UID=1000
ARG USER_GID=1000

RUN apt-get update && apt-get install -y --no-install-recommends \
        sudo \
        python3-colcon-common-extensions \
        python3-rosdep \
        build-essential \
        git \
        nano \
        can-utils \
        iproute2 \
        v4l-utils \
    && rm -rf /var/lib/apt/lists/*

# The Ubuntu base image ships a default 'ubuntu' user on UID 1000 — drop it,
# then create 'botwheel' with the host's UID/GID and passwordless sudo.
RUN userdel -r ubuntu 2>/dev/null || true \
    && groupadd --gid ${USER_GID} ${USERNAME} 2>/dev/null || true \
    && useradd --uid ${USER_UID} --gid ${USER_GID} --create-home --shell /bin/bash ${USERNAME} \
    && usermod --append --groups video,dialout ${USERNAME} \
    && echo "${USERNAME} ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} \
    && chmod 0440 /etc/sudoers.d/${USERNAME}

WORKDIR ${WS}
RUN chown ${USER_UID}:${USER_GID} ${WS}

###############################################################################
# Stage: collector
# Gather ONLY the package.xml manifests. Isolating them means the dependency
# layer below is rebuilt only when a manifest changes, not on every code edit.
###############################################################################
FROM base AS collector

COPY botwheel_ws/src ./src
RUN mkdir -p /manifests \
    && find src -name "package.xml" -exec cp --parents {} /manifests/ \;

###############################################################################
# Stage: rosdep
# Install every ROS / system dependency declared by the packages.
# Cached against the collected manifests only.
###############################################################################
FROM base AS rosdep

COPY --from=collector /manifests/src ./src
RUN rosdep update --rosdistro "${ROS_DISTRO}" \
    && apt-get update \
    && rosdep install --from-paths src --ignore-src --rosdistro "${ROS_DISTRO}" -y \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf ./src

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

###############################################################################
# Stage: build
# Compile the workspace. Feeds the runtime image; not used by the dev image.
###############################################################################
FROM rosdep AS build

SHELL ["/bin/bash", "-c"]
COPY botwheel_ws/src ./src
RUN source "/opt/ros/${ROS_DISTRO}/setup.bash" \
    && colcon build

###############################################################################
# Stage: dev  (default)
# Dependencies only — the workspace is NOT built here so you can bind-mount it
# and run `colcon build` yourself to debug. Idles by default.
###############################################################################
FROM rosdep AS dev

# Install Node.js (LTS) — packages installed per-user below, not as root
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

USER botwheel

# User-level npm prefix so global installs are writable without sudo,
# which allows claude/gemini to self-update inside the container.
ENV NPM_CONFIG_PREFIX=/home/botwheel/.npm-global
ENV PATH=/home/botwheel/.local/bin:/home/botwheel/.npm-global/bin:$PATH

RUN npm install -g @anthropic-ai/claude-code @google/gemini-cli \
    && claude install

ENTRYPOINT ["/entrypoint.sh"]
CMD ["sleep", "infinity"]

###############################################################################
# Stage: runtime
# Ships the prebuilt workspace to actually drive the robot.
###############################################################################
FROM rosdep AS runtime

COPY --from=build ${WS}/install ${WS}/install

USER botwheel
ENTRYPOINT ["/entrypoint.sh"]
CMD ["ros2", "launch", "odrive_botwheel_explorer", "botwheel_explorer.launch.py"]
