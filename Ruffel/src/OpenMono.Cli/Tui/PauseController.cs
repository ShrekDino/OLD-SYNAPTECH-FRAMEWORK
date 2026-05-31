namespace OpenMono.Tui;

public class PauseController
{
    private volatile bool _isPaused;
    private readonly object _lock = new();
    private TaskCompletionSource<bool>? _resumeSource;

    public bool IsPaused => _isPaused;

    public event EventHandler<bool>? OnPauseStateChanged;

    public void TogglePause()
    {
        lock (_lock)
        {
            _isPaused = !_isPaused;
            if (_isPaused)
            {
                _resumeSource = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
            }
            else
            {
                _resumeSource?.TrySetResult(true);
                _resumeSource = null;
            }
        }
        OnPauseStateChanged?.Invoke(this, _isPaused);
    }

    public Task WaitIfPausedAsync(CancellationToken cancellationToken)
    {
        if (!_isPaused)
            return Task.CompletedTask;

        TaskCompletionSource<bool>? source;
        lock (_lock)
        {
            if (!_isPaused)
                return Task.CompletedTask;
            source = _resumeSource ??= new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        }

        using (cancellationToken.Register(() => source.TrySetCanceled(cancellationToken)))
        {
            return source.Task;
        }
    }
}
