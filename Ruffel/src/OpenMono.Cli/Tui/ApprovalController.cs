using OpenMono.Session;

namespace OpenMono.Tui;

public enum ApprovalDecision
{
    Allow,
    Deny,
    AllowAll,
    DenyAll,
}

public class ApprovalController
{
    private bool _manualApprovalMode;
    private bool _allowAll;
    private bool _denyAll;

    public bool ManualApprovalMode => _manualApprovalMode;

    public Func<ToolCall, CancellationToken, Task<ApprovalDecision>>? RequestApprovalFunc { get; set; }

    public event EventHandler<bool>? OnApprovalModeChanged;

    public void ToggleApprovalMode()
    {
        _manualApprovalMode = !_manualApprovalMode;
        if (!_manualApprovalMode)
        {
            _allowAll = false;
            _denyAll = false;
        }
        OnApprovalModeChanged?.Invoke(this, _manualApprovalMode);
    }

    public void ResetTurn()
    {
        _allowAll = false;
        _denyAll = false;
    }

    public async Task<ApprovalDecision> CheckApprovalAsync(ToolCall call, CancellationToken ct)
    {
        if (_allowAll)
            return ApprovalDecision.Allow;
        if (_denyAll)
            return ApprovalDecision.DenyAll;
        if (!_manualApprovalMode)
            return ApprovalDecision.Allow;

        if (RequestApprovalFunc is not null)
        {
            var decision = await RequestApprovalFunc(call, ct);
            if (decision == ApprovalDecision.AllowAll)
                _allowAll = true;
            if (decision == ApprovalDecision.DenyAll)
                _denyAll = true;
            return decision;
        }

        return ApprovalDecision.Allow;
    }
}
