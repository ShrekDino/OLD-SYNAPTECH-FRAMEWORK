# Ruffel Mono Agent — JSON-RPC 2.0 Protocol Specification

> **Version:** 1.0  
> **Transport:** Line-delimited JSON on stdin/stdout  
> **Specification:** [JSON-RPC 2.0](https://www.jsonrpc.org/specification)  

---

## 1. Transport Layer

### 1.1 Stdio Protocol

Both processes communicate over the standard I/O streams of a child process:

```
Frontend (TypeScript)                  Backend (C# .NET 10)
       │                                      │
       │——— stdin: JSON-RPC request ————————→│
       │                                      │
       │←—— stdout: JSON-RPC response ———————│
       │                                      │
       │←—— stdout: JSON-RPC notification ——→│ (no id field)
       │                                      │
       │←—— stderr: diagnostic logs (raw) ———│ (non-JSON, human-readable)
       │                                      │
```

Every JSON object is exactly one line terminated by `\n` (byte 0x0A). There is no leading or trailing whitespace on any line.

### 1.2 Stderr Isolation (Terminal Mode)

In `--rpc` mode, the backend calls `Console.SetOut(Console.Error)` at startup. This redirects ALL `Console.Write`/`Console.WriteLine` calls to stderr. The JSON-RPC server writes to stdout via a cached reference to the original pipe. This guarantees:

- **Stderr is pure diagnostics**: Logs, debug output, errors, stack traces
- **Stdout is pure JSON**: No stray text can corrupt the protocol

### 1.3 Byte-Level Buffering

Both frontends use byte-level stream partitioning (not `readline`):

```typescript
// Pseudocode — actual implementation in JsonRpcTransport.ts
buffer = Buffer.concat([buffer, chunk])
while (buffer.indexOf(0x0A) !== -1) {
  line = buffer.subarray(0, nl)
  buffer = buffer.subarray(nl + 1)
  parseAndDispatch(line)
}
```

---

## 2. JSON-RPC 2.0 Conventions

### 2.1 Request Format

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "session/start",
  "params": {
    "working_directory": "/home/user/project"
  }
}
```

- `id`: Integer (auto-incrementing on the client). Must echo in response.
- `method`: Namespaced string using `/` as separator
- `params`: Object (may be empty)

### 2.2 Response Format (Success)

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "session_id": "a1b2c3d4e5f6",
    "model": "qwen2.5-coder:14b",
    "status": "ready"
  }
}
```

