<div align="center">
  <h1>🤖 Ruffel Mono Agent</h1>
  <p><strong>Local-first AI coding agent. Zero cloud. Zero cost. Full offline autonomy.</strong></p>
  <p><sub>Powered by .NET 10  ·  Local inference via llama.cpp  ·  AGPL-3.0</sub></p>
</div>

<div align="center">
  <a href="#quickstart">Quickstart</a> ·
  <a href="ARCHITECTURE.md">Architecture</a> ·
  <a href="docs/API.md">API</a> ·
  <a href="SETUP.md">Setup</a> ·
  <a href="CONFIG.md">Configuration</a> ·
  <a href="CONTRIBUTING.md">Contributing</a> ·
  <a href="ROADMAP.md">Roadmap</a>
</div>

<br>

<div align="center">

[![.NET 10](https://img.shields.io/badge/.NET-10-512BD4?logo=dotnet&logoColor=white)](https://dotnet.microsoft.com/)
[![AGPL-3.0](https://img.shields.io/badge/license-AGPL--3.0-green)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED?logo=docker&logoColor=white)](SETUP.md#docker)
[![llama.cpp](https://img.shields.io/badge/inference-llama.cpp-black?logo=llama&logoColor=white)](https://github.com/ggerganov/llama.cpp)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-blue)](SETUP.md)
[![Status](https://img.shields.io/badge/status-beta-FF8C00)]()
[![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen)](CONTRIBUTING.md)

</div>

---

## Overview

**Ruffel Mono Agent** is a production-grade, completely offline local-first AI coding agent. It runs entirely on your hardware — no cloud telemetry, no API subscriptions, no data leaves your machine. The entire pipeline from LLM inference to tool execution to file manipulation lives in a single Docker container (or native install).

The system is split into two communicating processes:

| Component | Language | Role |
|-----------|----------|------|
| **`OpenMono.Cli` (backend)** | C# 13 (.NET 10) | LLM orchestration, tool execution (20+ tools), session management, file history with atomic undo, permission enforcement, secret scanning |
| **`ruffel` (frontend)** | TypeScript (Node.js) | Terminal UI: REPL input, streaming output rendering, permission dialogs, session lifecycle. Also available as a [VS Code extension](ARCHITECTURE.md#vs-code-extension) |

The two halves communicate exclusively over **line-delimited JSON-RPC 2.0 on stdio** — no network ports, no HTTP, no gRPC. This eliminates firewall issues, port contention, and attack surface.

---

## Quickstart

### Docker (Recommended)

```bash
# 1. Clone the repo
git clone https://github.com/ShrekDino/Ruffel.git
cd Ruffel

# 2. Start the full stack (llama.cpp + agent)
docker compose --profile full up -d

# 3. Verify the LLM is ready
curl http://localhost:7474/health

# 4. Launch the terminal client
docker exec -it ruffel-agent ruffel
```

### Native Linux

```bash
# Prerequisites: .NET 10 SDK, Node.js 20+, llama.cpp

# 1. Build the backend
dotnet build src/OpenMono.Cli

# 2. Build the terminal client
cd terminal
npm install && npm run compile
npm link   # makes `ruffel` available globally

# 3. Start llama.cpp (example with Qwen2.5-Coder)
docker compose up -d llama-server

# 4. Run
ruffel
```

### macOS / Windows

See [SETUP.md](SETUP.md#macos) and [SETUP.md](SETUP.md#windows) for platform-specific guides.

### VS Code Extension

```bash
cd opencode/sdks/vscode
npm install
npm run compile
# Install the extension from the `dist/` directory or copy to your VS Code extensions folder
```

---

## Features

### Core Engine

| Feature | Description |
|---------|-------------|
| **Local LLM Inference** | Runs via llama.cpp with full GPU offload (CUDA, Metal, Vulkan). Supports any GGUF model. Auto-detects model from server `/props`. |
| **20+ Built-in Tools** | File read/write/edit, glob, grep, Bash, Web fetch/search, LSP code intelligence, Roslyn C# analysis, Git operations, Todo tracking, Memory persistence, MCP server integration, Playbook workflows |
| **Atomic Undo** | Every file modification is tracked via `FileHistory.RevertAsync()`. Undo the last N actions with a single command. |
| **Permission System** | Dual-tier: legacy 3-level (AutoAllow/Ask/Deny) + capability-based (file reads, network egress, process execution, VCS mutations). Supports granular session-wide allow/deny rules. |
| **Secret Scanning** | `SecretScanner.Redact()` scrubs 30+ secret patterns (AWS keys, GitHub PATs, OpenAI tokens, SSH keys) from all output crossing the process boundary. Applied at the serialization level in the JSON-RPC server. |
| **Tool Caching** | Read-only tool results (file reads, grep, glob) are cached with input-aware cache keys. Cache invalidation on file writes. |
| **Doom Loop Detection** | Detects repeated identical tool calls and interrupts the pattern — prevents LLM infinite loops. |
| **Plan Mode** | When active, write tools are blocked. The agent must investigate and produce a plan before making changes. |
| **Checkpointing & Compaction** | Dual mechanism for context window management: checkpoints preserve conversation structure with summaries; compaction destructively replaces old turns. |
| **Session Persistence** | All sessions saved as JSONL files. Full session resume support via `/resume`. Export to markdown/JSON/HTML. |

### Terminal Client

| Feature | Description |
|---------|-------------|
| **Streaming Output** | Real-time token-by-token streaming from the LLM. Thinking/reasoning blocks rendered distinctly. |
| **Permission Dialogs** | Inline [y/N/a/d] prompts for tool permissions. Supports allow, deny, always-allow, always-deny. |
| **REPL Interface** | Read-eval-print loop with command history. Slash commands: `/undo`, `/exit`, `/help`. |
| **Turn Cancellation** | Ctrl+C cancels the current running turn without killing the daemon. |
| **MEMORY.md Seeding** | Automatically reads `.opencode/MEMORY.md` on session start for persistent context. |

### VS Code Extension

| Feature | Description |
|---------|-------------|
| **WebView Chat Panel** | Full chat UI with streaming responses, permission buttons, undo toolbar. |
| **Workspace Automation** | Auto-sends file context on tab switch and save (300ms debounce). |
| **6 Commands** | Open chat, New session, Add file to context, Undo last action, Show logs, Open terminal. |
| **Keybindings** | `Cmd+Esc` open chat, `Cmd+Shift+Esc` new session, `Cmd+Shift+Z` undo. |
| **Permission Fallback** | WebView unavailable? Falls back to VS Code notification dialogs. |

---

## Repository Structure

```
Ruffel/
├── src/
│   └── OpenMono.Cli/          # .NET 10 backend
│       ├── Config/             # AppConfig, ConfigLoader, JsonOptions
│       ├── Rendering/          # IRenderer + implementations
│       │   ├── TerminalJsonRpcServer.cs   # JSON-RPC server (--rpc mode)
│       │   ├── OpenCodeBridgeRenderer.cs  # Terminal IRenderer
│       │   ├── VscodeJsonRpcServer.cs     # JSON-RPC server (--vscode mode)
│       │   └── VscodeRenderer.cs          # VS Code IRenderer
│       ├── Session/            # SessionState, ConversationLoop, TurnJournal
│       ├── Tools/              # ToolRegistry, ToolDispatcher, 20+ ITool impls
│       ├── Permissions/        # PermissionEngine, capability system
│       ├── History/            # FileHistory with atomic snapshots
│       ├── Llm/                # LLM clients (OpenAI-compat, Anthropic)
│       ├── Mcp/                # MCP server integration
│       ├── Memory/             # MemoryStore, memory index
│       ├── Hooks/              # Pre/post tool hooks, session hooks
│       └── Playbooks/          # Step-by-step workflow engine
│
├── terminal/                   # Terminal client (TypeScript)
│   ├── src/
│   │   ├── index.ts              # CLI entry point
│   │   ├── AgentController.ts     # RPC orchestrator
│   │   ├── JsonRpcTransport.ts    # Byte-level buffer transport
│   │   └── TerminalUI.ts          # REPL + permission prompts
│   ├── bin/ruffel                 # Shell wrapper
│   ├── package.json
│   ├── tsconfig.json
│   └── esbuild.js
│
├── opencode/
│   └── sdks/vscode/           # VS Code extension (TypeScript) (submodule)
│           └── src/
│               ├── extension.ts           # Extension entry point
│               ├── AgentSession.ts        # Session orchestrator
│               ├── JsonRpcTransport.ts     # Byte-level buffer transport
│               └── WebViewProvider.ts      # WebView chat UI
│
├── docker/                    # Docker compose files for llama.cpp
├── docs/                      # Documentation
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── CONFIG.md
│   ├── SETUP.md
│   ├── DEVELOPMENT.md
│   ├── COMPREHENSIVE_REFERENCE.md
│   └── CHANGELOG.md
├── ruffel-mono-agent.sh       # Bootstrap script
├── README.md
├── CONTRIBUTING.md
├── SECURITY.md
└── LICENSE
```

---

## Communication Protocol

The frontend and backend communicate over **JSON-RPC 2.0 on stdio**. Every message is a single line-delimited JSON object.

### Client → Server

| Method | Purpose | Backend Handler |
|--------|---------|-----------------|
| `session/start` | Initialize a session | `SessionManager.CreateSession()` |
| `session/status` | Get session state | `SessionState` properties |
| `session/undo` | Revert last N file changes | `FileHistory.RevertAsync(count)` |
| `session/stop` | Graceful shutdown | `CancellationTokenSource.Cancel()` |
| `input/send` | Send user text input | `ConversationLoop.RunTurnAsync()` |
| `input/cancel` | Cancel running turn | Turn-level `CancellationTokenSource.Cancel()` |
| `context/addFile` | Register file context | Message injection |
| `tool/execute` | Direct tool invocation | `ToolDispatcher.ExecuteSingleToolAsync()` |
| `permission/respond` | User permission decision | TCS resolution |

### Server → Client

Notifications use namespaced method names (no `kind` field — the method IS the type):

| Method | Purpose |
|--------|---------|
| `text/delta` | Streaming assistant text |
| `text/thinking` | Reasoning tokens |
| `text/markdown` | Markdown content |
| `text/diff` | File diff |
| `turn/start` / `turn/end` | Turn lifecycle |
| `tool/start` / `tool/result` / `tool/crash` | Tool lifecycle |
| `permission/ask` | Permission prompt (TCS-blocked) |
| `question/ask` | User question (TCS-blocked) |
| `session/welcome` / `session/update` / `session/error` / `session/warning` / `session/info` / `session/debug` | Session state |

Full protocol specification: [docs/API.md](docs/API.md)

---

## Architecture Highlights

### Stray Log Isolation

In `--rpc` mode, the backend isolates stray `Console.Write` calls:

```csharp
var realStdout = Console.Out;  // Save original stdout
Console.SetOut(Console.Error); // Redirect all future Console.Out to stderr
_stdout = realStdout;          // Server uses original stdout for JSON-RPC
```

This guarantees that any rogue `Console.WriteLine()` from third-party libraries routes to stderr, never corrupting the JSON-RPC protocol on stdout.

### Byte-Level Stream Buffer

Both frontends use explicit `Buffer.concat()` accumulation on `data` events, scanning for `\n` (byte 0x0A) in a while-loop — no `readline` dependency. This ensures zero line-boundary loss regardless of TCP segmentation or write atomicity.

### Serialization-Level Secret Redaction

`SecretScanner.Redact()` is applied to the **entire serialized JSON string** before writing to stdout — a single choke point that catches all output paths, including error responses and notifications.

### TaskCompletionSource Permission Freeze

Instead of polling, the permission system uses `ConcurrentDictionary<string, TaskCompletionSource<PermissionResponse>>`. When the agent requests permission:

1. A TCS is created and stored by `callId`
2. A `permission/ask` notification is sent to the frontend
3. The backend awaits `tcs.Task.WaitAsync(ct)` — **zero CPU usage while blocked**
4. The frontend shows a dialog (terminal: [y/N/a/d], WebView: buttons)
5. User responds, `permission/respond` arrives via stdin
6. TCS resolves, execution resumes instantly

---

## Performance & Resource Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| **RAM** | 8 GB | 16–32 GB |
| **GPU VRAM** | 4 GB | 8–12 GB |
| **Disk** | 10 GB | 20 GB (for models) |
| **CPU** | 4 cores | 8+ cores |
| **Model size** | 7B parameters (Q4) | 14B–34B parameters (Q4) |

The system uses llama.cpp with GPU offload. Models run at 20–40 tok/s on a single RTX 3090 for 14B-parameter models.

---

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for our contributing guidelines, code of conduct, and development workflow.

## Security

See [SECURITY.md](SECURITY.md) for our security policy and vulnerability reporting process.

## License

GNU Affero General Public License v3.0 — see [LICENSE](LICENSE) for details.

---

<div align="center">
  <sub>Built with ❤️ by <a href="https://github.com/ShrekDino">ShrekDino</a> and the Ruffel community</sub>
</div>
