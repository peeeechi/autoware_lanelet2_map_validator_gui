FROM ros:humble

ARG VALIDATOR_HASH=4d1167c3c253b7c5ecb053be5831584331dd3e6b
ARG DEBIAN_FRONTEND=noninteractive

ENV TZ=Asia/Tokyo
ENV USER_NAME=autoware
ENV GROUP_NAME=${USER_NAME}

SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y \
  git \
  && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 1000 ${GROUP_NAME} && \
    useradd -s /bin/bash -u 1000 -g ${GROUP_NAME} ${USER_NAME} && \
    echo "${USER_NAME}:${USER_NAME}" | chpasswd

USER ${USER_NAME}

WORKDIR /home/${USER_NAME}/

# 1. Clone Autoware
RUN git clone https://github.com/autowarefoundation/autoware.git \
  && cd /home/${USER_NAME}/autoware/ \
  && mkdir src \
  && vcs import src < autoware.repos \
  && cd /home/${USER_NAME}/autoware/src/ \
# 2. Clone autoware_lanelet2_map_validator
  && git clone https://github.com/tier4/autoware_lanelet2_map_validator.git \
  && cd autoware_lanelet2_map_validator \
  && git checkout ${VALIDATOR_HASH}

WORKDIR /home/${USER_NAME}/autoware/

# 3. Install dependent packages
USER root
RUN apt update && apt upgrade -y \
  && source /opt/ros/humble/setup.bash \
  && rosdep update \
  && rosdep install -y --from-paths src --ignore-src --rosdistro $ROS_DISTRO

USER ${USER_NAME}

# 4. Build autoware_lanelet2_map_validator
RUN source /opt/ros/humble/setup.bash \
  && colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release --packages-up-to \
  autoware_lanelet2_map_validator \
  autoware_lanelet2_extension \
  autoware_lanelet2_extension_python

# 5. Install other necessary packages
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

EXPOSE 8080