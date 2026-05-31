# Ruffel Mono Agent — Setup Guide

> **Last updated:** 2026-05-25  
> **Platforms:** Linux (Ubuntu, Arch, Fedora), macOS (Intel + Apple Silicon), Windows (WSL2), Docker

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Docker (All Platforms)](#docker-all-platforms)
- [Linux](#linux)
  - [Ubuntu / Debian](#ubuntu--debian)
  - [Arch Linux](#arch-linux)
  - [Fedora](#fedora)
- [macOS](#macos)
- [Windows (WSL2)](#windows-wsl2)
- [Building from Source](#building-from-source)
  - [Backend (.NET 10)](#backend-net-10)
  - [Terminal Client (TypeScript)](#terminal-client-typescript)
  - [VS Code Extension](#vs-code-extension)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

---

## Prerequisites

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 8 GB | 16–32 GB |
| GPU VRAM | 4 GB | 8–12 GB (RTX 3090 / A4000) |
| Disk space | 10 GB | 20 GB (includes model storage) |
| CPU | 4 cores | 8+ cores |
| Operating System | Linux kernel 5.x+ | Ubuntu 22.04+ / Arch / macOS 14+ |

Software requirements vary by installation method:

| Method | Requirements |
|--------|--------------|
| **Docker** | Docker Engine 24+ with NVIDIA Container Toolkit (for GPU) |
| **Native Linux** | .NET 10 SDK, Node.js 20+, llama.cpp, CUDA 12+ (GPU optional) |
| **Native macOS** | .NET 10 SDK, Node.js 20+, Metal-compatible GPU |
| **Windows (WSL2)** | WSL2 with Ubuntu, .NET 10 SDK, Node.js 20+, CUDA (Windows GPU via WSL2) |

---

## Docker (All Platforms)

Docker is the **recommended** installation method — it handles llama.cpp compilation, GPU configuration, and all dependencies automatically.

### 1. Install Docker

```bash
# Ubuntu / Debian
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

# macOS — install Docker Desktop from https://docs.docker.com/desktop/

# Windows — install Docker Desktop with WSL2 backend
```

### 2. Install NVIDIA Container Toolkit (for GPU acceleration)

```bash
# Ubuntu / Debian
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Arch Linux
sudo pacman -S nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Verify
docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
```

### 3. Clone and Start

```bash
git clone https://github.com/ShrekDino/Ruffel.git
cd Ruffel

# Start llama.cpp + agent
docker compose --profile full up -d

# Verify LLM is running
curl http://localhost:7474/health

# Launch the terminal client
docker exec -it ruffel-agent ruffel
```

### Docker Compose Profiles

| Profile | Services | Use Case |
|---------|----------|----------|
| `full` | llama-server + ruffel-agent | Full stack with GPU inference |
| `llama-server` | llama-server only | If running the agent natively |
| `cpu` | llama-server (CPU mode) + ruffel-agent | No GPU available |

```bash
# CPU-only mode
docker compose --profile cpu up -d

# llama-server only (for native agent)
docker compose --profile llama-server up -d
```

---

## Linux

### Ubuntu / Debian

```bash
# 1. Install .NET 10 SDK
wget https://dot.net/v1/dotnet-install.sh
chmod +x dotnet-install.sh
./dotnet-install.sh --channel 10.0
echo 'export PATH=$HOME/.dotnet:$PATH' >> ~/.bashrc
source ~/.bashrc
dotnet --version  # Should show 10.x

# 2. Install Node.js 20+
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
node --version  # Should show 20.x

# 3. Install llama.cpp
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
mkdir build && cd build
cmake .. -DLLAMA_CUDA=ON -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
sudo make install
cd ../..

# 4. Download a model (Qwen2.5-Coder-14B recommended)
mkdir -p models
wget -O models/qwen2.5-coder-14b-q4.gguf \
  https://huggingface.co/Qwen/Qwen2.5-Coder-14B-Instruct-GGUF/resolve/main/qwen2.5-coder-14b-instruct-q4_k_m.gguf

# 5. Build the backend
dotnet build src/OpenMono.Cli

# 6. Build the terminal client
cd terminal
npm install
npm run compile
npm link   # Now `ruffel` is available globally
cd ../..

# 7. Start llama.cpp and run
llama-server -m models/qwen2.5-coder-14b-q4.gguf --port 7474 --n-gpu-layers 99 &
ruffel
```

### Arch Linux

```bash
# 1. Install prerequisites
sudo pacman -S dotnet-sdk nodejs npm base-devel cmake

# 2. Install llama.cpp (via AUR or build manually)
yay -S llama.cpp-cuda  # or llama.cpp for CPU-only

# 3. Clone, build, and run
git clone https://github.com/ShrekDino/Ruffel.git
cd Ruffel
dotnet build src/OpenMono.Cli

cd terminal
npm install && npm run compile && npm link
cd ../..

llama-server -m /path/to/model.gguf --port 7474 --n-gpu-layers 99 &
ruffel
```

### Fedora

```bash
# 1. Install .NET 10
sudo dnf install dotnet-sdk-10.0

# 2. Install Node.js
sudo dnf install nodejs

# 3. Install llama.cpp
sudo dnf install cmake gcc-c++ cuda-toolkit
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
cmake -B build -DLLAMA_CUDA=ON
cmake --build build --config Release
sudo cmake --install build
cd ..

# 4. Build and run (same as Ubuntu steps 5-8)
```

---

## macOS

### Apple Silicon (M1/M2/M3/M4)

```bash
# 1. Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install .NET 10 SDK
brew install --cask dotnet-sdk

# 3. Install Node.js
brew install node

# 4. Install llama.cpp
brew install llama.cpp

# 5. Clone and build
git clone https://github.com/ShrekDino/Ruffel.git
cd Ruffel
dotnet build src/OpenMono.Cli

cd terminal
npm install && npm run compile && npm link
cd ../..

# 6. Download model and run
mkdir -p models
# Download GGUF model (e.g., Qwen2.5-Coder-7B for 8GB Macs)
llama-server -m models/model.gguf --port 7474 --n-gpu-layers 99 --metal &
ruffel
```

### Intel Mac

Same as Apple Silicon but omit `--metal` flag for llama-server. GPU acceleration may not be available; use `--n-gpu-layers 0` for CPU-only.

---

## Windows (WSL2)

```powershell
# 1. Install WSL2
wsl --install -d Ubuntu-24.04

# 2. Open WSL2 terminal
wsl

# 3. Install .NET 10 SDK (inside WSL2)
wget https://dot.net/v1/dotnet-install.sh
chmod +x dotnet-install.sh
./dotnet-install.sh --channel 10.0
echo 'export PATH=$HOME/.dotnet:$PATH' >> ~/.bashrc
source ~/.bashrc

# 4. Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 5. For GPU acceleration in WSL2:
#    - Install NVIDIA drivers on Windows (not WSL2)
#    - Install CUDA in WSL2:
wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get install -y cuda-toolkit-12-2

# 6. Build and run (same as Ubuntu steps 5-8)
```

---

## Building from Source

### Backend (.NET 10)

```bash
cd src/OpenMono.Cli
dotnet restore
dotnet build

# Build with Native AOT (smaller binary, faster startup)
dotnet publish -c Release -r linux-x64 --self-contained

# Run tests
dotnet test src/OpenMono.Tests
```

### Terminal Client (TypeScript)

```bash
cd terminal
npm install           # Install dependencies
npm run compile       # Build with esbuild → dist/index.js
npm link              # Make `ruffel` globally available

# Development with watch mode
npm run dev

# Type check
npx tsc --noEmit
```

### VS Code Extension

```bash
cd opencode/sdks/vscode
npm install
npm run compile       # Build with esbuild → dist/extension.js

# Install in VS Code:
# Option 1: Copy dist/ to ~/.vscode/extensions/ruffel-mono-agent/
# Option 2: Run as Extension Host
code .                 # Open in VS Code, then F5 to run
```

---

## Configuration

### Minimal Configuration

The backend will work with zero configuration if:
- An LLM server is running at `http://localhost:7474`
- The terminal client can find the `openmono` binary on PATH

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENMONO_ENDPOINT` | `http://localhost:7474` | LLM server endpoint |
| `OPENMONO_MODEL` | (auto-detected) | Model name override |
| `OPENMONO_API_KEY` | (none) | API key for cloud providers or auth |
| `OPENMONO_WORKSPACE` | CWD | Working directory |
| `OPENMONO_RENDERER` | `terminal` | Renderer mode: `terminal`, `tui`, `vscode`, `rpc` |
| `OPENMONO_DATA_DIR` | `~/.openmono` | Data directory for sessions, memory |
| `OPENMONO_CONTEXT_SIZE` | 196608 | LLM context window size |
| `OPENMONO_MAX_OUTPUT_TOKENS` | 16384 | Maximum output tokens |

### Settings File

```json
// ~/.openmono/settings.json
{
  "llm": {
    "endpoint": "http://localhost:7474",
    "model": "qwen2.5-coder:14b",
    "contextSize": 196608,
    "maxOutputTokens": 16384,
    "temperature": 0.7,
    "topP": 0.8
  },
  "renderer": "rpc",
  "verbose": false,
  "workingDirectory": "/home/user/projects"
}
```

### CLI Flags

```bash
openmono --rpc --workdir /path/to/project
openmono --vscode
openmono --endpoint http://localhost:7474 --model qwen2.5-coder:14b
```

See [CONFIG.md](CONFIG.md) for the complete configuration reference.

---

## Troubleshooting

### "Could not load openmono binary"

```bash
# Verify the binary exists
ls -la src/OpenMono.Cli/bin/Debug/net10.0/openmono

# Build if missing
dotnet build src/OpenMono.Cli

# Specify path explicitly
ruffel --binary ./src/OpenMono.Cli/bin/Debug/net10.0/openmono
```

### "LLM server not reachable at http://localhost:7474"

```bash
# Check if llama-server is running
curl http://localhost:7474/health

# Start if not running
docker compose up -d llama-server

# Or direct llama.cpp
llama-server -m models/model.gguf --port 7474 --n-gpu-layers 99
```

### "Permission denied for Bash tool every time"

```bash
# When prompted "Allow Bash? [y/N/a/d]":
#   y = allow once
#   a = always allow this session
#   d = always deny this session
#   A/always = allow all for this session

# To reset session permissions, start a new session:
/exit
ruffel
```

### "Out of memory / Context too long"

```bash
# Use the /compact slash command to summarize conversation
/compact

# Or start a fresh session
/exit
ruffel

# Reduce context size in settings
# ~/.openmono/settings.json → "contextSize": 131072
```

### "GPU not being used for inference"

```bash
# Verify CUDA is available
nvidia-smi

# Check llama-server logs
docker logs ruffel-llama-server-1 2>&1 | grep -i gpu

# Ensure nvidia-container-toolkit is installed
docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi

# For native, pass --n-gpu-layers flag
llama-server -m model.gguf --port 7474 --n-gpu-layers 99
```

### "JSON-RPC communication broken — garbled output"

This indicates a `Console.Write` call from a library is corrupting the stdio protocol.

```bash
# Check stderr for diagnostic messages
ruffel 2>/tmp/ruffel-stderr.log

# The --rpc mode automatically isolates Console.Write → stderr
# If running in another mode, ensure no stray Console.WriteLine() calls
```

---

## Next Steps

- [Architecture Overview](ARCHITECTURE.md) — Understand the system design
- [API Reference](docs/API.md) — JSON-RPC protocol specification
- [Configuration Guide](CONFIG.md) — All configuration options
- [Contributing Guide](CONTRIBUTING.md) — How to contribute
- [Development Guide](docs/DEVELOPMENT.md) — Setting up a dev environment
