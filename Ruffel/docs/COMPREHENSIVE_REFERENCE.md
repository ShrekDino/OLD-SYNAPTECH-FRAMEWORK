# OpenMono.ai — Complete Codebase Reference

> **Version**: 0.1.0 | **License**: AGPL-3.0 | **Stack**: .NET 10 (C# 13, preview) | **Assembly**: `openmono`
>
> A local-first AI coding agent. Runs an agentic loop powered by a local LLM (llama.cpp, Ollama) or cloud LLM (OpenAI, Anthropic). 20+ built-in tools, sub-agents, LSP code intelligence, MCP protocol, playbooks, Docker sandboxing.

---

## Table of Contents

1. [Project Identity](#1-project-identity)
2. [Directory Structure](#2-directory-structure)
3. [Build Configuration](#3-build-configuration)
4. [Architecture Overview](#4-architecture-overview)
5. [Core Data Model (Session/)](#5-core-data-model-session)
6. [LLM Provider Layer (Llm/)](#6-llm-provider-layer-llm)
7. [Built-in Tool Inventory (Tools/)](#7-built-in-tool-inventory-tools)
8. [Permission System (Permissions/)](#8-permission-system-permissions)
9. [Configuration System (Config/)](#9-configuration-system-config)
10. [MCP Protocol (Mcp/)](#10-mcp-protocol-mcp)
11. [LSP Integration (Lsp/)](#11-lsp-integration-lsp)
12. [Agent System (Agents/)](#12-agent-system-agents)
13. [Playbook System (Playbooks/)](#13-playbook-system-playbooks)
14. [Memory System (Memory/)](#14-memory-system-memory)
15. [File History / Undo (History/)](#15-file-history--undo-history)
16. [Hooks System (Hooks/)](#16-hooks-system-hooks)
17. [Secret Scanner (Utils/SecretScanner.cs)](#17-secret-scanner-utilssecretscannercs)
18. [Rendering System (Rendering/)](#18-rendering-system-rendering)
19. [TUI System (Tui/)](#19-tui-system-tui)
20. [Slash Commands (Commands/)](#20-slash-commands-commands)
21. [Utilities (Utils/)](#21-utilities-utils)
22. [Session Persistence](#22-session-persistence)
23. [Docker Deployment](#23-docker-deployment)
24. [Test Infrastructure](#24-test-infrastructure)
25. [OpenCode SDK (opencode/)](#25-opencode-sdk-opencode)
26. [Ruffel Mono Agent (Merged Architecture)](#26-ruffel-mono-agent-merged-architecture)

---

## 1. Project Identity

| Field | Value |
|-------|-------|
| **Full name** | OpenMono.ai |
| **Version** | 0.1.0 (public beta) |
| **License** | GNU Affero General Public License v3.0 |
| **Owner** | StartupHakk (© 2026) |
| **Language** | C# 13 (LangVersion `preview`) |
| **Target framework** | `net10.0` |
| **SDK pin** | .NET 10.0.100 (`rollForward: latestMinor`) |
| **Assembly name** | `openmono` |
| **Root namespace** | `OpenMono` |
| **Solution** | `OpenMono.sln` (2 projects: `OpenMono.Cli` + `OpenMono.Tests`) |
| **Source files** | 99 `.cs` files across 18 subdirectories in `src/OpenMono.Cli/` |
| **Test files** | 44 `.cs` files across 12+ subdirectories in `src/OpenMono.Tests/` |
| **CI** | GitHub Actions: .NET build + test + Docker build + ShellCheck |

**Mission**: A coding agent that runs entirely on local hardware — no subscriptions, no data leaving the network, no per-token billing. Pairs a .NET 10 CLI with its own llama.cpp inference server, giving a full agentic loop with 20+ built-in tools, Docker sandboxing, and deep code intelligence.

---

## 2. Directory Structure

```
/home/cinni/Ruffel/
├── OpenMono.sln                          # Solution file (2 projects)
├── global.json                           # .NET 10.0.100 SDK pin
├── Directory.Build.props                 # Shared C# build config
├── .gitignore
├── .dockerignore
├── LICENSE                               # AGPL-3.0
├── README.md                             # Project overview, badges, feature table
├── ARCHLINUX.md                          # Arch Linux install guide
├── CONTRIBUTING.md                       # Contribution guidelines
├── ROADMAP.md                            # April 2026 roadmap
├── SECURITY.md                           # Security policy
├── get-openmono.sh                       # One-liner installer
├── setup-hybrid.sh                       # Hybrid MoE + TurboQuant setup
│
├── src/
│   ├── OpenMono.Cli/                     # Main console application (99 .cs files)
│   │   ├── Program.cs                    # Entry point, CLI arg parser, startup (~1005 lines)
│   │   ├── OpenMono.Cli.csproj           # Project file (NuGet deps)
│   │   │
│   │   ├── Commands/                     # 17 files: slash commands
│   │   │   ├── ICommand.cs               # Command interface
│   │   │   ├── CommandRegistry.cs        # Command lookup/registration
│   │   │   ├── HelpCommand.cs            # /help
│   │   │   ├── StatusCommand.cs          # /status
│   │   │   ├── StatsCommand.cs           # /stats
│   │   │   ├── ModelCommand.cs           # /model
│   │   │   ├── CompactCommand.cs         # /compact
│   │   │   ├── ClearCommand.cs           # /clear
│   │   │   ├── RetryCommand.cs           # /retry
│   │   │   ├── UndoCommand.cs            # /undo
│   │   │   ├── CheckpointCommand.cs      # /checkpoint
│   │   │   ├── ThinkCommand.cs           # /think
│   │   │   ├── DebugCommand.cs           # /debug
│   │   │   ├── InitCommand.cs            # /init
│   │   │   ├── ResumeCommand.cs          # /resume
│   │   │   ├── ExportCommand.cs          # /export
│   │   │   ├── PlanCommand.cs            # /plan
│   │   │
│   │   ├── Config/                       # 4 files: 3-layer config system
│   │   │   ├── AppConfig.cs              # Config model (LlmConfig, ProviderSettings, McpServerSettings, etc.)
│   │   │   ├── ConfigLoader.cs           # Load → merge user/project/explicit + env overrides
│   │   │   ├── ProjectConfig.cs          # OPENMONO.md project instructions reader
│   │   │   └── JsonOptions.cs            # Shared JSON serialization options
│   │   │
│   │   ├── Session/                      # 17 files: core agentic loop engine
│   │   │   ├── SessionState.cs           # Conversation state: messages, todos, tokens, checkpoints
│   │   │   ├── SessionManager.cs         # Create/load/save sessions
│   │   │   ├── SessionMetadata.cs        # Meta flags: planMode, thinkingEnabled, FileHistory, etc.
│   │   │   ├── Message.cs                # Message + ToolCall records (System/User/Assistant/Tool)
│   │   │   ├── ConversationLoop.cs       # Main agentic loop (stream → parse → execute → loop)
│   │   │   ├── Compactor.cs              # LLM-based context compaction at 80% capacity
│   │   │   ├── CompactionReport.cs       # Metrics for compaction (tokens before/after, evicted count)
│   │   │   ├── Checkpointer.cs           # Checkpoint management at 65% capacity
│   │   │   ├── CheckpointEntry.cs        # Checkpoint record (ID, summary, cutoff index)
│   │   │   ├── SummaryPrompt.cs          # Prompt templates for checkpoint/compaction summarization
│   │   │   ├── TurnJournal.cs            # Event-sourced JSONL journal (11 event types)
│   │   │   ├── DoomLoopDetector.cs       # Tool-call repetition detector (periods 1-4, 12-call history)
│   │   │   ├── TokenTracker.cs           # Token usage tracking + tool usage statistics
│   │   │   ├── CursorStore.cs            # Cursor-based reading state
│   │   │   ├── ToolResultCache.cs        # Cache for read-only tool results
│   │   │   ├── ArtifactStore.cs          # Persistence for large tool outputs
│   │   │   └── PlanModeInstructions.cs   # System prompt fragments for plan mode
│   │   │
│   │   ├── Llm/                          # 5 files: LLM client layer
│   │   │   ├── ILlmClient.cs             # Interface + StreamChunk/LlmOptions/UsageInfo records
│   │   │   ├── IProvider.cs              # Provider interface
│   │   │   ├── ProviderRegistry.cs       # Registry of 4 providers + CreateClient() logic
│   │   │   ├── OpenAiCompatClient.cs     # OpenAI-compatible + Qwen XML parser
│   │   │   └── AnthropicClient.cs        # Anthropic SSE client
│   │   │
│   │   ├── Tools/                        # 28 files: all built-in tools
│   │   │   ├── ITool.cs                  # Tool interface (Name, Description, InputSchema, ExecuteAsync, etc.)
│   │   │   ├── ToolBase.cs               # Abstract base + SchemaBuilder fluent API
│   │   │   ├── ToolContext.cs            # Execution context (registry, session, permissions, etc.)
│   │   │   ├── ToolResult.cs             # Result record (Success, Error, Crash, etc. + metadata)
│   │   │   ├── ToolRegistry.cs           # Tool registration/lookup/resolution + BuildToolDefinitions()
│   │   │   ├── ToolDispatcher.cs         # Full execution pipeline (journal → parse → validate → sanity → permission → hooks → execute → cache)
│   │   │   ├── SchemaValidator.cs        # JSON Schema validation against tool schemas
│   │   │   ├── SanityCheck.cs            # Pre-flight safety checks for Bash and file writes
│   │   │   ├── BashParser.cs             # Shell command parser for capability detection
│   │   │   ├── FileReadTool.cs           # Read file content
│   │   │   ├── FileWriteTool.cs          # Write file content
│   │   │   ├── FileEditTool.cs           # Search-and-replace editing
│   │   │   ├── GlobTool.cs               # File pattern matching
│   │   │   ├── GrepTool.cs               # Regex content search
│   │   │   ├── ListDirectoryTool.cs      # List directory contents
│   │   │   ├── BashTool.cs               # Shell execution (foreground + background)
│   │   │   ├── AgentTool.cs              # Sub-agent spawner
│   │   │   ├── TodoTool.cs               # Task tracking
│   │   │   ├── AskUserTool.cs            # User prompts
│   │   │   ├── MemorySaveTool.cs         # Cross-session memory
│   │   │   ├── WebFetchTool.cs           # URL fetching
│   │   │   ├── WebSearchTool.cs          # Web search
│   │   │   ├── ApplyPatchTool.cs         # Unified diff application
│   │   │   ├── PlanModeTool.cs           # Enter/Exit plan mode
│   │   │   ├── LspTool.cs                # LSP queries
│   │   │   ├── RoslynTool.cs             # C# semantic analysis
│   │   │   ├── PlaybookTool.cs           # Playbook execution
│   │   │   └── ToolSearchTool.cs         # Tool search
│   │   │
│   │   ├── Mcp/                          # 3 files: MCP protocol
│   │   │   ├── McpClient.cs              # JSON-RPC 2.0 client over stdio
│   │   │   ├── McpServerManager.cs       # Server lifecycle + tool registration
│   │   │   └── McpToolAdapter.cs         # MCP tool → ITool adapter
│   │   │
│   │   ├── Lsp/                          # 2 files: LSP integration
│   │   │   ├── LspClient.cs              # JSON-RPC 2.0 LSP client over stdio
│   │   │   └── LspServerManager.cs       # Server lifecycle (5 default languages)
│   │   │
│   │   ├── Agents/                       # 1 file: agent definitions
│   │   │   └── AgentDefinition.cs        # 5 agent types (GeneralPurpose, Explore, Plan, Coder, Verify)
│   │   │
│   │   ├── Permissions/                  # 3 files: permission engine
│   │   │   ├── PermissionEngine.cs       # 3-tier + capability-based + session-level allow/deny
│   │   │   ├── Capability.cs             # Capability types (FileRead/Write, ProcessExec, NetworkEgress, etc.)
│   │   │   └── PathGuard.cs             # Workspace root validation for file paths
│   │   │
│   │   ├── Rendering/                    # 14 files: output/input interfaces + implementations
│   │   │   ├── IRenderer.cs              # Composite: IOutputSink + IInputReader + ILiveFeedback
│   │   │   ├── IOutputSink.cs            # Output interface (WriteWarning, WriteToolStart, StreamText, etc.)
│   │   │   ├── IInputReader.cs           # Input interface (ReadInput, AskUser, AskPermission)
│   │   │   ├── ILiveFeedback.cs          # Turn lifecyle (BeginTurn, EndTurn)
│   │   │   ├── ITerminal.cs              # Raw terminal abstraction
│   │   │   ├── TerminalRenderer.cs       # Classic scrolling Spectre.Console renderer
│   │   │   ├── AnsiTuiRenderer.cs        # Full-screen Terminal.Gui TUI renderer
│   │   │   ├── AnsiMarkdown.cs           # Markdown-to-ANSI rendering
│   │   │   ├── AnsiPainter.cs            # ANSI escape code painting
│   │   │   ├── AnsiInputReader.cs        # TUI input reader
│   │   │   ├── AnsiSuggestionOverlay.cs  # Command suggestion overlay
│   │   │   ├── CommandAwareInput.cs      # Tab-completion for slash commands
│   │   │   ├── ConsoleTerminal.cs        # Concrete ITerminal (System.Console)
│   │   │   └── NullLiveFeedback.cs       # No-op live feedback
│   │   │
│   │   ├── Tui/                          # 7 files (+ subdirs): TUI components
│   │   │   ├── ApprovalController.cs     # Inline tool approval UI
│   │   │   ├── PauseController.cs        # User-triggerable pause during streaming
│   │   │   ├── StreamingMetrics.cs       # Real-time token/s, TTFT, elapsed
│   │   │   ├── ContextWindowMeter.cs     # Context usage visual bar
│   │   │   ├── Keybindings/              # Keyboard shortcut manager
│   │   │   ├── Rendering/                # Markdown renderer, syntax highlighter, theme
│   │   │   └── Export/                   # Markdown/JSON/HTML exporters
│   │   │
│   │   ├── Playbooks/                    # 7 files: playbook system
│   │   │   ├── PlaybookDefinition.cs     # Definition records + enums (TriggerMode, GateType, etc.)
│   │   │   ├── PlaybookLoader.cs         # Load playbooks from search paths
│   │   │   ├── PlaybookRegistry.cs       # Register/resolve/lookup playbooks
│   │   │   ├── PlaybookExecutor.cs       # Step-by-step execution with LLM calls
│   │   │   ├── PlaybookState.cs          # Checkpoint/resume state for running playbooks
│   │   │   ├── TemplateEngine.cs         # {{param}} and {{step.output}} substitution
│   │   │   └── ParameterValidator.cs     # Type/constraint validation for playbook params
│   │   │
│   │   ├── Memory/                       # 1 file: cross-session memory
│   │   │   └── MemoryStore.cs            # YAML-frontmatter .md files + auto-generated index
│   │   │
│   │   ├── History/                      # 2 files: file undo system
│   │   │   ├── FileHistory.cs            # Snapshot manager (record before/after, revert N steps)
│   │   │   └── FileSnapshot.cs           # Before/after content snapshot record
│   │   │
│   │   ├── Hooks/                        # 1 file: hooks system
│   │   │   └── HookRunner.cs             # Pre/post tool hooks + session start hooks
│   │   │
│   │   └── Utils/                        # 9 files: utilities
│   │       ├── SecretScanner.cs          # 20+ regex rules for API keys/credentials
│   │       ├── ProcessRunner.cs          # Simple process start + async read
│   │       ├── ProcessWatchdog.cs        # Hard-kill scheduler for double Ctrl+C
│   │       ├── PathUtils.cs              # Path resolution helpers
│   │       ├── GitHelper.cs              # Current branch, status, recent commits
│   │       ├── FileSearcher.cs           # File search with pattern matching
│   │       ├── Log.cs                    # Single-file append logger
│   │       ├── InputSanitizer.cs         # Control character stripping
│   │       └── InlineDiff.cs             # Colored diff computation
│   │
│   └── OpenMono.Tests/                   # 44 test files
│       ├── OpenMono.Tests.csproj         # xUnit + FluentAssertions + NSubstitute
│       ├── Tools/                        # Tool unit tests
│       ├── Session/                      # ConversationLoop, Compactor, SessionManager, etc.
│       ├── Tui/                          # TUI component tests
│       ├── Mcp/                          # MCP tool adapter tests
│       ├── Config/                       # ConfigLoaderTests
│       ├── Permissions/                  # PermissionEngineTests
│       ├── Playbooks/                    # Playbook loader/state/validator tests
│       ├── History/                      # FileHistoryTests
│       ├── Memory/                       # MemoryStoreTests
│       ├── Rendering/                    # Interface segregation + ANSI markdown tests
│       ├── Integration/                  # SmokeTests, CapabilityAndDeferredToolTests
│       └── Fakes/                        # TerminalMockWrapper
│
├── docker/
│   ├── docker-compose.yml                # Main compose: llama-server + agent
│   ├── docker-compose.override.yml       # GPU/turboquant override
│   ├── docker-compose.hybrid-moe.yml     # CPU MoE config
│   ├── Dockerfile.agent                  # Multi-stage .NET 10 build
│   ├── openmono-wrapper.sh               # Docker run wrapper
│   ├── .env.example
│   └── .env.hybrid.example
│
├── models/
│   └── Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf  # Pre-downloaded MoE model (~17.6 GB)
│
├── scripts/
│   ├── install.sh                        # Main multi-platform installer
│   ├── install_arch.sh / install_macos.sh / install_prereqs.sh
│   ├── healthcheck.sh
│   ├── switch-agent.sh                   # Toggle OpenCode ↔ OpenMono
│   ├── setup-tunnel-inference.sh         # frp tunnel for dual-box mode
│   ├── setup-graph.sh / setup-graphify.sh
│   └── lib/ (perf-common.sh, log.sh)
│
├── setup/
│   ├── build.sh                          # Delegates to scripts/
│   ├── prereqs.sh
│   └── graph.sh
│
├── docs/
│   ├── ARCHITECTURE.md                   # Component architecture + startup sequence
│   ├── CONFIG.md                         # CLI reference
│   ├── SETUP.md                          # Installation guide
│   ├── MODELS.md                         # Model selection rationale
│   ├── PLAYBOOKS.md                      # Playbook specification
│   ├── graphify.md                       # Semantic knowledge graph docs
│   ├── code-review-graph.md              # Code review graph tool docs
│   ├── assets/                           # Architecture diagrams + logos
│   └── playbooks-examples/               # 7 example playbooks (commit, release, pr-ready, etc.)
│
├── .github/
│   ├── workflows/ci.yml                  # .NET build + test + Docker + ShellCheck
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── ISSUE_TEMPLATE/ (bug_report.md, feature_request.md)
│
└── opencode/                             # OpenCode SDK (separate TypeScript project)
    ├── README.md
    ├── packages/ (core, web, sdk, slack, plugin, llm, etc.)
    ├── sdks/vscode/                      # VS Code extension (v1.15.10)
    ├── specs/v2/                         # V2 architecture specs
    ├── .github/workflows/                # 22 CI workflow files
    └── ... (flake.nix, flake.lock, etc.)
```

---

## 3. Build Configuration

### `Directory.Build.props` (shared across all projects)

```xml
<TargetFramework>net10.0</TargetFramework>
<LangVersion>preview</LangVersion>
<Nullable>enable</Nullable>
<ImplicitUsings>enable</ImplicitUsings>
<TreatWarningsAsErrors>true</TreatWarningsAsErrors>
<EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
```

### NuGet Dependencies (`OpenMono.Cli.csproj`)

| Package | Version | Purpose |
|---------|---------|---------|
| `Spectre.Console` | 0.50.0 | Classic mode terminal UI (markdown, tables, panels) |
| `Spectre.Console.Json` | 0.50.0 | JSON pretty-printing in terminal |
| `Markdig` | 0.40.0 | Markdown-to-ANSI conversion |
| `YamlDotNet` | 16.3.0 | YAML frontmatter parsing for memory files |
| `Microsoft.Extensions.FileSystemGlobbing` | 10.0.0-preview.4.25258.110 | Glob file matching |
| `Microsoft.CodeAnalysis.CSharp.Workspaces` | 4.12.0 | Roslyn C# semantic analysis |
| `Terminal.Gui` | 2.0.0-develop.5264 | Full-screen TUI framework |
| `TiktokenSharp` | 1.2.1 | Token counting (o200k_base encoding) |

### Test Dependencies (`OpenMono.Tests.csproj`)

| Package | Version | Purpose |
|---------|---------|---------|
| `xunit` | 2.9.3 | Test framework |
| `xunit.runner.visualstudio` | 3.1.0 | Test runner |
| `FluentAssertions` | 8.3.0 | Fluent assertions |
| `NSubstitute` | 5.3.0 | Mocking framework |
| `Xunit.SkippableFact` | 1.5.61 | Conditional test skipping |
| `Microsoft.NET.Test.Sdk` | 17.14.0 | MSBuild test integration |

---

## 4. Architecture Overview

### Startup Sequence (in `Program.cs:88-425`)

```
User CLI input
  ↓
1. Parse args (--endpoint, --model, --workdir, --config, --verbose, --classic, --tui, --help, --version)
  ↓
2. ConfigLoader.Load() → AppConfig (3-layer merge + env var overrides)
  ↓
3. TryDetectActualModelAsync() → query /props → fallback /v1/models
  ↓
4. Setup renderer (TerminalRenderer classique or AnsiTuiRenderer TUI)
  ↓
5. Initialize services:
   - PermissionEngine
   - MemoryStore
   - HookRunner
   - LspServerManager
   - TokenTracker
   - FileHistory
   - ToolRegistry (register all 20+ tools)
   - McpServerManager (connect MCP servers)
   - Checkpointer
   - Compactor
   - TurnJournal
   - CommandRegistry (register 17 commands)
  ↓
6. Build system prompt (base + project instructions + memory + git + environment + playbooks)
  ↓
7. ConversationLoop = new ConversationLoop(llm, tools, permissions, renderer, config, session, ...)
  ↓
8. Enter main loop: while(true) { ReadInput → RunTurnAsync() }
```

### Agentic Loop (per turn, inside `ConversationLoop.RunTurnAsync()`)

```
User input arrives
  ↓
1. DoomLoopDetector.Reset()
  ↓
2. Add user Message to SessionState
  ↓
3. Check if Checkpoint needed (65% context threshold)
    → if yes: create checkpoint via LLM, replace old turns
  ↓
4. Check if Compaction needed (80% context threshold)
    → if yes: summarize old turns via LLM, evict large outputs
  ↓
5. Build context window + tool definitions (filtered by plan mode)
  ↓
6. FOR iteration = 0..1000:
    a. Stream LLM response via IAsyncEnumerable<StreamChunk>
    b. Accumulate text + tool calls from stream
    c. Launch concurrency-safe read-only tools early (while streaming)
    d. Check DoomLoopDetector (same tool sequence ×3 → abort)
    e. Execute tool calls (parallel reads, sequential writes)
    f. Store large results as artifacts
    g. Feed results back as Tool Messages
    h. If LLM produces no tool calls → turn complete
    i. If iteration cap (1000) hit → generate summary, return
```

### Tool Execution Pipeline (inside `ToolDispatcher.ExecuteSingleToolAsync()`)

```
ToolCall arrives
  ↓
1. Parse JSON arguments
  ↓
2. SchemaValidator.Validate() against tool's InputSchema
  ↓
3. SanityCheck.Check() — path safety, command safety
  ↓
4. Plan mode guard (block writes if plan mode active)
  ↓
5. Permission check:
   - Capability-based (if tool provides RequiredCapabilities)
   - Legacy permission (if not)
   - 3 tiers: AutoAllow / Ask / Deny
   - Session-level allow/deny all
  ↓
6. Cache lookup (read-only tools only)
  ↓
7. Pre-tool-use hooks (by tool name / input content)
  ↓
8. Execute tool (tool.ExecuteAsync)
  ↓
9. Post-tool-use hooks
  ↓
10. Artifact store (if > 20KB output → persist to disk)
  ↓
11. Update cache (read-only) + invalidate cache (writes to known paths)
  ↓
12. Journal every step (schema_validated, sanity_checked, permission_decided, tool_started, tool_completed/crashed)
```

---

## 5. Core Data Model (Session/)

### `SessionState` (`SessionState.cs`)

```csharp
class SessionState {
    string Id                         // 12-char hex (Guid.NewGuid().ToString("N")[..12])
    DateTime StartedAt                // DateTime.UtcNow
    List<Message> Messages            // Conversation history
    SessionMetadata Meta              // PlanMode, ThinkingEnabled, TokenTracker, FileHistory, LastPlan
    List<TodoItem> Todos              // Active todo items
    int TotalTokensUsed               // Running total
    int TurnCount                     // Number of turns
    List<CheckpointEntry> Checkpoints // Compression checkpoint records
    int CheckpointCutoffIndex         // Index of first message after last checkpoint
}
```

### `Message` (`Message.cs`)

```csharp
enum MessageRole { System, User, Assistant, Tool }

record Message {
    MessageRole Role
    string? Content                    // Plain text content
    List<ToolCall>? ToolCalls         // Assistant messages may contain tool calls
    string? ToolCallId                 // Tool result messages reference their call ID
    string? ToolName                   // Name of tool that produced this result
    DateTime Timestamp                 // Auto-generated UTC timestamp
}

record ToolCall {
    string Id                          // Unique call ID from LLM
    string Name                        // Tool name
    string Arguments                    // JSON string of arguments
}
```

### `CheckpointEntry` (`CheckpointEntry.cs`)

```csharp
record CheckpointEntry {
    string Id                          // 8-char hex
    DateTime CreatedAt
    int TurnIndex
    int CutoffMessageIndex             // Index in Messages list
    string Summary                     // LLM-generated summary
    int MessagesCompressed
}
```

### `TurnJournal` (`TurnJournal.cs`) — Event-sourced journaling

Records 11 event types as JSONL (one object per line) under `~/.openmono/sessions/{date}_{sessionId}.journal.jsonl`:

| Event | Fields | Description |
|-------|--------|-------------|
| `TurnStarted` | turnId, parentMessageId, model, timestamp | Start of a turn |
| `TurnFinished` | turnId, finishReason (`text_only`/`doom_loop`/`turn_break`/`max_iterations`) | End of a turn |
| `ToolCallReceived` | turnId, callId, toolName, argsHash (SHA256[..16]) | Tool call from LLM |
| `SchemaValidated` | callId | JSON schema validated ✅ |
| `SchemaRejected` | callId, error | JSON schema rejected ❌ |
| `SanityChecked` | callId | Sanity check passed ✅ |
| `SanityRejected` | callId, reason | Sanity check failed ❌ |
| `PermissionDecided` | callId, decision (allow/deny), reason | Permission verdict |
| `ToolStarted` | callId | Execution started |
| `ToolCompleted` | callId, resultClass, artifactIds | Execution success |
| `ToolCrashed` | callId, exceptionClass, message | Execution exception |

Journal uses source-generated JSON serialization (`JournalSerializerContext`) with snake_case naming.

### `Compactor` (`Compactor.cs`)

- **Trigger**: 80% of context window (`N * 0.80`)
- **Secondary trigger**: 65% of context window (for mid-turn compaction)
- **Action**:
  1. Preserve system messages + 4 most recent user turns
  2. Evict tool outputs > 2000 chars (replace with `[Tool result evicted — was N chars]`)
  3. Build conversation text of remaining messages
  4. Call LLM to generate summary (`MaxTokens: 4096, Temperature: 0.1`)
  5. Replace summarized messages with: `[Conversation summary — N messages compacted]` + summary
  6. Add assistant acknowledgment: `"Understood. Continuing..."`

### `Checkpointer` (`Checkpointer.cs`)

- **Trigger**: 65% of context window (`N * 0.65`)
- **Action**:
  1. Find messages since last checkpoint (greedy: try keeping 4 turns, fall back to 3, 2, 1)
  2. Generate LLM summary
  3. Store as `CheckpointEntry` in session
  4. Set `CheckpointCutoffIndex`
- **Context window building**: System + `[Checkpoint #N — summary]` + assistant acknowledgment + recent messages

### `DoomLoopDetector` (`DoomLoopDetector.cs`)

- **Detection strategy**: Normalize tool call arguments (sorted JSON keys) → create signature → check for repeating patterns
- **Supports**: Periods 1–4 (e.g., detects AAAA, ABAB, ABCABC, ABCDABCD)
- **Threshold**: Period 1 = 3 repetitions, Periods 2-4 = 2 repetitions
- **History**: Max 12 signatures tracked
- **Action**: Injects system message `[System: Doom loop detected...]` and aborts turn

### `TokenTracker` (`TokenTracker.cs`)

- Tracks: total prompt/completion tokens, API call count, max prompt tokens, per-call tool usage, files modified/created
- `OnUsageUpdated` callback for TUI live updates
- `GetSummary()` produces a formatted statistics block

---

## 6. LLM Provider Layer (Llm/)

### `ILlmClient` Interface

```csharp
interface ILlmClient : IDisposable {
    IAsyncEnumerable<StreamChunk> StreamChatAsync(
        IReadOnlyList<Message> messages,  // Conversation history
        JsonElement? tools,               // Tool definitions passed to LLM
        LlmOptions options,               // Model, temperature, max_tokens, top_p, etc.
        CancellationToken ct
    );
}
```

### `StreamChunk` Record

```csharp
record StreamChunk {
    string? ThinkingDelta           // Reasoning/thinking tokens (suppressed from final output)
    string? TextDelta               // Visible response text
    ToolCall? ToolCallDelta         // Tool call parsed from stream
    bool IsComplete                 // End-of-stream
    UsageInfo? Usage                // Token counts (from stream_options: include_usage)
}
```

### `LlmOptions` Record

```csharp
record LlmOptions {
    string Model                    // Override model name
    double Temperature = 0.2        // Sampling temperature
    int MaxTokens = 4096            // Max output tokens
    double TopP = 0.8              // Nucleus sampling
    int TopK = 20                   // Top-K sampling
    double PresencePenalty = 1.5    // Presence penalty
    double MinP = 0.0              // Minimum probability
    double RepetitionPenalty = 1.0 // Repetition penalty
    bool? EnableThinking            // Thinking/reasoning mode toggle
}
```

### Provider Registry (4 providers in `ProviderRegistry.cs`)

| Provider (`Name`) | Client Class | Default Endpoint | Default Model | Validation |
|-------------------|-------------|-----------------|---------------|------------|
| `local` | `OpenAiCompatClient` | `http://localhost:7474` | Auto-detected via `/props` | None |
| `openai` | `OpenAiCompatClient` | `https://api.openai.com` | `gpt-4o` | Requires API key |
| `anthropic` | `AnthropicClient` | `https://api.anthropic.com` | `claude-sonnet-4-20250514` | Requires ANTHROPIC_API_KEY |
| `ollama` | `OpenAiCompatClient` | `http://localhost:11434` | `qwen3.5:9b` | None |

**Provider selection logic** (`ProviderRegistry.CreateClient()`):
1. If `config.Providers` has an entry with `Active: true`, use that provider's client
2. Default: `OpenAiCompatClient` with the configured LLM endpoint

### `OpenAiCompatClient` (`OpenAiCompatClient.cs`)

- **Streaming**: SSE (`data: ...` lines) from `POST {endpoint}/v1/chat/completions`
- **Tool call detection** — two strategies:
  1. **Standard OpenAI**: Parses `delta.tool_calls` array from SSE chunks, accumulates by index
  2. **Qwen XML**: If text contains `<function=name>` tags, falls back to regex extraction: `<function=(\w+)>(.*?)</function>` with nested `<parameter=key>value</parameter>`
- **Thinking support**: Reads `delta.reasoning_content` field (Qwen-style thinking tokens)
- **Retry**: Exponential backoff (1s, 4s, 16s) for 429/500/502/503/504. Max 3 retries.
- **Tool choice**: `"auto"` when tools are provided. `"none"` for warmup/completion requests.

### `AnthropicClient` (`AnthropicClient.cs`)

- **Streaming**: SSE from `POST {endpoint}/v1/messages`
- **Event types**:
  - `content_block_start` → detects tool_use block, captures ID + name
  - `content_block_delta` → text_delta or input_json_delta (tool argument fragments)
  - `content_block_stop` → yields complete tool call
  - `message_delta` → yields usage info (completion_tokens only)
  - `message_stop` → yields completion marker
  - `error` → throws exception
- **System prompt**: Sent as top-level `system` field (not in messages array)
- **Tool format**: Anthropic-specific format with `name`, `description`, `input_schema`
- **Tool results**: Wrapped as `{ type: "tool_result", tool_use_id, content }` under role `user`

---

## 7. Built-in Tool Inventory (Tools/)

### Tool Interface (`ITool.cs`)

```csharp
interface ITool {
    string Name
    string Description
    JsonElement InputSchema           // JSON Schema for arguments
    bool IsConcurrencySafe            // Can run in parallel with other tools
    bool IsReadOnly                   // Does not modify state
    bool IsDeferred                   // Not included in default tool list (default: false)
    Task<ToolResult> ExecuteAsync(JsonElement input, ToolContext context, CancellationToken ct)
    PermissionLevel RequiredPermission(JsonElement input)  // AutoAllow | Ask | Deny
    IReadOnlyList<Capability> RequiredCapabilities(JsonElement input)  // For capability-based permissions
}
```

### Tool Base Class (`ToolBase.cs`)

```csharp
abstract class ToolBase : ITool {
    abstract string Name
    abstract string Description
    virtual bool IsConcurrencySafe = false
    virtual bool IsReadOnly = false
    virtual bool IsDeferred = false
    virtual PermissionLevel DefaultPermission = PermissionLevel.Ask
    abstract SchemaBuilder DefineSchema()
    abstract Task<ToolResult> ExecuteCoreAsync(JsonElement input, ToolContext context, CancellationToken ct)
    // InputSchema auto-built from DefineSchema() → cached
    // ExecuteAsync() delegates to ExecuteCoreAsync()
}
```

### Schema Builder (`SchemaBuilder`, in `ToolBase.cs`)

Fluent API for defining JSON Schema:

```csharp
new SchemaBuilder()
    .AddString("name", "Description")
    .AddInteger("count", "Description", minimum: 1, maximum: 100)
    .AddBoolean("flag", "Description")
    .AddEnum("mode", "Description", "fast", "deep")
    .AddArray("items", "Description", new { type = "string" })
    .AddProperty("custom", new { type = "object", properties = new { ... } })
    .Require("name", "count")
    .Build()
```

Returns `JsonElement` with type=object, properties dict, optional required array.

### Full Tool Catalog

#### File Read/Write Tools

| Tool | Name | Read-Only | Concurrency Safe | Permission | Schema |
|------|------|-----------|------------------|------------|--------|
| `FileReadTool` | `FileRead` | ✅ | ✅ | AutoAllow | `file_path` (required), `from_cursor` (optional), `limit` (optional) |
| `FileWriteTool` | `FileWrite` | ❌ | ❌ | Ask | `file_path` (required), `content` (required) |
| `FileEditTool` | `FileEdit` | ❌ | ❌ | Ask | `file_path` (required), `old_string` (required), `new_string` (required), `replace_all` (optional) |
| `ApplyPatchTool` | `ApplyPatch` | ❌ | ❌ | Ask | `patch` (required) — unified diff format |

#### Search Tools

| Tool | Name | Read-Only | Concurrency Safe | Permission | Schema |
|------|------|-----------|------------------|------------|--------|
| `GlobTool` | `Glob` | ✅ | ✅ | AutoAllow | `pattern` (required), `path` (optional) |
| `GrepTool` | `Grep` | ✅ | ✅ | AutoAllow | `pattern` (required), `path` (optional), `include` (optional) |
| `ListDirectoryTool` | `ListDirectory` | ✅ | ✅ | AutoAllow | `path` (required) |
| `ToolSearchTool` | `ToolSearch` | ✅ | ✅ | AutoAllow | `query` (required), `max_results` (optional) |

#### Web Tools

| Tool | Name | Read-Only | Concurrency Safe | Permission | Schema |
|------|------|-----------|------------------|------------|--------|
| `WebFetchTool` | `WebFetch` | ✅ | ✅ | Ask | `url` (required), `format` (optional: markdown/text/html) |
| `WebSearchTool` | `WebSearch` | ✅ | ✅ | Ask | `query` (required), `num_results` (optional), `livecrawl` (optional) |

#### Execution Tools

| Tool | Name | Read-Only | Concurrency Safe | Permission | Schema |
|------|------|-----------|------------------|------------|--------|
| `BashTool` | `Bash` | ❌ | ❌ | Ask/Deny* | `command` (required), `timeout_ms` (optional, max 600000), `background` (optional) |
| `AgentTool` | `Agent` | ❌ | ✅ | Ask** | `description` (required), `prompt` (required), `agent_type` (optional: general-purpose/Explore/Plan/Coder/Verify) |

\* `BashTool`: `Deny` for destructive commands (detected by `SanityCheck.IsDestructiveCommand()`), `Ask` otherwise.
\* `AgentTool`: Uses capability-based permission (`AgentSpawnCap`).

#### Interactive Tools

| Tool | Name | Read-Only | Concurrency Safe | Permission | Schema |
|------|------|-----------|------------------|------------|--------|
| `AskUserTool` | `AskUser` | ❌ | ✅ | AutoAllow | `question` (required) |
| `TodoTool` | `TodoWrite` | ❌ | ✅ | AutoAllow | `todos` (required array), `description` (optional) |

#### Memory Tools

| Tool | Name | Read-Only | Concurrency Safe | Permission | Schema |
|------|------|-----------|------------------|------------|--------|
| `MemorySaveTool` | `MemorySave` | ❌ | ✅ | Ask | `name` (required), `type` (required), `description` (required), `content` (required) |

#### Plan Mode Tools

| Tool | Name | Read-Only | Concurrency Safe | Permission | Schema |
|------|------|-----------|------------------|------------|--------|
| `EnterPlanModeTool` | `EnterPlanMode` | ✅ | N/A | AutoAllow | (none) |
| `ExitPlanModeTool` | `ExitPlanMode` | ✅ | N/A | AutoAllow | `plan` (optional) — text plan |

#### Intelligence Tools

| Tool | Name | Read-Only | Concurrency Safe | Permission | Schema |
|------|------|-----------|------------------|------------|--------|
| `LspTool` | `Lsp` | ✅ | ❌ | AutoAllow | `operation` (required: hover/definition/references), `file_path` (required), `line` (required), `character` (required) |
| `RoslynTool` | `Roslyn` | ✅ | ✅ | AutoAllow | `operation` (required), various per-operation args |

#### Playbook Tool

| Tool | Name | Read-Only | Concurrency Safe | Permission | Schema |
|------|------|-----------|------------------|------------|--------|
| `PlaybookTool` | `Playbook` | ❌ | ✅ | Ask | `name` (required) + playbook-specific params |

#### MCP Tools (Dynamic)

| Tool | Name Format | Read-Only | Concurrency Safe | Permission |
|------|-------------|-----------|------------------|------------|
| McpToolAdapter | `mcp__{serverName}__{toolName}` | Varies | ✅ | Ask |

### `ToolResult` Record (`ToolResult.cs`)

```csharp
record ToolResult {
    string ModelPreview                // Human-readable result
    object? MachinePayload             // Structured payload for programmatic use
    IReadOnlyList<ArtifactRef> Artifacts  // References to persisted large outputs
    IReadOnlyList<string> Warnings
    IReadOnlyList<SideEffect> SideEffects
    ResultClass Class                  // Success | InvalidInput | PermissionDenied | StateConflict | Crash | Empty | Cancelled
    string? RetryHint                  // Suggestion for retrying on failure
    string? CacheKey
    string? Diff                       // Inline diff text (for file edits)
    bool BreakTurn                     // Signal to stop the turn (plan mode presentation)
}

enum ResultClass { Success, InvalidInput, PermissionDenied, StateConflict, Crash, Empty, Cancelled }
```

Factory methods: `ToolResult.Success()`, `.Error()`, `.InvalidInput()`, `.PermissionDenied()`, `.StateConflict()`, `.Crash()`, `.Empty()`, `.Cancelled()`, `.SuccessWithPayload()`.

### `ToolContext` (`ToolContext.cs`)

```csharp
class ToolContext {
    ToolRegistry ToolRegistry
    SessionState Session
    PermissionEngine Permissions
    AppConfig Config
    string WorkingDirectory
    Action<string> WriteOutput
    Func<string, CancellationToken, Task<string>> AskUser
    FileHistory? FileHistory
    CursorStore? Cursors
    Action? BeginResponse
    Action? EndResponse
    Action<string>? StreamText
}
```

### Concurrency Model

- **Read-only + concurrency-safe tools**: Executed in parallel via `Task.WhenAll()`
- **Write tools**: Executed sequentially (one at a time)
- **Early-flight optimization**: Tools that are read-only AND concurrency-safe can be launched while the LLM stream is still in progress (pipeline steps P2.4 in `ConversationLoop.cs`). Results are collected after streaming completes. If one crashes, sibling tasks are cancelled.

---

## 8. Permission System (Permissions/)

### Permission Engine (`PermissionEngine.cs`)

The engine enforces two parallel permission systems:

#### A. Legacy 3-Tier Permission (tool-defined)

```csharp
enum PermissionLevel { AutoAllow, Ask, Deny }
```

**Flow** (`CheckAsync()`):

```
1. Check config deny patterns → if match, auto-deny (or prompt if escalation threshold hit)
2. Check session allow/deny all → return cached decision
3. If level = AutoAllow → allow
4. If level = Deny → deny
5. If config allow patterns match → allow (via glob pattern matching)
6. Otherwise → prompt user
```

**Session-level decisions**:
- `AllowAll` — adds tool to `_sessionAllowAll` set
- `DenyAll` — adds tool to `_sessionDenyAll` set (with message: "Do NOT suggest chmod/chown/OS permission commands")

**Escalation**: After 3 consecutive denials or 20 total denials, forces a re-prompt

**Pattern matching**: Glob-to-regex translation (`*` → `.*`, `?` → `.`)

#### B. Capability-Based Permission (newer, richer)

**Capability types** (`Capability.cs`):

| Capability | Fields | Description |
|------------|--------|-------------|
| `FileReadCap` | `Path` | Reading a file |
| `FileWriteCap` | `Path` | Writing to a file |
| `ProcessExecCap` | `Binary`, `Args`, `WorkingDir` | Running a command |
| `NetworkEgressCap` | `Host`, `Port` | Making network requests |
| `VcsMutationCap` | `Repo`, `Operation` | Git operations (commit, push, etc.) |
| `MemoryCap` | `Namespace`, `Operation` | Reading/writing memory |
| `AgentSpawnCap` | `AgentType`, `Description` | Spawning a sub-agent |

**Flow** (`CheckCapabilitiesAsync()`):

```
1. If session allow/deny all → short-circuit
2. For each capability:
   a. Check deny rules (protected paths, blocked binaries)
   b. Check allow rules (session allow patterns, auto-allow rules)
3. Auto-allowed capabilities:
   - FileReadCap within workspace
   - MemoryCap (read)
   - ProcessExecCap for safe read-only commands (ls, cat, git status, etc.)
4. Uncovered capabilities → prompt user with Allow/Deny/AllowAll/DenyAll
```

**Auto-allowed safe read-only commands**:

```
ls, cat, head, tail, wc, pwd, whoami, date, echo, which, type, file, stat, du, df,
git status, git log, git diff, git branch, git show,
npm list, npm view, yarn list,
dotnet --version, node --version, python --version
```

### PathGuard (`PathGuard.cs`)

- Validates all file paths against workspace root
- Expands relative paths and checks `StartsWith(workspaceRoot)`
- Prevents path traversal attacks

### SanityCheck (`SanityCheck.cs`)

Pre-flight validation before execution:

| Check | What it blocks |
|-------|---------------|
| **Quick destructive patterns** | Fork bombs, `dd if=/dev/zero of=/dev/sda`, `> /dev/sda` |
| **Process substitution** | `>()`, `<()`, `=()` |
| **Permission modifiers** | `chmod`, `chown`, `chattr`, `setfacl`, `icacls`, `takeown`, `attrib` |
| **`sed -i`** | Redirects to use FileEdit instead |
| **`eval`/`exec` builtins** | Arbitrary code execution via strings |
| **Inline interpreters** | `python -c`, `node -e`, `perl -e`, `ruby -e`, `php -r`, `lua -e` |
| **Protected system paths** | `/etc/`, `/usr/bin/`, `/sbin/`, `/bin/`, `/boot/`, `/sys/`, `/proc/`, `/dev/`, `/system/`, `/library/` |
| **Credential directories** | `~/.ssh`, `~/.aws`, `~/.gnupg`, `~/.config/gcloud`, `~/.kube` |

---

## 9. Configuration System (Config/)

### Three-Layer Merge

```
Layer 1 (user):    ~/.openmono/settings.json
Layer 2 (project): .openmono/settings.json  (relative to working directory)
Layer 3 (explicit): --config /path/to/settings.json
```

Environment variables override all layers.

### Full `AppConfig` Model (`AppConfig.cs`)

```csharp
class AppConfig {
    LlmConfig Llm                              // LLM connection + generation parameters
    PermissionConfig Permissions                // Tool → Allow/Deny/Ask patterns
    HookConfig Hooks                            // Pre/Post/SessionStart hooks
    PlaybookConfig Playbooks                    // Playbook search paths
    Dictionary<string, ProviderSettings> Providers    // Named provider configs
    Dictionary<string, ModelPresetSettings> ModelPresets  // Named model presets
    Dictionary<string, McpServerSettings> McpServers    // MCP server definitions
    bool AutoDetectCodeGraph = true
    bool Verbose = false
    bool ShowDetail = false
    string WorkingDirectory                     // Default: current directory
    string? HostWorkingDirectory                // For Docker host path mapping
    string DataDirectory                        // Default: ~/.openmono
}
```

### `LlmConfig` (base config, shared by ModelPresetSettings)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `Endpoint` | string | `http://localhost:7474` | LLM server URL |
| `Model` | string | `""` | Model name (auto-detected if empty) |
| `ApiKey` | string? | null | API key for cloud providers |
| `ContextSize` | int | 196608 | Maximum context window tokens |
| `MaxOutputTokens` | int | 16384 | Maximum generation tokens |
| `Temperature` | double | 0.7 | Sampling temperature |
| `TopP` | double | 0.8 | Nucleus sampling |
| `TopK` | int | 20 | Top-K sampling |
| `PresencePenalty` | double | 1.5 | Presence penalty |
| `MinP` | double | 0.0 | Minimum probability |
| `RepetitionPenalty` | double | 1.0 | Repetition penalty |

### `ProviderSettings`

```csharp
class ProviderSettings {
    string? ApiKey
    string? Endpoint
    string? Model
    bool Active                           // Set to true to activate this provider
}
```

### `McpServerSettings`

```csharp
class McpServerSettings {
    string Command                        // Server binary path
    string[]? Args                       // Command-line arguments
    Dictionary<string, string>? Env       // Environment variables
    string? WorkingDirectory
    bool Enabled = true
}
```

### `PermissionConfig`

```csharp
class PermissionConfig {
    Dictionary<string, ToolPermissionRules> Tools  // Tool name → rules
}

class ToolPermissionRules {
    List<string> Allow                    // Glob patterns for auto-allow
    List<string> Deny                     // Glob patterns for auto-deny
    List<string> Ask                      // Glob patterns for ask-on-each
}
```

### `HookConfig`

```csharp
class HookConfig {
    List<HookDefinition> PreToolUse       // Run before tool execution
    List<HookDefinition> PostToolUse      // Run after tool execution
    List<HookDefinition> SessionStart     // Run on session start
}

class HookDefinition {
    HookCondition? Condition              // if.tool, if.inputContains
    string Run                            // Bash command to execute
}

class HookCondition {
    string? Tool                          // Filter by tool name
    string? InputContains                 // Filter by input content
}
```

### Environment Variable Overrides

| Variable | Maps to |
|----------|---------|
| `OPENMONO_ENDPOINT` | `config.Llm.Endpoint` |
| `OPENMONO_MODEL` | `config.Llm.Model` |
| `OPENMONO_API_KEY` | `config.Llm.ApiKey` |
| `OPENMONO_WORKSPACE` | `config.WorkingDirectory` |
| `OPENMONO_HOST_WORKSPACE` | `config.HostWorkingDirectory` |
| `OPENMONO_DATA_DIR` | `config.DataDirectory` |
| `OPENMONO_CONTEXT_SIZE` | `config.Llm.ContextSize` |
| `OPENMONO_MAX_OUTPUT_TOKENS` | `config.Llm.MaxOutputTokens` |
| `OPENMONO_TOP_P` | `config.Llm.TopP` |
| `OPENMONO_TOP_K` | `config.Llm.TopK` |
| `OPENMONO_PRESENCE_PENALTY` | `config.Llm.PresencePenalty` |
| `OPENMONO_MIN_P` | `config.Llm.MinP` |
| `OPENMONO_REPETITION_PENALTY` | `config.Llm.RepetitionPenalty` |
| `OPENMONO_MODEL_PRESET` | Activates named preset |
| `OPENMONO_PROVIDER` | Activates named provider |

---

## 10. MCP Protocol (Mcp/)

### `McpClient` (`McpClient.cs`)

- **Transport**: JSON-RPC 2.0 over stdio
- **Protocol version**: `2024-11-05`
- **Client info**: `{ name: "OpenMono.ai", version: "0.1.0" }`
- **Thread safety**: `SemaphoreSlim(1,1)` per client
- **Error handling**: Throws `InvalidOperationException` with "MCP error: {message}" on JSON-RPC error responses
- **Timeout**: No per-request timeout (relies on CancellationToken)

**Operations**:
```csharp
// Connection
client = await McpClient.ConnectAsync(config, ct)
  → sends "initialize" request
  → sends "notifications/initialized"

// Tool discovery
JsonElement tools = await client.ListToolsAsync(ct)
  → returns { tools: [{ name, description, inputSchema }] }

// Tool execution
JsonElement result = await client.CallToolAsync(name, arguments, ct)
  → returns { content: [{ type, text }], isError? }

// Resources (optional)
JsonElement resources = await client.ListResourcesAsync(ct)
JsonElement resource = await client.ReadResourceAsync(uri, ct)
```

### `McpServerManager` (`McpServerManager.cs`)

- Connects to all enabled MCP servers on startup
- Registers returned tools via `McpToolAdapter`
- Tool name format: `mcp__{serverName}__{toolName}`
- Handles connection failures gracefully (logs warning, continues)

### `McpToolAdapter` (`McpToolAdapter.cs`)

- Wraps MCP tools as `ITool` instances
- `IsConcurrencySafe = true`, `IsReadOnly = false` (unless the MCP tool declares otherwise)
- `RequiredPermission` returns `Ask`
- Result extraction: Looks for `content[].type == "text"` items, joins with newlines
- Supports structured payload via `McpResponsePayload` for programmatic use

---

## 11. LSP Integration (Lsp/)

### `LspServerManager` (`LspServerManager.cs`)

**Default language servers**:

| Language | Extension | Command | Args |
|----------|-----------|---------|------|
| C# | `.cs` | `omnisharp` | `[-lsp]` |
| TypeScript | `.ts`, `.tsx` | `typescript-language-server` | `[--stdio]` |
| JavaScript | `.js`, `.jsx` | `typescript-language-server` | `[--stdio]` |
| Python | `.py` | `pylsp` | — |
| Go | `.go` | `gopls` | `[serve]` |
| Rust | `.rs` | `rust-analyzer` | — |
| Java | `.java` | (no default) | — |

**Lazy-start**: Servers are started on first use (when a file of that language is queried) via `GetClientAsync(filePath, ct)`. If a server fails to start, the warning is logged and subsequent calls return `null`.

### `LspClient` (`LspClient.cs`)

- JSON-RPC 2.0 over stdio
- Capabilities: `textDocument/hover`, `textDocument/definition`, `textDocument/references`
- Initialization: Sends `initialize` with `capabilities` + `textDocument/didOpen` notifications

---

## 12. Agent System (Agents/)

### 5 Built-in Agent Definitions (`AgentDefinition.cs`)

| Agent | Name | Allowed Tools | Max Turns | System Prompt Focus |
|-------|------|--------------|-----------|-------------------|
| **GeneralPurpose** | `general-purpose` | `*` (all) | 200 | Full access for complex multi-step tasks. Rules: read before write, minimal changes, no comments beyond what was asked, never leave code broken. |
| **Explore** | `Explore` | `FileRead`, `Glob`, `Grep`, `mcp__*` | 100 | Read-only codebase discovery. Cannot write anything. Reports exact paths and line numbers. Uses Graphify MCP tools when available. |
| **Plan** | `Plan` | `FileRead`, `Glob`, `Grep`, `TodoWrite`, `mcp__*` | 100 | Software architect. Produces numbered implementation plans with dependencies and risks. Cannot write files. |
| **Coder** | `Coder` | `FileRead`, `FileWrite`, `FileEdit`, `Glob`, `Grep`, `Bash` | 300 | Senior engineer. Minimal changes, verifies with tests, never leaves code broken. Lists every file changed. |
| **Verify** | `Verify` | `FileRead`, `Glob`, `Grep`, `Bash`, `Roslyn`, `Lsp`, `mcp__*` | 150 | Adversarial tester. Runs `dotnet build`, `dotnet test`, Roslyn diagnostics, probes edge cases. Cannot modify project files (writes ephemeral scripts to /tmp only). Structured output with PASS/FAIL/PARTIAL verdict. |

### Sub-Agent Execution Flow (`AgentTool.ExecuteCoreAsync()`)

1. Create sub-`ToolRegistry` with parent's tools minus `AgentTool`, filtered by allowed tools
2. Create sub-`SessionState` with agent system prompt + user prompt
3. Create fresh `OpenAiCompatClient` (sub-agents always use OpenAI-compatible protocol)
4. Loop up to `agentDef.MaxTurns` iterations:
   - Stream LLM response
   - Stream text to parent via `ToolContext.StreamText` (if available)
   - If no tool calls → done
   - Execute each tool call (permission-checked through parent's engine)
   - Feed results back
5. Return final text (or "hit turn limit" warning)

---

## 13. Playbook System (Playbooks/)

### Playbook Definition (`PlaybookDefinition.cs`)

```csharp
record PlaybookDefinition {
    string Name                           // Unique name
    string Version = "1.0.0"
    string Description
    TriggerMode Trigger = Manual          // Manual, Auto, Both
    string[] TriggerPatterns              // Patterns for auto-trigger
    bool UserInvocable = true
    string? ArgumentHint                  // Usage hint (e.g., "<message>")
    Dictionary<string, ParameterDefinition> Parameters
    StepDefinition[] Steps
    ConstraintSet Constraints
    string[] AllowedTools = ["*"]
    ContextMode ContextMode = Selective   // Full, Selective, Fork
    int MaxContextTokens = 3000
    string[] DependsOn                    // Other playbooks this depends on
    string[] Tags
    string BasePath
    string? RoleDescription
}
```

### Parameter Types and Constraints

```csharp
enum ParameterType { String, Number, Boolean, Array }

record ParameterDefinition {
    ParameterType Type
    bool Required
    object? Default
    string? Hint
    string[]? Enum                       // String enum values
    double? Min / Max                    // Number bounds
}
```

### Step Types

```csharp
record StepDefinition {
    string Id                            // Unique step ID
    string? File                         // Path to prompt template file
    string? InlinePrompt                 // Inline LLM prompt
    string[]? Requires                   // Required prior step IDs
    GateType Gate = None                 // None, Confirm, Review, Approve
    string? Agent                        // Agent type to use (Explore, Plan, Coder, etc.)
    string? Output                       // Variable name for step output
    string? Script                       // Bash command to execute
    string? Playbook                     // Sub-playbook name
    Dictionary<string, string>? Params   // Parameters for sub-playbook
}
```

### Template Engine (`TemplateEngine.cs`)

- `{{param}}` — substituted with playbook parameter values
- `{{step.output}}` — substituted with output from a previous step

### Gate Types (`GateType`)

| Gate | Behavior |
|------|----------|
| `None` | Step executes automatically |
| `Confirm` | User must confirm before execution |
| `Review` | User must review step output before proceeding |
| `Approve` | User must explicitly approve |

### Constraints (`ConstraintSet`)

```csharp
record ConstraintSet {
    string? File                         // Path to constraint file
    List<string> Inline                  // Inline constraint expressions
}
```

### Execution Pipeline (`PlaybookExecutor.cs`)

1. Validate parameters against `ParameterDefinition` types/constraints using `ParameterValidator`
2. Resolve template variables in prompts/scripts
3. Execute steps sequentially:
   - For `Script` steps: run via Bash
   - For `InlinePrompt`/`File` steps: call LLM with the prompt
   - For `Playbook` steps: resolve and execute sub-playbook
   - For `Gate` steps: pause for user interaction
4. Track state via `PlaybookState` for checkpoint/resume
5. Report results

### Built-in Example Playbooks (in `docs/playbooks-examples/`)

| Playbook | Purpose |
|----------|---------|
| `commit` | Stage and commit changes with a message |
| `release` | Create a release tag |
| `pr-ready` | Run checks before opening a PR |
| `deploy-ftp` | Deploy via FTP |
| `db-migrate` | Run database migrations |
| `incident-response` | Structured incident handling |
| `graphify` | Build semantic knowledge graph |

---

## 14. Memory System (Memory/)

### `MemoryStore` (`MemoryStore.cs`)

- **Storage location**: `~/.openmono/memory/`
- **File format**: Markdown files with YAML frontmatter
  ```markdown
  ---
  name: project-conventions
  description: Coding conventions for this project
  type: project
  ---
  Content here...
  ```
- **Auto-generated index**: `MEMORY.md` with links to all entries
- **Operations**: `LoadAll()`, `SaveAsync()`, `RemoveAsync()`
- **Memory entry format**:
  ```csharp
  record MemoryEntry {
      string Name         // Unique identifier
      string Description  // Human-readable description
      string Type         // category (project, preference, convention, etc.)
      string Content      // Full markdown content
      string FilePath     // Path to .md file
  }
  ```
- **Injection**: All memory entries are loaded at session start and injected into the system prompt under `# Memory` section

---

## 15. File History / Undo (History/)

### `FileHistory` (`FileHistory.cs`)

- **Purpose**: Snapshot-based undo system for file modifications
- **Storage**: `~/.openmono/file-history/`
- **Snapshot recording**:
  - `RecordBefore(filePath, toolName, messageIndex)` — captures file content before mutation
  - `RecordAfter(filePath)` — captures file content after mutation
  - `TrackAsync(filePath, toolName, messageIndex, action)` — convenience wrapper
- **Undo** (`RevertAsync(count, ct)`):
  - Reverses last N snapshots (oldest-first in the range)
  - For created files: deletes them
  - For modified files: restores `ContentBefore`
  - Removes reverted snapshots from history

### `FileSnapshot` (`FileSnapshot.cs`)

```csharp
record FileSnapshot {
    string FilePath
    string? ContentBefore                // null = file didn't exist (creation)
    string ContentAfter                  // empty = will be filled by RecordAfter
    DateTime Timestamp
    string ToolName
    int MessageIndex
    bool IsCreation => ContentBefore is null
}
```

---

## 16. Hooks System (Hooks/)

### `HookRunner` (`HookRunner.cs`)

**Three hook points**:
1. `RunSessionStartHooksAsync()` — runs during startup (before entering main loop)
2. `RunPreToolUseHooksAsync(toolName, toolInput)` — runs before each tool execution
3. `RunPostToolUseHooksAsync(toolName, toolOutput)` — runs after each tool execution

**Conditional execution** (pre/post only):
```json
{
  "if": { "tool": "Bash", "inputContains": "git push" },
  "run": "echo 'Push detected at {{tool_name}}'"
}
```

**Template variables**:
- `{{tool_name}}` — Name of the tool being executed (pre/post)
- `{{tool_input}}` — JSON string of tool input (pre)
- `{{tool_output}}` — Tool result content (post)

**Execution**:
- Commands run via `/bin/bash -c`
- 30-second timeout per hook
- Non-zero exit codes logged as warnings
- Failures are non-fatal (logged, execution continues)

---

## 17. Secret Scanner (Utils/SecretScanner.cs)

### 20+ Regex Rules

| Rule ID | Pattern (abbreviated) | Service |
|---------|----------------------|---------|
| `aws-access-token` | `(A3T\|AKIA\|ASIA\|ABIA\|ACCA)[A-Z2-7]{16}` | AWS access keys |
| `gcp-api-key` | `AIza[\w-]{35}` | Google Cloud API keys |
| `azure-ad-client-secret` | `[a-zA-Z0-9_~.]{3}\dQ~[a-zA-Z0-9_~.-]{31,34}` | Azure AD secrets |
| `digitalocean-pat` | `dop_v1_[a-f0-9]{64}` | DigitalOcean PAT |
| `anthropic-api-key` | `sk-ant-api03-[a-zA-Z0-9_-]{93}AA` | Anthropic API keys |
| `anthropic-admin-api-key` | `sk-ant-admin01-[a-zA-Z0-9_-]{93}AA` | Anthropic admin keys |
| `openai-api-key` | `sk-(proj\|svcacct\|admin)-...T3BlbkFJ...` | OpenAI API keys |
| `huggingface-access-token` | `hf_[a-zA-Z]{34}` | HuggingFace tokens |
| `github-pat` | `ghp_[0-9a-zA-Z]{36}` | GitHub PAT |
| `github-fine-grained-pat` | `github_pat_\w{82}` | GitHub fine-grained PAT |
| `github-app-token` | `(ghu\|ghs)_[0-9a-zA-Z]{36}` | GitHub app tokens |
| `github-oauth` | `gho_[0-9a-zA-Z]{36}` | GitHub OAuth |
| `github-refresh-token` | `ghr_[0-9a-zA-Z]{36}` | GitHub refresh tokens |
| `gitlab-pat` | `glpat-[\w-]{20}` | GitLab PAT |
| `gitlab-deploy-token` | `gldt-[0-9a-zA-Z_-]{20}` | GitLab deploy tokens |
| `slack-bot-token` | `xoxb-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9-]*` | Slack bot tokens |
| `slack-user-token` | `xox[pe](?:-[0-9]{10,13}){3}-[a-zA-Z0-9-]{28,34}` | Slack user tokens |
| `slack-app-token` | `xapp-\d-[A-Z0-9]+-\d+-[a-z0-9]+` | Slack app tokens |
| `twilio-api-key` | `SK[0-9a-fA-F]{32}` | Twilio API keys |
| `sendgrid-api-token` | `SG\.[a-zA-Z0-9=_\-.]{66}` | SendGrid API keys |
| `npm-access-token` | `npm_[a-zA-Z0-9]{36}` | npm tokens |
| `pypi-upload-token` | `pypi-AgEIcHlwaS5vcmc[\w-]{50,1000}` | PyPI upload tokens |
| `databricks-api-token` | `dapi[a-f0-9]{32}(?:-\d)?` | Databricks tokens |
| `hashicorp-tf-api-token` | `[a-zA-Z0-9]{14}\.atlasv1\.[a-zA-Z0-9\-_=]{60,70}` | Terraform Cloud tokens |
| `pulumi-api-token` | `pul-[a-f0-9]{40}` | Pulumi tokens |
| `postman-api-token` | `PMAK-[a-fA-F0-9]{24}-[a-fA-F0-9]{34}` | Postman tokens |
| `grafana-api-key` | `eyJrIjoi[A-Za-z0-9+/]{70,400}={0,3}` | Grafana API keys |
| `grafana-cloud-api-token` | `glc_[A-Za-z0-9+/]{32,400}={0,3}` | Grafana Cloud tokens |
| `grafana-service-account-token` | `glsa_[A-Za-z0-9]{32}_[A-Fa-f0-9]{8}` | Grafana SA tokens |
| `stripe-access-token` | `(sk\|rk)_(test\|live\|prod)_[a-zA-Z0-9]{10,99}` | Stripe keys |
| `shopify-access-token` | `shpat_[a-fA-F0-9]{32}` | Shopify tokens |
| `shopify-shared-secret` | `shpss_[a-fA-F0-9]{32}` | Shopify shared secrets |
| `private-key` | `-----BEGIN[A-Z0-9_-]{0,100}PRIVATE KEY-----...-----END...-----` | PEM private keys |
| Additional: sentry, mailchimp, mailgun, discord, telegram, datadog | | |

### Usage
- `Scan(content)` — returns list of matched rule IDs (unique)
- `Redact(content)` — replaces matched values with `[REDACTED]`
- `RuleIdToLabel(ruleId)` — converts `"aws-access-token"` → `"AWS Access Token"`

---

## 18. Rendering System (Rendering/)

### Interface Hierarchy

```
IRenderer (composite)
├── IOutputSink       — Write output, streaming, tool results, warnings
├── IInputReader      — Read input, ask user, ask permission
└── ILiveFeedback     — Begin/end turn lifecycle
```

### `IOutputSink` Interface

```csharp
interface IOutputSink {
    bool Verbose { get; set; }

    // Conversation streaming
    void StartAssistantResponse()
    void StreamText(string text)
    void EndAssistantResponse(TurnMetrics? metrics = null)

    // Thinking/Reasoning
    void AppendThinking(string text)
    void CollapseThinking(int charCount)

    // Waiting indicator
    void ShowWaitingIndicator()
    void ClearWaitingIndicator()

    // Output messages
    void WriteWelcome(string model, string endpoint)
    void WriteMarkdown(string markdown)
    void WriteDebug(string message)

    // Tool lifecycle
    void WriteToolStart(string toolName, string args)
    void WriteToolSuccess(string toolName)
    void WriteToolError(string toolName, string error)
    void WriteToolDenied(string toolName, string reason)
    void WriteToolDiff(string diff)
    void WriteToolContent(string toolName, string filePath, string content)

    // Log levels
    void WriteWarning(string message)
    void WriteError(string message)
    void WriteInfo(string message)

    // Meta
    void WriteTodos(IReadOnlyList<TodoItem> todos)
    void ClearConversation()
}
```

### `IInputReader` Interface

```csharp
interface IInputReader {
    void EnableCommandSuggestions(CommandRegistry registry)
    string ReadInput()                                    // Read user input
    string? ShowCommandPicker(CommandRegistry registry)    // Show command picker (/)
    Task<string> AskUserAsync(string question, CancellationToken ct)
    Task<PermissionResponse> AskPermissionAsync(string toolName, string summary, CancellationToken ct)
}
```

### Two Implementations

| Aspect | `TerminalRenderer` | `AnsiTuiRenderer` |
|--------|-------------------|-------------------|
| **Base class** | None (direct impl) | None (direct impl) |
| **Output** | Spectre.Console (AnsiConsole) | Terminal.Gui + raw ANSI |
| **Input** | Console.ReadLine with history | Terminal.Gui text field |
| **Markdown** | Spectre.Console Markdown | Custom AnsiMarkdown pipeline |
| **Thinking** | Collapsible text block | Collapsible TUI panel |
| **Permissions** | Y/N prompts | Inline menu (Allow/Deny/Always/Never) |
| **Mode** | Scrolling terminal | Full-screen fixed layout |
| **Ctrl+C** | Double-Ctrl+C to exit | Keyboard manager |

### `TurnMetrics` (passed to `EndAssistantResponse`)

```csharp
record TurnMetrics {
    int PromptTokens
    int CompletionTokens
    TimeSpan TimeToFirstToken
    TimeSpan TotalElapsed
}
```

---

## 19. TUI System (Tui/)

### Components

| Component | File | Purpose |
|-----------|------|---------|
| `ApprovalController` | `ApprovalController.cs` | Inline tool approval with Accept/Reject/Always/Never |
| `PauseController` | `PauseController.cs` | User-triggerable pause/resume during LLM streaming |
| `StreamingMetrics` | `StreamingMetrics.cs` | Real-time display: tokens/s, TTFT, elapsed time |
| `ContextWindowMeter` | `ContextWindowMeter.cs` | Visual progress bar showing context usage % |
| `Keybindings/` | `Keybindings/` directory | Keyboard shortcut registration and dispatch |
| `Rendering/` | `Rendering/` subdirectory | Markdown renderer, syntax highlighter, theme management |
| `Export/` | `Export/` subdirectory | Conversation export to Markdown, JSON, HTML |

### Key UI Features
- **Live streaming**: Text appears character-by-character from LLM
- **Thinking collapse**: Reasoning tokens collapse into a collapsible panel
- **Tool approval**: Non-blocking overlay for permission decisions
- **Command palette**: Ctrl+P or `/` to browse/select slash commands
- **Export**: Full conversation export in 3 formats

---

## 20. Slash Commands (Commands/)

| Command | Class | Description |
|---------|-------|-------------|
| `/help` | `HelpCommand` | List all available commands |
| `/status` | `StatusCommand` | Session info (turns, tokens, model, checkpoints) |
| `/stats` | `StatsCommand` | Token usage summary + tool analytics |
| `/model <name>` | `ModelCommand` | Switch model mid-session |
| `/compact` | `CompactCommand` | Force context compaction via LLM summary |
| `/clear` | `ClearCommand` | Wipe entire conversation |
| `/retry` | `RetryCommand` | Resend last user message |
| `/undo [n]` | `UndoCommand` | Revert last n file modifications (default: 1) |
| `/checkpoint` | `CheckpointCommand` | Force checkpoint creation |
| `/think` | `ThinkCommand` | Toggle step-by-step reasoning mode |
| `/init` | `InitCommand` | Auto-generate OPENMONO.md from project analysis |
| `/resume [id]` | `ResumeCommand` | Restore a previous session by ID |
| `/export` | `ExportCommand` | Export conversation (markdown, json, html) |
| `/debug` | `DebugCommand` | Toggle verbose debug output |
| `/plan` | `PlanCommand` | Enter plan mode (read-only) |
| `/quit` | (inline in Program.cs) | Exit the application |

### Command Interface

```csharp
interface ICommand {
    string Name
    string Description
    Task ExecuteAsync(string[] args, CommandContext ctx, CancellationToken ct)
}

class CommandContext {
    SessionState Session
    ToolRegistry ToolRegistry
    CommandRegistry CommandRegistry
    AppConfig Config
    IRenderer Renderer
    string WorkingDirectory
}
```

---

## 21. Utilities (Utils/)

| File | Purpose | Key Features |
|------|---------|-------------|
| `SecretScanner.cs` | API key/credential detection | 20+ regex rules, `Scan()` returns rule IDs, `Redact()` replaces with `[REDACTED]` |
| `ProcessRunner.cs` | Simple process execution | `RunAsync(command, workingDir, timeoutMs)` → `(exitCode, stdout, stderr)` |
| `ProcessWatchdog.cs` | Graceful+hard kill | `ScheduleHardKill()` → runs after current task completes |
| `PathUtils.cs` | Path resolution | Workspace-relative path normalization |
| `GitHelper.cs` | Git context | `GetContextAsync()` → branch, status, recent commits (for system prompt injection) |
| `FileSearcher.cs` | Pattern-based file search | Recursive search with include/exclude patterns |
| `Log.cs` | File-based logging | `Log.Info()`, `Log.Warn()`, `Log.Error()`, `Log.Debug()` to single-file append |
| `InputSanitizer.cs` | Input cleansing | Strips control characters, ANSI escape codes from user input |
| `InlineDiff.cs` | Diff computation | Colored diff display for file edits |

---

## 22. Session Persistence

### Storage Location

`~/.openmono/sessions/`

### File Format

- **Journal file**: `{date}_{sessionId}.journal.jsonl`
  - First line: header (version, model, date)
  - Subsequent lines: JSON events (see TurnJournal section)
- **Session metadata**: `{sessionId}.session.json`
  - Contains session state snapshot
- **Checkpoints**: `~/.openmono/sessions/{sessionId}/checkpoints/checkpoint_{N}.json`
  - Per-checkpoint files with LLM-generated summaries

### Auto-Save

Session is saved after every turn via `SessionManager.SaveAsync()` (in the `finally` block of `Program.cs`).

### Resume

`/resume [id]` loads a previous session by replaying the journal events into a fresh `SessionState`.

---

## 23. Docker Deployment

### Architecture

```
┌──────────────────────────────────────────────────┐
│  docker-compose.yml                               │
│                                                    │
│  ┌─────────────────────┐  ┌─────────────────────┐ │
│  │  llama-server        │  │  agent               │ │
│  │  (ghcr.io/ggml-org/  │  │  (Dockerfile.agent)  │ │
│  │   llama.cpp:server)  │  │                      │ │
│  │                      │  │  .NET 10 CLI         │ │
│  │  Port 7474           │  │  Mounts workspace/   │ │
│  │  196K context        │  │  Mounts ~/.openmono/ │ │
│  │  Flash-attention     │  │  Mounts Docker sock  │ │
│  │  Q8_0 KV cache       │  │                      │ │
│  └──────────┬───────────┘  └──────────┬───────────┘ │
│             │                          │             │
│             └──────────HTTP────────────┘             │
└──────────────────────────────────────────────────────┘
```

### Profiles

| Profile | Services | Use Case |
|---------|----------|----------|
| `full` | llama-server + agent | Default full deployment |
| `server` | llama-server only | LLM-only mode |
| `agent` | agent only | Agent-only mode (for external endpoints) |

### Dockerfile.agent

- Multi-stage build: `mcr.microsoft.com/dotnet/sdk:10.0` → publish → `mcr.microsoft.com/dotnet/runtime:10.0`
- Installed packages: `git`, `ripgrep`, `curl`, `jq`, `tree`, `python3`
- Optional tools: `code-review-graph`, `graphify`

### Configurations

| Config | File | Purpose |
|--------|------|---------|
| **Default (GPU)** | `docker-compose.yml` | Q4_K_M quantization, 24GB VRAM target |
| **GPU override** | `docker-compose.override.yml` | `--n-gpu-layers 99`, `--n-cpu-moe 40`, TurboQuant KV cache (turbo3), NVIDIA toolkit |
| **Hybrid MoE (CPU)** | `docker-compose.hybrid-moe.yml` | CPU-friendly, `--n-cpu-moe` flag for Qwen3.6-35B-A3B |
| **Dual-box** | (manual frp tunnel) | Agent on laptop, inference on separate GPU machine |

### Hardware Tiers

| VRAM/RAM | Model | Speed |
|----------|-------|-------|
| GPU 24 GB+ | Qwen3.6-27B-Q4_K_M | ~45-70 tok/s |
| GPU 16 GB | Qwen3.6-27B-UD-IQ3_XXS | ~20-42 tok/s |
| GPU 12 GB | Qwen3.5-9B-Q4_K_M | ~38-40 tok/s |
| GPU 8-16 GB + 32+ GB RAM | Qwen3.6-35B-A3B + MoE + TurboQuant | ~15-27 tok/s |
| CPU 24 GB RAM | Qwen3.6-35B-A3B-UD-Q4_K_XL | ~17-20 tok/s |

---

## 24. Test Infrastructure

### Test Project
- **Framework**: xUnit 2.9.3
- **Assertions**: FluentAssertions 8.3.0
- **Mocking**: NSubstitute 5.3.0
- **Skippable tests**: Xunit.SkippableFact 1.5.61
- **Test SDK**: Microsoft.NET.Test.Sdk 17.14.0

### Test Organization

| Directory | Tests For |
|-----------|-----------|
| `Tools/` | Individual tool unit tests |
| `Session/` | ConversationLoop, Compactor, SessionManager, TurnJournal, TokenTracker |
| `Tui/` | All TUI component tests |
| `Mcp/` | MCP tool adapter tests |
| `Config/` | ConfigLoaderTests |
| `Permissions/` | PermissionEngineTests |
| `Playbooks/` | Playbook loader, state, validator tests |
| `History/` | FileHistoryTests |
| `Memory/` | MemoryStoreTests |
| `Rendering/` | Interface segregation + ANSI markdown rendering tests |
| `Integration/` | Smoke tests, CapabilityAndDeferredToolTests |
| `Fakes/` | TerminalMockWrapper |

### CI Pipeline (`.github/workflows/ci.yml`)

Trigger: push/PR to `main`/`master`

```yaml
steps:
  1. Setup .NET 10.0.x
  2. dotnet restore
  3. dotnet build --configuration Release
  4. dotnet test (continues on failure)
  5. Docker build check (Dockerfile.agent)
  6. ShellCheck on scripts/
  7. Bash syntax check on get-openmono.sh, setup scripts
```

---

## 25. OpenCode SDK (opencode/)

A separate TypeScript-based AI coding agent co-located in the repo at `opencode/`. Not part of the main OpenMono C# project but shares the same repository.

### Key Information

| Aspect | Details |
|--------|---------|
| **Nature** | TypeScript AI coding agent |
| **Version** | VS Code extension v1.15.10 |
| **Package entry** | `packages/opencode` |
| **Architecture** | Plugin-based, event-driven, schema-first (per V2 specs) |
| **Install methods** | npm, bun, pnpm, scoop, choco, brew, pacman, nix, curl |

### Subdirectories

| Directory | Contents |
|-----------|----------|
| `packages/` | core, web (22+ i18n translations), sdk, slack, plugin, llm, http-recorder, function, effect-drizzle-sqlite, storybook, script |
| `sdks/vscode/` | VS Code extension (TypeScript, 3 commands, keybindings) |
| `specs/v2/` | V2 architecture specifications |
| `.github/workflows/` | 22 CI workflow files |
| Root | `flake.nix`, `flake.lock` (Nix support) |

### VS Code Extension (`sdks/vscode/`)

- **Commands**: `openChat`, `newSession`, `addFilepathToTerminal`, `undoLastAction`, `undoAction`, `showLogs`, `openTerminal`
- **Keybindings**: `cmd+escape`, `cmd+shift+escape`, `cmd+alt+k`, `ctrl+shift+z`

### Agent Switching

The `switch-agent.sh` script at the repository root allows toggling between OpenCode and OpenMono:

```bash
./scripts/switch-agent.sh opencode   # Switch to OpenCode
./scripts/switch-agent.sh openmono   # Switch to OpenMono (default)
```

---

## 26. Ruffel Mono Agent (Merged Architecture)

A merge of OpenMono.Cli (.NET 10 backend) with a TypeScript frontend, creating a local-first AI coding agent that runs entirely offline — no cloud telemetry or remote API calls. Two frontend modes are supported:

- **VS Code Extension** (`sdks/vscode/`): Integrates with VS Code via WebView, commands, and workspace hooks
- **Terminal Client** (`sdks/terminal/`): Standalone TUI/CLI application. Launched with the `ruffel` command

### Architecture Overview

```
Terminal Client (ruffel)             VS Code Extension                OpenMono.Cli Process
┌─────────────────────┐             ┌─────────────────────┐          ┌──────────────────────────────┐
│  TerminalUI.ts      │             │  extension.ts       │          │  Program.cs                  │
│  (REPL + prompts)   │             │  ┌───────────────┐  │          │  ┌────────────────────────┐  │
│  ┌───────────────┐  │  JSON-RPC   │  │ WebViewProvider│  │          │  │ TerminalJsonRpcServer  │  │
│  │ AgentController│──┼────────────┼──┤ (Chat UI)     │  │  JSON-RPC│  │  or VscodeJsonRpcServer │  │
│  │ (spawn+IPC)   │  │ 2.0 over   │  │  └───────┬───────┘  ├──────────┤  │  (stdin/stdout)        │  │
│  └───────┬───────┘  │  stdio      │  │          │          │          │  └────────┬───────────────┘  │
│          │          │             │  │  ┌───────┴───────┐  │          │           │                    │
│  ┌───────┴───────┐  │             │  │  │ AgentSession  │  │          │  ┌────────┴───────────────┐  │
│  │ JsonRpcTransport│ │             │  │  │ (orchestrator)│  │          │  │ OpenCodeBridgeRenderer │  │
│  │ (byte-level  │  │             │  │  └───────┬───────┘  │          │  │ or VscodeRenderer      │  │
│  │  buffer)     │  │             │  │          │          │          │  │ (IRenderer impl)       │  │
│  └───────────────┘  │             │  │  ┌───────┴───────┐  │          │  └────────┬───────────────┘  │
│                     │             │  │  │ JsonRpcTransport│ │          │           │                    │
│                     │             │  │  │ (byte-level   │  │          │  ┌────────┴───────────────┐  │
│                     │             │  │  │  buffer)      │  │          │  │ ConversationLoop       │  │
│                     │             │  │  └───────────────┘  │          │  │  ┌──────────────────┐  │  │
│                     │             │  └─────────────────────┘          │  │  │ ToolDispatcher   │  │  │
│                     │             │                                   │  │  │ (schema validation,│  │  │
│                     │             │                                   │  │  │  permissions,    │  │  │
│                     │             │                                   │  │  │  journaling)     │  │  │
│                     │             │                                   │  │  ├──────────────────┤  │  │
│                     │             │                                   │  │  │ ToolRegistry     │  │  │
│                     │             │                                   │  │  ├──────────────────┤  │  │
│                     │             │                                   │  │  │ SessionManager   │  │  │
│                     │             │                                   │  │  ├──────────────────┤  │  │
│                     │             │                                   │  │  │ PermissionEngine │  │  │
│                     │             │                                   │  │  ├──────────────────┤  │  │
│                     │             │                                   │  │  │ LLM Client       │──┼─┤──► local LLM
│                     │             │                                   │  │  └──────────────────┘  │  │
│                     │             │                                   │  └────────────────────────┘  │
└─────────────────────┘             └─────────────────────┘            └──────────────────────────────┘
```

Both frontends share the same backend JSON-RPC protocol. The terminal client uses `--rpc` flag; the VS Code extension uses `--vscode` flag.

### Communication Protocol

**JSON-RPC 2.0 over stdio** — line-delimited JSON on stdin/stdout. Both sides send one JSON object per line.

**Client → Server methods:**

| Method | Purpose | Maps to |
|--------|---------|--------|
| `session/start` | Initialize a new agent session | `SessionManager.CreateSession()` |
| `session/status` | Get current session state | `SessionState` properties |
| `session/undo` | Revert the last N file modifications | `FileHistory.RevertAsync(count)` |
| `input/send` | Send user text input | `ConversationLoop.RunTurnAsync()` |
| `input/cancel` | Cancel the current running turn | `CancellationTokenSource.Cancel()` on the active turn CTS |
| `context/addFile` | Register a file+selection as context | `ResolveAtReferences()` + message injection |
| `tool/execute` | Directly invoke a tool (Bash, FileEdit) | `ToolDispatcher.ExecuteSingleToolAsync()` |
| `permission/respond` | User responds to permission prompt | `PermissionEngine` user decision callback (TCS-driven) |
| `session/stop` | Gracefully shut down the agent process | `CancellationTokenSource.Cancel()` |

**Server → Client events (namespaced notification methods):**

| Event Method | Purpose |
|-------------|---------|
| `text/delta` | Streaming assistant text delta |
| `text/thinking` | Thinking/reasoning delta |
| `text/thinking_collapsed` | Thinking block collapsed to summary |
| `text/markdown` | Markdown-formatted content |
| `text/diff` | File diff content |
| `text/tool_content` | Tool file content preview |
| `turn/start` | Turn (assistant response cycle) started |
| `turn/end` | Turn completed, optionally with metrics |
| `tool/start` | Tool execution started |
| `tool/result` | Tool execution succeeded (includes `success: true`) |
| `tool/crash` | Tool execution failed with error details |
| `permission/ask` | Agent requests user permission (blocked via TCS) |
| `question/ask` | Agent asks the user a question (blocked via TCS) |
| `session/welcome` | Session welcome message (model + endpoint) |
| `session/error` | Error notification (non-fatal) |
| `session/update` | Session state change (token count, turn count, status) |
| `session/warning` | Warning message |
| `session/info` | Info message |
| `session/debug` | Debug message (only when verbose) |
| `session/todos` | Todo list update |
| `session/clear` | Clear conversation request |
| `session/waiting` | Waiting indicator |

### New Files

**OpenMono.Cli (C#):**

| File | Purpose |
|------|---------|
| `src/OpenMono.Cli/Rendering/VscodeJsonRpcServer.cs` | JSON-RPC 2.0 server for VS Code mode. Dispatches 8 methods: `session/start`, `session/status`, `session/undo`, `input/send`, `context/addFile`, `tool/execute`, `permission/respond`, `session/stop`. |
| `src/OpenMono.Cli/Rendering/VscodeRenderer.cs` | Implements `IRenderer` for VS Code mode. Namespaced JSON-RPC notifications. TCS permission freeze. |
| `src/OpenMono.Cli/Rendering/TerminalJsonRpcServer.cs` | JSON-RPC 2.0 server for terminal (`--rpc`) mode. Same core as VscodeJsonRpcServer but with **stray log isolation**: constructor saves original stdout via `Console.SetOut(Console.Error)`, ensuring rogue `Console.Write` calls route to stderr. Adds `input/cancel` method for turn cancellation. Uses existing `ToolDispatcher` for tool execution (schema validation, permissions, journal recording). **Serialization-level SecretScanner.Redact()** applied to entire JSON string. Thread-safe write serialization via `SemaphoreSlim`. |
| `src/OpenMono.Cli/Rendering/OpenCodeBridgeRenderer.cs` | Implements `IRenderer` for terminal mode. Same notification protocol as VscodeRenderer but no VS Code-specific references. TCS permission freeze. `NotifyToolResult()` for tool result notifications. `SecretScanner.Redact()` applied to user-visible content. |

**Terminal Client Application (`sdks/terminal/`):**

| File | Purpose |
|------|---------|
| `terminal/src/AgentController.ts` | Main RPC controller. Spawns `openmono --rpc --dir <path>` as child process. Reads `MEMORY.md` for context seeding. Routes notifications to TerminalUI. Exposes `sendInput()`, `undoLastAction()`, `respondPermission()`, `cancel()`, `stop()`. |
| `terminal/src/JsonRpcTransport.ts` | Byte-level stream buffer partitioner for stdout (same pattern as VS Code extension). Accumulates Buffer chunks, scans for `\n` delimiters, dispatches JSON-RPC responses and notifications. |
| `terminal/src/TerminalUI.ts` | REPL loop with `readline` interface. Renders streaming text, tool events, permission/[Y/N] dialogs, question prompts. Handles Ctrl+C for turn cancellation. Commands: `/undo`, `/exit`, `/help`. |
| `terminal/src/index.ts` | CLI entry point. Parses `--binary`, `--dir` flags. Instantiates AgentController + TerminalUI. |
| `terminal/bin/ruffel` | Shell wrapper: `node dist/index.js "$@"`. Installed globally as `ruffel` command. |

**opencode VS Code Extension (TypeScript):**

| File | Purpose |
|------|---------|
| `opencode/sdks/vscode/src/JsonRpcTransport.ts` | Spawns the OpenMono process as a child process. **Byte-level stream buffer partitioner**: uses explicit `Buffer.concat()` accumulation on `data` events, scans for `\n` (byte 10) in a while-loop to partition lines — no `readline` dependency. Non-JSON stdout lines are forwarded as stderr diagnostics. Exposes `onStderrLine` callback for directing stderr to a dedicated `vscode.OutputChannel`. |
| `opencode/sdks/vscode/src/AgentSession.ts` | High-level session orchestrator. Wraps the transport, manages typed message history, handles event routing (permission requests via TCS, questions, streaming text, tool updates). Exposes `sendInput()`, `addFileContext()`, **`undoLastAction(count)`**, `respondPermission()`, `respondQuestion()`. Accepts `onStderrLine` callback for backend log routing. |
| `opencode/sdks/vscode/src/WebViewProvider.ts` | VS Code `WebviewViewProvider` that renders the agent chat UI. Displays streaming responses, tool calls, permission prompts (allow/deny/always buttons), question dialogs. **Toolbar** with "↩ Undo" and "📋 Logs" buttons. Handles `undoLastAction` and `showLogs` message types. |

### Modified Files

| File | Change |
|------|--------|
| `src/OpenMono.Cli/Config/AppConfig.cs` | Added `RendererMode` enum (`Terminal`, `Tui`, `Vscode`, `Rpc`) and `Renderer` property |
| `src/OpenMono.Cli/Config/ConfigLoader.cs` | Loads `renderer` from `OPENMONO_RENDERER` env var |
| `src/OpenMono.Cli/Program.cs` | Added `--vscode` and `--rpc` CLI flags. VSCode mode creates VscodeRenderer + ToolDispatcher + VscodeJsonRpcServer. RPC mode creates OpenCodeBridgeRenderer + ToolDispatcher + TerminalJsonRpcServer. Both serve JSON-RPC and return when client disconnects. |
| `opencode/sdks/vscode/src/extension.ts` | Rewritten. Spawns `openmono --vscode` as child process, manages AgentSession, registers WebView provider. **Dedicated `vscode.OutputChannel("Ruffel Mono Agent (backend)")`** for stderr/logs. **Workspace context automation hooks**: `onDidChangeActiveTextEditor` and `onDidSaveTextDocument` auto-send `context/addFile` with 300ms debounce. Registers 7 commands (`ruffelMonoAgent.*`) including `undoAction` alias. **MEMORY.md seeding**: reads `.opencode/MEMORY.md` on session start and passes as `seed_context` in `session/start`. **Permission fallback**: if WebView is not available, falls back to `vscode.window.showInformationMessage` dialogs. |
| `opencode/sdks/vscode/package.json` | Changed name to `ruffel-mono-agent`, added `ruffelMonoAgent.*` commands (openChat, newSession, addFilepathToTerminal, openTerminal, **undoLastAction**, **showLogs**), configuration properties (`binaryPath`, `dataDir`, `localEndpoint`), WebView view contribution + activity bar icon, keybindings for undo (`Cmd+Shift+Z`). |

### Configuration

**VS Code settings** (`settings.json`):
```json
{
  "ruffelMonoAgent.binaryPath": "${workspaceFolder}/opencode/sdks/vscode/bin/openmono",
  "ruffelMonoAgent.localEndpoint": "http://localhost:7474",
  "ruffelMonoAgent.dataDir": "${userHome}/.openmono"
}
```

**OpenMono config** (`~/.openmono/settings.json`):
```json
{
  "llm": {
    "endpoint": "http://localhost:7474",
    "model": "qwen2.5-coder:14b"
  },
  "renderer": "vscode"
}
```

**Environment variables:**
- `OPENMONO_RENDERER=vscode` — select the VSCode renderer
- `OPENMONO_WORKSPACE=<path>` — set working directory
- `OPENMONO_ENDPOINT=<url>` — LLM server endpoint

### Command Mapping

| VS Code Command | Keybinding | JSON-RPC Method | OpenMono Pipeline |
|---|---|---|---|
| `ruffelMonoAgent.openChat` | `Cmd+Esc` | `session/start` | SessionManager → ConversationLoop |
| `ruffelMonoAgent.newSession` | `Cmd+Shift+Esc` | `session/start` (fresh) | SessionManager.CreateSession() |
| `ruffelMonoAgent.addFilepathToContext` | `Cmd+Alt+K` | `context/addFile` + `input/send` | `ResolveAtReferences()` → RunTurnAsync |
| `ruffelMonoAgent.undoLastAction` | `Cmd+Shift+Z` | `session/undo` | `FileHistory.RevertAsync(count)` |
| `ruffelMonoAgent.undoAction` | (alias) | `session/undo` | Delegates to `undoLastAction` |
| `ruffelMonoAgent.showLogs` | — | (none) | Reveals OutputChannel |
| `ruffelMonoAgent.openTerminal` | — | — | Opens VS Code terminal |
| (Permission allow) | — | `permission/respond(allow)` | PermissionEngine TCS resolve |

### Key Advanced Mechanisms

**Atomic Undo (FileHistory.RevertAsync):**
The `session/undo` JSON-RPC method calls `FileHistory.RevertAsync(count)` which reverses the last N file modifications by replaying stored `ContentBefore` snapshots. Deleted files are restored; created files are removed. The WebView's "↩ Undo" button triggers this with `count=1`. Each revert returns a human-readable list of actions taken.

**SecretScanner.Redact() Filtering:**
Redaction is applied at two levels:
1. **Serialization-level (VscodeJsonRpcServer)**: Every `SendNotificationAsync`, `SendResponse`, and `SendErrorResponse` applies `SecretScanner.Redact()` to the entire serialized JSON string before writing to stdout. This is a single choke point that catches all output paths.
2. **Per-field (VscodeRenderer)**: Individual fields carrying user-visible content (permission summaries, error messages, markdown content) are redacted before being passed to `SendNotificationAsync`.

This scrubs 30+ secret patterns (AWS keys, OpenAI tokens, GitHub PATs, SSH keys, etc.) from text that crosses the JSON-RPC boundary, preventing credentials from appearing in the VS Code WebView or being returned to the LLM context.

**TaskCompletionSource Permission Freeze:**
Instead of polling with `Task.Delay`, the permission system uses a `ConcurrentDictionary<string, TaskCompletionSource<PermissionResponse>>`. When the agent requests permission:
1. `AskPermissionAsync` creates a TCS, stores it by `callId`, sends `permission/ask` notification
2. The method awaits `tcs.Task.WaitAsync(ct)` — **zero CPU usage while blocked**
3. When the user clicks Allow/Deny in the WebView, `permission/respond` arrives via stdin
4. `ResolvePermission` looks up the TCS, calls `TrySetResult(result)`, and the blocked thread resumes

The same pattern is used for `question/ask` → `AskUserAsync` → TCS sleep → user answer in WebView → `permission/respond` → TCS resolve.

**Workspace Context Automation:**
The extension hooks `onDidChangeActiveTextEditor` (tab/selection change) and `onDidSaveTextDocument` (file save). After a 300ms debounce, it calls `context/addFile` with the active editor's file path and selection range, keeping the agent's session context aligned with what the user is currently viewing.

**Byte-Level Stream Buffer Partitioning:**
`JsonRpcTransport` avoids the `readline` module entirely. Raw `Buffer` chunks from `data` events are concatenated with `Buffer.concat()`. A `while` loop scans for `\n` byte (`0x0A`), extracts each line, parses JSON, and routes to the request promise or notification handlers. Partial lines persist in the buffer across chunks. This ensures no line boundaries are lost regardless of TCP segmentation or write atomicity.

### Bootstrap Script

`ruffel-mono-agent.sh` at the repository root automates:

1. `dotnet build` — compiles OpenMono.Cli
2. `npm run compile` — builds the VS Code extension (via esbuild)
3. Symlinks the openmono binary into `sdks/vscode/bin/`
4. Writes `.vscode/settings.json` with the binary path
5. Creates `~/.openmono/settings.json` with default renderer mode

```bash
# Full bootstrap
./ruffel-mono-agent.sh

# Then in VS Code: Cmd+Esc to open the agent chat panel

# Or use the terminal client:
cd terminal && npm run compile
node bin/ruffel --binary ../../src/OpenMono.Cli/bin/Debug/net10.0/openmono
```

For global `ruffel` command access:
```bash
npm link   # From terminal/
ruffel     # Now available globally
```

### Session Persistence

OpenMono's `SessionManager` persists sessions to `~/.openmono/sessions/` as JSONL files:

```
~/.openmono/sessions/
├── index.json                              # Session index
├── 2026-05-25_a1b2c3d4e5f6.jsonl          # Session messages
└── 2026-05-25_a1b2c3d4e5f6.checkpoints.json  # Checkpoints
```

Sessions are auto-saved after each turn. The VS Code extension can restore sessions via `session/start { "restoreSessionId": "..." }`.

---

1. **Dual permission systems**: The codebase has both legacy 3-tier permissions and newer capability-based permissions. Tools that implement `RequiredCapabilities()` bypass the legacy system and use capability-based checks instead.

2. **Two rendering modes with unified interface**: Both `TerminalRenderer` and `AnsiTuiRenderer` implement `IRenderer` (= `IOutputSink + IInputReader + ILiveFeedback`). The TUI mode layers raw ANSI escapes over Terminal.Gui for low-level control.

3. **Qwen XML tool calls**: The `OpenAiCompatClient` handles not just standard OpenAI tool_calls but also Qwen-style `<function=name><parameter=key>value</parameter></function>` XML tags, enabling compatibility with Qwen models on both llama.cpp and Ollama.

4. **Checkpointer vs Compactor**: Two distinct mechanisms:
   - **Checkpointer** (65% threshold): Creates structured checkpoint entries with LLM summaries. Preserves full conversation structure via `BuildContextWindow()`. Checkpoints are cumulative (each one covers content since the last checkpoint).
   - **Compactor** (80% threshold): Destructively replaces old messages with a single summary. Evicts large tool outputs. More aggressive.

5. **Async concurrency model**: Read-only + concurrency-safe tools run in parallel. Write tools run sequentially. Early-flight optimization launches concurrent-safe tools during LLM streaming.

6. **Secret scanning happens reactively**: Secrets in *tool output* are redacted before being passed back to the LLM (via `SecretScanner.Redact()`). Secrets in user input are not scanned at the input layer — they would be caught when they appear in tool results. `VscodeJsonRpcServer` applies `SecretScanner.Redact()` at the JSON serialization level (the entire serialized notification string is redacted before writing to stdout), and `VscodeRenderer` additionally redacts individual user-visible fields. This ensures credentials never reach the VS Code WebView, the LLM context, or the JSON-RPC transport layer.

7. **Agent tools share parent permissions**: Sub-agents use the parent's `PermissionEngine`, so user permission decisions apply uniformly across the main agent and sub-agents.

---

> **References**: [ARCHITECTURE.md](ARCHITECTURE.md) | [CONFIG.md](CONFIG.md) | [SETUP.md](SETUP.md) | [MODELS.md](MODELS.md) | [PLAYBOOKS.md](PLAYBOOKS.md) | [ROADMAP.md](../ROADMAP.md)
