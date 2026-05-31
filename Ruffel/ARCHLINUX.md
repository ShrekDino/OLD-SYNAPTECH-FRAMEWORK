# OpenMonoAgent on Arch Linux

## Overview

OpenMonoAgent has first-class support for Arch Linux. On Arch, the installer defaults to **Ollama provider mode** — a lightweight setup that uses your existing [Ollama](https://ollama.ai) instance as the LLM backend. No model download, no llama.cpp inference server, no GPU driver hassle.

## Quick Install

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/ShrekDino/OpenMonoAgent.ai/refs/heads/main/get-openmono.sh)
```

The installer will:

1. Install prerequisites via **pacman** (Docker, .NET 10, git, jq, ripgrep, cmake)
2. Build the OpenMono Docker agent image
3. Configure the Ollama provider settings
4. Set up shell integration

> **No sudo password prompts after the initial ones** — the installer handles Docker group membership, .NET installation, and symlinks.

### Manual Install (Step by Step)

If you prefer to do things manually:

```bash
# 1. Clone
git clone https://github.com/ShrekDino/OpenMonoAgent.ai.git ~/openmono.ai

# 2. Install .NET 10
curl -fsSL https://dot.net/v1/dotnet-install.sh | bash -s -- --channel 10.0 --install-dir "$HOME/.dotnet"
export DOTNET_ROOT="$HOME/.dotnet"
export PATH="$DOTNET_ROOT:$PATH"

# 3. Install Docker + tools
sudo pacman -S docker docker-compose git jq ripgrep cmake base-devel

# 4. Add yourself to docker group
sudo usermod -aG docker "$USER"
newgrp docker

# 5. Start Docker
sudo systemctl enable --now docker

# 6. Build the agent image
cd ~/openmono.ai/docker
docker compose build agent

# 7. Configure Ollama provider
mkdir -p ~/.openmono
cat > ~/.openmono/settings.json << 'EOF'
{
  "providers": {
    "ollama": {
      "endpoint": "http://localhost:11434",
      "model": "qwen3.5:9b",
      "active": true
    }
  },
  "permissions": {
    "tools": {
      "Bash": {
        "allow": ["git *", "dotnet *", "ls *", "cat *", "curl *"],
        "deny": ["rm -rf /", "sudo *"],
        "ask": ["sudo *", "systemctl *", "docker *"]
      }
    }
  },
  "auto_detect_code_graph": true,
  "verbose": false
}
EOF

# 8. Add to PATH
echo 'export PATH="$HOME/openmono.ai:$PATH"' >> ~/.bashrc
export PATH="$HOME/openmono.ai:$PATH"
```

## Ollama Provider Mode

This is the recommended mode on Arch Linux. The agent runs in Docker but connects to your **host's Ollama** instance.

### Requirements

- [Ollama](https://ollama.ai) installed and running
- At least one model pulled (e.g. `ollama pull qwen3.5:9b`)

### How it works

```
┌──────────────────────────────────┐
│  Docker Container (agent)        │
│  openmono CLI                    │
│  ↓ HTTP POST /v1/chat/completions│
└──────────────┬───────────────────┘
               │ network_mode: host
               ▼
┌──────────────────────────────────┐
│  Host Machine                    │
│  Ollama (port 11434)             │
│  GPU: 6GB RTX 3060 (partial)     │
│  Model: qwen3.5:9b               │
└──────────────────────────────────┘
```

The agent runs inside Docker with `network_mode: host`, giving it direct access to `localhost:11434` where Ollama is listening.

### Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| `providers.ollama.endpoint` | `http://localhost:11434` | Ollama API endpoint |
| `providers.ollama.model` | `qwen3.5:9b` | Model to use (change to any pulled model) |
| `providers.ollama.active` | `true` | Must be `true` to use Ollama provider |

Change model mid-session:
```bash
openmono config set llm.model qwen3.5:9b
```

Or via slash command in TUI:
```
/model qwen3.5:9b
```

### Available Models

List your downloaded models:
```bash
ollama list
```

Recommended models for coding:
- `qwen3.5:9b` — strong coding, fits 6GB VRAM
- `qwen3.5:4b` — lighter, faster on low VRAM
- `llama3.2:3b` — fastest option
- `deepseek-coder-v2` — specialized for code

## Full llama.cpp Mode

If you have 24GB+ VRAM or 24GB+ RAM and want the full bundled inference:

```bash
openmono setup --full
```

This will:
1. Download the appropriate model (~15-18 GB)
2. Build llama-server Docker image
3. Start the inference server
4. Configure OpenMono to use the local llama.cpp endpoint

## NVIDIA GPU on Arch

If you have an NVIDIA GPU and want GPU acceleration:

```bash
# Install drivers
sudo pacman -S nvidia-open nvidia-utils nvidia-container-toolkit

# Configure Docker
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Run setup with GPU mode
openmono setup --full --gpu
```

> **Note**: OpenMonoAgent's GPU mode requires 12GB+ VRAM minimum. With 6GB (RTX 3060), use **Ollama provider mode** instead.

## Troubleshooting

### Docker permission denied
```bash
sudo usermod -aG docker "$USER"
newgrp docker
```

### Ollama connection refused
```bash
systemctl --user enable --now ollama
curl http://localhost:11434/api/tags
```

### Agent can't reach Ollama from Docker
If using `network_mode: host` and still can't connect:
```bash
# Check if Ollama is listening on all interfaces
systemctl --user stop ollama
OLLAMA_HOST=0.0.0.0 ollama serve &
```

### OpenMono command not found
```bash
export PATH="$HOME/openmono.ai:$PATH"
# Or add to ~/.bashrc: echo 'export PATH="$HOME/openmono.ai:$PATH"' >> ~/.bashrc
```

### .NET build fails
```bash
export DOTNET_ROOT="$HOME/.dotnet"
export PATH="$DOTNET_ROOT:$PATH"
dotnet build ~/openmono.ai/OpenMono.sln
```

### Docker daemon not running
```bash
sudo systemctl enable --now docker
```

## Switching Between Modes

| Mode | Command | Use Case |
|------|---------|----------|
| Ollama (default) | `openmono setup --ollama` | Lightweight, uses existing Ollama |
| Full llama.cpp | `openmono setup --full` | Self-contained, bundled inference |
| Agent only | `openmono setup --agent` | Remote inference, dual-box |

Switch at any time — settings are stored in `~/.openmono/settings.json`.
