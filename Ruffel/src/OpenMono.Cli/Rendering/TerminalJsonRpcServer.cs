using System.Text.Json;
using OpenMono.Config;
using OpenMono.History;
using OpenMono.Session;
using OpenMono.Tools;
using OpenMono.Utils;

namespace OpenMono.Rendering;

public sealed class TerminalJsonRpcServer : IDisposable
{
    private readonly TextReader _stdin;
    private readonly TextWriter _stdout;
    private readonly SemaphoreSlim _writeLock = new(1, 1);
    private readonly CancellationTokenSource _shutdownCts = new();
    private CancellationTokenSource? _currentTurnCts;
    private Task? _serverTask;

    private readonly AppConfig _config;
    private readonly SessionManager _sessionManager;
    private SessionState _session;
    private readonly ToolDispatcher _toolDispatcher;
    private ConversationLoop? _loop;
    private readonly OpenCodeBridgeRenderer _renderer;

    private static readonly JsonSerializerOptions JsonOpts = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
        WriteIndented = false,
    };

    public TerminalJsonRpcServer(
        AppConfig config,
        SessionManager sessionManager,
        SessionState session,
        ToolDispatcher toolDispatcher,
        OpenCodeBridgeRenderer renderer)
    {
        var realStdout = Console.Out;
        Console.SetOut(Console.Error);

        _stdout = realStdout;
        _stdin = Console.In;
        _config = config;
        _sessionManager = sessionManager;
        _session = session;
        _toolDispatcher = toolDispatcher;
        _renderer = renderer;
    }

    public void SetLoop(ConversationLoop loop) => _loop = loop;

    public async Task ServeAsync(CancellationToken ct)
    {
        using var linkedCts = CancellationTokenSource.CreateLinkedTokenSource(ct, _shutdownCts.Token);
        var token = linkedCts.Token;

        _serverTask = Task.Run(async () =>
        {
            while (!token.IsCancellationRequested)
            {
                var line = await _stdin.ReadLineAsync(token);
                if (line is null) break;

                ProcessLine(line, token).Forget();
            }
        }, token);

        try { await _serverTask; }
        catch (OperationCanceledException) { }
    }

    private async Task ProcessLine(string line, CancellationToken ct)
    {
        JsonDocument doc;
        try
        {
            doc = JsonDocument.Parse(line);
        }
        catch (JsonException)
        {
            return;
        }

        var root = doc.RootElement;
        if (!root.TryGetProperty("method", out var methodEl)) return;

        var method = methodEl.GetString() ?? "";
        var hasId = root.TryGetProperty("id", out var idEl);
        var id = hasId ? idEl.GetRawText() : null;

        try
        {
            var @params = root.TryGetProperty("params", out var p) ? p : default;

            JsonElement? result = method switch
            {
                "session/start" => await HandleSessionStart(@params, ct),
                "session/status" => HandleSessionStatus(),
                "session/undo" => await HandleSessionUndo(@params, ct),
                "input/send" => await HandleInputSend(@params, ct),
                "input/cancel" => HandleInputCancel(),
                "context/addFile" => HandleContextAddFile(@params),
                "tool/execute" => await HandleToolExecute(@params, ct),
                "permission/respond" => HandlePermissionRespond(@params),
                "session/stop" => HandleSessionStop(),
                _ => null,
            };

            if (hasId && id is not null)
            {
                if (result is not null)
                    await SendResponse(id, result.Value, ct);
                else
                    await SendErrorResponse(id, -32601, $"Method not found: {method}", ct);
            }
        }
        catch (Exception ex)
        {
            if (hasId && id is not null)
                await SendErrorResponse(id, -32603, ex.Message, ct);
        }
    }

    private async Task<JsonElement> HandleSessionStart(JsonElement @params, CancellationToken ct)
    {
        var workDir = @params.TryGetProperty("working_directory", out var wd)
            ? wd.GetString() ?? _config.WorkingDirectory
            : _config.WorkingDirectory;

        _config.WorkingDirectory = workDir;
        _session = SessionManager.CreateSession();

        var seedContext = "";
        if (@params.TryGetProperty("seed_context", out var seed) && seed.ValueKind == JsonValueKind.String)
        {
            seedContext = seed.GetString() ?? "";
        }

        if (!string.IsNullOrEmpty(seedContext))
        {
            _session.AddMessage(new Message
            {
                Role = MessageRole.System,
                Content = seedContext,
            });
        }

        return JsonDocument.Parse(JsonSerializer.Serialize(new
        {
            session_id = _session.Id,
            model = _config.Llm.Model,
            status = "ready",
        }, JsonOpts)).RootElement.Clone();
    }

    private JsonElement HandleSessionStatus()
    {
        return JsonDocument.Parse(JsonSerializer.Serialize(new
        {
            session_id = _session.Id,
            turn_count = _session.TurnCount,
            message_count = _session.Messages.Count,
            total_tokens_used = _session.TotalTokensUsed,
            status = _loop is not null ? "running" : "idle",
        }, JsonOpts)).RootElement.Clone();
    }

    private async Task<JsonElement> HandleInputSend(JsonElement @params, CancellationToken ct)
    {
        var text = @params.GetProperty("text").GetString() ?? "";
        if (_loop is null)
        {
            return JsonDocument.Parse(JsonSerializer.Serialize(new
            {
                error = "No active conversation loop",
            }, JsonOpts)).RootElement.Clone();
        }

        using var turnCts = CancellationTokenSource.CreateLinkedTokenSource(ct);
        _currentTurnCts = turnCts;

        try
        {
            await _loop.RunTurnAsync(text, turnCts.Token);
        }
        finally
        {
            _currentTurnCts = null;
        }

        return JsonDocument.Parse(JsonSerializer.Serialize(new
        {
            turn_count = _session.TurnCount,
            total_tokens_used = _session.TotalTokensUsed,
        }, JsonOpts)).RootElement.Clone();
    }

    private JsonElement HandleInputCancel()
    {
        _currentTurnCts?.Cancel();
        return JsonDocument.Parse(JsonSerializer.Serialize(new
        {
            cancelled = true,
        }, JsonOpts)).RootElement.Clone();
    }

    private JsonElement HandleContextAddFile(JsonElement @params)
    {
        var path = @params.GetProperty("path").GetString() ?? "";
        var relPath = @params.TryGetProperty("relative_path", out var rp) ? rp.GetString() : path;
        var fragment = "";

        if (@params.TryGetProperty("selection", out var sel))
        {
            var start = sel.TryGetProperty("start_line", out var sl) ? sl.GetInt32() : 0;
            var end = sel.TryGetProperty("end_line", out var el) ? el.GetInt32() : 0;
            fragment = start == end ? $"#L{start}" : $"#L{start}-{end}";
        }

        var fileRef = $"@{relPath}{fragment}";
        _session.AddMessage(new Message
        {
            Role = MessageRole.User,
            Content = $"[Context: file reference added — {fileRef}]\nFull path: {path}",
        });

        return JsonDocument.Parse(JsonSerializer.Serialize(new
        {
            accepted = true,
            file_ref = fileRef,
        }, JsonOpts)).RootElement.Clone();
    }

    private async Task<JsonElement> HandleToolExecute(JsonElement @params, CancellationToken ct)
    {
        var callId = @params.TryGetProperty("call_id", out var ci) ? ci.GetString() : Guid.NewGuid().ToString("N")[..12];
        var toolName = @params.GetProperty("tool_name").GetString() ?? "";
        var arguments = @params.TryGetProperty("arguments", out var args) ? args.GetRawText() : "{}";

        var tool = _toolDispatcher.ResolveTool(toolName);
        if (tool is null)
        {
            return JsonDocument.Parse(JsonSerializer.Serialize(new
            {
                success = false,
                error = $"Unknown tool: {toolName}",
            }, JsonOpts)).RootElement.Clone();
        }

        var call = new ToolCall { Id = callId!, Name = toolName, Arguments = arguments };
        var context = _toolDispatcher.BuildToolContext();
        ToolResult result;

        try
        {
            result = await _toolDispatcher.ExecuteSingleToolAsync(call, tool, context, ct);
        }
        catch (OperationCanceledException)
        {
            return JsonDocument.Parse(JsonSerializer.Serialize(new
            {
                success = false,
                error = "Tool execution cancelled",
            }, JsonOpts)).RootElement.Clone();
        }
        catch (Exception ex)
        {
            return JsonDocument.Parse(JsonSerializer.Serialize(new
            {
                success = false,
                error = ex.Message,
            }, JsonOpts)).RootElement.Clone();
        }

        _renderer.NotifyToolResult(callId!, toolName, !result.IsError, result.ErrorMessage);

        return JsonDocument.Parse(JsonSerializer.Serialize(new
        {
            success = !result.IsError,
            content = result.Content,
            error = result.ErrorMessage,
        }, JsonOpts)).RootElement.Clone();
    }

    private JsonElement HandlePermissionRespond(JsonElement @params)
    {
        var requestId = @params.GetProperty("request_id").GetString() ?? "";
        var response = @params.GetProperty("response").GetString() ?? "deny";

        _renderer.ResolvePermission(requestId, response);

        return JsonDocument.Parse(JsonSerializer.Serialize(new
        {
            accepted = true,
        }, JsonOpts)).RootElement.Clone();
    }

    private async Task<JsonElement> HandleSessionUndo(JsonElement @params, CancellationToken ct)
    {
        var count = @params.TryGetProperty("count", out var c) ? c.GetInt32() : 1;
        var fileHistory = _session.Meta.FileHistory;

        if (fileHistory is null || fileHistory.Snapshots.Count == 0)
        {
            return JsonDocument.Parse(JsonSerializer.Serialize(new
            {
                success = false,
                error = "No file history to undo",
                reverted = new string[0],
            }, JsonOpts)).RootElement.Clone();
        }

        try
        {
            var reverted = await fileHistory.RevertAsync(count, ct);
            return JsonDocument.Parse(JsonSerializer.Serialize(new
            {
                success = true,
                count = reverted.Count,
                reverted,
            }, JsonOpts)).RootElement.Clone();
        }
        catch (Exception ex)
        {
            return JsonDocument.Parse(JsonSerializer.Serialize(new
            {
                success = false,
                error = ex.Message,
                reverted = new string[0],
            }, JsonOpts)).RootElement.Clone();
        }
    }

    private JsonElement HandleSessionStop()
    {
        _shutdownCts.Cancel();
        return JsonDocument.Parse(JsonSerializer.Serialize(new
        {
            stopped = true,
        }, JsonOpts)).RootElement.Clone();
    }

    public async Task SendNotificationAsync(string method, object? @params, CancellationToken ct)
    {
        await _writeLock.WaitAsync(ct);
        try
        {
            var notification = new Dictionary<string, object?>
            {
                ["jsonrpc"] = "2.0",
                ["method"] = method,
                ["params"] = @params,
            };
            var json = JsonSerializer.Serialize(notification, JsonOpts);
            var redacted = SecretScanner.Redact(json);
            await _stdout.WriteLineAsync(redacted.AsMemory(), ct);
            await _stdout.FlushAsync(ct);
        }
        finally
        {
            _writeLock.Release();
        }
    }

    private async Task SendResponse(string id, JsonElement result, CancellationToken ct)
    {
        await _writeLock.WaitAsync(ct);
        try
        {
            var response = new Dictionary<string, object?>
            {
                ["jsonrpc"] = "2.0",
                ["id"] = id,
                ["result"] = result,
            };
            var json = JsonSerializer.Serialize(response, JsonOpts);
            var redacted = SecretScanner.Redact(json);
            await _stdout.WriteLineAsync(redacted.AsMemory(), ct);
            await _stdout.FlushAsync(ct);
        }
        finally
        {
            _writeLock.Release();
        }
    }

    private async Task SendErrorResponse(string id, int code, string message, CancellationToken ct)
    {
        await _writeLock.WaitAsync(ct);
        try
        {
            var response = new Dictionary<string, object?>
            {
                ["jsonrpc"] = "2.0",
                ["id"] = id,
                ["error"] = new { code, message },
            };
            var json = JsonSerializer.Serialize(response, JsonOpts);
            var redacted = SecretScanner.Redact(json);
            await _stdout.WriteLineAsync(redacted.AsMemory(), ct);
            await _stdout.FlushAsync(ct);
        }
        finally
        {
            _writeLock.Release();
        }
    }

    public void Dispose()
    {
        _shutdownCts.Cancel();
        _shutdownCts.Dispose();
        _writeLock.Dispose();
    }
}
