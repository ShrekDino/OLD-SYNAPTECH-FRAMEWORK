# Ruffel Mono Agent — Architecture

> **Version:** 0.1.0 (Beta)  
> **Last updated:** 2026-05-25

---

## 1. System Overview

Ruffel Mono Agent is a **two-process architecture** where a TypeScript frontend communicates with a .NET 10 backend over JSON-RPC 2.0 on stdio.

```
┌─────────────────────────────┐     JSON-RPC 2.0      ┌────────────────────────────────────────────┐
│    Frontend (TypeScript)    │◄──────────────────────►│         Backend (C# 13 / .NET 10)           │
│                             │    line-delimited      │                                            │
│  ┌───────────────────────┐  │      stdin/stdout      │  ┌──────────────────────────────────────┐  │
│  │ TerminalUI / WebView  │  │                        │  │ TerminalJsonRpcServer /               │  │
│  │  (REPL / Chat UI)    │  │                        │  │ VscodeJsonRpcServer                   │  │
│  └──────────┬────────────┘  │                        │  │  (stdin/stdout JSON-RPC dispatcher)   │  │
│             │               │                        │  └──────────────┬───────────────────────┘  │
│  ┌──────────┴────────────┐  │                        │                 │                          │
│  │ AgentController /     │  │                        │  ┌──────────────┴───────────────────────┐  │
│  │ AgentSession          │  │                        │  │ OpenCodeBridgeRenderer /              │  │
│  │  (orchestrator)       │  │                        │  │ VscodeRenderer                        │  │
│  └──────────┬────────────┘  │                        │  │  (IRenderer → JSON-RPC notifications)  │  │
│             │               │                        │  └──────────────┬───────────────────────┘  │
│  ┌──────────┴────────────┐  │                        │                 │                          │
│  │ JsonRpcTransport      │  │                        │  ┌──────────────┴───────────────────────┐  │
│  │  (byte-level buffer)  │  │                        │  │ ConversationLoop                     │  │
│  └───────────────────────┘  │                        │  │  (RunTurnAsync → LLM → tools → loop)  │  │
│                             │                        │  └──────────────────────────────────────┘  │
│  ┌───────────────────────┐  │                        │                                            │
│  │ readline / WebView    │  │                        │  ┌──────────────┐ ┌────────────┐ ┌───────┐  │
│  │  (I/O capture)        │  │                        │  │ ToolRegistry │ │SessionMgr  │ │ LLM  │  │
│  └───────────────────────┘  │                        │  │ (20+ tools)  │ │(JSONL save)│ │Client │  │
│                             │                        │  └──────────────┘ └────────────┘ └───────┘  │
└─────────────────────────────┘                        └────────────────────────────────────────────┘
```

