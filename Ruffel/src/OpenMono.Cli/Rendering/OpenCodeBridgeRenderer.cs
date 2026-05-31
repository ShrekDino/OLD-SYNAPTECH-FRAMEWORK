using System.Collections.Concurrent;
using OpenMono.Commands;
using OpenMono.Permissions;
using OpenMono.Utils;

namespace OpenMono.Rendering;

public sealed class OpenCodeBridgeRenderer : IRenderer
{
    private TerminalJsonRpcServer _server;
    private readonly ConcurrentDictionary<string, TaskCompletionSource<PermissionResponse>> _pendingPermissions = new();

    public bool Verbose { get; set; }

    public OpenCodeBridgeRenderer()
    {
        _server = null!;
    }

    public OpenCodeBridgeRenderer(TerminalJsonRpcServer server)
    {
        _server = server;
    }

    public void SetServer(TerminalJsonRpcServer server) => _server = server;

    public void EnableCommandSuggestions(CommandRegistry registry) { }

    public string ReadInput()
    {
        throw new NotSupportedException("OpenCodeBridgeRenderer does not support ReadInput — use JSON-RPC input/send instead.");
    }

    public string? ShowCommandPicker(CommandRegistry registry) => null;

    public async Task<string> AskUserAsync(string question, CancellationToken ct)
    {
        var callId = "q_" + Guid.NewGuid().ToString("N")[..8];
        var tcs = new TaskCompletionSource<PermissionResponse>(TaskCreationOptions.RunContinuationsAsynchronously);
        _pendingPermissions[callId] = tcs;

        await _server.SendNotificationAsync("question/ask", new { question, call_id = callId }, ct);

        PermissionResponse result;
        try
        {
            result = await tcs.Task.WaitAsync(ct);
        }
        catch (OperationCanceledException)
        {
            _pendingPermissions.TryRemove(callId, out _);
            return "no";
        }

        return result switch
        {
            PermissionResponse.Allow => "yes",
            _ => "no",
        };
    }

    public async Task<PermissionResponse> AskPermissionAsync(string toolName, string summary, CancellationToken ct)
    {
        var callId = "perm_" + Guid.NewGuid().ToString("N")[..8];
        var tcs = new TaskCompletionSource<PermissionResponse>(TaskCreationOptions.RunContinuationsAsynchronously);
        _pendingPermissions[callId] = tcs;

        await _server.SendNotificationAsync("permission/ask", new
        {
            call_id = callId,
            tool_name = toolName,
            summary = SecretScanner.Redact(summary),
        }, ct);

        try
        {
            return await tcs.Task.WaitAsync(ct);
        }
        catch (OperationCanceledException)
        {
            _pendingPermissions.TryRemove(callId, out _);
            return PermissionResponse.Deny;
        }
    }

    public void NotifyToolResult(string callId, string toolName, bool success, string? error)
    {
        if (success)
        {
            _ = _server.SendNotificationAsync("tool/result", new
            {
                call_id = callId,
                tool_name = toolName,
                success = true,
            }, CancellationToken.None);
        }
        else
        {
            _ = _server.SendNotificationAsync("tool/crash", new
            {
                call_id = callId,
                tool_name = toolName,
                error = error is not null ? SecretScanner.Redact(error) : null,
            }, CancellationToken.None);
        }
    }

    internal void ResolvePermission(string requestId, string response)
    {
        var result = response.ToLowerInvariant() switch
        {
            "allow" => PermissionResponse.Allow,
            "allow_all" or "always" => PermissionResponse.AllowAll,
            "deny_all" => PermissionResponse.DenyAll,
            _ => PermissionResponse.Deny,
        };

        if (_pendingPermissions.TryRemove(requestId, out var tcs))
            tcs.TrySetResult(result);
    }

    private string MaybeRedact(string content)
    {
        return SecretScanner.Redact(content);
    }

    public void StartAssistantResponse()
    {
        _ = _server.SendNotificationAsync("turn/start", null, CancellationToken.None);
    }

