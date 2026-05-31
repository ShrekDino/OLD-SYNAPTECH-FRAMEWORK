# Changelog

All notable changes to Ruffel Mono Agent are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] — 2026-05-25

### Added

#### Core Engine
- **JSON-RPC 2.0 over stdio**: Two implementations — `TerminalJsonRpcServer` (for `--rpc` mode) and `VscodeJsonRpcServer` (for `--vscode` mode). Both support 9 methods: `session/start`, `session/status`, `session/undo`, `input/send`, `input/cancel`, `context/addFile`, `tool/execute`, `permission/respond`, `session/stop`.
- **Stray log isolation**: `Console.SetOut(Console.Error)` in terminal mode redirects all rogue `Console.Write` calls to stderr, protecting the JSON-RPC protocol on stdout.
- **Serialization-level secret redaction**: `SecretScanner.Redact()` applied to the entire serialized JSON string before writing to stdout — a single choke point covering all output paths.
- **20+ built-in tools**: FileRead, FileWrite, FileEdit, Glob, Grep, Bash, Agent, Todo, MemorySave, WebFetch, WebSearch, ListDirectory, ApplyPatch, EnterPlanMode, ExitPlanMode, Lsp, Roslyn, Playbook, AskUser, and more.
- **Atomic undo**: `FileHistory.RevertAsync(count)` tracks every file modification with content snapshots for lossless rollback.
- **Dual permission system**: Legacy 3-level (AutoAllow/Ask/Deny) + capability-based (file, network, process, VCS, memory, agent spawn). Session-wide allow/deny with denial tracking.
- **Doom loop detection**: Identical tool calls repeated 3+ times are detected and blocked.
- **Tool result caching**: Read-only tool results cached with input-aware keys; cache invalidation on dependent file writes.
- **Plan mode**: Write tools blocked when active; agent must investigate and plan before making changes.
- **Checkpointing and compaction**: Dual mechanism for context window management at 65%/80% thresholds.
- **Session persistence**: JSONL format with session index, full resume support, markdown/JSON/HTML export.
- **MCP server integration**: Dynamic registration of MCP tools via user-configured servers.
- **Playbook engine**: Step-by-step workflow definitions with conditional execution, gates, and state tracking.

#### Terminal Client (`terminal/`)
- **REPL interface** with streaming token-by-token output rendering.
- **Permission dialogs**: Inline [y/N/a/d] prompts supporting allow, deny, allow-all, deny-all.
- **Turn cancellation**: Ctrl+C cancels the running turn without killing the daemon.
- **MEMORY.md seeding**: Auto-reads `.opencode/MEMORY.md` for persistent session context.
- **Byte-level buffer transport**: `Buffer.concat()` accumulation with `\n` scan loop — no `readline` dependency.
- **Slash commands**: `/undo`, `/exit`, `/help`.

#### VS Code Extension (`opencode/sdks/vscode/`)
- **WebView chat panel** in activity bar with streaming responses.
- **6 commands**: Open chat, New session, Add file to context, Undo last action, Show logs, Open terminal.
- **Workspace context automation**: `onDidChangeActiveTextEditor` + `onDidSaveTextDocument` with 300ms debounce.
- **Keybindings**: `Cmd+Esc` (chat), `Cmd+Shift+Esc` (new session), `Cmd+Shift+Z` (undo), `Cmd+Alt+K` (add file to context).
- **Dedicated OutputChannel** for backend stderr logs.
- **Permission fallback**: `showInformationMessage` dialog when WebView is unavailable.

#### Docker
- **Full-stack compose profile**: llama-server + ruffel-agent with GPU pass-through.
- **CPU-only profile** for systems without GPU.
- **llama-server-only profile** for native agent usage.

#### Documentation
- `README.md` — Complete project overview with badges, architecture, quick start, feature table.
- `ARCHITECTURE.md` — Full system architecture with data flow, component descriptions, 16 sections.
- `SETUP.md` — Platform-specific setup (Ubuntu, Arch, Fedora, macOS, Windows/WSL2, Docker).
- `CONFIG.md` — All configuration options (CLI flags, env vars, settings.json).
- `docs/API.md` — Complete JSON-RPC 2.0 protocol specification with 20+ notification types.
- `docs/DEVELOPMENT.md` — Environment setup, building, debugging, testing, profiling, release process.
- `CONTRIBUTING.md` — Code of conduct, coding standards, PR process, testing guidelines.
- `SECURITY.md` — Threat model, secret scanning patterns, vulnerability reporting process.
- `CHANGELOG.md` — Version history.

### Architecture

- **Two-process design**: TypeScript frontend ↔ C# backend over JSON-RPC on stdio. No network ports, no HTTP, no gRPC.
- **Separation of renderers**: `OpenCodeBridgeRenderer` + `TerminalJsonRpcServer` for terminal mode; `VscodeRenderer` + `VscodeJsonRpcServer` for VS Code mode. Both share the same `ConversationLoop`, `ToolDispatcher`, and core engine.
- **Configuration hierarchy**: CLI flags → env vars → config file → project settings → user settings → defaults.

### ToolDispatcher

- Central tool execution pipeline integrating schema validation, sanity checks, permission engine, journal recording, hook execution, caching, artifact storage, and doom loop detection.

### License

- GNU Affero General Public License v3.0