### 1.1 Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **JSON-RPC over stdio, not HTTP** | Zero network surface. No ports, no firewall, no TLS, no contention. stdio is the only serialized pipe between two processes on the same machine. |
| **Two processes, not one** | The frontend (TypeScript) handles all user I/O; the backend (C#) handles all agent logic. If the agent crashes, the UI stays alive. If the UI restarts, the agent can resume. Clean separation of concerns. |
| **C# 13 / .NET 10 for backend** | Native AOT compilation, source-generated JSON serialization, `Task`-based concurrency, `SemaphoreSlim` for lock-free writes. .NET 10's `WaitAsync` enables the TCS permission freeze pattern. |
| **TypeScript for frontend** | Both the terminal client (Node.js) and VS Code extension (VS Code API) share the same JSON-RPC transport. The terminal client compiles via esbuild to a single 15KB JS bundle. |
| **Byte-level stream buffers** | Avoids `readline` module entirely. Raw `Buffer.concat()` accumulation ensures zero line-boundary loss regardless of write atomicity. |
| **`Console.SetOut(Console.Error)` isolation** | Catches all rogue `Console.Write` calls from third-party libraries before they corrupt the JSON-RPC protocol. |

---

## 2. Component Architecture

### 2.1 Backend: OpenMono.Cli (`src/OpenMono.Cli/`)

#### 2.1.1 Entry Point (`Program.cs`)

```csharp
// Simplified flow
Program.Main(args)
  → Parse flags (--vscode, --rpc, --tui, --classic, --workdir, etc.)
  → RunAgentAsync()
    → ConfigLoader.Load() → AppConfig
    → TryDetectActualModelAsync() → auto-detect model from /props
    → SessionManager.CreateSession() → SessionState
    → Register all tools (FileReadTool, BashTool, ...)
    → Register MCP servers, playbooks, hooks
    → Build system prompt (OPENMONO.md, memory, git context)
    → Create ConversationLoop
    → Depending on renderer mode:
      ├── RendererMode.Vscode: VscodeRenderer + VscodeJsonRpcServer
      ├── RendererMode.Rpc:    OpenCodeBridgeRenderer + TerminalJsonRpcServer
      ├── RendererMode.Tui:    AnsiTuiRenderer (full-screen TUI)
      └── RendererMode.Terminal: TerminalRenderer (scrolling REPL)
    → Serve JSON-RPC (for Vscode/Rpc modes) or enter interactive loop
```

#### 2.1.2 JSON-RPC Server

Two server implementations exist:

**`TerminalJsonRpcServer`** (for `--rpc` mode):
- Dispatches 9 methods: `session/start`, `session/status`, `session/undo`, `input/send`, `input/cancel`, `context/addFile`, `tool/execute`, `permission/respond`, `session/stop`
- Stray log isolation: `Console.SetOut(Console.Error)` at construction
- Background `ReadLineAsync` loop on thread-pool
- `SemaphoreSlim(1,1)` serialized writes to stdout
- Serialization-level `SecretScanner.Redact()` on every notification/response

**`VscodeJsonRpcServer`** (for `--vscode` mode):
- Same method set minus `input/cancel`
- No Console redirection (VS Code handles its own output channels)

#### 2.1.3 IRenderer Interface

`IRenderer` is the unified composite of three interfaces:

```
IRenderer = IOutputSink + IInputReader + ILiveFeedback
```

**`IOutputSink`** — All agent output:
- `StartAssistantResponse()`, `StreamText(string)`, `EndAssistantResponse(TurnMetrics?)`
- `AppendThinking(string)`, `CollapseThinking(int)`
- `WriteWelcome()`, `WriteMarkdown()`, `WriteDebug()`
- `WriteToolStart()`, `WriteToolSuccess()`, `WriteToolError()`, `WriteToolDenied()`, `WriteToolDiff()`, `WriteToolContent()`
- `WriteWarning()`, `WriteError()`, `WriteInfo()`, `WriteTodos()`
- `ClearConversation()`
- `Verbose` property

**`IInputReader`** — User input:
- `ReadInput()`, `ShowCommandPicker(CommandRegistry)`
- `AskUserAsync(string, CancellationToken)` → `Task<string>`
- `AskPermissionAsync(string, string, CancellationToken)` → `Task<PermissionResponse>`
- `EnableCommandSuggestions(CommandRegistry)`

**`ILiveFeedback`** — Turn lifecycle:
- `BeginTurn()`, `EndTurn()`

Three renderer implementations exist:
- **`OpenCodeBridgeRenderer`** — For terminal mode. All methods fire JSON-RPC notifications.
- **`VscodeRenderer`** — For VS Code mode. Same notification protocol.
- **`TerminalRenderer`** — For classic scrolling REPL. Direct ANSI output.
- **`AnsiTuiRenderer`** — For full-screen TUI. Uses `ConsoleTerminal` for low-level ANSI.

#### 2.1.4 ConversationLoop (`Session/ConversationLoop.cs`)

The core agent loop:

```
RunTurnAsync(userInput)
  → Add user message to session
  → Build context window (system prompt + conversation history)
  → Call LLM → receive response stream
  → Parse tool calls from stream
  → Execute tools via ToolDispatcher
  → Add results to session
  → Repeat (LLM → tools → LLM → tools) until natural stop
  → Save session
```

Key parameters:
- **Max tool loops**: Prevents infinite tool-calling patterns
- **Doom loop detection**: Same tool calls with identical args repeated 3+ times → break
- **Compactor/Checkpointer**: Triggered at 80%/65% context window usage

#### 2.1.5 ToolDispatcher (`Tools/ToolDispatcher.cs`)

Central dispatcher for tool execution. Each tool call goes through:

```
ExecuteSingleToolAsync(ToolCall, ITool, ToolContext)
  → RecordToolCallReceived (journal)
  → SchemaValidator.Validate (JSON schema check)
  → SanityCheck.Check (path traversal, blocked binaries, etc.)
  → Plan mode check (block write tools if active)
  → Capability-based or legacy permission check
  → Cache lookup (read-only tools)
  → HookRunner.RunPreToolUseHooksAsync
  → tool.ExecuteAsync(input, context, ct)
  → HookRunner.RunPostToolUseHooksAsync
  → Large output → ArtifactStore.PersistAndReplace
  → Cache put (read-only success)
  → Invalidate dependent caches (file writes clear read caches)
  → RecordToolCompleted/ToolCrashed (journal)
  → Render result
```

#### 2.1.6 Permission System (`Permissions/PermissionEngine.cs`)

**Dual-tier architecture:**

| Tier | Mechanism | Trigger |
|------|-----------|---------|
| **Legacy** | `tool.RequiredPermission(input)` → `PermissionLevel.AutoAllow/Ask/Deny` | Tools without `RequiredCapabilities()` |
| **Capability** | `tool.RequiredCapabilities(input)` → `Capability[]` | Tools implementing the capability interface |

**Capability types:**
- `FileReadCap`, `FileWriteCap` — File system access
- `ProcessExecCap` — Command execution (sub-process spawning)
- `NetworkEgressCap` — Network access
- `VcsMutationCap` — Git/VCS operations
- `MemoryCap` — Memory store operations
- `AgentSpawnCap` — Sub-agent spawning

**Decision flow:**

```
CheckAsync(toolName, input, level)
  → Config-level deny rules (blocked patterns)
  → Session allow-all set → allow
  → Session deny-all set → deny
  → AutoAllow level → allow
  → Deny level → deny
  → Config-level allow rules → allow
  → Prompt user via AskPermissionAsync → TCS freeze
```

**Session-wide decisions:**
- "Always Allow" → adds tool to `_sessionAllowAll`
- "Always Deny" → adds tool to `_sessionDenyAll`
- Denial tracking: after 3 consecutive or 20 total denials, re-prompts

---

## 3. JSON-RPC Protocol

See [docs/API.md](docs/API.md) for the complete protocol specification.

---

## 4. Data Flow

### 4.1 User Input Flow

```
User types message
  → TerminalUI / WebView captures input
  → JSON-RPC request: { method: "input/send", params: { text } }
  → TerminalJsonRpcServer / VscodeJsonRpcServer parses
  → HandleInputSend() → ConversationLoop.RunTurnAsync(text)
  → LLM generates tokens
  → OpenCodeBridgeRenderer / VscodeRenderer.StreamText(delta)
  → JSON-RPC notification: { method: "text/delta", params: { delta } }
  → TerminalUI / WebView renders token
  → (repeated for each streaming token)
  → Tool call detected by LLM
  → Renderer.WriteToolStart → notification: { method: "tool/start", ... }
  → ToolDispatcher.ExecuteSingleToolAsync
  → Renderer.WriteToolSuccess/Error → notification
  → (LLM continues with tool results)
  → Renderer.EndAssistantResponse → notification: { method: "turn/end" }
  → JSON-RPC response to original input/send request
  → TerminalUI shows prompt again
```

### 4.2 Permission Flow

```
Agent needs permission for dangerous operation
  → PermissionEngine.PromptUserAsync
  → OpenCodeBridgeRenderer.AskPermissionAsync(toolName, summary, ct)
  → Creates TaskCompletionSource, stores by callId
  → JSON-RPC notification: { method: "permission/ask",
       params: { call_id, tool_name, summary } }
  → TerminalUI receives notification
  → Shows permission dialog: "Allow Bash? [y/N/a/d]"
  → User types response
  → JSON-RPC request: { method: "permission/respond",
       params: { request_id: callId, response: "allow" } }
  → TerminalJsonRpcServer.HandlePermissionRespond()
  → OpenCodeBridgeRenderer.ResolvePermission(callId, "allow")
  → tcs.TrySetResult(PermissionResponse.Allow)
  → AskPermissionAsync returns
  → PermissionEngine.CheckAsync returns Allowed
  → Tool execution proceeds
```

### 4.3 Undo Flow

```
User requests undo
  → JSON-RPC request: { method: "session/undo", params: { count: 1 } }
  → TerminalJsonRpcServer.HandleSessionUndo()
  → FileHistory.RevertAsync(1)
  → Loads last N snapshots from session.Meta.FileHistory
  → For each snapshot:
    - If file still exists: write ContentBefore back
    - If file was created (ContentBefore = null): delete file
  → Returns list of reverted file paths
  → JSON-RPC response: { success: true, count: 1, reverted: ["src/main.cs"] }
```

---

## 5. Secret Scanning Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    JSON-RPC Output Path                          │
│                                                                  │
│  Any output method                                              │
│       │                                                         │
│       ▼                                                         │
│  JSON serialization (JsonSerializer.Serialize)                   │
│       │                                                         │
│       ▼                                                         │
│  SecretScanner.Redact(jsonString)                                │
│       │   ┌──────────────────────────────────────────────┐      │
│       │   │ Redacts 30+ patterns:                        │      │
│       │   │  • AWS Access/Secret Keys                    │      │
│       │   │  • OpenAI / Anthropic API keys               │      │
│       │   │  • GitHub PATs / GitLab tokens               │      │
│       │   │  • SSH private keys (PEM blocks)             │      │
│       │   │  • JWT tokens                                │      │
│       │   │  • Slack tokens, Discord webhooks            │      │
│       │   │  • Generic Bearer/Token auth headers         │      │
│       │   │  • MongoDB / PostgreSQL connection strings   │      │
│       │   │  • And more...                               │      │
│       │   └──────────────────────────────────────────────┘      │
│       ▼                                                         │
│  stdout.WriteLineAsync(redactedJson)                             │
└─────────────────────────────────────────────────────────────────┘
```

This is applied at two levels:
1. **Serialization-level** (`TerminalJsonRpcServer.SendNotificationAsync`): Entire JSON string redacted after serialization — single choke point
2. **Per-field** (`OpenCodeBridgeRenderer` methods): Individual fields redacted before being passed to `SendNotificationAsync` — defense-in-depth

---

## 6. File History & Atomic Undo

`FileHistory` in `src/OpenMono.Cli/History/` tracks every file modification:

```
File Write detected
  → Before writing: snapshot current file content (ContentBefore)
  → Store { Path, ContentBefore, ContentAfter, Timestamp } in Snapshots list
  → Execute write

Undo requested (count=N)
  → Pop last N snapshots
  → For each snapshot in reverse:
    - If ContentBefore != null: write ContentBefore to path
    - If ContentBefore == null (file was created): delete file
  → Return list of {(path, action)} for UI display
```

Key properties:
- Snapshots are stored in memory (`SessionState.Meta.FileHistory.Snapshots`)
- `FileHistoryTool` and `FileEditTool` register snapshots automatically
- The undo command (`session/undo`) calls `FileHistory.RevertAsync(count)`
- Also accessible as `/undo [n]` slash command in the classic REPL

---

## 7. Session Persistence

Sessions are persisted to `~/.openmono/sessions/` as JSONL files:

```
~/.openmono/sessions/
├── index.json                              # Session index (list of summaries)
├── 2026-05-25_a1b2c3d4e5f6.jsonl          # Session messages (one JSON per line)
│   ├── Line 1: SessionHeader { session_id, started_at, working_directory }
│   ├── Line 2+: Message { role, content, tool_calls, ... }
│   └── ...
└── 2026-05-25_a1b2c3d4e5f6.checkpoints.json  # Checkpoints list
```

Session saving happens:
- After every turn (automatic)
- On graceful shutdown
- Via `SessionManager.SaveAsync()` / `AppendMessageAsync()`

Session restoring:
- `/resume <session_id>` slash command
- `session/start { restoreSessionId: "..." }` JSON-RPC method

---

## 8. Streaming Architecture

The LLM client (`ILlmClient`) returns tokens via callbacks:

```
LLM generates token
  → OnText(streamingTextChunk)
  → renderer.StreamText(chunk)
  → JSON-RPC notification: { method: "text/delta", params: { delta: chunk } }
  → Frontend receives notification
  → Appends to current message buffer
  → Renders immediately
```

For tool calls during streaming:

```
LLM emits <function=ReadFile>
  → OnToolCall(toolCall)
  → renderer.WriteToolStart(toolName, args)
  → JSON-RPC notification: { method: "tool/start", params: { tool_name, arguments } }
  → ToolDispatcher executes tool
  → renderer.WriteToolSuccess(toolName) or WriteToolError(toolName, error)
  → JSON-RPC notification: { method: "tool/result", ... }
  → Tool result sent back to LLM via OnToolResult
```

---

## 9. Doom Loop Detection

Located in `ToolDispatcher._doomLoop` (`DoomLoopDetector`):

```csharp
class DoomLoopDetector
{
    private Queue<(string toolName, string argsHash)> _lastCalls = new(3);

    bool Check(List<ToolCall> calls)
    {
        // If the same tool with same args appears 3+ times in a row
        // across consecutive batches → return true (break loop)
    }
}
```

When detected:
- The agent receives `ToolResult.Error` with a message instructing it to stop
- The renderer shows a warning
- The LLM is forced to try a different approach or ask the user

---

## 10. Tool Registry

All available tools in `ToolRegistry`:

| Tool | Type | Read-Only | Deferred |
|------|------|-----------|----------|
| `FileReadTool` | Core | ✓ | |
| `FileWriteTool` | Core | | |
| `FileEditTool` | Core | | |
| `GlobTool` | Core | ✓ | |
| `GrepTool` | Core | ✓ | |
| `BashTool` | Core | | |
| `AgentTool` | Core | | ✓ |
| `TodoTool` | Core | | |
| `AskUserTool` | Core | | |
| `MemorySaveTool` | Memory | | |
| `WebFetchTool` | Web | ✓ | |
| `WebSearchTool` | Web | ✓ | |
| `ListDirectoryTool` | Core | ✓ | |
| `ApplyPatchTool` | Core | | |
| `EnterPlanModeTool` | Core | | |
| `ExitPlanModeTool` | Core | | |
| `LspTool` | LSP | ✓ | |
| `RoslynTool` | LSP | ✓ | |
| `PlaybookTool` | Playbook | | |

---

## 11. VS Code Extension Architecture

The VS Code extension (`opencode/sdks/vscode/`) provides:

- **WebView-based chat panel** in the VS Code activity bar
- **6 commands** registered in VS Code's command palette
- **Workspace context automation**: `onDidChangeActiveTextEditor` + `onDidSaveTextDocument` with 300ms debounce
- **Keybindings**: `Cmd+Esc` (open chat), `Cmd+Shift+Esc` (new session), `Cmd+Shift+Z` (undo)
- **Dedicated OutputChannel** for backend stderr logs
- **MEMORY.md seeding** from `.opencode/MEMORY.md`
- **Permission fallback** via `showInformationMessage` when WebView is unavailable

The extension communicates with the backend using the same JSON-RPC protocol as the terminal client. The `--vscode` flag ensures the backend uses `VscodeJsonRpcServer` instead of `TerminalJsonRpcServer`.

---

## 12. Frontend Comparison

| Aspect | Terminal Client | VS Code Extension |
|--------|----------------|-------------------|
| **Binary** | `ruffel` (global CLI) | VS Code extension |
| **Runtime** | Node.js 20+ | VS Code API |
| **UI** | REPL + inline prompts | WebView panel |
| **Permissions** | Keyboard [y/N/a/d] | Clickable buttons |
| **Auto-context** | Manual context via args | Automatic on editor change/save |
| **Build size** | 15KB (esbuild) | 100KB+ (esbuild) |
| **Startup** | `ruffel` | `Cmd+Esc` |
| **Platform** | Cross-platform (Node.js) | VS Code (all platforms) |

---

## 13. Docker Architecture

```yaml
docker-compose.yml:
  services:
    llama-server:        # llama.cpp with GPU offload
      image: local/llama-server
      ports: ["7474:7474"]
      volumes: [./models:/models]
      deploy:
        resources:
          reservations:
            devices: [{driver: nvidia, count: all, capabilities: [gpu]}]
    
    ruffel-agent:        # Full agent container
      build: .
      depends_on: [llama-server]
      stdin_open: true
      tty: true
      entrypoint: ["ruffel"]
```

The `ruffel-agent` container runs both the .NET backend and the Node.js frontend. The backend connects to `llama-server` via `http://llama-server:7474`.

---

## 14. Error Handling Strategy

| Layer | Strategy |
|-------|----------|
| **JSON parsing** | `JsonException` caught in `ProcessLine()` — malformed input silently dropped |
| **Unknown methods** | `SendErrorResponse(id, -32601, "Method not found: {method}")` |
| **Handler exceptions** | `SendErrorResponse(id, -32603, ex.Message)` — caught in outer try/catch |
| **Tool execution** | `ToolDispatcher.ExecuteSingleToolAsync()` wraps in try/catch → returns `ToolResult.Crash` or `ToolResult.Error` |
| **LLM connection** | `ConversationLoop` catches `HttpRequestException` → suggests recovery via health checks |
| **Permission cancellation** | `AskPermissionAsync` catches `OperationCanceledException` → returns `PermissionResponse.Deny` |
| **Process termination** | Frontend detects process exit → shows error, allows restart |
| **Stray Console.Write** | `Console.SetOut(Console.Error)` in terminal mode → rogue writes go to stderr |

---

## 15. Configuration Hierarchy

Configuration is loaded with the following priority (highest wins):

```
1. CLI flags (--endpoint, --model, --workdir, --config, --vscode, --rpc, --tui, --classic, -v)
2. Environment variables (OPENMONO_ENDPOINT, OPENMONO_MODEL, OPENMONO_WORKSPACE, OPENMONO_RENDERER, ...)
3. --config flag JSON file
4. Project settings.json (.openmono/settings.json in working directory)
5. User settings.json (~/.openmono/settings.json)
6. Built-in defaults (AppConfig property initializers)
```

See [CONFIG.md](CONFIG.md) for the complete configuration reference.

---

## 16. Module Dependencies

```
OpenMono.Cli
├── Config          ← AppConfig, ConfigLoader, JsonOptions
├── History         ← FileHistory (snapshot-based undo)
├── Hooks           ← HookRunner (pre/post tool, session start)
├── Llm             ← ILlmClient (OpenAI-compat, Anthropic)
├── Lsp             ← LspServerManager (code intelligence)
├── Mcp             ← McpServerManager (MCP protocol)
├── Memory          ← MemoryStore (key-value persistence)
├── Permissions     ← PermissionEngine (legacy + capability)
├── Playbooks       ← PlaybookExecutor (step-by-step workflows)
├── Rendering       ← IRenderer + implementations
├── Session         ← ConversationLoop, SessionState, TurnJournal
├── Tools           ← ToolRegistry, ToolDispatcher, 20+ ITool impls
├── Tui             ← AnsiTuiRenderer, ConsoleTerminal
└── Utils           ← SecretScanner, Log, ProcessRunner, InputSanitizer
```

All modules depend on `Config` (for `AppConfig`) and optionally on `Rendering` (for `IRenderer`). No circular dependencies exist.