    public void StreamText(string text)
    {
        _ = _server.SendNotificationAsync("text/delta", new { delta = MaybeRedact(text) }, CancellationToken.None);
    }

    public void EndAssistantResponse(TurnMetrics? metrics = null)
    {
        _ = _server.SendNotificationAsync("turn/end", metrics is not null ? new { metrics } : null, CancellationToken.None);
        if (metrics is not null)
        {
            _ = _server.SendNotificationAsync("session/update", new
            {
                turn_count = metrics.PromptTokens > 0 ? 1 : 0,
                total_tokens_used = metrics.PromptTokens + metrics.CompletionTokens,
                status = "idle",
            }, CancellationToken.None);
        }
    }

    public void AppendThinking(string text)
    {
        _ = _server.SendNotificationAsync("text/thinking", new { delta = text }, CancellationToken.None);
    }

    public void CollapseThinking(int charCount)
    {
        _ = _server.SendNotificationAsync("text/thinking_collapsed", new { char_count = charCount }, CancellationToken.None);
    }

    public void ShowWaitingIndicator()
    {
        _ = _server.SendNotificationAsync("session/waiting", null, CancellationToken.None);
    }

    public void ClearWaitingIndicator()
    {
    }

    public void WriteWelcome(string model, string endpoint)
    {
        _ = _server.SendNotificationAsync("session/welcome", new { model, endpoint }, CancellationToken.None);
    }

    public void WriteMarkdown(string markdown)
    {
        _ = _server.SendNotificationAsync("text/markdown", new { content = MaybeRedact(markdown) }, CancellationToken.None);
    }

    public void WriteDebug(string message)
    {
        if (!Verbose) return;
        _ = _server.SendNotificationAsync("session/debug", new { content = message }, CancellationToken.None);
    }

    public void WriteToolStart(string toolName, string args)
    {
        _ = _server.SendNotificationAsync("tool/start", new { tool_name = toolName, arguments = args }, CancellationToken.None);
    }

    public void WriteToolSuccess(string toolName)
    {
        _ = _server.SendNotificationAsync("tool/result", new { tool_name = toolName, success = true }, CancellationToken.None);
    }

    public void WriteToolError(string toolName, string error)
    {
        _ = _server.SendNotificationAsync("tool/result", new { tool_name = toolName, success = false, error = MaybeRedact(error) }, CancellationToken.None);
    }

    public void WriteToolDenied(string toolName, string reason)
    {
        _ = _server.SendNotificationAsync("tool/result", new { tool_name = toolName, success = false, error = $"Denied: {reason}" }, CancellationToken.None);
    }

    public void WriteToolDiff(string diff)
    {
        _ = _server.SendNotificationAsync("text/diff", new { content = MaybeRedact(diff) }, CancellationToken.None);
    }

    public void WriteToolContent(string toolName, string filePath, string content)
    {
        _ = _server.SendNotificationAsync("text/tool_content", new { tool_name = toolName, file_path = filePath, content = MaybeRedact(content) }, CancellationToken.None);
    }

    public void WriteWarning(string message)
    {
        _ = _server.SendNotificationAsync("session/warning", new { content = MaybeRedact(message) }, CancellationToken.None);
    }

    public void WriteError(string message)
    {
        _ = _server.SendNotificationAsync("session/error", new { message = MaybeRedact(message), fatal = false }, CancellationToken.None);
    }

    public void WriteInfo(string message)
    {
        _ = _server.SendNotificationAsync("session/info", new { content = MaybeRedact(message) }, CancellationToken.None);
    }

    public void WriteTodos(IReadOnlyList<Session.TodoItem> todos)
    {
        _ = _server.SendNotificationAsync("session/todos", new { todos }, CancellationToken.None);
    }

    public void ClearConversation()
    {
        _ = _server.SendNotificationAsync("session/clear", null, CancellationToken.None);
    }

    public void BeginTurn()
    {
        _ = _server.SendNotificationAsync("turn/start", null, CancellationToken.None);
    }

    public void EndTurn()
    {
        _ = _server.SendNotificationAsync("turn/end", null, CancellationToken.None);
    }
}
