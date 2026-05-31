FROM ubuntu:24.04 AS base

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    ninja-build \
    pkg-config \
    curl \
    zip \
    unzip \
    tar \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

FROM base AS vulkan-sdk

RUN apt-get update && apt-get install -y --no-install-recommends \
    libvulkan-dev \
    vulkan-validationlayers-dev \
    libvulkan1 \
    mesa-vulkan-drivers \
    && rm -rf /var/lib/apt/lists/*

FROM vulkan-sdk AS deps

RUN apt-get update && apt-get install -y --no-install-recommends \
    libsdl2-dev \
    libpipewire-0.3-dev \
    libdbus-1-dev \
    libspa-0.2-dev \
    shaderc \
    libspdlog-dev libfmt-dev libglm-dev nlohmann-json3-dev cli11-dev \
    && rm -rf /var/lib/apt/lists/*

FROM deps AS vcpkg

ENV VCPKG_ROOT=/opt/vcpkg
RUN git clone https://github.com/microsoft/vcpkg.git ${VCPKG_ROOT} \
    && cd ${VCPKG_ROOT} \
    && ./bootstrap-vcpkg.sh \
    && ./vcpkg integrate install

FROM vcpkg AS build

WORKDIR /workspace
COPY vcpkg.json /workspace/
RUN ${VCPKG_ROOT}/vcpkg install --triplet=x64-linux

COPY . /workspace/
RUN cmake --preset ci && cmake --build build/ci -j$(nproc)

FROM build AS test
RUN ctest --preset ci

FROM ubuntu:24.04 AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    libvulkan1 \
    mesa-vulkan-drivers \
    libsdl2-2.0-0 \
    libpipewire-0.3-0 \
    libdbus-1-3 \
    libspa-0.2-modules \
    pipewire \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /workspace/build/ci/src/freegen /usr/local/bin/

ENTRYPOINT ["freegen"]
