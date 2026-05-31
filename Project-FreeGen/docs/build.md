# Build Guide

## Prerequisites

### Linux (Ubuntu 24.04 / SteamOS / Arch)

```bash
# Required packages
sudo apt-get install -y \
    build-essential \
    cmake \
    ninja-build \
    pkg-config \
    git \
    libvulkan-dev \
    vulkan-validationlayers-dev \
    libsdl2-dev \
    libpipewire-0.3-dev \
    libdbus-1-dev \
    glslang-tools \
    libspa-0.2-dev

# Optional (development)
sudo apt-get install -y \
    clang-format \
    clang-tidy \
    doxygen \
    python3-pip

pip3 install mkdocs mkdocs-material
```

### Windows

1. Install [Visual Studio 2022](https://visualstudio.microsoft.com/) with C++ workload
2. Install [Vulkan SDK](https://vulkan.lunarg.com/sdk/home)
3. Install [git](https://git-scm.com/)
4. Install [CMake](https://cmake.org/download/)

## Build Steps

### Using manage.sh (Linux)

```bash
# Clone
git clone https://github.com/ShrekDino/Project-FreeGen.git
cd Project-FreeGen

# Build debug
./scripts/manage.sh build debug

# Build release
./scripts/manage.sh build release

# Run
./scripts/manage.sh run

# Run tests
./scripts/manage.sh test
```

### Using CMake directly

```bash
# Debug
cmake -B build/debug -DCMAKE_BUILD_TYPE=Debug
cmake --build build/debug -j$(nproc)

# Release
cmake -B build/release -DCMAKE_BUILD_TYPE=Release
cmake --build build/release -j$(nproc)
```

### Using CMake presets

```bash
cmake --preset debug
cmake --build build/debug
ctest --preset debug
```

### Using Docker

```bash
# Enter development shell
docker compose run --rm shell

# Build inside container
./scripts/manage.sh build

# Or build-only container
docker compose up build
```

## CMake Options

| Option | Default | Description |
|--------|---------|-------------|
| `FREEGEN_ENABLE_TESTS` | ON | Build unit tests |
| `FREEGEN_BUILD_SHADERS` | ON | Compile GLSL to SPIR-V at build time |
| `FREEGEN_ENABLE_SANITIZERS` | OFF | Enable ASan + UBSan |
| `FREEGEN_WARNINGS_AS_ERRORS` | OFF | Treat warnings as errors |

## Verification

After building, verify the application works:

```bash
# Should print version and launch a window
./build/release/src/freegen --version

# List available effects
./build/release/src/freegen --list-effects

# List capture sources
./build/release/src/freegen --list-sources
```

## Troubleshooting

### Vulkan not found

Ensure Vulkan SDK is installed and `VULKAN_SDK` environment variable is set:

```bash
# Ubuntu
sudo apt install libvulkan-dev vulkan-validationlayers-dev

# Verify
vulkaninfo --summary
```

### PipeWire not found

```bash
sudo apt install libpipewire-0.3-dev pipewire
systemctl --user enable --now pipewire
```

### Shader compilation fails

Ensure `glslc` is available:

```bash
# Ubuntu
sudo apt install glslang-tools

# Verify
glslc --version
```
