# Ruffel Mono Agent — Development Guide

> **Last updated:** 2026-05-25

---

## Table of Contents

- [Environment Setup](#environment-setup)
- [Building](#building)
- [Running in Development](#running-in-development)
- [Debugging](#debugging)
  - [Backend (.NET)](#backend-net)
  - [Terminal Client (TypeScript)](#terminal-client-typescript)
  - [VS Code Extension](#vs-code-extension)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Profiling](#profiling)
- [Adding a New Tool](#adding-a-new-tool)
- [Adding a New Renderer](#adding-a-new-renderer)
- [Modifying the JSON-RPC Protocol](#modifying-the-json-rpc-protocol)
- [Release Process](#release-process)

---

## Environment Setup

### Required Tools

| Tool | Version | Purpose |
|------|---------|---------|
| .NET SDK | 10.0.x | Compile and run the backend |
| Node.js | 20.x LTS | Compile and run the terminal client |
| npm | 10.x | Package management |
| Git | 2.40+ | Version control |
| llama-server | latest | Local LLM inference |

### Optional Tools

| Tool | Purpose |
|------|---------|
| VS Code | Development IDE |
| C# Dev Kit | C# language support in VS Code |
| dotnet-counters | .NET runtime metrics |
| dotnet-trace | .NET performance tracing |
| Grafana + Prometheus | Metrics visualization (production) |

---

## Building

### Full Build

```bash
# Backend
dotnet build src/OpenMono.Cli

# Terminal client
cd terminal
npm install
npm run compile

# VS Code extension
cd opencode/sdks/vscode
npm install
npm run compile
```

### Incremental Build

During development, use incremental builds for faster iteration:

```bash
# Backend (fastest — only changed files)
dotnet build src/OpenMono.Cli

# Terminal client (with watch mode)
cd terminal
node esbuild.js --watch
```

### Production Build

```bash
# Backend (Native AOT — optimize for startup time and binary size)
dotnet publish src/OpenMono.Cli -c Release -r linux-x64 --self-contained

# Terminal client (minified single file)
cd terminal
node esbuild.js
```

---

## Running in Development

### Quickest Path

```bash
# Terminal 1: Start llama-server (or use Docker)
docker compose up -d llama-server

# Terminal 2: Build and run the terminal client
dotnet build src/OpenMono.Cli && \
  cd terminal && npm run compile && \
  node bin/ruffel --binary ../../src/OpenMono.Cli/bin/Debug/net10.0/openmono
```

### Without llama-server

If you don't have a local LLM running, you can:

1. Set `OPENMONO_ENDPOINT` to a cloud provider endpoint
2. Or use a mock endpoint (the agent will show connection errors but tool execution still works)

---

## Debugging

### Backend (.NET)

#### 1. Console Logging

Run with verbose mode:

```bash
ruffel --verbose   # Passes -v to the backend
# or directly:
openmono --rpc -v
```

Verbose mode enables `WriteDebug()` calls, showing:
- LLM request/response bodies
- Tool execution timings
- Permission decisions
- Cache hits/misses

#### 2. File Logging

All logs are written to `~/.openmono/logs/`:

```bash
tail -f ~/.openmono/logs/*.log
```

Log format:
```
[2026-05-25 10:30:00.123] [INFO] Session starting — model=qwen2.5-coder:14b endpoint=http://localhost:7474
[2026-05-25 10:30:01.456] [DEBUG] Tool executing: FileRead
[2026-05-25 10:30:02.789] [WARN] Tool error: Bash — exit code 127
```

#### 3. Stderr Diagnostics

In `--rpc` mode, all `Console.Write` calls from libraries route to stderr:

```bash
ruffel 2>/tmp/ruffel-stderr.log

# In another terminal:
tail -f /tmp/ruffel-stderr.log
```

#### 4. Attaching a Debugger

```bash
# With VS Code: Configure launch.json for .NET
# Or use the dotnet CLI debugger:
DOTNET_ENVIRONMENT=Development dotnet run --project src/OpenMono.Cli -- --rpc
```

For VS Code `launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": ".NET Backend (RPC mode)",
      "type": "coreclr",
      "request": "launch",
      "projectPath": "${workspaceFolder}/src/OpenMono.Cli/OpenMono.Cli.csproj",
      "args": ["--rpc"],
      "cwd": "${workspaceFolder}",
      "console": "internalConsole",
      "stopAtEntry": false
    }
  ]
}
```

#### 5. ROSLYN Analysis

During tool changes, use RoslynTool for C# code analysis:

```
> Before editing a .cs file, call Roslyn capture-baseline target=<filepath>
> After finishing, call Roslyn diagnostics target=<filepath>
```

### Terminal Client (TypeScript)

#### 1. Console Logging

```bash
# Run with Node.js inspector
node --inspect-brk bin/ruffel

# Or add Node.js debugging flags
NODE_OPTIONS="--inspect" ruffel
```

#### 2. JSON-RPC Tracing

To see the raw JSON-RPC traffic:

```bash
# Pipe through a tracing script
ruffel 2>/tmp/ruffel-stderr.log

# Or modify AgentController.ts to log all messages:
# this.transport.onNotification((n) => console.error("[RPC]", JSON.stringify(n)))
```

### VS Code Extension

1. Open `opencode/sdks/vscode/` in VS Code
2. Press F5 → "Extension Development Host" opens
3. Set breakpoints in TypeScript code
4. Check the debug console for logs

---

## Testing

### Backend Tests

```bash
# Run all tests
dotnet test src/OpenMono.Tests

# Run specific test class
dotnet test src/OpenMono.Tests --filter "ToolDispatcherTests"

# Run with detailed output
dotnet test src/OpenMono.Tests -v n --logger "console;verbosity=detailed"

# Run with code coverage
dotnet test src/OpenMono.Tests /p:CollectCoverage=true /p:CoverletOutput=./coverage/
```

### Test File Structure

```
src/OpenMono.Tests/
├── Tools/
│   └── ToolDispatcherTests.cs
├── Permissions/
│   └── PermissionEngineTests.cs
├── Session/
│   └── ConversationLoopTests.cs
├── History/
│   └── FileHistoryTests.cs
└── Utils/
    └── SecretScannerTests.cs
```

### Test Patterns

```csharp
// Unit test example
[Fact]
public async Task SecretScanner_Redact_RemovesAwsKeys()
{
    var input = "AWS key: AKIAIOSFODNN7EXAMPLE";

    var result = SecretScanner.Redact(input);

    Assert.DoesNotContain("AKIAIOSFODNN7EXAMPLE", result);
    Assert.Contains("[REDACTED", result);
}

// Integration test example
[Fact]
public async Task ToolDispatcher_ExecuteSingleToolAsync_ReadOnlyTool_CachesResult()
{
    var dispatcher = CreateDispatcherWithFile("test.txt", "hello");
    var call = new ToolCall { Id = "1", Name = "FileRead", Arguments = """{"file_path": "test.txt"}""" };
    var tool = new FileReadTool();
    var context = CreateContext();

    var first = await dispatcher.ExecuteSingleToolAsync(call, tool, context, CancellationToken.None);
    var second = await dispatcher.ExecuteSingleToolAsync(call, tool, context, CancellationToken.None);

    Assert.Contains("[cached]", second.Content);
}
```

---

## Code Quality

### Linting

```bash
# Backend — .NET analyzers run during build
dotnet build src/OpenMono.Cli

# Terminal client
cd terminal
npx tsc --noEmit

# VS Code extension
cd opencode/sdks/vscode
npx eslint src
```

### Static Analysis

```bash
# .NET
dotnet build src/OpenMono.Cli -warnaserror

# TypeScript
npx tsc --noEmit --strict
```

### Code Review Checklist

- [ ] No `Console.WriteLine()` in library code (use the logging system)
- [ ] Cancellation tokens forwarded to all async operations
- [ ] No `.Result` or `.Wait()` — always `await`
- [ ] All new public APIs documented in XML comments
- [ ] Tests cover success and failure paths
- [ ] Documentation updated (ARCHITECTURE.md, API.md)
- [ ] Builds pass (`dotnet build` + `npx tsc --noEmit`)

---

## Profiling

### Backend CPU/Memory

```bash
# Install tools
dotnet tool install -g dotnet-counters
dotnet tool install -g dotnet-trace

# Run with counters
dotnet-counters monitor --process-id $(pgrep -f "openmono --rpc") System.Runtime
```

### LLM Latency

```bash
# Measure time-to-first-token
time curl -X POST http://localhost:7474/v1/chat/completions \
  -d '{"model":"qwen2.5-coder:14b","messages":[{"role":"user","content":"hello"}],"stream":true}' \
  -H 'Content-Type: application/json'
```

### Backend Request Latency

Add timing logs to `Program.cs` in the VSCode/RPC mode handler:

```csharp
var sw = Stopwatch.StartNew();
await rpcServer!.ServeAsync(CancellationToken.None);
sw.Stop();
Log.Info($"Session served for {sw.Elapsed.TotalSeconds:F1}s");
```

---

## Adding a New Tool

1. **Create the tool class** in `src/OpenMono.Cli/Tools/`:

```csharp
using System.Text.Json;
using OpenMono.Permissions;

namespace OpenMono.Tools;

public sealed class MyNewTool : ToolBase
{
    public override string Name => "MyNewTool";
    public override string Description => "Does something useful";
    public override bool IsReadOnly => true;
    public override PermissionLevel DefaultPermission => PermissionLevel.AutoAllow;

    protected override SchemaBuilder DefineSchema()
    {
        return new SchemaBuilder()
            .AddString("param1", "A parameter")
            .Require("param1");
    }

    protected override async Task<ToolResult> ExecuteCoreAsync(
        JsonElement input, ToolContext context, CancellationToken ct)
    {
        var param1 = input.GetProperty("param1").GetString()!;
        return ToolResult.Success($"Executed with {param1}");
    }
}
```

2. **Register the tool** in `Program.cs`:

```csharp
tools.Register(new MyNewTool());
```

3. **Add tests** in `src/OpenMono.Tests/Tools/`.
4. **Update documentation** in `ARCHITECTURE.md` tool list.

---

## Adding a New Renderer

1. **Implement `IRenderer`** in `src/OpenMono.Cli/Rendering/`:

```csharp
public sealed class MyRenderer : IRenderer
{
    // IOutputSink methods
    // IInputReader methods
    // ILiveFeedback methods
}
```

2. **Add `RendererMode`** in `AppConfig.cs`.
3. **Wire in `Program.cs`**:

```csharp
if (config.Renderer == RendererMode.MyMode)
{
    myRenderer = new MyRenderer();
    renderer = myRenderer;
    // or: myRenderer + JSON-RPC server
}
```

4. **Update docs**: ARCHITECTURE.md, COMPREHENSIVE_REFERENCE.md.

---

## Modifying the JSON-RPC Protocol

### Adding a New Method

1. **Add handler** in `TerminalJsonRpcServer.cs` (and `VscodeJsonRpcServer.cs` for VS Code support):

```csharp
private async Task<JsonElement> HandleMyMethod(JsonElement @params, CancellationToken ct)
{
    // Parse params, call backend service, return result
}

// Add to the switch statement:
"my/method" => await HandleMyMethod(@params, ct),
```

2. **Add TypeScript client method** in `AgentController.ts` or `AgentSession.ts`:

```typescript
async myMethod(param1: string): Promise<Result> {
  return this.transport.request<Result>("my/method", { param1 })
}
```

3. **Update API docs** in `docs/API.md`.

### Adding a New Notification

1. **Send from renderer** in `OpenCodeBridgeRenderer.cs` or `VscodeRenderer.cs`:

```csharp
_server.SendNotificationAsync("my/event", new { data = value }, CancellationToken.None);
```

2. **Handle in frontend**:

In `TerminalUI.ts`:
```typescript
case "my/event":
  // Render the event
  break
```

In `AgentSession.ts`:
```typescript
case "my/event": {
  // Handle and emit
  break
}
```

3. **Update API docs**.

---

## Release Process

### Versioning

This project follows [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR**: Breaking changes to the JSON-RPC protocol or file formats
- **MINOR**: New features, new tools, new notifications (backward compatible)
- **PATCH**: Bug fixes, performance improvements (backward compatible)

### Release Steps

1. **Create release branch** from `dev`:

```bash
git checkout dev
git checkout -b release/v0.2.0
```

2. **Update version**:

```bash
# CHANGELOG.md — move "Unreleased" to new version
# package.json (terminal) — update version
# package.json (vscode) — update version
# Program.cs — update --version output
```

3. **Final test**:

```bash
dotnet build src/OpenMono.Cli
dotnet test src/OpenMono.Tests
cd terminal && npx tsc --noEmit && cd ../..
cd opencode/sdks/vscode && npx tsc --noEmit && cd ../..
```

4. **Tag and merge**:

```bash
git tag -a v0.2.0 -m "v0.2.0: Feature summary"
git push origin v0.2.0
# Open PR against main, merge, then:
git checkout main && git pull
git checkout dev && git merge main
```

5. **Create GitHub Release**:
- Title: `v0.2.0`
- Description: Summary of changes
- Attach: built binaries (dotnet publish output)
- Set as latest