### 2.3 Response Format (Error)

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32601,
    "message": "Method not found: session/unknown"
  }
}
```

Standard JSON-RPC error codes:

| Code | Meaning |
|------|---------|
| -32600 | Invalid Request (malformed JSON) |
| -32601 | Method not found |
| -32602 | Invalid params |
| -32603 | Internal error (handler exception) |

### 2.4 Notification Format

Notifications have no `id` field. The backend does not expect a response.

```json
{
  "jsonrpc": "2.0",
  "method": "text/delta",
  "params": {
    "delta": "Hello, world!"
  }
}
```

---

## 3. Client → Server Methods

### 3.1 `session/start`

Initialize a new agent session.

**Params:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `working_directory` | `string` | No | Working directory (default: config value or CWD) |
| `seed_context` | `string` | No | Initial context text (e.g., MEMORY.md content) |
| `restore_session_id` | `string` | No | Resume a previous session by ID |

**Result:**

```json
{
  "session_id": "a1b2c3d4e5f6",
  "model": "qwen2.5-coder:14b",
  "status": "ready"
}
```

**Backend Handler:** `SessionManager.CreateSession()` — resets `SessionState`, adds seed context as system message.

### 3.2 `session/status`

Get current session state.

**Params:** None

**Result:**

```json
{
  "session_id": "a1b2c3d4e5f6",
  "turn_count": 5,
  "message_count": 23,
  "total_tokens_used": 45678,
  "status": "idle"
}
```

### 3.3 `session/undo`

Revert the last N file modifications.

**Params:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `count` | `int` | No | Number of actions to undo (default: 1) |

**Result:**

```json
{
  "success": true,
  "count": 1,
  "reverted": ["src/Program.cs", "src/Config.cs"]
}
```

**Backend:** `FileHistory.RevertAsync(count)` — reverses snapshots in LIFO order.

### 3.4 `session/stop`

Gracefully shut down the agent process.

**Params:** None

**Result:**

```json
{
  "stopped": true
}
```

**Backend:** `CancellationTokenSource.Cancel()` — ends the server loop, cleanup follows.

### 3.5 `input/send`

Send user text input to the agent. This is the primary interaction method.

**Params:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | `string` | Yes | User input text |

**Result:**

```json
{
  "turn_count": 6,
  "total_tokens_used": 51234
}
```

**Backend:** `ConversationLoop.RunTurnAsync(text)` — the main agent loop. This blocks until the turn completes (including all tool call cycles).

### 3.6 `input/cancel`

Cancel the currently running turn without killing the process.

**Params:** None

**Result:**

```json
{
  "cancelled": true
}
```

**Backend:** `CancellationTokenSource.Cancel()` on the turn's CTS. The LLM stream is interrupted, tool operations are cancelled, and `input/send` returns early.

### 3.7 `context/addFile`

Register a file reference as conversational context.

**Params:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `path` | `string` | Yes | Absolute file path |
| `relative_path` | `string` | No | Relative display path |
| `selection` | `object` | No | Text selection range |
| `selection.start_line` | `int` | No | Start line (1-indexed) |
| `selection.end_line` | `int` | No | End line (1-indexed) |

**Result:**

```json
{
  "accepted": true,
  "file_ref": "@src/Program.cs#L10-30"
}
```

**Backend:** Injects an `[Context: file reference added — @path#Lstart-end]` message into the session.

### 3.8 `tool/execute`

Directly execute a tool by name. Used for interactive tool testing.

**Params:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tool_name` | `string` | Yes | Tool name (e.g., "Bash", "FileRead") |
| `arguments` | `object` | Yes | Tool-specific arguments |
| `call_id` | `string` | No | Correlation ID (auto-generated if omitted) |

**Result:**

```json
{
  "success": true,
  "content": "File contents here...",
  "error": null
}
```

**Backend:** `ToolDispatcher.ExecuteSingleToolAsync()` — full execution pipeline including schema validation, permission check, execution, and journaling.

### 3.9 `permission/respond`

User response to a pending permission or question request.

**Params:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `request_id` | `string` | Yes | The `call_id` from the `permission/ask` or `question/ask` notification |
| `response` | `string` | Yes | one of: `"allow"`, `"deny"`, `"allow_all"`, `"deny_all"`, or free-text for questions |

**Result:**

```json
{
  "accepted": true
}
```

**Backend:** `Renderer.ResolvePermission(requestId, response)` → resolves the TCS → blocked execution resumes.

---

## 4. Server → Client Notifications

### 4.1 `text/delta`

Streaming assistant text. Multiple deltas form a complete response.

```json
{
  "jsonrpc": "2.0",
  "method": "text/delta",
  "params": {
    "delta": "The quick brown fox jumps..."
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `delta` | `string` | Incomplete text chunk |

### 4.2 `text/thinking`

Streaming reasoning/thinking tokens from the model.

```json
{
  "jsonrpc": "2.0",
  "method": "text/thinking",
  "params": {
    "delta": "Let me think about this step by step..."
  }
}
```

### 4.3 `text/thinking_collapsed`

A thinking block was collapsed to a summary.

```json
{
  "jsonrpc": "2.0",
  "method": "text/thinking_collapsed",
  "params": {
    "char_count": 1234
  }
}
```

### 4.4 `text/markdown`

Formatted markdown content (not streamed).

```json
{
  "jsonrpc": "2.0",
  "method": "text/markdown",
  "params": {
    "content": "# Hello\n\nThis is **markdown**."
  }
}
```

### 4.5 `text/diff`

File diff output.

```json
{
  "jsonrpc": "2.0",
  "method": "text/diff",
  "params": {
    "content": "--- a/src/Program.cs\n+++ b/src/Program.cs\n@@ -1,3 +1,4 @@\n+// new line\n using System;"
  }
}
```

### 4.6 `text/tool_content`

File content preview from tool execution.

```json
{
  "jsonrpc": "2.0",
  "method": "text/tool_content",
  "params": {
    "tool_name": "FileRead",
    "file_path": "/src/main.cs",
    "content": "using System;..."
  }
}
```

### 4.7 `turn/start`

A new assistant response turn has begun. Resets any accumulated streaming state.

```json
{
  "jsonrpc": "2.0",
  "method": "turn/start",
  "params": null
}
```

### 4.8 `turn/end`

The current turn has completed.

```json
{
  "jsonrpc": "2.0",
  "method": "turn/end",
  "params": {
    "metrics": {
      "promptTokens": 1234,
      "completionTokens": 567
    }
  }
}
```

### 4.9 `tool/start`

A tool execution has begun.

```json
{
  "jsonrpc": "2.0",
  "method": "tool/start",
  "params": {
    "tool_name": "Bash",
    "arguments": "echo hello",
    "call_id": "tool_a1b2c3d4"
  }
}
```

### 4.10 `tool/result`

A tool execution completed successfully.

```json
{
  "jsonrpc": "2.0",
  "method": "tool/result",
  "params": {
    "tool_name": "Bash",
    "success": true,
    "call_id": "tool_a1b2c3d4"
  }
}
```

### 4.11 `tool/crash`

A tool execution failed with an error.

```json
{
  "jsonrpc": "2.0",
  "method": "tool/crash",
  "params": {
    "tool_name": "FileWrite",
    "error": "Access to path denied",
    "call_id": "tool_e5f6g7h8"
  }
}
```

### 4.12 `permission/ask`

The agent requests user permission for an operation. The frontend must display a prompt and respond via `permission/respond`.

**Important:** This notification blocks the agent execution. The backend is awaiting a `TaskCompletionSource` — no other work will happen until the user responds. The frontend should respond as soon as possible.

```json
{
  "jsonrpc": "2.0",
  "method": "permission/ask",
  "params": {
    "call_id": "perm_a1b2c3d4",
    "tool_name": "Bash",
    "summary": "$ rm -rf /"
  }
}
```

The response format for `permission/respond`:
- `"allow"` — Allow this one time
- `"deny"` — Deny this one time
- `"allow_all"` — Always allow for this session
- `"deny_all"` — Always deny for this session

### 4.13 `question/ask`

The agent asks the user a question. Same blocking semantics as `permission/ask`.

```json
{
  "jsonrpc": "2.0",
  "method": "question/ask",
  "params": {
    "call_id": "q_a1b2c3d4",
    "question": "What database should I use?"
  }
}
```

The response for `permission/respond` should be the user's free-text answer.

### 4.14 `session/welcome`

Sent at session start with model and endpoint info.

```json
{
  "jsonrpc": "2.0",
  "method": "session/welcome",
  "params": {
    "model": "qwen2.5-coder:14b",
    "endpoint": "http://localhost:7474"
  }
}
```

### 4.15 `session/update`

Session state change notification.

```json
{
  "jsonrpc": "2.0",
  "method": "session/update",
  "params": {
    "turn_count": 6,
    "total_tokens_used": 51234,
    "status": "idle"
  }
}
```

### 4.16 `session/error`

Error notification (non-fatal — session continues).

```json
{
  "jsonrpc": "2.0",
  "method": "session/error",
  "params": {
    "message": "LLM connection failed: Connection refused",
    "fatal": false
  }
}
```

### 4.17 `session/warning`, `session/info`, `session/debug`

Status messages of varying severity.

```json
{
  "jsonrpc": "2.0",
  "method": "session/warning",
  "params": {
    "content": "Down to 15% context window remaining"
  }
}
```

### 4.18 `session/clear`

Clear the conversation display.

```json
{
  "jsonrpc": "2.0",
  "method": "session/clear",
  "params": null
}
```

### 4.19 `session/todos`

Todo list update.

```json
{
  "jsonrpc": "2.0",
  "method": "session/todos",
  "params": {
    "todos": [
      { "description": "Fix bug #123", "completed": false }
    ]
  }
}
```

### 4.20 `session/waiting`

Agent is waiting (e.g., warming up, loading model).

```json
{
  "jsonrpc": "2.0",
  "method": "session/waiting",
  "params": null
}
```

---

## 5. Error Handling

### 5.1 Backend Errors

All backend errors are returned as JSON-RPC error responses:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32603,
    "message": "Tool 'NonExistentTool' not found in registry"
  }
}
```

### 5.2 Protocol Errors

| Condition | Behavior |
|-----------|----------|
| Malformed JSON | Silently dropped (no response) |
| No `method` field | Silently dropped |
| Unknown method | Error response with code `-32601` |
| Handler throws exception | Error response with code `-32603` |
| Non-JSON on stdout | Forwarded to stderr diagnostics |
| Invalid request params | Method-specific validation error |

### 5.3 Frontend Error Recovery

```typescript
// Transport-level timeout (30s default per request)
try {
  const result = await transport.request("input/send", { text }, 30000)
} catch (err) {
  if (err.message.includes("timed out")) {
    // The request may still be processing — check session status
  }
  if (err.message.includes("Process exited")) {
    // The backend crashed — restart
    await controller.stop()
    await controller.start()
  }
}
```

---

## 6. Protocol Versioning

The protocol does not use a version field. Changes are additive only:

- **New methods**: Added without breaking existing clients
- **New notification fields**: Added without breaking existing clients
- **Changed behavior**: New CLI flag (`--rpc`, `--vscode`) selects different handler sets
- **Deprecation**: Old methods are supported for at least one minor version

---

## 7. Examples

### Minimal Session

```
→ {"jsonrpc":"2.0","id":1,"method":"session/start","params":{"working_directory":"/home/user/project"}}
← {"jsonrpc":"2.0","id":1,"result":{"session_id":"a1b2c3d4e5f6","model":"qwen2.5-coder:14b","status":"ready"}}
← {"jsonrpc":"2.0","method":"session/welcome","params":{"model":"qwen2.5-coder:14b","endpoint":"http://localhost:7474"}}

→ {"jsonrpc":"2.0","id":2,"method":"input/send","params":{"text":"Hello, what is in this directory?"}}
← {"jsonrpc":"2.0","method":"turn/start","params":null}
← {"jsonrpc":"2.0","method":"text/delta","params":{"delta":"Let me check the directory contents..."}}
← {"jsonrpc":"2.0","method":"tool/start","params":{"tool_name":"ListDirectory","arguments":"."}}
← {"jsonrpc":"2.0","method":"tool/result","params":{"tool_name":"ListDirectory","success":true}}
← {"jsonrpc":"2.0","method":"text/delta","params":{"delta":"\n\nYou have a C# project with these files:\n- Program.cs\n- Config.cs"}}
← {"jsonrpc":"2.0","method":"turn/end","params":null}
← {"jsonrpc":"2.0","id":2,"result":{"turn_count":1,"total_tokens_used":523}}
```

### Permission Flow

```
→ {"jsonrpc":"2.0","method":"tool/start","params":{"tool_name":"Bash","arguments":"ls -la","call_id":"tool_01"}}
← {"jsonrpc":"2.0","method":"permission/ask","params":{"call_id":"perm_01","tool_name":"Bash","summary":"$ ls -la"}}
   [User presses 'a' for allow]
→ {"jsonrpc":"2.0","id":5,"method":"permission/respond","params":{"request_id":"perm_01","response":"allow"}}
← {"jsonrpc":"2.0","id":5,"result":{"accepted":true}}
← {"jsonrpc":"2.0","method":"tool/result","params":{"tool_name":"Bash","success":true,"call_id":"tool_01"}}
```

### Cancellation

```
→ {"jsonrpc":"2.0","id":3,"method":"input/send","params":{"text":"Write a complex algorithm..."}}
← [streaming text/tool events...]
   [User presses Ctrl+C]
→ {"jsonrpc":"2.0","id":4,"method":"input/cancel","params":{}}
← {"jsonrpc":"2.0","id":4,"result":{"cancelled":true}}
← {"jsonrpc":"2.0","id":3,"result":{"turn_count":1,"total_tokens_used":1234}}
```
