FROM ros:humble

ARG VALIDATOR_TAG=1.6.0
ARG DEBIAN_FRONTEND=noninteractive

ENV TZ=Asia/Tokyo
ENV USER_NAME=autoware
ENV GROUP_NAME=${USER_NAME}

SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y \
  curl \
  unzip \
  python3-pip \
  ros-humble-autoware-lanelet2-extension \
  ros-humble-autoware-lanelet2-extension-python \
  && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 1000 ${GROUP_NAME} && \
    useradd -s /bin/bash -u 1000 -g ${GROUP_NAME} ${USER_NAME} && \
    echo "${USER_NAME}:${USER_NAME}" | chpasswd

USER ${USER_NAME}

WORKDIR /home/${USER_NAME}/autoware/

# validator install
RUN curl -L -o validator.zip https://github.com/tier4/autoware_lanelet2_map_validator/releases/download/${VALIDATOR_TAG}/autoware_lanelet2_map_validator-${VALIDATOR_TAG}-linux-x86_64.zip \
    && unzip validator.zip \
    && rm validator.zip

# 5. Install other necessary packages
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

EXPOSE 8080